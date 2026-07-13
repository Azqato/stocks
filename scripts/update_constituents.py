#!/usr/bin/env python3
"""
Refreshes the constituent lists the screener ranks against:
  data/nasdaq100.json  -- the live Nasdaq-100 index
  data/sp500.json      -- the live S&P 500 index

Each index is fetched from a PRIMARY source with a FALLBACK behind it. The
result gets the dual-class rule (keep only the Class A voting share when a
company has multiple classes in the index), is sanity-checked, preserves
existing curated short names, and is written only if membership actually
changed. Prints the add/remove diff so the Action log shows what moved.

Sources (2026-07-13 rewrite -- see PATCHNOTES v4.1.8):
  nasdaq100: Nasdaq's own index API  -> slickcharts
  sp500:     SSGA's SPY fund holdings -> slickcharts

Why not Wikipedia any more: the Nasdaq-100 article's components table was
removed outright, which broke this job silently (the S&P article still has
its table, but relying on a single scrape of an editable page is what failed).
Why not QQQ holdings for the Nasdaq-100: Invesco returns HTTP 406 to
non-browser clients, so it cannot be fetched from CI at all. Nasdaq's index
API is the more authoritative source anyway. SPY holdings ARE usable, so the
S&P 500 does come straight from the fund.

Each index needs BOTH of its sources to fail before the job errors, and the
sanity checks below mean a malformed-but-successful fetch aborts rather than
clobbering a good list.

Tickers are stored in display form (e.g. "BRK.B"); the data fetcher converts
the dot to a dash ("BRK-B") for Yahoo lookups.

Run weekly in CI. Dependencies: requests, pandas, lxml, openpyxl.
"""

import json
import re
import sys
from io import BytesIO, StringIO

import pandas as pd
import requests

# Some of these hosts (notably slickcharts) reject a bot-looking UA outright,
# so present as a normal browser.
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

TIMEOUT = 45

# Lower/no-vote share classes to drop, but only when their Class A sibling is present.
DUAL_CLASS = {"GOOG": "GOOGL", "FOX": "FOXA", "NWS": "NWSA"}

# Stripped repeatedly, longest-first, so a name like
# "Honeywell Aerospace Inc. Common Stock" reduces all the way to
# "Honeywell Aerospace". The share-class/security-type tails come from the
# Nasdaq API; the corporate tails come from every source.
NAME_SUFFIXES = (
    " Class A Common Stock", " Class B Common Stock", " Class C Common Stock",
    " Common Stock", " Common Shares", " Ordinary Shares", " Depositary Shares",
    ", Inc.", " Inc.", " Inc", " Corporation", " Corp.", " Corp", " Company",
    " plc", " PLC", " N.V.", " Ltd.", " Ltd", " S.A.", " Co.",
)

TICKER_RE = re.compile(r"^[A-Z][A-Z.]{0,5}$")


def clean_name(n):
    n = str(n).strip()
    changed = True
    while changed:
        changed = False
        for suf in NAME_SUFFIXES:
            if n.lower().endswith(suf.lower()):
                n = n[: -len(suf)].rstrip(",").strip()
                changed = True
                break
    return n


def normalize(rows):
    """[(sym, name)] -> cleaned, de-duped, dual-class-resolved [(sym, name)]."""
    clean = []
    for sym, name in rows:
        sym = str(sym).strip().upper().replace(" ", "")
        if not TICKER_RE.match(sym):
            continue  # skips cash/futures/placeholder lines in fund holdings files
        clean.append((sym, str(name).strip()))

    present = {s for s, _ in clean}
    out, seen = [], set()
    for sym, name in clean:
        if sym in DUAL_CLASS and DUAL_CLASS[sym] in present:
            continue  # drop the non-voting class, keep Class A
        if sym in seen:
            continue
        seen.add(sym)
        out.append((sym, name))
    return out


# ---- sources -------------------------------------------------------------
# Each returns [(symbol, name), ...] or raises.

def from_nasdaq_api():
    """Nasdaq's own index listing -- the authoritative Nasdaq-100 membership."""
    r = requests.get("https://api.nasdaq.com/api/quote/list-type/nasdaq100",
                     headers=UA, timeout=TIMEOUT)
    r.raise_for_status()
    rows = r.json()["data"]["data"]["rows"]
    return normalize([(x["symbol"], x.get("companyName", "")) for x in rows])


def from_spy_holdings():
    """State Street's published SPY holdings -- the actual fund, not a scrape."""
    url = ("https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/"
           "etfs/us/holdings-daily-us-en-spy.xlsx")
    r = requests.get(url, headers=UA, timeout=TIMEOUT)
    r.raise_for_status()
    # The sheet carries 4 rows of fund header/metadata above the real column names.
    df = pd.read_excel(BytesIO(r.content), skiprows=4)
    df = df[df["Ticker"].notna()]
    return normalize([(x["Ticker"], x["Name"]) for _, x in df.iterrows()])


def from_slickcharts(slug):
    """Fallback for both indices: one HTML table, Symbol + Company columns."""
    def _fetch():
        r = requests.get(f"https://www.slickcharts.com/{slug}", headers=UA, timeout=TIMEOUT)
        r.raise_for_status()
        table = next(t for t in pd.read_html(StringIO(r.text))
                     if "Symbol" in t.columns and "Company" in t.columns and len(t) > 50)
        return normalize([(x["Symbol"], x["Company"]) for _, x in table.iterrows()])
    return _fetch


# Per-index config: ordered sources, where to write, and the expected size band
# (a guard so a bad-but-successful fetch never clobbers a good list).
INDICES = {
    "nasdaq100": {
        "sources": [("nasdaq-api", from_nasdaq_api),
                    ("slickcharts", from_slickcharts("nasdaq100"))],
        "path": "data/nasdaq100.json",
        "count_lo": 90,
        "count_hi": 105,
    },
    "sp500": {
        "sources": [("spy-holdings", from_spy_holdings),
                    ("slickcharts", from_slickcharts("sp500"))],
        "path": "data/sp500.json",
        "count_lo": 480,
        "count_hi": 515,
    },
}


def fetch_constituents(name, cfg):
    """Try each source in order; return the first that yields a sane list."""
    errors = []
    for src_name, src in cfg["sources"]:
        try:
            fetched = src()
        except Exception as e:
            errors.append(f"{src_name}: {type(e).__name__}: {e}")
            print(f"[{name}] source '{src_name}' failed: {type(e).__name__}: {e}")
            continue

        syms = [s for s, _ in fetched]
        # Validate HERE, not after the loop, so a source that returns a
        # malformed list falls through to the next one instead of aborting
        # the whole job on data we could have recovered from.
        problem = None
        if not (cfg["count_lo"] <= len(syms) <= cfg["count_hi"]):
            problem = (f"unexpected count {len(syms)} "
                       f"(expected {cfg['count_lo']}-{cfg['count_hi']})")
        elif len(set(syms)) != len(syms):
            problem = "duplicate tickers"
        if problem:
            errors.append(f"{src_name}: {problem}")
            print(f"[{name}] source '{src_name}' rejected: {problem}")
            continue

        print(f"[{name}] source '{src_name}' OK: {len(syms)} tickers.")
        return fetched

    sys.exit(f"ABORT [{name}]: every source failed.\n  " + "\n  ".join(errors))


def sync(name, cfg):
    fetched = fetch_constituents(name, cfg)
    syms = [s for s, _ in fetched]

    path = cfg["path"]
    try:
        old = json.load(open(path, encoding="utf-8"))
    except Exception:
        old = []
    old_names = {x["t"]: x["n"] for x in old}
    old_syms = [x["t"] for x in old]

    # preserve curated short names for existing tickers; clean the source's name for new ones
    listing = [{"t": s, "n": old_names.get(s) or clean_name(nm)} for s, nm in fetched]
    # Sort by company name so the file's order is stable no matter what order a
    # given source happens to return: without this, simply switching sources
    # rewrites all ~500 lines and real add/removes get lost in the churn.
    listing.sort(key=lambda x: (x["n"].lower(), x["t"]))

    added = [s for s in syms if s not in old_syms]
    removed = [s for s in old_syms if s not in syms]
    if not added and not removed:
        print(f"[{name}] No constituent changes ({len(syms)} tickers).")
        return False

    with open(path, "w", encoding="utf-8") as f:
        json.dump(listing, f, indent=2)
        f.write("\n")
    print(f"[{name}] Updated {path}: {len(syms)} tickers. "
          f"Added: {added or 'none'}. Removed: {removed or 'none'}.")
    return True


def main():
    changed = False
    for name, cfg in INDICES.items():
        if sync(name, cfg):
            changed = True
    # Exit 0 either way; the workflow inspects the git diff to decide what to do.
    if not changed:
        print("No constituent changes for any index.")


if __name__ == "__main__":
    main()
