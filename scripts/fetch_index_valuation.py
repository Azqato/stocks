#!/usr/bin/env python3
"""
Builds data/index_valuation.json: trailing and forward P/E for the S&P 500,
Nasdaq 100, Dow Jones Industrial Average and Russell 2000, calculated from
their member stocks. Runs weekly (index-valuation.yml), after the Sunday
whole-market stock run, for the Invests Index Valuation page.

Why calculate rather than read: no free feed publishes forward P/E for these
indices. WSJ's "P/Es & Yields on Major Indexes" table is the usual reference
(trailing on reported earnings, forward from Birinyi Associates' estimates),
but it has no API. Checked against it on 2026-10-20, this method lands within
about 6% on both for the S&P 500, Nasdaq 100 and Dow.

Method:
  Trailing P/E  index market cap / index trailing earnings (a company's
                earnings are its market cap / its trailing P/E, from the
                stock feed).
  Forward P/E   index market cap / index forward earnings, where a company's
                forward EPS is the average of analysts' estimates for this
                fiscal year and next (Yahoo's earnings_estimate "0y" and
                "+1y").
  Both count profitable companies only, so the two are comparable. Counting
  losses was tried: for the Russell 2000 the losses outweigh the profits
  (-$149B against +$128B on 2026-10-20), which makes its P/E meaningless.
  WSJ's Russell 2000 figures (34.62 / 26.32) can't be reproduced by any one
  consistent rule; ours read about 15 / 13.
  Growth        trailing / forward - 1: the earnings growth the two imply.
  The Dow is price-weighted, so it sums share prices and EPS instead of
  market caps and earnings.

Membership:
  S&P 500, Nasdaq 100  data/sp500.json, data/nasdaq100.json (constituents.yml)
  Dow                  SSGA's DIA holdings, slickcharts fallback; cached in
                       data/dow30.json
  Russell 2000         Vanguard's VTWO holdings; cached in data/russell2000.json
  A failed or implausible fetch keeps the cached list rather than failing.

Prices, market caps and trailing P/E come from data/stocks/part-*.json; a
member missing from the parts is fetched from Yahoo directly.

Uses yfinance and public fund-holdings files, so there is no API key.
"""

import concurrent.futures as cf
import datetime
import glob
import io
import json
import math
import sys
import time

import pandas as pd
import requests
import yfinance as yf

sys.path.insert(0, "scripts")
import update_etf_constituents as vanguard  # noqa: E402  (shared Vanguard holdings fetcher)

OUT_PATH = "data/index_valuation.json"
UA = vanguard.UA
WORKERS = 4
MIN_FORWARD_SHARE = 0.85  # abort below this share of members with estimates
TICKER_OK = vanguard.re.compile(r"^[A-Z][A-Z.]{0,5}$")

INDICES = [
    {"key": "sp500", "name": "S&P 500", "weight": "cap", "list": "data/sp500.json"},
    {"key": "nasdaq100", "name": "Nasdaq 100", "weight": "cap", "list": "data/nasdaq100.json"},
    {"key": "dow", "name": "Dow Jones Industrial Average", "weight": "price", "list": "data/dow30.json",
     "lo": 29, "hi": 31},
    {"key": "russell2000", "name": "Russell 2000", "weight": "cap", "list": "data/russell2000.json",
     "lo": 1900, "hi": 2100},
]


def ok(v):
    return isinstance(v, (int, float)) and math.isfinite(v)


def from_dia():
    url = ("https://www.ssga.com/us/en/intermediary/library-content/products/fund-data/"
           "etfs/us/holdings-daily-us-en-dia.xlsx")
    r = requests.get(url, headers=UA, timeout=45)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), skiprows=4)
    return [str(t).strip() for t in df["Ticker"].dropna()]


def from_slickcharts_dow():
    r = requests.get("https://www.slickcharts.com/dowjones", headers=UA, timeout=45)
    r.raise_for_status()
    t = next(t for t in pd.read_html(io.StringIO(r.text)) if "Symbol" in t.columns)
    return [str(s).strip() for s in t["Symbol"]]


def from_vtwo():
    return [e["ticker"] for e in vanguard.fetch_entities("VTWO", 1500, 2500)]


SOURCES = {"dow": [("dia-holdings", from_dia), ("slickcharts", from_slickcharts_dow)],
           "russell2000": [("vtwo-holdings", from_vtwo)]}


def members(idx):
    """The index's tickers: fetched for the Dow and Russell 2000 (cached on success)."""
    path = idx["list"]
    for src, fn in SOURCES.get(idx["key"], []):
        try:
            tickers = sorted({t.replace("/", ".") for t in fn() if TICKER_OK.match(t.replace("/", "."))})
            if idx["lo"] <= len(tickers) <= idx["hi"]:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump([{"t": t} for t in tickers], f, indent=2)
                    f.write("\n")
                print(f"[{idx['key']}] {len(tickers)} members from {src}")
                return tickers
            print(f"[{idx['key']}] {src}: implausible count {len(tickers)}, skipped")
        except Exception as exc:
            print(f"[{idx['key']}] {src} failed: {type(exc).__name__}: {exc}")
    with open(path, encoding="utf-8") as f:
        tickers = [x["t"] for x in json.load(f)]
    print(f"[{idx['key']}] {len(tickers)} members from {path}")
    return tickers


def yahoo_quote(t):
    """Price, market cap and trailing P/E for a member the stock parts don't carry."""
    try:
        i = yf.Ticker(t.replace(".", "-")).info
        return {"price": i.get("currentPrice") or i.get("regularMarketPrice"),
                "marketCap": i.get("marketCap"), "peTTM": i.get("trailingPE")}
    except Exception:
        return {}


def estimates(t):
    """Analysts' average EPS estimate for this fiscal year and next, or None."""
    # Yahoo throttles bursts: an error is retried with a growing pause. An
    # empty table is a real answer (no analyst coverage), returned as None.
    for attempt in range(4):
        try:
            e = yf.Ticker(t.replace(".", "-")).earnings_estimate
            if e is None or e.empty:
                return None
            vals = [float(e.loc[k, "avg"]) for k in ("0y", "+1y") if k in e.index]
            vals = [v for v in vals if ok(v)]
            return sum(vals) / len(vals) if len(vals) == 2 else None
        except Exception:
            time.sleep(3 * (attempt + 1))
    return None


def valuation(idx, tickers, stocks, fwd):
    price_w = idx["weight"] == "price"
    cap_t = earn_t = cap_f = earn_f = 0.0
    n_t = n_f = 0
    for t in tickers:
        s = stocks.get(t) or {}
        price, cap, pe = s.get("price"), s.get("marketCap"), s.get("peTTM")
        if not (ok(price) and price > 0 and ok(cap) and cap > 0):
            continue
        size = price if price_w else cap
        if ok(pe) and pe > 0:
            cap_t += size
            earn_t += size / pe
            n_t += 1
        eps = fwd.get(t)
        if ok(eps) and eps > 0:
            cap_f += size
            earn_f += size * eps / price
            n_f += 1
    trailing = cap_t / earn_t if earn_t > 0 else None
    forward = cap_f / earn_f if earn_f > 0 else None
    return {
        "key": idx["key"], "name": idx["name"], "weighting": idx["weight"],
        "members": len(tickers), "trailingCount": n_t, "forwardCount": n_f,
        "trailingPE": round(trailing, 2) if trailing else None,
        "forwardPE": round(forward, 2) if forward else None,
        "growthPct": round((trailing / forward - 1) * 100, 1) if trailing and forward else None,
    }


def main():
    stocks = {}
    for f in sorted(glob.glob("data/stocks/part-*.json")):
        with open(f, encoding="utf-8") as fh:
            stocks.update(json.load(fh)["stocks"])
    lists = {idx["key"]: members(idx) for idx in INDICES}
    universe = sorted({t for ts in lists.values() for t in ts})

    missing = [t for t in universe if t not in stocks]
    with cf.ThreadPoolExecutor(WORKERS) as ex:
        for t, q in zip(missing, ex.map(yahoo_quote, missing)):
            if q:
                stocks[t] = q
    print(f"{len(universe)} unique members; {len(missing)} fetched from Yahoo directly")

    with cf.ThreadPoolExecutor(WORKERS) as ex:
        fwd = dict(zip(universe, ex.map(estimates, universe)))
    # A second, one-at-a-time pass over the misses after a pause: most are
    # throttled requests rather than stocks with no estimates.
    retry = [t for t in universe if fwd[t] is None]
    time.sleep(30)
    for t in retry:
        fwd[t] = estimates(t)
        time.sleep(0.3)
    print(f"second pass recovered {sum(1 for t in retry if fwd[t] is not None)} of {len(retry)}")
    print(f"forward estimates for {sum(1 for v in fwd.values() if v is not None)} of {len(universe)}")

    out = {
        "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": "yahoo",
        "method": "Market cap / earnings, profitable companies only. Trailing uses the last 12 "
                  "months; forward uses the average of this and next fiscal year's analyst EPS "
                  "estimates. The Dow is price-weighted.",
        "indices": [valuation(idx, lists[idx["key"]], stocks, fwd) for idx in INDICES],
    }
    for r in out["indices"]:
        if r["trailingPE"] is None or r["forwardPE"] is None:
            sys.exit(f"ABORT: no P/E for {r['name']}; not overwriting {OUT_PATH}")
    got = sum(1 for v in fwd.values() if v is not None)
    if got < MIN_FORWARD_SHARE * len(universe):
        sys.exit(f"ABORT: estimates for only {got} of {len(universe)} members (Yahoo throttling?); "
                 f"not overwriting {OUT_PATH}")
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    for r in out["indices"]:
        print(f"{r['name']}: trailing {r['trailingPE']} ({r['trailingCount']}/{r['members']}), "
              f"forward {r['forwardPE']} ({r['forwardCount']}/{r['members']}), growth {r['growthPct']}%")


if __name__ == "__main__":
    main()
