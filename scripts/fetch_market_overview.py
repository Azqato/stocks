#!/usr/bin/env python3
"""
Builds the Market Overview data feed: a price/change snapshot for a fixed
list of major benchmark ETFs plus the VIX index (data/market_overview_list.json,
owner-curated, hand-edited only -- no auto-sync). Runs three times per
trading day (15:00, 19:00, 22:00 UTC via market-overview.yml), unlike every
other feed in this pipeline which runs once daily after close -- this page
is meant to read as a same-day check-in, not a close-of-business number.

This is deliberately NOT the ETFs screener universe (fetch_etf_data.py /
data/screener_etfs.json): Market Overview is a plain snapshot display, not a
scored/ranked tool, so it only needs price and previous close, not returns
history, RSI, or technicals. Kept as its own lightweight fetch so this page's
data stays independent of the scored ETFs list (which the owner may reorder
or change without wanting Market Overview to follow).

VIX (data/market_overview_list.json's "VIX" entry) is an index, not a fund --
Yahoo symbol "^VIX", fetched via the same Ticker.info price/previousClose
fields as everything else. It has no shares/AUM/expense-ratio fields, but
this script only reads price fields, so it needs no special-casing beyond
the list's separate "y" (Yahoo fetch symbol) vs "t" (display ticker) columns.

Uses yfinance (public Yahoo Finance data), so there is no API key.

Each list entry also carries a "g" (group) field -- "benchmarks", "industries",
"leveraged", "commodities", "crypto", or "yields" -- so the frontend can render
separate sections without a second parallel config. Quote insertion order
matches the list's order, so the frontend does not need its own hardcoded
display-order array either.

"yields" entries carry an additional "unit": "pct" field, since their "price"
IS already a percentage (a Treasury yield), not a fund NAV -- the frontend
must not compute or display changePct for these (a small yield move looks
like a huge, misleading percentage move; e.g. 4.539 -> 4.569 is +0.66% of
the *number* but the actual, meaningful move is "+0.030 percentage points").
The plain "change" field (price - prevClose) is already the correct
point-change for these and needs no special handling. Yield symbols
(data/market_overview_list.json's "yields" group): 2-Year via "2YY=F"
(2-Year Yield Futures -- ^UST2Y/^US2Y do not exist on Yahoo, this is the
closest working proxy), 10-Year via "^TNX", 30-Year via "^TYX". All three
return the yield already in percent (no /10 scaling needed, verified
2026-07-10) via the same Ticker.info fields as everything else. Foreign
sovereign yields and the 30-year mortgage rate are NOT available via
yfinance (every plausible ticker guess 404s) -- see ROADMAP.md.

Output schema: { "updated": ISO, "source": "yahoo",
  "quotes": { TICKER: { "name", "group", "unit", "price", "prevClose", "change", "changePct" }, ... } }
"unit" is only present ("pct") on yield entries; absent means "price" (default).

Env:
  PAUSE   seconds to wait between symbols (default 0.5) -- be polite to Yahoo
"""

import datetime
import json
import os
import sys
import time

import yfinance as yf

LIST_PATH = "data/market_overview_list.json"
OUT_PATH = "data/market_overview.json"
PAUSE = float(os.environ.get("PAUSE", "0.5"))


def num(x):
    """Coerce to a finite float, else None."""
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    if f != f or f in (float("inf"), float("-inf")):
        return None
    return f


def fetch(yahoo_symbol):
    info = yf.Ticker(yahoo_symbol).info or {}
    price = num(info.get("regularMarketPrice")) or num(info.get("currentPrice"))
    prev = num(info.get("regularMarketPreviousClose")) or num(info.get("previousClose"))
    rec = {"price": price, "prevClose": prev, "change": None, "changePct": None}
    if price is not None and prev not in (None, 0):
        rec["change"] = price - prev
        rec["changePct"] = (price / prev - 1) * 100
    return rec


def main():
    now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    with open(LIST_PATH, encoding="utf-8") as f:
        listing = json.load(f)

    quotes = {}
    ok = 0
    for item in listing:
        ticker = item["t"]
        rec = {"name": item["n"], "group": item.get("g", "benchmarks")}
        if item.get("unit"):
            rec["unit"] = item["unit"]
        for attempt in range(3):
            try:
                rec.update(fetch(item["y"]))
                if rec.get("price") is not None:
                    ok += 1
                break
            except Exception as e:  # noqa: BLE001 - keep going on any single-symbol failure
                if attempt == 2:
                    print(f"{ticker}: failed after retries: {e!r}", file=sys.stderr)
                    rec.setdefault("price", None)
                    rec.setdefault("prevClose", None)
                    rec.setdefault("change", None)
                    rec.setdefault("changePct", None)
                else:
                    time.sleep(2)
        quotes[ticker] = rec
        time.sleep(PAUSE)

    out = {"updated": now, "source": "yahoo", "quotes": quotes}
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    print(f"Wrote {OUT_PATH}: {ok}/{len(listing)} symbols with price data.")


if __name__ == "__main__":
    main()
