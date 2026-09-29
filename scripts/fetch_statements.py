#!/usr/bin/env python3
"""
Builds one financial-statements file per stock: data/statements/<TICKER>.json.

Added 2026-09-28 for Automate Fundamentals' Research page (RS3), which shows an
income statement, balance sheet, and cash-flow table for one company at a time,
so the data is split per ticker rather than bundled into the screener feeds.

Runs weekly in GitHub Actions (statements change once a quarter). Uses yfinance
(public Yahoo Finance data), like the screener feeds.

Each file:
  {
    "t": "AAPL", "updated": ISO, "source": "yahoo", "cur": "USD",
    "columns": ["TTM", "FY2025", "FY2024", "FY2023"],
    "income":   { "revenue": [...], "grossProfit": [...], "operatingIncome": [...],
                  "netIncome": [...], "epsDiluted": [...] },
    "balance":  { "cash": [...], "totalAssets": [...], "totalDebt": [...], "equity": [...] },
    "cashflow": { "operatingCashFlow": [...], "capex": [...], "freeCashFlow": [...],
                  "dividendsPaid": [...], "buybacks": [...] },
    "revCagr3y": 7.1,    # % a year, last fiscal year versus three years earlier
    "fcfGrowth": -9.2    # %, last fiscal year versus the year before
  }

A stock Yahoo publishes no statements for still gets a file, carrying
`"noStatements": true` and null arrays, so that --oldest-first ages it like any
other instead of treating it as missing and refetching it every night.

Every array lines up with "columns"; a missing value is null. Money is in the
company's reporting currency ("cur"), which can differ from the trading currency
for ADRs. The balance sheet's TTM column is the latest quarter's balance sheet.

Usage:
  python scripts/fetch_statements.py data/nasdaq100.json data/sp500.json ...
  python scripts/fetch_statements.py --universe --oldest-first 520

--universe takes the symbol list from the master universe (data/stocks/tickers.json)
instead of named list files, so statements cover every stock the screener knows
about rather than only the curated lists.

--oldest-first N fetches just the N symbols whose statement files are missing or
least recently updated, which is how the daily rolling refresh works (v4.9.2).
The whole universe is about 3,575 stocks and a statements fetch is three Yahoo
tables per symbol, far too slow for one nightly run, so a seventh of it goes each
night and every stock comes round within a week. Choosing by file age rather than
by a fixed day-of-week shard is deliberate: a new ticker is picked up on the next
run instead of waiting for its shard, and a night that fails simply leaves those
files oldest, so the next run retries them without any state to keep.

Env:
  PAUSE   seconds to wait between symbols (default 0.8) -- be polite to Yahoo
"""

import argparse
import datetime
import json
import os
import sys
import time

import yfinance as yf

from fetch_screener_data import num, yahoo_symbol

OUT_DIR = "data/statements"
PAUSE = float(os.environ.get("PAUSE", "0.8"))
YEARS = 3  # fiscal-year columns after TTM

# Output key -> Yahoo row names to try, in order.
INCOME = {
    "revenue": ["Total Revenue", "Operating Revenue"],
    "grossProfit": ["Gross Profit"],
    "operatingIncome": ["Operating Income", "Total Operating Income As Reported"],
    "netIncome": ["Net Income", "Net Income Common Stockholders"],
    "epsDiluted": ["Diluted EPS"],
}
BALANCE = {
    "cash": ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"],
    "totalAssets": ["Total Assets"],
    "totalDebt": ["Total Debt"],
    "equity": ["Stockholders Equity", "Common Stock Equity"],
}
CASHFLOW = {
    "operatingCashFlow": ["Operating Cash Flow"],
    "capex": ["Capital Expenditure"],
    "freeCashFlow": ["Free Cash Flow"],
    "dividendsPaid": ["Cash Dividends Paid", "Common Stock Dividend Paid"],
    "buybacks": ["Repurchase Of Capital Stock", "Common Stock Payments"],
}


def cell(df, names, col):
    """First non-missing value among the row names for one column, else None."""
    if df is None or df.empty or col not in df.columns:
        return None
    for name in names:
        if name in df.index:
            v = num(df.loc[name, col])
            if v is not None:
                return v
    return None


def fiscal_columns(df):
    """The newest YEARS annual columns, newest first (Yahoo sometimes adds an all-empty old year)."""
    if df is None or df.empty:
        return []
    cols = [c for c in df.columns if df[c].notna().any()]
    return sorted(cols, reverse=True)


def table(rows, ttm_df, ttm_col, annual_df, years):
    out = {}
    for key, names in rows.items():
        out[key] = [cell(ttm_df, names, ttm_col) if ttm_col is not None else None] + [
            cell(annual_df, names, y) if y is not None else None for y in years
        ]
    return out


def growth(new, old, years=1):
    """Annualized growth in percent; None unless both values are positive."""
    if new is None or old is None or new <= 0 or old <= 0:
        return None
    return ((new / old) ** (1 / years) - 1) * 100


def fetch(symbol):
    t = yf.Ticker(yahoo_symbol(symbol))
    annual_income = t.income_stmt
    annual_balance = t.balance_sheet
    annual_cash = t.cashflow

    years_all = fiscal_columns(annual_income)
    years = years_all[:YEARS] + [None] * (YEARS - len(years_all[:YEARS]))
    columns = ["TTM"] + [f"FY{y.year}" if y is not None else None for y in years]

    ttm_income = t.ttm_income_stmt
    ttm_cash = t.ttm_cashflow
    quarterly_balance = t.quarterly_balance_sheet
    ttm_i = fiscal_columns(ttm_income)[:1]
    ttm_c = fiscal_columns(ttm_cash)[:1]
    last_q = fiscal_columns(quarterly_balance)[:1]

    # The balance sheet's fiscal-year columns use its own dates, matched to the income statement's years.
    bal_years = [next((c for c in fiscal_columns(annual_balance) if y is not None and c.year == y.year), None) for y in years]
    cash_years = [next((c for c in fiscal_columns(annual_cash) if y is not None and c.year == y.year), None) for y in years]

    rec = {
        "t": symbol,
        "source": "yahoo",
        "columns": columns,
        "income": table(INCOME, ttm_income, ttm_i[0] if ttm_i else None, annual_income, years),
        "balance": table(BALANCE, quarterly_balance, last_q[0] if last_q else None, annual_balance, bal_years),
        "cashflow": table(CASHFLOW, ttm_cash, ttm_c[0] if ttm_c else None, annual_cash, cash_years),
    }

    # 3-year revenue CAGR: the newest fiscal year versus three years before it (needs four years).
    rev = [cell(annual_income, INCOME["revenue"], y) for y in years_all[:4]]
    rec["revCagr3y"] = growth(rev[0], rev[3], 3) if len(rev) == 4 else None
    fcf = rec["cashflow"]["freeCashFlow"]
    rec["fcfGrowth"] = growth(fcf[1], fcf[2])

    try:
        cur = (t.info or {}).get("financialCurrency")
    except Exception:
        cur = None
    rec["cur"] = "GBP" if cur in ("GBp", "GBX") else cur
    return rec


UNIVERSE_PATH = "data/stocks/tickers.json"


def universe_symbols():
    """Every ticker in the master universe, in part order."""
    with open(UNIVERSE_PATH, encoding="utf-8") as f:
        return list(json.load(f)["tickers"].keys())


def oldest_first(symbols, limit):
    """Return the `limit` symbols whose statement files are missing or oldest.

    A missing file sorts before every existing one, so a newly added ticker is
    always in the next run's batch.
    """
    def age_key(sym):
        path = os.path.join(OUT_DIR, sym + ".json")
        try:
            with open(path, encoding="utf-8") as f:
                return (1, json.load(f).get("updated") or "")
        except Exception:
            return (0, "")          # missing or unreadable: refresh first
    return sorted(symbols, key=age_key)[:limit]


def main():
    ap = argparse.ArgumentParser(description="Build per-stock financial statement files.")
    ap.add_argument("lists", nargs="*", help="constituent list JSON files")
    ap.add_argument("--universe", action="store_true",
                    help=f"take symbols from {UNIVERSE_PATH} instead of list files")
    ap.add_argument("--oldest-first", type=int, default=None, metavar="N",
                    help="fetch only the N symbols whose files are missing or oldest")
    args = ap.parse_args()

    if args.universe:
        symbols = universe_symbols()
    else:
        symbols = []
        for path in (args.lists or ["data/nasdaq100.json"]):
            with open(path, encoding="utf-8") as f:
                for item in json.load(f):
                    if item["t"] not in symbols:
                        symbols.append(item["t"])

    total = len(symbols)
    if args.oldest_first:
        symbols = oldest_first(symbols, args.oldest_first)
        print(f"Refreshing the {len(symbols)} least recently updated of {total} symbols.")

    os.makedirs(OUT_DIR, exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    ok = 0
    for sym in symbols:
        for attempt in range(3):
            try:
                rec = fetch(sym)
                if rec["income"]["revenue"][0] is None and rec["income"]["revenue"][1] is None:
                    # Still written, flagged, rather than skipped. Yahoo has no
                    # statements for plenty of real listings (most foreign ones
                    # among them), and leaving no file meant --oldest-first saw
                    # them as missing and refetched them every single night,
                    # starving the stocks that do have data. A flagged file ages
                    # like any other, so they come round once a week.
                    print(f"{sym}: no statements", file=sys.stderr)
                    rec["noStatements"] = True
                    rec["updated"] = now
                    with open(os.path.join(OUT_DIR, sym + ".json"), "w", encoding="utf-8") as f:
                        json.dump(rec, f, indent=1)
                        f.write("\n")
                    break
                rec["updated"] = now
                # Tickers are file names; dual-class dots stay (BRK.B.json), matching the feeds' keys.
                with open(os.path.join(OUT_DIR, sym + ".json"), "w", encoding="utf-8") as f:
                    json.dump(rec, f, indent=1)
                    f.write("\n")
                ok += 1
                break
            except Exception as e:  # noqa: BLE001 - keep going on any single-symbol failure
                if attempt == 2:
                    print(f"{sym}: failed after retries: {e!r}", file=sys.stderr)
                else:
                    time.sleep(2)
        time.sleep(PAUSE)

    print(f"Wrote {ok}/{len(symbols)} statement files to {OUT_DIR}/.")
    if args.oldest_first:
        have = len([f for f in os.listdir(OUT_DIR) if f.endswith(".json")])
        print(f"{have}/{total} symbols in the universe now have a statements file.")


if __name__ == "__main__":
    main()
