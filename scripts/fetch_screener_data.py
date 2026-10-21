#!/usr/bin/env python3
"""
Builds a screener data feed from a constituent list.

Runs in GitHub Actions on a daily cron. Uses yfinance (public Yahoo Finance
data) so there is no API key and no per-symbol subscription restriction -- the
whole list is refreshed every run.

Three feeds are produced by three staggered runs so the Nasdaq 100 (the
screener's default view) always refreshes first and never waits on the larger
jobs:
  --list data/nasdaq100.json --out data/screener.json          (23:00 UTC)
  --list data/sp500.json     --out data/screener_sp500.json     (23:30 UTC)
  --combined growth=data/vug.json --combined value=data/vtv.json \
      --combined dividend=data/vig.json --out data/screener_gvd.json  (00:00 UTC)
Defaults reproduce the original Nasdaq 100 behavior when run with no args.

Combined mode bundles several universes into one feed file, keyed by universe
name, with each universe holding the same {updated, source, stocks} object a
single-list feed has. Symbols appearing in more than one universe (the Growth,
Value, and Dividend lists overlap heavily) are fetched from Yahoo only once
per run.

Forward metrics use the CURRENT fiscal-year ("0y") analyst consensus to match
Seeking Alpha's "FWD" convention (not yfinance's forwardPE / "+1y" rows, which
look a year further out). P/E FWD uses Yahoo's priceEpsCurrentYear and PEG FWD
uses Yahoo's pegRatio, both of which track Seeking Alpha. EPS Growth FWD is
GAAP-basis and will differ from SA's Non-GAAP figure.

Cash and debt are reported in a company's `financialCurrency`, which is not
always the currency it trades in (a US ADR like PDD is priced in USD but reports
its balance sheet in CNY). `fetch()` converts cash/debt into the trading
currency via a live Yahoo FX quote so they line up with marketCap/price; see the
comment there. Same-currency listings (nearly all of them) are untouched.

Trailing ratios (peTTM, psTTM, evEbitda, divYield, opMargin, roe, debtToEquity,
currentRatio, fcfYield) are extra fields for Automate Fundamentals' Research page;
screener.html ignores them. v5.2.0 added a second, larger block of them for the
same reader: TTM amounts (revenue, ebitda, netIncome, fcf, eps, ev), ratios (pb,
evRevenue, pegTTM, roa, ebitdaMargin, quickRatio, payoutRatio, divYield5yAvg,
beta, shortFloat, heldInsiders, heldInstitutions, targetMean, analystRating,
analystCount) and a price trend (high52, low52, ma200, change52w).

CAREFUL with revTTM and epsTTM: despite the names, they are NOT trailing
12-month figures. They carry Yahoo's `revenueGrowth` and `earningsGrowth`, which
are the LATEST QUARTER against the same quarter a year earlier. Measured
2026-10-11 against `quarterly_income_stmt` for AAPL, MSFT, NVDA, KO and WMT:
`revenueGrowth` matched the latest quarter year over year to within 0.05
percentage points on all five (AAPL 16.40 vs 16.36, NVDA 105.90 vs 105.85) and
is nowhere near a TTM-over-prior-TTM figure. The keys are left as they are
because the feeds are read by two other repos; the fix belongs in their labels.

Also note `priceToBook` is Yahoo's own and is not always sane: it returns
0.00098 for BRK.B (2026-10-11), apparently dividing a per-share price by total
book equity. Stored as returned rather than second-guessed.

Output schema matches what screener.html reads:
  { "updated": ISO, "source": "yahoo", "stocks": { TICKER: {...}, ... } }

--part N (v4.9.0) fetches one part of the master universe instead of one list,
which is how a ticker held by four lists gets fetched once a day rather than
four times. The part's membership comes from data/stocks/tickers.json, built by
build_universe.py, and names come from the list files through its name_map();
the output carries the same schema plus a "part" field. Per-list feeds are then
derived from the parts by build_legacy_feeds.py, with no further fetching.

Env:
  PAUSE   seconds to wait between symbols (default 0.8) -- be polite to Yahoo
"""

import argparse
import datetime
import json
import os
import sys
import time
from zoneinfo import ZoneInfo

import yfinance as yf

DEFAULT_LIST = "data/nasdaq100.json"
ET = ZoneInfo("America/New_York")  # earnings dates are US Eastern
DEFAULT_OUT = "data/screener.json"
PARTS_DIR = "data/stocks"
PAUSE = float(os.environ.get("PAUSE", "0.8"))


# Domestic dual-class tickers Wikipedia writes with a dot but Yahoo expects a
# dash. An explicit set rather than a blanket ".", "-" replace: International
# (VXUS) symbols also contain dots as real exchange suffixes (e.g. "2330.TW",
# "HSBA.L") that must NOT be touched, and a suffix-length heuristic can't tell
# them apart (London's ".L" is one letter, same shape as a domestic ".B"/".A").
DASH_TICKERS = {"BRK.B", "BF.B"}


def yahoo_symbol(sym):
    """Yahoo uses a dash for the small set of domestic tickers Wikipedia writes with a dot."""
    return sym.replace(".", "-") if sym in DASH_TICKERS else sym


def num(x):
    """Coerce to a finite float, else None."""
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    if f != f or f in (float("inf"), float("-inf")):
        return None
    return f


# FX rates fetched once per run and reused. Keyed by "FROMTO" (e.g. "CNYUSD").
_FX_CACHE = {}


def fx_rate(frm, to):
    """Units of `to` per 1 unit of `frm` (e.g. fx_rate('CNY','USD') ~ 0.148).

    Returns 1.0 when the currencies match, else the live Yahoo FX quote, else
    None if it cannot be resolved. Yahoo publishes most pairs directly as
    "<FROM><TO>=X"; a few resolve only as the inverse, so try both. Cached per
    run to avoid re-hitting Yahoo for every ADR in the same currency.
    """
    if not frm or not to:
        return None
    if frm == to:
        return 1.0
    key = frm + to
    if key in _FX_CACHE:
        return _FX_CACHE[key]
    rate = None
    try:
        rate = num(yf.Ticker(frm + to + "=X").info.get("regularMarketPrice"))
    except Exception:
        rate = None
    if rate is None or rate == 0:
        try:
            inv = num(yf.Ticker(to + frm + "=X").info.get("regularMarketPrice"))
            rate = 1.0 / inv if inv else None
        except Exception:
            rate = None
    _FX_CACHE[key] = rate
    return rate


def estimate_growth(df, period):
    """Pull the analyst 'growth' value (a decimal) for a period row, e.g. '0y'."""
    try:
        return num(df.loc[period, "growth"])
    except Exception:
        return None


def estimate_avg(df, period):
    """Pull the analyst average estimate (e.g. EPS or revenue) for a period row."""
    try:
        return num(df.loc[period, "avg"])
    except Exception:
        return None


def quarterly_yoy(t):
    """Latest reported quarter against the same quarter a year earlier, from the
    quarterly income statement. Returns (revenue %, eps %); either may be None.

    This is a FALLBACK ONLY, called when Yahoo's own revenueGrowth /
    earningsGrowth came back empty. Yahoo suppresses those fields whenever the
    year-earlier quarter was negative, because a percentage change from a
    negative base has no agreed convention; measured 2026-10-13, that left
    epsTTM absent for 1,598 of the 3,465 Domestic names (46%), each taking a
    hard zero on a 15-point metric. The comparison computed here is the same one
    Yahoo publishes when it does publish it, so a derived value and a reported
    value mean the same thing and rank against each other fairly.

    Five columns are needed (the latest quarter and the one four back). Yahoo
    serves five or six, so a name with a short history returns None rather than
    a comparison against the wrong quarter.
    """
    try:
        q = t.quarterly_income_stmt
    except Exception:
        return None, None
    if q is None or getattr(q, "empty", True):
        return None, None

    def row(name):
        if name not in q.index:
            return None
        return [num(v) for v in q.loc[name].values]

    def yoy(vals):
        if not vals or len(vals) < 5:
            return None
        new, old = vals[0], vals[4]
        if new is None or old is None or old == 0:
            return None
        # Percent change against the absolute base, so a loss-to-profit flip
        # reads positive rather than inverting its sign (owner decision
        # 2026-10-13, chosen over a symmetric or floored denominator).
        return (new - old) / abs(old) * 100

    eps = row("Diluted EPS") or row("Basic EPS")
    return yoy(row("Total Revenue")), yoy(eps)


def statements_balance(symbol):
    """Cash and total debt from this symbol's statements file, if one exists.

    Fallback for the 27 Domestic names whose quote carries no totalCash or
    totalDebt. The statements files are written by fetch_statements.py on its
    own nightly rotation, so a value here can be up to a few days older than the
    quote it backs up; that is acceptable for a balance sheet, which only moves
    when a new report lands. Imported inside the function because
    fetch_statements imports this module at module level.
    """
    try:
        from fetch_statements import OUT_DIR, file_name
    except Exception:
        return None, None
    path = os.path.join(OUT_DIR, file_name(symbol))
    if not os.path.exists(path):
        return None, None
    try:
        with open(path, encoding="utf-8") as fh:
            bal = (json.load(fh) or {}).get("balance") or {}
    except Exception:
        return None, None

    def latest(key):
        vals = bal.get(key) or []
        return num(vals[0]) if vals else None

    return latest("cash"), latest("totalDebt")


def earnings_date(info):
    """The next earnings report, from the same quote (v5.12.0), for the
    Invests Earnings Calendar.

    earnDate     YYYY-MM-DD in US Eastern time, or None.
    earnDateEnd  last day of Yahoo's window when the date is not confirmed and
                 spans several days; otherwise None.
    earnTime     "bmo" (before the open, report before 09:30 ET), "amc" (after
                 the close, 15:00 ET or later), or None (during the session,
                 or unknown: Yahoo often stamps unconfirmed dates at midnight).
                 15:00, not 16:00: Yahoo converts future times with daylight
                 time, so after the clocks change a 16:00 report reads 15:00
                 EST (AAPL, AMD, NVDA for November 2026). Reports in the last
                 trading hour are rare enough to call after the close.
    earnEst      True when Yahoo marks the date as an estimate, not confirmed.
    Yahoo keeps the last report's timestamp until the next is announced, so a
    date in the past is normal; the calendar filters by date.
    """
    start = num(info.get("earningsTimestampStart")) or num(info.get("earningsTimestamp"))
    if start is None:
        return {"earnDate": None, "earnDateEnd": None, "earnTime": None, "earnEst": None}
    end = num(info.get("earningsTimestampEnd"))
    s = datetime.datetime.fromtimestamp(start, ET)
    e = datetime.datetime.fromtimestamp(end, ET) if end is not None else s
    est = bool(info.get("isEarningsDateEstimate"))
    hm = s.hour * 60 + s.minute
    time_ = None if est and hm == 0 else "bmo" if hm < 9 * 60 + 30 else "amc" if hm >= 15 * 60 else None
    return {"earnDate": s.date().isoformat(),
            "earnDateEnd": e.date().isoformat() if e.date() > s.date() else None,
            "earnTime": time_, "earnEst": est}


def fetch(symbol):
    t = yf.Ticker(yahoo_symbol(symbol))
    info = t.info or {}

    rec = {}
    rec["price"] = num(info.get("currentPrice")) or num(info.get("regularMarketPrice"))
    rec["marketCap"] = num(info.get("marketCap"))
    rec["cash"] = num(info.get("totalCash"))
    rec["debt"] = num(info.get("totalDebt"))
    # ISO currency code (e.g. "TWD", "EUR"); USD for domestic listings. Used by
    # the frontend to label $-formatted columns correctly for the International
    # universe, where Yahoo returns prices in each listing's local currency.
    cur = info.get("currency")

    # Daily change: latest price vs the prior session's close. The pipeline runs
    # after the US close, so this is that trading day's move.
    prev = num(info.get("regularMarketPreviousClose")) or num(info.get("previousClose"))

    # Yahoo quotes London-listed stocks in pence ("GBp"/"GBX"), not pounds --
    # but the SAME listing's marketCap/totalCash/totalDebt are already in
    # pounds (verified: HSBA.L marketCap == price-in-pounds * sharesOutstanding).
    # Normalize the quote fields here so nothing downstream needs to know
    # about this trap; the rest of the record is unaffected.
    if cur in ("GBp", "GBX"):
        cur = "GBP"
        if rec["price"] is not None:
            rec["price"] /= 100
        if prev is not None:
            prev /= 100
    rec["cur"] = cur

    # Cash and debt come from the financial statements, reported in the company's
    # `financialCurrency`, which is NOT always the currency it trades in: a US
    # ADR like PDD (Pinduoduo) is priced and market-capped in USD but reports its
    # balance sheet in CNY. Left raw, totalCash/totalDebt would be labeled with
    # the wrong currency and, worse, the Net Cash / Mkt Cap column would divide
    # CNY cash by a USD market cap (PDD showed ~$436B cash against a ~$120B cap).
    # Convert cash/debt into the trading currency so they line up with marketCap
    # and price. (The scored Cash-vs-Debt metric is cash/debt, a currency-neutral
    # ratio, so it was already correct; this fixes the display + Net Cash column.)
    # GBp London listings already normalized `cur` to GBP above and report in GBP,
    # so they match here and skip conversion.
    fin_cur = info.get("financialCurrency")
    if fin_cur in ("GBp", "GBX"):
        fin_cur = "GBP"
    if fin_cur and cur and fin_cur != cur and (rec["cash"] is not None or rec["debt"] is not None):
        rate = fx_rate(fin_cur, cur)
        if rate:
            if rec["cash"] is not None:
                rec["cash"] *= rate
            if rec["debt"] is not None:
                rec["debt"] *= rate
        else:
            # Can't trust a cross-currency figure we can't convert: null both so
            # the columns show "—" (and the ratio scores as missing) rather than
            # displaying a number that is silently off by an FX factor.
            print("  WARN %s: no FX rate %s->%s; nulling cash/debt" % (symbol, fin_cur, cur),
                  file=sys.stderr)
            rec["cash"] = None
            rec["debt"] = None
    # Same rule for the balance sheet: fall back to the statements file only
    # when the quote carried nothing. A cross-currency record that was nulled
    # above is deliberately NOT refilled here, because the statements figures
    # are in the reporting currency and would reintroduce the FX error.
    if rec["cash"] is None and rec["debt"] is None and not (fin_cur and cur and fin_cur != cur):
        s_cash, s_debt = statements_balance(symbol)
        if s_cash is not None or s_debt is not None:
            rec["cash"], rec["debt"] = s_cash, s_debt
            derived_cd = True
        else:
            derived_cd = False
    else:
        derived_cd = False

    rec["prevClose"] = prev
    if rec["price"] is not None and prev not in (None, 0):
        rec["changePct"] = (rec["price"] / prev - 1) * 100
    else:
        rec["changePct"] = None

    rec.update(earnings_date(info))

    rg = num(info.get("revenueGrowth"))
    rec["revTTM"] = rg * 100 if rg is not None else None
    eg = num(info.get("earningsGrowth"))
    rec["epsTTM"] = eg * 100 if eg is not None else None

    # Derive what the quote did not carry, and only then: the extra request is
    # never made for the symbols whose pull already worked. `derived` records
    # which fields are ours rather than Yahoo's, so the site can say so and the
    # PRD can account for them.
    derived = ["cash", "debt"] if derived_cd else []
    if rec["revTTM"] is None or rec["epsTTM"] is None:
        q_rev, q_eps = quarterly_yoy(t)
        if rec["revTTM"] is None and q_rev is not None:
            rec["revTTM"] = q_rev
            derived.append("revTTM")
        if rec["epsTTM"] is None and q_eps is not None:
            rec["epsTTM"] = q_eps
            derived.append("epsTTM")

    # Margins (TTM), for the scoring model's profitability pillar (v3.30.0).
    gm = num(info.get("grossMargins"))
    rec["grossMargin"] = gm * 100 if gm is not None else None
    nm = num(info.get("profitMargins"))
    rec["netMargin"] = nm * 100 if nm is not None else None

    # Forward figures use the CURRENT fiscal-year ("0y") consensus estimate to
    # match Seeking Alpha's "FWD" convention. yfinance's forwardPE / "+1y" rows
    # are one fiscal year further out, which reads systematically too low.
    earn = None
    rev = None
    try:
        earn = t.earnings_estimate
    except Exception:
        pass
    try:
        rev = t.revenue_estimate
    except Exception:
        pass

    # P/E FWD: Yahoo's priceEpsCurrentYear (price / current-FY EPS) matches
    # Seeking Alpha's "P/E FWD" to the cent. Fall back to price / 0y estimate,
    # then to forwardPE.
    price = rec["price"]
    pe = num(info.get("priceEpsCurrentYear"))
    if pe is None:
        eps_cur = estimate_avg(earn, "0y")
        if price is not None and eps_cur is not None and eps_cur > 0:
            pe = price / eps_cur
        else:
            pe = num(info.get("forwardPE"))
    rec["peFwd"] = pe

    # Revenue / EPS Growth FWD = current-FY ("0y") consensus growth.
    # NOTE: EPS Growth FWD is GAAP-basis and will differ from Seeking Alpha,
    # which uses Non-GAAP consensus (not exposed by yfinance).
    eg_fwd = estimate_growth(earn, "0y")
    rec["epsFwd"] = eg_fwd * 100 if eg_fwd is not None else None
    rg_fwd = estimate_growth(rev, "0y")
    rec["revFwd"] = rg_fwd * 100 if rg_fwd is not None else None

    # PEG FWD: Yahoo's pegRatio incorporates a longer-term growth rate and
    # tracks Seeking Alpha's PEG (FWD) closely (SA's exact 3-5yr long-term
    # growth input is not exposed by yfinance). Fall back to trailingPegRatio,
    # then to the 1-yr forward PEG (P/E / EPS growth).
    peg = num(info.get("pegRatio"))
    if peg is None or peg == 0:
        peg = num(info.get("trailingPegRatio"))
    if (peg is None or peg == 0) and rec["peFwd"] is not None and rec["epsFwd"] not in (None, 0) and rec["epsFwd"] > 0:
        peg = rec["peFwd"] / rec["epsFwd"]
    rec["pegFwd"] = peg

    # Trailing ratios Yahoo computes itself (added 2026-09-28 for Automate Fundamentals Research, RS3).
    # Units: margins/ROE come as decimals and are stored as percents like the other margins;
    # Yahoo already reports dividendYield and debtToEquity in percent, so D/E is divided by 100
    # to store a plain multiple (0.78x, not 78).
    rec["peTTM"] = num(info.get("trailingPE"))
    rec["psTTM"] = num(info.get("priceToSalesTrailing12Months"))
    rec["evEbitda"] = num(info.get("enterpriseToEbitda"))
    rec["divYield"] = num(info.get("dividendYield"))
    om = num(info.get("operatingMargins"))
    rec["opMargin"] = om * 100 if om is not None else None
    roe = num(info.get("returnOnEquity"))
    rec["roe"] = roe * 100 if roe is not None else None
    de = num(info.get("debtToEquity"))
    rec["debtToEquity"] = de / 100 if de is not None else None
    rec["currentRatio"] = num(info.get("currentRatio"))
    # FCF yield = TTM free cash flow / market cap. FCF is in the reporting currency, so convert it
    # to the trading currency first, exactly as cash/debt above.
    fcf = num(info.get("freeCashflow"))
    if fcf is not None and fin_cur and cur and fin_cur != cur:
        rate = fx_rate(fin_cur, cur)
        fcf = fcf * rate if rate else None
    cap = rec["marketCap"]
    rec["fcfYield"] = fcf / cap * 100 if fcf is not None and cap else None

    # Fields added 2026-10-11 (v5.2.0) for Automate Fundamentals' metrics
    # audit (its PRD, FM2/FM3/FM5). Every one comes out of the same `info` call
    # above, so they cost no extra Yahoo requests. The screener ignores them,
    # as it does the v4.3.6 trailing ratios.

    def money(key):
        """A reporting-currency amount from `info`, converted to the trading currency.

        Same trap as cash/debt: these come off the statements in
        `financialCurrency`, so an ADR like NVO reports revenue in DKK against a
        USD price. Null rather than wrong when the rate cannot be resolved.
        """
        v = num(info.get(key))
        if v is None or not (fin_cur and cur) or fin_cur == cur:
            return v
        rate = fx_rate(fin_cur, cur)
        return v * rate if rate else None

    def pct(key):
        """A fraction from `info`, stored as a percent like the margins above."""
        v = num(info.get(key))
        return v * 100 if v is not None else None

    # TTM amounts (FM2). Automate Fundamentals divides these against each other
    # for margins and multiples, so they must share one currency.
    rec["revenue"] = money("totalRevenue")
    rec["ebitda"] = money("ebitda")
    rec["netIncome"] = money("netIncomeToCommon")
    rec["ev"] = money("enterpriseValue")
    rec["fcf"] = fcf                      # already converted for fcfYield above
    rec["eps"] = num(info.get("trailingEps"))   # per share, already in the trading currency

    # Ratios (FM3). Currency-neutral, so no conversion.
    rec["pb"] = num(info.get("priceToBook"))
    rec["evRevenue"] = num(info.get("enterpriseToRevenue"))
    rec["pegTTM"] = num(info.get("trailingPegRatio"))
    rec["roa"] = pct("returnOnAssets")
    # Yahoo answers 0.0 rather than null for a company it has no EBITDA for
    # (every bank: HSBA.L, 2026-10-11), which would read as a real zero margin.
    rec["ebitdaMargin"] = pct("ebitdaMargins") if rec["ebitda"] is not None else None
    rec["quickRatio"] = num(info.get("quickRatio"))
    rec["payoutRatio"] = pct("payoutRatio")
    # Already a percent on Yahoo's side, like dividendYield; do not scale it.
    rec["divYield5yAvg"] = num(info.get("fiveYearAvgDividendYield"))
    rec["beta"] = num(info.get("beta"))
    rec["shortFloat"] = pct("shortPercentOfFloat")
    rec["heldInsiders"] = pct("heldPercentInsiders")
    rec["heldInstitutions"] = pct("heldPercentInstitutions")
    rec["targetMean"] = num(info.get("targetMeanPrice"))
    rec["analystRating"] = num(info.get("recommendationMean"))   # 1 strong buy to 5 sell
    rec["analystCount"] = num(info.get("numberOfAnalystOpinions"))

    # Price trend (FM5). Same currency as price, so the GBp halving above applies.
    rec["high52"] = num(info.get("fiftyTwoWeekHigh"))
    rec["low52"] = num(info.get("fiftyTwoWeekLow"))
    rec["ma200"] = num(info.get("twoHundredDayAverage"))
    if cur == "GBP" and info.get("currency") in ("GBp", "GBX"):
        for k in ("high52", "low52", "ma200", "targetMean"):
            if rec[k] is not None:
                rec[k] /= 100
    rec["change52w"] = pct("52WeekChange")

    # psTTM above is Yahoo's priceToSalesTrailing12Months, which for an ADR
    # divides a trading-currency price by reporting-currency sales per share:
    # NVO read 0.52 against a true 3.46 (measured 2026-10-11, DKK sales against
    # a USD price). Now that revenue is FX-converted, derive it instead whenever
    # the two currencies differ. This is the same class of bug as peFwd in the
    # PRD's Documentation Versus Reality item 9, which is still open because
    # there is no converted forward EPS to derive a replacement from.
    if fin_cur and cur and fin_cur != cur:
        rec["psTTM"] = (rec["marketCap"] / rec["revenue"]
                        if rec.get("marketCap") and rec.get("revenue") else None)

    # Only when something was derived, so the parts files do not grow a key per
    # record for the majority of symbols that need no fallback at all.
    if derived:
        rec["derived"] = derived

    return rec


def build_stocks(listing, now, cache):
    """Fetch every symbol in a listing, reusing records already fetched this run."""
    stocks = {}
    ok = 0
    for item in listing:
        sym = item["t"]
        if sym in cache:
            rec = dict(cache[sym])
            rec["name"] = item["n"]  # each list keeps its own curated name
            stocks[sym] = rec
            if rec.get("price") is not None:
                ok += 1
            continue
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
        cache[sym] = rec
        time.sleep(PAUSE)
    return stocks, ok


def part_listing(part):
    """Return [{"t","n"}, ...] for one part of the master universe.

    Order follows tickers.json, which build_universe.py writes in list-priority
    order, so a part file's key order is stable from day to day and its git
    diffs stay readable (v4.4.0 mines those diffs).
    """
    import build_universe

    part_of = build_universe.part_map()
    names = build_universe.name_map()
    listing = [{"t": t, "n": names.get(t, t)}
               for t, p in part_of.items() if p == part]
    if not listing:
        sys.exit(f"ABORT: part {part} holds no tickers; "
                 f"run build_universe.py first (or check --part).")
    return listing


def main():
    ap = argparse.ArgumentParser(description="Build a screener data feed from a constituent list.")
    ap.add_argument("--list", dest="list_path", default=DEFAULT_LIST,
                    help=f"constituent list JSON (default {DEFAULT_LIST})")
    ap.add_argument("--combined", action="append", default=[], metavar="NAME=LIST",
                    help="bundle several universes into one feed keyed by NAME "
                         "(repeatable, e.g. --combined growth=data/vug.json); overrides --list")
    ap.add_argument("--part", type=int, default=None, metavar="N",
                    help="fetch part N of the master universe instead of a list; "
                         f"writes {PARTS_DIR}/part-NN.json unless --out says otherwise")
    ap.add_argument("--out", dest="out_path", default=None,
                    help=f"output feed JSON (default {DEFAULT_OUT})")
    args = ap.parse_args()

    now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    cache = {}  # symbol -> fetched record, shared across universes in one run

    if args.part is not None and args.combined:
        sys.exit("--part and --combined are mutually exclusive.")
    out_path = args.out_path or (f"{PARTS_DIR}/part-{args.part:02d}.json"
                                 if args.part is not None else DEFAULT_OUT)

    if args.part is not None:
        listing = part_listing(args.part)
        stocks, ok = build_stocks(listing, now, cache)
        out = {"updated": now, "source": "yahoo", "part": args.part, "stocks": stocks}
        summary = f"part {args.part}: {ok}/{len(listing)}"
        os.makedirs(PARTS_DIR, exist_ok=True)
    elif args.combined:
        universes = {}
        totals = []
        for spec in args.combined:
            name, _, list_path = spec.partition("=")
            if not name or not list_path:
                sys.exit(f"Bad --combined spec {spec!r}; expected NAME=LIST.")
            with open(list_path, encoding="utf-8") as f:
                listing = json.load(f)
            stocks, ok = build_stocks(listing, now, cache)
            universes[name] = {"updated": now, "source": "yahoo", "stocks": stocks}
            totals.append(f"{name} {ok}/{len(listing)}")
        out = {"updated": now, "source": "yahoo", "universes": universes}
        summary = "; ".join(totals)
    else:
        with open(args.list_path, encoding="utf-8") as f:
            listing = json.load(f)
        stocks, ok = build_stocks(listing, now, cache)
        out = {"updated": now, "source": "yahoo", "stocks": stocks}
        summary = f"{ok}/{len(listing)}"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    print(f"Wrote {out_path}: {summary} symbols with price data.")


if __name__ == "__main__":
    main()
