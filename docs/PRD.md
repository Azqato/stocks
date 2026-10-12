# PRD - Azqato Stocks Data Feed

**Version:** 5.1.0
**Status:** Current
**Author:** Azqato
**Last Updated:** 2026-10-11

---

## What This Repo Is

Since v5.0.0 (2026-10-02) this repository is a **data feed**, not a website. The methodology pages, the screener and Market Overview moved to Azqato Invests (azqato.com/invests/, built from the `azqato.github.io` repo). What stays here:

- **Scheduled jobs** (`.github/workflows/`) and the **scripts** they run (`scripts/`), which fetch public Yahoo Finance, Nasdaq, State Street and Vanguard data and commit it.
- **The data** (`data/`), served by GitHub Pages at `azqato.github.io/stocks/data/` and read by:
  - Azqato Invests' Screener (`screener*.json`, `stocks/`, `vti.json`) and Market Overview (`market_overview.json`)
  - Automate Fundamentals' Research page (`statements/`)
- **Redirect pages** at the old page addresses (`index.html`, `screener.html`, `market.html`, `metrics.html`, `philosophy.html`, `indices.html`, `faq.html`, `finviz.html`, `seekingalpha.html`). Each sends visitors to its Invests page in one hop. Never reuse these addresses.
- **Documentation**: `README.md`, `docs/PRD.md` (this file), `docs/PATCHNOTES.md`, `docs/TODO.md`.

The product side (who the site is for, page content, design, SEO, roadmap) lives in the Azqato Invests PRD (`azqato.github.io` repo, `docs/PRD.md`). Versions of this file before 5.1.0 hold the full history of the old site and stay in git.

---

## Runbook

### Local Setup

1. Install Python 3.12+ and `pip install yfinance==1.4.1` (the weekly constituent sync also needs `requests pandas lxml openpyxl`).
2. Clone: `git clone https://github.com/Azqato/stocks.git && cd stocks`
3. Enable the push hook once per clone: `git config core.hooksPath .githooks`

There is no build step. A push to `main` publishes `data/` through GitHub Pages within a few minutes.

### Data Pipeline (Automated)

Four data pipelines are refreshed automatically, staggered so the default Nasdaq 100 view always has priority (the four per-list stock feeds became one parts pipeline in v4.9.4). Three of them run once per trading day, anchored 30 minutes after the **latest possible** US market close in UTC terms rather than a fixed Eastern-clock offset: close is always 4:00pm US Eastern, which is 21:00 UTC in winter (EST, UTC-5) but only 20:00 UTC in summer (EDT, UTC-4): GitHub Actions cron is UTC-only and does not observe DST, so anchoring to the winter (later-in-UTC) close guarantees at least a 30-minute buffer after close year-round, growing to 90 minutes in summer. Every job in that daily chain lands on the same calendar day (no more day-rollover crons). Two things sit outside it. Market Overview (added 2026-07-10) runs **three times per trading day** rather than once after close, per direct owner instruction. And the whole-market half of the stock data runs **weekly on Sunday** (v4.9.4), because its roughly 2,950 extra stocks are a research pool whose fundamentals move quarterly, and a Sunday run gives every part the same Friday close:

**Every cron fires on an odd, off-peak minute, never `:00` or `:30`** (v4.1.8). GitHub's scheduler queues all repositories' crons globally, so the top of the hour is its most congested slot: jobs scheduled there are delayed and, under enough load, dropped entirely. On 2026-07-10 the three Market Overview runs fired 112, 85 and 58 minutes late; on 2026-07-13 the 15:00 run never fired at all, leaving the page showing Friday's data on a Monday morning. Odd minutes are GitHub's own documented recommendation. **Do not move these back to `:00`/`:30`.**

- **All stock universes** (`data/stocks/part-*.json`, and the four per-list feeds derived from them): **two cadences via `.github/workflows/stock-data.yml`** (v4.9.4). **Daily**, trading days (Mon-Fri) at 21:37 UTC, covering only the parts the seven curated universes occupy, about 1,000 symbols in one wave of the matrix, roughly 11 minutes. **Weekly**, Sundays at 21:17 UTC, covering every part, about 3,575 symbols, roughly 21 minutes, which is when the whole-market universe refreshes. The daily run's part list is read from `data/stocks/index.json` by `build_universe.py --parts-for`, never hardcoded, because sticky part assignment can place a newly added index member in a high part. A `needs:`-gated job then derives `screener.json`, `screener_sp500.json`, `screener_gvd.json` and `screener_intl.json` from the parts with no further fetching, each stamped with the oldest part it was built from rather than its own write time, so a failed part job cannot make a feed look fresh (v4.9.5), so those four files keep their exact schema and their git history (v4.4.0 mines it)
- **Market Overview** (`data/market_overview.json`): trading days (Mon-Fri) at 15:07, 19:07, and 22:07 UTC via `.github/workflows/market-overview.yml`, shortly after the open, midday, and shortly after the close, so this page reads as a same-day check-in rather than a close-of-business number. A price/change-only snapshot (`scripts/fetch_market_overview.py`), independent of the scored ETFs universe so it isn't affected by any future change to that list. The 22:07 run lands near the ETFs job below; both share the `screener-data` concurrency group with `cancel-in-progress: false`, so they queue rather than race
- **ETFs** (`data/screener_etfs.json`): trading days (Mon-Fri) at 22:12 UTC via `.github/workflows/screener-data-etfs.yml` (a 36-symbol fetch that slots between the two index jobs; run by `scripts/fetch_etf_data.py`, which shares no field logic with the stock fetcher)
- **International** (`data/screener_intl.json`): derived from the parts like the other three, and still the only stock feed carrying a `cur` field (native ISO currency code) that the frontend uses to label Price/Mkt Cap/Cash/Debt in the listing's own currency instead of USD
- **Constituent sync**: Saturdays at 23:17 UTC via `.github/workflows/constituents.yml`; regenerates a feed only if a list's membership changed. Sources below
- **Financial statements** (`data/statements/<TICKER>.json`): **nightly at 02:17 UTC** via `.github/workflows/statements.yml` (v5.2.0), rolling rather than per-list. `fetch_statements.py --universe --oldest-first 1000` refreshes the 1,000 symbols whose files are missing or least recently updated, so the whole 3,577-stock universe comes round in 3.6 days and a newly added index member is picked up the next night (a missing file sorts ahead of every existing one). Before v5.2.0 this ran weekly over the five curated US lists only, which left the roughly 3,050 stocks outside them with no statements at all. 02:17 is the one slot in the day with nothing on either side of it, and the job now carries `stock-data.yml`'s rebase-retry push loop, so a commit landing from another workflow no longer throws away an hour of fetching. **One file name is not simply the ticker**: a ticker colliding with a Windows reserved device name (`CON`, `PRN`, `AUX`, `NUL`, `COM0-9`, `LPT0-9`) is written with a trailing underscore, so Concentra Group Holdings is `data/statements/CON_.json`. This is not cosmetic. Windows reserves those names with any extension, and git on Windows refuses to check such a path out at all, so a single one of these files makes the whole repo unclonable there rather than merely unreadable; it happened for real on 2026-10-11 when the first whole-universe pass reached CON. **Any reader resolving a ticker to a file name must apply the same rule.** The `t` field inside the record always holds the real ticker. See `file_name()` in `fetch_statements.py`. This is also the only data job outside the `screener-data` concurrency group

#### Constituent sources (v4.1.8)

Each index list has a **primary source and a fallback**, so one source breaking no longer stops the sync. A source that returns a malformed or out-of-band list is rejected and the next one is tried; only if *every* source for a list fails does the job abort (it never clobbers a good list with bad data).

| List | Primary | Fallback |
|------|---------|----------|
| `data/nasdaq100.json` | Nasdaq's official index API (`api.nasdaq.com/api/quote/list-type/nasdaq100`) | Slickcharts |
| `data/sp500.json` | State Street's published SPY holdings (`.xlsx`, needs `openpyxl`) | Slickcharts |
| `data/vug.json`, `vtv.json`, `vig.json`, `vxus.json` | Vanguard's holdings API | (none) |
| `data/etfs.json` | Hand-curated, never synced | none |

**Wikipedia was dropped as a source on 2026-07-13.** The Nasdaq-100 article's components table was removed from the page entirely, so the scraper could no longer find it and the weekly job failed, silently, since nothing was watching it. It had been stale long enough that the index list was missing two real constituents (HONA, SPCX). Scraping a single editable page was the underlying fragility; the fallback chain above replaces it.

**QQQ holdings are deliberately *not* used** for the Nasdaq 100: Invesco returns HTTP 406 to non-browser clients, so it cannot be fetched from CI at all. Nasdaq's own index API is the more authoritative source anyway. **yfinance cannot substitute** for either index: `Ticker(...).funds_data.top_holdings` returns only the **top 10** holdings, not the full constituent list.

VXUS holdings are additionally resolved from ISIN to a suffixed Yahoo symbol via `data/vxus_map.json` (a committed resolution cache with a `manual` override block).
- **Trigger manually:** GitHub Actions tab → the relevant workflow → Run workflow (use this to seed a feed the first time)
- **Run the parts pipeline locally (v4.9.0):** `python3 scripts/build_universe.py` to refresh `data/stocks/index.json` + `tickers.json`, then `python3 scripts/fetch_screener_data.py --part 1` per part (about 10 minutes for 500 symbols), then `python3 scripts/build_legacy_feeds.py` to derive the four per-list feeds from the parts with no further fetching (`--dry-run` reports what each feed would contain). The GitHub workflow is `stock-data.yml`.
- **Run locally:** `python3 scripts/fetch_screener_data.py --list data/nasdaq100.json --out data/screener.json` (the `--list`/`--out` args default to the Nasdaq 100; point them at `data/sp500.json` / `data/screener_sp500.json` for the S&P 500, or `data/vxus.json` / `data/screener_intl.json` for International). For the combined feed: `python3 scripts/fetch_screener_data.py --combined growth=data/vug.json --combined value=data/vtv.json --combined dividend=data/vig.json --out data/screener_gvd.json`
- **Output:** each feed holds its list's tickers with price, market cap, cash, debt, growth metrics, P/E, PEG, currency code, and timestamps; the GVD feed nests one `{updated, source, stocks}` object per universe under a `universes` key
- **No API key required** for the yfinance pipeline (yfinance is pinned to 1.4.1 in all workflows)


### Workflow Failure Detection

Two independent layers, added in v4.3.5 after a second multi-week silent outage. Neither replaces the other: the CI layer catches failures when nobody is working in the repo, and the local layer catches them at the moment someone is about to build on top of a broken pipeline.

**CI layer, `.github/workflows/alert-on-failure.yml`.** A single `workflow_run` listener covering every other workflow. On a failure it opens a GitHub issue titled `CI failure: <workflow name>`, or comments on the existing open one so a job that fails weekly does not bury the issue list. Closing the issue is the "dealt with" signal; the next failure after that opens a fresh one.

> `workflow_run` matches on a workflow's **`name:` field, not its filename**. A typo or a renamed workflow silently watches nothing, which is the same class of invisible failure this is meant to catch, so `check_workflow_health.py` verifies the watch list against the workflow files on every push. Six of the seven names were guessed wrong on the first attempt at writing that list, which is why the check exists.

**Local layer, `.githooks/pre-push` plus `scripts/check_workflow_health.py`.** Prints each workflow's latest run state before a push. It flags two separate conditions, because the two historical outages were one of each: a run that **failed** (the Vanguard break, which ran and failed weekly), and a run that is **stale** (the Wikipedia break, where the job stopped producing anything). GitHub's own `pages-build-deployment` is included, since a failed site deploy is just as invisible. It reads the public Actions API and needs no token.

- **Enable in a clone** (git does not copy hooks): `git config core.hooksPath .githooks`
- **Run by hand:** `python3 scripts/check_workflow_health.py` (add `--quiet` to print only when something is wrong)
- **It never blocks a push.** The push is often the fix, and a check that blocks work gets disabled within a week. It warns and exits 0; only the standalone script exits 1.
- **Staleness thresholds** live in `MAX_AGE_HOURS` and carry deliberate slack for GitHub's scheduler firing hours late (see Known Technical Debt). Tighten them only alongside that entry.

**Still owner-only:** repository Actions failure emails are an account notification setting (github.com → Settings → Notifications → Actions), not something the repo can turn on for you.

### Ad Hoc ETF Holdings Analysis

`scripts/analyze_etf_holdings.py` rates the top-10 holdings of any list of ETFs using the **individual-stock** scoring model, then rolls the holdings up into one number per fund. Added v4.2.0 (2026-09-21) after the analysis was run by hand and the owner asked for it to be repeatable on funds supplied later.

- **Run:** `python3 scripts/analyze_etf_holdings.py SCHD SCHG FNDX` (any number of tickers; add `--out report.md` to write the markdown instead of printing it, and `--json raw.json` to dump holdings, fundamentals, scores, and per-metric points for further work)
- **Baseline:** by default each holding is ranked against the committed daily feed for its market, domestic against `data/screener_sp500.json` and foreign-listed against `data/screener_intl.json`, with `--universe` and `--intl-universe` overriding either (shorthands `sp500`, `nasdaq100`, `intl`, `growth`, `value`, `dividend`, or a path)
- **Output:** one markdown table per fund (ticker, company, fund weight, score, tier, and the pool it was ranked in), an overall weighted-average rating per fund, and a summary table ranking the funds
- **Not on a cron, not wired into any feed.** It reads nothing from `data/` and writes nothing into it.

**This is deliberately not the ETF Universe Scoring Model** documented under Technical Requirements. That model grades a fund as a timing decision (technicals plus long-horizon returns) and is the right model for the screener's ETFs tab. This script ignores the wrapper completely, including expense ratio, yield, and every technical, and asks a different question: what would the screener say about the companies inside the fund? Both answers are valid and they will frequently disagree. A dividend-oriented fund scores poorly here by construction, since the stock model rewards revenue and EPS growth and a PEG-cheap valuation, which mature high-payout companies structurally do not have. That is a model-fit result, not a judgment on the fund.

**Scores are relative to a ranking pool, which is the single most important thing to state when quoting one.** Each pool is ranked independently, exactly as the live screener ranks within whichever universe is loaded, so a holding present in a feed scores what the site shows for it. Holdings missing from a feed (a second share class like GOOG, a fund-only name) are fetched and added to that pool, which is why the printed pool size can exceed the feed's own count.

Routing is by listing: a symbol with a foreign exchange suffix goes to the international pool, and share-class dots (`.A`, `.B`, `.C`) are excluded from that test so `BRK.B` stays domestic. `SYMBOL_FIXES` is applied before matching, so a holding returned under a wrong suffix still resolves into the right feed. A fund holding both (FNDF, VXUS) gets each holding ranked in its own pool, and the fund's weighted average therefore mixes two pools: acceptable, since both are percentile scores on the same 0-100 model, but worth stating when quoting a mixed fund's number.

**`--universe holdings` restores the original self-contained behavior**, ranking the holdings only against each other. That is useful for comparing a set of funds head to head, but it produces much harsher and less stable tiers: with a few dozen mega-caps in the pool and no weak companies beneath them, strong companies are forced into the bottom bands, and every tier moves when the fund list changes. Observed concretely on 2026-09-21: Apple scored 12/F against a 16-name pool of growth-fund holdings and 65/B against the S&P 500 on the same day with the same fundamentals. Prefer an index baseline whenever a rating will be quoted or written down.

**The `RATING_BANDS` labels compress against a broad index.** They were calibrated against the original holdings-only pool. Ranked against the S&P 500, the top-10 holdings of large-cap funds are by construction among the largest companies in that index, so they cluster high: on a 2026-09-21 run of 17 funds, 11 landed in a 6-point spread and all read "Excellent." Within that cluster the label carries little information and the ordering and the underlying per-holding tiers are the real signal. The bands are deliberately left as-is rather than re-tuned to manufacture spread; re-tuning them for index-relative mode is an open question, not a settled decision.

**Drift control:** `fetch()` and `num()` are imported from `fetch_screener_data.py` rather than copied, so metric definitions cannot drift from the live daily pipeline. The scoring curve, weights, and tier cuts are a hand port of `screener.js` (`METRICS`, `pointsFromPct`, `computeScoreMap`, `computeTierMap`) and **must be updated by hand when that model changes**; the port omits the two weight-0 context metrics (`peVsG`, `netCashMc`), which color cells in the UI and contribute nothing to a score.

**What has actually been verified, and what that covers:** on 2026-09-21 the script's output was checked against a hand-computed run of 8 Schwab funds, and all 8 fund-level averages and all 34 holding-level scores matched exactly. That check was made in `--universe holdings` mode, which was the default at the time, so **it validates the port of the scoring curve, weights, and tier cuts, not the index-baseline routing added in v4.3.0.** The index-relative default was checked separately, by scoring each committed feed standalone and confirming the tier bands land on the proportions `TIER_CUTS` specifies:

| Feed | n | S+ and S | A | B | C | F |
|---|---|---|---|---|---|---|
| `screener_sp500.json` | 500 | 53 (50 expected) | 53 (50) | 145 (150) | 125 (125) | 124 (125) |
| `screener.json` (Nasdaq 100) | 101 | 12 (10) | 8 (10) | 31 (30) | 25 (26) | 25 (25) |
| `screener_intl.json` | 100 | 10 (10) | 10 (10) | 30 (30) | 25 (25) | 25 (25) |

Each band sits on its target, with small overflow in the top bands exactly where the model's documented "boundary ties round up" rule predicts it. This validates `compute_tiers` against real 100-name and 500-name universes, which is the path the index-relative default actually uses. What still has not been done is a cell-by-cell reconciliation of specific tickers against the live site's rendered screener view; the scores are correct by construction (a holding in a feed reuses that feed's own record and runs through the same ported algorithm), but that end-to-end check would catch a port error the band proportions cannot.

**Known rough edges, by design rather than unresolved:**
- Some funds return fewer than 10 holdings from Yahoo (FNDF returned 9 on 2026-09-21). The script reports the count it got and says so in the fund's summary line rather than padding the table.
- Yahoo's fund-holdings endpoint returns a few foreign listings under an exchange suffix its own quote endpoint then mishandles. `SYMBOL_FIXES` maps them (currently two, both Korean: Samsung Electronics and SK hynix come back on `.KQ` and resolve on `.KS`). Expect to add entries when analyzing new international funds. **This failure is not always loud:** SK hynix's `.KQ` symbol returned a price from a different instrument along with null fundamentals, so it scored a confident-looking F instead of erroring. `MIN_METRICS` guards against that class of bug generally: a holding scoring on fewer than 3 of the 6 metrics is dropped from the ranking pools and reported as unrated rather than scored, since a thin fetch is indistinguishable from a genuinely weak company once it reaches the table. A blanket `.KQ` to `.KS` rewrite is deliberately avoided, matching `fetch_screener_data.py`'s `DASH_TICKERS` reasoning: KOSDAQ is a real exchange and genuine KOSDAQ listings would break.
- The `funds_data.top_holdings` top-10 limit, flagged above as the reason yfinance cannot substitute for a constituent source, is exactly the wanted behavior here.
- Cyclical recoveries score very high on a model with no way to tell a rebound off a depressed base from durable growth (memory-chip names scored S+ on the 2026-09-21 run). Holding companies score poorly for the mirror reason: Berkshire's PEG is not a meaningful input. Flag both when presenting results.


### Rollback

To restore a feed to a known-good version:

```bash
git checkout <hash> -- data/screener.json
git commit -m "revert screener.json to <hash>"
git push origin main
```

The jobs push often, so pull first. Never rewrite history: the feeds' git history is the score-history record (see Known Technical Debt).

### Common Errors

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| Invests' screener shows no data or a stale banner | A feed job failed or has not run | Check the Actions tab (or the open `CI failure:` issue) and re-run the job by hand |
| A job fails with HTTP 429 | Yahoo Finance throttling | Wait and re-run; the fetchers retry per symbol |
| A push is rejected | Another job pushed first | Pull with rebase and push again; for a conflict in a generated feed, keep the newer build |
| Constituent sync fails | A source changed shape | It falls back to the next source; if every source fails it aborts without touching the list (see Constituent sources) |

---

## Technical Requirements

### System Architecture

```
GitHub Actions (cron)
   ├── Mon-Fri 21:37 UTC → stock-data.yml: fetch_screener_data.py --part N (curated parts)
   │                       → data/stocks/part-NN.json, then build_legacy_feeds.py derives
   │                         screener.json, screener_sp500.json, screener_gvd.json, screener_intl.json
   ├── Sun 21:17 UTC     → stock-data.yml: every part (whole market, about 3,575 symbols)
   ├── Mon-Fri 22:12 UTC → screener-data-etfs.yml: fetch_etf_data.py (36 funds) → data/screener_etfs.json
   ├── Mon-Fri 15:07, 19:07, 22:07 UTC → market-overview.yml: fetch_market_overview.py → data/market_overview.json
   ├── Daily 02:17 UTC   → statements.yml: fetch_statements.py → data/statements/<TICKER>.json
   ├── Sat 23:17 UTC     → constituents.yml: update_constituents.py + update_etf_constituents.py
   └── on any failure    → alert-on-failure.yml opens or comments on a GitHub issue
        │
        ▼
main branch → GitHub Pages → azqato.github.io/stocks/data/ → Azqato Invests, Automate Fundamentals
```

Every cron uses an odd, off-peak minute (see Data Pipeline). All the data jobs except statements share the `screener-data` concurrency group, so runs that land close together queue rather than race.

### Folder Structure

```
.github/workflows/   the scheduled jobs (6)
.githooks/pre-push   prints failing or stale workflows before a push
scripts/             the fetchers and helpers (see Data Pipeline), plus analyze_etf_holdings.py (ad hoc)
data/                constituent lists, generated feeds, stocks/ parts, statements/
*.html               redirect pages to Azqato Invests (9)
docs/                PRD.md, PATCHNOTES.md, TODO.md
README.md
```

### Data Models

**nasdaq100.json**

```json
[
  { "t": "NVDA", "n": "NVIDIA" },
  { "t": "AAPL", "n": "Apple" }
]
```

Array of 100 objects. `t` = ticker symbol (string), `n` = company name (string). Multi-class rule: when a company has multiple share classes in the index (e.g., Alphabet GOOGL/GOOG), only the Class A voting shares are listed.

**screener.json**

```json
{
  "updated": "2026-06-27T23:51:56.164931Z",
  "source": "yahoo",
  "stocks": {
    "NVDA": {
      "t": "NVDA",
      "name": "NVIDIA",
      "price": 192.53,
      "marketCap": 4663269130240.0,
      "cash": 53171998720.0,
      "debt": 12814000128.0,
      "revTTM": 85.2,
      "epsTTM": 214.5,
      "peFwd": 21.483,
      "epsFwd": 87.88,
      "revFwd": 81.4,
      "pegFwd": 0.59,
      "priceUpdated": "2026-06-27T23:51:56.164931Z",
      "fundamentalsUpdated": "2026-06-27T23:51:56.164931Z"
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `updated` | ISO 8601 string | Timestamp of the pipeline run |
| `source` | string | Data source identifier ("yahoo") |
| `t` | string | Ticker symbol |
| `name` | string | Company name |
| `price` | number | Current stock price (USD) |
| `prevClose` | number | Prior session's closing price (USD) |
| `changePct` | number | Daily change: price vs prior close (%) |
| `marketCap` | number | Market capitalization (USD) |
| `cash` | number | Total cash and equivalents (USD) |
| `debt` | number | Total debt (USD) |
| `revTTM` | number | Yahoo's `revenueGrowth` (%). **Not a TTM figure despite the key**: it is the latest quarter against the same quarter a year earlier. Measured 2026-10-11 against `quarterly_income_stmt` for AAPL, MSFT, NVDA, KO and WMT, it matched latest-quarter year over year to within 0.05 percentage points on all five (AAPL 16.40 vs 16.36, NVDA 105.90 vs 105.85). The key is kept because two other repos read it; see Documentation Versus Reality item 11 |
| `epsTTM` | number | Yahoo's `earningsGrowth` (%). Same quarterly basis as `revTTM`, and the same naming problem |
| `grossMargin` | number | Gross margin TTM (%), in the feed but not scored or displayed since v3.31.0 |
| `netMargin` | number | Net (profit) margin TTM (%), in the feed but not scored or displayed since v3.31.0 |
| `peFwd` | number | Forward P/E (price ÷ current-FY EPS). **Unreliable for ADRs whose `financialCurrency` differs from their trading currency:** Yahoo divides a trading-currency price by a reporting-currency EPS, so the value is off by an FX factor (see Known Technical Debt) |
| `epsFwd` | number | Forward EPS growth (%), GAAP basis |
| `revFwd` | number | Forward revenue growth (%) |
| `pegFwd` | number | PEG ratio (Yahoo `pegRatio` field, long-term growth based) |
| `cur` | string | ISO currency code (e.g. `"USD"`, `"TWD"`, `"GBP"`); added v3.34.0, used only by the International universe to label $-formatted cells in the listing's own currency. Yahoo's London-listed quotes report in pence (`GBp`), not pounds, while that listing's `marketCap`/`cash`/`debt` are already in pounds, the pipeline normalizes `GBp`/`GBX` to `GBP` and divides `price`/`prevClose` by 100 before this field is ever written, so nothing downstream needs to know about the pence convention |
| `priceUpdated` | ISO 8601 string | Timestamp of price data |
| `fundamentalsUpdated` | ISO 8601 string | Timestamp of fundamentals data |

Trailing ratios in the feed for Automate Fundamentals, unused by the screener: `peTTM`, `psTTM`, `evEbitda`, `divYield`, `opMargin` (%), `roe` (%), `debtToEquity` (a plain multiple, Yahoo's percent divided by 100), `currentRatio`, `fcfYield` (%) from v4.3.6.

**Fields added in v5.2.0**, also for Automate Fundamentals (its metrics audit FM2, FM3, FM5) and also ignored by the screener. Every one comes out of the same `Ticker.info` call the pipeline already makes, so they add no Yahoo requests and about 400 bytes a stock.

| Field | Type | Description |
|-------|------|-------------|
| `revenue`, `ebitda`, `netIncome`, `fcf`, `ev` | number | TTM amounts and enterprise value, FX-converted from `financialCurrency` into the trading currency exactly as `cash`/`debt` are, and nulled when no rate resolves. They are divided against each other downstream, so they must share one currency |
| `eps` | number | Trailing EPS per share, already in the trading currency |
| `pb`, `evRevenue`, `pegTTM`, `quickRatio`, `beta` | number | Yahoo's `priceToBook`, `enterpriseToRevenue`, `trailingPegRatio`, `quickRatio`, `beta`. Currency-neutral, so untouched. `pb` is not always sane: Yahoo returned 0.00098 for BRK.B on 2026-10-11, apparently dividing a per-share price by total book equity. Stored as returned |
| `roa`, `ebitdaMargin`, `payoutRatio`, `shortFloat`, `heldInsiders`, `heldInstitutions`, `change52w` | number | Fractions from Yahoo stored as percents, like the existing margins. `ebitdaMargin` is nulled when `ebitda` is missing, because Yahoo answers `0.0` rather than null for a company it has no EBITDA for (every bank) |
| `divYield5yAvg` | number | Yahoo's `fiveYearAvgDividendYield`, which is **already** a percent; not scaled, same as `divYield` |
| `targetMean`, `analystRating`, `analystCount` | number | Mean price target, consensus rating (1 strong buy to 5 sell) and the number of analysts behind it |
| `high52`, `low52`, `ma200` | number | 52-week high and low and the 200-day average, in the same currency as `price`, so the `GBp` pence division applies to these and to `targetMean` too |


**screener_gvd.json (combined feed)**

```json
{
  "updated": "2026-07-03T21:00:00Z",
  "source": "yahoo",
  "universes": {
    "growth":   { "updated": "…", "source": "yahoo", "stocks": { "NVDA": { } } },
    "value":    { "updated": "…", "source": "yahoo", "stocks": { "MU":   { } } },
    "dividend": { "updated": "…", "source": "yahoo", "stocks": { "AVGO": { } } }
  }
}
```

One file, three universes. Each entry under `universes` has exactly the shape of a single-list feed, so the screener can point at `universes.growth` (etc.) and reuse every code path. Stock records are identical in schema to screener.json above; a symbol held by more than one fund is fetched from Yahoo once per run and duplicated into each universe with that list's curated name.

**screener_etfs.json (ETFs feed, v3.33.0)**

Same `{updated, source, stocks}` envelope as the stock feeds (so the frontend reuses every load/cache path), but with fund-specific fields per record: `price`, `prevClose`, `changePct`, `aum` (total assets, USD), `yieldPct` (trailing distribution yield, %), `expenseRatio` (net, %), `ytd`/`ret1y`/`ret5y`/`ret10y` (total returns incl. reinvested distributions, %, computed from 11 years of dividend-adjusted daily closes), `rsi` (14-day Wilder), `wk52Low`/`wk52High` (unadjusted 1-year closes), `pctVs20dma`/`pctVs100dma`/`pctVs200dma` (price vs moving average, %, unadjusted basis), plus the standard timestamps. Sourced by `scripts/fetch_etf_data.py`; yield uses Yahoo's `dividendYield` (never `trailingAnnualDividendYield`, which is missing or wrong for several funds) and expense ratio uses `netExpenseRatio`.

**etfs.json** follows the nasdaq100.json shape (array of `{"t", "n"}`) but holds the owner-picked funds (36 since 2026-10-11) and is never auto-synced.

**vug.json / vtv.json / vig.json** follow the nasdaq100.json shape (array of `{"t", "n"}`), hold exactly 100 entries (top holdings by weight after the dual-class dedupe), and are synced weekly from Vanguard's holdings API (Vanguard publishes fund holdings monthly, so constituent freshness lags the index lists by up to a month; acceptable because the fund's published holdings are the universe definition).

**screener_intl.json (International feed, v3.34.0)** is a plain single-list stock feed, identical schema to screener.json, `cur` field included, produced by the same `fetch_screener_data.py` fetcher and scored by the same six-metric client-side model. No separate scoring logic exists for this universe.

**vxus.json** follows the nasdaq100.json shape (array of `{"t", "n"}`) but `t` holds a **Yahoo symbol already resolved from the Vanguard holding's ISIN** (e.g. `"2330.TW"`, `"AI.PA"`), not the raw local-exchange ticker Vanguard returns. Synced weekly alongside VUG/VTV/VIG. Two per-run quirks the sync script handles that the domestic lists never hit: (1) Vanguard's API occasionally reports the same ISIN as two separate rows (observed for BHP Group and Barrick Gold), and these are summed by weight before ranking so "top 100" means 100 distinct issuers; (2) the retired profile API capped this fund at exactly 500 returned entities (not the ~8,500 VXUS actually holds), which is why the raw-count sanity guard was historically a tight 480-520 band; **as of v4.3.4 the current endpoint returns the full holdings list** (8,794 rows on 2026-09-21) and the guard band is 7,000-11,000. Because the list is weight-sorted and only the top 100 survives, the cap's removal does not move the membership, but same-issuer ISIN duplicates can now be detected deeper in the list than the old 500-row window reached.

**vxus_map.json** is the ISIN → Yahoo symbol resolution cache: `{"manual": {ISIN: symbol}, "resolved": {ISIN: symbol}}`. `manual` always wins and is how a bad auto-resolution gets corrected by hand (seeded at launch with the one holding that had a blank Vanguard ticker field and three dual-listing cases pinned to their primary exchange). `resolved` is the cache proper, populated by Yahoo's search endpoint (ISIN query first, company-name query as a fallback) and only queried for holdings not already in the cache, so a weekly sync's live-lookup cost is proportional to newly-added holdings, not the full 100.


### Screener Scoring Model (v3, shipped v4.1.12; four even pillars)

A relative, percentile-based model, confirmed directly against the `METRICS` array in `screener.js` (lines 191-209). Each stock is ranked against its loaded peers on four scored metrics in four evenly-weighted 25-point pillars totaling 100 points.

| Pillar | Weight | Metric | Direction | Value ranked |
|--------|--------|--------|-----------|--------------|
| Reported | 10 | Revenue Growth, latest quarter year over year | higher is better | `revTTM` |
| Reported | 15 | EPS Growth, latest quarter year over year | higher is better | `epsTTM` |
| FWD | 10 | Revenue Growth FWD | higher is better | `revFwd` |
| FWD | 15 | EPS Growth FWD | higher is better | `epsFwd` |
| Valuation | 25 | PEG FWD | lower is better | `pegFwd` (Yahoo); when forward P/E ≤ 0, ranks worst and the column shows our own negative `peFwd / epsFwd` instead of Yahoo's misleading positive |
| Balance sheet | 25 | Cash vs Debt | higher is better | `cash / debt` (no debt ranks best) |

Two further metrics are computed and ranked for cell-coloring context only, at zero score weight: the P/E-vs-growth ratio (`peVsG` = `peFwd / epsFwd`, negative-P/E and shrinking-earnings rank worst) colors the P/E FWD column, and Net Cash vs Market Cap (`netCashMc`) colors its own context column.

This four-pillar model (v3) replaced an earlier three-pillar model (Growth 60, forward growth weighted double trailing: Rev TTM 10, Rev FWD 20, EPS TTM 10, EPS FWD 20; Valuation 20; Balance sheet 20) that had shipped as v3.30.0/v3.31.0 (margins scored briefly as a fourth pillar in v3.30.0, removed the same day). The reweighting to four even 25-point pillars shipped as **v4.1.12** (2026-08-19, owner decision, reached while comparing weighting schemes against a private ad-hoc watchlist tool): trailing and forward growth now count equally rather than forward counting double, a quality/value tilt versus the prior growth tilt. Applies to all six stock universes (Nasdaq 100, S&P 500, Growth, Value, Dividend, International); the ETFs universe's separate technicals model, below, is unaffected. The percentile clamp, tier bands, and S+ threshold (all described next) were unchanged by this reweighting; only pillar weights moved.

**Percentile → points:** `points = clamp(20 × (percentile − 0.22) / 0.56, 0, 20)` (`CLAMP_Q = 0.22` in `screener.js`), then scaled by the metric's weight ÷ 20. Bottom 22% scores 0; top 22% scores full marks; the median scores half. Ties take the average rank. The 22% clamp was originally calibrated on the live feeds against the prior 6-metric weighted model (2026-07-03, v3.31.0) to the owner's target of ~1 perfect score in the Nasdaq 100 and ~5 in the S&P 500, ties allowed; it was carried forward unchanged into v4.1.12's four-pillar reweighting. The clamp must be re-fitted whenever the metric set or weights change materially enough to shift score distribution: the earlier 8-metric model needed 28%, and an interim 15% fit against incomplete feeds proved far too tight (top scores stalled around 99 with no perfect scores).

**Score:** weighted sum out of a fixed 100. **Missing data is a hard zero** (owner decision 2026-07-03, unchanged by v4.1.12): a metric with no value contributes nothing and the denominator does not shrink, so incomplete data can never outrank complete data. A stock at the median on everything scores 50; a stock with no scored metrics at all shows NO DATA.

**Tiers (v3.29.0, rank-based):** the scored stocks are ranked by score and sliced into S (top 10% of the list, `TIER_CUTS` `["s", 0.10]`), A (next 10%, `["a", 0.20]`), B (20–50%, `["b", 0.50]`), C (50–75%, `["c", 0.75]`), F (bottom 25%). Boundary ties round up: every stock whose rounded score equals the last stock inside a band joins that band, so a tier stretches past its quota only on identical scores. Tier counts are therefore structurally fixed per universe (~10/10/30/25/25 in a 100-stock list, scaled to ~50/50/150/125/125 for the S&P 500). Above the bands sits **S+** (v3.30.0, owner request): any stock scoring a perfect 100/100; those stocks come out of the S band's headcount, and the clamp calibration keeps them rare. The tier, not the raw score, drives the badge and score-bar colors (S+ purple `--color-tier-splus`, S dark green `--color-tier-s`, A light green, B yellow, C light red, F reuses `--color-negative` directly rather than a dedicated F token). This replaced the v3.20.0 fixed score bands (Pass ≥ 80 / Watch 50–79 / Fail < 50); the S/A/B/C/F tier-list vocabulary was chosen over broker-style labels (Strong Buy…Strong Sell) to stay clear of advice language.

**Factors chip:** count of the scored metrics earning 15+ of 20 percentile points (the upper part of the pack); a missing metric counts as a miss. **Discrepancy flag:** the metric count driving the score dropped from six to four with v4.1.12's reweighting; whether the chip's denominator followed to /4 or was left at /6 was not independently re-verified against `screener.js` during the 2026-08-25 documentation audit. Read the chip's render code before relying on this figure.

**Relative-scoring caveats:** because grades are peer-relative, a stock's score can change when *other* companies' numbers change, and because tiers are ranks, a fixed share of every list always lands in C and F no matter how strong the list is (an F means "bottom quarter of this list", not "broken company"). Scores are computed over the currently loaded set (normally all 100 from the daily feed).

**Cell colors:** every colored cell follows the same percentile ranking, not absolute thresholds, green = top of the pack on that metric, red = bottom, amber = in between. A missing value in a scored metric renders dark red (it is a hard zero); only the unscored context column (P/E FWD) shows gray for missing. A negative forward P/E or PEG renders red and sorts as a worst (expensive) value, never a cheap one.

**Per-stock popup:** clicking any row opens a focused breakdown for that stock, all six scored metrics with value, percentile, and weighted points (e.g. "7.2/10"), color-coded, with the total score and tier. Missing metrics show 0 points in dark red. Reuses the modal component.

### ETF Universe Scoring Model (v3.33.0, shipped 2026-07-03)

A sixth universe, entirely separate from the five stock universes above: a **fixed, owner-picked list of 36 ETFs**, not an auto-synced index or fund-holdings list. Doctrine-consistent by design, the site's own rule is that individual stocks are judged on fundamentals while index/ETF purchases are timed on technicals, so this universe scores exactly the technical and cost signals the stock universes deliberately exclude.

**The 36 ETFs (fixed list, no auto-sync):** QQQ, SPY, DIA, IWM, VTI, VXUS, VUG, VIG, VTV, SPMO, RWL, SPHQ, SPHB, FNDF, MGV, VBR, SCHD, RSP, VBK, ISCG, FNDB, FNDX, SCHB, IMCG, XLG, SPGP, ILCG, IUSG, IVW, SPYG, SCHG, IWF, VONG, MGK, IWY, MLRG. The first 10 shipped 2026-07-03; the other 26 were added 2026-10-11 at the owner's request (all verified on Yahoo with full data; MLRG is the iShares MSCI USA ETF).

**Visible columns:** Price, Daily % Change, YTD Performance, 1 Year Total Return, 5 Year Total Return, 10 Year Total Return, Yield, Expense Ratio, Yield − Expense Ratio, RSI, 52-Week Range, Price vs 20-Day Moving Average, Price vs 100-Day Moving Average, Price vs 200-Day Moving Average, AUM (owner-added 2026-07-03; unscored display, `info["totalAssets"]`, verified for all 10 funds).

**Scoring criteria (current, confirmed directly against `screener.js` lines 211-248), Technicals 50 + Performance 50:**

| Pillar | Metric | Direction | Points |
|--------|--------|-----------|--------|
| Technicals | RSI | lowest is best | 20 |
| Technicals | 52-Week Range (position within range) | lowest is best | 20 |
| Technicals | Price vs 200-Day Moving Average (trend/momentum) | highest is best | 10 |
| Performance | 1 Year Total Return | highest is best | 10 |
| Performance | 5 Year Total Return | highest is best | 20 |
| Performance | 10 Year Total Return | highest is best | 20 |

Yield and Expense Ratio are **not scored**: they were removed from the scoring model in **v3.37.0** and now render as unscored display/context columns only (see "Review concerns" item 1 below, where the original spec's income tilt was later reversed). Unlike the stock universes' percentile-clamped model, this universe uses **rank-linear points, not a percentile clamp**: on each metric the best of the 10 funds earns full points and the worst earns 0, spaced evenly by rank (ties take the average rank); see item 4 under "Review concerns" for why. The 20-day and 100-day moving-average columns remain **display/context only** (unscored), giving a fuller trend picture (short, medium, long) alongside the scored 200-day signal, the same "scored vs. context-only" pattern the stock universes use for P/E FWD.

**Discrepancy flag:** the table immediately below ("Scoring criteria... 100 of 100 points decided 2026-07-03") and the "As built" paragraph further down both describe the **original v3.33.0 launch spec**, which scored Yield (10) and Expense Ratio (10) and used different pillar totals (Technicals 50 / Performance 30 / Income & cost 20). That spec was superseded by v3.37.0 (see the Milestone Table and PATCHNOTES.md), which the table directly above this note reflects. The two are kept side by side, original text un-touched, per this audit's merge-don't-overwrite rule: the "Review concerns" and "As built" sections below are the historical record of the launch decision, not the current behavior; the table directly above this paragraph is the current behavior as read from code.

**Data availability (verified live against yfinance 1.4.1, 2026-07-03, all 10 funds):** yield via `info["dividendYield"]` (do **not** use `trailingAnnualDividendYield`, missing or wrong for several funds, e.g. VUG); expense ratio via `info["netExpenseRatio"]` (present and correct for all 10); everything else (YTD/1Y/5Y/10Y total returns, RSI-14, 52-week range, 20/100/200-day MAs) computed from one 11-year daily history call. Convention: total returns use dividend-adjusted closes (`auto_adjust=True`), RSI/MAs/52W range use unadjusted prices (standard charting basis). SPMO (inception Oct 2015) is the youngest fund and just clears the 10-year return window; a missing return scores a hard zero, consistent with the stock model.

**Review concerns logged 2026-07-03 and owner resolutions (decided 2026-07-03 before implementation):**

1. **Yield is partially double-counted and carries a style bias** (total returns already include distributions, so scoring yield again favors income-style VIG/VTV over growth-style QQQ/VUG/SPMO). Alternatives offered: score Yield − Expense Ratio instead, or drop yield and raise Expense Ratio to 20. **Resolved: keep as specced**, the income tilt is an accepted, intentional preference.
2. **50 of the 100 points move together.** RSI, 52-Week Range position, and Price vs 200DMA are all "how far below recent prices" measures; in a broad selloff all three fire at once, so half the score is effectively one dip-depth factor and scores will swing hard day to day. **Accepted as designed**, it makes the score a strong timing dial, per the technicals-time-ETF-purchases doctrine.
3. **The S/A/B/C/F rank-band tier system fits a 10-fund list oddly** (S = 1 fund, A = 1, B = 3, C = 2-3, F = 2-3; an F badge lands on household index funds; S+ is nearly unreachable with 10 peers). Alternatives offered: score-only with no tier badges, or absolute score cuts. **Resolved: keep the rank bands**, an F means "bottom of this list right now," consistent with every other universe, and the caveat language already covers it.
4. **Relative percentiles are very coarse at N=10** (the 22% clamp was calibrated for 100+ stocks; reused unchanged, the top 2 funds per metric max out and the bottom 2 zero out). **Resolved: rank-based linear points for this universe**, on each metric the best fund earns full points and the worst earns 0, spaced evenly by rank (ties take the average rank), no clamp, no calibration to maintain.

**As built (shipped 2026-07-03):** static `data/etfs.json` list (hand-edited only, no auto-sync); `scripts/fetch_etf_data.py` (the field set shares nothing with the stock fetcher); `data/screener_etfs.json` feed in the standard `{updated, source, stocks}` envelope; `.github/workflows/screener-data-etfs.yml` Mon-Fri 23:15 UTC (between the Nasdaq 100 and S&P 500 runs, same `screener-data` concurrency group). Frontend: sixth universe button ("ETFs"); screener.js routes by a per-universe `kind` flag, the `<thead>` and Columns menu are config-driven and re-render when the universe kind changes (a refactor that also pre-pays for the International universe), sort and Columns events moved to delegation to survive the re-render, and the stock universes' scoring/markup are unchanged (verified by a headless regression run matching the v3.31.0 baseline exactly). ETF pillars as displayed: **Technicals 50** (RSI 20, 52W range 20, vs-200DMA 10), **Performance 30** (1/5/10y returns), **Income & cost 20** (yield 10, expense ratio 10); rank-linear points (best fund 20, worst 0, evenly spaced, ties averaged, missing = hard zero); Factors chip /8; the same rank-band tiers (on 10 funds: 1 S, 1 A, 3 B, 3 C, 2 F, verified live); cell colors green at 15+ rank points and red at 5 or less (the stock thresholds of exactly 20/0 would color only the single best/worst fund); per-fund popup breakdown; a dedicated ETF section in the methodology popup shown when the ETFs universe is active.


The scoring code lives in Azqato Invests (`invests/assets/js/stocks/screener.js` in the `azqato.github.io` repo). Both models are documented here because the feeds' fields exist to serve them and `analyze_etf_holdings.py` ports the stock model.

### Third-Party Integrations

| Service | Purpose | Authentication |
|---------|---------|---------------|
| Yahoo Finance (via yfinance) | Prices, fundamentals, statements | None (public) |
| Nasdaq index API, State Street SPY holdings, Slickcharts | Index membership | None (public) |
| Vanguard holdings API | VUG, VTV, VIG, VXUS, VTI membership | None (public) |
| GitHub Actions and Pages | Scheduling, hosting the data | Owner account |

### Known Technical Debt

| Debt | Description | Correct Solution |
|------|-------------|-----------------|
| Constituent name quality | New tickers added by the auto-sync use cleaned source names, which may be slightly longer than the curated short names (`clean_name()` strips corporate and share-class tails like "Inc." / "Class A Common Stock") | Hand-edit `data/nasdaq100.json` names after a sync if desired (existing names are preserved automatically) |
| `peFwd` not FX-converted for ADRs | `fetch()` converts `cash` and `debt` from `financialCurrency` into the trading currency but applies no equivalent treatment to `peFwd`, which Yahoo supplies via `priceEpsCurrentYear` already computed as a trading-currency price over a reporting-currency EPS. Any ADR reporting in a different currency therefore carries a forward P/E off by an FX factor. Found 2026-09-21 on NVO (Novo Nordisk ADR): feed value 1.76 against a real forward P/E near 11.9, because a USD 39.80 price is divided by a DKK 22.57 EPS. **Scoring is not affected today** and this is a display defect: `peFwd` carries zero weight, and its only scored use is the sign guard in the PEG metric (`peFwd <= 0` ranks worst), which survives because dividing by a positive FX rate preserves sign. It does corrupt the weight-0 `peVsG` context ratio that colors the P/E FWD column, so affected ADRs get a miscolored cell as well as a wrong number | Apply the same `fx_rate()` conversion `fetch()` already uses for cash and debt: when `financialCurrency` differs from `currency`, recompute `peFwd` as `price / (EPS × rate)` rather than trusting Yahoo's `priceEpsCurrentYear`, and fall back to nulling the field when no rate resolves, matching the existing cash/debt behavior. Would become urgent if `peFwd` is ever given scoring weight or surfaced in the planned multi-year EPS and P/E tool |
| Scheduled crons fire hours late | GitHub is starting every scheduled run well after its cron time, and the lag is growing: measured 2026-09-21, `screener-data` fired 2h37m late (21:37 UTC cron, 00:14 UTC start) and Market Overview's three runs fired 4h49m, 3h25m and 2h34m late. `run_started_at` equals `created_at` on every run, so this is the scheduler firing late, not slow jobs. The v4.1.8 off-peak-minute fix (odd minutes to dodge top-of-hour congestion) is no longer sufficient. **The screener feeds are unaffected** (they only need to land after the US close and still do), but **Market Overview's three snapshots have collapsed**: mid-morning, pre-close and post-close were all pushed to at or after the close, so two of the three now read the same post-close prices | No clean fix available inside GitHub Actions, whose schedule is best-effort by design. Options, none chosen: move Market Overview's crons hours earlier to land where they were meant to; accept two redundant snapshots and drop one; or move the trigger off GitHub's scheduler entirely (an external ping to `workflow_dispatch`). Re-measure before acting, since the lag is not stable |
| A failing cron is invisible | No notification existed when a scheduled workflow failed, so a weekly job could fail indefinitely without anyone noticing. This caused two multi-week silent outages: the Wikipedia constituent break (v4.1.8) and the Vanguard endpoint break (v4.3.4, six consecutive Saturday failures found only because the owner asked for an audit) | **Largely addressed in v4.3.5** by two layers, documented under Runbook, Workflow Failure Detection: `alert-on-failure.yml` opens a GitHub issue on any workflow failure, and `.githooks/pre-push` reports failing or stale workflows before a push. What remains is outside the repo: Actions failure emails are an account-level notification setting only the owner can enable, and the pre-push hook needs `git config core.hooksPath .githooks` once per clone |

Not debt (reclassified v3.32.0): the generated data feeds (`screener.json`, `screener_sp500.json`, `screener_gvd.json`, `screener_etfs.json`, `screener_intl.json`) are committed to the repo **intentionally**. Their git history is the site's only record of past scores and is the data source for the planned v4.1.0 score-history sparklines. Do not move them to GitHub Releases or external artifact storage; the growing history is the feature.

---


---

## Security

- No secrets: every source is public and no workflow uses an API key. The old `FMP_API_KEY` secret was deleted on 2026-07-03.
- Only the owner and the repo's own workflows push to `main`.
- The feeds hold public market data only, with no personal data.
- yfinance is pinned to 1.4.1 in every workflow; bump it deliberately after testing, never float `latest`.

---

## Documentation Process

Four documents: `README.md` (short, at the repo root), `docs/PRD.md` (this file: how the feed works), `docs/PATCHNOTES.md` (every change, written when it ships) and `docs/TODO.md` (unscheduled ideas only; an item leaves it once it has a version). `docs/DESIGN.md` was deleted in v5.1.0 along with the old site's styles.

PATCHNOTES entries use `## vMAJOR.MINOR.PATCH - YYYY-MM-DD - Title` with Added, Changed, Fixed and Removed sections. Old entries are never rewritten; a correction gets its own entry.

**Writing style:** no em dashes in any form (not the character, not `&mdash;`, not a spaced double hyphen). Direct and functional, no marketing language.

**Commits:** automated commits use `chore: update <feed> [skip ci]`; human commits use a lowercase `type: description` or a short plain summary. Work happens on `main`.

---

## Deprecation and Removal

- **Old page addresses** stay as redirect pages permanently and are never reused (v5.0.0). The map is in the Azqato Invests PRD (Part 2, Invests: Deprecation and Removal). `guide.html` and `indexes.html`, retired long before, simply 404.
- **A data file that Invests or Automate Fundamentals reads** must not be renamed or removed without changing the reader first.
- **Internal-only files** (an unused script, a retired helper) are a plain delete, recorded in PATCHNOTES.

---

## Documentation Versus Reality


Every discrepancy found during the 2026-08-25 documentation audit (v4.1.13), recorded here rather than silently fixed, per this audit's own instruction that code can be wrong just as easily as docs. Resolved entries keep a note on how they were resolved rather than being deleted, so this list stays a real record over time.

| # | Discrepancy | Source of truth used | Status |
|---|---|---|---|
| 1 | Screener Scoring Model section (Technical Requirements) described the retired three-pillar model; live code (`screener.js` lines 191-209) implements a four-pillar model shipped in v4.1.12 | Code (directly read) | **Resolved 2026-08-25**: section rewritten in place, old model's history kept as context, not deleted |
| 2 | ETF Universe Scoring Model's scoring-criteria table described the pre-v3.37.0 spec (Yield and Expense Ratio scored, 30/20 pillar split); live code implements Technicals 50 / Performance 50 with Yield and Expense Ratio unscored | Code (directly read) | **Resolved 2026-08-25**: current table added above the original spec text, original left in place and flagged as historical, not deleted |
| 3 | External FAQ #5, #6, #7 and Press Release described the retired three-pillar model | This file's own corrected Screener Scoring Model section | **Resolved 2026-08-25**: FAQ answers corrected in place; Press Release is a dated historical artifact and was left as-written with a discrepancy note appended, not rewritten |
| 4 | README's former project-structure comment tree and this file's System Architecture diagram / Folder Structure tree showed the pre-v4.1.8 round-minute cron schedule (21:30/22:00/22:30/23:00/23:30 UTC); actual workflow YAML files use odd off-peak minutes (21:37/22:12/22:42/23:12/23:42 UTC) | `.github/workflows/*.yml` (directly read) | **Resolved 2026-08-25**: README's tree was removed entirely in its rewrite (README no longer carries implementation detail); this file's diagrams corrected |
| 5 | "Five files" documentation-strategy language (Internal FAQ, old Documentation Process section) referenced a `docs/ROADMAP.md` that no longer exists post-audit | This audit's own consolidation | **Resolved 2026-08-25**: updated to "four files," ROADMAP.md content merged into Roadmap → Open Milestone Detail |
| 6 | `style.css`'s `.sidebar-brand-sub` rule references `var(--color-text-muted)`, a custom property never defined anywhere in `:root`: a dead CSS variable reference (renders as the browser's `unset`/inherited default, not a crash, but not the intended styling either) | `style.css` (directly read, both the usage site and the full `:root` block) | **Open**: a real code bug, not a documentation gap; out of scope for a docs-only audit to fix. See Risks and Open Questions below |
| 7 | The Factors chip's denominator (screener universes): whether it reads `/4` or was left at the pre-v4.1.12 `/6` after the metric count dropped from six scored metrics to four | Not independently verified this pass | **Open**: flagged inline in the Screener Scoring Model section; needs a direct code read before the figure is trusted |
| 8 | `docs/DESIGN.md`'s documented monospace font stack includes `'Courier New'` as a fourth fallback, which a code-reading pass's grep excerpt of `style.css` did not show | Not fully reconciled; the grep excerpt may simply have been truncated | **Open, low priority**: re-verify the full monospace stack in `style.css` directly before treating either version as authoritative |
| 9 | `peFwd` in the committed feeds is Yahoo's `priceEpsCurrentYear`, which for an ADR reporting in a foreign currency divides a trading-currency price by a reporting-currency EPS; `fetch()` FX-converts `cash` and `debt` for exactly this reason but does nothing for `peFwd` | `fetch_screener_data.py` and the live `data/screener_sp500.json` record for NVO (both directly read, 2026-09-21) | **Open**: display-only today (`peFwd` has zero scoring weight and its only scored use, the PEG sign guard, survives a positive FX factor), but it also skews the weight-0 `peVsG` context ratio that colors the P/E FWD cell. See Known Technical Debt for the fix |
| 11 | `revTTM` and `epsTTM` are named and documented as trailing 12-month growth, and were labeled "Rev Growth TTM" / "EPS Growth TTM" on the screener, but they carry Yahoo's `revenueGrowth` and `earningsGrowth`, which are the latest quarter against the same quarter a year earlier | Yahoo's own `quarterly_income_stmt`, measured directly for AAPL, MSFT, NVDA, KO and WMT on 2026-10-11: agreement with latest-quarter year over year was within 0.05 percentage points on all five | **Resolved 2026-10-11 (v5.2.0 here; Invests 2.18.1, Automate Fundamentals v0.124.2)**: the feed keys are deliberately kept, being internal names read by two other repos that already treat them as quarterly, so a rename costs a coordinated three-repo deploy and gains a reader nothing. Everything a reader sees was corrected instead. Invests renamed the columns to Rev Q YoY and EPS Q YoY, renamed the first scoring pillar from TTM to Reported, retitled and rewrote both metrics-page sections, and removed guidance telling readers to watch a four-quarter deceleration sequence on a single-quarter number. Automate Fundamentals corrected its two Learn lessons; its metric glossary and SEC quality report already described the metric correctly, and its own SEC pipeline independently computes quarter-over-year-ago-quarter for the same key. The semantics are documented at the field, in the fetcher's docstring and here |
| 12 | `psTTM` carried Yahoo's `priceToSalesTrailing12Months` unconverted, which for an ADR divides a trading-currency price by reporting-currency sales per share | The feed's own FX-converted revenue, added v5.2.0: NVO read `psTTM` 0.52 against a market cap over revenue of 3.46 (measured 2026-10-11, DKK sales against a USD price) | **Resolved 2026-10-11 (v5.2.0)**: `psTTM` is now derived as `marketCap / revenue` whenever `financialCurrency` differs from the trading currency, and left as Yahoo's for the same-currency majority. Item 9 (`peFwd`) stays open because there is no converted forward EPS to derive a replacement from |
| 10 | This file described Vanguard's holdings source as the profile API at `/investment-products/etfs/profile/api/{fund}/portfolio-holding/stock`, with a 500-entity cap on VXUS; that endpoint was retired between 2026-08-08 and 2026-08-15 and now answers HTTP 200 with the site's SPA HTML shell | Vanguard's own `portfolio-composition` web component (`fundsBaseUrl` in its `common-*.js` bundle), read directly 2026-09-21 | **Resolved 2026-09-21 (v4.3.4)**: script repointed at `/irr/funds/profile/{TICKER}-AdditionalFundData`, field names remapped, the VXUS guard band widened for the now-uncapped response, and this file's data-model note corrected |

**Which source to trust, generally:** code, when the question is "what does the site actually do right now": this file and DESIGN.md are describing a moving target and lag behind ships by anywhere from hours to (as items 1 and 2 show) over a month. PATCHNOTES.md is the one document that's structurally hard to let drift, since each entry is written at ship time; when this file and PATCHNOTES.md disagree on what shipped, trust PATCHNOTES.md and correct this file.

---


**Closed by v5.1.0:** items 6 and 8 concerned `style.css` and `docs/DESIGN.md`, both deleted with the old site; item 7 (the Factors chip) now belongs to the Invests copy of the screener.

---

## Risks and Open Questions

- **GitHub's scheduler fires crons hours late** (see Known Technical Debt). The screener feeds only need to land after the close and still do; Market Overview's three snapshots can collapse into one.
- ~~The overnight statements schedule is undecided.~~ **Settled in v5.2.0**: nightly at 02:17 UTC, 520 symbols a night, with a push retry loop. **The cadence was then settled too** (v5.2.1, owner decision 2026-10-11): 1,000 a night, a 3.6-day cycle at 3,577 stocks. The 520 it replaced had been sized for a 619-stock universe. Measured 2026-10-10, 520 symbols took 20m01s, so about 2.1 seconds a symbol, which put 1,000 near 37 minutes against a 180-minute timeout. Measured directly at the new count on 2026-10-11: **36m18s**, with 995 of 1,000 files written. The ceiling is roughly 5,000 a night and the whole universe would fit in one pass at about 127 minutes, but statements only change when a company reports, so a nightly full pass would refetch an identical file about 90 times a quarter; 1,000 holds the pickup lag under four days through earnings season at twice the request budget rather than seven times. Raise it if the universe outgrows about 7,000 stocks, which is where a one-week cycle would need more than 1,000 a night; lower it only if Yahoo starts throttling, which shows up as a falling `Wrote N/1000` count rather than as a failure.
- **The scored trailing metrics are a single quarter, not twelve months** (see Documentation Versus Reality item 11). They carry 25 of the model's 100 points, and a quarterly figure is the more current but noisier choice. Switching them to fiscal-year growth is now possible, since v5.2.0 gives the whole universe statements, but it would move scores materially (measured 2026-10-11 across the Nasdaq 100: a 7.0 percentage point median gap, 10 of 100 names disagreeing on direction, and a 9-place median rank shift) and the percentile clamp would need re-fitting. Not scheduled; the pillar is named Reported rather than TTM so the documentation matches the data either way.
- **A reader resolving a statements file name must handle the reserved-name rule** (`CON` is stored as `CON_.json`; see Data Pipeline). Automate Fundamentals reads this directory and has not been told yet.
- **The feeds are read from other repos.** A field or file change here can break Invests or Automate Fundamentals without any check in this repo noticing; check both readers before changing a feed's shape.
