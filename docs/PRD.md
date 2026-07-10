# PRD — Azqato Stock Methodology Site

**Version:** 4.1.5
**Status:** Current
**Author:** Azqato
**Last Updated:** 2026-07-04

---

## Problem Statement

Retail investors face a fundamental problem: markets are noisy, opinions are everywhere, and financial media profits from attention rather than accuracy. Beginner and intermediate investors have no structured, opinionated, non-commercial resource that explains not just what metrics to use, but why each one matters, how to read it, and what a complete evaluation actually looks like end-to-end.

Most investing resources either oversimplify (buy low, sell high) or overwhelm (Bloomberg Terminal). Neither helps a motivated person build a repeatable process. Azqato's methodology exists to fill that gap: a documented, first-person framework for long-term equity investing built from years of practice, refined through mistakes, and presented without any commercial incentive.

---

## Target Users

**Primary: The "first-position investor" (beginner to intermediate, self-directed)**
- Owns 1-3 individual stocks or an index fund bought on gut feel, or is close to a first purchase
- Has heard terms like P/E ratio and RSI but cannot apply them confidently; can read a quote page but glazes over at a financial summary
- Invests from income (regular contributions), not a lump-sum windfall
- Has personally felt at least one of: buying at peak hype, panic-selling a dip, or selling a winner early and watching it run
- Follows Azqato on Twitch, YouTube, or Discord (B5TA community)
- All editorial content is written for this reader: teach before asserting, define terms in plain English at first use, and anchor concepts to decisions they have already faced

**Secondary: Intermediate investor looking to formalize a process**
- Already investing but decisions are ad hoc
- Wants a structured methodology to compare against their current approach
- Comfortable with spreadsheets but not with coding or professional research tools

**Not the target user:**
- Day traders or swing traders (this methodology is explicitly buy-and-hold)
- Professional fund managers or analysts (this is not Bloomberg or FactSet)
- People seeking hot tips or stock picks

---

## Goals

1. Give any motivated reader enough understanding to evaluate a stock using the 12-metric framework
2. Explain the philosophical foundation so readers internalize the rules rather than mechanically applying them
3. Provide practical tool setup guides so readers can replicate the workflow (Finviz + Seeking Alpha)
4. Offer a live Nasdaq 100 screener that applies the methodology's scoring model transparently
5. Cover index/ETF investing separately with appropriate timing-signal frameworks
6. Remain accurate and trustworthy long-term without requiring constant editorial updates

---

## Non-Goals

- Not providing financial advice or personalized recommendations
- Not providing real-time data in editorial content (the screener is a labeled, separate tool)
- Not building a trading platform, portfolio tracker, or brokerage integration
- Not supporting user accounts, authentication, or any backend
- Not covering options, futures, crypto, forex, or any non-equity asset class
- Not covering day trading, swing trading, or technical pattern trading

---

## User Stories

- As a beginner investor, I want to understand what PEG ratio means so that I can evaluate whether a stock's valuation is justified by its growth.
- As an investor who bought at the wrong time, I want to learn when not to buy so that I stop entering positions at peak hype.
- As someone who panicked and sold winners, I want to understand the cost of selling so that I never make that mistake again.
- As a Seeking Alpha user, I want to know exactly which columns to configure so that my watchlist matches the methodology.
- As someone with a lump sum to invest, I want to understand when and how to deploy it into index funds so that I make the mathematically sound decision.
- As a Finviz user, I want the exact filter settings for the methodology so that I can find candidates without doing manual research from scratch.
- As someone overwhelmed by market noise, I want a philosophical framework so that I can distinguish signal from sentiment.
- As an investor wanting to see all 100 Nasdaq companies scored, I want the interactive screener so that I can identify which ones pass or fail the methodology.

---

## Feature List

### MVP (shipped)

- 8 educational pages with sidebar navigation (Home, Philosophy, Metrics, Screener, Finviz, Seeking Alpha, Indices, FAQ)
- 12-metric evaluation framework documented with examples, how-to-read guides, and caveats
- 12-section philosophy page (belief and long game, ownership model, research process, GVD framework, offense cadence, protecting gains, investor-vs-trader discipline, Wall Street critique, hype/weak-hands, leadership cycles, knowledge building, why we wait on IPOs)
- 36-item FAQ accordion
- Step-by-step Finviz screener setup guide
- Step-by-step Seeking Alpha watchlist setup guide (12-column layout)
- Index/ETF methodology with VIX action levels, AAII sentiment, RSI, 52W range, structural quality metrics, DCA vs lump sum
- Interactive screener with relative percentile scoring model and seven switchable universes: Nasdaq 100 (default), S&P 500, the top 100 holdings of Vanguard's Growth (VUG), Value (VTV), Dividend Appreciation (VIG), and Total International Stock (VXUS) ETFs (all six-metric fundamentals-scored), and a fixed owner-curated ETFs list (10 funds) with its own column set and technicals-based scoring model, each with its own daily data feed
- Scoring model v2: 6 metrics in three weighted pillars (Growth 60 with forward growth weighted double, Valuation 20, Balance sheet 20), ranked against peers with a top/bottom-22% points clamp, missing data scoring a hard zero, total /100, mapped to S+/S/A/B/C/F tiers (S+ = a perfect 100 score; S = top 10%, A = next 10%, B = 20–50%, C = 50–75%, F = bottom 25% by rank within the loaded list; boundary ties round up)
- Methodology popup explaining the scoring model in plain language with worked examples
- Daily yfinance data pipeline via GitHub Actions (no API key required)
- Screener loads its feed directly from GitHub (works even when the file is opened locally), with an offline localStorage cache
- Per-stock breakdown popup (click any row) and percentile-based cell colors that track the score
- Responsive design (desktop, tablet, mobile)
- "On This Page" anchor navigation with IntersectionObserver scroll tracking
- Open Graph and Twitter Card social cards on all pages
- Accessibility: WCAG AA contrast, aria attributes, focus styles, reduced motion support

### Future (post-launch)

- Deeper coverage of index fund types (sector ETFs, international allocation, bond tent strategy) — scheduled as v4.2.0
- Additional illustrative examples using historical market events — scheduled as v4.3.0
- Separate pages for Growth, Value, and Dividend stock frameworks
- Conference call research guide (how to listen, what to note, how to log insights) — scheduled as v4.5.0

---

## Constraints

- No backend, no server, no database. Static files only.
- No paid APIs or subscriptions in the primary data path (yfinance is free)
- No external font loading (system fonts only)
- No frontend JavaScript libraries or frameworks
- Content must remain accurate without date-bound updates (no "as of today" editorial references)
- Data pipeline must run within GitHub Actions free tier limits
- No user-facing API keys or credentials of any kind
- Site must be instantly servable by opening index.html in a browser. The screener reads its feed from GitHub raw, so it also works when opened as a local `file://`

---

## Assumptions

- GitHub Pages will remain free for this use case indefinitely
- yfinance will remain a viable data source for Nasdaq 100 tickers
- Yahoo Finance data quality is sufficient for educational screening purposes (not institutional-grade)
- The Nasdaq 100 constituent list changes infrequently enough that annual manual review is acceptable
- Seeking Alpha's column configuration UI will not change frequently enough to invalidate the setup guide
- Finviz's free tier filter set will remain available without requiring an account

---

## Success Criteria

- All 12 metrics explained clearly enough that a reader with no finance background can apply them
- Philosophy content covers all major behavioral and conceptual foundations of the strategy
- FAQ answers the most common investor questions (36 items) without requiring outside research
- Screener shows all 100 Nasdaq 100 tickers with current scores, updated daily automatically
- Site loads with no errors and no external requests in any modern browser
- Mobile-readable at 375px minimum width
- No real-time data, no company-specific live recommendations, no financial advice language
- Navigation is consistent and correct on all 9 pages (11 nav items total)
- All pages render a preview card when shared on Discord, X, or Slack

---

## Tenets

Listed in priority order. When two tenets conflict, the higher one wins.

**1. Accuracy over coverage**
Document fewer things correctly than more things loosely. A reader who trusts this site trusts it because every claim they can verify turns out to be right. One wrong statement costs more than ten missing ones.

**2. Permanence over freshness**
Every page should be as useful in five years as it is today. Real-time data, current prices, and company-specific snapshots age immediately. Conceptual frameworks, calibrated thresholds, and illustrative examples do not. When choosing between a vivid current example and a durable hypothetical one, choose the hypothetical.

**3. Teach before asserting**
Someone reading this site has already decided to learn, but has not yet used these tools in practice. Explain what a term means, in plain English at its first use on each page, before building an argument on it, and let opinionated conclusions land after the reader has the machinery to see why they hold. Added words must teach: scaffolding that earns its length (worked examples, analogies, inline definitions, takeaway boxes) is welcome; padding is not.

**4. Tools serve the methodology, methodology does not serve the tools**
Finviz and Seeking Alpha are referenced because they are the best free tools for this workflow, not because they are partners or sponsors. If better tools emerge, the guides should be rewritten without sentiment. The scoring model exists to make the methodology testable, not to make the screener impressive.

**5. Simplicity is a feature**
Zero frontend dependencies, no build tools, no login. This is a deliberate choice. Every dependency is a maintenance burden and a failure point. The site works by opening a file in a browser. That is worth protecting.

**6. Separate the tool from the editorial**
The screener presents live third-party data. The educational pages use hypothetical examples. These are different things and must never be confused. The distinction preserves the integrity of both: live data is labeled and timestamped; educational content is durable and non-specific.

**7. Opinions over hedging**
This methodology has a point of view. It says to buy quality and hold it. It says to ignore short-term price movements. It says selling winners early is almost always wrong. These are controversial positions that real investors disagree with. State them directly. A hedged methodology is not useful to anyone.

---

## Roadmap

### Current Phase: Operational (v3.x)

The site is live, fully featured, and running automated daily data refreshes. The core methodology is documented end-to-end. The screener is scoring all 100 Nasdaq 100 tickers daily. Documentation has been consolidated into five files (README, PRD, DESIGN, PATCHNOTES, ROADMAP).

Detailed implementation plans for every Planned milestone below live in [docs/ROADMAP.md](ROADMAP.md); this table remains the source of truth for what is planned and in what order.

### Milestone Table

| Milestone | Target | Status |
|-----------|--------|--------|
| v1.0.0 — Initial release (3 pages, light theme) | 2026-06 | Complete |
| v1.9.0 — Philosophy page, 12 metrics, content expansion | 2026-06 | Complete |
| v2.x — Social cards, FAQ expansion, punctuation audit, sitewide nav | 2026-06 | Complete |
| v3.0.0 — Leveraged Strategies nav link | 2026-06 | Complete |
| v3.4.0 — Interactive screener + data pipeline | 2026-06 | Complete |
| v3.7.0 — yfinance pipeline, constituent fix | 2026-06 | Complete |
| v3.12.0 — New 5-factor scoring model | 2026-06 | Complete |
| v3.13.0 — Methodology popup on screener | 2026-06 | Complete |
| v3.14.0 — Documentation consolidation (this audit) | 2026-06-27 | Complete |
| v3.15.0 — Relative percentile scoring model | 2026-06-27 | Complete |
| v3.16.0 — Per-stock popup, GitHub-direct loading, FMP removed | 2026-06-27 | Complete |
| v3.17.0–v3.18.0 — Constituent auto-sync; screener.js extraction | 2026-06-27 | Complete |
| v3.19.0 — Mobile hamburger nav; wider popups | 2026-06-28 | Complete |
| v3.20.0 — Tighter verdict bands (Pass 80 / Watch 50 / Fail <50) | 2026-06-28 | Complete |
| v3.21.0 — Per-stock popup shows only scored metrics | 2026-06-29 | Complete |
| v3.22.0 — Expand to S&P 500 toggle (second daily feed) | 2026-06-29 | Complete |
| v3.23.0 — Trading-day (Mon-Fri) refresh; constituents moved to Saturday | 2026-06-29 | Complete |
| v3.24.0 — "Protecting gains after a strong run" theme (FAQ + home + philosophy + indices) | 2026-07-02 | Complete |
| v3.25.0 — Educational rewrite (first-position investor) + technicals-for-indices doctrine | 2026-07-02 | Complete |
| v3.26.0 — Screener: Daily Change % column + snapshot-first column reorder | 2026-07-02 | Complete |
| v3.27.0 — SEO/discoverability pass (FAQ schema, sitemap.xml, canonicals, meta review) | 2026-07-03 | Complete |
| Google Search Console setup — property verified 2026-07-03 (meta tag, v3.27.5), sitemap.xml submitted; awaiting first Google fetch (new-property "Couldn't fetch" is normal for up to ~48h; sitemap confirmed serving HTTP 200 application/xml) | 2026-07-03 | Complete (pending Google fetch) |
| v3.28.0 — Screener: Growth, Value, and Dividend (GVD) universes. Three new selectable datasets alongside the Nasdaq 100 and S&P 500: Growth = top 100 holdings of VUG (Vanguard Growth ETF), Value = top 100 holdings of VTV (Vanguard Value ETF, owner-added 2026-07-03), Dividend = top 100 holdings of VIG (Vanguard Dividend Appreciation ETF). All three ship in a single combined feed file (`data/screener_gvd.json`) refreshed on trading days 30 minutes after the S&P 500 feed (00:00 UTC, Tue-Sat cron); constituents auto-synced weekly from Vanguard's own holdings API (the source of truth for an ETF-defined universe; Vanguard publishes holdings monthly). Includes pinning the yfinance version (==1.4.1) across all data workflows (folded in from pipeline hardening, since this release touches every workflow anyway) | 2026-07-03 | Complete |
| v3.29.0 — Screener: S/A/B/C/F tier scale, rank-based (owner-decided 2026-07-03; pulled ahead of pipeline cleanup by owner priority). Pass/Watch/Fail replaced by a tier list assigned by rank within the loaded universe: **S** = top 10% (dark green), **A** = next 10% (light green), **B** = 20-50% (yellow), **C** = 50-75% (light red), **F** = bottom 25% (dark red), boundary ties round up into the higher tier. Column and chips relabeled **Tier**; 4 new color tokens; tier drives badge and score-bar colors. Tier-list vocabulary chosen over the owner's first proposal (Strong Buy through Strong Sell), which conflicted with this PRD's non-goals ("not a buy/sell signal generator", "no financial advice language"); rank-based bands chosen over fixed score cuts (80/65/50/35) so tier sizes stay constant per universe regardless of score clustering | 2026-07-03 | Complete |
| v3.30.0 — Screener: scoring model v2 (owner decisions locked 2026-07-03, pulled ahead of pipeline cleanup). Four weighted pillars over eight metrics: Growth 40 (Rev TTM 10, Rev FWD 10, EPS TTM 10, EPS FWD 10, adding the TTM pair per owner request), Valuation 20 (PEG FWD only; the P/E-vs-growth ratio drops to a zero-weight context ranking, removing the old double-count), Profitability 20 (gross margin 10, net margin 10, new `grossMargin`/`netMargin` feed fields, aligning the screener with doctrine metrics 11-12), Balance sheet 20 (cash vs debt). Points curve re-clamped from top/bottom 25% to top/bottom 28% (calibrated against the final live 8-metric feeds, replacing an interim 15% clamp fitted before the margin fields existed) to the owner's target of ~1 perfect 100 in the Nasdaq 100 and ~5 in the S&P 500, ties rounding up (live result at ship: 2 tied at 100 in the Nasdaq 100, exactly 5 in the S&P 500). A perfect 100 earns the **S+ tier** (owner request 2026-07-03, purple `--color-tier-splus`), sitting above the rank bands. Missing data ("—") scores a hard zero and renders dark red; the /100 denominator never shrinks. Methodology popup rewritten: pillar table, new points curve, universe-source table (Nasdaq 100 and S&P 500 from the indices, Growth/Value/Dividend from top-100 VUG/VTV/VIG holdings), hard-zero rule. All three feeds reseeded with margins | 2026-07-03 | Complete |
| v3.31.0 — Screener: margins removed from scoring, owner growth-forward weights (owner decision 2026-07-03, same day as v3.30.0). The owner had not intended gross/net margin to be scored: the Profitability pillar and its two columns are removed, leaving six metrics in three pillars with owner-set weights Rev TTM 10, Rev FWD 20, EPS TTM 10, EPS FWD 20 (forward growth counts double trailing), PEG FWD 20, Cash vs Debt 20 (Growth 60 / Valuation 20 / Balance sheet 20). Curve re-clamped to top/bottom 22%, recalibrated on the 6-metric model to the same target (~1 perfect 100 in the Nasdaq 100, ~5 in the S&P 500; live at ship: 2 tied and exactly 5). The `grossMargin`/`netMargin` feed fields stay in the pipeline and JSON (harmless, available for future use); Factors chip becomes /6 | 2026-07-03 | Complete |
| v3.32.0 — Pipeline cleanup. Legacy `FMP_API_KEY` secret deleted from repo settings by the owner (unused since v3.16.0; verified no workflow, script, or page references FMP). Data-files-in-git reclassified from tech debt to intentional design: the committed feeds' git history is the score record that the v4.0.0 sparklines will mine (renumbered v4.1.0 on 2026-07-04, see v3.34.12) | 2026-07-03 | Complete |
| v3.32.1 — Docs only. ETFs universe pulled ahead of the International universe in the roadmap by owner priority; milestone numbers swapped (ETFs now v3.33.0, International now v3.34.0) | 2026-07-03 | Complete |
| v3.32.2 — Docs only. v3.33.0 ETF Universe Scoring Model spec locked: the 10-fund fixed list, the 11 visible columns, and 90 of 100 scoring points, per owner instruction. Last 10-point criterion still pending an owner decision | 2026-07-03 | Complete |
| v3.32.3 — Docs only. v3.33.0 ETF Universe Scoring Model spec completed: last 10 points assigned to Price vs 200-Day Moving Average (highest is best); Price vs 20-Day and Price vs 100-Day Moving Average added as unscored display/context columns. Full 100/100 scoring model and 14 visible columns now locked | 2026-07-03 | Complete |
| v3.32.4 — Docs only. Four pre-implementation review concerns logged against the v3.33.0 ETF spec (yield double-count/style bias, 50 correlated timing points, tier bands vs a 10-fund list, percentile coarseness at N=10); spec unchanged, concerns to be resolved during implementation | 2026-07-03 | Complete |
| v3.33.0 — Screener: ETFs universe (owner-requested 2026-07-03; pulled ahead of the International universe by owner priority 2026-07-03; owner locked the full spec, fund list, visible fields, and all 100 scoring points, 2026-07-03, see the ETF Universe Scoring Model spec below). A **fixed** list of 10 owner-picked ETFs (QQQ, SPY, DIA, IWM, VTI, VXUS, VUG, VIG, VTV, SPMO — no auto-sync, no Vanguard-holdings dependency) rated on an entirely different basis than the stock universes: **technicals (RSI, 52-week range), long-term performance (1/5/10-year returns), yield, and expense ratio, not fundamentals**. This is doctrine-consistent by design: the methodology's own rule is that technicals time index/ETF purchases while stocks are judged on fundamentals, so the ETF universe gets the technical scoring the stock universes deliberately exclude. Needs its own scoring model, its own column set (no Rev/EPS/PEG columns), feed fields from yfinance (price history for RSI/52W/returns; trailing yield; expense ratio, if available via yfinance `fundInfo`/`info` — needs verification per fund), and methodology popup section. Shipped 2026-07-03: sixth universe button, new `data/etfs.json` fixed list + `scripts/fetch_etf_data.py` + `data/screener_etfs.json` feed + Mon-Fri 23:15 UTC workflow, config-driven table header (screener.js re-renders the `<thead>` and Columns menu per universe kind, pre-paying for future non-stock universes), rank-linear scoring, per-fund popup, methodology popup ETF section. Verified headless against the live local feed: 10/10 scored, tiers 1 S / 1 A / 3 B / 3 C / 2 F, stock universes unregressed | 2026-07-03 | Complete |
| v3.33.1 — Docs only. New `docs/ROADMAP.md`: detailed implementation plans for every remaining roadmap item (v3.34.0 International with a probe-first phase plan, v4.0.0 sparklines with the recompute-from-git-history design and Python-port parity gate, v4.1.0-v4.4.0 content release plans with a shared release checklist), per owner request (v4.x renumbered on 2026-07-04, see v3.34.12) | 2026-07-03 | Complete |
| v3.33.2 — Docs only. Ran the v3.34.0 Phase 0 probe (Vanguard API shape, ISIN→Yahoo symbol resolution, yfinance field coverage) live against real VXUS data and logged findings in ROADMAP.md and this milestone row; no code, workflow, or behavior changes | 2026-07-03 | Complete |
| v3.34.0 — Screener: International universe, top 100 holdings of VXUS (Vanguard Total International Stock ETF) only, scored with the **same six-metric stock model** as the other stock universes (no scoring changes; this is a stock universe, not a variant). Probed and built 2026-07-03/04. **Phase 0 probe** found: Vanguard's holdings API caps at exactly 500 entities (not ~8,500), every entity carries an ISIN; two ISINs (BHP Group, Barrick Gold) appear as **split duplicate rows that must be summed before ranking**, or the top-100 cut silently admits 98 unique issuers plus one double-counted holding; ISIN→Yahoo resolution hit 100/100 (99 direct via Yahoo search, 1 via name-search fallback for a holding with a blank Vanguard ticker field, 3 correctly auto-resolved dual-listing cases pinned into the manual-override cache for stability); yfinance field coverage on all six scored metrics is 88-100%. **Owner decisions locked**: native-currency display labeled with the **currency symbol** (NT$/₩/€/£/¥/HK$/C$ etc., ISO-code fallback for symbol-less currencies like CHF); hard-zero rule kept exactly as-specced (coverage was strong enough that no denominator change was needed); rank the local listing Vanguard actually holds, not a US ADR. **Build-time discovery not anticipated in the plan**: Yahoo quotes London-listed stocks (`HSBA.L`, `BP.L`, `RIO.L`, etc.) in **pence** (`GBp`), not pounds, while that same listing's market cap/cash/debt are already reported in pounds (verified: HSBC's marketCap == its pence-converted price &times; shares outstanding) — the pipeline normalizes this (divide by 100, relabel `GBP`) so the frontend never has to know about the quirk. Shipped: seventh universe button, `data/vxus.json` (100 resolved Yahoo symbols) + `data/vxus_map.json` (ISIN&rarr;symbol cache with manual overrides) + `update_etf_constituents.py` `sync_vxus()` (tested idempotent against the live Vanguard API) + `data/screener_intl.json` feed + Tue-Sat 00:15 UTC workflow, joined into the Saturday constituent-sync workflow; `screener.js` gained a `cur`-aware `fmtPrice`/`fmtMoney` (defaults to `$` when absent, so the five domestic universes are byte-for-byte unaffected) and a `CURRENCY_SYMBOLS` lookup; `fetch_screener_data.py`'s dot-to-dash ticker fix (for `BRK.B`-style dual classes) was narrowed from a blanket replace to an explicit 2-ticker set, since a blanket replace would have corrupted every International exchange suffix (e.g. `2330.TW` &rarr; `2330-TW`). Verified headless against the live local feed: 100/100 scored, tiers 1 S+ / 10 S / 13 A / 29 B / 22 C / 25 F, currency symbols render correctly per row, Nasdaq 100 regression still exactly matches the v3.31.0 baseline (2 S+ / 10 S / 8 A / 32 B / 24 C / 24 F, MU and NVDA at 100) | 2026-07-04 | Complete |
| v3.34.1 — Docs only. New roadmap item logged: a screener Methodology audit (confirm popup content is current against the shipped model after five same-day edits) plus a table-display bug fix. Root cause already found by code inspection: `style.css`'s `.table-wrap` rule sets `overflow-x: auto` but a later `overflow: hidden` in the same block silently overrides it for both axes, clipping wide methodology tables instead of scrolling them; compounded by `thead th { white-space: nowrap }` forcing headers not to wrap. See ROADMAP.md v3.35.0 for the full plan | 2026-07-04 | Complete |
| v3.34.2 — Docs only. Owner requested a GitHub Actions workflow timing review as the immediate next step, and a site-wide mobile-friendliness pass appended to the end of the roadmap at the time (later reprioritized to the front and renumbered v4.0.0, see v3.34.11). Both logged in ROADMAP.md; the timing review's schedule table and findings were compiled the same day, see v3.34.5 below | 2026-07-04 | Complete |
| v3.34.5 — Ops. GitHub Actions workflow timing review, owner-requested. Owner decisions: keep a fixed non-DST-aware schedule, but re-anchor 30 minutes after the *latest possible* US market close in UTC terms (winter EST close is 21:00 UTC, later than summer EDT's 20:00 UTC) instead of a fixed Eastern-clock offset, guaranteeing at least a 30-minute post-close buffer year-round (up to 90 in summer); widen every gap in the chain to a uniform 30 minutes. New same-day schedule: Nasdaq 100 21:30 → ETFs 22:00 → S&P 500 22:30 → GVD 23:00 → International 23:30 UTC (all Mon-Fri; the day-rollover Tue-Sat cron pattern the GVD/International jobs needed is gone). All five daily workflow files updated; docs (README, PRD pipeline/architecture/FAQ) updated to match | 2026-07-04 | Complete |
| v3.34.3 — Docs only. Owner-flagged bug logged: the International feed lists the same company twice under different share classes (`005930.KS`/`005935.KS`, Samsung Electronics common/preferred, different ISINs). Logged as v3.34.6 in ROADMAP.md, sequenced right after the workflow timing review | 2026-07-04 | Complete |
| v3.34.6 — Screener/pipeline. International feed: same-company duplicate holdings fixed (owner-flagged: `005930.KS`/`005935.KS` were both Samsung Electronics, common and preferred). Scanned the full raw Vanguard response by name-normalization and hand-verified every candidate — this caught a false positive the same heuristic would have wrongly merged (SoftBank Group Corp and SoftBank Corp are genuinely different companies, not share classes), confirming the plan's caution against automatic name-matching. Found and fixed 3 categories via a hand-verified `VXUS_SAME_ISSUER_MERGE` map in `update_etf_constituents.py` (8 entries): a duplicate custody record for the identical security (Air Liquide/L'Oreal/Engie, one line always blank-ticker), a real dual share class (Samsung, Investor AB, Atlas Copco), and a dual listing of the same group across exchanges (Rio Tinto, CATL). Rebuilding correctly promoted L'Oreal and Investor AB into the true top 100 on their combined weight. Verified: 100 unique companies, `sync_vxus()` idempotent against the live API. See ROADMAP.md for the full record | 2026-07-04 | Complete |
| v3.34.4 — Docs only. Two owner-requested screener features logged: International universe should lead with company name instead of ticker (v3.34.7), and a "FANG+" filter (v3.36.0, blocked on the owner supplying the ticker list — designed as a client-side filter over the currently loaded universe, not a new universe/feed) | 2026-07-04 | Complete |
| v3.34.7 — International universe: display company name as primary, ticker secondary (owner-requested; local-exchange tickers like `005930.KS` are meaningless to most readers, unlike domestic tickers). Added a `nameFirst` per-universe display hint (`UNIVERSES.intl`), swapping cell prominence/DOM order, the mobile-breakpoint hide rule, the column header label ("Company"), the ticker-column sort comparator, and the per-stock popup title — all gated on the new flag, a confirmed no-op for the five domestic universes. See ROADMAP.md for the full record | 2026-07-04 | Complete |
| v3.34.8 — Screener bug fix. Horizontal scroll broken at some resolutions (reported: a friend of the owner's couldn't scroll the table left/right at all). Root cause: two compounding, classic CSS gotchas — `.app-table-wrap` missing `min-height: 0` on a `flex:1` child of a column flex container (defaults to `min-height:auto`, overflowing its parent instead of scrolling itself), and the shared `.site-layout` grid using a bare `1fr` column (implicit `min-width:auto`) instead of `minmax(0, 1fr)`. Both browser-rounding-sensitive, explaining "works on my machine, breaks at a different resolution." Fixed with two one-line CSS changes; verified via before/after headless screenshots at a constrained viewport. Kept as its own bug-fix item, not folded into v4.0.0 — a correctness fix needed immediately, not a design-pass question | 2026-07-04 | Complete |
| v3.34.10 — Screener bug, diagnosis only (superseded). Two further reports after v3.34.8 shipped confirmed the scroll issue wasn't fully fixed (Opera at 1280×1024 on a 10-row ETFs table; Chrome window-narrowing). Diagnosed via a live-site width sweep: the v3.34.8 box-sizing fix is correct at every width, but headless Chromium can't reproduce what real Opera/Chrome show — pointing at the browsers' default overlay scrollbar (invisible in a static look) as the cause. A scrollbar-visibility fix was drafted but never shipped: owner clarified the real requirement is eliminating the need to scroll entirely, folding this into a reprioritized v4.0.0. See ROADMAP.md for the full diagnosis record | 2026-07-04 | Superseded by v4.0.0 |
| v3.34.11 — Docs only. Owner clarified the real requirement for the screener scroll issue: eliminate the need to scroll entirely (auto-hide columns responsively) rather than making the existing scrollbar easier to find. Merged v3.34.10's diagnosis into a reprioritized mobile pass (then still numbered v4.5.0), moved from the end of the roadmap to the front of the queue, since both are the same underlying design question across the full width range (desktop-narrow through phone) | 2026-07-04 | Complete |
| v3.34.12 — Docs only. Owner asked to renumber the reprioritized mobile pass to v4.0.0 to match its new front-of-queue position, rather than keep the v4.5.0 label from when it was the last item on the roadmap. All five other v4.x items shift by one: sparklines v4.0.0→v4.1.0, index coverage v4.1.0→v4.2.0, historical examples v4.2.0→v4.3.0, philosophy v4.3.0→v4.4.0, conference call guide v4.4.0→v4.5.0. PATCHNOTES entries dated before today are left with their original numbers (a dated changelog, not renumbered retroactively); this table's older rows were updated for consistency since it's a living reference, not a changelog | 2026-07-04 | Complete |
| v3.34.9 — Docs only. Owner flagged that the ETFs universe rating methodology needs a review; no specifics given yet, logged as v3.37.0 (unscoped) in ROADMAP.md pending the owner's follow-up | 2026-07-04 | Complete |
| v3.34.13 — Docs only. Finalized roadmap order: v3.36.0 (renamed "FANG+" → "MAG 10" with the owner-supplied ticker list) moved to the front as next up; v3.37.0 (ETFs rating review) moved ahead of v4.0.0; v3.35.0 retired and merged into v4.0.0 (both are screener table/CSS work). See ROADMAP.md for the full restructure | 2026-07-04 | Complete |
| v3.36.0 — **"MAG 10" filter shipped.** Fixed 10-ticker watchlist (AAPL, AMD, AMZN, AVGO, GOOGL, META, MSFT, NFLX, NVDA, TSLA), renamed from the "FANG+" placeholder once the owner supplied the list. A client-side toggle sourced specifically from S&P 500 data (owner instruction) — switches the active universe to S&P 500 if needed, then filters to these 10 rows, so each stock's score/tier reflects its percentile among the full 500-stock universe; ANDs with the existing tier filter and search box; auto-deactivates on manual universe switch. Verified via headless Chrome (script-injected click): correct 10-row filter, correct AND with tier chips, zero regression on the default Nasdaq 100 load. See ROADMAP.md for the full record | 2026-07-04 | Complete |
| v3.36.1 — Docs only. ETF rating methodology review: current model presented, cross-checked against `indices.html`, 3 doctrine gaps found. Owner decided to document Price vs 200-Day MA on `indices.html` (rather than remove it from the screener) and to remove Yield/Expense Ratio, with a recommendation given for reallocating the freed 20 points. Logged in ROADMAP.md v3.37.0; awaiting the owner's reallocation decision | 2026-07-04 | Complete |
| v3.37.1 — Screener UI tweak. "MAG 10" button (v3.36.0) moved from the tier-chip toolbar row to the top app-bar, to the right of the International universe button, per owner request. Left-border/margin separates it visually from the universe buttons since it's a filter toggle, not an eighth universe. Re-verified via headless Chrome screenshot; Nasdaq 100 regression unaffected | 2026-07-04 | Complete |
| v3.37.2 — Screener UX tweak. Stale-data banner threshold raised from 24 hours to a week (owner feedback: 24 hours fired too eagerly for a daily-refresh pipeline that can reasonably slip a day). `isStale()`, banner copy, static HTML fallback, and PRD's own runbook/API-design mentions all updated for consistency. Verified via headless Chrome: banner correctly absent for data that's stale under the old threshold but not the new one | 2026-07-04 | Complete |
| v3.37.0 — ETFs universe rating methodology review, **fully shipped.** Current methodology presented and cross-checked against `indices.html`'s own doctrine, surfacing 3 gaps (VIX/AAII structurally can't be per-fund metrics; Price vs 200-Day MA was scored but undocumented on `indices.html`, owner decided to document it rather than remove it, written up under v4.0.0; YTD is doctrine-named but unscored while 1Y isn't doctrine-named but is scored — remains unaddressed, owner declined the recommendation to promote YTD). Owner removed Yield and Expense Ratio from scoring (demoted to weight-0 context, still displayed) and weighted up the two longest return horizons instead: 5-Year 10→20, 10-Year 10→20, keeping 1-Year at 10. Final model: Technicals 50 (unchanged) + Performance 50 (1Y 10, 5Y 20, 10Y 20) = 100. `ETF_METRICS`, `ETF_POPUP_METRICS`, column header titles, and the `#methodEtf` popup all updated. Verified via headless Chrome (ETFs universe: 10/10 scored, tiers 1S/1A/3B/3C/2F, Factors chip now `/6`) and a Nasdaq 100 regression check (exact match to the v3.31.0 baseline). See ROADMAP.md for the full record | 2026-07-04 | Complete |
| v4.0.0 — **Screener responsive redesign, methodology table fix & site-wide mobile-friendliness pass, shipped** (absorbs the retired v3.35.0). Fixed the methodology modal's `.table-wrap` CSS bug (a trailing `overflow: hidden` shorthand was silently cancelling `overflow-x: auto`); audited `#methodStock`/`#methodEtf` content against the current scoring code (no drift found). Implemented live-responsive auto-hide column groups (owner decision: recompute on every resize, overriding manual Columns-menu picks, rather than a one-time load default) — Ticker/Tier/Score/Factors always visible; stock kind hides Snapshot→Balance→Valuation→Growth as the window narrows, ETF kind hides Income&Cost→Snapshot→Performance→Technicals. Width-audit also surfaced and fixed a second implicit-`min-width:auto` grid bug: the mobile media query reset `.site-layout`'s grid track to a bare `1fr`, dropping the v3.34.8 `minmax(0, 1fr)` fix exactly at phone widths, so the universe-button row overflowed the page instead of wrapping. Wrote the Price vs 200-Day Moving Average subsection into `indices.html`'s Timing Signals section (framed as a trend-health confirmation signal, distinct from RSI/52W range's contrarian dip-buying framing), updating the page's doctrine counts from nine metrics/four timing signals to ten metrics/five timing signals throughout. Verified via headless Chrome: zero page-level horizontal overflow from 375px to 1920px across the screener (both stock and ETF kind) and all 8 other content pages; Nasdaq 100 regression exactly matches the v3.31.0 baseline. See ROADMAP.md for the full as-built record | 2026-07-04 | Complete |
| v4.0.1 — Screener UI bug fix. Owner reported the MAG 10 button "appears different than the others" in the app-bar; diagnosed via `getBoundingClientRect()` that its `margin-left: 6px` (added in v3.37.1) stacked on top of `.universe-group`'s own `gap: 6px`, doubling its lead-in gap to 12px versus every other button's 6px. Removed the redundant margin; the intentional left-border divider and squared-off corner are unaffected. Verified via headless Chrome edge measurements: uniform 6.0px gap between all 8 app-bar buttons | 2026-07-04 | Complete |
| v4.1.1 — Content: two new philosophy sections + two new FAQ items, sourced from a video transcript review (owner-requested, pulled ahead of v4.1.0 by direct instruction). "Investor, Not Trader" (`philosophy.html#section-trader`, `faq.html#answer-trader`) generalizes the transcript's warning about volatile stretches pulling investors into trading behavior (chasing price action, the gambler's-chase pattern) into durable doctrine: hold the fundamentals test constant regardless of a position's size or the last week's price swings. "Why We Wait on IPOs" (`philosophy.html#section-ipo`, `faq.html#answer-ipo`) is new ground for the site: IPO timing favors the seller, not the buyer, illustrated with the closed 2021 SPAC/IPO boom and Meta's own 2012 IPO ($38 to sub-$18 within the year) as historical (non-live-price) examples, and ties the "no-touch" rule to requirements the methodology already has (conference call history, multi-quarter financials) rather than inventing a new rule. Ticker-specific, dated commentary from the source video (single-stock price targets, capex debates, one creator's current portfolio positions) was deliberately excluded as out of scope per this doc's non-goals and permanence tenet. FAQ item count 34→36, philosophy section count 9(stale)/10(actual)→12; all three counts corrected across README/PRD | 2026-07-08 | Complete |
| v4.1.2 — Screener UI bug fix. Owner reported the MAG 10 button "looks weird when I click on it." `#mag10Btn`'s segmented-control overrides (`border-radius: 0 7px 7px 0`, `border-left`, `padding-left: 12px` — added in v4.0.1 as a divider to read "filter, not an eighth universe") never actually sat flush against the universe buttons, since `.universe-group` uses `gap: 6px`; the squared-off left corners just looked broken once the accent border lit up on click. Removed all three overrides; MAG 10 is now a plain `.btn` rendering identically to the universe buttons in both states. **Reverses the v4.0.1 "keep the squared-off corner" decision** — consistency wins now that the segmented look never worked with the flex gap in place | 2026-07-09 | Complete |
| v4.1.3 — Docs only, backfilled. Sidebar rebrand to "Azqato Invests" with an "Individual Stocks" sub-label (shipped as commit `b856324` without a PATCHNOTES entry) logged retroactively: brand text 0.9rem→1.125rem with -0.3px letter-spacing, new `.sidebar-brand-sub` muted sub-label, applied across all 8 content pages and screener.html via shared `style.css` rules | 2026-07-09 | Complete |
| v4.1.0 — **Market Overview page, shipped.** New standalone page `market.html`: a CNBC-style card strip showing price/change for DIA, SPY, QQQ, IWM, VTI, VXUS, VUG, VTV, VIG, and VIX, in that fixed order. Owner decisions (locked via AskUserQuestion before build): standalone page, not a widget on an existing page; prioritized ahead of the sparklines release (renumbered to v4.2.0). Cadence was initially scoped as a once-daily batch snapshot, then **changed mid-build to intraday** (three runs per trading day: 15:00, 19:00, 22:00 UTC) per direct owner instruction — the only workflow in the pipeline that isn't once-daily-after-close; the stale-banner threshold was recalibrated 7 days→4 days to fit. Explicitly a snapshot, not a screener extension: no scoring, tiers, or ranking. New lightweight `scripts/fetch_market_overview.py` and `data/market_overview.json` feed, kept independent of the scored ETFs universe (`fetch_etf_data.py`/`screener_etfs.json`) since it needs far fewer fields; VIX fetched via its Yahoo index symbol `^VIX`. New `market-overview.yml` workflow, sharing the `screener-data` concurrency group (its 22:00 UTC run queues behind the ETFs feed job rather than racing it). Nav link added to all 9 pages, `sitemap.xml` entry added. Verified via headless Chrome: correct data and green/red coloring on all 10 cards (including a live down-day on VIX exercising the red path), zero horizontal overflow 375-1920px, 2-column mobile card layout confirmed at 700px. See ROADMAP.md for the full as-built record | 2026-07-10 | Complete |
| v4.1.4 — **Market Overview: expanded symbol list, renames, sectioned placeholders, shipped.** Same-day owner follow-up while testing the live v4.1.0 page. Renamed 5 card labels for brevity (Dow Jones, US Market, International Market, Dividend, Volatility). Added 7 symbols to the benchmarks group (TLT, RSP, SPMO, VBR, IJH, IJR, XLP; 17 total), reordered so SPY/QQQ/VIX lead. Removed the "not the screener" explainer callout per owner request. Reworked `data/market_overview_list.json` to carry a `"g"` (group) field, threaded through `fetch_market_overview.py` into each quote's `"group"` field, letting `market.html` drop its hardcoded `ORDER` array entirely (now iterates the feed's own insertion order and buckets by group) — removes a config-drift risk between the list file and the frontend. New "Industries" (VNQ) and "Leveraged ETFs" (TQQQ) placeholder sections, each hidden automatically if empty, meant to grow one symbol at a time. Verified via headless Chrome with `raw.githubusercontent.com` network-blocked to force the local data path (the earlier v4.1.0 push had already made stale data live at that URL): correct order, renames, and section rendering confirmed; TQQQ's live move (+4.98%) sanity-checked against QQQ's (+1.66%), consistent with a ~3x leveraged relationship. See ROADMAP.md for the full as-built record | 2026-07-10 | Complete |
| v4.1.5 — **Market Overview: bond yields, commodities, crypto & UI polish, shipped.** Same-day continuation of v4.1.4. Bond yields: owner asked for actual yields (percent + point-change), not fund price movement, per a CNBC "Bonds" tab reference. US Treasury yields work directly via yfinance, already in percent (`^TNX` 10Y, `^TYX` 30Y, `2YY=F` 2Y); foreign sovereign yields are **not available** (every ticker guess 404'd) — shipped US-only, scope corrected and confirmed with the owner. New `"unit": "pct"` field drives a distinct yield-card renderer (percent + bare point-delta, not percent-of-percent). Commodities (Gold `GLD`, Oil `CL=F`) and Crypto (Bitcoin `BTC-USD`) all work through the same plain price/prevClose mechanism as everything else, no special API needed. **Bug found and fixed**: the render function's group-bucket object was hardcoded to 3 of what were now 6 groups, silently misrouting new-group cards into the Indices grid — fixed by deriving it from the same config used for grid/section lookup. UI polish: "Benchmarks" retitled "Indices" with a heading, "Market Snapshot" badge removed, "Last updated" restyled as a `.hero-badge` pill moved into the intro, vertical spacing tightened. Verified via headless Chrome (network-blocked to force the local data path): 25/25 symbols across 6 groups render correctly and independently after the bucket fix. See ROADMAP.md for the full as-built record, including the mortgage-rate gap (needs FRED, not yfinance — folded into v4.2.0) | 2026-07-10 | Complete |
| v4.2.0 — **Market Overview: reorganize categories & mortgage rate, planned.** Two owner requests logged together, both unscoped pending owner input: (1) reorganize the page's now-6 sections (added incrementally over one session) — do not guess a new structure, wait for specifics; (2) mortgage rate needs a non-yfinance data source (likely FRED's `MORTGAGE30US` series, requiring this site's first-ever API key) — needs its own probe before design. See ROADMAP.md | Next up | Planned |
| v4.3.0 — **Market Overview: period-return filters, planned.** Owner request: YTD/12-Month/5-Year/10-Year return filters. Materially bigger than prior Market Overview additions — needs real price history (like `fetch_etf_data.py`'s existing return calculations), not the single-quote snapshot every other card uses, plus a UI toggle/filter control and a decision on whether returns refresh on the same 3x/day cadence as prices (likely not, since history-based returns don't change intraday). Awaiting owner scope confirmation. See ROADMAP.md | TBD | Planned |
| v4.4.0 — Screener score history sparklines (mine screener.json git history for per-stock score trends; renumbered from v4.1.0 on 2026-07-09, then v4.2.0 on 2026-07-10, then v4.3.0 on 2026-07-10 as further Market Overview items were prioritized ahead of it) | After v4.3.0 | Planned |
| v4.5.0 — Deeper index fund coverage (sector ETFs, international allocation, bond tent strategy; renumbered from v4.2.0→v4.3.0→v4.4.0 across the same sequence of reprioritizations) | TBD | Planned |
| v4.6.0 — Additional illustrative examples using historical market events (renumbered from v4.3.0→v4.4.0→v4.5.0) | TBD | Planned |
| v4.7.0 — Additional philosophy sections (renumbered from v4.4.0→v4.5.0→v4.6.0) | TBD | Planned |
| v4.8.0 — Conference call research guide (renumbered from v4.5.0→v4.6.0→v4.7.0) | TBD | Planned |

### Feature Breakdown by Phase

**v3.x (current):** Screener with daily data, relative percentile scoring, methodology popup, documentation consolidation.

**Queue head (updated 2026-07-04):** v3.28.0 GVD universes, v3.29.0 rank-based tier scale, v3.30.0 scoring model v2, v3.31.0 margins-out re-weighting, v3.32.0 pipeline cleanup, v3.33.0 ETFs universe, v3.34.0 International universe, v3.34.5 workflow timing review, v3.34.6 International same-company duplicate fix, v3.34.7 International name-primary display, v3.34.8 horizontal-scroll bug fix, v3.36.0 "MAG 10" filter, v3.37.0 ETF rating methodology review, and v4.0.0 screener responsive redesign are all shipped — all seven screener universes are live, the daily pipeline is re-scheduled (Nasdaq 100 21:30 → ETFs 22:00 → S&P 500 22:30 → GVD 23:00 → International 23:30 UTC, all Mon-Fri, 30-min gaps throughout, anchored to the latest-possible market close), the International list's top 100 correctly represents 100 distinct companies, the International universe leads with company names, a fixed 10-stock "MAG 10" watchlist toggle scores against the full S&P 500, the ETF scoring model is reweighted (Yield/Expense Ratio removed, 5Y/10Y weighted up), the screener now auto-hides column groups responsively so no width ever requires horizontal scroll, and `indices.html` documents Price vs 200-Day MA as a fifth timing signal. v3.34.10's scrollbar-visibility fix is superseded; v3.35.0 is retired and merged into v4.0.0. v4.1.0 Market Overview page also shipped 2026-07-10 (`market.html`, 9th content page, own intraday feed), followed same-day by v4.1.4 (symbol expansion to 19 across 3 groups, renames, grouped-section rendering) and v4.1.5 (bond yields, commodities, crypto, 25 symbols across 6 groups, UI polish). **Next: v4.2.0** Market Overview reorganize-categories & mortgage-rate (both awaiting owner scope), then v4.3.0 Market Overview period-return filters (awaiting owner scope), then v4.4.0 sparklines, then v4.5.0-v4.8.0 content releases. Constituent sourcing decision (2026-07-03): index universes stay on Wikipedia (updates within days of index changes); ETF universes use Vanguard's holdings API (authoritative but month-lagged, acceptable because the fund's published holdings are the universe definition). Switching the S&P 500 to VOO holdings was considered and rejected for the freshness reason. Note the dependency: the v4.4.0 sparklines mine the git history of the committed data feeds, so keeping generated data files in the repo is an intentional design choice, not tech debt.

**v4.x (order updated 2026-07-10):** v4.0.0 screener responsive redesign & site-wide mobile-friendliness pass shipped 2026-07-04, v4.0.1 MAG 10 button spacing fix shipped same day, v4.1.1 two new philosophy sections + FAQ items shipped 2026-07-08, v4.1.2 MAG 10 button restyle and v4.1.3 sidebar rebrand (docs backfill) shipped 2026-07-09, v4.1.0/v4.1.4/v4.1.5 Market Overview (page, then two same-day expansions) all shipped 2026-07-10, v4.2.0 Market Overview reorganize-categories & mortgage-rate next (both awaiting owner scope), v4.3.0 Market Overview period-return filters (awaiting owner scope), v4.4.0 score history sparklines, v4.5.0 deeper index fund coverage, v4.6.0 additional historical illustrative examples, v4.7.0 additional philosophy sections, v4.8.0 conference call research guide. Potential Growth/Value/Dividend standalone framework pages remain unversioned backlog.

### Explicitly Deferred

- Email/RSS changelog subscription: removed from the roadmap by owner decision (2026-07-03); not planned
- Historical backtests of the scoring model: removed from the roadmap by owner decision (2026-07-03); not planned
- Options/crypto/forex coverage: out of scope permanently; this methodology is equities-only

---

## Metrics

### North Star Metric

**Return visit rate:** The percentage of readers who come back within 30 days. A reader who returns has found the content trustworthy and useful enough to consult again. One-time visitors may be curious; return visitors are building a habit.

### Acquisition Metrics

| Metric | Target | Timeframe | Measurement |
|--------|--------|-----------|-------------|
| Monthly unique visitors | 1,000+ | 6 months post-launch | GitHub Pages analytics or Plausible |
| Referral traffic from Discord/Twitch | 30% of sessions | Ongoing | UTM parameters on shared links |
| Organic search impressions | 5,000/month | 12 months | Google Search Console |

### Engagement Metrics

| Metric | Target | Timeframe | Measurement |
|--------|--------|-----------|-------------|
| Average session duration | 4+ minutes | Ongoing | Analytics |
| Pages per session | 2.5+ | Ongoing | Analytics |
| Screener usage rate | 20% of visitors open screener | Ongoing | Analytics (page views) |
| FAQ engagement | 40% of FAQ visitors expand 3+ items | Ongoing | Analytics (events) |

### Retention Metrics

| Metric | Target | Timeframe | Measurement |
|--------|--------|-----------|-------------|
| Return visitor rate (30-day) | 25%+ | Ongoing | Analytics |
| Screener return rate | 40% of screener users return within 7 days | Ongoing | Analytics |

### Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Page load time (LCP) | Under 1.5s on 3G | Lighthouse / PageSpeed Insights |
| JavaScript bundle | Under 5KB | File inspection |
| CSS bundle | Under 50KB | File inspection |
| Time to Interactive | Under 2s | Lighthouse |
| Uptime | 99.9% (GitHub Pages SLA) | GitHub status page |
| screener.json freshness | Updated within 25 hours of previous | GitHub Actions run log |

### Reporting Cadence

- Performance metrics: monthly Lighthouse audit
- Acquisition and engagement: monthly review
- Retention: monthly review
- screener.json freshness: visible in screener "as of" timestamp, checked ad hoc

---

## Runbook

### Local Setup (from a fresh machine)

1. Install a modern browser (Chrome, Firefox, Safari, or Edge)
2. Install Python 3.12+ (only needed for the data pipeline)
3. Clone the repository: `git clone https://github.com/Azqato/stocks.git && cd stocks`
4. Install the pipeline dependency: `pip install yfinance`
5. Open `index.html` in a browser — the site works immediately for all pages except the screener data fetch
6. For the screener to load live data locally, run: `python3 -m http.server 8080` and visit `http://localhost:8080/screener.html`

### Build

There is no build step. The site is pure static files.

### Deploy

1. Commit changes to the `main` branch
2. Push to GitHub: `git push origin main`
3. GitHub Pages automatically serves the updated files within 1–2 minutes
4. Verify deployment at `https://azqato.github.io/stocks/`

GitHub Pages is configured to serve from the repository root. No additional configuration is needed.

### Data Pipeline (Automated)

Six data feeds are refreshed automatically, staggered so the default Nasdaq 100 view always has priority. Five of the six run once daily (2026-07-04 schedule, owner-reviewed), anchored 30 minutes after the **latest possible** US market close in UTC terms rather than a fixed Eastern-clock offset: close is always 4:00pm US Eastern, which is 21:00 UTC in winter (EST, UTC-5) but only 20:00 UTC in summer (EDT, UTC-4) — GitHub Actions cron is UTC-only and does not observe DST, so anchoring to the winter (later-in-UTC) close guarantees at least a 30-minute buffer after close year-round, growing to 90 minutes in summer. Every job in that daily chain lands on the same calendar day (no more day-rollover crons). The sixth, Market Overview (added 2026-07-10), is the one exception: it runs **three times per trading day** rather than once after close, per direct owner instruction:

- **Nasdaq 100** (`data/screener.json`): trading days (Mon-Fri) at 21:30 UTC via `.github/workflows/screener-data.yml`
- **ETFs** (`data/screener_etfs.json`): trading days (Mon-Fri) at 22:00 UTC via `.github/workflows/screener-data-etfs.yml` (a 10-symbol fetch that slots between the two index jobs; run by `scripts/fetch_etf_data.py`, which shares no field logic with the stock fetcher)
- **Market Overview** (`data/market_overview.json`): trading days (Mon-Fri) at 15:00, 19:00, and 22:00 UTC via `.github/workflows/market-overview.yml` — shortly after the open, midday, and shortly after the close, so this page reads as a same-day check-in rather than a close-of-business number. A 10-symbol price/change-only snapshot (`scripts/fetch_market_overview.py`), independent of the scored ETFs universe so it isn't affected by any future change to that list. The 22:00 run shares its trigger minute with the ETFs job above; both share the `screener-data` concurrency group with `cancel-in-progress: false`, so they queue rather than race
- **S&P 500** (`data/screener_sp500.json`): trading days (Mon-Fri) at 22:30 UTC via `.github/workflows/screener-data-sp500.yml` (the larger ~500-symbol fetch runs after the small jobs so it never delays them)
- **Growth/Value/Dividend** (`data/screener_gvd.json`): trading days (Mon-Fri) at 23:00 UTC via `.github/workflows/screener-data-gvd.yml`, 30 minutes after the S&P 500 job. One combined file holding all three universes; symbols shared between lists are fetched once (~220 unique of 300)
- **International** (`data/screener_intl.json`): trading days (Mon-Fri) at 23:30 UTC via `.github/workflows/screener-data-intl.yml`, 30 minutes after the GVD job — the last job in the daily chain. Top 100 VXUS holdings, same `fetch_screener_data.py` stock fetcher as the domestic universes (`--list data/vxus.json --out data/screener_intl.json`), plus a `cur` field (native ISO currency code) that the frontend uses to label Price/Mkt Cap/Cash/Debt in the listing's own currency instead of USD
- **Constituent sync** (`data/nasdaq100.json` + `data/sp500.json` from Wikipedia; `data/vug.json` + `data/vtv.json` + `data/vig.json` + `data/vxus.json` from Vanguard's holdings API): Saturdays at 23:00 UTC via `.github/workflows/constituents.yml`; regenerates a feed only if a list's membership changed. VXUS holdings are additionally resolved from ISIN to a suffixed Yahoo symbol via `data/vxus_map.json` (a committed resolution cache with a `manual` override block). The ETFs list (`data/etfs.json`) is **not** synced: it is a fixed, owner-curated set of 10 funds, changed only by hand
- **Trigger manually:** GitHub Actions tab → the relevant workflow → Run workflow (use this to seed a feed the first time)
- **Run locally:** `python3 scripts/fetch_screener_data.py --list data/nasdaq100.json --out data/screener.json` (the `--list`/`--out` args default to the Nasdaq 100; point them at `data/sp500.json` / `data/screener_sp500.json` for the S&P 500, or `data/vxus.json` / `data/screener_intl.json` for International). For the combined feed: `python3 scripts/fetch_screener_data.py --combined growth=data/vug.json --combined value=data/vtv.json --combined dividend=data/vig.json --out data/screener_gvd.json`
- **Output:** each feed holds its list's tickers with price, market cap, cash, debt, growth metrics, P/E, PEG, currency code, and timestamps; the GVD feed nests one `{updated, source, stocks}` object per universe under a `universes` key
- **No API key required** for the yfinance pipeline (yfinance is pinned to 1.4.1 in all workflows)

### Rollback

To revert to a previous version of the site:

```bash
git log --oneline        # find the commit hash
git revert <hash>        # creates a new revert commit
git push origin main     # deploys the revert
```

To revert `data/screener.json` to a known-good version:

```bash
git checkout <hash> -- data/screener.json
git commit -m "revert screener.json to <hash>"
git push origin main
```

### Environment Configs

| Environment | URL | Notes |
|-------------|-----|-------|
| Production | `https://azqato.github.io/stocks/` | Served by GitHub Pages from `main` |
| Local | `http://localhost:8080` | `python3 -m http.server 8080` from repo root |

No staging environment. Changes are previewed locally before pushing to main.

### Common Errors

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| Screener shows no data | `data/screener.json` missing or empty | Run the pipeline manually or wait for the next 21:30 UTC weekday cron run |
| Screener shows stale data banner | screener.json older than a week | Check GitHub Actions — if last run failed, trigger manually |
| GitHub Action fails with HTTP 429 | yfinance rate limit (Yahoo Finance throttling) | Wait and re-run; the pipeline has per-symbol retry logic |
| Page shows unstyled HTML | `style.css` path wrong | Check that style.css is in the same directory as the HTML file |
| Social card image missing | `og-image.png` not at site root | Verify the file exists at root; regenerate with the PowerShell snippet in DESIGN.md |
| Screener sorts wrong | `Infinity`/negative sentinels in sort logic | Negative P/E and PEG are mapped to worst-rank; debt-free companies sort to top of Cash/Debt |
| Screener shows "Couldn't load the data" | Offline, or `raw.githubusercontent.com` unreachable | Check connectivity; the page retries the same-origin copy and a localStorage cache |

### Monitoring

- **Uptime:** GitHub Pages status at `githubstatus.com`
- **Pipeline runs:** GitHub Actions tab in the repository
- **Data freshness:** The screener "as of" timestamp in the top bar
- **Errors:** Browser DevTools console on any page

---

## Technical Requirements

### System Architecture

The site is a fully static architecture. No server processes any requests. No database stores any state. All computation (screener scoring, sorting, filtering) happens client-side in the browser.

```
[GitHub Repository]
       │
       ├── main branch (HTML, CSS, JS, data/)
       │         │
       │    GitHub Pages → serves static files at azqato.github.io/stocks/
       │
       └── GitHub Actions (cron)
                 │
                 ├── Mon-Fri 21:30 UTC → fetch_screener_data.py --list nasdaq100.json → commits data/screener.json
                 │                       (30 min after the latest possible US market close, winter EST 21:00 UTC)
                 │
                 ├── Mon-Fri 22:00 UTC → fetch_etf_data.py (fixed 10-fund list)       → commits data/screener_etfs.json
                 │
                 ├── Mon-Fri 22:30 UTC → fetch_screener_data.py --list sp500.json     → commits data/screener_sp500.json
                 │
                 ├── Mon-Fri 23:00 UTC → fetch_screener_data.py --combined growth/value/dividend → commits data/screener_gvd.json
                 │                       (30 min after the S&P 500 run)
                 │
                 ├── Mon-Fri 23:30 UTC → fetch_screener_data.py --list vxus.json         → commits data/screener_intl.json
                 │                       (30 min after the GVD run; last job in the daily chain)
                 │
                 ├── Mon-Fri 15:00, 19:00, 22:00 UTC → fetch_market_overview.py (fixed 10-symbol list) → commits data/market_overview.json
                 │                       (intraday, not once-daily-after-close -- the one exception in this chain;
                 │                        22:00 run shares its trigger minute with the ETFs job, queues via concurrency group)
                 │
                 └── Sat 23:00 UTC     → update_constituents.py + update_etf_constituents.py → regenerates changed feed(s)
```

### Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| HTML | HTML5 semantic | Browser-native |
| CSS | CSS3 custom properties | Browser-native |
| JavaScript | ES6 (vanilla) | Browser-native |
| Data pipeline | Python 3 | 3.12+ |
| Data library | yfinance | 1.4.1 (pinned in all workflows) |
| Hosting | GitHub Pages | Free tier |
| CI/CD | GitHub Actions | Free tier |
| Data format | JSON | — |
| Version control | Git | — |

### Folder Structure

```
stocks/
├── README.md                          ← Developer front door
├── index.html                         ← Home page
├── philosophy.html                    ← Philosophy (12 sections)
├── metrics.html                       ← 12-metric glossary
├── screener.html                      ← Interactive Nasdaq 100 screener (app: markup + CSS)
├── screener.js                        ← Screener logic (data load, scoring, render, popup)
├── market.html                        ← Market Overview: daily benchmark snapshot (self-contained)
├── finviz.html                        ← Finviz setup guide
├── seekingalpha.html                  ← Seeking Alpha setup guide
├── indices.html                       ← Index/ETF methodology
├── faq.html                           ← FAQ accordion (36 items)
├── style.css                          ← Design system stylesheet
├── script.js                          ← Accordion + IntersectionObserver (content pages)
├── og-image.png                       ← Social card image (1200×630)
├── data/
│   ├── nasdaq100.json                 ← Nasdaq 100 constituent list (auto-synced from Wikipedia)
│   ├── sp500.json                     ← S&P 500 constituent list (auto-synced from Wikipedia)
│   ├── vug.json                       ← Growth list: top 100 VUG holdings (auto-synced from Vanguard)
│   ├── vtv.json                       ← Value list: top 100 VTV holdings (auto-synced from Vanguard)
│   ├── vig.json                       ← Dividend list: top 100 VIG holdings (auto-synced from Vanguard)
│   ├── etfs.json                      ← ETFs list: fixed, owner-curated 10 funds (hand-edited only)
│   ├── vxus.json                      ← International list: top 100 VXUS holdings (auto-synced, ISIN-resolved)
│   ├── vxus_map.json                  ← ISIN → Yahoo symbol resolution cache + manual overrides
│   ├── market_overview_list.json      ← Market Overview list: fixed, owner-curated 10 symbols (hand-edited only)
│   ├── screener.json                  ← Nasdaq 100 daily metrics feed
│   ├── screener_sp500.json            ← S&P 500 daily metrics feed
│   ├── screener_gvd.json              ← Combined Growth/Value/Dividend daily metrics feed
│   ├── screener_etfs.json             ← ETFs daily metrics feed (technicals/returns/yield/cost)
│   ├── screener_intl.json             ← International daily metrics feed (six-metric stock model + `cur`)
│   └── market_overview.json           ← Market Overview daily price/change snapshot (10 symbols)
├── scripts/
│   ├── fetch_screener_data.py         ← yfinance → stock screener feeds (--list/--out per index; --combined for GVD)
│   ├── fetch_etf_data.py              ← yfinance → ETFs feed (returns, RSI, MAs, yield, expense ratio, AUM)
│   ├── fetch_market_overview.py       ← yfinance → Market Overview feed (price/prevClose/change only)
│   ├── update_constituents.py         ← Wikipedia → nasdaq100.json + sp500.json (weekly auto-sync)
│   └── update_etf_constituents.py     ← Vanguard holdings API → vug/vtv/vig/vxus.json (weekly auto-sync)
├── img/                               ← Historical screenshots
├── .github/
│   └── workflows/
│       ├── screener-data.yml          ← Nasdaq 100 feed (Mon-Fri 21:30 UTC)
│       ├── screener-data-etfs.yml     ← ETFs feed (Mon-Fri 22:00 UTC)
│       ├── screener-data-sp500.yml    ← S&P 500 feed (Mon-Fri 22:30 UTC)
│       ├── screener-data-gvd.yml      ← Growth/Value/Dividend feed (Mon-Fri 23:00 UTC)
│       ├── screener-data-intl.yml     ← International feed (Mon-Fri 23:30 UTC)
│       ├── market-overview.yml        ← Market Overview feed (Mon-Fri 22:05 UTC)
│       └── constituents.yml           ← Constituent sync, indices + ETFs (Sat 23:00 UTC)
└── docs/
    ├── PRD.md                         ← This file
    ├── DESIGN.md                      ← Design specification
    ├── PATCHNOTES.md                  ← Full changelog
    └── ROADMAP.md                     ← Implementation plans for planned releases
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
| `revTTM` | number | Revenue growth TTM (%) |
| `epsTTM` | number | EPS growth TTM (%) |
| `grossMargin` | number | Gross margin TTM (%) — in the feed but not scored or displayed since v3.31.0 |
| `netMargin` | number | Net (profit) margin TTM (%) — in the feed but not scored or displayed since v3.31.0 |
| `peFwd` | number | Forward P/E (price ÷ current-FY EPS) |
| `epsFwd` | number | Forward EPS growth (%) — GAAP basis |
| `revFwd` | number | Forward revenue growth (%) |
| `pegFwd` | number | PEG ratio (Yahoo `pegRatio` field, long-term growth based) |
| `cur` | string | ISO currency code (e.g. `"USD"`, `"TWD"`, `"GBP"`); added v3.34.0, used only by the International universe to label $-formatted cells in the listing's own currency. Yahoo's London-listed quotes report in pence (`GBp`), not pounds, while that listing's `marketCap`/`cash`/`debt` are already in pounds — the pipeline normalizes `GBp`/`GBX` to `GBP` and divides `price`/`prevClose` by 100 before this field is ever written, so nothing downstream needs to know about the pence convention |
| `priceUpdated` | ISO 8601 string | Timestamp of price data |
| `fundamentalsUpdated` | ISO 8601 string | Timestamp of fundamentals data |

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

**etfs.json** follows the nasdaq100.json shape (array of `{"t", "n"}`) but holds exactly the 10 owner-picked funds and is never auto-synced.

**vug.json / vtv.json / vig.json** follow the nasdaq100.json shape (array of `{"t", "n"}`), hold exactly 100 entries (top holdings by weight after the dual-class dedupe), and are synced weekly from Vanguard's holdings API (Vanguard publishes fund holdings monthly, so constituent freshness lags the Wikipedia-sourced index lists by up to a month; acceptable because the fund's published holdings are the universe definition).

**screener_intl.json (International feed, v3.34.0)** is a plain single-list stock feed — identical schema to screener.json, `cur` field included — produced by the same `fetch_screener_data.py` fetcher and scored by the same six-metric client-side model. No separate scoring logic exists for this universe.

**vxus.json** follows the nasdaq100.json shape (array of `{"t", "n"}`) but `t` holds a **Yahoo symbol already resolved from the Vanguard holding's ISIN** (e.g. `"2330.TW"`, `"AI.PA"`), not the raw local-exchange ticker Vanguard returns. Synced weekly alongside VUG/VTV/VIG. Two per-run quirks the sync script handles that the domestic lists never hit: (1) Vanguard's API occasionally reports the same ISIN as two separate rows (observed for BHP Group and Barrick Gold) — these are summed by weight before ranking so "top 100" means 100 distinct issuers; (2) Vanguard's holdings API caps at exactly 500 returned entities for this fund (not the ~8,500 VXUS actually holds), so the raw-count sanity guard is a tight 480-520 band rather than the wide band used for the smaller funds.

**vxus_map.json** is the ISIN → Yahoo symbol resolution cache: `{"manual": {ISIN: symbol}, "resolved": {ISIN: symbol}}`. `manual` always wins and is how a bad auto-resolution gets corrected by hand (seeded at launch with the one holding that had a blank Vanguard ticker field and three dual-listing cases pinned to their primary exchange). `resolved` is the cache proper, populated by Yahoo's search endpoint (ISIN query first, company-name query as a fallback) and only queried for holdings not already in the cache, so a weekly sync's live-lookup cost is proportional to newly-added holdings, not the full 100.

### API Design (Internal Data Flow)

The site has no traditional API. The internal data flow for the screener is:

1. `screener.html` loads in the browser, defaulting to the Nasdaq 100 universe
2. On load it reads any cached copy of the active feed from `localStorage` and renders it immediately, then fetches the latest `screener.json` from GitHub — `raw.githubusercontent.com/.../data/screener.json` first (so it works even when the file is opened locally), falling back to the same-origin `data/screener.json`
3. On success the fresh feed replaces the data and is written back to the localStorage cache; if every source fails, the last cached copy is kept (or a "Couldn't load" message is shown)
4. **Universe buttons:** the app bar has one button per universe (Nasdaq 100, S&P 500, Growth, Value, Dividend, ETFs, International). Clicking one lazy-fetches that universe's feed the same way (separate localStorage cache key per universe) and swaps it into the table; loaded datasets are held in memory so switching back is instant. Growth/Value/Dividend share the combined `data/screener_gvd.json`, so the first fetch of any of the three fills all three stores. On-screen labels (`.universe-name` spans, page title) swap to match. If a feed hasn't been generated yet, the view stays where it was with an explanatory message
5. If the feed is more than a week old, an informational stale banner is shown (the daily refresh likely hasn't run) — a week rather than 24 hours, since the daily refresh slipping a day or two (a weekend, a rate-limited run) isn't worth alarming the user; only a genuinely stuck pipeline should surface it
6. `computeScoreMap()` ranks the loaded stocks and computes each one's relative percentile score and per-metric points client-side — so scores are relative to whichever universe is active
7. `render()` applies sort, filter, and column visibility to produce the table DOM; clicking a row opens a per-stock breakdown popup
8. No data is sent to any server; the only network requests are the read-only fetches of the public feeds

### Screener Scoring Model (v2, shipped v3.30.0; margins removed and re-weighted v3.31.0)

A relative, percentile-based model. Each stock is ranked against its loaded peers on six metrics in three weighted pillars totaling 100 points, with forward growth weighted double trailing growth (owner-set weights, 2026-07-03). (v2 replaced the five-metric v3.15 model, which had double-counted valuation, ignored the TTM metrics the site's doctrine teaches, and let a quarter of the list share perfect metric scores; that in turn had replaced the v3.12 absolute-threshold model. v3.30.0 briefly scored gross/net margin as a fourth Profitability pillar; the owner had not intended margins to be scored and they were removed the same day in v3.31.0, though the feed fields remain.)

| Pillar | Weight | Metric | Direction | Value ranked |
|--------|--------|--------|-----------|--------------|
| Growth | 10 | Revenue Growth TTM | higher is better | `revTTM` |
| Growth | 20 | Revenue Growth FWD | higher is better | `revFwd` |
| Growth | 10 | EPS Growth TTM | higher is better | `epsTTM` |
| Growth | 20 | EPS Growth FWD | higher is better | `epsFwd` |
| Valuation | 20 | PEG FWD | lower is better | `pegFwd` (Yahoo); when forward P/E ≤ 0, ranks worst and the column shows our own negative `peFwd / epsFwd` instead of Yahoo's misleading positive |
| Balance sheet | 20 | Cash vs Debt | higher is better | `cash / debt` (no debt ranks best) |

The P/E-vs-growth ratio (`peFwd / epsFwd`, negative-P/E and shrinking-earnings rank worst) is still computed and ranked, but only to color the P/E FWD column — it carries zero score weight, removing the old PEG double-count.

**Percentile → points:** `points = clamp(20 × (percentile − 0.22) / 0.56, 0, 20)`, then scaled by the metric's weight. Bottom 22% scores 0; top 22% scores full marks; the median scores half. Ties take the average rank. The 22% clamp was calibrated on the live feeds against the 6-metric weighted model (2026-07-03, v3.31.0) to the owner's target of ~1 perfect score in the Nasdaq 100 and ~5 in the S&P 500, ties allowed (live at ship: 2 tied at 100 in the Nasdaq 100, exactly 5 in the S&P 500). The clamp must be re-fitted whenever the metric set or weights change: the v3.30.0 8-metric model needed 28%, and an interim 15% fit against incomplete feeds proved far too tight (top scores stalled around 99 with no perfect scores).

**Score:** weighted sum out of a fixed 100. **Missing data is a hard zero** (owner decision 2026-07-03): a metric with no value contributes nothing and the denominator does not shrink, so incomplete data can never outrank complete data (pre-v2, missing metrics were dropped and the score rescaled, letting stocks scored on 3 of 5 metrics reach 100). A stock at the median on everything scores 50; a stock with no scored metrics at all shows NO DATA.

**Tiers (v3.29.0, rank-based):** the scored stocks are ranked by score and sliced into S (top 10% of the list), A (next 10%), B (20–50%), C (50–75%), F (bottom 25%). Boundary ties round up: every stock whose rounded score equals the last stock inside a band joins that band, so a tier stretches past its quota only on identical scores. Tier counts are therefore structurally fixed per universe (~10/10/30/25/25 in a 100-stock list, scaled to ~50/50/150/125/125 for the S&P 500). Above the bands sits **S+** (v3.30.0, owner request): any stock scoring a perfect 100/100 — those stocks come out of the S band's headcount, and the clamp calibration keeps them rare (~1 in the Nasdaq 100, ~5 in the S&P 500). The tier, not the raw score, drives the badge and score-bar colors (S+ purple `--color-tier-splus`, S dark green `--color-tier-s`, A light green, B yellow, C light red, F dark red). This replaced the v3.20.0 fixed score bands (Pass ≥ 80 / Watch 50–79 / Fail < 50); the S/A/B/C/F tier-list vocabulary was chosen over broker-style labels (Strong Buy…Strong Sell) to stay clear of advice language.

**Factors chip:** count of the six scored metrics earning 15+ of 20 percentile points (the upper part of the pack), out of a fixed /6; a missing metric counts as a miss.

**Relative-scoring caveats:** because grades are peer-relative, a stock's score can change when *other* companies' numbers change, and because tiers are ranks, a fixed share of every list always lands in C and F no matter how strong the list is (an F means "bottom quarter of this list", not "broken company"). Scores are computed over the currently loaded set (normally all 100 from the daily feed).

**Cell colors:** every colored cell follows the same percentile ranking, not absolute thresholds — green = top of the pack on that metric, red = bottom, amber = in between. A missing value in a scored metric renders dark red (it is a hard zero); only the unscored context column (P/E FWD) shows gray for missing. A negative forward P/E or PEG renders red and sorts as a worst (expensive) value, never a cheap one.

**Per-stock popup:** clicking any row opens a focused breakdown for that stock — all six scored metrics with value, percentile, and weighted points (e.g. "7.2/10"), color-coded, with the total score and tier. Missing metrics show 0 points in dark red. Reuses the modal component.

### ETF Universe Scoring Model (v3.33.0, shipped 2026-07-03)

A sixth universe, entirely separate from the five stock universes above: a **fixed, owner-picked list of 10 ETFs**, not an auto-synced index or fund-holdings list. Doctrine-consistent by design — the site's own rule is that individual stocks are judged on fundamentals while index/ETF purchases are timed on technicals, so this universe scores exactly the technical and cost signals the stock universes deliberately exclude.

**The 10 ETFs (fixed list, no auto-sync):** QQQ, SPY, DIA, IWM, VTI, VXUS, VUG, VIG, VTV, SPMO.

**Visible columns:** Price, Daily % Change, YTD Performance, 1 Year Total Return, 5 Year Total Return, 10 Year Total Return, Yield, Expense Ratio, Yield − Expense Ratio, RSI, 52-Week Range, Price vs 20-Day Moving Average, Price vs 100-Day Moving Average, Price vs 200-Day Moving Average, AUM (owner-added 2026-07-03; unscored display, `info["totalAssets"]`, verified for all 10 funds).

**Scoring criteria (100 of 100 points decided 2026-07-03):**

| Metric | Direction | Points |
|--------|-----------|--------|
| RSI | lowest is best | 20 |
| 52-Week Range (position within range) | lowest is best | 20 |
| 1 Year Total Return | highest is best | 10 |
| 5 Year Total Return | highest is best | 10 |
| 10 Year Total Return | highest is best | 10 |
| Yield | highest is best | 10 |
| Expense Ratio | lowest is best | 10 |
| Price vs 200-Day Moving Average (trend/momentum) | highest is best | 10 |

The 20-day and 100-day moving-average columns are **display/context only** (unscored), giving a fuller trend picture (short, medium, long) alongside the scored 200-day signal, the same "scored vs. context-only" pattern the stock universes use for P/E FWD.

**Data availability (verified live against yfinance 1.4.1, 2026-07-03, all 10 funds):** yield via `info["dividendYield"]` (do **not** use `trailingAnnualDividendYield` — missing or wrong for several funds, e.g. VUG); expense ratio via `info["netExpenseRatio"]` (present and correct for all 10); everything else (YTD/1Y/5Y/10Y total returns, RSI-14, 52-week range, 20/100/200-day MAs) computed from one 11-year daily history call. Convention: total returns use dividend-adjusted closes (`auto_adjust=True`), RSI/MAs/52W range use unadjusted prices (standard charting basis). SPMO (inception Oct 2015) is the youngest fund and just clears the 10-year return window; a missing return scores a hard zero, consistent with the stock model.

**Review concerns logged 2026-07-03 and owner resolutions (decided 2026-07-03 before implementation):**

1. **Yield is partially double-counted and carries a style bias** (total returns already include distributions, so scoring yield again favors income-style VIG/VTV over growth-style QQQ/VUG/SPMO). Alternatives offered: score Yield − Expense Ratio instead, or drop yield and raise Expense Ratio to 20. **Resolved: keep as specced** — the income tilt is an accepted, intentional preference.
2. **50 of the 100 points move together.** RSI, 52-Week Range position, and Price vs 200DMA are all "how far below recent prices" measures; in a broad selloff all three fire at once, so half the score is effectively one dip-depth factor and scores will swing hard day to day. **Accepted as designed** — it makes the score a strong timing dial, per the technicals-time-ETF-purchases doctrine.
3. **The S/A/B/C/F rank-band tier system fits a 10-fund list oddly** (S = 1 fund, A = 1, B = 3, C = 2-3, F = 2-3; an F badge lands on household index funds; S+ is nearly unreachable with 10 peers). Alternatives offered: score-only with no tier badges, or absolute score cuts. **Resolved: keep the rank bands** — an F means "bottom of this list right now," consistent with every other universe, and the caveat language already covers it.
4. **Relative percentiles are very coarse at N=10** (the 22% clamp was calibrated for 100+ stocks; reused unchanged, the top 2 funds per metric max out and the bottom 2 zero out). **Resolved: rank-based linear points for this universe** — on each metric the best fund earns full points and the worst earns 0, spaced evenly by rank (ties take the average rank), no clamp, no calibration to maintain.

**As built (shipped 2026-07-03):** static `data/etfs.json` list (hand-edited only, no auto-sync); `scripts/fetch_etf_data.py` (the field set shares nothing with the stock fetcher); `data/screener_etfs.json` feed in the standard `{updated, source, stocks}` envelope; `.github/workflows/screener-data-etfs.yml` Mon-Fri 23:15 UTC (between the Nasdaq 100 and S&P 500 runs, same `screener-data` concurrency group). Frontend: sixth universe button ("ETFs"); screener.js routes by a per-universe `kind` flag — the `<thead>` and Columns menu are config-driven and re-render when the universe kind changes (a refactor that also pre-pays for the International universe), sort and Columns events moved to delegation to survive the re-render, and the stock universes' scoring/markup are unchanged (verified by a headless regression run matching the v3.31.0 baseline exactly). ETF pillars as displayed: **Technicals 50** (RSI 20, 52W range 20, vs-200DMA 10), **Performance 30** (1/5/10y returns), **Income & cost 20** (yield 10, expense ratio 10); rank-linear points (best fund 20, worst 0, evenly spaced, ties averaged, missing = hard zero); Factors chip /8; the same rank-band tiers (on 10 funds: 1 S, 1 A, 3 B, 3 C, 2 F, verified live); cell colors green at 15+ rank points and red at 5 or less (the stock thresholds of exactly 20/0 would color only the single best/worst fund); per-fund popup breakdown; a dedicated ETF section in the methodology popup shown when the ETFs universe is active.

### State Management

Client-side state lives in two places:

1. **DOM:** Sort column, sort direction, active filter chip, column visibility, search query — all derived from UI interactions and re-applied on each render
2. **localStorage:** A cached copy of the public daily feed, used only as an offline fallback. No credentials are stored.

No cookies. No session storage. No server-side state.

### Third-Party Integrations

| Service | Purpose | Authentication | Data Sent |
|---------|---------|---------------|-----------|
| Yahoo Finance (via yfinance) | Daily data pipeline (server-side, in GitHub Actions) | None (public) | Ticker symbols in HTTP requests |
| Vanguard holdings API | Weekly ETF constituent sync for the Growth/Value/Dividend lists (server-side, in GitHub Actions) | None (public) | Fund tickers (VUG, VTV, VIG) in HTTP requests |
| GitHub (raw + Pages) | Static hosting and the screener's data feed | None for reads | None (read-only fetch of a public JSON file) |
| GitHub Actions | CI/CD scheduling | GitHub account (owner only) | None from users |

### Performance Requirements

| Metric | Target |
|--------|--------|
| Largest Contentful Paint (LCP) | Under 1.5s on 3G |
| Time to Interactive (TTI) | Under 2s on 3G |
| JavaScript | `script.js` ~49 lines (content pages); `screener.js` ~900 lines (loaded only on the screener page) |
| CSS total | Under 50KB (style.css: ~850 lines) |
| screener.json size | Under 100KB for 100 tickers |
| Font requests | 0 (system fonts only) |

### Known Technical Debt

| Debt | Description | Correct Solution |
|------|-------------|-----------------|
| Constituent name quality | New tickers added by the auto-sync use cleaned Wikipedia names, which may be slightly longer than the curated short names | Hand-edit `data/nasdaq100.json` names after a sync if desired (existing names are preserved automatically) |

Not debt (reclassified v3.32.0): the generated data feeds (`screener.json`, `screener_sp500.json`, `screener_gvd.json`, `screener_etfs.json`, `screener_intl.json`) are committed to the repo **intentionally**. Their git history is the site's only record of past scores and is the data source for the planned v4.1.0 score-history sparklines. Do not move them to GitHub Releases or external artifact storage; the growing history is the feature.

---

## Security

### Authentication Model

None. The site is fully public. There are no user accounts, no sessions, no login flows, and no credentials of any kind. The screener only performs a read-only fetch of a public JSON feed.

### Authorization Model

No role-based access. All content is publicly readable. The only write access is the GitHub Actions workflow committing `screener.json`, which is governed by GitHub's repository permissions (owner-only push to main).

### Data Storage

The site stores no user data. The only browser storage is:

- **localStorage:** a cached copy of the public daily feed (offline fallback only). No credentials, no PII.
- **No cookies.**
- **No analytics that collect PII** (if analytics are added, use a privacy-preserving tool like Plausible).

### Environment Variables

No secrets are used or hardcoded. The legacy `FMP_API_KEY` GitHub Actions secret from the pre-v3.16.0 FMP era was deleted from the repository settings on 2026-07-03 (v3.32.0); no workflow had referenced it since v3.16.0.

### Third-Party Trust

| Service | Data Received | Notes |
|---------|--------------|-------|
| Yahoo Finance | Ticker symbols (server-side, in the pipeline) | Public endpoints, no user PII |
| GitHub (raw + Pages) | Read-only file fetches | Serves static files / the public JSON feed |
| GitHub Actions | None from end users | Repository automation only |

### Known Attack Surface

| Area | Risk | Mitigation |
|------|------|------------|
| screener.json injection | Malicious content in the data file could be rendered as HTML | The data file is owner-controlled (only the GitHub Action writes it). Cell values come from number formatting; ticker/name come from the static constituent list. No user-supplied HTML is rendered. |
| Dependency supply chain | yfinance is a third-party library | yfinance is pinned (==1.4.1) in all Actions workflows; monitor for new releases and bump deliberately. |
| GitHub Pages serving | Cached stale content | GitHub Pages cache is controlled by GitHub; not a controllable risk at this layer. |

### Dependency Policy

- Frontend: zero dependencies. No monitoring required.
- Backend: one data dependency (yfinance, pinned to 1.4.1 in every workflow as of v3.28.0; bump the pin deliberately after testing, never float `latest`), plus requests/pandas/lxml in the weekly constituent sync only. Monitor the yfinance GitHub repository for security advisories.

---

## Press Release

**FOR IMMEDIATE RELEASE**

### Free Tool Lets Everyday Investors Apply a Proven Fundamentals Framework to the Entire Nasdaq 100

**New site from independent investor Azqato gives retail investors a complete methodology, interactive screener, and step-by-step guides — all without paying for a subscription or selling their data**

*Seattle, WA — June 2026* — Azqato, an independent long-term investor and content creator, today launched a comprehensive public resource at `azqato.github.io/stocks` documenting the complete individual stock picking methodology he has refined over years of active investing. The site combines in-depth educational content, practical tool setup guides, and a live interactive screener that evaluates every Nasdaq 100 company against a three-pillar scoring model, updated daily.

The site addresses a real gap in publicly available investing education. While financial media is abundant, structured, non-commercial investing frameworks are rare. Most free resources either oversimplify or exist to sell something. Azqato's site does neither: it documents a real methodology built from practice, presented with the same directness he brings to his Twitch streams and YouTube videos.

The site covers twelve evaluation metrics (revenue growth, EPS growth, P/E, PEG, cash, debt, RSI, 52-week range, gross margin, and net margin), a nine-section philosophy page on long-term conviction investing, thirty-four Q&A items in an interactive accordion, and setup guides for both Finviz and Seeking Alpha. For index investors, a separate methodology covers VIX action levels, AAII sentiment signals, dollar-cost averaging, and lump-sum deployment strategy. The interactive Nasdaq 100 screener scores all 100 constituents daily using a transparent algorithm and shows each stock's S-to-F tier at a glance.

"I kept explaining the same framework to the same questions over and over in streams and Discord," said Azqato. "Building this site meant I could say: here, read this. It is everything I know about how to evaluate a stock, written down in one place, for free."

The site is available now at `azqato.github.io/stocks`. No account required. No email address. No subscription.

**About Azqato**
Azqato is an independent investor and content creator focused on long-term, fundamentals-driven equity investing. He publishes investing methodology content on Twitch, YouTube, and Discord (B5TA community), and maintains a suite of free public tools and sites at `azqato.github.io`.

---

## Frequently Asked Questions

### External FAQ (User-Facing)

**1. What is this site?**
A free educational resource documenting Azqato's individual stock picking methodology. It explains which metrics to evaluate, how to read them, how to find candidates using Finviz, how to track them in Seeking Alpha, and how to think about index/ETF investing alongside individual stocks.

**2. Who is this for?**
Beginner to intermediate retail investors who want a structured, non-commercial framework for long-term equity investing. Especially useful for people who follow Azqato on Twitch, YouTube, or Discord (B5TA community).

**3. Is this financial advice?**
No. This site documents one investor's personal methodology. Nothing here is a recommendation to buy or sell any specific security. Every page includes an "Educational use only. Not financial advice." disclaimer.

**4. How do I use the site?**
Start at the Home page to see the strategy overview and the metric grid. Read Philosophy if you want to understand the mindset behind the rules. Use Metrics as a reference when evaluating a specific signal. Use Finviz and Seeking Alpha pages to set up your research tools. Use the Screener to see how all 100 Nasdaq companies score against the methodology today. Use FAQ when you have questions about the strategy.

**5. What are the 12 metrics?**
Revenue Growth TTM, Revenue Growth FWD, EPS Growth TTM, EPS Growth FWD, P/E FWD, PEG FWD, Total Cash, Total Debt, RSI, 52-Week Range, Gross Margin, and Net Margin. The ten growth, valuation, profitability, and balance sheet metrics drive individual stock decisions (the screener scores six of them across three weighted pillars). RSI and the 52-Week Range are technical signals used to time index and ETF purchases, tracked on stock watchlists for context only.

**6. What is the Nasdaq 100 screener?**
An interactive tool that applies the methodology's three-pillar scoring model to all 100 Nasdaq 100 companies. Data is updated daily from Yahoo Finance. Each company receives a score from 0 to 100 and a rank-based tier from S (top 10% of the list) to F (bottom 25%), with a rare S+ tier reserved for perfect 100 scores. This is a screening and educational tool, not a buy/sell signal generator.

**7. How does the screener score stocks?**
Each stock is ranked against the rest of the loaded universe on six metrics in three weighted pillars: Growth 60 (revenue and EPS growth, trailing and forward, with forward growth weighted double), Valuation 20 (PEG FWD), and Balance sheet 20 (cash vs debt). Points follow percentile rank (bottom 22% scores 0, the median half marks, the top 22% full marks), missing data scores zero, and the pillars sum to 0–100. The score's rank within the list maps to a tier: S is the top 10% of the list, A the next 10%, B 20–50%, C 50–75%, F the bottom 25% (boundary ties round up), and a perfect 100 earns S+. It is a relative ranking, so a high tier means a stock looks better than most of the list right now rather than that it cleared a fixed target. The Methodology button on the screener explains it with a worked example.

**8. How often is the screener data updated?**
On trading days (Monday through Friday), starting at 21:30 UTC via an automated pipeline (30 minutes after the latest possible US market close in UTC terms, so there's always at least a 30-minute buffer after close). Weekends are skipped because the US market is closed. The "as of" timestamp in the screener header shows when the data was last refreshed.

**9. Where does the screener data come from?**
Yahoo Finance, fetched on trading days by a Python script (using the free yfinance library) that runs in GitHub Actions and commits the result. No API key is required, and there is nothing to configure — the page just reads the published feed from GitHub.

**10. Does the screener use real-time data?**
No. It uses data from the most recent pipeline run (refreshed once per trading day, starting at 21:30 UTC). Prices shown reflect the close or after-hours price at the time of the last fetch.

**11. What is the Palantir story?**
A first-person account where Azqato bought Palantir at $9, sold at $45, and watched it go to $150. It is the single most important lesson documented on the site: selling a business because the price went up is a category mistake. Price and value are not the same thing. It lives on the FAQ page.

**12. Do I need to pay for anything?**
No. The site is entirely free with nothing to configure. Finviz's screener is free (no account needed). Seeking Alpha has a free account tier that covers the 12-column watchlist setup described. The screener's daily data feed is free and requires no API key.

**13. Do you cover short selling, options, or crypto?**
No. This methodology covers long-only equity investing with a buy-and-hold time horizon. Derivatives and crypto are outside scope.

**14. What is the recommended portfolio size?**
10–20 stocks. Fewer than 10 concentrates risk; more than 20 dilutes conviction. Every position should be high-conviction within that range.

**15. When should I sell a stock?**
The short answer: rarely. The methodology's default posture is to hold quality positions through volatility. Selling is appropriate when the fundamental thesis has changed (not just because the price moved), or when the balance sheet or margins have deteriorated materially over multiple quarters.

**16. How do I find stocks to evaluate?**
Use the Finviz guide to set up a screener that filters for candidates meeting the methodology's basic thresholds. Then move candidates to a Seeking Alpha watchlist (12-column setup guide on the site) to track them over time.

**17. Is Dollar-Cost Averaging or lump-sum investing better?**
For regular income-stream investing (each paycheck), DCA-style contributions are the right default. For a one-time pool of money, lump-sum investing beats DCA on average in about 2/3 of historical 12-month windows, rising to roughly 90% at 36 months. The Indices page covers both approaches in detail.

**18. What does the VIX have to do with investing?**
VIX is a fear gauge: it measures implied volatility in S&P 500 options. When VIX is elevated (25+), fear is high, and broad market prices are typically lower. This makes it a useful contrarian indicator for timing index and ETF purchases. The Indices page covers VIX action levels (5 bands from below 15 to above 45).

**19. What is AAII sentiment?**
The AAII Investor Sentiment Survey is a weekly poll of retail investor outlook (bullish, neutral, or bearish). Published Thursdays since 1987. It is used as a contrarian indicator: when more than 60% of respondents are bearish, that historically marks or precedes major market bottoms. The Indices page has the full framework.

**20. Why does holding for more than 12 months matter?**
Tax treatment. In the US, positions held more than 12 months qualify for long-term capital gains tax rates (15–20%) rather than short-term rates (22–37% ordinary income). The hidden cost of impatience includes paying the higher rate on every gain realized too early.

**21. How is this different from just buying an S&P 500 index fund?**
An index fund is a valid and often superior choice for most investors. This methodology adds a layer: identifying individual companies with above-average growth trajectories at reasonable valuations, which may outperform a broad index over long periods if the fundamentals thesis is correct. Both approaches have a place: the Indices page covers ETF investing as a distinct and complementary strategy.

**22. Is the site code open source?**
Yes. The repository is public on GitHub. The code is simple enough to read directly: one CSS file, one JS file, one Python script.

**23. What sites does Azqato also run?**
The portfolio site at `azqato.github.io`, ComposerAtlas (a strategy research tool), and a Leveraged Strategies site. The stock methodology site links to Leveraged Strategies in the sidebar nav.

**24. What if I disagree with the methodology?**
The methodology is opinionated by design. It says to buy quality and hold it, to ignore short-term price movements, and to treat selling winners as almost always wrong. These are real positions that real investors disagree with. If you have a different framework, this site may still be useful as a reference for how to evaluate specific metrics, even if the overall philosophy does not match yours.

**25. How do I get help or report an issue?**
Reach out in Azqato's Discord (B5TA community) or open a GitHub issue on the repository.

---

### Internal Stakeholder FAQ

**What is the return on investment for maintaining this site?**
The site serves two functions: it converts interested viewers into engaged community members who understand the methodology deeply, and it serves as a reference that reduces repetitive explanation in streams and Discord. Both contribute to the quality of the community around Azqato's content.

**What are the success metrics?**
Return visitor rate (25%+ within 30 days) and average session duration (4+ minutes). These indicate that readers are finding the content trustworthy and useful enough to consult repeatedly. See the Metrics section above for the full table.

**What is the roadmap direction?**
Deepen existing content before adding new content. The philosophy and metrics pages are more valuable when they are exceptionally thorough than when new pages are added at average quality. The next meaningful additions are a mobile navigation improvement and a conference call research guide.

**How do we ensure the methodology stays accurate over time?**
The site is deliberately designed to avoid time-sensitive claims. All editorial content uses hypothetical examples, conceptual frameworks, and calibrated thresholds rather than current prices or live company data. Threshold updates (e.g., "strong gross margin is 50%+") require review when market structures change, but this is infrequent.

**How is the screener data quality monitored?**
The "as of" timestamp in the screener header shows the last refresh time. If the daily pipeline fails, GitHub sends an email notification to the repository owner. The pipeline is designed to retry failed symbol fetches automatically and commit whatever data was successfully retrieved.

**What is the documentation strategy going forward?**
Five files: README.md (developer front door), PRD.md (this file, the comprehensive reference), DESIGN.md (design system), PATCHNOTES.md (full changelog), ROADMAP.md (implementation plans for planned releases; plans are trimmed to pointers once shipped). All major changes are documented in PATCHNOTES.md. PRD.md is updated when product requirements, architecture, or process changes significantly. Documentation changes are included in version increments.

---

## Site Structure Reference

### Navigation Order (11 items)

Home → Philosophy → Metrics → Screener → Market Overview → Finviz → SeekingAlpha → Indices → FAQ → Leveraged Strategies → Support

**Nav label rule:** Every sidebar nav label is a single token (no spaces) except "Market Overview" and the two trailing external links. Labels: Home, Philosophy, Metrics, Screener, Market Overview, Finviz, SeekingAlpha, Indices, FAQ, Leveraged Strategies, Support.

### Pages and Their Section IDs

| Page | Section IDs ("On This Page") |
|------|------------------------------|
| `index.html` | `#section-strategy`, `#section-metrics-grid`, `#section-reference`, `#section-portfolio` |
| `philosophy.html` | `#section-possible`, `#section-ownership`, `#section-research`, `#section-gvd`, `#section-offense`, `#section-protect`, `#section-trader`, `#section-wall-street`, `#section-hype`, `#section-leadership`, `#section-knowledge`, `#section-ipo` |
| `metrics.html` | `#metric-rev-ttm`, `#metric-rev-fwd`, `#metric-eps-ttm`, `#metric-eps-fwd`, `#metric-pe-fwd`, `#metric-peg-fwd`, `#metric-cash`, `#metric-debt`, `#metric-rsi`, `#metric-52w`, `#metric-gross-margin`, `#metric-net-margin` |
| `finviz.html` | `#section-purpose`, `#section-step1`, `#section-step2`, `#section-step3`, `#section-coverage`, `#section-quickref` |
| `seekingalpha.html` | `#section-account`, `#section-portfolio-create`, `#section-tickers`, `#section-columns`, `#section-sort`, `#section-done` |
| `indices.html` | `#section-types`, `#section-dca`, `#section-lumpsum`, `#section-framework`, `#section-vix`, `#section-timing`, `#section-aaii`, `#section-quality`, `#section-signals`, `#section-sa-setup` |
| `faq.html` | No "On This Page" block (accordion pattern) |
| `screener.html` | No "On This Page" block (app page, no long-form sections) |
| `market.html` | No "On This Page" block (card grid, no long-form sections) |

### Content Philosophy (Enforced Rules)

- No real-time data in editorial content
- RSI and the 52-week range are index/ETF timing signals only. Editorial content must never present technicals as individual-stock buy or sell criteria; stocks are valued on fundamentals and valuation, with technicals at most providing context
- All illustrative examples use hypothetical labels ("High-growth tech co.", "Accelerating")
- No company-specific live examples (the Palantir story is the one named historical exception)
- No em dashes in any form: ` -- `, `—`, or `&mdash;`
- No "- Azqato" suffix on `<title>` or `og:title`
- No financial advice language
- "Educational use only. Not financial advice." in every page's sidebar footer

### Key Concepts Documented (Video Transcript Analysis)

The following concepts were integrated from video transcript analyses. This table preserves the full concept inventory.

| Concept | Site Location |
|---------|--------------|
| Long-term thinking / compounding mindset | philosophy.html (Section 0, Stay on Offense), index.html |
| Belief that significant wealth-building is possible | philosophy.html (Section 0) |
| Plan-to-100 time horizon / underestimating multi-decade compounding | philosophy.html (Section 0) |
| Short-termism / dopamine-culture trap | philosophy.html (Section 0) |
| Stay on offense: regular investing discipline | philosophy.html (Section 4) |
| SWOT analysis framework | philosophy.html (Section 2) |
| Sequential evaluation: business first, then financials, then valuation | philosophy.html (Section 2) |
| Revenue growth as primary screener | metrics.html (Revenue TTM + FWD) |
| Revenue deceleration warning signal (quarterly trend) | metrics.html (Revenue TTM) |
| Peak hype avoidance | philosophy.html (Section 5.5), faq.html |
| Weak-hands cascade mechanics | philosophy.html (Section 5.5), faq.html |
| Buy cadence: at least twice a month | philosophy.html (Section 4) |
| Grow income over cutting expenses | philosophy.html (Section 4) |
| Balance sheet strength (cash > debt) | metrics.html (Cash, Debt), philosophy.html (Section 2) |
| Balance sheet advantage in rate-hiking cycles | metrics.html (Total Cash) |
| Gross margin trends and thresholds | metrics.html (Gross Margin), index.html reference table |
| Net margin trends and thresholds | metrics.html (Net Margin), index.html reference table |
| Margins as competitive-position signal | philosophy.html (Section 7) |
| Wall Street prices margin trends | philosophy.html (Section 7) |
| Market cap vs potential mental model | index.html |
| Short-term vs long-term price drivers | philosophy.html (Section 1) |
| Opportunities outside tech | philosophy.html (Section 7) |
| Double/lose-50% decision framework | philosophy.html (Section 2) |
| Diversification: 10–20 stocks | index.html, faq.html |
| GVD framework: growth/value/dividend stocks | philosophy.html (Section 3) |
| Risk-on vs risk-off market environments | philosophy.html (Section 3), faq.html |
| Stocks as ownership (farmland analogy) | philosophy.html (Section 1) |
| Wall Street incentive misalignment | philosophy.html (Section 5) |
| Revenue and net income up and to the right TTM | metrics.html, philosophy.html |
| Dividends as crash-deployment capital | philosophy.html (Section 3) |
| Always research why margins move | metrics.html (Net Margin), philosophy.html (Section 7) |
| Competitive complacency / market leadership cycles | philosophy.html (Section 6) |
| Unprofitable stocks: position sizing rules | faq.html |
| Study business models for pattern recognition | philosophy.html (Section 7) |
| Conference call discipline | philosophy.html (Section 7) |
| Dollar-cost averaging as the default | indices.html (DCA section), faq.html |
| Lump-sum superiority on average; dry-powder trap; hybrid | indices.html (Lump-Sum), faq.html |
| Broad-market vehicles: VT, VTI + VXUS | indices.html (DCA section) |

---

## Documentation Process

### How This File Is Maintained

This PRD is the comprehensive reference for the project. It should be updated whenever:
- A new feature ships that changes the product requirements, architecture, or user stories
- A new page or major section is added to the site
- The scoring model or methodology thresholds change materially
- The data pipeline changes in a way that affects data model fields or quality
- The roadmap or metrics targets change

Updates to this file are versioned in PATCHNOTES.md like any other change.

### How PATCHNOTES.md Is Maintained

Every code change, content change, or documentation change gets a new entry. Format:

```
## v<MAJOR>.<MINOR>.<PATCH> — YYYY-MM-DD — Title

Brief summary sentence.

### Added
- What was added

### Changed
- What was changed

### Fixed
- What was fixed

### Removed
- What was removed
```

Version bumps follow semantic versioning:
- MAJOR: breaking changes, complete redesigns, migration events
- MINOR: new features, new pages, new sections
- PATCH: bug fixes, copy corrections, small improvements

### What NEVER Goes in Memory or Documentation as a Standalone File

- Ephemeral task lists or in-progress work
- PR descriptions (these belong in the commit and PR)
- Debugging sessions (the fix is in the code; the commit message has the context)
- Time-sensitive market commentary
- Specific current stock data or prices
