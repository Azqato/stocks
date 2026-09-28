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

Every array lines up with "columns"; a missing value is null. Money is in the
company's reporting currency ("cur"), which can differ from the trading currency
for ADRs. The balance sheet's TTM column is the latest quarter's balance sheet.

Usage:
  python scripts/fetch_statements.py data/nasdaq100.json data/sp500.json ...

Env:
  PAUSE   seconds to wait between symbols (default 0.8) -- be polite to Yahoo
"""

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


def main():
    lists = sys.argv[1:] or ["data/nasdaq100.json"]
    symbols = []
    for path in lists:
        with open(path, encoding="utf-8") as f:
            for item in json.load(f):
                if item["t"] not in symbols:
                    symbols.append(item["t"])

    os.makedirs(OUT_DIR, exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    ok = 0
    for sym in symbols:
        for attempt in range(3):
            try:
                rec = fetch(sym)
                if rec["income"]["revenue"][0] is None and rec["income"]["revenue"][1] is None:
                    print(f"{sym}: no statements", file=sys.stderr)
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


if __name__ == "__main__":
    main()
