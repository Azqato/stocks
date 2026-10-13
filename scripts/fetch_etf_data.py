#!/usr/bin/env python3
"""
Builds the ETFs screener data feed from the fixed fund list.

Runs in GitHub Actions on a daily cron (Mon-Fri 23:15 UTC, between the
Nasdaq 100 and S&P 500 stock-feed runs). Uses yfinance (public Yahoo Finance
data), so there is no API key. The fund list (data/etfs.json) is owner-curated
and hand-edited only -- there is no auto-sync for this universe.

The ETF universe is scored on technicals, long-term performance, yield, and
cost, not fundamentals, so this script shares no field logic with
fetch_screener_data.py:

  - Quote and fund facts from Ticker.info: price, previous close, AUM
    (totalAssets), yield (dividendYield -- NOT trailingAnnualDividendYield,
    which is missing or wrong for several funds), and expense ratio
    (netExpenseRatio). All verified present for the 10 funds (2026-07-03).
  - Everything else from one 11-year daily history call per fund:
      * Total returns (YTD, 1y, 5y, 10y) on dividend-adjusted closes
        (auto_adjust=True), i.e. a total-return basis.
      * RSI (14-day Wilder), 52-week high/low, and the 20/100/200-day
        moving averages on unadjusted closes (standard charting basis).

Output schema matches the single-list stock feeds:
  { "updated": ISO, "source": "yahoo", "stocks": { TICKER: {...}, ... } }

Env:
  PAUSE   seconds to wait between symbols (default 0.8) -- be polite to Yahoo
"""

import datetime
import json
import os
import sys
import time

import yfinance as yf

LIST_PATH = "data/etfs.json"
OUT_PATH = "data/screener_etfs.json"
PAUSE = float(os.environ.get("PAUSE", "0.8"))


def num(x):
    """Coerce to a finite float, else None."""
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    if f != f or f in (float("inf"), float("-inf")):
        return None
    return f


def rsi14(closes):
    """14-day Wilder RSI from a list of closes (needs 15+; feed it ~1y)."""
    if len(closes) < 15:
        return None
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    up = sum(d for d in deltas[:14] if d > 0) / 14
    down = -sum(d for d in deltas[:14] if d < 0) / 14
    for d in deltas[14:]:
        up = (up * 13 + max(d, 0)) / 14
        down = (down * 13 + max(-d, 0)) / 14
    if down == 0:
        return 100.0
    return 100 - 100 / (1 + up / down)


def total_return(closes, index, last, years):
    """Percent total return vs the closest close on/before N calendar years ago."""
    target = index[-1] - datetime.timedelta(days=round(years * 365.25))
    base = None
    for ts, close in zip(index, closes):
        if ts <= target:
            base = close
        else:
            break
    # Require the history to actually reach back: the base must sit within a
    # few weeks of the target date, or the fund is younger than the window.
    if base is None or (index[0] - target).days > 21:
        return None
    if base == 0:
        return None
    return (last / base - 1) * 100


def fetch(symbol):
    t = yf.Ticker(symbol)
    info = t.info or {}
    rec = {}

    rec["price"] = num(info.get("regularMarketPrice")) or num(info.get("currentPrice"))
    prev = num(info.get("regularMarketPreviousClose")) or num(info.get("previousClose"))
    rec["prevClose"] = prev
    if rec["price"] is not None and prev not in (None, 0):
        rec["changePct"] = (rec["price"] / prev - 1) * 100
    else:
        rec["changePct"] = None

    rec["aum"] = num(info.get("totalAssets"))
    rec["yieldPct"] = num(info.get("dividendYield"))       # already in percent (e.g. 0.98)
    rec["expenseRatio"] = num(info.get("netExpenseRatio")) # already in percent (e.g. 0.0945)

    # Total returns: dividend-adjusted closes = total-return basis.
    adj = t.history(period="11y", interval="1d", auto_adjust=True)["Close"].dropna()
    closes = [num(c) for c in adj]
    index = [ts.to_pydatetime().replace(tzinfo=None) for ts in adj.index]
    last = closes[-1] if closes else None
    if last is not None:
        rec["ret1y"] = total_return(closes, index, last, 1)
        rec["ret5y"] = total_return(closes, index, last, 5)
        rec["ret10y"] = total_return(closes, index, last, 10)
        # YTD vs the prior year's final close.
        year = index[-1].year
        base = None
        for ts, close in zip(index, closes):
            if ts.year < year:
                base = close
        rec["ytd"] = (last / base - 1) * 100 if base not in (None, 0) else None
    else:
        rec["ret1y"] = rec["ret5y"] = rec["ret10y"] = rec["ytd"] = None

    # Technicals: unadjusted closes (standard charting basis).
    hist = t.history(period="1y", interval="1d", auto_adjust=False)
    raw = hist["Close"].dropna()
    raw_closes = [num(c) for c in raw]
    rec["rsi"] = rsi14(raw_closes)

    # The 52-week range is INTRADAY (v5.3.0), the conventional definition and
    # the one Yahoo's own fiftyTwoWeekLow/High reports. These were the min and
    # max of the daily closes, which understates the range and therefore
    # misplaces a fund inside it: MGK read a low of 70.70 against a true 63.74
    # (measured 2026-10-13), and the 52-week range position is 20 of the 100
    # points in the ETF model. Falls back to the closes if the frame has no
    # high/low columns.
    lows = [num(v) for v in hist["Low"].dropna()] if "Low" in hist else []
    highs = [num(v) for v in hist["High"].dropna()] if "High" in hist else []
    lows = [v for v in lows if v is not None] or raw_closes
    highs = [v for v in highs if v is not None] or raw_closes
    rec["wk52Low"] = min(lows) if lows else None
    rec["wk52High"] = max(highs) if highs else None
    raw_last = raw_closes[-1] if raw_closes else None
    for n in (20, 100, 200):
        key = f"pctVs{n}dma"
        if raw_last is not None and len(raw_closes) >= n:
            ma = sum(raw_closes[-n:]) / n
            rec[key] = (raw_last / ma - 1) * 100 if ma else None
        else:
            rec[key] = None

    return rec


def main():
    now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    with open(LIST_PATH, encoding="utf-8") as f:
        listing = json.load(f)

    stocks = {}
    ok = 0
    for item in listing:
        sym = item["t"]
        rec = {"t": sym, "name": item["n"]}
        for attempt in range(3):
            try:
                rec.update(fetch(sym))
                rec["priceUpdated"] = now
                rec["fundamentalsUpdated"] = now
                if rec.get("price") is not None:
                    ok += 1
                break
            except Exception as e:  # noqa: BLE001 - keep going on any single-symbol failure
                if attempt == 2:
                    print(f"{sym}: failed after retries: {e!r}", file=sys.stderr)
                else:
                    time.sleep(2)
        stocks[sym] = rec
        time.sleep(PAUSE)

    out = {"updated": now, "source": "yahoo", "stocks": stocks}
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    print(f"Wrote {OUT_PATH}: {ok}/{len(listing)} funds with price data.")


if __name__ == "__main__":
    main()
