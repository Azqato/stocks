#!/usr/bin/env python3
"""
Refreshes the ETF-defined constituent lists the screener's Growth, Value,
Dividend, and International universes rank against:
  data/vug.json   -- top 100 holdings of VUG (Vanguard Growth ETF)
  data/vtv.json   -- top 100 holdings of VTV (Vanguard Value ETF)
  data/vig.json   -- top 100 holdings of VIG (Vanguard Dividend Appreciation ETF)
  data/vxus.json  -- top 100 holdings of VXUS (Vanguard Total International Stock ETF)

For VUG/VTV/VIG it fetches the full stock holdings from Vanguard's own
holdings API (weight-sorted, refreshed monthly by Vanguard), applies the dual-class rule
(keep only the Class A voting share when a fund holds multiple classes), takes
the top 100 by weight, sanity-checks the result, preserves existing curated
short names, and writes the file only if membership actually changed. Prints
the add/remove diff so the GitHub Action commit message / log shows what moved.

Tickers are stored in display form (e.g. "BRK.B"); the data fetcher converts
the dot to a dash ("BRK-B") for Yahoo lookups.

VXUS is handled separately (see sync_vxus): its holdings report local-exchange
tickers with no exchange suffix and no US convention, so each holding is
identified by ISIN (which Vanguard's API returns directly) and resolved to a
suffixed Yahoo symbol via Yahoo's search endpoint. The resolution is cached in
data/vxus_map.json (ISIN -> Yahoo symbol) so a weekly sync only needs to
resolve newly-added holdings; a `manual` block in that file always overrides
the automatic resolution and is how a bad auto-resolution gets corrected.
Vanguard's raw holdings occasionally report the same ISIN as two separate
rows (observed for BHP Group and Barrick Gold); these are merged by summing
weight before ranking, so "top 100 by weight" means 100 distinct issuers.

Run weekly in CI alongside update_constituents.py. Dependencies: requests.
"""

import json
import re
import sys
import time

import requests

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept": "application/json",
}

# Vanguard's holdings endpoint, as called by their own portfolio-composition
# web component (fundsBaseUrl in common-*.js). The previous profile-API path
# (/investment-products/etfs/profile/api/{fund}/portfolio-holding/stock) was
# retired sometime after 2026-08-08 and is now swallowed by the site's SPA
# router, which answers HTTP 200 with the app's HTML shell, so
# raise_for_status() passes and only .json() fails. check_payload() below
# turns that class of failure into an explicit abort.
API = "https://investor.vanguard.com/irr/funds/profile/{fund}-AdditionalFundData"
YAHOO_SEARCH = "https://query2.finance.yahoo.com/v1/finance/search"

# Duplicate share classes to drop, but only when the kept sibling is present.
# Convention matches the index lists: keep the Class A voting share, except
# Berkshire where the accessible B share is the one every list carries.
DUAL_CLASS = {"GOOG": "GOOGL", "FOX": "FOXA", "NWS": "NWSA", "BF.B": "BF.A",
              "HEI.A": "HEI", "BRK.A": "BRK.B", "LEN.B": "LEN"}

NAME_SUFFIXES = (
    ", Inc.", " Inc.", " Inc", " Corporation", " Corp.", " Corp", " Company",
    " plc", " PLC", " N.V.", " NV", " Ltd.", " Ltd", " S.A.", " SA", " & Co.",
    " AG", " SE", " ASA", " A/S", " KGaA", " SpA", " S.p.A.", " AB", " OYJ", " Oy", " GmbH",
)

TOP_N = 100

# Per-fund config: which fund to fetch, where to write, and the expected size
# band of the RAW holdings list (a guard so a bad response never clobbers a
# good list -- both funds hold comfortably more than 100 stocks).
FUNDS = {
    "vug": {"fund": "VUG", "path": "data/vug.json", "raw_lo": 110, "raw_hi": 500},
    "vtv": {"fund": "VTV", "path": "data/vtv.json", "raw_lo": 110, "raw_hi": 500},
    "vig": {"fund": "VIG", "path": "data/vig.json", "raw_lo": 110, "raw_hi": 500},
}

# VXUS config: the retired profile API capped this fund at exactly 500
# entities (confirmed empirically 2026-07-03), so the guard band used to be a
# tight 480-520. The current endpoint returns the full holdings list instead
# (8,794 rows on 2026-09-21), so the band is widened to match. Because the
# list is weight-sorted and only the top 100 is kept, the practical effect of
# the cap's removal is nil, but same-issuer ISIN duplicates can now be found
# deeper in the list than the old 500-row window reached.
VXUS_FUND = "VXUS"
VXUS_LIST_PATH = "data/vxus.json"
VXUS_MAP_PATH = "data/vxus_map.json"
VXUS_RAW_LO = 7000
VXUS_RAW_HI = 11000
# A Yahoo symbol looks like TICKER or TICKER.SUFFIX, where TICKER may contain
# digits (Asian local tickers) and letters (Western ones), and SUFFIX is a
# short exchange code -- much looser than the domestic BRK.B-style regex.
VXUS_SYMBOL_RE = re.compile(r"^[A-Z0-9-]{1,10}(\.[A-Z]{1,3})?$")

# Same-issuer entries Vanguard reports under multiple ISINs that should count
# as ONE company for the top-100 cut (weight summed into the kept ISIN, the
# other dropped before ranking). Three distinct reasons, all hand-verified by
# inspecting Vanguard's raw response 2026-07-04 -- do NOT auto-detect this by
# name similarity, since a naive name match also flags SoftBank Group Corp
# and SoftBank Corp as "the same," which they are not (parent holding company
# vs. a separately-traded, separately-run subsidiary):
#   - A genuine duplicate custody record for the identical security: one line
#     always has a blank ticker (Vanguard shortName ends "-PRIM" for Air
#     Liquide), likely a French registered/bearer-share settlement split.
#     Keep the ticker-bearing line.
#   - A real dual share class (Samsung Electronics common/preferred, Investor
#     AB and Atlas Copco A/B): keep the higher-weighted (more liquid) class.
#   - A dual listing of the same underlying group across exchanges (Rio
#     Tinto's London/Australia listings, CATL's Hong Kong/Shenzhen listings):
#     keep the higher-weighted listing.
VXUS_SAME_ISSUER_MERGE = {
    "KR7005930003": ["KR7005931001"],   # Samsung Electronics: common kept, preferred merged in
    "FR0000120073": ["FR0000053951"],   # Air Liquide: ticker-bearing line kept, blank-ticker duplicate merged in
    "FR0000120321": ["FR0011149590"],   # L'Oreal: ticker-bearing line kept, blank-ticker duplicate merged in
    "FR0010208488": ["FR0013215407"],   # Engie: ticker-bearing line kept, blank-ticker duplicate merged in
    "SE0015811963": ["SE0015811955"],   # Investor AB: Class B (higher weight) kept, Class A merged in
    "SE0017486889": ["SE0017486897"],   # Atlas Copco: Class A (higher weight) kept, Class B merged in
    "GB0007188757": ["AU000000RIO1"],   # Rio Tinto: London plc (higher weight) kept, Australia Ltd merged in
    "CNE100006WS8": ["CNE100003662"],   # CATL: Hong Kong listing (higher weight) kept, Shenzhen A-share merged in
}


def clean_name(n):
    n = str(n).strip()
    for suf in NAME_SUFFIXES:
        if n.endswith(suf):
            return n[: -len(suf)].rstrip(",").strip()
    return n


def parse_weight(v):
    """'13.61%' -> 13.61. Vanguard sends the weight as a percent string."""
    m = re.search(r"-?[\d.]+", str(v).replace(",", ""))
    return float(m.group()) if m else 0.0


def fetch_entities(fund, raw_lo, raw_hi):
    """Return Vanguard's equity holdings for `fund`, normalized and guarded.

    Each row is {ticker, name, weight, isin}. The response also carries
    shortTermReservesHoldings and derivativeHoldings, which are deliberately
    not merged in: only equityHoldings holds the stocks the screener ranks.
    """
    r = requests.get(API.format(fund=fund), headers=UA, timeout=90)
    r.raise_for_status()
    entities = check_payload(r, fund)
    if not (raw_lo <= len(entities) <= raw_hi):
        sys.exit(f"ABORT [{fund}]: unexpected raw holdings count {len(entities)} "
                 f"(expected {raw_lo}-{raw_hi}).")
    return [{
        # This endpoint spells share classes with a slash ("BRK/B"); the lists,
        # the DUAL_CLASS rule and the screener all use the dot form ("BRK.B").
        "ticker": str(e.get("ticker") or "").strip().upper()
                  .replace(" ", "").replace("/", "."),
        "name": str(e.get("securityLongDescription")
                    or e.get("securityShortDescription") or "").strip(),
        "weight": parse_weight(e.get("marketValuePercentage")),
        "isin": str(e.get("isin") or "").strip(),
    } for e in entities]


def check_payload(r, fund):
    """Return holdingDetails.equityHoldings, or abort with a readable reason.

    Exists because the retired endpoint answers 200-with-HTML rather than 404:
    a silent source removal that read as a JSONDecodeError traceback and went
    unnoticed for six weekly runs. Anything other than the expected JSON shape
    aborts here, naming what arrived instead.
    """
    ctype = r.headers.get("content-type", "")
    if "json" not in ctype.lower():
        sys.exit(f"ABORT [{fund}]: expected JSON from {r.url}, got "
                 f"{ctype!r} ({len(r.text)} bytes). The endpoint has most "
                 f"likely moved again; re-derive it from the fundsBaseUrl "
                 f"value in Vanguard's portfolio-composition web component.")
    try:
        entities = r.json()["holdingDetails"]["equityHoldings"]
    except (ValueError, KeyError, TypeError) as exc:
        sys.exit(f"ABORT [{fund}]: JSON from {r.url} has an unexpected shape "
                 f"({type(exc).__name__}: {exc}); expected "
                 f"holdingDetails.equityHoldings.")
    if not isinstance(entities, list) or not entities:
        sys.exit(f"ABORT [{fund}]: holdingDetails.equityHoldings is empty or "
                 f"not a list.")
    return entities


def fetch_holdings(fund, raw_lo, raw_hi):
    """Return [(symbol, name), ...] weight-sorted from Vanguard's holdings API."""
    rows = []
    for e in fetch_entities(fund, raw_lo, raw_hi):
        sym, name = e["ticker"], e["name"]
        if sym and name:
            rows.append((e["weight"], sym, name))
    rows.sort(key=lambda x: -x[0])  # the API is weight-sorted; make it explicit
    present = {s for _, s, _ in rows}
    out = []
    for _, sym, name in rows:
        if sym in DUAL_CLASS and DUAL_CLASS[sym] in present:
            continue  # drop the non-voting class, keep Class A
        out.append((sym, name))
    return out[:TOP_N]


def sync(name, cfg):
    raw = fetch_holdings(cfg["fund"], cfg["raw_lo"], cfg["raw_hi"])
    syms = [s for s, _ in raw]

    # --- sanity checks: never clobber the list on a bad fetch ---
    if len(syms) != TOP_N:
        sys.exit(f"ABORT [{name}]: expected {TOP_N} holdings after dedupe, got {len(syms)}.")
    if len(set(syms)) != len(syms):
        sys.exit(f"ABORT [{name}]: duplicate tickers in fetched list.")
    bad = [s for s in syms if not re.match(r"^[A-Z][A-Z.]{0,5}$", s)]
    if bad:
        sys.exit(f"ABORT [{name}]: suspicious tickers {bad}.")

    path = cfg["path"]
    try:
        old = json.load(open(path, encoding="utf-8"))
    except Exception:
        old = []
    old_names = {x["t"]: x["n"] for x in old}
    old_syms = [x["t"] for x in old]

    # preserve curated short names for existing tickers; clean Vanguard name for new ones
    listing = [{"t": s, "n": old_names.get(s) or clean_name(nm)} for s, nm in raw]

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


def fetch_vxus_raw():
    """Return VXUS holdings deduped by ISIN (weight summed), weight-sorted.

    Vanguard's raw response occasionally reports the same ISIN as two
    separate rows (observed for BHP Group and Barrick Gold) -- merge those
    before ranking so "top 100 by weight" means 100 distinct issuers, not
    a split holding occupying two slots. Separately, VXUS_SAME_ISSUER_MERGE
    folds in hand-verified same-company holdings reported under genuinely
    different ISINs (dual share classes, dual listings, and a same-security
    custody-record duplicate), so "top 100 by weight" also means 100 distinct
    companies, not a company occupying two slots under two ISINs.
    """
    entities = fetch_entities(VXUS_FUND, VXUS_RAW_LO, VXUS_RAW_HI)
    by_isin = {}
    for e in entities:
        isin = e["isin"]
        if not isin:
            continue
        if isin in by_isin:
            by_isin[isin]["weight"] += e["weight"]
        else:
            by_isin[isin] = dict(e)
    for kept, dropped_isins in VXUS_SAME_ISSUER_MERGE.items():
        if kept not in by_isin:
            continue
        for dropped in dropped_isins:
            if dropped in by_isin:
                by_isin[kept]["weight"] += by_isin.pop(dropped)["weight"]
    rows = sorted(by_isin.values(), key=lambda x: -x["weight"])
    return rows[:TOP_N]


def yahoo_search(query):
    """Query Yahoo's search endpoint; return the EQUITY-type hits."""
    try:
        r = requests.get(YAHOO_SEARCH, params={"q": query}, headers=UA, timeout=20)
        r.raise_for_status()
        quotes = r.json().get("quotes", [])
    except Exception:
        return []
    return [q for q in quotes if q.get("quoteType") == "EQUITY" and q.get("symbol")]


def resolve_vxus_symbol(isin, name, manual, cache):
    """ISIN -> Yahoo symbol, via manual override, then cache, then live lookup.

    Live lookup tries ISIN search first (works for ~99% of holdings); falls
    back to a name search for the rare holding with no ticker in Vanguard's
    data (observed for Air Liquide). Returns None if nothing resolves --
    the caller aborts rather than writing a partial list.
    """
    if isin in manual:
        return manual[isin]
    if isin in cache:
        return cache[isin]
    hits = yahoo_search(isin)
    if not hits:
        hits = yahoo_search(name)
    time.sleep(0.3)
    return hits[0]["symbol"] if hits else None


def sync_vxus():
    raw = fetch_vxus_raw()

    try:
        vmap = json.load(open(VXUS_MAP_PATH, encoding="utf-8"))
    except Exception:
        vmap = {"manual": {}, "resolved": {}}
    manual = vmap.get("manual", {})
    cache = dict(vmap.get("resolved", {}))

    resolved = {}
    for item in raw:
        sym = resolve_vxus_symbol(item["isin"], item["name"], manual, cache)
        if not sym or not VXUS_SYMBOL_RE.match(sym):
            sys.exit(f"ABORT [vxus]: could not resolve a Yahoo symbol for "
                      f"{item['ticker']!r} / {item['isin']} ({item['name']}).")
        resolved[item["isin"]] = sym

    syms = list(resolved.values())
    if len(syms) != TOP_N:
        sys.exit(f"ABORT [vxus]: expected {TOP_N} holdings, got {len(syms)}.")
    if len(set(syms)) != len(syms):
        dupes = [s for s in syms if syms.count(s) > 1]
        sys.exit(f"ABORT [vxus]: duplicate resolved symbols {dupes} -- add a manual override.")

    try:
        old = json.load(open(VXUS_LIST_PATH, encoding="utf-8"))
    except Exception:
        old = []
    old_names = {x["t"]: x["n"] for x in old}
    old_syms = [x["t"] for x in old]

    listing = [{"t": resolved[item["isin"]], "n": old_names.get(resolved[item["isin"]]) or clean_name(item["name"])}
               for item in raw]

    # Cache write happens regardless of whether membership changed, so newly
    # resolved holdings are never re-resolved on the next run.
    with open(VXUS_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump({"manual": manual, "resolved": resolved}, f, indent=2)
        f.write("\n")

    added = [s for s in syms if s not in old_syms]
    removed = [s for s in old_syms if s not in syms]
    if not added and not removed:
        print(f"[vxus] No constituent changes ({len(syms)} tickers).")
        return False

    with open(VXUS_LIST_PATH, "w", encoding="utf-8") as f:
        json.dump(listing, f, indent=2)
        f.write("\n")
    print(f"[vxus] Updated {VXUS_LIST_PATH}: {len(syms)} tickers. "
          f"Added: {added or 'none'}. Removed: {removed or 'none'}.")
    return True


def main():
    changed = False
    for name, cfg in FUNDS.items():
        if sync(name, cfg):
            changed = True
    if sync_vxus():
        changed = True
    # Exit 0 either way; the workflow inspects the git diff to decide what to do.
    if not changed:
        print("No constituent changes for any fund.")


if __name__ == "__main__":
    main()
