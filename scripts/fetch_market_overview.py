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

Uses yfinance (public Yahoo Finance data) and FRED's public CSV endpoint, so
there is no API key.

Each list entry carries a "category" field -- free text, e.g. "Indices",
"Factors", "Industries", "Commodities", "Bonds", "Leveraged ETFs", "Crypto" --
that becomes the section heading verbatim on the page. This is intentionally
the *exact* structure of data/market_overview_categories.xlsx (Category /
Ticker / Display Name columns), which is the owner's working document for
reorganizing this page: the owner edits the spreadsheet, and this list (plus
the section layout on market.html, which renders sections dynamically from
whatever categories it finds -- no hardcoded per-category HTML/JS to update)
is rebuilt from it. Quote insertion order matches the list's order, so the
frontend does not need its own hardcoded display-order array either.

Crypto entries are ordered by market cap (largest first), per owner
instruction (2026-07-10) -- re-check and reorder if reshuffling this section,
market cap ranks change over time.

"Bonds" category entries carry an additional "unit": "pct" field, since their
"price" IS already a percentage (a Treasury yield), not a fund NAV -- the
frontend must not compute or display changePct for these (a small yield move
looks like a huge, misleading percentage move; e.g. 4.539 -> 4.569 is +0.66%
of the *number* but the actual, meaningful move is "+0.030 percentage
points"). The plain "change" field (price - prevClose) is already the
correct point-change for these and needs no special handling. Yield symbols:
2-Year via "2YY=F" (2-Year Yield Futures -- ^UST2Y/^US2Y do not exist on
Yahoo, this is the closest working proxy), 5-Year via "^FVX", 10-Year via
"^TNX", 30-Year via "^TYX". All four return the yield already in percent (no
/10 scaling needed, verified 2026-07-10) via the same Ticker.info fields as
everything else. Foreign sovereign yields and the 30-year mortgage rate are
NOT available via yfinance (every plausible ticker guess 404s) -- see
ROADMAP.md.

10-day RSI (2026-10-18): Yahoo entries carry "rsi10", a 10-day Wilder RSI on
the year of daily closes (the same method as fetch_etf_data.py's 14-day one;
10 days to match the TQQQ FTLT / Holy Grail signals). FRED entries have none:
an RSI of a monthly inflation print or a policy rate means nothing.

52-week range (2026-10-18): every quote carries "low52" and "high52". Yahoo's
fiftyTwoWeekLow/High is used for prices, but NOT for yields: it reported ^TNX's
52-week low as 0.0 (measured 2026-10-18), so "pct" entries, and any price
entry whose Yahoo range is missing or impossible, take the low/high of one
year of daily history instead. The range is widened to include the current
price, so the frontend marker can never fall outside the bar.

FRED entries (2026-10-18): the Fed Funds Rate, CPI and Core CPI are not on
Yahoo. Entries with a "fred" field (instead of "y") are read from the St. Louis
Fed's public CSV endpoint (fredgraph.csv, no API key):
  DFF       Effective Federal Funds Rate, daily ("transform": "level")
  CPIAUCSL  CPI, all items, monthly index    ("transform": "yoy")
  CPILFESL  Core CPI (less food and energy)  ("transform": "yoy")
CPI is an index level (e.g. 336.298), meaningless on its own, so "yoy" turns
it into the year-over-year inflation rate in percent. "change" is then the
move from the previous release, in percentage points, like a yield. These
quotes also carry "asOf" (the observation date, YYYY-MM-DD), since CPI is
monthly and DFF lags a day or two -- the page shows it so a reader does not
mistake last month's CPI for today's. "dp" in the list sets display decimals.

Output schema: { "updated": ISO, "source": "yahoo+fred",
  "quotes": { TICKER: { "name", "category", "unit", "dp", "price", "prevClose", "change",
                        "changePct", "low52", "high52", "rsi10", "asOf", "freq" }, ... } }
"unit" is only present ("pct") on yield/rate entries; absent means "price" (default).
"dp", "asOf" and "freq" ("monthly", on CPI and Core CPI) are only present where set/known.

Env:
  PAUSE   seconds to wait between symbols (default 0.5) -- be polite to Yahoo
"""

import csv
import datetime
import io
import json
import os
import sys
import time
import urllib.request

import yfinance as yf

LIST_PATH = "data/market_overview_list.json"
OUT_PATH = "data/market_overview.json"
PAUSE = float(os.environ.get("PAUSE", "0.5"))
# cosd trims the download to the last two years (enough for a YoY series plus
# its 52-week range). Do NOT set a custom User-Agent: FRED times out requests
# with browser-like or custom agents, but serves the default Python-urllib one
# (measured 2026-10-18).
FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}&cosd={}"


def num(x):
    """Coerce to a finite float, else None."""
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    if f != f or f in (float("inf"), float("-inf")):
        return None
    return f


def finish(rec):
    """Fill change/changePct from price/prevClose and widen the 52-week range to include price."""
    price, prev = rec.get("price"), rec.get("prevClose")
    rec.setdefault("change", None)
    rec.setdefault("changePct", None)
    if price is not None and prev not in (None, 0):
        rec["change"] = price - prev
        rec["changePct"] = (price / prev - 1) * 100
    lo, hi = rec.get("low52"), rec.get("high52")
    if price is not None and lo is not None and hi is not None:
        rec["low52"], rec["high52"] = min(lo, price), max(hi, price)
    return rec


def rsi(closes, n=10):
    """n-day Wilder RSI, the same method as fetch_etf_data.py's rsi14."""
    if len(closes) < n + 1:
        return None
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    up = sum(d for d in deltas[:n] if d > 0) / n
    down = -sum(d for d in deltas[:n] if d < 0) / n
    for d in deltas[n:]:
        up = (up * (n - 1) + max(d, 0)) / n
        down = (down * (n - 1) + max(-d, 0)) / n
    if down == 0:
        return 100.0
    return 100 - 100 / (1 + up / down)


def history_range(h):
    """52-week low/high from one year of daily bars, or (None, None)."""
    if h is None or h.empty:
        return None, None
    # Yahoo's futures history carries stray zero bars (2YY=F, 2026-10-18), so
    # only positive values count.
    lo, hi = h["Low"][h["Low"] > 0], h["High"][h["High"] > 0]
    if lo.empty or hi.empty:
        return None, None
    return num(lo.min()), num(hi.max())


def fetch(yahoo_symbol, is_pct=False):
    t = yf.Ticker(yahoo_symbol)
    info = t.info or {}
    price = num(info.get("regularMarketPrice")) or num(info.get("currentPrice"))
    prev = num(info.get("regularMarketPreviousClose")) or num(info.get("previousClose"))
    lo, hi = num(info.get("fiftyTwoWeekLow")), num(info.get("fiftyTwoWeekHigh"))
    info_ok = lo is not None and hi is not None and 0 < lo <= hi
    try:
        h = t.history(period="1y", interval="1d")
    except Exception as e:  # noqa: BLE001 - missing history must not lose the quote
        print(f"{yahoo_symbol}: history failed: {e!r}", file=sys.stderr)
        h = None
    closes = [] if h is None or h.empty else [c for c in (num(x) for x in h["Close"]) if c is not None and c > 0]
    rsi10 = rsi(closes)
    if is_pct or not info_ok:
        h_lo, h_hi = history_range(h)
        # History wins when usable; otherwise keep Yahoo's range if it is sane.
        # 2YY=F needs this: its daily history is all zeros (2026-10-18) while
        # its info range is plausible.
        if h_lo is not None and h_hi is not None:
            lo, hi = h_lo, h_hi
        elif not info_ok:
            lo, hi = None, None
    return finish({"price": price, "prevClose": prev, "low52": lo, "high52": hi, "rsi10": rsi10})


def fred_series(series_id):
    """[(date, value), ...] oldest first, skipping FRED's '.' missing markers."""
    start = (datetime.date.today() - datetime.timedelta(days=760)).isoformat()
    with urllib.request.urlopen(FRED_CSV.format(series_id, start), timeout=30) as r:
        rows = list(csv.reader(io.StringIO(r.read().decode("utf-8"))))
    out = []
    for row in rows[1:]:
        if len(row) >= 2 and num(row[1]) is not None:
            out.append((datetime.date.fromisoformat(row[0]), num(row[1])))
    return out


def fetch_fred(series_id, transform):
    obs = fred_series(series_id)
    if transform == "yoy":
        by_date = dict(obs)
        yoy = []
        for d, v in obs:
            # Feb 29 has no same-day match a year back; skip it rather than crash.
            base = by_date.get(d.replace(year=d.year - 1)) if not (d.month == 2 and d.day == 29) else None
            if base:
                yoy.append((d, (v / base - 1) * 100))
        obs = yoy
    if not obs:
        return finish({"price": None, "prevClose": None, "low52": None, "high52": None})
    last_date, price = obs[-1]
    prev = obs[-2][1] if len(obs) > 1 else None
    cutoff = last_date - datetime.timedelta(days=365)
    year = [v for d, v in obs if d > cutoff]
    rec = finish({"price": price, "prevClose": prev, "low52": min(year), "high52": max(year),
                  "asOf": last_date.isoformat()})
    # Monthly series (CPI) are dated the 1st of the month they measure; flag
    # them so the page shows "Sep 2026" rather than a misleading day.
    if len(obs) > 1 and (last_date - obs[-2][0]).days > 20:
        rec["freq"] = "monthly"
    # A rate's percent-of-percent move is misleading (see the Bonds note above).
    rec["changePct"] = None
    return rec


def main():
    now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    with open(LIST_PATH, encoding="utf-8") as f:
        listing = json.load(f)

    quotes = {}
    ok = 0
    for item in listing:
        ticker = item["t"]
        rec = {"name": item["n"], "category": item["category"]}
        if item.get("unit"):
            rec["unit"] = item["unit"]
        if item.get("dp") is not None:
            rec["dp"] = item["dp"]
        for attempt in range(3):
            try:
                if item.get("fred"):
                    rec.update(fetch_fred(item["fred"], item.get("transform", "level")))
                else:
                    rec.update(fetch(item["y"], item.get("unit") == "pct"))
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
                    rec.setdefault("low52", None)
                    rec.setdefault("high52", None)
                    rec.setdefault("rsi10", None)
                else:
                    time.sleep(2)
        quotes[ticker] = rec
        time.sleep(PAUSE)

    out = {"updated": now, "source": "yahoo+fred", "quotes": quotes}
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    print(f"Wrote {OUT_PATH}: {ok}/{len(listing)} symbols with price data.")


if __name__ == "__main__":
    main()
