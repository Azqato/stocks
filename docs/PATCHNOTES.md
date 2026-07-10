# PATCHNOTES.md — Azqato Stock Methodology Site

---

## v4.1.0 — 2026-07-10 — Market Overview page shipped

**New standalone page: a price/change snapshot for 10 major market benchmarks, in the style of a CNBC market-strip, refreshed three times per trading day. Owner-requested; scoped and prioritized ahead of the sparklines release via AskUserQuestion; cadence changed from once-daily to intraday mid-build per direct owner instruction.**

### Added

- **`market.html`**: new page, self-contained (its own inline `<style>`/`<script>`, no shared JS file) following the existing guide-page sidebar/nav pattern. Card grid shows DIA, SPY, QQQ, IWM, VTI, VXUS, VUG, VTV, VIG, and VIX in that fixed order, each card showing name, ticker, last price, change, and %change, colored green/red by direction via the site's existing `--color-positive`/`--color-negative` tokens (a top accent border + colored change text, not a solid CNBC-style fill, to stay consistent with the site's existing dark theme). Explicitly **not** the screener: no scoring, no tiers, no ranking, just a snapshot. A stale-data banner and an "as of" timestamp reuse the screener's established pattern, with the threshold recalibrated to 4 days (down from the screener's 7) to match this page's faster refresh cadence while still tolerating a holiday weekend.
- **`scripts/fetch_market_overview.py`**: new lightweight fetch script, deliberately separate from `fetch_etf_data.py`/`data/screener_etfs.json` (the scored ETFs universe) since this only needs price and previous close, not returns history, RSI, or technicals. Reads the fixed list from `data/market_overview_list.json` (owner-curated, hand-edited only, no auto-sync — same convention as `data/etfs.json`). VIX is fetched via its Yahoo index symbol `^VIX` (the list's `y` column) but displayed under the ticker `VIX` (the list's `t` column); no other special-casing was needed since the script only reads price fields.
- **`data/market_overview.json`**: new generated feed, `{"updated", "source", "quotes": {TICKER: {"name","price","prevClose","change","changePct"}}}`.
- **`.github/workflows/market-overview.yml`**: new workflow, three runs per trading day (15:00, 19:00, 22:00 UTC — shortly after the open, midday, shortly after the close), the only workflow in the pipeline that isn't once-daily-after-close. Shares the `screener-data` concurrency group with the other five data workflows; the 22:00 run lands the same minute as the ETFs feed job, so the two queue rather than race.
- **Navigation**: new "Market Overview" nav item added to all 9 pages (between Screener and Finviz), `sitemap.xml` entry added.

### Verified

- Headless Chrome: all 10 cards render with correct data and correct green/red coloring (verified against a live run where VIX was down and every ETF was up, exercising both color paths); responsive sweep 375-1920px shows zero horizontal overflow (`scrollWidth === clientWidth` at every width, plus a 700px screenshot confirming the 2-column mobile card layout and hamburger nav both work).
- `fetch_market_overview.py` run against live data: 10/10 symbols fetched successfully including `^VIX`.
- Screener regression: `screener.html`'s nav-link addition confirmed non-breaking via headless dump (tier counts intact modulo normal weekly constituent drift, unrelated to this change).

---

## v4.1.3 — 2026-07-09 — Docs backfill: sidebar rebrand entry (belated)

**Backfilling a PATCHNOTES entry for the sidebar rebrand shipped earlier the same day (commit `b856324`), which landed without one.**

### Changed

- **Sidebar branding**: `.sidebar-brand a` renamed to "Azqato Invests" with a new sub-label "Individual Stocks" beneath it (`.sidebar-brand-sub`, muted small text). Brand text size increased 0.9rem → 1.125rem with tightened letter-spacing (-0.3px) to read as a wordmark rather than a nav link. Applied identically across all 8 content pages plus `screener.html`; shared styling lives in `style.css`.

---

## v4.1.2 — 2026-07-09 — MAG 10 button styling unified with universe buttons

**Owner reported the MAG 10 button "looks weird when I click on it" and asked for its CSS to match the other buttons.**

### Fixed

- **MAG 10 button no longer styled as a segmented-control segment**: `#mag10Btn` carried `border-radius: 0 7px 7px 0` (square left corners), `border-left`, and `padding-left: 12px` — a divider treatment meant to read as "filter, not an eighth universe" (see v4.0.1). But `.universe-group` uses `gap: 6px; flex-wrap: wrap`, so the button never sits flush against the universe buttons; it floats with a 6px gap, leaving two square left corners that looked broken once the accent border lit up on click. Removed all three overrides. MAG 10 is now a plain `.btn` (no `.u-btn`) that renders identically to the universe buttons in both resting and active states; its `.active` rule still mirrors `.u-btn.active`. **This reverses the "keep the squared-off left corner" decision from v4.0.1** — with the flex gap in place, the segmented look never worked, and consistency wins over the filter/universe visual distinction (the button's label, tooltip, and position already convey that).

### Verified

- `#mag10Btn` block in `screener.html` now contains only the `.active` rule; the JS toggle (`toggleMag10`/`updateMag10Button` in `screener.js`) was already correct and is unchanged.

---

## v4.1.1 — 2026-07-08 — Investor-vs-trader discipline & IPO-timing content (video-sourced)

**Owner asked for a video transcript to be reviewed for durable, non-dated concepts and folded into the site in the existing methodology's tone. Two new philosophy sections and two new FAQ items shipped; ticker-specific and time-bound commentary from the source video was left out by design.**

### Added

- **`philosophy.html#section-trader` — "Investor, Not Trader"**: generalizes the transcript's warning that unusually volatile stretches (a stock swinging hard on a single analyst note or sector-wide selling) pull investors into trading behavior — buying because a stock just ran, selling because it just dropped, or chasing a loss with a bigger, faster trade (the same mechanism behind compulsive gambling). The stated antidote: re-run your own revenue/EPS growth and valuation expectations and let that decide, not the last week's chart; a large unrealized gain does not change the test in either direction. Linked from `faq.html#answer-trader`.
- **`philosophy.html#section-ipo` — "Why We Wait on IPOs"**: new ground for the site. Explains that IPO timing is chosen by the seller (the company and its lock-up-bound early shareholders) to maximize proceeds, not to offer a fair price to a new buyer, so offerings cluster in euphoric, richly-priced windows. Uses two closed historical illustrations rather than live data: the 2021 SPAC/IPO boom (most of that cohort fell sharply within about a year and never recovered) and Meta's own 2012 IPO ($38 to sub-$18 within the same calendar year, in a bull market, before going on to become one of the most valuable companies in the world) as proof that even excellent businesses aren't exempt from the pattern. Ties the "no-touch" rule to requirements this methodology already has — conference call history, multi-quarter financials — rather than inventing a new one. Linked from `faq.html#answer-ipo`.
- **`faq.html`**: two new accordion items + matching FAQPage JSON-LD entries (`answer-trader`, `answer-ipo`); item count 34→36, corrected in the page's meta description, README.md, and PRD.md.

### Not carried over (by design)

- Single-stock price targets, capex commentary, and one creator's current portfolio positions from the source video — all dated, ticker-specific, and opinion-based, which conflicts with this site's non-goals ("not a buy/sell signal generator," "no financial advice," "no real-time data in editorial content") and the permanence-over-freshness tenet.

### Verified

- FAQ accordion item count and JSON-LD `Question` entry count both recount to 36 (`grep -c` on `faq.html`); philosophy section count recounts to 12. README.md and PRD.md counts corrected to match (PRD's stale "9 sections" / 10-actual label is also fixed as part of this pass).

---

## v4.0.1 — 2026-07-04 — MAG 10 button spacing fix

**Owner reported the MAG 10 button "appears different than the others" in the screener's app-bar. Diagnosed via `getBoundingClientRect()` comparison across all universe buttons.**

### Fixed

- **MAG 10 button gap doubled**: `#mag10Btn`'s `margin-left: 6px` (added in v3.37.1, when the button moved into the app-bar) stacked on top of `.universe-group`'s own `gap: 6px`, giving MAG 10 a 12px gap before it instead of the uniform 6px between every other button. Removed the redundant `margin-left`; the left-border divider and squared-off left corner (intentional, so it still reads as a filter rather than an eighth universe) are unaffected.

### Verified

- Headless Chrome: measured left/right edges of all 8 app-bar buttons before and after — gap between every consecutive pair (including International → MAG 10) is now a uniform 6.0px.

---

## v4.0.0 — 2026-07-04 — Screener responsive redesign, methodology table fix & mobile-friendliness pass

**A dedicated pass so the screener never requires horizontal scrolling, from full desktop down to phone width, plus a methodology-modal display bug fix, a content-drift audit, and the `indices.html` write-up for Price vs 200-Day Moving Average that v3.37.0's ETF rating review had left open. Absorbs the retired v3.35.0.**

### Fixed

- **Methodology modal table overflow**: `style.css`'s `.table-wrap` rule set `overflow-x: auto` and then, three lines later, the shorthand `overflow: hidden` — which resets both axes and silently cancelled the horizontal scrollbar on every wide methodology table sitewide. Changed the trailing declaration to the longhand `overflow-y: hidden`, preserving the rounded-corner clipping without cancelling `overflow-x`.
- **Universe-button row overflowing the page at phone widths**: a second instance of the implicit-`min-width:auto` grid bug from v3.34.8, this time hitting the *mobile* breakpoint. `style.css`'s `max-width: 1023px` media query reset `.site-layout`'s grid track to a bare `1fr` (the single-column mobile layout), dropping the `minmax(0, 1fr)` fix that only covered the desktop two-column rule — so the overflowing 7-button-plus-MAG-10 row forced the whole page wider than the viewport instead of wrapping. Fixed by applying `minmax(0, 1fr)` to the mobile override too.

### Added

- **Live-responsive auto-hide columns**: the screener table now hides column groups automatically as the window narrows, recomputing on every resize (not just once on load), so Ticker/Tier/Score/Factors are always reachable without horizontal scroll at any width. Stock kind hides Snapshot → Balance → Valuation → Growth as it narrows; ETF kind hides Income & Cost → Snapshot → Performance → Technicals. Built on the existing Columns-menu checkboxes/`applyColumnVisibility()` rather than a new component; manual picks still work and are only overridden when a resize crosses a breakpoint.
- **`indices.html`: Price vs 200-Day Moving Average** subsection added to the Timing Signals section, alongside RSI and 52-Week Range — the write-up v3.37.0's ETF methodology review had flagged as open. Framed as a trend-health confirmation signal (price above the 200-day MA confirms an intact uptrend; below it is the classic long-term downtrend warning), explicitly distinct from RSI/52-week range's contrarian dip-buying framing. The page's doctrine counts (metrics and timing-signal totals) were updated from nine/four to ten/five everywhere they're stated, including the quick-reference table.

### Verified

- Content audit: `#methodStock`/`#methodEtf` already correctly reflected the current scoring code (no drift found after five same-day scoring edits — the audit itself is the deliverable).
- Headless Chrome sweep (375, 700, 900, 1023, 1150, 1440, 1920px): zero page-level horizontal overflow (`scrollWidth === clientWidth`) at every width, for the screener (both stock and ETF kind) and all 8 other content pages; column-hide order matches spec at every breakpoint crossing; universe-button row wraps cleanly at narrow widths.
- Nasdaq 100 regression: exact match to the v3.31.0 baseline (2 S+ / 10 S / 8 A / 32 B / 24 C / 24 F, MU and NVDA at 100) at every width tested — this pass is render-only, no scoring code touched.

---

## v3.37.2 — 2026-07-04 — Screener: stale-data banner threshold raised from 24 hours to a week

**Owner feedback: the "this data is more than 24 hours old" banner fired too eagerly — a daily refresh slipping a day (a weekend, a rate-limited run) isn't worth alarming a user over. Raised the threshold to a week, which only surfaces the banner for a genuinely stuck pipeline.**

### Changed

- `isStale()` in `screener.js`: threshold changed from `24 * 3600 * 1000` to `7 * 24 * 3600 * 1000` milliseconds.
- Banner copy updated to match: "This data is from [timestamp] (more than a week old). The daily refresh may not have run." Static HTML fallback text and PRD's runbook/API-design mentions of the 24-hour threshold updated for consistency.

### Verified

- Headless Chrome against the live feed (updated 2026-07-03, so >24h but <7 days old at test time): banner's `on` class is correctly absent — hidden under the new threshold, where it would have shown under the old one.

---

## v3.37.1 — 2026-07-04 — Screener: "MAG 10" button moved to the top app-bar

**Owner request: move the "MAG 10" filter toggle (v3.36.0) from the tier-chip toolbar row to the top app-bar, next to the universe buttons, to the right of International.**

### Changed

- `#mag10Btn` moved into `#universeGroup`, inheriting the row's `flex-wrap` spacing. A left border and margin visually separate it from the universe buttons, since it's a filter toggle, not an eighth universe to switch to. No JS changes needed — the button's click binding is by ID, unaffected by its position in the DOM.

### Verified

- Headless Chrome screenshot: button renders correctly to the right of International, active-state highlight works, universe-switch-to-S&P-500 and the 10-ticker filter still function correctly after the move.
- Nasdaq 100 regression: exact match to the v3.31.0 baseline.

---

## v3.37.0 — 2026-07-04 — Screener: ETF scoring model reweighted (Yield/Expense Ratio removed)

**Owner-requested change to the ETFs universe scoring model (v3.33.0). Yield and Expense Ratio are no longer scored; the freed 20 points went to weighting up the 5-year and 10-year return horizons instead of the recommended alternative (promoting YTD), which the owner declined.**

### Changed

- **`ETF_METRICS`**: Yield and Expense Ratio weights changed from 10 to 0 (demoted to context-only, same treatment as YTD/net yield/20-100-day MAs — still displayed and colored, just not scored). 5-Year Total Return and 10-Year Total Return weights changed from 10 to 20 each; 1-Year Total Return unchanged at 10. Final model: **Technicals 50 (unchanged) + Performance 50 (1Y 10, 5Y 20, 10Y 20) = 100**.
- **`ETF_POPUP_METRICS`**: Yield and Expense Ratio entries removed from the per-fund popup breakdown (matching how the stock model already excludes its own weight-0 metrics from `POPUP_METRICS`); 5Y/10Y weights updated to 20.
- **Column header titles**: Yield and Expense Ratio now say "Context only, not scored"; 5Y/10Y titles explain the double-weighting and reference `indices.html`'s framing of the 10-year return as "the most durable signal" of structural (not lucky) outperformance.
- **`#methodEtf` popup**: pillar table and lead paragraph rewritten for Technicals 50/Performance 50 ("six scored metrics," not eight); notes the change and points to `indices.html`'s Structural Quality Metrics section.
- Row rendering: Yield/Expense Ratio cells switched from `colorScored` (hard-zero-red on missing) to `colorFromPts` (muted on missing), matching every other context-only column.

### Verified

- Headless Chrome, ETFs universe: 10/10 scored, tiers 1 S / 1 A / 3 B / 3 C / 2 F, Factors chip correctly reads `/6`. Yield/Expense Ratio/Yld−ER/YTD columns all still visible and colored as context.
- Nasdaq 100 regression: exact match to the v3.31.0 baseline, confirming zero impact on stock universes.

### Still open

- The `indices.html` doctrine write-up for Price vs 200-Day Moving Average (owner decided to document this metric there rather than remove it from the screener) has not been written yet — tracked separately in ROADMAP.md's v3.37.0 section.

---

## v3.36.1 — 2026-07-04 — Roadmap: ETF rating methodology review in progress

**Owner-requested review of the ETFs universe scoring methodology (v3.33.0). Current model presented in full and cross-checked against `indices.html`'s own documented doctrine, surfacing three gaps. Discussion in progress; no code changes in this entry.**

### Findings

- **VIX and AAII Sentiment**, which `indices.html` calls its two most actionable timing signals, are absent from the screener entirely — both are market-wide readings, not per-fund metrics, so they structurally can't differentiate scores across the 10-fund relative-ranking model. An accepted limitation.
- **Price vs 200-Day Moving Average** (10 pts, scored) has no grounding in `indices.html`'s doctrine, which names only RSI and 52-Week Range as ETF timing technicals. **Owner decision: document this metric on `indices.html` rather than remove it from the screener** — logged as a to-do in ROADMAP.md's v3.37.0 section, ready to execute independent of the other changes below.
- **YTD Performance** is named in doctrine as one of five structural quality signals but is unscored context in the screener, which instead scores 1-Year Total Return (not named in doctrine).

### In progress

- Owner requested removing Yield and Expense Ratio (20 points) from the ETF scoring model. Recommendation given: promote YTD Performance to a scored metric at the freed 20 points (Technicals 50 + Performance 50: YTD 20, 1Y 10, 5Y 10, 10Y 10), since it directly closes the doctrine gap above rather than an arbitrary redistribution. Awaiting the owner's decision before touching `ETF_METRICS` in `screener.js`.

---

## v3.36.0 — 2026-07-04 — Screener: "MAG 10" filter

**A fixed 10-stock watchlist toggle: AAPL, AMD, AMZN, AVGO, GOOGL, META, MSFT, NFLX, NVDA, TSLA. Renamed from the original "FANG+" placeholder once the owner supplied the real list. Sourced specifically from S&P 500 data (owner instruction), so each stock's score and tier reflects its percentile rank among the full 500-stock universe, not a smaller or differently-composed one.**

### Added

- **`MAG10_TICKERS`** hardcoded in `screener.js` (10 fixed tickers didn't warrant a separate JSON file, unlike the ~100-entry universe lists).
- **`#mag10Btn`** toggle button next to the tier-chip group. Clicking it switches the active universe to S&P 500 (reusing the existing lazy-load `selectUniverse()` path) if not already active, then filters the table to just these 10 rows via a new predicate in `render()`'s existing filter step — ANDs with the tier chip and search box rather than replacing them, so "MAG 10 stocks that are also tier S" is a valid combination.
- Manually switching to a different universe button while the toggle is active turns it off automatically (the filter is tied to S&P 500 data specifically, not a general cross-universe toggle).

### Verified

- Headless Chrome (script-injected click, since no Selenium/chromedriver was available): toggling on switches the universe label to S&P 500, scores against the full 500-stock set, and shows exactly the 10 MAG 10 rows. Combined with the tier-S chip: correctly narrows to the 5 MAG 10 names that are also tier S.
- Nasdaq 100 default-load regression: exact match to the v3.31.0 baseline, confirming zero impact on existing behavior.

---

## v3.34.13 — 2026-07-04 — Roadmap finalized: MAG 10 filter next, ETF review before v4.0.0, v3.35.0 retired

**Docs only. Roadmap order finalized per owner instruction: v3.36.0 (renamed "FANG+" → "MAG 10" with the owner's actual ticker list) moves to the front as next up; v3.37.0 (ETFs rating methodology review) moves ahead of v4.0.0; v3.35.0 is retired and its scope merged into v4.0.0. No code changes in this entry.**

### Changed

- **v3.36.0 renamed "MAG 10"**: the owner supplied the real ticker list (AAPL, AMD, AMZN, AVGO, GOOGL, META, MSFT, NFLX, NVDA, TSLA) and specified it should be sourced from S&P 500 data specifically, not whichever universe is active — updated design in ROADMAP.md accordingly.
- **v3.35.0 retired, merged into v4.0.0**: both are screener table/CSS work (the methodology modal's `.table-wrap` bug fix and content audit, plus the responsive column-auto-hide redesign), so building them as one pass avoids reviewing the same table rendering twice.
- **v3.37.0 moved ahead of v4.0.0** in the release order.

---

## v3.34.12 — 2026-07-04 — Roadmap renumbered: v4.5.0 mobile pass becomes v4.0.0

**Following v3.34.11's reprioritization (mobile pass moved to the front of the queue), the owner asked to renumber it to v4.0.0 to match its new position, rather than keep the v4.5.0 label from when it was the last item on the roadmap. All five other v4.x items shift by one to keep the sequence contiguous: v4.0.0 (sparklines) → v4.1.0, v4.1.0 (index coverage) → v4.2.0, v4.2.0 (historical examples) → v4.3.0, v4.3.0 (philosophy) → v4.4.0, v4.4.0 (conference call guide) → v4.5.0. No code changes; ROADMAP.md and PRD.md updated to the new numbers. Earlier PATCHNOTES entries are left as originally written and still use the numbering that was current when each was published (e.g. v3.33.1 and v3.34.1 still correctly say "v4.0.0 sparklines" and "v4.5.0 mobile pass" — patch notes are a dated historical record, not a living document, so they aren't retroactively renumbered).**

---

## v3.34.11 — 2026-07-04 — Roadmap restructure: screener scroll fix reframed as a responsive redesign, reprioritized

**Owner clarified the real requirement behind the ongoing scroll reports: the screener should reflow so scrolling is never needed at all, not just that the existing (apparently invisible/overlay) scrollbar become easier to find. Also asked whether this should merge with the already-planned v4.5.0 mobile pass — reversing an earlier decision to keep them separate, since the design question (how should the table adapt across widths?) is now the same task, not a narrow bug fix plus a later broad audit. No code changes in this entry — a roadmap restructure only.**

### Changed

- **v3.34.10's scrollbar-visibility fix is superseded, never shipped.** Its diagnosis (confirmed via a live-site width sweep that the v3.34.8 box-sizing fix is correct everywhere, and that headless Chromium can't reproduce Chrome/Opera's default overlay-scrollbar behavior) is kept for the record but the planned CSS/JS fix itself is moot once columns auto-hide instead of overflowing.
- **v4.5.0 reprioritized from the end of the roadmap to the front of the queue**, and rescoped: owner decided on auto-hiding column groups at narrower widths (Ticker/Tier/Score/Factors always visible; other groups progressively hide, extending the existing Columns menu with width-based defaults) over a card-view rebuild or fluid/shrink-to-fit sizing.
- **Scope audit**: confirmed only `screener.html` has any fixed-width element causing this class of problem — the other 8 pages already reflow correctly with no changes needed. Also confirmed the toolbar row (chips, Columns/Methodology buttons) already wraps correctly via `flex-wrap` at narrow widths in headless Chrome — no fix needed there.

---

## v3.34.10 — 2026-07-04 — Diagnosis: scrollbar still undiscoverable after v3.34.8 (plan only, not yet executed)

**Two further reports after v3.34.8 shipped show the horizontal-scroll issue isn't fully resolved: the original friend still can't scroll on Opera at their native 1280×1024, and the owner reports the table "stops scaling" when narrowing a Chrome window. Diagnosed via a live-site width sweep (1030-1400px) in headless Chrome: the v3.34.8 box-sizing fix is confirmed correct at every width tested, but headless Chromium can't reproduce what two real users on two Chromium-family browsers are both seeing — pointing at Chrome/Opera's default overlay scrollbar (hover-only, invisible in a static look) as the real remaining cause. A three-part fix is drafted in ROADMAP.md (persistently-visible scrollbar styling, wheel-to-horizontal-scroll redirect, right-edge fade affordance) but intentionally not yet executed, per instruction to present the plan first. No code changed in this entry.**

---

## v3.34.9 — 2026-07-04 — Flagged: ETF rating methodology needs review

**Owner flagged that the ETFs universe scoring methodology needs a review; specifics to follow in a later prompt. No code changes in this entry — logged here and in ROADMAP.md as a placeholder so it isn't lost.**

---

## v3.34.8 — 2026-07-04 — Screener: fixed horizontal scroll broken at some resolutions

**A friend of the owner's reported the screener table couldn't be scrolled left or right at all on their machine — it simply cut off after the Growth/Valuation columns with no visible scrollbar. Diagnosed and fixed the same day with two one-line CSS changes; kept as its own bug-fix item rather than folded into the later v4.5.0 mobile pass, since this is a desktop-resolution correctness bug, not a phone-layout design question.**

### Fixed

- **`screener.html`**: added `min-height: 0;` to `.app-table-wrap`. It's a `flex:1` child of a column flex container (`.app`, fixed at `height: 100vh`); without an explicit `min-height: 0`, a flex item's default `min-height: auto` resolves to "big enough to fit all the content" for a large scroll container, so it overflowed its parent instead of scrolling itself — and since `body { overflow: hidden }`, that overflow became invisible and unreachable.
- **`style.css`**: changed the shared `.site-layout` grid from `grid-template-columns: var(--sidebar-width) 1fr` to `var(--sidebar-width) minmax(0, 1fr)`. A bare `1fr` track has an implicit minimum size equal to its content's intrinsic width, not 0 — the screener's wide table could force the whole grid column, and the page, wider than the viewport. This is a shared rule used by every page but a no-op everywhere except the screener, which is the only page with content wide enough to hit the edge case.
- Both are classic, browser-rounding-sensitive flex/grid gotchas, which is why the bug was resolution/DPI/zoom-dependent rather than universal.

### Verified

- Headless Chrome screenshots at a constrained 1366×700 viewport, before (bug reproduced by temporarily reverting both fixes) and after: before shows the table clipped mid-row with no scrollbar and the toolbar's right-hand buttons unreachable; after shows a full horizontal scrollbar and complete table/toolbar access.

---

## v3.34.7 — 2026-07-04 — Screener: International universe leads with company name

**Owner-requested display change: the International universe now shows each holding's company name as the primary label, with the local-exchange ticker (e.g. `005930.KS`, `7203.T`) secondary — those codes aren't recognizable the way domestic tickers (AAPL, NVDA) are. Every other universe is unchanged.**

### Added

- **`nameFirst` flag** on `UNIVERSES.intl` in `screener.js` — absent on all five domestic universes, confirmed a true no-op there.
- **Table cell**: `screenCells(r)` swaps DOM order (name first, for screen readers) and adds a `name-first` class; new CSS in `screener.html` swaps which span (`.tkr` / `.tkr-name`) gets the bold/primary styling. The 720px mobile-breakpoint rule, which previously unconditionally hid `.tkr-name`, now hides whichever span is secondary in the active mode.
- **Column header**: reads "Company" for International, "Ticker" everywhere else, via a new `updateTickerColumnLabel()` called on every universe switch — a small DOM patch rather than growing the existing `HEADS` config into a third dimension (ETF mode's own "Fund" label is untouched, still driven by its separate `HEADS.etf` entry).
- **Sorting**: the ticker column now sorts by company name for International, matching what a user visually scanning names would expect; unchanged (sorts by ticker) everywhere else.
- **Per-stock popup**: title leads with the company name and subtitle shows the ticker for International, mirroring the table row.

### Verified

- Headless Chrome, International: header reads "Company", first row's cell is `<span class="tkr-name">Samsung Electronics Co.</span><span class="tkr">005930.KS</span>` with `name-first` present, 100/100 rows, no console errors.
- Headless Chrome, Nasdaq 100 (regression): header still "Ticker", cell structure and DOM order unchanged, tiers exactly match the v3.31.0 baseline (2 S+ / 10 S / 8 A / 32 B / 24 C / 24 F, MU at top).

---

## v3.34.6 — 2026-07-04 — Screener: International feed same-company duplicate fix

**Owner-flagged bug fixed the same day: the International universe listed Samsung Electronics twice (`005930.KS` common, `005935.KS` preferred) since they carry different ISINs and the v3.34.0 dedup only caught literal duplicate-ISIN rows. Scanned the full raw Vanguard response for other cases and hand-verified every candidate before writing any merge logic.**

### Fixed

- **`VXUS_SAME_ISSUER_MERGE`** added to `update_etf_constituents.py`: a hand-verified `{kept_isin: [dropped_isin, ...]}` map (8 entries) applied in `fetch_vxus_raw()` before the top-100 cut, covering three distinct categories found by inspection: a duplicate custody record for the identical security (Air Liquide, L'Oreal, Engie — each had a normal-ticker line and a blank-ticker line, likely a French registered/bearer-share settlement split), a real dual share class (Samsung Electronics common/preferred, Investor AB and Atlas Copco Class A/B), and a dual listing of the same group across exchanges (Rio Tinto London/Australia, CATL Hong Kong/Shenzhen, tie-broken by raw market value where the rounded weight was equal).
- **No automatic name-matching ships in production**, per the original plan's caution — validated by a real false positive the scanning heuristic produced: SoftBank Group Corp and SoftBank Corp are genuinely different, separately-traded companies (parent vs. its separately-listed telecom subsidiary), not share classes of one issuer. Every merge entry was hand-checked against the raw data before being added.
- **Rebuilding `data/vxus.json`** against the live Vanguard API correctly promoted L'Oreal (`OR.PA`) and Investor AB (`INVE-B.ST`) into the true top 100 on their properly-combined weight, bumping out two lower-weighted names that had only ranked ahead under the old split-weight accounting. `screener.js`'s `CURRENCY_SYMBOLS` gained `SEK` (Investor AB introduced Swedish krona). The now-dead manual override for Air Liquide's merged-away ISIN was removed from `vxus_map.json`.

### Verified

- `data/vxus.json`: 100 entries, 100 unique symbols, exactly one Samsung Electronics row (Samsung Electro-Mechanics correctly remains separate).
- Headless Chrome: 100/100 rows, no duplicate company names, tiers sum to 100.
- `sync_vxus()` re-run against the live Vanguard API reproduced the corrected list with zero further changes.

---

## v3.34.5 — 2026-07-04 — Ops: data pipeline re-scheduled (owner decisions)

**Following the workflow timing review logged in v3.34.2, the owner made two decisions and the full daily pipeline schedule is re-anchored and widened. All five daily workflow files updated; docs updated to match.**

### Changed

- **Anchor changed from a fixed Eastern-clock offset to "30 minutes after the latest possible US market close in UTC terms."** US market close is always 4:00pm Eastern, which is 21:00 UTC in winter (EST) but only 20:00 UTC in summer (EDT) — winter is later in UTC. The old schedule (23:00 UTC start) drifted the post-close buffer between 2 and 3 hours depending on season with no clear guarantee; the new anchor (21:30 UTC start) guarantees **at least 30 minutes** after close in every season, growing to 90 minutes in summer. Owner decision: keep a fixed, non-DST-aware cron (no seasonal cron swaps), but pick the anchor point deliberately rather than inheriting whatever a round-number UTC time happened to imply.
- **Every gap in the daily chain widened to a uniform 30 minutes** (previously a 15/15/30/15 mix), a safety margin against a slow prior run bumping into the next job's start.
- **New schedule** (all Mon-Fri, all same calendar day): Nasdaq 100 21:30 UTC → ETFs 22:00 UTC → S&P 500 22:30 UTC → Growth/Value/Dividend 23:00 UTC → International 23:30 UTC. A side effect of the new anchor: since the whole chain now fits before midnight UTC, the Tue-Sat day-rollover cron pattern the GVD and International jobs previously needed is gone — all five daily crons are now a plain Mon-Fri (`1-5`).
- Saturday constituent sync (23:00 UTC) is unchanged and still clear of the daily chain.
- Docs updated to match: README (pipeline paragraph, tech stack table, project structure), PRD (Data Pipeline section, architecture diagram, folder structure, two FAQ entries), ROADMAP.md (v3.34.5 marked done with the old-vs-new schedule table).

---

## v3.34.4 — 2026-07-04 — Roadmap: two owner-requested screener features logged

**Docs only. Two new roadmap items in ROADMAP.md, both owner-requested. No code, workflow, or behavior changes in this entry.**

### Added

- **v3.34.7 — International universe: lead with company name, not ticker.** Local-exchange tickers (`005930.KS`, `7203.T`) are meaningless to most readers compared to the company name; the domestic universes keep ticker-primary since those tickers (AAPL, NVDA) are already recognizable. Needs a per-universe display hint beyond the existing stock/ETF `kind` split, since International shares "stock" kind with the five domestic universes and today's `screenCells()`/`renderHead()` have no hook for "which is primary" at that finer grain.
- **v3.36.0 — "FANG+" filter.** Blocked on the owner supplying the actual ticker list (no composition guessed ahead of that). Designed as a client-side toggle over whichever universe is currently loaded, not a new universe or feed — ANDs with the existing tier filter and search box rather than replacing them, and the list is stored in a small reusable `{"name", "tickers"}` JSON shape rather than a single hardcoded array, in case future curated watchlists get requested.

---

## v3.34.3 — 2026-07-04 — Roadmap: International feed same-company duplicate bug logged

**Docs only. Owner flagged that the International universe lists the same company twice under different share classes: `005930.KS` (Samsung Electronics common) and `005935.KS` (Samsung Electronics Co. Ltd. Preference Shares) — confirmed present in the live `data/vxus.json`. Different ISINs, so v3.34.0's ISIN-dedup (built to solve Vanguard reporting one ISIN twice, e.g. BHP/Barrick) never caught this. Logged as v3.34.6 in ROADMAP.md, right after the workflow timing review. No code, workflow, or behavior changes in this entry.**

### Added

- **Root cause and scope note**: the domestic Growth/Value/Dividend lists already solve this exact problem via `update_etf_constituents.py`'s `DUAL_CLASS` map, which collapses multiple share classes to one listing before the top-100 cut. `sync_vxus()` never got the equivalent treatment because its dedup step targets literal duplicate ISIN rows, not two-different-ISINs-same-issuer pairs.
- **Plan in ROADMAP.md (v3.34.6)**: scan the full raw Vanguard response for other common/preferred or multi-class pairs (expect a short list, not a large one), decide a matching signal more reliable than name-similarity alone, decide which class to keep (likely the higher-weighted/more liquid one, using Vanguard's own `percentWeight`), and implement as a hand-verified override map mirroring `DUAL_CLASS` rather than an automatic name-matching rule running unattended on the weekly sync.

---

## v3.34.2 — 2026-07-04 — Roadmap: GitHub Actions workflow timing review logged as the immediate next step

**Docs only. Owner asked to review when every GitHub Actions workflow runs and the gaps between them, as the very next item ahead of v3.35.0. Logged in ROADMAP.md (v3.34.5) with the full schedule already compiled, so the review is ready without further digging. No code, workflow, or behavior changes in this entry.**

### Added

- **Full six-job schedule table** (all times UTC): Nasdaq 100 23:00 → ETFs 23:15 (+15m) → S&P 500 23:30 (+15m) → Growth/Value/Dividend 00:00 next day (+30m) → International 00:15 next day (+15m) → constituent sync Saturday 23:00 (weekly, not daily). All six share one concurrency group with `cancel-in-progress: false`, so overlapping runs queue rather than race.
- **Three findings flagged for owner review**: (1) GitHub's cron scheduler is UTC-only and does not observe US daylight saving time, so the entire staggered chain shifts an hour relative to US market close twice a year (already a code comment in `screener-data.yml`, easy to miss); (2) the 15-minute gaps around the ETFs and International jobs are tighter than the 30-minute GVD gap, worth confirming against actual run durations if either job has run long; (3) the Saturday constituent sync lands at the same time-of-day as the weekday jobs but on a day none of them run, so it only looks like a collision on paper.

---

## v3.34.1 — 2026-07-04 — Roadmap: methodology audit, table display bug, and a mobile-friendliness pass logged

**Docs only, two owner requests logged as new roadmap items in ROADMAP.md. No code, workflow, or behavior changes in this entry.**

### Added

- **v3.35.0** (next up): owner flagged display issues with the screener's Methodology popup tables and asked for a content-currency audit. The likely root cause was found by code inspection before any code changed: `style.css`'s `.table-wrap` rule sets `overflow-x: auto` and then a later `overflow: hidden` in the same block silently overrides it for both axes (the `overflow` shorthand resets both `overflow-x` and `overflow-y`), so a methodology table wider than the modal gets its content clipped instead of scrolling, with no visible scrollbar. `thead th { white-space: nowrap }` compounds this by keeping header cells from wrapping.
- **v4.5.0** (appended to the end of the queue): a site-wide mobile-friendliness pass, owner-requested. Scoped as a hardening/audit pass rather than a rebuild, since real responsive infrastructure already exists (viewport meta, hamburger nav collapse, modal width breakpoint, wrapping universe-switcher buttons). Starting points already identified: whether the screener's main table should pin its Ticker/Tier/Score columns while scrolling the rest, how the now-7-button universe switcher behaves at phone widths, and that it should sequence after v3.35.0 so the table CSS fix isn't reviewed twice under two different roadmap items.

---

## v3.34.0 — 2026-07-04 — Screener: International universe

**A seventh screener universe: the top 100 holdings of VXUS (Vanguard Total International Stock ETF), scored with the exact same six-metric stock model as the other stock universes — no new scoring logic, just a new feed and a currency-aware price/balance-sheet display. Built following the Phase 0-3 plan in ROADMAP.md (probed and decided in v3.33.2/v3.33.3); two real data quirks turned up during the build that weren't in the plan and are documented below.**

### Added

- **International universe button**, seventh in the switcher, reusing the domestic stock table, columns, scoring, and popup byte-for-byte (Growth 60 / Valuation 20 / Balance sheet 20, hard-zero missing data, S+/S/A/B/C/F tiers).
- **`data/vxus.json`** (100 holdings, `t` already resolved to a Yahoo symbol) and **`data/vxus_map.json`** (ISIN → Yahoo symbol resolution cache with a `manual` override block), built from a live Vanguard + Yahoo run and verified idempotent by re-running the new sync logic against the live API with zero changes reported.
- **`sync_vxus()`** in `update_etf_constituents.py`: fetches VXUS holdings, **dedupes two ISINs Vanguard reports as split rows** (BHP Group, Barrick Gold — summed by weight before ranking, or the top-100 cut silently admits only 98 distinct issuers), resolves each via ISIN search (99/100 direct) with a name-search fallback (1/100, a holding with a blank Vanguard ticker field), and never writes a partial list.
- **`data/screener_intl.json`** feed and **`.github/workflows/screener-data-intl.yml`** (Tue-Sat 00:15 UTC, 15 minutes after the GVD job), plus VXUS membership + resolution-cache handling folded into the existing Saturday `constituents.yml` sync.
- **`cur` field** added to every stock feed record (`fetch_screener_data.py`): the ISO currency code, used only by the frontend's International-universe price/balance-sheet formatting; harmless for the five USD universes (defaults display exactly as before).
- **Currency-symbol display**: `screener.js` gained a `CURRENCY_SYMBOLS` lookup and a `cur`-aware `fmtPrice`/`fmtMoney` — Price, Mkt Cap, Total Cash, and Total Debt render in each stock's native currency labeled with its symbol (`NT$`, `₩`, `€`, `£`, `¥`, `HK$`, `C$`, etc.), falling back to the ISO code for symbol-less currencies (`CHF`).
- Methodology popup: the stock section's universe-source table gained an International row (VXUS top 100, currency note, thin-foreign-coverage note); disclaimer bar updated.

### Fixed / discovered during the build (not anticipated in the Phase 0-3 plan)

- **Yahoo quotes London-listed stocks in pence (`GBp`/`GBX`), not pounds** — but that same listing's `marketCap`/`totalCash`/`totalDebt` are already reported in pounds (verified: HSBC's `marketCap` exactly equals its pence-converted price × `sharesOutstanding`). `fetch_screener_data.py` now normalizes `GBp`/`GBX` to `GBP` and divides `price`/`prevClose` by 100 at fetch time, so nothing downstream — including the currency-symbol display above — ever has to know about the pence convention.
- **The domestic dot-to-dash ticker fix would have corrupted every International symbol.** `fetch_screener_data.py` previously replaced every `.` with `-` (for `BRK.B`-style dual-class tickers). That's fine for the two domestic tickers that actually need it, but would have turned `2330.TW` into the invalid `2330-TW`. Replaced with an explicit `{"BRK.B", "BF.B"}` set instead of a blanket replace, since a suffix-length heuristic can't distinguish a domestic `.B`/`.A` share class from London's one-letter `.L` exchange suffix.

### Verified

- Headless Chrome against the live local feed: 100/100 scored, tiers 1 S+ / 10 S / 13 A / 29 B / 22 C / 25 F, currency symbols render correctly per row (₩/NT$/¥/€/£ spot-checked), no console errors.
- Nasdaq 100 regression still exactly matches the v3.31.0 baseline (2 S+ / 10 S / 8 A / 32 B / 24 C / 24 F, MU and NVDA at 100) — the `cur` parameter is additive and optional everywhere it was threaded through.
- `sync_vxus()` re-run against the live Vanguard API reproduced the committed `data/vxus.json` with zero changes, confirming the sync logic matches what was hand-verified during the probe.

---

## v3.33.3 — 2026-07-03 — Docs: v3.34.0 Phase 3 owner decisions locked

**Docs only. All three Phase 3 owner-decision gates for the v3.34.0 International universe are now locked: currency display (native currency, labeled with the currency symbol rather than the ISO code, per owner refinement), sparse estimates (hard-zero rule kept as-specced, already resolved by the probe), and ADR vs. local-listing ranking (rank the local listing). Phase 1 (constituents and mapping) is cleared to begin. No code, workflow, or behavior changes.**

### Changed

- ROADMAP.md Phase 3: currency-display decision refined from a plain ISO-code label (e.g. `2,445 TWD`) to a **currency-symbol** label (e.g. `NT$2,445`, `₩309,500`, `€284.10`) wherever a standard symbol exists, falling back to the ISO code only when no widely recognized symbol exists (e.g. `CHF`) or where a bare `$` would be ambiguous with the site's existing USD `$` convention (so `HK$`/`NT$`/`C$`, never a bare `$`).
- ROADMAP.md Phase 4 (frontend): added a `CURRENCY_SYMBOLS` lookup design note (ISO code → symbol, plain object lookup) for the eventual `cur`-field formatter, so v3.34.0's build has this decided in advance.

---

## v3.33.2 — 2026-07-03 — Docs: v3.34.0 Phase 0 probe findings

**Docs only. Ran the v3.34.0 International-universe Phase 0 probe live (Vanguard holdings API shape, ISIN-to-Yahoo symbol resolution, yfinance field coverage on the six scored metrics) against real VXUS data, ahead of any production code. Findings logged in ROADMAP.md and the PRD milestone table. No code, workflow, or behavior changes.**

### Findings

- **Vanguard API caps at exactly 500 holdings**, not the ~8,500 VXUS actually holds — a correction to the original plan's assumption. No pagination needed; every entity carries an **ISIN** directly, so no separate lookup call is needed to get an identity key.
- **Symbol resolution: 100/100 on the real top 100 holdings** using the planned two-rung ladder — 99 resolved directly via ISIN → Yahoo search, 1 (Air Liquide, whose Vanguard entity had a blank ticker field) via the name-search fallback to its primary Paris listing. Three dual-listing cases (Alibaba, Siemens, Siemens Energy) returned multiple hits; the first (primary listing) was correct in all three.
- **Field coverage on all six scored metrics is 88-100%** (worst case `earningsGrowth`/epsTTM at 88/100), using the exact yfinance fields `fetch_screener_data.py` reads. Because the hard-zero rule already applies per metric (not per stock), this resolves the sparse-estimates concern: keep the rule exactly as specified, no shrunk denominator, no dropped names — the methodology popup gets one added sentence instead.
- **Currency diversity confirmed material**: 8+ currencies (TWD, KRW, EUR, GBP, JPY, CHF, HKD, CAD) in just the top 15 holdings, settling the currency-display decision toward native-currency-with-label over USD conversion.
- Remaining owner decision, unaffected by the probe: ADR vs. local-listing ranking preference. Recommendation unchanged (rank the local listing Vanguard actually holds); none of the top 100 needed an ADR fallback in the probe.

---

## v3.33.1 — 2026-07-03 — Docs: ROADMAP.md implementation plans

**Docs only. A fifth documentation file, `docs/ROADMAP.md`, holds a detailed implementation plan for every remaining roadmap item, per owner request. The PRD milestone table stays the source of truth for what is planned and in what order; ROADMAP.md is the reference for how each item will be built, and a shipped item's plan is trimmed to a pointer. No code, workflow, or behavior changes.**

### Added

- **v3.34.0 International (VXUS top 100) plan**: probe-first phasing (Vanguard API shape at ~8,500 holdings, ISIN-or-name symbol resolution to Yahoo suffixed symbols, six-metric field-coverage census on the real top 100 before any production code); `data/vxus.json` storing resolved Yahoo symbols plus a committed `data/vxus_map.json` resolution cache with manual overrides; feed via the existing `fetch_screener_data.py --list/--out` path and a Tue-Sat 00:15 UTC workflow; three owner decision gates (currency display, sparse-estimates handling under the hard-zero rule, local listing vs ADR) to be presented with the probe's coverage report; mandatory stock-universe regression against the v3.31.0 baseline.
- **v4.0.0 score-history sparklines plan**: built around the central design fact that the feeds store raw metrics, not scores, so history must be recomputed by replaying git-history snapshots (`git log`/`git show`) through a Python port of the scoring model; a hard parity gate (the Python scorer must exactly reproduce the live headless-rendered scores for all universes, and the parity test runs in CI so future scoring drift fails loudly); `data/history.json` capped at 90 trading days per ticker with a size budget; inline SVG sparkline column plus popup chart, lazily fetched and gracefully degrading; recommended owner decisions recorded (replay under the current model, 90-day window, all six universes).
- **v4.1.0-v4.4.0 content release plans**: deeper index fund coverage (sector ETFs, international allocation sequenced after v3.34.0 for cross-linking, bond tent), historical illustrative examples (candidate episodes, embed-in-context placement, hindsight-flagged format), additional philosophy sections (candidate topics including when to sell and position sizing), and the conference call research guide as a new `conferencecalls.html` guide page mapped to the six scored metrics; plus a shared release-mechanics checklist (persona/content rules, sidebar/FAQ/sitemap/meta touches, headless verification).

### Changed

- PRD: roadmap section links to ROADMAP.md; documentation strategy FAQ and the current-phase note now count five documentation files.
- README: project structure and Full Documentation list gained ROADMAP.md.

---

## v3.33.0 — 2026-07-03 — Screener: ETFs universe

**A sixth screener universe: a fixed, owner-curated list of 10 ETFs (QQQ, SPY, DIA, IWM, VTI, VXUS, VUG, VIG, VTV, SPMO), scored on technicals, long-term performance, yield, and cost instead of fundamentals — the technical scoring the stock universes deliberately exclude, per the site's technicals-time-ETF-purchases doctrine. Owner-specced same day (v3.32.2-v3.32.4), decisions resolved via review (rank-linear points, rank-band tiers kept, yield scored as specced).**

### Added

- **ETFs universe button** with its own 20-column table: AUM, Price, Chg %, YTD, 1Y/5Y/10Y Total Return, Yield, Expense Ratio, Yield−ER, RSI, 52W Range, Price vs 20/100/200-Day MA, Updated. Scored 100 points: Technicals 50 (RSI 20 lowest-best, 52W range position 20 lowest-best, vs-200DMA 10 highest-best), Performance 30 (1/5/10y total returns, 10 each), Income & cost 20 (yield 10, expense ratio 10 lowest-best). YTD, Yield−ER, and the 20/100-day MAs are colored context columns with no points; AUM is display-only.
- **Rank-linear points for this universe**: with 10 funds a percentile clamp is far too coarse, so the best fund on a metric earns full points, the worst 0, evenly spaced, ties averaged. Missing data stays a hard zero out of a fixed /100. Factors chip is /8. Cell colors: green at 15+ rank points (top ~3), red at 5 or less (bottom ~3).
- **`data/etfs.json`** (fixed list, hand-edited only, never auto-synced), **`scripts/fetch_etf_data.py`** (one 11-year history call per fund: total returns on dividend-adjusted closes, RSI/52W/MAs on unadjusted closes; yield from `dividendYield`, expense ratio from `netExpenseRatio`, both verified live for all 10 funds), **`data/screener_etfs.json`** feed, and **`.github/workflows/screener-data-etfs.yml`** (Mon-Fri 23:15 UTC, between the Nasdaq 100 and S&P 500 jobs, same concurrency group).
- **Methodology popup: dedicated ETF section** (pillar table, rank-points explanation, tiers-on-10-funds note including why an F here usually means "already ran up", fixed-list provenance) shown when the ETFs universe is active; the stock section shows otherwise. Per-fund popup breakdown with rank points per metric.

### Changed

- **screener.js: the table header and Columns menu are now config-driven** and re-render when the universe kind changes (stock vs ETF); sort clicks and Columns-menu changes moved to event delegation so they survive the re-render. This refactor pre-pays for future non-stock universes. **Stock universe logic and output are unchanged**: verified headless against the local feeds — Nasdaq 100 = 2 S+ / 10 S / 8 A / 32 B / 24 C / 24 F with MU and NVDA at 100, matching the v3.31.0 baseline exactly; ETF→stock switching restores the stock table byte-for-byte.
- Tier rank bands on the 10-fund list land at 1 S / 1 A / 3 B / 3 C / 2 F (verified live; owner accepted that an F badge on a household index fund means "bottom of this list right now").
- Screener meta description and disclaimer updated for the sixth universe (the ETFs list is fixed, not synced).

---

## v3.32.4 — 2026-07-03 — Roadmap: v3.33.0 ETF spec review concerns logged

**Docs only. Four pre-implementation review concerns are logged in the PRD's ETF Universe Scoring Model section, per owner request after a spec review. The spec itself is unchanged; the concerns are to be resolved during or before implementation: (1) yield is partially double-counted by total returns and tilts toward income-style funds; (2) RSI + 52W Range + Price vs 200DMA put 50 correlated dip-depth points in one factor, so scores will swing with selloffs; (3) S/A/B/C/F rank bands fit a 10-fund list badly (F badges on SPY/VTI, S+ nearly unreachable); (4) percentile scoring is coarse at N=10 and the 22% clamp was calibrated for 100+ stocks — absolute thresholds or rank-points recommended for this universe.**

---

## v3.32.3 — 2026-07-03 — Roadmap: v3.33.0 ETF Universe Scoring Model spec completed

**Docs only. The owner picked Price vs 200-Day Moving Average for the last 10 scoring points, and asked for Price vs 20-Day and Price vs 100-Day Moving Average as additional display columns. The ETF Universe Scoring Model is now fully specced at 100/100. No code, workflow, or behavior changes.**

### Added

- **Price vs 200-Day Moving Average**, highest is best, 10 points — completes the 100-point scoring model (RSI 20, 52-Week Range 20, 1Y/5Y/10Y Total Return 10 each, Yield 10, Expense Ratio 10, Price vs 200DMA 10).
- **Price vs 20-Day Moving Average** and **Price vs 100-Day Moving Average**, unscored display/context columns, giving short/medium/long trend context alongside the scored 200-day signal (same scored-vs-context pattern the stock universes use for P/E FWD).

### Changed

- Visible column count for the ETFs universe is now 14 (was 11): Price, Daily % Change, YTD/1Y/5Y/10Y Total Return, Yield, Expense Ratio, Yield − Expense Ratio, RSI, 52-Week Range, Price vs 20DMA, Price vs 100DMA, Price vs 200DMA.

---

## v3.32.2 — 2026-07-03 — Roadmap: v3.33.0 ETF Universe Scoring Model spec locked

**Docs only. The owner locked the fixed 10-fund ETF list, the visible column set, and 90 of 100 scoring points for the upcoming v3.33.0 ETFs universe. No code, workflow, or behavior changes.**

### Added

- **PRD "ETF Universe Scoring Model" section**: fixed list (QQQ, SPY, DIA, IWM, VTI, VXUS, VUG, VIG, VTV, SPMO, no auto-sync); 11 visible columns (Price, Daily % Change, YTD/1Y/5Y/10Y Total Return, Yield, Expense Ratio, Yield − Expense Ratio, RSI, 52-Week Range); scoring table for the 9 decided criteria: RSI (lowest best, 20), 52-Week Range (lowest best, 20), 1Y/5Y/10Y Total Return (highest best, 10 each), Yield (highest best, 10), Expense Ratio (lowest best, 10) — 90 of 100 points.
- **Open question recorded:** the last 10-point criterion. Five options were put to the owner: (1) YTD Performance, highest best — already a visible column, fills the gap in the return-horizon ladder alongside 1Y/5Y/10Y, needs no new yfinance field; (2) Yield − Expense Ratio (net yield), highest best — also already a visible column, rewards funds whose distribution actually outpaces its cost to hold; (3) Price vs. 200-day moving average (trend/momentum), a technical signal in the same family as RSI; (4) Trailing volatility (e.g. 1-year return standard deviation), lowest best, a risk-adjusted/steadiness signal; (5) Average trading volume/liquidity, highest best, a practical tradability signal (weakest fit to the technicals/performance/cost doctrine of the other nine criteria).

---

## v3.32.1 — 2026-07-03 — Roadmap: ETFs universe prioritized ahead of International

**Docs only. The owner asked to ship the ETFs universe before the International (VXUS) universe. Milestone numbers swapped: ETFs is now v3.33.0 (still blocked on the owner's ETF list), International is now v3.34.0. No code, workflow, or behavior changes.**

---

## v3.32.0 — 2026-07-03 — Pipeline cleanup

**Housekeeping only; no code, workflow, or behavior changes.**

### Changed

- **Legacy `FMP_API_KEY` secret deleted** from the repository settings (owner step). It dated from the pre-v3.16.0 Financial Modeling Prep integration; verified that no workflow, script, or page has referenced FMP since v3.16.0 removed that path.
- **Data-files-in-git reclassified from tech debt to intentional design** in the PRD: the committed feeds (`screener.json`, `screener_sp500.json`, `screener_gvd.json`) are the site's only record of past scores, and their git history is the data source the planned v4.0.0 score-history sparklines will mine. Moving them to external artifact storage would delete the feature's raw material.

---

## v3.31.0 — 2026-07-03 — Scoring: margins removed, owner growth-forward weights

**Gross Margin and Net Margin are removed from the scoring model and the table, hours after v3.30.0 shipped them: the owner had not intended margins to be scored. The remaining six metrics carry owner-set weights with forward growth counting double trailing: Rev TTM 10, Rev FWD 20, EPS TTM 10, EPS FWD 20, PEG FWD 20, Cash vs Debt 20 (Growth 60 / Valuation 20 / Balance sheet 20).**

### Changed

- **Profitability pillar removed**: the Gross Mgn / Net Mgn columns, their Columns-menu toggle, and their 20 score points are gone. The `grossMargin`/`netMargin` feed fields stay in the pipeline and JSON (harmless, available for future use).
- **Growth pillar re-weighted to 60** with the owner's asymmetric weights: forward revenue and EPS growth carry 20 points each, trailing 10 each.
- **Points curve re-clamped from top/bottom 28% to top/bottom 22%**: `points = clamp(20 × (pct − 0.22) / 0.56, 0, 20)`. Recalibrated on the live feeds for the 6-metric weighted model against the same owner target (~1 perfect 100 in the Nasdaq 100, ~5 in the S&P 500, ties round up); live at ship: 2 tied at 100 in the Nasdaq 100, exactly 5 in the S&P 500.
- **Factors chip is now x/6**; the per-stock popup lists the six scored metrics; the methodology popup's pillar table, curve table, Apple worked example, and factor text all updated.

---

## v3.30.0 — 2026-07-03 — Scoring model v2: four pillars, margins, hard-zero missing data, S+ tier

**The scoring model is rebuilt around four weighted pillars over eight metrics: Growth 40 (Rev TTM 10, Rev FWD 10, EPS TTM 10, EPS FWD 10), Valuation 20 (PEG FWD), Profitability 20 (Gross Margin 10, Net Margin 10), Balance sheet 20 (Cash vs Debt). A perfect 100/100 now earns a new S+ tier. Pulled ahead of pipeline cleanup by owner priority; all decisions owner-approved after live-data simulations.**

### Added

- **S+ tier for a perfect 100/100** (owner request): sits above the S/A/B/C/F rank bands, in purple (`--color-tier-splus` #bc8cff) so it stands apart from the green ramp. New S+ filter chip, badge, summary count (shown only when at least one exists), and methodology legend entry. S+ stocks come out of the S band's headcount. The clamp calibration keeps S+ rare: at ship, MU and NVDA (tied) in the Nasdaq 100 and ADSK, SCHW, META, MU, NVDA in the S&P 500.
- **TTM growth is now scored** (owner request): Revenue Growth TTM and EPS Growth TTM join the Growth pillar at 10 points each, matching the doctrine's "revenue and net income up and to the right TTM".
- **Profitability pillar**: `grossMargin` and `netMargin` (TTM, from yfinance `grossMargins`/`profitMargins`) added to the pipeline, all three feeds reseeded, and a new Profitability column group (Gross Mgn, Net Mgn) added to the table with its own Columns toggle. The screener now reflects doctrine metrics 11-12.
- **Methodology popup: "Where each list comes from"** (owner request): a source table for all five universes (Nasdaq 100 / S&P 500 from the published index lists via weekly sync; Growth / Value / Dividend from the top 100 VUG / VTV / VIG holdings by weight, Vanguard-published, monthly cadence, dual classes collapsed).

### Changed

- **Points curve re-clamped from top/bottom 25% to top/bottom 28%**: `points = clamp(20 × (pct − 0.28) / 0.44, 0, 20)`, scaled by metric weight. Calibrated against the final live 8-metric feeds to the owner's target of ~1 stock at 100 in the Nasdaq 100 and ~5 in the S&P 500 (ties round up): live at ship, 2 tied at 100 in the Nasdaq 100 and exactly 5 in the S&P 500, vs 4 and 11 under the old quartile clamp, which handed a perfect 20/20 to a quarter of the list per metric. (An interim 15% clamp, fitted before the margin fields landed in the feeds, proved too tight with all eight metrics live: top scores stalled at 99 with zero perfect scores.)
- **Valuation double-count removed**: P/E-vs-growth drops to a zero-weight context ranking that only colors the P/E FWD column; PEG FWD carries the full 20-point valuation pillar alone.
- **Missing data is a hard zero** (owner decision): a "—" in any scored metric contributes 0 points, the /100 denominator never shrinks, and the cell renders dark red. Pre-v2, missing metrics were dropped and the score rescaled, letting stocks scored on 3 of 5 metrics reach 100 (several of the S&P 500's perfect scores had missing EPS TTM).
- **Factors chip is now x/8 fixed-denominator** (missing = miss, never a pass); per-stock popup lists all eight metrics with weighted points (e.g. "7.2/10") and shows zeroed missing rows in dark red; methodology popup rewritten (pillar table, new curve table, updated Apple worked example).

### Notes

- Tiers are structurally unaffected: S/A/B/C/F sizes are rank-based and stay fixed; only scores, colors, and per-metric points change underneath.
- The decision history (Strong Buy labels rejected, fixed cuts rejected, curve calibration data) is recorded in the PRD roadmap.

---

## v3.29.2 — 2026-07-03 — Roadmap: ETFs universe planned

**Docs only. New planned milestone v3.32.0: an ETFs screener universe from a fixed, owner-provided list, rated on technicals (RSI, 52-week range), long-term performance, and expense ratios instead of fundamentals — the technical scoring the stock universes deliberately exclude, per the site's technicals-for-indices doctrine. Blocked on the owner's ETF list. The pending scoring-model-v2 milestone renumbers from v3.32.0 to v3.33.0.**

---

## v3.29.1 — 2026-07-03 — Roadmap: scoring model v2 under review

**Docs only. New planned milestone v3.32.0 documents the scoring-model revision under owner review: a full-range linear points curve (to end the crowd of 100/100 scores), a possible four-pillar metric restructure scoring Rev/EPS TTM and gross/net margins while removing the valuation double-count, and a missing-data rule so a "—" in a scored metric reads dark red and hurts the score instead of being dropped and rescaled. Decisions pending; priority TBD.**

---

## v3.29.0 — 2026-07-03 — Screener: rank-based S/A/B/C/F tier scale

**Pass/Watch/Fail is replaced by a five-tier, rank-based grade. Tiers are assigned by position within the loaded universe, not by fixed score cuts: S = top 10% of the list, A = next 10%, B = 20-50%, C = 50-75%, F = bottom 25%, with boundary ties rounding up into the higher tier. Pulled ahead of pipeline cleanup by owner priority (planned as v3.31.0, shipped as v3.29.0).**

### Added

- **Tier column** (replacing Verdict) with S/A/B/C/F badges; filter chips relabeled All/S/A/B/C/F with live counts; summary line shows the tier distribution.
- **Four color tokens** in style.css and DESIGN.md: `--color-tier-s` #2ea043 (dark green), `--color-tier-a` #7ee787 (light green), `--color-tier-b` #e3b341 (yellow), `--color-tier-c` #ffa198 (light red); tier F reuses `--color-negative` (dark red). Score-bar fill and badges are colored by tier, so the same score can carry a different color in a different universe.
- **Methodology popup**: tier legend (percent bands, not score ranges), the tie round-up rule, and the fixed-distribution property (~10/10/30/25/25 per 100 stocks, scaling to any universe size).

### Changed

- `screener.js`: `verdictOf()` (fixed cuts) replaced by `computeTierMap()` (sorts scored stocks, slices at 10/20/50/75% with tie promotion); per-stock popup shows "Tier S" style labels; "bottom third always lands in Fail" caveat rewritten ("an F means the bottom of this particular list, not a broken company").
- Rank-based bands were chosen over the initially planned fixed score cuts (80/65/50/35) after the owner reviewed live distributions: score clustering at the top quartile put 19 stocks in S and 37 in F on the Nasdaq 100; rank bands fix the sizes structurally (verified live: Nasdaq 100 = 10/10/32/23/25 with tie stretch, S&P 500 = 52/49/149/131/119, Dividend = 10/10/30/25/25).
- Decision history preserved: the owner's first proposal (Strong Buy through Strong Sell) was dropped for conflicting with the PRD's no-advice-language rules; S/A/B/C/F tier-list vocabulary carries the relative-ranking meaning natively.

### Notes

- Roadmap renumbered: pipeline cleanup is now v3.30.0, the International (VXUS) universe v3.31.0.
- A scoring-model revision (points curve, TTM metrics in the score, missing-data handling) is under owner review as a separate follow-up.

---

## v3.28.2 — 2026-07-03 — Roadmap: v3.31.0 tier labels decided (S/A/B/C/F)

**Docs only. The v3.31.0 five-tier scale's open label question is resolved: S / A / B / C / F tiers under a "Tier" column header, cuts at 80/65/50/35, dark green through dark red. Chosen over the original Strong Buy-to-Strong Sell proposal, which conflicted with the PRD's no-advice-language rules; tier-list vocabulary carries the relative-ranking meaning natively for the site's audience.**

---

## v3.28.1 — 2026-07-03 — Roadmap: five-tier verdict scale planned

**Docs only. New planned milestone v3.31.0: replace the screener's Pass/Watch/Fail verdicts with five bands on the existing score, colored dark green through dark red. The owner's proposed labels (Strong Buy through Strong Sell) are recorded alongside the open conflict with the PRD's no-advice-language rules; a screen-relative alternative label set is noted for decision at build time.**

---

## v3.28.0 — 2026-07-03 — Screener: Growth, Value & Dividend universes

**The screener grows from two universes to five. New Growth, Value, and Dividend views cover the top 100 holdings of Vanguard's VUG, VTV, and VIG ETFs, refreshed daily from one combined feed. The "Expand to S&P 500" toggle is replaced by a five-button universe switcher. Scope note: the owner added Value (VTV) mid-build, turning the planned Growth/Dividend pair into the site's GVD framework trio.**

### Added

- **Three ETF universes**: Growth (top 100 VUG holdings), Value (top 100 VTV holdings), Dividend (top 100 VIG holdings). Constituents come from Vanguard's own holdings API (authoritative for an ETF-defined universe; Vanguard publishes holdings monthly), synced weekly by the new `scripts/update_etf_constituents.py` into `data/vug.json` / `data/vtv.json` / `data/vig.json` with the same dual-class dedupe and never-clobber sanity guards as the index sync. New dual-class pairs handled: BRK.A→BRK.B, LEN.B→LEN, BF.B→BF.A, HEI.A→HEI. All 300 tickers (220 unique) were validated against Yahoo before shipping; names were aligned to the site's curated short forms.
- **Combined feed** `data/screener_gvd.json`: `fetch_screener_data.py` gains a repeatable `--combined NAME=LIST` mode producing `{universes: {growth, value, dividend}}`, each entry shaped exactly like a single-list feed. Overlapping symbols are fetched from Yahoo once per run. New workflow `screener-data-gvd.yml` refreshes it 30 minutes after the S&P 500 job (00:00 UTC, Tue-Sat cron = Mon-Fri US trading days), sharing the `screener-data` concurrency group. The feed was seeded locally (100/100 price coverage in all three universes) so the views work immediately.
- **Universe switcher**: five `.btn`-style buttons in the app bar (Nasdaq 100, S&P 500, Growth, Value, Dividend), active one lit in the accent color, with per-ETF tooltips. One fetch of the combined feed fills all three GVD stores, so switching among them is instant. Page title, `.universe-name` labels, and the per-stock popup's peer-group note all follow the active universe.
- **Methodology popup**: a "Good to know" sentence explaining the ETF universes and why the same stock can score differently against different peer groups.

### Changed

- **yfinance pinned to 1.4.1 in all four data workflows** (folded in from pipeline hardening). The S&P 500 job previously installed `--upgrade yfinance`, making runs non-reproducible.
- Saturday `constituents.yml` now also runs the ETF sync and regenerates the combined feed when any ETF list changes.
- Screener meta description now mentions all five universes (page title stays "Nasdaq 100 Screener", the canonical default view).
- Screener footer wording: constituent lists are "synced weekly", and may differ from "the current index or fund holdings".

### Removed

- The two-state "Expand to S&P 500" / "Back to Nasdaq 100" toggle button (replaced by the universe switcher).

### Notes

- Verified headlessly in Chrome against a local server: all five universes render fully scored (100/100 per GVD universe, 500/500 S&P) with correct titles, active buttons, and verdict counts.
- Roadmap: v3.30.0 International universe added (top 100 VXUS holdings only; deliberately its own release because VXUS reports unsuffixed local-exchange tickers, local currencies, and sparser analyst estimates). Considered and rejected: sourcing the S&P 500 list from VOO holdings (Vanguard data lags ~1 month; Wikipedia updates within days).

---

## v3.27.6 — 2026-07-03 — Search Console verified; sitemap submitted

**Docs only. The Search Console property for azqato.github.io/stocks/ is verified and sitemap.xml is submitted. Google shows "Couldn't fetch" pending its first crawl (normal for a new property; the sitemap serves HTTP 200 with application/xml). Roadmap item marked complete pending Google's fetch.**

---

## v3.27.5 — 2026-07-03 — Google Search Console verification tag

**The owner's google-site-verification meta tag added to the head of all 8 pages (after the canonical link), unblocking Search Console property verification and sitemap submission for the outstanding roadmap item.**

---

## v3.27.4 — 2026-07-03 — Roadmap: Search Console to #1; yfinance pinning folded into v3.28.0

**Docs only. The owner-only Google Search Console setup moves to the head of the queue (nothing gates it and its SEO benefit compounds from submission date). Pinning the yfinance version is folded into v3.28.0 (the Growth/Dividend universes release touches every data workflow anyway), leaving v3.29.0 as pipeline cleanup: delete the legacy FMP secret and reclassify data-files-in-git as intentional score-history design.**

---

## v3.27.3 — 2026-07-03 — Roadmap reordered (owner priority)

**Docs only. New queue order: v3.28.0 Growth/Dividend screener universes (VUG/VIG), v3.29.0 pipeline hardening, v4.0.0 score history sparklines, v4.1.0 deeper index fund coverage, v4.2.0 additional historical illustrative examples, v4.3.0 additional philosophy sections, v4.4.0 conference call research guide, then the outstanding owner-only Search Console setup. Email/RSS changelog removed from the roadmap entirely. Sub-items renumbered as MINOR versions (v4.1.0-v4.4.0 rather than v4.0.x patches) per this file's own semver rules: new pages and sections are MINOR bumps, PATCH is reserved for fixes.**

---

## v3.27.2 — 2026-07-03 — Roadmap: backtesting removed

**Docs only. All backtesting items removed from the roadmap by owner decision: the standalone "Historical screener performance backtest" milestone, the scoring-backtest half of v4.0.0, and the Future-list entry. The Explicitly Deferred section records the decision.**

---

## v3.27.1 — 2026-07-03 — Roadmap: Growth and Dividend screener universes planned

**Docs only. New planned milestone v3.30.0 added to the PRD roadmap: two additional screener universes, Growth (top 100 VUG holdings) and Dividend (top 100 VIG holdings), delivered as one combined feed file refreshing on trading days 30 minutes after the S&P 500 feed. Also marks the owner-only Google Search Console setup as Outstanding/paused.**

---

## v3.27.0 — 2026-07-03 — SEO/discoverability pass

**Sitemap, canonical URLs, structured data, and search-intent meta descriptions across the site. No visual or content changes; aimed at the PRD's 5,000/month organic search impressions target.**

### Added

- **sitemap.xml** at the repo root listing all 8 pages with lastmod dates.
- **Canonical `<link rel="canonical">` tags** on all 8 pages, pointing at the `azqato.github.io/stocks/` URLs (the home page canonicalizes to the trailing-slash root, not index.html).
- **FAQPage JSON-LD** on faq.html: all 34 questions with first-paragraph answers, generated from the live accordion markup so schema and visible content cannot drift. Makes the FAQ eligible for rich results.
- **WebSite JSON-LD** on index.html (site name, URL, author).

### Changed

- **Meta descriptions rewritten for search intent** on index, metrics, philosophy, faq, and indices (the old ones duplicated page leads; metrics' was 450+ characters). Screener, finviz, and seekingalpha descriptions were already appropriate and kept. Open Graph / Twitter descriptions unchanged (social copy is a different job).
- **FAQ count corrected from 31 to 34** in PRD.md and README.md; the accordion has grown across v3.24-v3.25 and the docs were never recounted.

### Notes

- **robots.txt intentionally not shipped:** this site lives at a subpath, and crawlers only read robots.txt at the domain root, so a copy in /stocks/ would be a dead file. Sitemap discovery is handled by direct Search Console submission instead.
- **Owner-only follow-ups:** (1) submit `https://azqato.github.io/stocks/sitemap.xml` in Google Search Console; (2) optionally add a `Sitemap:` line for it to the root `azqato.github.io` repo's robots.txt.

---

## v3.26.1 — 2026-07-03 — Columns dropdown order matches the table

**One-line fix: the screener's Columns visibility dropdown now lists the groups in on-screen order (Snapshot, Growth, Valuation, Balance Sheet) after v3.26.0 moved Snapshot to the front.**

---

## v3.26.0 — 2026-07-02 — Screener: Daily Change % column + column reorder

**The screener table gains a Daily Change % column and the display order now leads with the market snapshot. New order after Ticker/Verdict/Score/Factors: Mkt Cap, Price, Chg %, Rev TTM, Rev FWD, EPS TTM, EPS FWD, P/E FWD, PEG FWD, Total Cash, Total Debt, Cash/Debt, Updated.**

### Added

- **Daily Change % (`changePct`)**: `scripts/fetch_screener_data.py` now fetches the prior session's close (`regularMarketPreviousClose`, fallback `previousClose`) and writes `prevClose` and `changePct` into both feeds. Verified locally against live Yahoo data before shipping. The screener renders the new `Chg %` column (signed, green/red by direction, sortable via the existing sort path); stocks show "—" until a feed refresh includes the field.
- Both data workflows were triggered manually after deploy so the live feeds gain the field immediately rather than waiting for the next 23:00 UTC run.

### Changed

- **Column order (screener.html thead + screener.js rowHtml):** the Snapshot group (Mkt Cap, Price, Chg %) moved from the far right to directly after the Azqato Screen group; Growth, Valuation, and Balance Sheet follow unchanged; the per-row Updated age keeps a trailing slot (still governed by the Snapshot column toggle). Scoring, sorting semantics, and the per-stock popup are unchanged; Chg % is display-only and feeds nothing into the score.
- **docs/PRD.md:** screener.json data-model table gains `prevClose` and `changePct`; roadmap renumbered (SEO pass → v3.27.0, pipeline hardening → v3.28.0, score sparklines → v3.29.0) since this release took the v3.26.0 slot.

---

## v3.25.2 — 2026-07-02 — Roadmap: next three milestones committed

**Docs only. The next three milestones are now committed in order: v3.26.0 SEO/discoverability pass, v3.27.0 pipeline hardening, v3.28.0 screener score history sparklines.**

### Changed

- **docs/PRD.md roadmap:** three new planned milestone rows and a phase note. Pipeline hardening is scoped to pinning yfinance and deleting the legacy FMP secret; "move data files out of git" is dropped from the tech-debt plan because the sparklines feature (and the future backtest) mine that git history, making committed data feeds an intentional design choice.

---

## v3.25.1 — 2026-07-02 — Documentation alignment audit

**Post-rewrite audit of all four documentation files against the live site state. Docs only: no site changes.**

### Fixed

- **docs/PRD.md external FAQ:** "What are the 12 metrics?" no longer claims "the first 10 are tracked in the screener." It now states the accurate split: eight growth/valuation/balance-sheet metrics drive stock decisions (five scored by the screener), RSI and 52-Week Range time index/ETF purchases (context-only on stock watchlists), and the two margins are evaluated during research. "How do I use the site?" reworded to match.
- **docs/PRD.md version** bumped to 3.25.1. README.md and DESIGN.md audited; no changes required (no tech-stack, structure, or visual changes in v3.25.x).

---

## v3.25.0 — 2026-07-02 — Educational rewrite + technicals-for-indices doctrine

**Sitewide editorial rewrite targeting the "first-position investor" (owns 1-3 stocks or an index fund, knows the terms but cannot apply them), plus a methodology stance change: RSI and the 52-week range are now index/ETF timing signals only; individual stocks are valued on fundamentals and valuation, never technicals. Core logic, thresholds, numbers, and examples are unchanged. Content and docs only: no code, data, or design changes.**

### Changed

- **metrics.html (educational pass):** every metric now defines itself in plain English at first use, most with a worked example (P/E: $110 ÷ $5 = 22; PEG: 26 ÷ 32 = 0.81; gross margin: $100M sales / $20M cost = 80%). New "How the twelve fit together" intro box groups the metrics into five teams. Lead fixed from "Ten metrics" to "Twelve metrics" (matching the 12 Signals badge and FAQ). Jargon glossed at first use: buybacks, dilution, free cash flow, balance sheet, moat, consensus estimate, operating leverage, multiple.
- **metrics.html (doctrine):** RSI and 52-Week Range sections repositioned as index/ETF timing tools. All thresholds and levels unchanged; badge and table actions reframed from "initiate a position / review fundamentals" to "deployment window / index buys." Both caveats now explain the asymmetry: an index low usually reflects market-wide fear, a stock low can be deserved.
- **philosophy.html:** jargon-dense passages unpacked (price drivers caveat, hype-section "stretched multiple" mechanics, options/margin clocks); new "What to remember" takeaway box in the research section; switching costs and P/E glossed; "entry-timing signals" watchlist sentence reworded to valuation-based patience.
- **index.html:** strategy overview now states stocks are bought on fundamentals with technicals reserved for index timing (was "Entry timing is guided by RSI and 52-week range"); RSI/52W metric cards and reference-table rows relabeled "(index timing)"; Portfolio vs. Watchlist criteria rewritten from RSI/52W triggers to valuation triggers (PEG at/below target, P/E vs growth); market cap defined inline.
- **faq.html:** watchlist answer rewritten to valuation triggers; "Do you use technical analysis?" now answers "Not for individual stocks. Deliberately for indices and ETFs"; RSI answer scoped to index timing with stocks as context-at-most; ETF-difference answer aligned; protective puts glossed; missing paren fixed in the AAII answer.
- **indices.html:** three sentences tying RSI/52W to individual-stock entry timing reworded; the timing-signals section now states this page is where the two technical signals belong.
- **screener.html:** methodology popup closing note now explains the screener grades fundamentals only and technicals time index purchases (was a pointer to "entry timing" on the Metrics page).
- **finviz.html:** RSI and 52-Week Low filters reframed as optional context filters that surface beaten-down candidates for fundamental review, never buy criteria; Step 3 technical-view guidance rewritten accordingly.
- **seekingalpha.html:** new note after the 12-column table clarifying the two Technical columns are context, not stock decision inputs.
- **docs/PRD.md:** primary target user sharpened to the first-position investor profile; Tenet 3 revised from "The reader is motivated, not passive" to "Teach before asserting"; new enforced content rule for the technicals-for-indices doctrine; milestone row added.

### Notes

- Verified after each page: no em dashes introduced, all section IDs and anchors intact, every threshold/number byte-identical where logic was preserved (metrics.html tables verified byte-identical before the doctrine reframe of RSI/52W action labels).
- Voice decision record: teacher-first hybrid; inline definitions, worked hypothetical examples, analogies, and takeaway boxes applied where they fit; pages allowed to grow 20-40% where scaffolding earns it.

---

## v3.24.0 — 2026-07-02 — Protecting gains after a strong run

**Added a new "don't blow up your portfolio" theme (self-inflicted risk, escalation traps, forcing trades, structure as protection) and threaded it across the FAQ, home, philosophy, and indices pages. Content only: no code, data, or design changes.**

### Added

- **New FAQ question: "How do you avoid blowing up your portfolio after a big run?"** (faq.html, inserted before the conference-calls item, id `answer-blowup`). Covers the three self-inflicted-risk safeguards: diversify across growth/value/dividend types, refuse to escalate risk with margin or options after a win, and stay patient with new capital (let opportunities come to you, judge purchases on a decade horizon). Cross-links to the existing Growth/Value/Dividend and "staying on offense" answers.
- **New Philosophy section: "Do Not Blow Yourself Up"** (philosophy.html, id `section-protect`, inserted after "Stay on Offense", with a new "On This Page" nav link). Fullest treatment of the theme: the escalation trap, "do not force it," and structure as the real protection. Cross-links to the GVD section and the FAQ checklist.
- **Home page strategy paragraph** (index.html, "The Strategy" section) on self-inflicted risk after a run, cross-linking the FAQ and the new Philosophy section.
- **Indices caveat box** (indices.html, Dollar-Cost Averaging section) applying the same "do not escalate after a strong run" discipline to index/ETF exposure (no dumping earmarked lump sums, oversizing, or reaching for leverage), cross-linking the FAQ.

### Notes

- All additions use the site's editorial voice: hypothetical framing only, no live company examples, no real-time data, no em dashes.

---

## v3.23.0 — 2026-06-29 — Trading-day refresh schedule

**The automated data jobs now run only on trading days (Mon-Fri), and the weekly constituent sync moved to Saturday. Schedule housekeeping only: no change to the site, the scoring model, or the data format.**

### Changed

- **Screener feeds run Mon-Fri.** Both daily jobs (Nasdaq 100 at 23:00 UTC, S&P 500 at 23:30 UTC) now fire Monday through Friday only (`* * 1-5`). Weekends are skipped because the US market is closed and the figures do not move, so the prior Saturday/Sunday runs were redundant.
- **Constituent sync moved to Saturday 23:00 UTC.** `constituents.yml` previously ran Mondays at 06:00 UTC; it now runs Saturdays at 23:00 UTC, matching the time-of-day of the weekday feeds and landing on the one day those feed jobs are idle (so the shared `screener-data` concurrency group never contends).

### Notes

- `workflow_dispatch` (manual run) is unchanged on all three workflows, so any feed can still be regenerated on demand.
- GitHub cron is UTC-only and does not follow DST; the 23:00 UTC slot is ~6pm US Eastern in winter (EST), ~7pm in summer (EDT).

---

## v3.22.0 — 2026-06-29 — Expand to S&P 500

**The screener can now widen its universe from the Nasdaq 100 to the full S&P 500. A new "Expand to S&P 500" button (right of the Azqato label) lazy-loads a second daily feed and re-ranks every stock against the ~500-name index; clicking again returns to the Nasdaq 100. On-screen labels swap to match the active view.**

### Added

- **"Expand to S&P 500" toggle** in the screener app-bar (`#universeToggle`, right of the Azqato pill). First click lazy-fetches `data/screener_sp500.json`, swaps it into the table, and re-scores against the full S&P 500; the button then reads "Back to Nasdaq 100" and toggles instantly (both datasets are held in memory). Each universe has its own `localStorage` offline cache. If the S&P 500 feed hasn't been generated yet, the view stays on the Nasdaq 100 and the summary explains it'll appear after the next daily update.
- **Dynamic universe labels.** The brand heading, summary, methodology popup, disclaimer, and page title swap between "Nasdaq 100" and "S&P 500" via `.universe-name` spans as the view changes. SEO meta tags stay Nasdaq-100 (the canonical default page).
- **Second data feed + constituent list.** `data/sp500.json` (constituents, scraped from Wikipedia's "List of S&P 500 companies") and `data/screener_sp500.json` (the daily feed). Dotted tickers (`BRK.B`) are stored in display form and converted to Yahoo's dash form (`BRK-B`) at fetch time. The same dual-class rule used for the Nasdaq 100 (keep the Class A voting share) applies.

### Changed

- **Scoring note:** scoring remains relative to whichever set is loaded, so a stock's score shifts between the Nasdaq 100 and S&P 500 views — by design (it's a ranking). The methodology popup already says "computed across whichever stocks are currently loaded."
- **Pipeline generalized.** `fetch_screener_data.py` is now parameterized (`--list` / `--out`) instead of hardcoding the Nasdaq 100. `update_constituents.py` syncs both indices.
- **Staggered refresh so the Nasdaq 100 keeps priority.** The Nasdaq 100 feed refreshes at 23:00 UTC (unchanged); a new workflow refreshes the larger S&P 500 feed at 23:30 UTC, so the default view is never delayed by the ~500-symbol fetch. Both share the `screener-data` concurrency group so commits never race.

### Seeding (one-time)

- Because the S&P 500 feed is generated by CI, run the **"Update Constituents"** (or "Update Screener Data (S&P 500)") GitHub Action once via *workflow_dispatch* to create `data/sp500.json` + `data/screener_sp500.json`. Until then the button shows the "not available yet" message. Daily runs keep both feeds fresh afterward.

### Docs

- PRD (dual-feed data flow, toggle feature, new files), DESIGN (version history) updated.

---

## v3.21.0 — 2026-06-29 — Per-Stock Popup Shows Only Scored Metrics

**The per-stock breakdown popup now lists only the five metrics that actually feed the score. The two TTM "(context)" rows — Revenue Growth TTM and EPS Growth TTM — are removed so the popup reads as a clean scorecard.**

### Changed

- **Per-stock popup filtered to scored metrics only.** `openStock()` in `screener.js` now renders `POPUP_METRICS.filter(m => m.scored)`, dropping the two unscored context rows (Revenue Growth TTM, EPS Growth TTM). The `(context)` tag markup and the note's "(TTM growth is shown as context, not scored)" parenthetical were removed since they no longer apply. The TTM columns remain in the main screener table; only the popup changed.

### Docs

- PRD (per-stock popup), DESIGN (version history) updated.

---

## v3.20.0 — 2026-06-28 — Tighter Verdict Bands

**The screener's Pass/Watch/Fail thresholds are raised so the labels are more demanding. A median-on-everything stock (score 50) now sits at the very bottom of Watch rather than mid-Watch, and a clear majority of the index reads Watch or Fail.**

### Changed

- **Verdict bands recalibrated to Pass ≥ 80, Watch 50–79, Fail < 50** (was Pass ≥ 65, Watch 40–64, Fail < 40). Applied in `screener.js` to both `verdictOf()` (the PASS/WATCH/FAIL label) and `scoreColor()` (the green/amber/red score-cell color), and to the legend in `screener.html`. No data or scoring-math change — only the thresholds that map a score to a verdict.

### Docs

- PRD (verdict bands), DESIGN (version history) updated.

---

## v3.19.0 — 2026-06-28 — Mobile Hamburger Nav + Wider Popups

**The cramped wrapping top-bar nav on phones/tablets is replaced with a proper hamburger menu, and the screener popups are wider so they're easier to read.**

### Added

- **Mobile hamburger navigation** on all pages. Below 1024px the sidebar shows a ☰ button (top-right); tapping it drops the nav down as a full-width vertical list, and the icon becomes ✕. Pure CSS (a hidden checkbox + label toggle in `style.css`), so no JavaScript is needed and it works identically on the content pages and the screener. A `<input class="nav-toggle">` + `<label class="nav-burger">` were added to each page's sidebar.

### Changed

- **Methodology and per-stock popups widened** from a fixed 540px to **65% of the viewport** (max 1100px), with more padding; they go full-width below 900px. Much easier to read the tables and worked examples.

### Docs

- DESIGN (responsive table + version history) updated.

---

## v3.18.0 — 2026-06-27 — Extract Screener JS to `screener.js`

**Housekeeping. The screener's ~490 lines of inline JavaScript moved out of `screener.html` into a dedicated `screener.js`, addressing the "scoring lives in-HTML" technical debt. No behavior change.**

### Changed

- `screener.html` now loads `<script src="screener.js"></script>` instead of an inline `<script>` block. The page is markup + CSS; all logic (data loading, `computeScoreMap`, render, sort, the per-stock popup) lives in `screener.js`.

### Removed (tech debt closed)

- "Screener scoring in-HTML" debt resolved.
- The "`og-image.png` duplicated" debt entry was stale — `img/` contains only historical screenshots, no duplicate image. Cleaned up the docs accordingly.

### Docs

- PRD (folder structure, tech-stack JS line, tech-debt table) and README (tech stack, structure) updated for the new file.

---

## v3.17.0 — 2026-06-27 — Nasdaq 100 Constituent Auto-Sync

**The constituent list is now maintained automatically instead of by hand, and the screener derives its universe from the feed so there's a single source of truth.**

### Added

- `scripts/update_constituents.py` — fetches the live Nasdaq 100 from Wikipedia, applies the dual-class rule (keeps only the Class A voting share, e.g. GOOGL over GOOG), sanity-checks the result (count 90–105, valid tickers, no dupes), preserves existing curated short names, and rewrites `data/nasdaq100.json` only if membership changed (printing the add/remove diff).
- `.github/workflows/constituents.yml` — runs the sync weekly (Mondays 06:00 UTC) plus manual dispatch; if the list changed, it regenerates `data/screener.json` and commits both. Shares the data workflow's concurrency group so commits never race.

### Changed

- **`screener.html` now derives its ticker universe from the loaded feed** (`Object.keys(data)`) via a `universe()` helper, instead of a hardcoded array. `data/nasdaq100.json` → daily feed → page is now a single source of truth; the ~100-line embedded list was removed, eliminating the dual-list drift that previously let the constituents go stale.
- Ran the new sync: the list synced to the current index — **added** ALAB (Astera Labs), CRWV (CoreWeave), LITE (Lumentum), NBIS (Nebius), RKLB (Rocket Lab), SNDK (Sandisk), TER (Teradyne); **removed** VRSK, INSM, ZS, TEAM, CTSH, CHTR, CSGP. Regenerated the feed (100/100 populated).

### Docs

- PRD (folder structure, pipeline, tech-debt), README (project structure) updated.

---

## v3.16.0 — 2026-06-27 — Screener: Per-Stock Popup, GitHub-Direct Loading, FMP Removed

**A round of screener improvements: cell colors now track the relative score, clicking a row opens a per-stock breakdown, the data loads straight from GitHub (so it works locally), and the bring-your-own-key Financial Modeling Prep path was removed entirely.**

### Added

- **Per-stock breakdown popup.** Clicking any row opens a focused modal for that stock: each metric's value, its percentile rank vs the Nasdaq 100, and its 0–20 points, color-coded, with the total score and verdict. Reuses the existing modal component (`openStock()` / `#stockModal`).
- **Offline cache.** The last successfully fetched feed is stored in `localStorage` and shown instantly on load (and as a fallback if the network is down).

### Changed

- **Cell colors now track the relative percentiles**, not absolute thresholds: green = top quartile on that metric, red = bottom quartile, amber = the middle half, gray = no data. The TTM growth columns are ranked for color only (they still don't feed the score). `computeScoreMap()` now also returns per-metric percentiles (`pctiles`) for the popup, and a generic `colorFromPts()` replaced the old `cls*` threshold functions.
- **Data loads directly from GitHub.** The screener fetches `raw.githubusercontent.com/.../data/screener.json` first (CORS-enabled, so it works even when `screener.html` is opened as a local `file://`), falling back to the same-origin copy, then the localStorage cache. Always shows the latest published feed.
- **Sort:** a negative forward P/E or PEG now sorts like a high (expensive) value rather than a cheap one, so unprofitable names group with the worst, matching their red cells and zero score.

### Removed

- **Financial Modeling Prep bring-your-own-key loader**, the Settings modal, the API-key input, the "Load Data" / "Refresh with your API key" buttons, the progress bar, and all related code (`loadData`, `fetchJson`, `nearestForwardPair`, etc.). The screener is now purely the cached daily feed — nothing to configure. The legacy `FMP_API_KEY` GitHub Actions secret is unused and can be deleted.

### Docs

- `docs/PRD.md`, `README.md`, and `docs/DESIGN.md` updated to drop all FMP/bring-your-own-key references and describe the GitHub-direct loading, percentile colors, and per-stock popup.

---

## v3.15.4 — 2026-06-27 — Negative Forward P/E Cell Now Renders Red

**Color fix in the screener table. A negative forward P/E was rendering green (because `peFwd < epsFwd` is trivially true when P/E is negative). `clsPe()` now returns red for any forward P/E ≤ 0.**

### Fixed

- `screener.html` `clsPe()`: forward P/E ≤ 0 colors the P/E FWD cell red instead of green/default, matching how the scoring treats unprofitable names (e.g. INSM, GILD, WBD).

---

## v3.15.3 — 2026-06-27 — Shrinking Forward Earnings Now Rank Worst on P/E vs Growth

**The "P/E vs Growth" factor previously dropped (excused) a company whose forward EPS growth was ≤ 0. It now ranks those companies worst, consistent with how unprofitable (negative P/E) names are handled.**

### Fixed

- `screener.html` `computeScoreMap()`: the "P/E vs Growth" metric returns `Infinity` (worst rank) when forward EPS growth is ≤ 0, instead of `null` (dropped/rescaled). A company with shrinking expected earnings no longer gets a free pass on that factor.
- Impact: 7 profitable-but-declining names were re-scored — PDD 61 → 49, PYPL 40 → 32 (Watch → Fail), QCOM 36 → 29, BKR 23 → 18, CPRT 25 → 20, KHC 25 → 20, GILD 7 → 6. Other names shifted +1 to +3 from the percentile reshuffle. Verdict spread Pass 37 / Watch 24 / Fail 39.
- Documented in the Methodology popup note and `docs/PRD.md` scoring metric table.

---

## v3.15.2 — 2026-06-27 — Negative-P/E Fix Extended to PEG

**Follow-up to v3.15.1. The PEG factor had the same unprofitable-company flaw: Yahoo's `pegRatio` reports a positive (cheap-looking) PEG even when forward earnings are negative, so INSM was still scoring near-top on PEG.**

### Fixed

- `screener.html`: when forward P/E ≤ 0, the **PEG metric now ranks worst** in scoring (same `Infinity` sentinel as P/E vs Growth), regardless of Yahoo's reported value.
- **Display:** for those unprofitable names the PEG column now shows our own forward PEG (`peFwd / epsFwd`, a negative number) instead of Yahoo's misleading positive, via the new `pegDisplay()` helper. The negative value renders red automatically, so display and score now agree.
- Impact: INSM's PEG shows ≈ −0.66 and scores 0, dropping its total from 79 to **60 (now Watch, was Pass)** — the honest grade for a pre-profit, hyper-growth name (scored on its real strengths: revenue growth and balance sheet). Only INSM affected; ±1 reshuffle elsewhere.
- Documented in the Methodology popup note and `docs/PRD.md` scoring metric table.

---

## v3.15.1 — 2026-06-27 — Fix: Negative P/E No Longer Scores Best

**Bug fix in the relative scoring model. A negative forward P/E (an unprofitable company) was ranking as the cheapest possible on the "P/E vs Growth" metric and earning full marks, when it should rank worst.**

### Fixed

- `screener.html` `computeScoreMap()`: the "P/E vs Growth" value function now returns `Infinity` (worst rank) when forward P/E is ≤ 0, instead of a negative ratio that sorted to the best end. "Cheap relative to earnings" has no meaning when there are no earnings, so unprofitable names now land at the bottom of that metric.
- Impact on the current feed: only INSM (Insmed, negative forward P/E) was affected — its score drops from 99 to 79 (still a Pass on its real strengths: ~178% revenue growth, healthy cash/debt, mid PEG). About 20 other stocks shifted by ±1 from the percentile reshuffle; the Pass/Watch/Fail spread is unchanged.
- Documented in the Methodology popup (a note under the metrics table) and `docs/PRD.md` (scoring model metric table).

---

## v3.15.0 — 2026-06-27 — Relative Percentile Scoring Model

**The screener's scoring model changed from absolute thresholds to a relative, percentile-based ranking. Each stock is now graded against its Nasdaq 100 peers rather than against fixed cut-offs.**

### Changed

- `screener.html`: replaced the absolute `score()` (five factors with fixed thresholds, each scaled 0–20) with `computeScoreMap()`, which ranks every loaded stock on each of the five forward metrics (Revenue Growth FWD, EPS Growth FWD, P/E vs EPS Growth, PEG FWD, Cash vs Debt) and converts the percentile rank to points: `points = clamp(40 × (percentile − 0.25), 0, 20)` — bottom quartile scores 0, the median 10, the top quartile 20. The five sum to a score out of 100, rescaled across whichever metrics a stock has. `rows()` now reads from the precomputed map.
- Verdict bands recalibrated for the new distribution: **Pass ≥ 65, Watch 40–64, Fail < 40** (was 70 / 40).
- Methodology popup rewritten to explain the relative/percentile model, the percentile-to-points curve, and a worked example (Apple's PEG); the old absolute worked examples (AMD/AAPL point tables) were removed. Settings "How stocks are scored" pointer updated. Kept em-dash-free per the content rules.
- `docs/PRD.md` (to v3.1): Screener Scoring Model section rewritten for v3.15; feature list, External FAQ #7, roadmap line, milestone table, internal data-flow step, and known-technical-debt entry updated.
- `docs/DESIGN.md`: version-history row added.

### Notes

- No data change — scoring is computed client-side from the existing feed. Live calibration: Pass 36 / Watch 25 / Fail 39; top names WDC, NVDA, MU at 100, INSM 99, META 95; bottom WBD, EXC, CMCSA, CCEP at 0.
- Trade-off, documented in the popup and PRD: scores are now peer-relative, so a stock's grade can move when *other* companies' numbers change, and roughly the bottom third of the index always lands in Fail. The educational methodology pages (absolute thresholds such as PEG < 1) are unchanged; only the screener tool's scoring is relative.

---

## v3.14.0 — 2026-06-27 — Documentation Consolidation Audit

**Full documentation audit and consolidation. All prior docs merged into four canonical files: README.md (root), docs/PRD.md, docs/DESIGN.md, and docs/PATCHNOTES.md. Every file rewritten to reflect the current state of the codebase at v3.13.0.**

### Added

- `docs/PRD.md` rewritten from v2.0 to v3.0: added Problem Statement, Target Users, Goals, Non-Goals, User Stories, Feature List (MVP/Future), Constraints, Assumptions, Success Criteria, Tenets (7), Roadmap (milestone table), Metrics (north star + acquisition + engagement + retention + performance), Runbook (local setup, build, deploy, pipeline, rollback, common errors, monitoring), Technical Requirements (architecture, tech stack, folder structure, data models, API design, scoring model, state management, third-party integrations, performance requirements, known technical debt), Security (authentication, authorization, data storage, environment variables, third-party trust, attack surface, dependency policy), Press Release, External FAQ (25 questions), Internal Stakeholder FAQ, Site Structure Reference (section IDs table, concept inventory), and Documentation Process guide
- `docs/DESIGN.md` rewritten from v1.1 to v2.0: added Spacing System, Breakpoints, Modals component, complete Social Cards section (with per-page values table and og-image regeneration snippet), Content Philosophy enforcement rules, updated CSS File Structure map, and brought Version History current through v3.13.0
- `README.md` rewritten: added Tech Stack table, Prerequisites, Installation steps, Running Locally note (screener requires local server), Environment Variables table, Build and Deploy section, and annotated Project Structure tree

### Changed

- `README.md`: restructured for developer audience; removed marketing language; added explicit note that screener requires a local server for JSON fetch; added full annotated directory tree
- `docs/PRD.md`: consolidated all previously separate sections (social cards, OG meta tags, concept tracking table, nav label rules, section ID maps, content philosophy rules) that were scattered across PRD.md sections into a unified reference document
- `docs/DESIGN.md`: consolidated all design rules, social card specs, and content philosophy into a single coherent spec; removed redundant version-history entries that were already in PATCHNOTES.md
- `docs/PATCHNOTES.md`: no content changes to existing entries; this entry added at top

### Removed

- Nothing deleted from the codebase; only documentation restructured

### Notes

Going forward, all documentation changes must be reflected in PATCHNOTES.md as a versioned entry. PRD.md is the single source of truth for product requirements, architecture, and process. DESIGN.md is the single source of truth for visual and UX decisions. README.md is the developer entry point. If information belongs in one of these four files, it does not belong anywhere else.

---

## v3.13.0 — June 2026 — "Methodology" Popup on the Screener

**Added a Methodology button to the screener toolbar that opens a plain-language popup explaining exactly how the score is calculated.**

- New **📊 Methodology** button in the toolbar (next to Settings), opening a modal that reuses the existing `.modal-backdrop` / `.modal` component
- Content: the five factors and their point rules (as a table), what P/E / PEG / Cash-vs-Debt mean and the sliding-scale formula in beginner terms, two fully worked examples (AMD = 84 Pass, AAPL = 45 Watch), the Factors-chip definition, and the missing-data rescaling rule. Uses the site's verdict badges and table styling
- The Settings modal's "How stocks are scored" section was slimmed to a one-line pointer to the new popup (no more duplicated explanation)
- Standard modal behavior: close button, click-outside, and Escape (Escape now closes either modal)

---

## v3.12.0 — June 2026 — New Screener Scoring Model (5 Factors, Granular, /100)

**Replaced the screener's 7-factor pass/acceptable/weak score with a leaner, granular 5-factor model. The two trailing (TTM) growth factors were dropped; each of the five remaining forward-looking factors now scores continuously 0–20, summing to 100.**

### The model (`score()` in `screener.html`)

Each factor is worth up to 20 points, scaled granularly (not bucketed):

1. **Revenue Growth FWD** — 1 pt per 1% of growth, capped at 20 (20%+ = full)
2. **EPS Growth FWD** — 1 pt per 1% of growth, capped at 20
3. **P/E FWD vs EPS Growth** — `20 × (2 − r) / 1.5`, r = P/E ÷ growth%; full at r ≤ 0.5, zero at r ≥ 2.0
4. **PEG FWD** — `20 × (2 − PEG) / 1.5`; full at PEG ≤ 0.5, zero at PEG ≥ 2.0
5. **Cash vs Debt** — `20 × (cash/debt) / 1.5`; full at cash ≥ 1.5× debt (or no debt), ~13 at cash = debt, zero as debt dominates

Total = sum → 0–100. If a metric is missing, that factor is dropped and the rest are rescaled to /100.

### Changes

- **Dropped Revenue Growth TTM and EPS Growth TTM from scoring** (they remain visible as columns, just no longer scored)
- **Verdict bands** changed to fit the new distribution: **Pass ≥ 70, Watch 40–69, Fail < 40** (was 80/60)
- **Factors chip** redefined: count of factors scoring strong (**15+/20**) out of those graded; header tooltip added
- Settings "How stocks are scored" text rewritten to describe the granular model
- No data change — scoring is computed client-side from the existing feed. Calibration on the live 100: Pass 27 / Watch 33 / Fail 40; examples MU 100, NVDA 99, TEAM 91, META 88, AMD 84, AAPL 45 (Watch), COST 37 (Fail)

---

## v3.11.0 — June 2026 — P/E FWD and PEG FWD Now Track Seeking Alpha (Direct Yahoo Fields)

**A yfinance coverage probe found that Yahoo exposes purpose-built fields that match Seeking Alpha better than our computed values. Switched P/E FWD and PEG FWD to those fields.**

### Pipeline (`scripts/fetch_screener_data.py`)

- **P/E FWD** → now uses Yahoo's `priceEpsCurrentYear` (price ÷ current-FY EPS), which matches Seeking Alpha **to the cent** (NVDA 21.48, META 17.10, AMD 70.65, ADBE 8.30, GOOGL 23.73, TEAM 14.30). Falls back to `price ÷ 0y estimate`, then `forwardPE`
- **PEG FWD** → now uses Yahoo's `pegRatio` (which incorporates a longer-term growth rate, à la Seeking Alpha's PEG), falling back to `trailingPegRatio`, then the 1-yr forward PEG. Lands within ~0.1 of SA (e.g. META 0.80 vs 0.82, NOW 0.95 vs 0.96). SA's exact 3–5yr long-term growth input is not exposed by yfinance, so this is the closest available
- **EPS Growth FWD** → unchanged (current-FY GAAP-basis growth). Per the chosen approach, it is now **labeled** rather than re-sourced: SA's Non-GAAP forward EPS growth is not available from yfinance
- Regenerated `data/screener.json` (100/100, no missing P/E or PEG)

### Screener UI (`screener.html`)

- The **EPS FWD** column header is marked with `*` and a tooltip: "GAAP-basis forward EPS growth … may differ from Seeking Alpha, which uses Non-GAAP consensus"
- Footer disclaimer corrected: the daily feed is **Yahoo Finance** (it previously still credited Financial Modeling Prep, which is now only the manual bring-your-own-key fallback), and it notes the forward-figure basis and the EPS-growth GAAP caveat

### Probe takeaways (for the record)

- Yahoo's `LTG` (long-term growth) row is `NaN` for essentially all tickers — the raw 3–5yr rate cannot be shown — but `pegRatio` bakes it in and is a good proxy
- The forward EPS *level* from Yahoo is effectively Non-GAAP (hence P/E matches SA), but there is no Non-GAAP trailing *base* to reproduce SA's EPS growth *rate* without a second data source

---

## v3.10.0 — June 2026 — Consolidate Dual-Class Listings (GOOG → GOOGL)

**Removed the duplicate Alphabet listing so each company appears once. The screener now holds 100 tickers (was 101).**

- Removed **GOOG** (Alphabet Class C, non-voting); kept **GOOGL** (Alphabet Class A, voting), renamed to "Alphabet (Class A)"
- Established a **multi-class rule**: when a company has more than one share class in the index, the screener lists only the **Class A voting** shares. Documented in `README.md` (data files) and `docs/PRD.md` (Screener page)
- Synced all three sources — `data/nasdaq100.json`, the embedded fallback list in `screener.html`, and the generated `data/screener.json` — to the identical 100-ticker set

---

## v3.9.0 — June 2026 — Forward Metrics Aligned to Seeking Alpha's Current-Year Basis

**Fixed the screener's forward valuation/growth figures to match Seeking Alpha. The pipeline was reading the wrong forward period — yfinance's `forwardPE` / "+1y" rows, which look one fiscal year further out than Seeking Alpha's "FWD" convention — so P/E FWD (and the growth figures) read systematically low.**

### The fix (`scripts/fetch_screener_data.py`)

- **P/E FWD** now = `price ÷ current fiscal-year ("0y") EPS estimate` (falls back to `forwardPE` only if the estimate is unavailable). Previously used yfinance `forwardPE`, which divides by the *next* fiscal year's EPS
- **Revenue Growth FWD** and **EPS Growth FWD** now use the current-FY ("0y") consensus growth instead of the "+1y" row
- **PEG FWD** continues to be computed as forward P/E ÷ forward EPS growth %, now on the corrected current-year basis (still a 1-year PEG — see caveat below)
- Added an `estimate_avg()` helper; documented the convention in the script docstring

### Verification vs the Seeking Alpha screenshot

P/E FWD now matches almost exactly: NVDA 21.48 (was 15.1), AMD 70.65 (was 39.6), ADBE 8.30 (was 7.4), GOOGL 23.73 (was 23.2), TEAM 14.30 (was 12.7). Revenue Growth FWD moved much closer to SA across the board. Regenerated `data/screener.json` (101/101 populated) with the corrected values.

### Known remaining gaps (not addressed here)

- **EPS Growth FWD** still differs from SA because SA uses **Non-GAAP** consensus EPS while yfinance exposes a GAAP-basis figure; the forward EPS *level* matches (hence P/E matches), but the growth *base year* differs. yfinance has no Non-GAAP consensus to close this
- **PEG FWD** differs because SA divides forward P/E by a **3–5yr long-term growth CAGR**, not the 1-year growth; yfinance's long-term-growth field is usually empty
- **Total Cash / Total Debt** already matched SA and were unchanged

---

## v3.8.0 — June 2026 — Cash/Debt Ratio Column on the Screener

**Added a sortable Cash/Debt ratio to the Balance Sheet column group in `screener.html`, sitting after Total Cash and Total Debt.**

- New **Cash/Debt** column shows `cash ÷ debt` as a multiple (e.g. `4.15x`). Click the header to sort like any other column
- Color-coded to the methodology's balance-sheet thresholds: green when cash ≥ debt (ratio ≥ 1.0), amber when debt is under 3× cash (ratio > 0.33), red when debt exceeds 3× cash (ratio ≤ 0.33)
- Zero-debt companies (e.g. ISRG) show `∞` and sort to the top. The sort comparator was updated to treat `Infinity` as a valid high value rather than missing data; missing values still sink to the bottom
- Belongs to the existing **Balance Sheet** column group, so the Columns toggle shows/hides it alongside Total Cash and Total Debt. Group header colspan and header/body cell counts kept in sync (16 columns)

---

## v3.7.0 — June 2026 — Screener Data Pipeline Moved to yfinance + Nasdaq 100 Constituent Fix

**The screener's daily data pipeline was switched from Financial Modeling Prep to yfinance, which fixed both a coverage bug and a wasted-quota bug. The constituent list was also fact-checked against authoritative sources and corrected — most notably, NVIDIA (the largest component) had been missing.**

### Why the change

FMP's free tier only serves a small subset of symbols. A manual workflow run revealed the problem: of ~50 symbols attempted, only ~7 returned data and the rest came back `HTTP 402 "this symbol is not available under your current subscription"`, each burning an API call (71 calls for 7 populated rows). Throttling could not fix this — the blocked symbols are simply unavailable on the free plan.

### New pipeline (yfinance)

- `scripts/fetch_screener_data.py` — Python 3.12 script using `yfinance` (public Yahoo Finance data). No API key, no per-symbol subscription limits, so **all constituents refresh every run**. Maps Yahoo fields to the same `data/screener.json` schema: price/market cap, total cash/debt, TTM revenue & earnings growth, forward P/E, and forward revenue/EPS growth + PEG from the `+1y` analyst estimates. Per-symbol retries and a polite delay between symbols
- `.github/workflows/screener-data.yml` — now runs `setup-python` + `pip install yfinance` + the Python script (was Node + FMP). Same daily cron (23:00 UTC), same commit-and-push of `data/screener.json`. **No secret required** — the `FMP_API_KEY` secret is no longer used by the pipeline and can be deleted
- Removed the superseded Node fetcher `scripts/fetch-screener-data.mjs`
- The in-browser "Load Data" (bring-your-own-key) path in `screener.html` still uses FMP as a manual fallback; it inherits FMP's free-tier symbol limitation, but it is now secondary since the daily feed covers everything

### Nasdaq 100 constituent fix

- Fact-checked `data/nasdaq100.json` against stockanalysis.com and Wikipedia. Rebuilt it to match the authoritative current index (101 tickers = 100 companies + GOOGL/GOOG dual class)
- **Added (were missing):** NVDA (NVIDIA — the largest component), WMT, SHOP, STX, WDC, FER, ALNY, AXON, INSM, MPWR, TRI
- **Removed (no longer in the index):** ANSS (acquired/delisted), AZN, BIIB, CDW, GFS, LULU, MRNA, ON, SMCI, TTD
- Kept the page's embedded fallback list (`screener.html`) in sync with `data/nasdaq100.json`; verified all three (canonical list, embedded list, generated feed) hold the identical 101 tickers
- Committed a freshly generated `data/screener.json` (101/101 symbols populated) so the screener shows full data immediately

### Infra

- `.gitignore`: removed `finviz.html` (it is now an active page, not an orphan) and added `__pycache__/`

### Docs

- `README.md`, `docs/PRD.md`, `docs/DESIGN.md` updated to describe the yfinance pipeline and the corrected constituent list

---

## v3.6.0 — June 2026 — Navigation: Screener in Nav, Relabeled Links, Shared Sidebar in the App

**The interactive screener is now part of the site navigation, the two setup-guide links were relabeled to their destinations, and the screener app adopted the shared site sidebar so it navigates like every other page.**

### Navigation label changes (all pages)

- Sidebar nav label **"Screener" → "Finviz"** (points to `finviz.html`, the Finviz setup guide)
- Sidebar nav label **"Watchlist" → "SeekingAlpha"** (points to `seekingalpha.html`, the Seeking Alpha setup guide)
- Labels only; hrefs were already correct from v3.5.0

### Screener added to the nav

- New sidebar item **"Screener" → `screener.html`** (the interactive Nasdaq 100 screener), inserted **after Metrics** on all pages
- Nav order is now: Home → Philosophy → Metrics → Screener → Finviz → SeekingAlpha → Indices → FAQ → Leveraged Strategies → Support (10 items)

### Screener app uses the shared sidebar

- `screener.html` replaced its custom top-bar navigation with the standard site sidebar (same brand, nav, and footer as every other page; the **Screener** item is marked active)
- The app keeps a slim header inside the main column: title + `Azqato` screen pill + "as of" timestamp + symbol filter (the old in-bar nav links were removed)
- Layout wrapped in the standard `.site-wrapper` / `.site-layout` grid; the dense table and toolbar live in a `<main class="app">` column
- Added a `max-width: 1023px` CSS override so that when the shared sidebar collapses to a top bar on mobile, the app flows and scrolls with the page (the table area caps at `80vh`) instead of being locked to `100vh`

### Link audit (post-rename verification)

- Swept every page: all internal `.html` link targets resolve to existing files, all anchor targets (`#…`) exist in their pages, and no stale names remain (`watchlist.html`, `screenapp.html`, `guide.html`, `indexes.html`)

### Docs

- `docs/PRD.md`: page table adds the Screener app; Navigation Order and nav-label rule updated; success-criteria page/item counts updated (8 pages, 10 nav items); "On This Page" note records that the Screener app has no section block
- `docs/DESIGN.md`: version-history row v3.6 added

---

## v3.5.0 — June 2026 — Page Renames (Finviz / Seeking Alpha / Screener)

**Three pages renamed to clearer, destination-named files, with every reference updated sitewide. No content or layout changes — purely filenames and the links/metadata that point to them.**

> Note on history: earlier entries below are left unchanged on purpose. They are an accurate changelog of what each release touched at the time (e.g., v1.5 created `screener.html` and `watchlist.html`; a still-earlier rename moved `finviz.html` → `screener.html`). This entry records the current renames rather than rewriting that history.

### Renames

| Old name | New name | What it is |
|----------|----------|------------|
| `screener.html` | `finviz.html` | Finviz stock screener setup guide |
| `watchlist.html` | `seekingalpha.html` | Seeking Alpha 12-column watchlist setup guide |
| `screenapp.html` | `screener.html` | Interactive Nasdaq 100 screener (introduced in v3.4.0) |

Renames were performed with `git mv` (history preserved). Reference updates were applied in order — `screener.html` → `finviz.html` first, then `screenapp.html` → `screener.html` — so the reused `screener.html` name never collided.

### References updated

- **All HTML pages:** sidebar nav hrefs (`Screener` → `finviz.html`, `Watchlist` → `seekingalpha.html`), cross-links, faq/teaser links, `og:url` / canonical metadata, and the active-page marker on the renamed guide
- **Interactive screener (`screener.html`, formerly `screenapp.html`):** `og:url` updated; its in-app "Finviz Guide" link now points to `finviz.html`. The data feed path (`data/screener.json`) is unchanged
- **Data pipeline:** header comment in `scripts/fetch-screener-data.mjs` updated. The workflow and `data/screener.json` filename were unaffected (no `.html` references)
- **Docs:** `README.md` pages table and Content Philosophy carve-out; `docs/PRD.md` page tables, section headers (3.4 Finviz Setup, 3.5 Seeking Alpha), `og:url` table, and anchor map; `docs/DESIGN.md` version history (v3.4 and v3.5 rows added)

### Nav note

Nav labels are unchanged. The "Screener" nav item points to `finviz.html`, and the interactive screener at `screener.html` deliberately remains out of the nav (per request). Adding a nav entry for it is a future step.

---

## v3.4.0 — June 2026 — Interactive Nasdaq 100 Screener (`screenapp.html`) + Daily Data Pipeline

**New interactive tool that rates every Nasdaq 100 company against the methodology factors, scored and ranked in the browser. Ships as a new standalone page (`screenapp.html`) plus an optional zero-config data pipeline: a daily GitHub Action regenerates `data/screener.json` so the public page shows live data with no setup. A bring-your-own-key loader (Financial Modeling Prep) remains available as a manual refresh and as the fallback whenever the published data is more than 24 hours old. The existing `screener.html` Finviz guide is unchanged.**

> Scope / content-philosophy note: the site's editorial content uses hypothetical examples only (no real-time data). This addition is an interactive *tool*, not editorial copy — it presents live third-party metrics that are clearly labeled, timestamped ("as of"), opt-in, and carry an educational-use disclaimer. The distinction (hypothetical teaching content vs. a labeled live tool) is intentional and documented in README's Content Philosophy.

### New file: `screenapp.html`

- Full-width dense screener modeled on the Screener3000 layout (top bar with brand + `Azqato` screen pill + "as of" timestamp + symbol filter; toolbar with verdict filter chips, a Columns group toggle, Settings, and Load Data; grouped sticky header — Azqato Screen / Growth / Valuation / Balance Sheet / Snapshot; sortable columns; sticky ticker column), styled with the site's existing `style.css` tokens (teal `#00d4a0`, `#0d1117` bg, SF Mono numerics, badge styles)
- **Scoring** — seven factors drawn from the "What Strong Metrics Look Like" reference table: Revenue Growth TTM, Revenue Growth FWD, EPS Growth TTM, EPS Growth FWD, P/E FWD vs EPS Growth % (primary signal), PEG FWD, and Cash vs Debt. Each factor scores 2 (strong) / 1 (acceptable) / 0 (weak); the score is the percentage of available points earned. Verdicts: Pass (80%+), Watch (60–79%), Fail (under 60%), plus a `passes/total` factor chip
- Columns: Ticker, Verdict, Score, Factors, Rev TTM, Rev FWD, EPS TTM, EPS FWD, P/E FWD, PEG FWD, Total Cash, Total Debt, Price, Mkt Cap, Updated. Cell coloring keyed to the methodology thresholds
- "Updated" column shows the age of each ticker's data (sortable; tooltip breaks out the price vs. fundamentals timestamps; flagged when over 8 days old). Per-ticker timestamps are written by both the pipeline and the bring-your-own-key loader
- Filter chips (All / Pass / Watch / Fail with live counts), client-side symbol/name search, click-to-sort headers, and a Columns dropdown to show/hide the Growth / Valuation / Balance Sheet / Snapshot groups
- **Data sources, in priority order:** (1) the published `data/screener.json` feed if present and current; (2) the user's own most-recent bring-your-own-key pull (stored in `localStorage`); whichever is newer wins
- Bring-your-own-key loader uses the Financial Modeling Prep **stable** API (the legacy `/api/v3/` endpoints were retired by FMP on 2025-08-31). Per symbol: quote, balance-sheet, financial-growth, analyst-estimates (4 requests). Concurrency pool, incremental save to `localStorage` (resume across days), progress bar, and graceful handling of auth (401/403), rate-limit (429), and premium (402) responses including FMP's JSON-object and plain-text error bodies. Defaults to 60 symbols per run to stay under the free tier's 250 requests/day
- Stale-data banner: when the active data is more than 24 hours old, a banner surfaces the "Refresh with your API key" action. API key and pulled data live only in the browser's local storage

### New: daily data pipeline (zero-config public data)

- `scripts/fetch-screener-data.mjs` — dependency-free Node 20 script (global `fetch`, no `npm install`). Each run **fully refreshes a rotating slice of the stalest symbols, oldest-first** — a full refresh is 4 requests/symbol (quote, balance-sheet, financial-growth, analyst-estimates). At the default `DAILY_COUNT=50` that is ~200 requests/run, under the 250/day free limit, cycling the whole 100-name list every ~2 days. Ordering is by the *stalest* of each symbol's two timestamps (never-fetched first). Writes `data/screener.json`; stops gracefully and saves progress on rate-limit/auth/budget (`REQ_BUDGET=240` ceiling)
- `.github/workflows/screener-data.yml` — daily cron at **23:00 UTC (6:00pm US Eastern / EST in winter; 7:00pm in summer, since GitHub cron does not follow DST — use `0 22 * * *` for 6:00pm during summer)** plus manual `workflow_dispatch` (with a `daily_count` input for larger backfills). Reads the `FMP_API_KEY` repo secret, runs the script, and commits `data/screener.json` when it changes (`contents: write`, concurrency-guarded)
- `data/nasdaq100.json` — canonical Nasdaq 100 constituent list (ticker + name) read by the script; the page keeps an embedded copy as a structural fallback. Both are static and may differ from the live index; edit as the index reconstitutes
- `data/screener.json` — generated data feed. Committed initially as an empty placeholder (`{ "updated": null, "stocks": {} }`) so the page does not 404 before the first Action run

### README.md changes

- Pages table: added `screenapp.html` row; added `data/` and `scripts/` rows for the pipeline
- Content Philosophy: added a carve-out distinguishing the hypothetical editorial content from the new labeled, opt-in live screener tool

### Setup required (one-time, by the site owner)

- Add the FMP API key as a GitHub repository secret named `FMP_API_KEY` (Settings → Secrets and variables → Actions). Until then, the page still works via the bring-your-own-key loader. Rotate any key that has been shared in plaintext

---

## v3.3.0 — June 2026 — DCA and Lump-Sum Investing Sections (Indices Page)

**Two new sections added to `indices.html` covering how to time getting cash into the market: Dollar-Cost Averaging and Lump-Sum Investing. Placed between "Types of Index Funds" and "Fundamentals vs. Technicals." Focus on broad-market vehicles VT and VTI + VXUS. Related FAQ entry and documentation updates.**

> Scope note: the request named `index.html`, but the two anchor sections it referenced ("Types of Index Funds" and "Fundamentals vs. Technicals") exist only on `indices.html`, and the content (VT, VTI + VXUS, broad-market timing) is index/ETF material. The sections were therefore added to `indices.html`, the only page where the placement is executable.

### indices.html changes

- Added sidebar "On This Page" links: `Dollar-Cost Averaging` (`#section-dca`) and `Lump-Sum Investing` (`#section-lumpsum`), placed between Types of Index Funds and Fundamentals vs. Technicals
- New section `#section-dca` — **Dollar-Cost Averaging**: DCA defined; VT and VTI + VXUS presented as the broad-market vehicles in a two-card grid; why broad funds are ideal DCA vehicles (the what-to-buy question is already solved); a "why DCA is the right default for most investors" how-to-read list (removes emotion, removes timing, matches paycheck investing, builds the habit); explicit statement that this holds regardless of the page's timing signals (regular contributions should not be paused waiting for fear); caveat box on terminology (paycheck investing is closer to repeated small lump sums than formal DCA)
- New section `#section-lumpsum` — **Lump-Sum Investing**: LSI defined; the on-average superiority of LSI (Vanguard: ~2/3 of the time over a 12-month window, ~90% at 36 months) because markets trend up and money invested sooner compounds longer; how-to-read list (the math, the timing/regret risk, who it is best for); H3 "Do not hold cash as dry powder" (waiting for a dip underperforms; reconciles the VIX/AAII signals as tools for deploying earmarked cash, not for indefinite cash-holding); H3 "The hybrid approach" (invest 1/2 to 1/3 now, DCA the rest over 3-6 months, keep the window short); bottom-line caveat box

### faq.html changes

- Added question "Should I invest all at once or spread it out over time?" (`answer-dca`, placed after the leveraged ETF question). Covers DCA as the default for income-stream investing, LSI superiority for a one-time pool, the hybrid, the dry-powder trap, and reconciliation with the VIX/AAII signals. Links to `indices.html#section-dca` and `indices.html#section-lumpsum`.

### docs/PRD.md changes

- Section 3.6 (Indices & ETF Investing): Dollar-Cost Averaging and Lump-Sum Investing added to the sections list with descriptions
- Section 3.7 (FAQ): new question 13 (DCA vs lump sum) documented
- Section 5 (On This Page): `#section-dca` and `#section-lumpsum` added to the indices.html row
- Section 7 concept tracking table: new rows for DCA, LSI/dry-powder/hybrid, and the VT / VTI + VXUS vehicles

### docs/DESIGN.md changes

- Section 14 (Version History): v3.3 entry added

### README.md changes

- Pages table: `indices.html` row updated to mention DCA and lump-sum timing

---

## v3.2.0 — June 2026 — FAQ Aligned with Philosophy v3.1.0

**`faq.html` updated to reflect the v3.1.0 philosophy-page expansion. One new accordion question added; three existing answers deepened; one cross-link added. No design or component changes.**

### faq.html changes

**New question (1):**

- **"Is getting wealthy in the stock market realistic, and how long does it take?"** (`answer-longgame`, inserted after the Stay-on-Offense question). Covers belief as a prerequisite for consistency, the plan-to-one-hundred time-horizon framing (a 40-year-old is past the first quarter, a 50-year-old at halftime), people underestimating multi-decade compounding (city-skyline analogy), and the short-termism / instant-gratification trap. Links to `philosophy.html#section-possible`.

**Existing answers deepened (3):**

- **"What does staying on offense mean..." (`answer-offense`):** new paragraph on a concrete buy cadence (at least twice a month, regardless of conditions) and growing income over cutting expenses (floor on cutting, no ceiling on earning).
- **"How do you think about a company's balance sheet health?" (`answer-balancesheet`):** new paragraph adding the personal-finance (cousin) analogy: heavy debt and little cash = fragile; high cash and low debt = resilient and able to go on offense in downturns.
- **"What does gross margin reveal about a business?" (`answer-grossmargin`):** new paragraph framing margins as a window into a position of power vs weakness, why Wall Street pays up for margin expansion and sells compression, and how a durable margin trend is the quantified version of SWOT strengths and threats.

**Cross-link added (1):**

- **"When is the wrong time to buy a great company?" (`answer-hype`):** now links to `philosophy.html#section-hype` (the hype / weak-hands cascade concept was already covered here; this ties it to the new philosophy section).

### docs/PRD.md changes

- Section 3.7 (FAQ): new question 12 documented; note added recording that the numbered list is not exhaustive and summarizing the v3.2.0 answer enhancements and cross-links

### docs/DESIGN.md changes

- Section 14 (Version History): v3.2 entry added

---

## v3.1.0 — June 2026 — Philosophy Page Expansion (Second Transcript)

**`philosophy.html` expanded from seven to nine sections, integrating new concepts from a second video transcript ("How to Get Filthy Rich in the Stock Market"). Two new sections added; three existing sections deepened with new subsections. Content only; no new components or design changes.**

### philosophy.html changes

**New sections (2):**

- **`#section-possible` — "It Is Possible, and the Game Is Long"** (added as the first section, before Stocks as Ownership). Covers: belief as a structural prerequisite for wealth-building; ordinary starting points reaching large outcomes; the plan-to-one-hundred time-horizon framing (a 40-year-old is past the first quarter, a 50-year-old at halftime); people underestimating multi-decade compounding (city-skyline analogy); caveat box on the short-termism / dopamine-culture trap.
- **`#section-hype` — "Hype, Sentiment, and the Weak-Hands Cascade"** (added after Wall Street vs the Individual, before Market Leadership Cycles). Covers: saturating attention as a late-stage signal rather than a buy signal; the weak-hands cascade mechanism (late buyers near a peak sell on the first slip, pushing successive cohorts underwater); the defense (build before broad attention; anchor to long-term fundamentals over sentiment). Cross-references the short-term vs long-term price-driver framing in the ownership section.

**Existing sections deepened (3):**

- **How to Research a Company:** new subsection "Read the balance sheet like a person's finances" added after the double/lose-50% test (the cousin analogy: heavy debt and little cash = fragile; high cash/investments and low debt = resilient and able to go on offense in downturns).
- **Stay on Offense:** new paragraph on a concrete buy cadence (at least twice a month regardless of conditions) and growing income over cutting expenses (floor on cutting, no ceiling on earning).
- **Building Investment Knowledge:** new subsection "Margins reveal competitive position" added between Study business models and Conference call discipline (multi-year margin direction signals power vs weakness; Wall Street pays up for margin expansion and sells compression; durable margin trends are the quantified version of SWOT strengths and threats).

### Navigation

- "On This Page" sidebar block on `philosophy.html` updated: added `The Long Game` (`#section-possible`) at the top and `Hype & the Weak Hands` (`#section-hype`) after Wall Street. Now nine anchor links.

### docs/PRD.md changes

- Section 3.2 retitled "Nine sections" (was Seven); new Section 0 and Section 5.5 documented; balance-sheet, buy-cadence, income-focus, and margins-as-competitive-position bullets added to existing sections
- Section 5 "On This Page" table: `#section-possible` and `#section-hype` added to the philosophy.html row
- Section 7 concept tracking table: new rows for belief, plan-to-100 horizon, short-termism trap, buy cadence, income focus, and margins-as-competitive-position; existing peak-hype, weak-hands, and balance-sheet rows updated to cite philosophy.html; intro note records the second transcript analysis

### docs/DESIGN.md changes

- Section 4 (Sidebar): nav link list updated to 9 items (Leveraged Strategies added; reflects v3.0.0)
- Section 14 (Version History): v3.0 and v3.1 entries added

### README.md changes

- Pages table: `philosophy.html` row added (was previously missing), summarizing all nine sections

---

## v3.0.0 — June 2026 — Leveraged Strategies Nav Link

**"Leveraged Strategies" added to the left sidebar navigation on all eight pages, immediately above the Support link. Links to the external Leveraged Strategies site in the same tab.**

### Navigation changes (all pages)

- Added `<li><a href="https://azqato.github.io/leveraged-strategies/">Leveraged Strategies</a></li>` above the Support link on all eight HTML files: `index.html`, `philosophy.html`, `metrics.html`, `screener.html`, `watchlist.html`, `indices.html`, `faq.html`
- Final nav order: **Home → Philosophy → Metrics → Screener → Watchlist → Indices → FAQ → Leveraged Strategies → Support**

---

## v2.9.0 — June 2026 — AAII Investor Sentiment Survey Section

**New comprehensive section on `indices.html` covering the AAII Investor Sentiment Survey as a contrarian indicator. Related FAQ entry and documentation updates.**

### indices.html changes

- Added sidebar "On This Page" link: `AAII Investor Sentiment` pointing to `#section-aaii` (placed between Timing Signals and Structural Quality Metrics)
- Updated framework intro paragraph: nine metrics (was eight), four timing signals listed as "VIX, RSI, 52W Range, AAII Sentiment" (was three)
- Added new section `#section-aaii` between `#section-timing` and `#section-quality` containing:
  - H2: AAII Investor Sentiment Survey
  - Intro paragraphs: what the survey is (weekly poll since 1987, ~150K members, Thursday publication, historical averages 37.5% bullish / 31.5% neutral / 31.0% bearish, bull-bear spread ~+6.5 points)
  - How-to-read box: how to access current readings at aaii.com/sentimentsurvey
  - H3: Why It Is a Contrarian Indicator (mechanism explanation)
  - H3: Historical Evidence — 7-row table (March 2000 dot-com peak through Feb 2025 correction)
  - Caveat box: "Historical pattern, not a mechanical rule"
  - H3: AAII Sentiment Action Levels — 5-row table (< 25% through > 60% bearish)
  - H3: Combining AAII with VIX — three-tier framework (Tier 1: either elevated; Tier 2: both elevated; Tier 3: both at extremes with VIX > 35 and AAII > 60%)
  - H3: Conclusion and Next Steps with links to aaii.com and philosophy.html#section-gvd
- Added AAII Bear % row to "What Strong Signals Look Like" signals table (between 52W Range and YTD Perf rows): Strong Signal `> 60% bearish`, Caution Zone `< 25% bearish`
- Updated signals table note: "four timing signals (VIX, RSI, 52W Range, AAII Sentiment)" (was three)
- Updated signals section intro count: "nine" (was eight)

### faq.html changes

- Added Q22: "What is the AAII Investor Sentiment Survey and how do I use it when investing in indices?" with `id="answer-aaii"` (placed immediately after Q21 VIX question)
  - Covers: what the survey is, contrarian mechanism, action levels with historical examples, combined VIX + AAII three-tier framework, link to full indices.html#section-aaii

### docs/PRD.md changes

- Section 3.6 (Indices & ETF Investing): added AAII Investor Sentiment Survey to sections list with description of contrarian use and three-tier combined signal
- Section 3.6 signals table note updated: nine signals, four timing
- Section 3.7 (FAQ): added Q12 entry for AAII FAQ question
- Section 5 (On This Page): added `#section-aaii` to indices.html section IDs between `#section-timing` and `#section-quality`

---

## v2.8.0 — June 2026 — Sitewide Title, Social Card, and Description Alignment

**`<title>`, `og:title`, and `og:description` now match the H1 and lead paragraph on each page exactly. "- Azqato" brand suffix removed from all `<title>` tags sitewide.**

### Convention established

- `<title>` = page H1 text (no brand suffix)
- `og:title` = page H1 text (identical to `<title>`)
- `og:description` = lead paragraph on the page (identical to `<meta name="description">`)
- `twitter:title` and `twitter:description` mirror the OG values

### Changes per page

| Page | Element | Old | New |
|------|---------|-----|-----|
| `index.html` | `<title>` | Azqato - Stock Picking Methodology | Stock Picking Methodology |
| `index.html` | `og:title` | Buy Quality. Hold Long. A Stock Picking Methodology. | Stock Picking Methodology |
| `index.html` | `og:description` | A fundamentals-first, buy-and-hold framework... | A disciplined, metrics-driven approach to long-term equity investing. No day trading. No panic selling. No noise. |
| `philosophy.html` | `<title>` | Philosophy - Azqato | The Philosophy of Long-Term Conviction Investing |
| `philosophy.html` | `og:description` | The conceptual foundation of the methodology... | The concepts that sit behind every rule in this methodology. Understanding why the rules exist makes them easier to follow when markets are moving fast and the temptation to react is strongest. |
| `metrics.html` | `<title>` | Metrics Glossary - Azqato | Stock Evaluation Metrics Explained |
| `metrics.html` | `og:title` | 12 Stock Evaluation Metrics Explained | Stock Evaluation Metrics Explained |
| `metrics.html` | `og:description` | Deep explanations of all 12 evaluation metrics... | Ten metrics. Each one earns its place. This page explains what each signal measures, why it matters for long-term investing decisions, and how to interpret the numbers. |
| `screener.html` | `<title>` | Finviz Screener Setup - Azqato | How to Set Up a Finviz Stock Screener For Free |
| `screener.html` | `og:title` | How to Set Up a Finviz Stock Screener | How to Set Up a Finviz Stock Screener For Free |
| `screener.html` | `og:description` | Step-by-step guide to configuring the Finviz stock screener... | How to configure Finviz's free stock screener to surface candidates that align with the methodology. |
| `watchlist.html` | `<title>` | Watchlist Setup - Azqato | How to Build a Stock Watchlist in Seeking Alpha For Free |
| `watchlist.html` | `og:title` | How to Build a 12-Column Stock Watchlist in Seeking Alpha | How to Build a Stock Watchlist in Seeking Alpha For Free |
| `watchlist.html` | `og:description` | How to configure a 12-column Seeking Alpha watchlist... | Step-by-step guide to creating a free Seeking Alpha account and configuring a portfolio to track individual stocks with the exact 12-column layout. |
| `indices.html` | `<title>` | Indices &amp; ETF Investing - Azqato | Indices &amp; ETF Investing |
| `indices.html` | `og:title` | How to Evaluate Index Funds and ETFs | Indices &amp; ETF Investing |
| `indices.html` | `og:description` | A separate methodology for evaluating index funds and ETFs... | A separate methodology for evaluating broad market indices and ETFs. Different assets require different frameworks. Where individual stock picking is driven primarily by fundamentals, index investing is driven by market sentiment, timing signals, and structural efficiency. |
| `faq.html` | `<title>` | FAQ - Azqato | Stock Investing Q&amp;A |
| `faq.html` | `og:title` | Stock Investing Q&amp;A: Philosophy, Timing, and Position Sizing | Stock Investing Q&amp;A |
| `faq.html` | `og:description` | Philosophy and practice Q&amp;A: why to never sell winners... | The thinking behind the strategy. Questions about how decisions are made, why certain rules exist, and what the long-term mindset actually looks like in practice. |

### Docs updated

- `docs/PRD.md` — Section 5 updated: convention rule added, required tags template updated, per-page values table updated with new titles and descriptions
- `docs/DESIGN.md` — Section 12 updated: "no - Azqato suffix" rule added

---

## v2.7.0 — June 2026 — H1 and Copy Corrections on Metrics, Watchlist, and FAQ Pages

**H1 headings corrected on three pages. Two additional corruptions on faq.html fixed: nav link label and an inline body copy reference.**

| File | Element | Old | New |
|------|---------|-----|-----|
| `metrics.html` | H1 | 12 Stock Evaluation Metrics Explained | Stock Evaluation Metrics Explained |
| `watchlist.html` | H1 | How to Build a Stock Watchlist For Free in Seeking Alpha | How to Build a Stock Watchlist in Seeking Alpha For Free |
| `faq.html` | H1 | Stock Investing Q&A: Philosophy, Timing, and Position Sizing &amp; Philosophy | Stock Investing Q&A |
| `faq.html` | Nav link | Stock Investing Q&A: Philosophy, Timing, and Position Sizing | FAQ |
| `faq.html` | Body copy | "The Palantir story at the top of this Stock Investing Q&A: Philosophy, Timing, and Position Sizing documents..." | "The Palantir story at the top of this page documents..." |

---

## v2.6.0 — June 2026 — H1 Heading Corrections on Screener and Watchlist Pages

**Two page H1 headings corrected after being corrupted by a prior sitewide replace operation.**

| Page | Old H1 | New H1 |
|------|--------|--------|
| `screener.html` | Finviz How to Set Up a Finviz Stock Screener | How to Set Up a Finviz Stock Screener For Free |
| `watchlist.html` | Seeking Alpha How to Build a 12-Column Stock Watchlist in Seeking Alpha | How to Build a Stock Watchlist For Free in Seeking Alpha |

---

## v2.5.0 — June 2026 — Social Cards Rolled Out Sitewide

**Open Graph and Twitter Card meta tags added to all remaining six pages. Every page on the site now renders a preview card when shared on Discord, X, Slack, or any OG-compatible platform.**

### Pages updated

| Page | `og:title` |
|------|-----------|
| `philosophy.html` | Philosophy - Azqato |
| `metrics.html` | Metrics Glossary - Azqato |
| `screener.html` | Screener Setup - Azqato |
| `watchlist.html` | Watchlist Setup - Azqato |
| `indices.html` | Indices and ETF Investing - Azqato |
| `faq.html` | FAQ - Azqato |

Each page received: `<meta name="description">`, five Open Graph tags (`og:type`, `og:url`, `og:title`, `og:description`, `og:image`), and three Twitter Card tags (`twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`). All pages share `og-image.png`.

---

## v2.4.0 — June 2026 — Open Graph Social Cards

**Open Graph and Twitter Card meta tags added to `index.html` so Discord, X, Slack, and similar platforms render a preview card when the link is shared. `og-image.png` (1200x630) added to the site root. PRD updated with Section 5 documenting the full requirement for all seven pages.**

### index.html

- `<meta name="description">` added
- Open Graph tags added: `og:type`, `og:url`, `og:title`, `og:description`, `og:image`
- Twitter Card tags added: `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`

### og-image.png (new)

- 1200x630 PNG at the site root
- Site favicon (📈, U+1F4C8) centered on `#0d1117` background, rendered as a white monochrome icon
- Referenced by all OG/Twitter image tags across the site

### docs/PRD.md

- Section 5 "Social Cards (Open Graph)" added: required tag template, per-page values table for all seven pages, image spec, and PowerShell regeneration snippet

---

## v2.3.0 — June 2026 — FAQ Expansion and Badge Text Corrections

**faq.html expanded from 11 to 30 accordion items. Hero badge text corrected sitewide to be distinct from each page's H1 title.**

### faq.html — Expanded Q&A (11 original, 19 new)

19 new accordion items added covering topics derived from all site pages:

| # | New Question |
|---|---|
| 3 | What is the "stocks as ownership" mental model? |
| 4 | What does "staying on offense" mean and why does it matter? |
| 5 | Can I trust Wall Street recommendations? |
| 6 | What is market leadership cycle and why does it matter? |
| 8 | How do you research a company before looking at any numbers? |
| 9 | What is the double/lose-50% test? |
| 11 | How do you build investment knowledge over time? |
| 13 | What is market cap vs. potential and why does it matter? |
| 14 | What does gross margin reveal about a business? |
| 15 | How do you think about a company's balance sheet health? |
| 16 | What is the revenue deceleration warning signal? |
| 17 | Why is PEG a better valuation signal than P/E alone? |
| 18 | What are Growth, Value, and Dividend stocks and how do they differ? |
| 20 | What is RSI and how do you use it as an entry signal? |
| 21 | What is the VIX and how should I use it when investing in indices? |
| 22 | How is investing in ETFs different from picking individual stocks? |
| 23 | What is an expense ratio and why does it matter for ETF investing? |
| 24 | What are leveraged ETFs and when are they appropriate? |
| 30 | Why do conference calls matter more than earnings press releases? |

### Hero badge text corrections

Five pages had badges that were identical or near-identical to their H1 title. Updated to purpose/type labels distinct from the page name:

| Page | Old Badge | New Badge |
|------|-----------|-----------|
| `philosophy.html` | 📖 Investment Philosophy | 📖 Mindset &amp; Principles |
| `metrics.html` | 📊 Metrics Glossary | 📊 The 12 Signals |
| `screener.html` | 🔍 Screener Setup Guide | 🔍 Candidate Discovery |
| `watchlist.html` | 📋 Watchlist Setup Guide | 📋 12-Column Tracking Setup |
| `faq.html` | ❓ FAQ &amp; Philosophy | ❓ Strategy Q&amp;A |

---

## v2.2.0 — June 2026 — Sitewide Hero Badge System

**Hero badge added to all seven pages and repositioned consistently below the page description. Badge position is now: headline, then description, then badge.**

### index.html

- `<div class="hero-badge">` moved from the top of the `.hero` section to after `.hero-sub`
- `margin-top: 16px` added inline to create consistent spacing between the description and the badge
- `.hero` `padding-bottom` reduced from `36px` to `16px` in `style.css` to visually center the badge between the description and the section divider

### Badges added (new)

| Page | Badge |
|------|-------|
| `philosophy.html` | 📖 Investment Philosophy |
| `metrics.html` | 📊 Metrics Glossary |
| `screener.html` | 🔍 Screener Setup Guide |
| `watchlist.html` | 📋 Watchlist Setup Guide |
| `faq.html` | ❓ FAQ & Philosophy |

All new badges use `margin-top: 16px` inline and appear after the page description inside the intro container (`.metrics-intro`, `.guide-intro`, or `.faq-intro`).

### indices.html

- Existing badge moved from above the `<h1>` to after the description paragraph, consistent with the sitewide pattern. `margin-bottom: 16px` replaced with `margin-top: 16px`.

---

## v2.1.0 — June 2026 — Sitewide "On This Page" Navigation

**"On This Page" sidebar anchor navigation extended from metrics.html to all content pages. Block repositioned to appear below the Support link on every page with named sections. IntersectionObserver generalized to work across all pages without per-page configuration.**

### Navigation changes

The "On This Page" anchor block was previously nested inside the Metrics nav item on `metrics.html` only. It is now:

- A standalone `<li>` element positioned below the Support link (bottom of the main nav list) on every page with named sections
- Present on six pages: index, philosophy, metrics, screener, watchlist, indices
- Hidden on mobile alongside other sidebar sub-navigation (existing behavior unchanged)
- Absent on `faq.html` where the accordion pattern is not suited to anchor-link navigation

### Pages updated

| Page | Sections added to "On This Page" |
|------|----------------------------------|
| `philosophy.html` | Stocks as Ownership, How to Research a Company, Growth/Value/Dividend, Stay on Offense, Wall Street vs the Individual, Market Leadership Cycles, Building Investment Knowledge |
| `index.html` | The Strategy, The 10 Metrics, What Strong Metrics Look Like, Portfolio vs. Watchlist |
| `screener.html` | What Finviz Is For, Step 1, Step 2, Step 3, Finviz Free Tier Coverage, Quick-Reference Summary |
| `watchlist.html` | Step 1: Create Account, Step 2: Create Portfolio, Step 3: Add Tickers, Step 4: Configure Columns, Step 5: Sort Order, Your Watchlist Is Ready |
| `indices.html` | Types of Index Funds, Fundamentals vs. Technicals, The VIX, Timing Signals, Structural Quality Metrics, What Strong Signals Look Like, Seeking Alpha Setup |
| `metrics.html` | Block moved from nested under Metrics link to after Support (position change only; links and IDs unchanged) |

### Section IDs added

All section IDs follow the `section-*` prefix convention (e.g., `section-ownership`, `section-strategy`). Existing `metrics.html` IDs (`metric-rev-ttm`, etc.) are unchanged.

### script.js

`IntersectionObserver` generalized. Previously hardcoded to observe `.metric-block` elements (metrics.html only). Now derives section targets from the `href` attributes of `.metric-links a` elements present on the page. Works across all pages with no per-page configuration. No behavioral change on `metrics.html`.

### docs/PRD.md

Section 5 updated with an "On This Page" sidebar navigation reference table listing all section IDs by page, plus implementation notes for the observer.

### docs/DESIGN.md

- Section 4 (Sidebar) updated: nav item list corrected to all 8 nav items; "On This Page" pattern documented
- Section 6 (Signature Element) updated: block now described as sitewide rather than metrics-only
- Section 7 (Navigation) sub-link description updated
- Version history: v1.8.0 entry added

---

## v2.0.0 — June 2026 — Sitewide Punctuation Audit

**Complete em dash and double hyphen removal across all seven active HTML pages and all three documentation files. No content changes; punctuation only. PRD.md updated with formal punctuation policy and audit checklist.**

### Policy

Per the punctuation policy documented in `docs/PRD.md` (Section 4), no em dashes or double hyphens (`--`) are permitted in copy. All instances replaced with contextually appropriate alternatives: comma (flowing continuation), colon (introducing an explanation or list), semicolon (two independent clauses), parentheses (aside or supplementary info), or period (sentence split).

When auditing for em dashes, all three forms must be checked: ` -- ` (double hyphen), `—` (raw Unicode U+2014), and `&mdash;` (HTML entity).

### Pages audited and cleaned

| File | Instances fixed |
|------|----------------|
| `philosophy.html` | ~20 instances |
| `metrics.html` | ~65 instances |
| `screener.html` | 2 instances |
| `watchlist.html` | 2 instances |
| `indices.html` | ~19 instances |
| `faq.html` | ~25 instances |
| `index.html` | 0 (already clean) |

### Docs audited and cleaned

| File | Instances fixed |
|------|----------------|
| `docs/PATCHNOTES.md` | ~17 instances |
| `docs/DESIGN.md` | 6 instances |
| `docs/PRD.md` | 0 prose instances (policy section updated) |

### docs/PRD.md

- **Section 4 (Content Philosophy):** Punctuation policy statement updated to explicitly name all three em dash forms to audit: ` -- `, `—`, and `&mdash;`
- **Punctuation style guide:** New "Audit checklist" block added at the top of the section, listing all three search targets with notes that `&mdash;` is especially easy to miss in HTML source

### Other fixes

- `screener.html`: Stale link `href="guide.html"` corrected to `href="watchlist.html"` (guide.html is an orphaned legacy page not in active nav)

### Legacy files removed

Three orphaned HTML files that were superseded by current pages and are not linked from the active nav were deleted:

| File removed | Replaced by |
|---|---|
| `finviz.html` | `screener.html` |
| `guide.html` | `watchlist.html` |
| `indexes.html` | `indices.html` |

### Notes

- `&ndash;` (`–`) in numeric ranges (e.g., VIX table `15 &ndash; 25`) was left untouched; en dashes for numeric ranges are correct
- CSS custom property names (`--color-text-primary`, `--color-text-secondary`, etc.) were left untouched; `--` is valid CSS variable syntax, not punctuation
- Backtick-wrapped code literals showing `--` as a UI display value (e.g., "PEG shows `--` when not applicable") were left untouched

---

## v1.9.0 — June 2026 — Major Content Expansion

**New Philosophy page. Two new business quality metrics (Gross Margin and Net Margin). Revenue deceleration signal added. Balance sheet rate-hiking advantage documented. FAQ expanded with four new questions. Strategy section deepened with diversification rule and market cap vs potential concept. All 30 concepts from video transcript analysis integrated into site content.**

### New Pages

| File | Description |
|------|-------------|
| `philosophy.html` | New full-length page covering the conceptual foundation of the methodology: stocks as ownership (Buffett farmland analogy), how to research a company (sequential evaluation and SWOT framework), the GVD framework (growth/value/dividend stocks and risk-on/risk-off environments), staying on offense as a psychological discipline, Wall Street incentive misalignment, market leadership cycles and complacency risk, and building investment knowledge through business model study and conference call discipline |

### Navigation Changes (all pages)

- `philosophy.html` added to sidebar nav between Home and Metrics on all seven pages
- Final nav order: **Home → Philosophy → Metrics → Screener → Watchlist → Indices → FAQ → Support**

### index.html

- **Strategy Overview expanded:** Added paragraph on the 10-to-20 stock diversification rule (fewer than 10 concentrates risk, more than 20 dilutes conviction)
- **Strategy Overview expanded:** Added paragraph on the market cap vs potential mental model, comparing current market cap to the addressable opportunity as an input to upside estimation
- **"The 10 Metrics" section:** Added note pointing to Gross Margin and Net Margin entries in the Metrics glossary as supplementary business quality signals
- **"What Strong Metrics Look Like" table:** Two new rows added: Gross Margin (strong: >50%, caution: <30%) and Net Margin (strong: >25%, caution: <10%)
- **FAQ teaser:** Updated to include a link to the new Philosophy page alongside the existing Palantir story link

### metrics.html

- **Sidebar nav:** Anchor links for Gross Margin and Net Margin added to the "On This Page" sub-nav
- **Revenue Growth TTM ("Why it matters"):** New paragraph added explaining the quarterly deceleration warning signal: a consistent pattern of declining quarterly growth rates (+20%, +15%, +10%, +5%) is one of the clearest warning signals available even when absolute growth is still positive
- **Total Cash ("Why it matters"):** New paragraph added explaining the rate-hiking earnings advantage: cash-heavy companies earn interest income at elevated rates while debt-heavy companies face rising interest expense, creating an earnings-level competitive divergence
- **New metric #11: Gross Margin.** Full metric block with what it measures, why it matters (margin direction as a signal of competitive position strength or weakness), how to read it (50%+ strong, 30-50% moderate, <30% caution, declining trend = red flag), gross margin by business type illustrative table, and caveat on cross-industry comparability
- **New metric #12: Net Margin.** Full metric block with what it measures, why it matters (operating leverage as the engine of earnings compounding), how to read it (30%+ elite, 25-30% excellent, 10-25% good, <10% context-required, negative = investigate), trajectory table, and caveat on always researching why margins move

### faq.html

- **"How many stocks should I hold?":** 10-20 rule: below 10 concentrates risk, above 20 dilutes conviction; full construction rationale
- **"When is the wrong time to buy a great company?":** Peak hype avoidance and the weak-hands cascade mechanism: late buyers without business conviction trigger selling cascades when prices pull back; the best entry points are before widespread attention arrives
- **"What should I think about position sizing?":** Core positions (profitable, established companies) vs speculative positions (unprofitable, binary outcomes); keep speculative positions small regardless of prior wins
- **"How does market environment affect which stocks perform best?":** Risk-on/risk-off states, how each affects growth vs value vs dividend stocks, dividends as crash-deployment capital; links to Philosophy page for full GVD framework

### philosophy.html (new)

Seven sections covering the full conceptual foundation of the methodology:

1. **Stocks as Ownership, Not Symbols:** Farmland and franchise mental models; productive asset framing; explicit short-term vs long-term price driver distinction
2. **How to Research a Company:** Sequential evaluation order (business model first, then financials, then valuation); SWOT framework; the double/lose-50% decision test
3. **Growth, Value, and Dividend Stocks:** The three stock types; risk-on and risk-off market environments; dividends as crash-deployment capital; 2022 as the textbook example
4. **Stay on Offense:** Why regular investing is psychologically critical; offensive vs defensive investor mindset; consistency over size
5. **Wall Street vs the Individual Investor:** AUM fee incentive structure; herd mentality as volatility amplifier; the S&P 500 proof point; do your own research
6. **Market Leadership Cycles:** No company stays dominant forever; the complacency mechanism; continuous thesis reassessment; the opportunity in next-generation companies
7. **Building Investment Knowledge:** Business model study for pattern recognition; conference call discipline (twice-listen rule, 2x speed, 50-100 calls per season); always research why margins move

### docs/PRD.md

- Complete rewrite. Previous version described the v1.0.0 three-page site with live META data. Updated to reflect the current 7-page site, all 12 metrics, the philosophy framework, the full FAQ, and a full 30-concept concept tracking table preserving the transcript analysis before the temp file was deleted.

---

## v1.8.0 — June 2026 — Launch Release

**Initial public launch. Yield label generalized on indices page. README updated to reflect full site scope.**

### indices.html

- **"4Y Avg Yield" renamed to "Yield"** throughout the page: metric card description, introductory paragraph, "What Strong Signals Look Like" summary table. The label now reflects yield broadly (trailing 12-month, 30-day SEC, or multi-year average) rather than anchoring to a specific averaging window.
- **"4Y Average Yield" section heading renamed to "Yield."** Section explanation updated: now describes yield as the dividend or distribution yield of an ETF, noting that the specific format (trailing 12-month, 30-day SEC, multi-year average) varies by platform and ETF type. The operative test remains yield vs. expense ratio regardless of how it is expressed.
- **Seeking Alpha ETF watchlist setup table:** "Yield" row retains the label "4Y Avg Yield" in the watchlist column reference, since that is the actual column name in Seeking Alpha's interface.

### README.md

- Full rewrite. Previous version was a v1.0.0 snapshot (3-page site, META live data, old project structure). Updated to reflect the full 7-page site, all metrics, the index/ETF methodology, design system summary, and current content philosophy.

---

## v1.7.0 — June 2026

**Text color refinement. Primary and secondary text tokens now distinct.**

### style.css

- `--color-text-primary` updated from `#e6edf3` to `#eef3f7`: slightly brighter, cleaner white for body copy and headings
- `--color-text-secondary` updated from `#e6edf3` to `#cbdae6`: soft blue-gray for subtitles, captions, lead text, and metric card definitions; visually distinct from primary without being muted or hard to read

---

## v1.6.0 — June 2026

**Indices & ETF guide added. Navigation restructured. Sitewide readability improvements. Long-term capital gains content. FAQ expanded.**

### New Files

| File | Description |
|------|-------------|
| `indices.html` | Full index and ETF investing guide: VIX action levels, fund types, structural quality metrics, Seeking Alpha ETF watchlist setup |
| `watchlist.html` | Renamed from `guide.html`. Seeking Alpha individual stocks watchlist setup guide (content unchanged). |

### Navigation Changes (all pages)

Final nav order: **Home → Metrics → Screener → Watchlist → Indices → FAQ → Support**

- `guide.html` retired; replaced by `watchlist.html` with updated self-link
- Nav label "SA Watchlist" shortened to "Watchlist"
- Nav label "Finviz Screener" shortened to "Screener"
- "Indexes" renamed to "Indices"
- FAQ moved to position 6 (just above Support), making logical groupings: content (Home, Metrics), tools (Screener, Watchlist, Indices), help (FAQ, Support)

### indices.html (new)

- Full methodology page for index and ETF investing
- **Fund Types section:** Six metric cards explaining broad market funds, growth funds, dividend funds, value funds, sector-specific funds, and international funds: their role, risk profile, and how each is used in a diversified ETF strategy
- **Fundamentals vs. Technicals section:** Educational explanation of why technicals dominate index investing while fundamentals dominate individual stock picking. Core insight: indices cannot go to zero; individual stocks can. This asymmetry shifts the analytical framework.
- **VIX: The Fear Gauge:** Full explanation of what VIX measures, why it is contrarian and mean-reverting, and five action level ranges (< 15, 15-25, 25-35, 35-45, > 45) with educational market condition descriptions and recommended deployment postures
- **Leveraged ETFs caveat:** Explanation of when to use 2x/3x ETFs (VIX > 45 recovery plays only, not long-term holds)
- **RSI & 52W Range:** Applied to index/ETF context with how-to-read guidance
- **Structural Quality Metrics:** YTD Performance, 5Y Total Return, 10Y Total Return, 4Y Avg Yield (yield > expense ratio test), Expense Ratio with full tier breakdown (< 0.10% to > 0.75%)
- **"What Strong Signals Look Like" table:** 8-metric reference table with Type (Timing/Structural), Strong Signal, Caution Zone, and What It Confirms columns
- **Seeking Alpha ETF Watchlist Setup:** 10-column ETF portfolio setup with exact search terms; VIX tracking note; yield column caveat

### faq.html

- **Q5 (Technical Analysis) substantially rewritten.** Now explains why technicals are used minimally for individual stocks but significantly more for indices/ETFs. Core distinction: individual companies can go bankrupt to $0; broad market indices cannot. This asymmetry makes "what to buy" the primary question for stocks (answered by fundamentals) and "when to buy" the primary question for indices (answered by technicals). VIX cited as the most powerful timing tool for index investing.
- **New Q7 added: "Why does holding for over 12 months matter beyond investment returns?"** Full explanation of long-term vs. short-term capital gains tax treatment. Covers the rate differential (15-20% LTCG vs. 22-37% ordinary income for short-term), compounding advantage of tax deferral, and the hidden cost of selling before the 12-month threshold. Five-paragraph educational response.

### index.html

- **Strategy Overview section updated.** Added paragraph about long-term capital gains: holding positions for more than 12 months qualifies for the lower long-term rate; selling too early converts gains to ordinary income; the strategy's default posture of holding is both a better investment philosophy and the most tax-efficient one available.

### style.css

- **`.accordion-content`** color changed from `--color-text-secondary` to `--color-text-primary`. All FAQ accordion body text is now full-brightness readable.
- **`td`** `white-space` changed from `nowrap` to `normal`. All table cell text now wraps rather than clipping. `white-space: nowrap` preserved on `td.num` (numbers) and `td.ticker-cell` (tickers) where truncation is not a concern.
- **`--color-text-secondary` unified with `--color-text-primary`** in `:root`. Changed from `#8b949e` to `#e6edf3`. All elements using the secondary token (metric card descriptions, accordion body text, lead paragraphs, captions, sidebar labels) now render at full legibility. Both color tokens resolve to the same value. This is a root-level change that applies universally; individual class overrides are not needed.
- **`.guide-note`** color set to `--color-text-primary` (explicit, pre-dating the root unification).

---

## v1.5.0 — June 2026

**Two new setup guide pages. Navigation expanded to six items. Text readability improvements. P/E FWD educational content deepened.**

### New Files

| File | Description |
|------|-------------|
| `guide.html` | Step-by-step Seeking Alpha watchlist setup guide |
| `screener.html` | Finviz stock screener setup guide with recommended filter values |

### Changes

#### guide.html (new)

- Full step-by-step guide for creating a free Seeking Alpha account and configuring a portfolio watchlist with the exact 12-column methodology layout
- Emphasizes free tier (no credit card, no subscription required)
- Primary entry point: `seekingalpha.com/account/portfolio`
- Covers: account creation, portfolio creation, ticker addition, column customization (all 12 columns with exact Seeking Alpha search terms and categories), sort order setup
- Column reference table includes the exact search terms to use in Seeking Alpha's column picker for all 12 metrics (Symbol, Market Cap, Price, Change %, Revenue Growth FWD, EPS Growth FWD, P/E Non-GAAP FWD, PEG Non-GAAP FWD, Total Cash, Total Debt, RSI (14), 52 Week Range)
- Non-GAAP vs. GAAP callout box explaining why Non-GAAP is preferred for P/E and PEG
- Cross-links to Finviz screener guide for candidate discovery

#### screener.html (new)

- Full Finviz screener setup guide for finding new stock candidates aligned with the methodology
- Free screener, no account required. Entry point: `finviz.com/screener`
- Explains Finviz's role as a candidate discovery tool vs. Seeking Alpha as the full evaluation tool
- Step-by-step filter setup: Market Cap, Forward P/E, PEG, EPS Growth Next Year, EPS Growth Next 5Y, Sales Growth QoQ, Total Debt/Equity, RSI (14), 52-Week Low
- Recommended filter values with rationale for each
- Results table navigation: Valuation view, PEG sort, Technical view
- Coverage table showing which methodology metrics are directly available vs. proxy-only in Finviz free tier
- Quick-reference filter summary table
- Cross-links to Seeking Alpha watchlist guide

#### All pages (index.html, metrics.html, faq.html, guide.html, screener.html)

- **Navigation expanded.** Two new nav items added to all sidebars, between FAQ and Support:
  - `SA Watchlist` → `guide.html`
  - `Finviz Screener` → `screener.html`
- All five pages have consistent 6-item nav: Home, Metrics, FAQ, SA Watchlist, Finviz Screener, Support

#### style.css

- **Text readability improvement.** `.hero-sub` and `.lead` changed from `--color-text-secondary` to `--color-text-primary`. These classes are used for intro paragraphs and hero subtext sitewide; the previous muted color created unnecessary visual friction for body-level reading content.
- **Guide step body text.** `.guide-step-body p` and `.guide-step-body li` also use `--color-text-primary` for consistency with the above change.
- **New component classes added** for guide pages: `.guide-intro`, `.guide-steps`, `.guide-step`, `.guide-step-header`, `.step-num`, `.guide-step-title`, `.guide-step-body`, `.ui-text`, `.guide-note`, `.filter-strong`, `.filter-caution`

#### metrics.html: P/E FWD section

- **"Why it matters" section substantially expanded.** Added explicit explanation of the core P/E vs. EPS Growth comparison: when P/E FWD is lower than the EPS Growth FWD percentage, the growth rate outpaces the multiple paid: a strong signal that the stock is underpriced relative to its earnings trajectory. When P/E is higher than the EPS growth rate, the multiple exceeds what earnings can currently justify.
- This concept was previously implied through the PEG ratio explanation. It is now stated directly as the primary criterion for reading P/E FWD.
- **"How to read it" box updated.** First bullet now explicitly marks "P/E FWD below the forward EPS growth rate" as the primary signal. Secondary bullet covers sector/5Y comparison.
- **Caveat box updated.** Reinforces the direct P/E vs. growth comparison as the operative test, not just PEG.

#### index.html: "What Strong Metrics Look Like" table

- **P/E FWD row updated.** Strong Signal changed from "Below 5Y avg + sector" to `P/E < EPS Growth %` as the primary criterion. Caution Zone updated to `P/E > EPS Growth %`. "What It Confirms" updated to reflect the growth-adjusted framing.

---

## v1.4.0 — June 2026

**Content generalization pass. Removed real-time data references. Expanded educational content.**

### Summary

All three pages audited for real-time or company-specific data that would become stale or imply a live recommendation. Such references replaced with educational prose and hypothetical illustrative examples. The Palantir story and all other explicit historical first-person accounts are retained.

### Changes

#### index.html

- **Removed:** "Individual Stonks" holdings table (21 rows of live portfolio data with prices, P/E, PEG, RSI, and 52W range values)
- **Removed:** "Potential Buys" watchlist ticker tag section
- **Added:** "What Strong Metrics Look Like" reference table: 7-row directional guide showing strong signal ranges, caution zones, and what each metric confirms. Uses no company-specific data.
- **Added:** "Portfolio vs. Watchlist" section: 4-paragraph educational explanation of entry criteria and the patience mechanism. Replaces the removed data tables with methodology context.

#### metrics.html

- **Rewrote all 10 metric blocks.** Every META-specific example table replaced with hypothetical illustrative examples using generic labels ("High-growth tech co.", "Slow-growth value co.", "Accelerating / Stable / Decelerating").
- All real-time figures (META P/E 18.18, PEG 0.88, Cash $81.18B, Debt $86.77B, RSI 40, etc.) removed.
- Expanded educational prose for each metric; each block now explains what to look for across a range of companies, not how to read one company's current snapshot.
- PEG FWD illustrative table shows why P/E alone misleads using hypothetical growth rates.
- 52W Range section includes a combined RSI + range positioning table showing how the two signals reinforce each other.
- P/E FWD section includes two hypothetical tables: P/E compression over time (showing multiple expansion from growth), and P/E vs sector/5Y-average comparison.

#### faq.html

- **Q4 moat examples generalized.** Specific company names removed from the moat type examples. Replaced with category descriptions that teach the concept without anchoring to a specific stock:
  - "switching costs (Salesforce)" → "switching costs (enterprise software platforms deeply embedded in customer workflows)"
  - "network effects (Meta)" → "network effects (social and communication platforms where value scales with users)"
  - "scale advantages (Amazon)" → "scale advantages (cloud and logistics infrastructure where size creates a cost floor competitors cannot match)"
  - "regulatory moats (Regeneron)" → "regulatory moats (biotechnology and drug pipelines protected by patents and approval timelines)"
  - "brand (American Express)" → "brand (premium financial services and consumer goods where trust itself is the barrier)"
- **Palantir story unchanged.** Retained in full as a first-person historical account ($9 buy-in, $45 sale, $150 outcome). This is a named historical example, not a real-time recommendation.

#### docs/DESIGN.md

- **Section 13 added:** Content Philosophy. Documents the rule that all illustrative examples must use hypothetical labels or category descriptions, not real-time company data. Named exceptions (Palantir story) are explicitly noted.
- **Section 14 (Version History):** v1.4.0 entry added.

---

## v1.3.0 — June 2026

**Footer cleanup.**

- Removed "Educational use only. Nothing on this site constitutes financial advice." from the footer on all three pages. Disclaimer is retained in the sidebar footer where it already lives cleanly.
- Footer now reads only: "Built by Azqato" (linked to azqato.github.io).

---

## v1.2.0 — June 2026

**Navigation and branding updates.**

### Changes

#### All three HTML files (index.html, metrics.html, faq.html)

- **Sidebar brand renamed.** "Azqato." replaced with "Individual Stocks." (teal dot accent retained). Font size reduced from 1.1rem to 0.9rem to accommodate the longer text within the 220px sidebar width.
- **Support link added** to sidebar nav on all pages. Opens `https://azqato.github.io/support.html` in a new tab (`target="_blank" rel="noopener"`). Placed after FAQ in the nav order.
- **Footer updated** to match `azqato.github.io` pattern: "Built by [Azqato](link)" as the primary line, with the educational disclaimer on a second line. "Azqato" links to `https://azqato.github.io/`.

#### style.css

- `.sidebar-brand a`: `font-size` reduced from `1.1rem` to `0.9rem`; `letter-spacing` removed; `white-space: nowrap` added to prevent wrapping.

---

## v1.1.0 — June 2026

**Dark theme rebrand. Aligned to Azqato brand system.**

### Summary

Full visual redesign to match the GitHub Dark-inspired aesthetic used across all Azqato properties (portfolio, VIX Strategy, ComposerAtlas). No content changes; all metric text, table data, and FAQ copy is unchanged. Changes are purely CSS, HTML head tags, and documentation.

### Changes

#### style.css

- **Color system replaced.** All CSS custom properties updated to the Azqato dark theme palette:
  - Background `#FAFAFA` → `#0d1117`
  - Surface `#FFFFFF` → `#161b22`
  - Border `#E2E6EA` → `#30363d`
  - Accent `#1A6B4A` (deep forest green) → `#00d4a0` (Azqato teal-green)
  - Accent light `#EBF5F0` → `rgba(0,212,160,0.08)` (dark-mode teal tint)
  - Text primary `#1A1F2E` → `#e6edf3`
  - Text secondary `#5A6070` → `#8b949e`
  - Positive `#16A34A` → `#3fb950`
  - Negative `#DC2626` → `#f85149`
  - Warning `#B45309` → `#ffa657`
  - Added: `--color-tag-bg: #21262d`, `--color-card-hover: #1c2128`, `--color-accent-hover: #00e6b0`, `--color-purple: #bc8cff`

- **Typography replaced.** Removed IBM Plex Serif / IBM Plex Sans / IBM Plex Mono (Google Fonts). Now uses system font stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`) with system monospace (`'SF Mono', 'Consolas', 'Liberation Mono', monospace`). Eliminates external font dependency, matches Azqato brand.

- **h2 accent bar added.** All `h2` elements now render with a `::before` vertical accent bar (3px wide, teal) via flexbox, matching the section title design from `azqato.github.io`.

- **Metric cards updated.** Added card hover effects: `translateY(-2px)`, box-shadow teal tint, accent border color, and 2px gradient top border (`--color-accent` to `--color-purple`) via `::before`. Matches project card hover behavior from the portfolio site.

- **Badges restyled.** Changed from solid backgrounds to semi-transparent tinted pills with matching border colors (consistent with Azqato pill pattern).

- **Tables.** Header now uses `--color-card-hover`. Table wrapper gets `border-radius: 8px`. Alternating rows use `rgba(255,255,255,0.02)`. Hover uses accent-tinted background.

- **Accordion.** Content background changed from solid `--color-accent-light` to `rgba(0,212,160,0.04)`. Trigger hover uses teal tint. Palantir story text changed to `--color-text-primary` (full brightness) to signal elevated importance.

- **Footer.** Changed from solid dark background to `--color-bg` with `border-top: 1px solid --color-border` (matches portfolio site pattern).

- **Sidebar collapse.** On tablet, collapsed sidebar now uses `backdrop-filter: blur(12px)` frosted glass effect.

#### All three HTML files (index.html, metrics.html, faq.html)

- Removed Google Fonts `<link>` tags (3 link tags per file: preconnect x2, fonts.googleapis.com)
- Added `📈` emoji SVG data URI favicon via `<link rel="icon" href="data:image/svg+xml,...">` 
- Sidebar brand updated: `Azqato.` with teal `<span>` on the period (matching `azqato.github.io` logo pattern)
- Hero badge added to `index.html`: "📈 Methodology Documentation" pill badge in `--color-positive`
- Hero thesis updated: "Do not sell." wrapped in `<span class="highlight">` for teal accent treatment

#### docs/DESIGN.md

- Full rewrite to reflect v1.1.0 design system
- Documents new dark palette, system font stack, component specs for dark theme
- Added version history table
- Removed IBM Plex references, updated all color tokens
- Added new sections: Hero Badge, Watchlist Ticker Tags, Favicon

---

## v1.0.0 — June 2026

**Initial release. Full site built from scratch.**

### Files Created

| File | Description |
|------|-------------|
| `index.html` | Home page |
| `metrics.html` | Metrics glossary (all 10 metrics) |
| `faq.html` | FAQ and philosophy (accordion) |
| `style.css` | Full design system stylesheet |
| `script.js` | Accordion behavior and IntersectionObserver sidebar highlight |
| `docs/README.md` | Project overview |
| `docs/PRD.md` | Product requirements document |
| `docs/DESIGN.md` | Design specification |
| `docs/PATCHNOTES.md` | This file |

---

### index.html

**Sections built:**
- Hero: one-line thesis statement and sub-headline
- Strategy Overview: 3-paragraph explanation of the core methodology
- The 10 Metrics: 2-column card grid, each card links to the full metric entry on `metrics.html`
- Individual Stonks: table of 21 current holdings with Symbol, Price, P/E FWD, PEG FWD, RSI, and 52W Range (visual range bar showing price position within annual range)
- Potential Buys: watchlist of 25 tickers displayed as tag badges (full numeric data not available from source screenshot at this time; can be expanded to full table format)
- FAQ Teaser: link to the Palantir story on `faq.html`
- Footer: disclaimer

**Holdings data source:** Seeking Alpha individual stocks view, June 2026.

**Holdings included (sorted by PEG FWD ascending):**
HUBS, NVDA, TOST, WDAY, CRM, ADBE, TEAM, DELL, INTU, META, LULU, NOW, AMD, REGN, AMZN, AXP, ELF, GOOGL, ZM, PLNH, BRK.B

**Watchlist tickers:**
ACN, APP, AXON, BBY, BX, CELH, COUR, CRCL, GS, HNST, HOOD, IFJPY, IMAX, LZ, MNDY, MSFT, NFLX, NKE, PINS, RVLV, SOFI, TER, TTD, UBER, VEEV

---

### metrics.html

**All 10 metrics documented with:**
- Name and full title
- What it measures (plain English definition)
- Why it matters (investment context)
- How to read it (range badges: good / caution / red flag)
- META example table (real data from Seeking Alpha screenshots)
- Caveat box (edge cases and limitations)

**Metrics covered:**
1. Revenue Growth TTM
2. Revenue Growth FWD
3. EPS Growth TTM
4. EPS Growth FWD
5. P/E FWD
6. PEG FWD
7. Total Cash
8. Total Debt
9. RSI
10. 52-Week Range

**Primary example company:** META Platforms (META), data from Seeking Alpha valuation/metrics page, June 2026.

**META data used:**
- P/E Non-GAAP (FWD): 18.18
- PEG Non-GAAP (FWD): 0.88
- Total Cash: $81.18B
- Total Debt: $86.77B
- RSI: 40
- 52W Range: $520.28 - $798.25
- EPS Growth estimates: Dec 2026: 8.53%, Dec 2027: 12.28%, Dec 2028: 14.20%, Dec 2029: 21.53%
- P/E estimates: 2025 Actual: 19.73, 2026: 18.18, 2027: 16.19, 2028: 14.17, 2029: 11.66

**Sidebar navigation:** Sticky left sidebar with in-page anchor links for all 10 metrics. Active link highlighted in accent green via IntersectionObserver scroll detection.

---

### faq.html

**Accordion items built:**

1. Why do you never sell your stocks?
2. The Palantir Story (visually distinguished with accent left border, italicized trigger)
3. How do you build a watchlist?
4. What makes a company worth holding long-term?
5. Do you use technical analysis?
6. What is the biggest mistake beginner investors make?

**Palantir story:** 5-paragraph essay. Covers the $9 buy-in, the $45 sale, the $150 outcome, and the framework rule derived from the experience. Formatted as an expandable accordion item with a left-border accent treatment to distinguish it visually.

---

### style.css

**CSS architecture (in order as built):**
1. `:root` CSS custom properties (color system, sidebar width)
2. Reset and base styles
3. Layout (site-wrapper flex container, site-layout grid)
4. Sidebar styles (sticky, scroll-independent, brand, nav, footer)
5. Main content area
6. Footer
7. Typography (H1 IBM Plex Serif, H2 IBM Plex Serif, H3 IBM Plex Sans, body IBM Plex Sans, mono for data)
8. Tables (header row, alternating rows, hover, ticker cells, positive/negative value coloring, 52W range bar)
9. Hero section
10. Section container
11. Metric cards (index page 2-column grid)
12. Metric blocks (metrics page full entries)
13. Accordion (FAQ page)
14. Badges (good / caution / negative)
15. FAQ teaser
16. Ticker tags (watchlist display)
17. Metrics intro header
18. Media queries: tablet (max 1023px), mobile (max 767px)
19. Reduced motion preference

**Color tokens used:**
- `--color-bg: #FAFAFA`
- `--color-surface: #FFFFFF`
- `--color-border: #E2E6EA`
- `--color-text-primary: #1A1F2E`
- `--color-text-secondary: #5A6070`
- `--color-accent: #1A6B4A`
- `--color-accent-light: #EBF5F0`
- `--color-positive: #16A34A`
- `--color-negative: #DC2626`
- `--color-warning: #B45309`

**Fonts:** IBM Plex Serif (headings), IBM Plex Sans (body/UI), IBM Plex Mono (data/ticker/numbers). Loaded from Google Fonts.

---

### script.js

**Accordion behavior:**
- Click any accordion trigger to expand its body (max-height transition, 200ms ease-in-out)
- Opening one item closes all others
- `aria-expanded` attribute toggled for accessibility
- Icon toggles between `+` and `-`

**Sidebar IntersectionObserver (metrics.html):**
- Observes all `.metric-block` sections
- When a section enters the viewport (with `-15% / -65%` root margin), the corresponding sidebar link receives `.active` class
- Provides "you are here" awareness as user scrolls through the 10 metrics

---

### Design decisions and notes

- No em dashes used anywhere in copy (per design spec)
- No gradient backgrounds, no dark mode, no chart widgets, no animations beyond accordion and sidebar highlight
- 52W Range column uses a CSS custom property `--pos` to position the dot on a 4px track bar, calculated as `(price - low) / (high - low)` as a percentage
- Potential Buys displayed as ticker tag badges rather than a full table because the source screenshot did not have legible numeric data. Can be converted to a full table format when source data is available
- PEG values below 1.0 highlighted in `--color-positive` green in the holdings table
- PEG values above 3.0 highlighted in `--color-warning` amber (ZM: 3.93)
- `PLNH` and `BRK.B` show `--` for PEG FWD as the metric is not applicable for these securities

---

## Planned Updates

- [ ] Add numeric data to Potential Buys table when Seeking Alpha source data is refreshed
- [ ] Add a "Last Updated" timestamp to both snapshot tables
- [ ] Consider adding Revenue FWD and EPS Growth FWD columns to the holdings table
- [ ] Consider adding a portfolio allocation section (% weight per holding)
- [ ] Mobile hamburger menu for the sidebar nav on small screens
