# ROADMAP.md — Implementation Plans for Planned Releases

**Version:** 4.1.5
**Last Updated:** 2026-07-10

This document holds the detailed implementation plan for every item still open on the [PRD roadmap](PRD.md#roadmap). The PRD's milestone table remains the source of truth for **what** is planned and in what order; this file is the reference for **how** each item will be built. When a release ships, its plan here is trimmed to a pointer at the PRD milestone row and the PATCHNOTES entry.

Release order (updated 2026-07-10): **v4.2.0 Market Overview: reorganize categories & mortgage rate (next up, new — both awaiting owner scope/confirmation)** → v4.3.0 Market Overview: period-return filters (new — awaiting owner scope) → v4.4.0 score sparklines (renumbered from v4.1.0) → v4.5.0 index coverage (renumbered from v4.2.0) → v4.6.0 historical examples (renumbered from v4.3.0) → v4.7.0 philosophy sections (renumbered from v4.4.0) → v4.8.0 conference call guide (renumbered from v4.5.0). (v3.34.0, v3.34.5, v3.34.6, v3.34.7, v3.34.8, v3.36.0, v3.37.0, v3.37.1, v3.37.2, v4.0.0, v4.0.1, v4.1.1, v4.1.2, v4.1.3, v4.1.0 Market Overview, v4.1.4, and v4.1.5 Market Overview expansions all shipped, most recently 2026-07-10.)

---

## v4.1.1 — Investor-vs-Trader Discipline & IPO-Timing Content — DONE 2026-07-08

Content release pulled ahead of the roadmap queue by direct owner instruction, sourced from a video transcript review: two new `philosophy.html` sections ("Investor, Not Trader" and "Why We Wait on IPOs") plus two matching `faq.html` items, generalizing the transcript's warnings into durable, non-dated doctrine consistent with the site's existing no-advice/no-live-example rules. Ticker-specific and time-bound commentary from the source video was deliberately excluded. Not previously planned in this file (jumped the queue); see PATCHNOTES.md and the PRD milestone row for the full shipped record.

---

## v4.1.3 — Docs Backfill: Sidebar Rebrand Entry — DONE 2026-07-09

The sidebar rebrand to "Azqato Invests" (with a new "Individual Stocks" sub-label) shipped as commit `b856324` earlier the same day without a PATCHNOTES entry. Logged retroactively: `.sidebar-brand a` sized up 0.9rem→1.125rem with -0.3px letter-spacing to read as a wordmark, new `.sidebar-brand-sub` muted sub-label beneath it, applied across all 8 content pages and `screener.html` via shared `style.css` rules. See PATCHNOTES.md for the backfilled record.

---

## v4.1.2 — MAG 10 Button Styling Unified with Universe Buttons — DONE 2026-07-09

Owner reported the MAG 10 button "looks weird when I click on it." The v4.0.1 fix corrected the button's *spacing* but left its segmented-control styling (`border-radius: 0 7px 7px 0`, `border-left`, `padding-left: 12px`) in place; since `.universe-group` uses `gap: 6px`, the button never actually sat flush against the universe buttons, so the squared-off left corners just looked broken once the accent border lit up on click instead of reading as an intentional divider. Fix: removed all three segmented-control overrides from `#mag10Btn` in `screener.html` — it's now a plain `.btn`, rendering identically to the universe buttons in both resting and active states. **This reverses the v4.0.1 "keep the squared-off left corner" decision**: consistency wins now that the segmented look never worked once the flex gap was in place. See PATCHNOTES.md for the shipped record.

---

## v4.0.1 — MAG 10 Button Spacing Fix — DONE 2026-07-04

Owner reported the MAG 10 button "appears different than the others" in the screener's app-bar. Diagnosed by injecting a debug script that measured `getBoundingClientRect()` for every app-bar button: the gap between International and MAG 10 was 12.0px, double the uniform 6.0px gap between every other consecutive pair. Root cause: `#mag10Btn`'s `margin-left: 6px` (added in v3.37.1, when the button moved from the tier-chip toolbar into the app-bar) stacked on top of `.universe-group`'s own flex `gap: 6px`. Fix: removed the redundant `margin-left` from `#mag10Btn` in `screener.html`, leaving the left-border divider and squared-off left corner (`border-radius: 0 7px 7px 0`) intact — those were believed at the time to be intentional visual cues that it's a filter, not an eighth universe. Re-verified with the same measurement script: all 8 gaps uniform at 6.0px. **Superseded by v4.1.2**, which found the divider styling itself was the remaining problem and removed it. See PATCHNOTES.md for the shipped record.

---

## v3.37.2 — Stale-Data Banner Threshold: 24 Hours to a Week — DONE 2026-07-04

Owner feedback: the "more than 24 hours old" banner fired too eagerly for a daily-refresh pipeline that can reasonably slip a day (weekends, a rate-limited Yahoo run) without anything actually being wrong. Raised `isStale()`'s threshold in `screener.js` from `24 * 3600 * 1000` to `7 * 24 * 3600 * 1000` ms, updated the banner copy ("more than a week old... may not have run"), the static HTML fallback text, and the two PRD mentions of the old 24-hour behavior (Common Errors table, API Design section). Verified via headless Chrome against the live feed (updated 2026-07-03, so >24h but <1 week old at test time): banner's `on` class is correctly absent under the new threshold.

---

## v3.34.10 — Screener: Scrollbar Undiscoverable/Invisible at Narrower Widths — SUPERSEDED BY v4.0.0

Diagnosis performed 2026-07-04 (kept below for the record); the fix itself never shipped. After the owner clarified the actual requirement is "the table should reflow/adapt so scrolling is never needed, not just that the existing scrollbar becomes easier to find," this item's scope was folded entirely into a reprioritized v4.0.0 (see below), since a scrollbar-visibility patch would be moot once the table auto-hides columns to fit instead of overflowing. The diagnosis below remains useful background for *why* v4.0.0 needed to happen now instead of later.

<details>
<summary>Original diagnosis (2026-07-04, read-only, no code shipped)</summary>

The v3.34.8 fix resolved the *sizing* bug (the table-wrap escaping its container) but did not fully resolve the reported issue: the table still becomes unreachable past a certain window width, for more than one person and more than one browser. Two further reports the same day, both after v3.34.8 shipped:
1. The original friend, on **Opera**, still can't scroll the ETFs table (only 10 rows — rules out vertical-height/row-count as a factor) at their native 1280×1024 resolution, maximized.
2. The owner, on **Chrome** (Incognito), reports that narrowing the browser window from the right causes the table and toolbar to stop scaling — the table just cuts off after a point, with no visible way to reach the rest.

**Diagnosis:**
1. Confirmed the v3.34.8 fix is live on the deployed site (`min-height: 0` on `.app-table-wrap`, `minmax(0, 1fr)` on `.site-layout` both present) — rules out stale cache/deployment lag.
2. Reproduced both reports' exact widths in headless Chrome against the live site (1280×1024 for the Opera report; a sweep from 1030px to 1400px for the Chrome resize report) — the scrollbar renders correctly and the box is properly sized at every width tested. Strong evidence the box-sizing bug is genuinely fixed.
3. Headless Chromium was not reproducing what two different real users, on two different Chromium-family browsers, were both experiencing — pointing at Chrome/Opera's default `overflow: auto` scrollbar rendering as a thin overlay that only appears on hover/active scrolling (invisible in a static look, and in every headless screenshot). Confirmed via a separate check: the `.app-toolbar` row (chips, Columns/Methodology buttons) already wraps correctly onto a second line at narrow widths in headless Chrome (`flex-wrap: wrap` working as designed) — the site's existing responsive infrastructure works; it's specifically the *table's* horizontal-scroll affordance that's undiscoverable.
4. The drafted (never-shipped) fix was: a persistently-visible non-overlay scrollbar via `::-webkit-scrollbar` styling, a wheel-to-horizontal-scroll redirect, and a right-edge fade affordance. **Superseded** — see v4.0.0.

</details>

---

## v3.34.8 — Screener: Horizontal Scroll Broken at Some Resolutions — DONE 2026-07-04

A friend of the owner's reported the screener table couldn't be scrolled left/right on their machine — the table simply cut off after the Growth/Valuation columns with no visible way to reach the rest, no scrollbar, no response to scroll gestures. Diagnosed and fixed the same day. **Kept as its own standalone bug-fix item, not folded into v4.0.0's mobile-friendliness pass** — this is a desktop-resolution CSS correctness bug (an existing feature silently breaking at certain DPI/zoom/window-size combinations), not a design question about phone-width layout; it needed to ship immediately rather than wait behind a broader redesign pass.

### Root cause (two compounding bugs, both classic CSS gotchas)

1. **Nested flexbox `min-height:auto`**: `.app` is `display:flex; flex-direction:column; height:100vh`, and `.app-table-wrap` (the `flex:1` child that owns the table's own scrolling) had no `min-height: 0`. A flex item's default `min-height` is `auto`, which for a large-content scroll container resolves to "big enough to fit all the content" rather than "shrink to the space I was actually given" — so the box overflowed its flex parent (fixed at `height: 100vh`) instead of triggering its own internal `overflow: auto` scrollbars. Since `body { overflow: hidden }` (screener.html relies on the app owning its own scroll regions), that overflow became invisible and unreachable.
2. **CSS Grid implicit `min-width:auto`**: the shared `.site-layout` (used by every page, in `style.css`) declares `grid-template-columns: var(--sidebar-width) 1fr` — a bare `1fr` track has an implicit minimum size equal to its content's intrinsic width, not 0. The screener's wide table (20+ columns) could force the whole `1fr` grid column, and therefore the page, wider than the viewport, again trapped by `overflow: hidden`.

Both are well-documented, browser-rounding-sensitive edge cases — exactly why this "worked on my machine" (the owner's) but broke on a different resolution: DPI scaling, zoom level, and window width all shift where the flex/grid sizing math lands relative to the content's intrinsic size, so the same page can render fine at one resolution and silently clip at another.

### Fix

- `screener.html`: added `min-height: 0;` to `.app-table-wrap`.
- `style.css`: changed `.site-layout`'s grid-template-columns from `var(--sidebar-width) 1fr` to `var(--sidebar-width) minmax(0, 1fr)`. This is a site-wide shared rule but the change is a no-op for every other page (none of them have content wide enough to hit the implicit-minimum edge case) — only the screener's table exercises the difference.

### Verified

Headless Chrome screenshots at a constrained 1366×700 viewport (simulating reduced usable height from browser chrome/taskbar), before and after:
- **Before** (bug reproduced by temporarily reverting both fixes): table clipped after the Valuation column group, chip filter counts cut off mid-row, no horizontal scrollbar visible anywhere, Columns/Methodology buttons not reachable.
- **After** (fix applied): full horizontal scrollbar visible at the bottom of the table (classic Windows-style, with arrow buttons and a draggable thumb), entire table and toolbar reachable.

---

## v3.34.5 — GitHub Actions Workflow Timing Review — DONE 2026-07-04

Owner requested review of when every GitHub Actions workflow runs and how much time sits between them. Reviewed and re-scheduled the same day; two owner decisions and the resulting schedule are below.

### Owner decisions

1. **DST**: keep a fixed (non-DST-aware) cron schedule — do not swap cron lines twice a year. But instead of anchoring to a fixed Eastern-clock offset (the old approach, which silently shifted the buffer-after-close by an hour each season), **anchor 30 minutes after the *latest possible* US market close in UTC terms**. Market close is always 4:00pm US Eastern: 21:00 UTC in winter (EST, UTC-5), only 20:00 UTC in summer (EDT, UTC-4) — winter is later in UTC. Anchoring the first job at 21:30 UTC (30 min after the winter close) guarantees at least a 30-minute buffer after close in every season, growing to 90 minutes in summer.
2. **Gap spacing**: widen every gap in the chain to a uniform 30 minutes (up from the original 15/15/30/15 mix).

### Old vs. new schedule (all times UTC)

| Workflow | Old cron | New cron | Old gap | New gap |
|----------|----------|----------|---------|---------|
| Nasdaq 100 (`screener-data.yml`) | 23:00, Mon-Fri | **21:30, Mon-Fri** | — | — |
| ETFs (`screener-data-etfs.yml`) | 23:15, Mon-Fri | **22:00, Mon-Fri** | 15 min | 30 min |
| S&P 500 (`screener-data-sp500.yml`) | 23:30, Mon-Fri | **22:30, Mon-Fri** | 15 min | 30 min |
| Growth/Value/Dividend (`screener-data-gvd.yml`) | 00:00, Tue-Sat (next day) | **23:00, Mon-Fri (same day)** | 30 min | 30 min |
| International (`screener-data-intl.yml`) | 00:15, Tue-Sat (next day) | **23:30, Mon-Fri (same day)** | 15 min | 30 min |
| Constituent sync (`constituents.yml`) | 23:00, Saturday | 23:00, Saturday (unchanged) | weekly | weekly |

A side benefit of the new anchor: since the whole chain now fits between 21:30 and 23:30 UTC, every daily job lands on the **same calendar day** — the Tue-Sat day-rollover cron pattern the GVD/International jobs needed under the old schedule is gone, and their crons simplified back to a plain `1-5` (Mon-Fri) like the others.

All six still share the `screener-data` concurrency group with `cancel-in-progress: false` (unchanged): if one run is still going when the next is scheduled to start, GitHub queues the next one rather than racing or canceling.

### Shipped

All five daily workflow files updated (`screener-data.yml`, `screener-data-etfs.yml`, `screener-data-sp500.yml`, `screener-data-gvd.yml`, `screener-data-intl.yml`), plus the `constituents.yml` comment noting the new same-day window. Docs (README, PRD pipeline section + architecture diagram + folder structure + FAQ) updated to match.

---

## v3.34.6 — International Feed: Same-Company Duplicate Holdings — DONE 2026-07-04

Owner-flagged bug fixed the same day: `005930.KS` (Samsung Electronics common) and `005935.KS` (Samsung Electronics preferred) were both in the top-100 list under different ISINs, so the v3.34.0 dedup (built only for literal duplicate-ISIN rows like BHP/Barrick) never caught it.

### Full scope found

Scanned the full ~500-row raw Vanguard response by name-normalization (stripping legal suffixes, class markers, preference-share wording) and hand-verified every candidate — this confirmed the plan's caution against automatic name-matching was warranted: the same heuristic that correctly flagged Samsung also flagged **SoftBank Group Corp vs. SoftBank Corp**, which are genuinely different, separately-traded companies (parent holding company vs. its separately-listed telecom subsidiary) — a real false positive that would have wrongly merged two distinct securities if the matching had been automatic rather than hand-checked. Three real categories of same-company duplication were found:

1. **A duplicate custody record for the identical security** (not a different share class at all): Air Liquide, L'Oreal, and Engie each had one normal-ticker line and one **blank-ticker** line (Vanguard's shortName for the blank one ends "-PRIM" for Air Liquide) — almost certainly a French registered/bearer-share settlement split reported as two rows by Vanguard's custodian. Fix: sum the weight into the ticker-bearing line, drop the blank one.
2. **A real dual share class**: Samsung Electronics common/preferred, Investor AB Class A/B, Atlas Copco Class A/B. Fix: keep the higher-weighted (more liquid) class, matching the domestic `DUAL_CLASS` convention.
3. **A dual listing of the same underlying group across exchanges**: Rio Tinto's London (plc)/Australia (Ltd) listings, CATL's Hong Kong/Shenzhen listings (tie-broken by raw market value, not the rounded percentWeight, since both showed 0.04%). Fix: keep the higher-weighted listing.

### Implementation

Added `VXUS_SAME_ISSUER_MERGE` to `update_etf_constituents.py` — a hand-verified `{kept_isin: [dropped_isin, ...]}` map (8 entries, all three categories above), applied in `fetch_vxus_raw()` immediately after the existing exact-ISIN dedup and before the top-100 cut: each dropped ISIN's weight is summed into its kept ISIN, then removed entirely. No automatic name-matching ships in production code — exactly per the plan's caution, validated by the SoftBank false positive.

### Result

Rebuilding `data/vxus.json` against the live Vanguard API: Samsung preferred (`005935.KS`) dropped as expected, and correctly-combined weights promoted **L'Oreal** (`OR.PA`, 0.07%+0.14%=0.21%) and **Investor AB** (`INVE-B.ST`, 0.16%+0.04%=0.20%) into the true top 100, bumping out two lower-weighted names that had been ranked ahead of them under the old split-weight accounting (only Rio Tinto's Australian listing and CATL's Shenzhen listing were already below the cutoff on either side, so those two merges didn't change today's membership, just future-proof it). `data/vxus_map.json`'s now-unreachable manual override for Air Liquide's dropped ISIN was removed. `screener.js`'s `CURRENCY_SYMBOLS` gained `SEK` (Investor AB introduced Swedish krona to the feed).

### Verified

- `data/vxus.json`: 100 entries, 100 unique symbols, exactly one Samsung Electronics entry (Samsung Electro-Mechanics correctly remains separate — it's a genuinely different company).
- Headless Chrome: 100/100 rows rendered, no duplicate company names, tiers sum to 100.
- `sync_vxus()` re-run against the live Vanguard API twice (once before, once after removing the dead manual override) both reproduced the corrected list with zero further changes — full idempotency confirmed.

---

## v3.34.7 — International Universe: Lead with Company Name, Not Ticker — DONE 2026-07-04

Owner-requested display change shipped the same day, following the plan below exactly.

### Implementation

- **`UNIVERSES.intl`** gained `nameFirst: true` (absent/falsy on all five domestic universes, so nothing about them changes — verified below).
- **`screenCells(r)`** now checks `isNameFirst()` and, when true, swaps both the DOM order (name span first, for screen readers) and adds a `name-first` class to the `<td class="col-ticker">` cell.
- **CSS** (`screener.html`): new `.col-ticker.name-first .tkr-name` / `.tkr` rules swap which span gets the prominent styling (name: bold, proportional font, primary text color; ticker: small, muted, keeps the inherited monospace from `tbody td`). The 720px mobile breakpoint rule was generalized from unconditionally hiding `.tkr-name` to hiding whichever span is secondary in the active mode (`.col-ticker:not(.name-first) .tkr-name` vs. `.col-ticker.name-first .tkr`).
- **Header label**: new `updateTickerColumnLabel()` in `screener.js`, called on every `activate()`, sets the `data-sort="ticker"` header cell to "Company" when `isNameFirst()` and "Ticker" otherwise — skipped entirely in ETF mode, whose own "Fund" label comes from its separate `HEADS.etf` entry via the existing kind-change `renderHead()` path. A tiny DOM patch rather than growing `HEADS` into a third dimension, exactly as planned.
- **Sorting**: the `ticker` sort key now compares `a.name.localeCompare(b.name)` when `isNameFirst()`, matching what a user visually scanning company names would expect; every other universe is unchanged (still sorts by ticker string).
- **Per-stock popup**: `openStock()` now sets the modal title to the company name and the subtitle to the ticker when `isNameFirst()`, mirroring the table row's lead/secondary swap; unchanged for every other universe.

### Verified

- Headless Chrome, International universe: header reads "Company", first row's `col-ticker` cell is `<span class="tkr-name">Samsung Electronics Co.</span><span class="tkr">005930.KS</span>` with the `name-first` class present, 100/100 rows, no console errors.
- Headless Chrome, Nasdaq 100 (regression): header still reads "Ticker", cell is the original `<span class="tkr">MU</span><span class="tkr-name">Micron Technology</span>` with no `name-first` class, tiers exactly match the v3.31.0 baseline (2 S+ / 10 S / 8 A / 32 B / 24 C / 24 F, MU at top) — the `nameFirst` flag is a confirmed no-op everywhere it's absent.

---

## v3.35.0 — RETIRED, MERGED INTO v4.0.0

This item's number is retired. Its scope (the `.table-wrap` CSS display bug in the methodology modal, plus a content-currency audit of `#methodStock`/`#methodEtf`) is folded into v4.0.0 (Screener Responsive Redesign & Site-Wide Mobile-Friendliness Pass) — both are screener table/layout work, and splitting them across two releases would mean touching the same table rendering twice. See the v4.0.0 section below for the full combined plan.

---

## v3.36.0 — "MAG 10" Filter — DONE 2026-07-04

Implemented exactly per plan, no deviations. Hardcoded `MAG10_TICKERS` array in `screener.js` (no separate JSON file, per the plan's judgment call — 10 fixed tickers didn't warrant one). New `mag10Active` state, `#mag10Btn` toggle button, `toggleMag10()` switches the active universe to S&P 500 (via the existing `selectUniverse()` lazy-load path) if not already active, then the filter ANDs into `render()`'s existing `view = rs.filter(...)` step alongside the tier chip and search box. Manually switching to a different universe button while the toggle is active turns it off automatically.

**Button placement, revised same day**: originally placed next to the tier-chip group in the toolbar row; owner asked to move it to the top app-bar, to the right of the International universe button. Moved into `#universeGroup` (inherits the row's `flex-wrap` spacing) with a left-border/margin to visually separate it from the universe buttons, since it's a filter toggle, not an eighth universe. `#mag10Btn`'s ID-based click binding and CSS were unaffected by the DOM move.

**Verified** (headless Chrome, script-injected click since no Selenium/chromedriver was available in this environment): confirmed all 10 tickers exist in `data/sp500.json` first. Toggling on switches the universe label to "S&P 500", scores against the full 500-stock set (summary line unchanged: "5 S+ · 49 S · 51 A · 147 B · 124 C · 124 F · 500/500 scored"), and shows exactly the 10 MAG 10 rows (META, NVDA, AMD, GOOGL, AVGO, MSFT, NFLX, AMZN, AAPL, TSLA). Combined with the tier-S chip: correctly ANDs down to the 5 MAG 10 names that are also tier S (AMD, GOOGL, AVGO, MSFT, NFLX). Re-verified after the button move with a screenshot: correctly positioned to the right of International, active-state highlight renders, universe switch and filter still work. Nasdaq 100 default-load regression check: exact match to the v3.31.0 baseline, confirming zero impact on existing behavior.

### Goal (original plan, retained below)

Owner-requested filter for a fixed 10-stock watchlist, the "Magnificent Ten" mega-cap names. Renamed from the original "FANG+" placeholder once the owner supplied the actual list (2026-07-04):

**AAPL, AMD, AMZN, AVGO, GOOGL, META, MSFT, NFLX, NVDA, TSLA**

### Design direction

Requested as **a filter**, not a new universe — narrows the visible rows to just these 10 names within a loaded dataset, reusing 100% of existing scoring/rendering:

1. **No new feed or scoring path.** The filter operates purely client-side; a stock's score, tier, and every column stay exactly as already computed — the filter only changes which rows are visible.
2. **Sourced from the S&P 500 data specifically** (owner instruction: "use the S&P 500 data for reference of these stocks"), not whichever universe happens to be active. All 10 names are S&P 500 constituents, so this guarantees complete, consistent data and means each stock's score/tier reflects its percentile rank among the full 500-stock S&P universe — the most meaningful reference set for mega-caps, rather than a smaller or differently-composed universe. Toggling the filter on switches the active universe to S&P 500 (loading it if not already cached, same lazy-load path every other universe button uses) and applies the ticker-membership filter on top.
3. **This is an orthogonal filter axis, not another tier chip.** ANDs with the existing tier-chip filter and the search box rather than replacing them (e.g. "MAG 10 stocks that are also tier S" should be a valid combination) — implemented as a separate toggle button near the tier group.
4. **Store the list in a small `{"name","tickers"}` shape** (matching the pattern already used for `vxus_map.json`'s override blocks) rather than a bare array, so a future curated-watchlist request costs nothing extra.

### Plan

1. Hardcode the 10-ticker list in `screener.js` (small and fixed; no separate JSON file needed for just 10 tickers, unlike the ~100-entry universe lists).
2. Add a `mag10Active` toggle state and a "MAG 10" button near the tier chip group.
3. Clicking the button: if S&P 500 isn't the active universe, switch to it (reusing `selectUniverse("sp500")`); then apply the ticker-membership filter in `render()`'s `view = rs.filter(...)` step, ANDed with the existing tier/search filters.
4. Switching to a different universe via the normal universe buttons while the filter is active turns it off automatically (the filter is meaningfully tied to S&P 500 data specifically, not a general cross-universe toggle).

### Verification

- Confirm all 10 tickers exist in `data/sp500.json` before implementing (guards against a silent missing row).
- Toggle on: confirm exactly these 10 rows show, scored/tiered relative to the full S&P 500 (not just the 10); toggle off: full S&P 500 list returns.
- Combine with a tier chip and the search box to confirm all three filters AND correctly.
- Switching to a different universe button while the toggle is active turns the filter off (doesn't leave a confusing stale state).

---

## v3.37.0 — ETFs Universe: Rating Methodology Review — DONE 2026-07-04 (doctrine write-up completed under v4.0.0)

Owner flagged 2026-07-04 that the ETFs universe scoring methodology (v3.33.0: Technicals 50 / Performance 30 / Income & cost 20, rank-linear points across the fixed 10-fund list) needed a review. Current methodology presented in full and cross-checked against `indices.html`'s own doctrine, surfacing three gaps (below). Owner decided on the scoring change; shipped the same day. The `indices.html` doctrine write-up for Price vs 200-Day MA (item 2 below) was completed as part of v4.0.0's scope — see that section for the as-shipped subsection.

### Findings from the `indices.html` doctrine review

The page states its own framework explicitly: "The nine metrics on this page split into two groups. Four are timing signals (VIX, RSI, 52W Range, AAII Sentiment)... Five are structural quality signals (YTD Performance, 5Y Return, 10Y Return, Yield, Expense Ratio)." Comparing to the shipped screener model surfaced three gaps:

1. **VIX and AAII Sentiment are absent from the screener entirely** — both are market-wide signals (one reading, not one per fund), so they structurally can't differentiate scores across the 10-fund relative-ranking model. An accepted limitation, not a bug.
2. **Price vs 200-Day MA (10 pts, scored) has no grounding in `indices.html`'s doctrine.** The page names only RSI and 52-Week Range as ETF timing technicals. **Owner decision (2026-07-04): document this metric on the indices page rather than remove it from the screener** — write a Price vs 200-Day Moving Average subsection into `indices.html`'s Timing Signals section (alongside RSI and 52W Range). **Done under v4.0.0** — see that section below.
3. **YTD Performance is named in doctrine as one of the five structural signals but is unscored context in the screener**, which instead scores 1-Year Total Return (not named in doctrine). Owner declined to promote YTD (see decision below); this gap remains, unaddressed by design.

### Scoring change — DONE 2026-07-04

Owner requested removing Yield and Expense Ratio from scoring. Recommendation presented (promote YTD to a scored metric) was declined; owner instead chose to weight up the two longest return horizons: **5-Year Total Return 10→20, 10-Year Total Return 10→20**, keeping 1-Year Total Return at 10. Final model: **Technicals 50 (unchanged: RSI 20, 52W Range 20, vs 200-Day MA 10) + Performance 50 (1Y 10, 5Y 20, 10Y 20) = 100.** Yield and Expense Ratio demoted to weight-0 context columns (same treatment as YTD, net yield, and the 20/100-day MAs) rather than removed from the table entirely, consistent with how the stock model demotes P/E FWD to context instead of deleting it.

**Implementation**: `ETF_METRICS` in `screener.js` updated (weights only, no structural changes); `ETF_POPUP_METRICS` updated to match (Yield/Expense Ratio entries removed from the popup breakdown, matching how weight-0 metrics are already excluded from the stock model's `POPUP_METRICS`); column header titles updated to mark Yield/Expense Ratio "context only, not scored" and to explain the 5Y/10Y double-weighting; `#methodEtf` pillar table and lead paragraph rewritten (Technicals 50/Performance 50, "six scored metrics" not eight); Factors chip denominator auto-updates via existing `scoredCount` logic (no code change needed there).

**Verified**: headless Chrome on the ETFs universe — 10/10 scored, tiers 1 S / 1 A / 3 B / 3 C / 2 F, Factors chip correctly shows `/6`, all context columns (Yield, Expense Ratio, Yld−ER, YTD) still visible and colored via `colorFromPts`. Nasdaq 100 regression: exact match to the v3.31.0 baseline, confirming zero impact on stock universes.

### Plan (remaining)

Done — see v4.0.0 below for the as-shipped `indices.html` write-up.

---

## v3.34.0 — Screener: International Universe (VXUS Top 100) — SHIPPED 2026-07-04

Fully built and verified; see [PRD.md](PRD.md#roadmap) (milestone table + Data Pipeline + Data Model sections) and [PATCHNOTES.md](PATCHNOTES.md) for the as-built record, including two data quirks the probe below didn't anticipate (a Vanguard split-ISIN duplicate and Yahoo's pence-not-pounds London quoting). The plan below is kept for historical reference.

<details>
<summary>Original plan (superseded by the as-built record above)</summary>

### Goal

A seventh screener universe: the top 100 holdings of VXUS (Vanguard Total International Stock ETF), scored with the **same six-metric stock model** as the other stock universes (Growth 60 / Valuation 20 / Balance sheet 20, hard-zero missing data, S+/S/A/B/C/F tiers). This is a stock universe, not an ETF universe: it reuses the stock table, columns, and scoring path with zero changes to the scoring math.

### Why this is its own release

Three problems the domestic universes never had, each needing its own solution:

1. **Symbol mapping.** Vanguard reports VXUS holdings with local-exchange tickers and no exchange suffix (`2330` for TSMC, `NESN` for Nestlé). Yahoo needs suffixed symbols (`2330.TW`, `NESN.SW`). A mapping layer is required.
2. **Currency display.** yfinance returns prices in each listing's local currency (TWD, CHF, JPY, EUR…). The screener's Price and Cash/Debt columns are currently formatted as dollars.
3. **Sparse analyst estimates.** Forward revenue/EPS estimates and PEG are thinner for foreign listings. Under the hard-zero rule, poor coverage could zero out 50 of 100 points for a large share of the list.

### Phase 0 — Probe (complete 2026-07-03)

Mirrored the approach that de-risked v3.33.0: verified empirically before writing production code. Findings:

1. **Vanguard holdings API shape.** The endpoint (`.../profile/api/VXUS/portfolio-holding/stock`) does **not** return all ~8,500 VXUS holdings — it caps at exactly **500** entities, weight-sorted. That's actually convenient (no pagination to build), but it changes the Phase 1 sanity-check band: the guard should assert **exactly 500** returned (or a tight band around it, e.g. 480-520), not the wide 110-500 band used for VUG/VTV/VIG. Every entity carries an **ISIN** directly (`"isin": "TW0002330008"`), plus a `sedol` field — no separate lookup call needed to get an identity key. Top-100-by-weight coverage sums to 37.4 of the fund's 65.5% visible weight in the 500-row response, consistent with a long, thin international tail below that.
2. **Symbol resolution ladder, tested on the real top 100 holdings:**
   - **Rung 1 — ISIN → Yahoo search** (`query2.finance.yahoo.com/v1/finance/search?q=<ISIN>`): resolved **99/100** with exactly one EQUITY hit each (2330 → `2330.TW`, NESN → `NESN.SW`, 8306 → `8306.T`, etc.). Three names returned more than one EQUITY match (dual-listing cases: Alibaba HK/Singapore, Siemens DE/Frankfurt-classic, Siemens Energy DE/Stuttgart) — first hit (primary listing) was correct in all three on inspection.
   - **Rung 2 — name search fallback**: the one ISIN miss (Air Liquide, `FR0000053951` — Vanguard's raw entity had a blank `ticker` field) resolved cleanly by name search to `AI.PA`, its primary Paris listing.
   - **Net result: 100/100 resolvable** with the two-rung ladder as planned. No case needed the market-cap/country validation step; it stays in as a guard for future weeks' new entrants, not because today's data needed it.
3. **Field coverage on the resolved top 100**, using the exact yfinance fields `fetch_screener_data.py` reads (not approximations): `revenueGrowth` (revTTM) 94/100, `earningsGrowth` (epsTTM) 88/100, current-FY `revenue_estimate` growth (revFwd) 100/100, current-FY `earnings_estimate` growth (epsFwd) 98/100, `pegRatio`/`trailingPegRatio` (pegFwd) 100/100, `totalCash`/`totalDebt` 100/100. **This resolves the sparse-estimates worry**: coverage is 88-100% across all six scored inputs, and because the hard-zero rule already applies **per metric, not per stock** (screener.js `activeMetrics()`/`ETF_METRICS` pattern: a missing input zeros only its own weight, the /100 denominator never shrinks), the worst case is roughly a dozen names losing 10 of 100 points on `epsTTM` alone — a minor haircut, not the "zero out 50 of 100 points" scenario the original concern envisioned.
4. **Currency diversity confirmed material**: even the top 15 holdings alone span TWD, KRW, EUR, GBP, JPY, CHF, HKD, CAD. This settles the currency-display decision in favor of the native-currency-with-label recommendation below — a single reporting currency was never realistic for this universe.

Deliverable (this section) presented to the owner 2026-07-03; Phase 3 decisions below are now data-backed rather than speculative.

### Phase 1 — Constituents and mapping

1. **`data/vxus.json`** — same `[{"t","n"}]` shape as the other lists, but `t` holds the **Yahoo symbol** (suffixed), so the data fetcher needs no special casing.
2. **`data/vxus_map.json`** (new, committed) — the resolution cache: Vanguard identity (ISIN, keyed off the `isin` field Vanguard already returns) → Yahoo symbol, plus a `manual` override block that the sync script always honors (seed it with the Air Liquide case and the three confirmed dual-listing picks found in the probe). This makes weekly syncs cheap (only newly added holdings need resolution) and makes bad auto-resolutions correctable by hand-editing one file.
3. **Extend `update_etf_constituents.py`** with a `vxus` entry: fetch holdings, take top 100 by weight, resolve each through the cache (hitting Yahoo search only for cache misses: ISIN first, name-search fallback second, per the tested ladder), apply the same never-clobber sanity checks (raw count in the 480-520 band per the probe finding above, no duplicates, plus a new check: every symbol must have resolved; abort rather than write a partial list). The existing ticker regex `^[A-Z][A-Z.]{0,5}$` must be relaxed for this fund only (digits and exchange suffixes: `2330.TW`, `005930.KS`, `AI.PA`).
4. Weekly sync joins the existing Saturday 23:00 UTC `constituents.yml` job.

### Phase 2 — Feed

1. Reuse **`scripts/fetch_screener_data.py`** unchanged if possible (`--list data/vxus.json --out data/screener_intl.json`); it already takes list/out arguments. Additions if needed: capture `info["currency"]` per ticker into a new feed field `cur`, and market cap left in native currency.
2. New workflow **`screener-data-intl.yml`**: Tue-Sat 00:15 UTC (15 minutes after the GVD job, keeping the stagger), same `screener-data` concurrency group, same pinned `yfinance==1.4.1`, `[skip ci]` commit.
3. Seed the feed with a local run before shipping, as with every prior universe.

### Phase 3 — Owner decisions (all locked 2026-07-03)

1. **Currency display — LOCKED: native currency, labeled with the currency symbol where one exists.** Numbers render in each stock's local currency using its **symbol**, not the 3-letter code, wherever a standard symbol exists (e.g. `NT$2,445` for TWD, `₩309,500` for KRW, `€284.10` for EUR, `£` for GBP, `¥` for JPY, `HK$` for HKD, `C$` for CAD). Fall back to the 3-letter ISO code (e.g. `CHF`) only for currencies with no widely recognized symbol or where the symbol is ambiguous with `$` alone (e.g. distinguish `HK$`/`NT$`/`C$` rather than a bare `$`, since the site's existing `$` always means USD elsewhere). No FX-rate feed dependency; scoring is unaffected either way — all six scored metrics are growth rates and ratios, currency-agnostic by construction.
2. **Sparse estimates — resolved by the probe, no owner decision needed.** Coverage on all six scored inputs is 88-100% (worst case `earningsGrowth`/epsTTM at 88/100). Keep the hard-zero rule exactly as-is: no shrunk denominator, no dropped names. The methodology popup gets one added sentence noting that a small number of international names may show a lower Factors count where Yahoo's analyst coverage is thin, same framing as the existing hard-zero note for domestic stocks.
3. **ADR preference — LOCKED: rank the local listing.** Rank the local listing that Vanguard actually holds (that's what the fund owns and what should be scored); use a liquid US ADR only as a manual-override fallback in `vxus_map.json` for the rare case where the local line has no Yahoo data at all — none of the top 100 needed this in the probe, so the fallback path may simply go unused at launch.

**All three Phase 3 gates are now clear. Phase 1 (constituents and mapping) can begin.**

### Phase 4 — Frontend

Small by design, because v3.33.0 pre-paid for it:

1. Add `intl` to `UNIVERSES` in `screener.js` with `kind` omitted (stock kind), paths to `screener_intl.json`, its own cache key. Seventh button in `screener.html` plus meta/disclaimer updates.
2. Thread the `cur` field (ISO code from `info["currency"]`) through `rows()` and the Price/Cash/Debt cell formatters for stock mode (no-op for feeds without `cur`, so the five domestic universes render exactly as before). Add a small `CURRENCY_SYMBOLS` lookup (ISO code → symbol: `TWD → "NT$"`, `KRW → "₩"`, `EUR → "€"`, `GBP → "£"`, `JPY → "¥"`, `HKD → "HK$"`, `CAD → "C$"`, `CHF` has no fallback so it prints the code, plus entries for any other currency the resolved top 100 turns up) so formatting is a plain object lookup, not per-currency branching logic. Unknown/unmapped codes fall back to printing the ISO code itself.
3. Methodology popup: one paragraph in the stock section's universe-source table (VXUS top 100, Vanguard holdings API, local listings, currency note, estimates-coverage note).

### Verification and acceptance

- Headless-Chrome check on the ETF universe pattern: all rows render, tier counts sum to 100, popup opens on a suffixed symbol (`.TW`, `.SW` in element IDs/selectors must not break — probe for selector-safety, dots in tickers already exist as `BRK.B` so `data-ticker` handling is likely fine but must be confirmed).
- **Stock regression is mandatory**: Nasdaq 100 headless run must still match the v3.31.0 baseline (2 S+ / 10 S / 8 A / 32 B / 24 C / 24 F, MU and NVDA at 100, subject to that day's data).
- Feed run completes 100/100 tickers with retries; nulls only where Yahoo genuinely has no data.
- All four docs updated; PATCHNOTES entry; PRD milestone flipped to Complete.

### Risks

- Vanguard may paginate or shape the VXUS response differently at ~8,500 holdings (the sibling funds return a few hundred). The probe settles this.
- Yahoo search rate limits during first-time resolution of 100 names: resolve with a pause and cache aggressively; this cost is paid once.
- yfinance field names for foreign listings can differ in reliability (the v3.33.0 lesson: verify `dividendYield`-class traps per field, per market, before trusting them).

</details>

---

## v4.1.4 — Market Overview: Expanded Symbol List, Renames, Sectioned Placeholders — DONE 2026-07-10

Follow-up owner requests, same day as v4.1.0 shipped, made iteratively while testing the live page:

- **Renames** (shorter card labels): "Dow Jones 30"→"Dow Jones", "US Total Market"→"US Market", "International Total Market"→"International Market", "Dividend Appreciation"→"Dividend", "Volatility Index"→"Volatility".
- **6 new benchmark symbols added** to the main grid: TLT (Long-Term Bonds), RSP (S&P 500 Equal Weight), SPMO (Momentum), VBR (Small-Cap Value), IJH (Mid-Cap), IJR (Small-Cap), XLP (Consumer Staples) — 17 symbols in the `benchmarks` group total.
- **Reordered** so SPY, QQQ, VIX lead the grid (previously DIA led).
- **Removed** the "This is a snapshot, not the screener" explainer callout entirely, per owner request — the page now goes straight from the intro to the data.
- **New grouped-section architecture**: `data/market_overview_list.json` entries gained a `"g"` (group) field (`benchmarks`, `industries`, `leveraged`), which `fetch_market_overview.py` now copies through into each quote's `"group"` field in `data/market_overview.json`. This let `market.html` drop its previously-hardcoded `ORDER` array entirely — the frontend now iterates `Object.keys(feed.quotes)` (JSON preserves insertion order, which matches the list file's order) and buckets by `group`, rendering each into its own `.market-section` with a heading, hidden automatically if empty. This removes a config-drift risk: before this change, the symbol list and the display order lived in two separate places (`market_overview_list.json` and a hardcoded JS array) that had to be kept in sync by hand on every symbol add.
- **New "Industries" section**: placeholder, seeded with one symbol (VNQ, Real Estate). Meant to grow one symbol at a time per future owner requests.
- **New "Leveraged ETFs" section**: placeholder, seeded with one symbol (TQQQ, 3x Nasdaq 100).

### Verified

- `fetch_market_overview.py` re-run after each change: 11, then 14, then 16, then 17, then 19 symbols (final), all with live price data.
- Headless Chrome, network-blocked to `raw.githubusercontent.com` to force the local-fallback data path (necessary since the previous v4.1.0 push already made old data live at that URL, which headless Chrome would otherwise fetch instead of the local copy under test): confirmed SPY/QQQ/VIX lead the grid, all renames applied, Industries and Leveraged sections render with their single placeholder symbols and correct headings, explainer callout fully removed.
- TQQQ's live change (+4.98%) sanity-checked against QQQ's same-day move (+1.66%) — roughly the expected ~3x leveraged relationship, a good real-data confirmation that the leveraged-fund price data is being read correctly (not a validation of the fund's actual daily-reset leverage mechanics, which can drift from a clean 3x over any period longer than one day).

---

## v4.1.0 — Market Overview Page — DONE 2026-07-10

### Goal

A new standalone page, styled as a CNBC-style card strip, showing at-a-glance price/change for the market's major broad benchmarks: DIA (Dow), SPY (S&P 500), QQQ (Nasdaq 100), IWM (Russell 2000), VTI (US Broad Market), VXUS (International Broad Market), VUG (Growth), VTV (Value), VIG (Dividend), and VIX (Volatility Index). Owner decisions locked 2026-07-09 (via AskUserQuestion): **new standalone page** (not a widget on an existing page); **prioritized ahead of v4.1.0 sparklines** (this is the new v4.1.0; sparklines and everything after shifted down one, see the renumbering note in PATCHNOTES.md/this file's release-order line). Cadence was initially locked as a once-daily batch snapshot matching the rest of the site, then **changed mid-build to intraday**, three times per trading day, per direct owner instruction (see Cadence below) — this page is meant to feel like a same-day market check-in, not a close-of-business number.

### Scope boundary (owner-set)

This is a snapshot display, explicitly **not** the screener: no scoring, no tiers, no percentile ranking, no per-metric breakdown popup. Just symbol, name, last price, change, %change, and a "last updated" timestamp per card.

### Cadence (revised mid-build)

Originally scoped as a once-daily refresh alongside the rest of the site's pipeline. The owner asked, mid-implementation, for three updates per trading day instead: **15:00, 19:00, 22:00 UTC** (shortly after the US open, midday, and shortly after the US close). This is the only workflow in the pipeline that isn't once-daily-after-close; every other feed stayed on its existing schedule. The stale-data banner threshold was recalibrated from the screener's 7-day threshold down to **4 days**, since a 3x/day cadence makes 7 days too loose to mean anything, but a shorter threshold like 24 hours would falsely flag every ordinary weekend (Friday's 22:00 UTC run to Monday's 15:00 UTC run is already ~65 hours; a Monday holiday pushes it to ~89 hours) — 4 days safely covers a holiday weekend while still catching a genuinely stuck pipeline well before a week passes.

### Data

1. **VIX is an index, not a fund** — Yahoo symbol `^VIX`, no shares/volume/AUM fields, only price data. Every other symbol is a normal ETF. `data/market_overview_list.json` carries both a `t` (display ticker) and `y` (Yahoo fetch symbol) column so VIX's `^VIX` fetch symbol never leaks into the display — no other special-casing was needed since the script only reads price fields.
2. New lightweight `scripts/fetch_market_overview.py`, deliberately not an extension of `fetch_etf_data.py`: this only needs price and previous close (no returns history, RSI, or technicals), and staying independent means the scored ETFs list (`data/etfs.json`) can change without Market Overview following it.
3. Output: `data/market_overview.json`, `{"updated": ..., "source": "yahoo", "quotes": {"DIA": {"name": ..., "price": ..., "prevClose": ..., "change": ..., "changePct": ...}, ...}}`.
4. Workflow: `.github/workflows/market-overview.yml`, three cron entries (15:00/19:00/22:00 UTC, Mon-Fri), sharing the `screener-data` concurrency group with `cancel-in-progress: false` — the 22:00 run lands the same minute as `screener-data-etfs.yml`'s daily job, so the two simply queue rather than race.

### Frontend

1. **New page `market.html`**, self-contained (its own inline `<style>` and `<script>`, no shared JS file needed for a page this size), following the existing guide-page sidebar/nav pattern.
2. **Card grid**: one card per symbol in the owner-specified fixed order, showing name, ticker, last price, change arrow, change, and %change. Colored via a top accent border + colored change text using the site's existing `--color-positive`/`--color-negative` tokens — a solid CNBC-style fill was considered and rejected as inconsistent with the site's existing dark-theme, subtle-tint visual language (the same formula `.badge-good`/`.badge-negative` already use). "As of" timestamp and a stale-data banner reuse the screener's established pattern.
3. Responsive: `grid-template-columns: repeat(auto-fill, minmax(220px, 1fr))` reflows the grid naturally at any width; verified zero horizontal overflow 375-1920px via the v4.0.0 methodology (`scrollWidth === clientWidth`, not screenshots alone) plus a 700px screenshot confirming the 2-column mobile layout.
4. Navigation: new "Market Overview" nav item added to all 9 pages (11th nav item total, inserted between Screener and Finviz), `sitemap.xml` entry added.
5. Content rule check: falls under the same labeled real-time-data exception the screener already has, since this displays live-ish market data rather than editorial content.

### Decisions made during build (no further owner input needed)

1. Filename/nav label: `market.html` / "Market Overview".
2. Card order: fixed list order exactly as the owner specified (DIA, SPY, QQQ, IWM, VTI, VXUS, VUG, VTV, VIG, VIX).
3. Card content: kept minimal (price, change, %change only) — no day range, no mini sparkline. A sparkline can be revisited once v4.2.0's score-history infrastructure exists, but Market Overview's benchmarks are outside that system's scope (it mines the *scored* universes' git history) so this would need its own follow-up design, not an automatic carry-over.

### Verified

- `scripts/fetch_market_overview.py` run against live data: 10/10 symbols fetched successfully, including `^VIX`.
- Headless Chrome: all 10 cards render with correct data; correct green/red coloring confirmed against a live run where VIX was down and every ETF was up (exercising both color paths); responsive sweep 375-1920px shows zero overflow at every width tested.
- `screener.html`'s new nav-link line confirmed non-breaking via headless dump (tier counts intact modulo normal weekly constituent drift, unrelated to this change).

---

## v4.1.5 — Market Overview: Bond Yields, Commodities, Crypto & UI Polish — DONE 2026-07-10

Same-day continuation of v4.1.4, adding three new data categories and fixing a rendering bug found along the way.

### Bond yields

Owner asked for yields specifically (a CNBC "Bonds" tab reference screenshot: "4.541%" + "+0.002", not a fund's price/%-change). Data-source probe: **US Treasury yields work directly via yfinance**, already in percent (no `/10` scaling needed) — `^TNX` (10-Year, 4.539), `^TYX` (30-Year, 5.053), and `2YY=F` (2-Year Yield Futures — `^UST2Y`/`^US2Y` don't exist on Yahoo, this is the closest working proxy, 3.886). **Foreign sovereign yields are NOT available**: every plausible ticker for German Bund, UK Gilt, and Japan JGB (`DE10Y-DE`, `GB10Y-GB`, `JP10Y-JP`, `DE10YT=RR`, and the CNBC-style `US10Y:Tradeweb` format) returned HTTP 404. **A CNBC-identical multi-country curve is not achievable with this site's free data source** — shipped US-only (2Y/10Y/30Y), scope corrected and confirmed with the owner. New `"unit": "pct"` field on yield entries in `data/market_overview_list.json`, read by `fetch_market_overview.py` (passed through to the feed) and `market.html` (a distinct card renderer: price shown as `X.XXX%`, change shown as a bare point-delta like `+0.030` rather than a percent-of-percent, which would misleadingly read a 0.03-point move as "+0.66%"). Direction-only green/red coloring, same convention as every other card (rising yields aren't "good," just a direction).

### Commodities and Crypto

Gold (`GLD`) and Oil (`CL=F`, the front-month WTI crude futures contract) both work through the exact same `Ticker.info` price/prevClose mechanism as everything else — no special API needed, so nothing went to the roadmap for these. Same for Bitcoin (`BTC-USD`). New "Commodities" and "Crypto" sections, same placeholder-group pattern as Industries/Leveraged.

### Bug found and fixed

`render()`'s `byGroup` bucket object was hardcoded to `{ benchmarks, industries, leveraged }` — adding `yields`/`commodities`/`crypto` groups without updating that literal silently misrouted every new group's cards into the `benchmarks` bucket (fell through the `byGroup[group] || byGroup.benchmarks` fallback). Fixed by deriving `byGroup`'s keys from `GROUP_GRIDS` instead of a second hardcoded list. Caught via the network-blocked headless screenshot below, not by inspecting the code — worth remembering: a config-driven grouping system still needs its *initialization* to be config-driven, not just its lookup.

### UI polish (owner requests, same session)

- "Benchmarks" section retitled **"Indices"** with a visible `<h2>`, matching the other sections instead of being the one unlabeled group.
- Removed the "📊 Market Snapshot" hero badge.
- The "Last updated" timestamp restyled as a `.hero-badge` pill (reusing the site's existing badge component) with a clock emoji, moved inside `.guide-intro` (after the description, before the divider) rather than sitting below it.
- Tightened vertical rhythm: `.market-asof`'s own margin zeroed out (it sits inside `.guide-intro`, which already supplies 40px of padding-bottom — the badge's default margin-bottom was stacking dead space on top of that), `.market-section` margin-top reduced 40px→24px, `.market-grid` margin-top increased 8px→16px (heading-to-first-card gap was too tight the other direction).

### Verified

- `fetch_market_overview.py` run against live data: 25/25 symbols across all 6 groups.
- Headless Chrome with `raw.githubusercontent.com` network-blocked (necessary again — the v4.1.4 push had already made intermediate data live at that URL): confirmed all 6 sections (Indices, Bond Yields, Industries, Leveraged ETFs, Commodities, Crypto) render independently with correct data after the bucket-bug fix; yield cards show percent + point-delta formatting correctly; spacing changes visually confirmed via a top-of-page screenshot.

### Not built (remaining gaps, folded into v4.2.0 below)

**Mortgage rate** (owner request): no Yahoo Finance ticker exists for the 30-year mortgage average — every plausible guess (`^MORTGAGE30US`, `MORTGAGE30US`) 404'd. This is genuinely a different data source (FRED's `MORTGAGE30US` series, or a Freddie Mac PMMS scrape), not a yfinance gap that more ticker-guessing will close.

---

## v4.2.0 — Market Overview: Reorganize Categories & Mortgage Rate

### Goal

Two open items, logged together since both are small and unscoped pending owner input:

1. **Reorganize categories** (owner request, 2026-07-10, no specifics given yet). The page now has 6 sections (Indices, Bond Yields, Industries, Leveraged ETFs, Commodities, Crypto) added incrementally over one session — worth a deliberate pass on ordering, grouping, and whether "Indices" (17 symbols) should itself be split (e.g. broad index / factor-tilt / sector subgroups) now that it's grown well past the other sections. **Do not guess a new structure** — wait for the owner's specific direction on what "reorganize" means before touching section order or the grouping scheme.
2. **Mortgage rate**: needs a non-yfinance data source. FRED's public API (`MORTGAGE30US` series, weekly Freddie Mac PMMS data) is the most likely candidate — free, no scraping fragility, but does require a FRED API key (free to obtain) and a second fetch mechanism alongside yfinance in `fetch_market_overview.py`, or a small dedicated fetch step. Needs a probe (confirm the FRED API's actual response shape and key-acquisition process) before committing to the design, same probe-first approach as the bond-yields item above.

### Owner confirmation needed before implementation starts

Both items need owner input before work begins: specifics on what "reorganize" should produce, and a decision on whether a FRED API key is acceptable (this site has otherwise been entirely key-free, so this would be a first).

---

## v4.3.0 — Market Overview: Period-Return Filters

### Goal

Owner request (2026-07-10): filters for YTD, 12-Month, 5-Year, and 10-Year returns on Market Overview, presumably so a card can show a longer-horizon return instead of (or alongside) today's change from the previous close.

### Scope note

This is a materially bigger feature than every other Market Overview addition so far. Every existing card is driven by a single lightweight `Ticker.info` call (`regularMarketPrice`/`regularMarketPreviousClose`) — todays-only data. Multi-year returns require actual price **history**, not a snapshot: the same kind of `t.history(period="11y", ...)` pull `fetch_etf_data.py` already does for the scored ETFs universe (`ret1y`/`ret5y`/`ret10y`/`ytd`, computed on dividend-adjusted closes for a true total-return basis). `fetch_market_overview.py` in its current form cannot produce this without a real design change — either:

1. **Extend `fetch_market_overview.py`** with the same history-pull-and-compute-returns logic `fetch_etf_data.py` already has (duplicating that logic, or factoring it into a shared helper both scripts import) — heavier per-run cost (a full history call per symbol instead of a single quote call) for a job that currently runs 3x/day, which needs reconsidering: history-based returns don't change intraday, so recomputing them 3 times a day is wasted work. Likely needs decoupling: keep the existing price/change snapshot on its current 3x/day cadence, add returns on their own once-daily (or even once-weekly) cadence.
2. **UI design**: "filters" implies a toggle that changes what every card's change-figure shows (today's %-change vs. YTD vs. 1Y vs. 5Y vs. 10Y), rather than one additional field always shown — needs a control (tabs/dropdown similar to the screener's tier chips) and a decision on which symbols this applies to (all 25+ across every group, or just the Indices section).
3. Yield-group cards (`unit: "pct"`) and price-group cards would need different return semantics if this filter applies site-wide — a yield's "5-year return" isn't a meaningful concept the way a fund's total return is; scope may need to exclude the Bond Yields section.

### Owner confirmation needed before implementation starts

Do not begin building until the owner confirms: which symbols/sections this applies to, whether it's a toggle (one figure shown at a time) or additional always-visible fields, and whether the returns-refresh cadence can reasonably diverge from the existing 3x/day price cadence (recommended, for cost/staleness reasons above).

---

## v4.4.0 — Screener Score History Sparklines

### Goal

A per-ticker score trend visual in the screener: a small inline sparkline column in the table and a larger score-history chart in the per-stock popup, mined from the git history of the committed data feeds. This is why the feeds live in git (PRD: reclassified as intentional design in v3.32.0).

### The central design fact

**The feeds store raw metrics, not scores.** Scores are computed client-side at render time. So "score history" cannot be read out of old files directly; it must be **recomputed** by replaying each historical feed snapshot through the scoring model. Two consequences:

1. The scoring model must be **ported to Python** (a second implementation). Parity risk is real and must be tested, not assumed.
2. A decision is forced about **which** model to replay (see decisions below), because the model itself changed over time (v3.21 percentile scoring → v3.30 model v2 → v3.31 six-metric weights).

### Phase 1 — History builder (`scripts/build_score_history.py`)

1. For each feed file (`screener.json`, `screener_sp500.json`, `screener_gvd.json`, `screener_etfs.json`):
   - `git log --reverse --format="%H %cI" -- data/<feed>` to enumerate snapshots; take at most one per calendar day (feeds commit once per trading day already).
   - `git show <sha>:data/<feed>` to read each snapshot without checkouts.
2. **Python port of the scoring model** (current model only): stock mode = percentile rank per metric across the loaded universe, 22% clamp, weights 10/20/10/20/20/20, hard-zero missing, sum /100; ETF mode = rank-linear points. GVD needs the same per-universe splitting the frontend does (score within Growth, Value, Dividend separately).
   - **Parity gate:** the port must reproduce today's live scores exactly. Test = run the Python scorer on the current feeds and diff against the headless-Chrome-rendered scores for all universes (the same harness used for the v3.33.0 regression). Any mismatch is a bug in the port; fix before mining history.
   - Old snapshots predate some fields (margins came and went; earlier feeds may lack fields entirely). The miner scores whatever fields exist under the current model's rules: a missing metric is a hard zero, same as live. Snapshots older than the six current fields will therefore show depressed scores; the window cap below makes this mostly moot.
3. **Output format** — `data/history.json` (or one file per universe if size demands): `{"updated": ..., "window": 90, "series": {"NVDA": [[<date>, <score>], ...]}}`, capped at the **last 90 trading days** per ticker. Budget check before committing to the format: ~750 unique tickers × 90 points ≈ small single-digit MB pretty-printed; minify (no indent) and it comfortably fits GitHub Pages. If it grows past ~2 MB, split per universe so the screener only fetches the active universe's history.
4. **Workflow**: extend each existing feed workflow with a final step that rebuilds history after committing the feed, or (cleaner, recommended) one new nightly workflow at 00:30 UTC Tue-Sat that runs once after all four feeds have landed, needs `fetch-depth: 0` (full clone; the feed workflows can stay shallow), and commits `data/history.json` with `[skip ci]`. Same concurrency group.

### Phase 2 — Frontend

1. **Trend column**: new narrow column (in the Snapshot group, next to Score) rendering an inline SVG polyline of the ticker's score series. Pure vanilla: one `<svg>` per row, points normalized to a fixed 0-100 y-scale so sparklines are comparable across rows; stroke colored by net direction (up = green token, down = red token, flat = muted). No axes, no libraries.
2. **Popup chart**: larger version in the per-stock popup with first/last score labels and the window ("last 90 trading days"). Same SVG approach.
3. **Loading**: history fetched lazily (after the main feed renders, non-blocking) with its own cache key; if the fetch fails the Trend column renders the missing glyph and everything else works. The Columns menu gets Trend as a toggleable column.
4. Methodology popup: a sentence on what the sparkline shows and the recompute-under-current-model caveat.

### Owner decisions to confirm before build

1. **Replay model**: recommend recomputing all history under the **current** model (consistent, comparable series). The alternative (as-shipped scores per era) is not reconstructible anyway; the historical rendered scores were never stored.
2. **Window**: recommend 90 trading days shown; the miner can be re-run with a bigger window later since git history keeps everything.
3. **Universes covered**: recommend all six including ETFs (rank-linear replays identically).
4. Whether Trend ships as a **major** version: yes as planned (v4.4.0), it introduces the first derived-data artifact and a new default column across every universe.

### Verification and acceptance

- Parity gate passes (Python scorer == headless JS scores, all universes, exact).
- History workflow green end-to-end in Actions; `history.json` size within budget.
- Headless check: sparkline SVG present per row, popup chart renders, history-fetch-failure path degrades gracefully (test by pointing the copy at a 404 path).
- Stock scoring regression baseline still holds (no scoring code changes in JS; the frontend change is render-only).

### Risks

- Scoring-port drift over time: any future scoring change must be made in **both** screener.js and the Python scorer. Mitigation: the parity test runs in the history workflow itself, so a drift fails CI loudly instead of silently mining wrong history.
- Early-history noise: feeds before v3.28 covered fewer universes and different fields. The 90-day window and hard-zero rule handle this without special cases.

---

## v4.5.0 — Deeper Index Fund Coverage

### Goal

Expand `indices.html` beyond the current core-index methodology with three new teaching sections: sector ETFs, international allocation, and the bond tent strategy. Content release: no screener, pipeline, or scoring changes.

### Plan

1. **Sector ETFs** — what sector funds are (XLK/XLV/XLE-class examples used descriptively, not as picks), how they concentrate risk relative to broad indices, how the methodology's timing signals (RSI, 52-week range, price vs 200DMA — now live in the ETFs screener universe) apply to them, and why they sit outside the core allocation.
2. **International allocation** — the case for and against ex-US exposure, VXUS as the broad instrument (cross-link to the v3.34.0 International screener universe once live), currency risk in plain English, and how the reader's home-country bias shows up in practice.
3. **Bond tent strategy** — what it is (rising bond allocation approaching a goal date, descending after), why it exists (sequence-of-returns risk, defined at first use per content rules), and how it interacts with the income-contribution investing model the site teaches.
4. Sequencing note: ship **after** v3.34.0 so the international section can link to the live International universe; the sector-ETF section already has the ETFs universe to point at.

### Mechanics (applies to all four content releases, v4.5.0-v4.8.0)

- Written for the primary persona (first-position investor): teach before asserting, define terms at first use, anchor to decisions the reader has faced.
- Content rules: no em dashes, no advice language (educational framing only, no buy/sell verbs aimed at the reader), examples are descriptive not prescriptive.
- Each new section gets: sidebar nav entry (IntersectionObserver hookup is automatic from the section markup pattern), FAQ page additions where a natural Q&A falls out, `sitemap.xml` lastmod bump, meta description review on the touched page.
- Docs per release: PATCHNOTES entry, PRD milestone flip, README page-count touch-ups if section counts are cited.
- Verification: headless render of the touched page, accordion/sidebar behavior intact, no console errors.

---

## v4.6.0 — Additional Illustrative Examples (Historical Market Events)

### Goal

Add worked historical examples across existing pages, showing the methodology applied to real, dated market episodes.

### Plan

1. Candidate episodes (owner to pick 3-5 at kickoff): the 2020 COVID crash and recovery (timing signals at the extreme), the 2021-2022 growth drawdown (what PEG/valuation flagged before it), the 2022-2023 rate cycle (cash-vs-debt pillar behavior), dot-com era NVDA/CSCO contrast (surviving a winner's drawdown), and a dividend-cut case study (what the balance sheet showed first).
2. Placement: each example embeds in the page whose concept it illustrates (metrics examples on `metrics.html`, timing examples on `indices.html`, temperament examples on `philosophy.html`) rather than a standalone examples page, so concepts and cases stay adjacent.
3. Format per example: dated setup (what was knowable then, hindsight explicitly flagged), the metric readings at the time, what the methodology's rules said, what happened, and the teaching point. Historical figures verified against at least one primary-ish source before publishing; approximate figures rounded and labeled approximate.
4. Constraint: examples must not read as track-record claims (no "this is what I bought"); they are illustrations of the rules, per the no-advice rule.
5. Mechanics per the shared checklist in v4.5.0.

---

## v4.7.0 — Additional Philosophy Sections

### Goal

Extend `philosophy.html` (currently 9 sections) with new conceptual material.

### Plan

1. Candidate sections (owner to pick at kickoff; these came out of prior roadmap discussion and PRD content-goals): when to sell (the hardest omission in most methodologies), position sizing and concentration for the income-contribution investor, drawdown temperament (what a 30% paper loss actually feels like and pre-committing behavior), the difference between conviction and stubbornness, and information diet (what to read daily vs quarterly vs never).
2. Each section follows the existing philosophy-page pattern: concept, first-person grounding, the practical rule that falls out of it, cross-links to the metric/page that operationalizes it.
3. FAQ additions for each new section (the FAQ page mirrors philosophy questions today).
4. Mechanics per the shared checklist in v4.5.0.

---

## v4.8.0 — Conference Call Research Guide

### Goal

A new setup-guide page (peer to `finviz.html` and `seekingalpha.html`) teaching how to research earnings conference calls: how to listen, what to note, how to log insights.

### Plan

1. **New page `conferencecalls.html`** following the existing guide-page pattern (step sections, sidebar nav, callout boxes): where calls live (IR pages, transcript sources incl. Seeking Alpha, cross-linking the existing guide), the anatomy of a call (prepared remarks vs Q&A and why Q&A matters more), what to listen for mapped to the site's six scored metrics (guidance vs the forward estimates the screener scores, margin commentary, balance-sheet language), red-flag phrasing patterns, and a simple insight log template (date, company, claim, metric affected, follow-up date).
2. Navigation: header/footer nav additions across all pages (the one release in this set that touches every HTML file), sitemap entry, og/meta for the new page.
3. Ties into the site loop: the guide should close the loop from screener score → "why is the forward estimate what it is" → hearing management's own version on the call.
4. Mechanics per the shared checklist in v4.5.0, plus: full-site headless spot check since nav on every page changes.

---

## v4.0.0 — Screener Responsive Redesign, Methodology Table Fix & Site-Wide Mobile-Friendliness Pass — DONE 2026-07-04

### Why this moved to the front of the queue, and why v3.35.0 merged in

Originally the last item in the roadmap (a backlog hardening pass). Reprioritized the same day two real users hit the screener's horizontal-scroll problem (v3.34.8, v3.34.10): the owner clarified the actual requirement is **the screener should reflow so scrolling is never needed at all**, not just that the existing scroll mechanism become easier to find. That is fundamentally the same design question this pass was already scoped to answer ("should the table pin columns and reflow, or just scroll, at narrow widths?") — solving it once now, across the full width range (desktop-narrow through phone), avoids redoing the same design work twice and avoids shipping two different narrow-width behaviors a few weeks apart. v3.34.10's scrollbar-visibility fix is superseded and folded in here (see that entry for the diagnosis that led to this decision).

v3.35.0 (the methodology modal's `.table-wrap` display bug and a content-currency audit) was then also merged in and its number retired: both items touch screener table CSS/rendering, so building them as one pass avoids reviewing the same table-rendering code twice in quick succession.

### Merged scope from v3.35.0 (methodology modal table fix + content audit)

**Root cause found (code inspection, 2026-07-04):** `style.css`'s `.table-wrap` rule is self-contradictory:

```css
.table-wrap {
  overflow-x: auto;   /* intended: horizontal scrollbar for wide tables */
  margin-bottom: 6px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  overflow: hidden;    /* BUG: shorthand resets BOTH axes, silently cancels the line above */
}
```
`overflow` is shorthand for `overflow-x` + `overflow-y`; the later `overflow: hidden` wins in the cascade and overrides the `overflow-x: auto` three lines above for both axes. The practical effect: a methodology table wider than the modal (the pillar tables have 4 columns including a long "Better means"/description column, and the International row added in v3.34.0 has a long single-paragraph cell) doesn't get a horizontal scrollbar — its overflow is just clipped and invisible. Compounding it, `thead th { white-space: nowrap; }` keeps header cells from wrapping at all.

Merged plan items from v3.35.0, folded into the plan below:
- Fix the CSS bug (remove or reorder the trailing `overflow: hidden`); this is a shared rule, so verify `metrics.html`/`indices.html`/guide pages don't regress.
- Decide scroll-vs-wrap per methodology table (numeric/short-label tables can scroll; long-prose cells like the universe-source description column read better wrapping).
- Audit `#methodStock`/`#methodEtf` content against the current `METRICS`/`ETF_METRICS` scoring code for drift (the popup's been edited five times in one day across v3.30.0-v3.34.0) — pillar weights, tier-band language, the International row's tone, and whether the worked PEG example is still representative.
- General visual polish pass on the modal (spacing, heading hierarchy) now that its content volume has grown substantially since v3.29.0.

### Goal

A dedicated redesign so the screener remains fully usable — no horizontal scrolling required — across the entire range from full desktop down to phone width, plus the original mobile-hardening scope for the other 8 content pages (which, per audit below, don't have this problem — they're normal flowing content with no fixed-width elements).

### Owner decision (2026-07-04)

**Auto-hide column groups at narrower widths**, extending the existing Columns menu rather than building a new component: below defined width breakpoints, lower-priority column groups progressively hide automatically (Ticker/Tier/Score/Factors and Snapshot always visible; Growth/Performance, then Valuation/Income, then Balance Sheet/Technicals drop off as the window narrows), with the existing Columns menu still available to manually override which groups show at any width. Rejected alternatives: a card-per-stock layout (real UI rebuild, loses at-a-glance column scanning) and pure fluid/shrink-to-fit sizing (hard legibility floor with 15-20 financial columns; wouldn't actually eliminate scrolling on its own).

### Scope confirmed narrow (2026-07-04, read-only audit)

Checked all 9 pages for fixed-width elements that could force horizontal overflow: **only `screener.html` has one** (the data table). The other 8 pages (`philosophy.html`, `metrics.html`, `indices.html`, `finviz.html`, `seekingalpha.html`, `faq.html`, `index.html`, plus the shared sidebar) are normal flowing prose/content with no wide fixed-width elements, and already reflow correctly — the `max-width: 767px` breakpoint (shrinks headings, collapses the metric grid) has not been checked against real device widths but is not expected to need structural changes, just verification. The `.app-toolbar` row (chips, Columns/Methodology buttons) already wraps correctly via `flex-wrap: wrap` at narrow widths (confirmed in headless Chrome at 1150px — Methodology button wraps to its own second line rather than being clipped) — no fix needed there, just inclusion in the width-sweep verification pass.

### Known starting points (carried over from the original scope, still relevant)

1. **The universe switcher has 7 buttons** (Nasdaq 100, S&P 500, Growth, Value, Dividend, ETFs, International) in a `flex-wrap` row — functional, but never checked for how many rows it wraps to on a 375px phone or whether it pushes other controls down awkwardly. May also need auto-collapse-to-dropdown treatment at some width, consistent with the column-hiding approach.
2. **Touch target sizing** has not been audited: chip filters, column-visibility checkboxes, and the sort-arrow click targets in table headers were sized for mouse pointers first.

### 1. Methodology modal `.table-wrap` overflow bug — fixed

`style.css`'s `.table-wrap` rule set `overflow-x: auto` and then, three lines later, the shorthand `overflow: hidden` — which resets both axes and silently cancelled the horizontal scrollbar. Changed the trailing declaration to the longhand `overflow-y: hidden`, which keeps the rounded-corner clipping intent for the container without cancelling `overflow-x`. Shared rule, used by every `.table-wrap` sitewide (`metrics.html`, `indices.html`, guide pages, the methodology modal); the two overrides (`.example-table .table-wrap`, `.guide-step-body .table-wrap`) only touch margin/border, not overflow, so both inherit the fix with no further changes needed.

### 2. `#methodStock`/`#methodEtf` content audit — no drift found

Read both sections in full against the current scoring code (`METRICS`/`ETF_METRICS` in `screener.js`). Both already correctly reflected the live model: stock pillars at Growth 60/Valuation 20/Balance 20, and the ETF pillars at the v3.37.0-reweighted Technicals 50 (RSI 20, 52W Range 20, vs 200-Day MA 10) / Performance 50 (1Y 10, 5Y 20, 10Y 20). No edits needed — the audit is the deliverable here, confirming the popup content had not drifted from the five scoring changes shipped earlier the same day.

### 3. Responsive auto-hide columns — implemented

Owner decisions locked before implementation: (a) **live-responsive** — column groups recompute on every resize (debounced 120ms), overriding manual Columns-menu picks until the next breakpoint crossing, rather than only setting a one-time default on load; the v4.0.0 goal (never require horizontal scroll) can't be guaranteed by a "sticky until universe change" default. (b) **Hide order**: least decision-relevant groups drop first — stock kind hides Snapshot, then Balance, then Valuation, then Growth (the heaviest-weighted 60pt pillar stays visible longest); ETF kind hides Income & Cost, then Snapshot, then Performance, then Technicals (the two scored pillars are tied at 50/50, so Technicals — the day-to-day entry-timing half — gets the edge to stay a beat longer).

Implementation in `screener.js`: `HIDE_ORDER` (per kind, ordered array) + `WIDTH_TIERS = [1440, 1150, 900, 700]` px; `autoHiddenCount(width)` counts how many tiers the current width falls under; `applyResponsiveColumns()` sets the Columns-menu checkboxes to match, then calls the existing `applyColumnVisibility()`. Wired to fire on `window resize` (debounced via `scheduleResponsiveColumns()`), on init, and inside `activate()` right after `renderColsMenu()` on a stock↔ETF kind change (so switching to ETFs/International re-evaluates against the new column set immediately, not just on the next resize).

### 4. Universe-switcher/toolbar overflow at narrow widths — a second implicit-min-width bug found and fixed

The width audit (below) surfaced a real bug beyond the table itself: at phone widths, the 7 universe buttons + MAG 10 button overflowed past the viewport edge instead of wrapping, dragging the whole page into horizontal scroll even though `.universe-group` already had `flex-wrap: wrap`. Root cause: `style.css`'s `max-width: 1023px` media query resets `.site-layout`'s `grid-template-columns` to a bare `1fr` (the mobile single-column layout, sidebar collapsed to a top bar) — dropping the `minmax(0, 1fr)` fix shipped in v3.34.8 for the *desktop* rule exactly at the narrow widths where it's needed most. A bare `1fr` track's implicit minimum size is its content's intrinsic width, not 0, so the overflowing button row forced `main.app` (900px+) wider than its 485px-wide grid track instead of being clipped/wrapped into it. Fixed by changing the mobile override to `grid-template-columns: minmax(0, 1fr)`, matching the desktop rule. Confirmed via `getBoundingClientRect()` debug instrumentation (not just visual screenshots, which undercounted the actual rendered width because headless Chrome enforces a ~500px effective minimum viewport below that request size) that `document.documentElement.scrollWidth === clientWidth` at every width tested afterward.

### 5. Device-width audit — completed

Headless Chrome sweep (375, 700, 900, 1023, 1150, 1440, 1920px) confirmed, per width, via `scrollWidth`/`clientWidth` equality (a provable check, unlike the scrollbar-visibility dead end in v3.34.10) and DOM inspection of which `.grp-*` groups carry `.col-hidden`:
- **Zero page-level horizontal overflow** at any tested width, for the screener (both stock-kind and ETF-kind) and all 8 other content pages (`indices.html`, `metrics.html`, `faq.html`, `philosophy.html`, `index.html`, and by shared-layout inference `finviz.html`/`seekingalpha.html`, which use the identical `.site-layout`/`.main-content` structure with no wide fixed-width elements).
- Column-group hide order confirmed exactly matching `HIDE_ORDER` at every breakpoint crossing, for both stock kind (Snapshot→Balance→Valuation→Growth) and ETF kind (Income&Cost→Snapshot→Performance→Technicals).
- Universe-button row wraps onto 2 lines at phone widths, 1 line from ~800px up; no page-level scrollbar at any width post-fix.
- Nasdaq 100 default-load regression: exact match to the v3.31.0 baseline (2 S+ / 10 S / 8 A / 32 B / 24 C / 24 F, MU and NVDA at 100) at every width tested — the responsive work is render-only, no scoring code touched.

### 6. `indices.html` Price vs 200-Day Moving Average write-up — completed

Added a third `<h3>` subsection to the Timing Signals section (`#section-timing`), alongside RSI and 52-Week Range, following the same structure (explanatory paragraphs + a `<div class="how-to-read">` badge list). Framed as a **trend-health confirmation** signal, explicitly distinct from RSI/52W range's contrarian dip-buying framing: price above the 200-day MA confirms an intact long-term uptrend (the favorable condition, matching the ETF model's `higher: true` scoring direction), price below it is the classic long-term downtrend warning — a pullback within an uptrend reads differently than one occurring below a broken trend line, even if RSI is identical in both cases.

Section heading renamed "Timing Signals: RSI, 52W Range, and Price vs 200-Day MA"; updated the page's own doctrine counts everywhere they were stated (the intro "nine metrics... four timing signals" line, the "What Strong Signals Look Like" quick-reference table — new row added for Price vs 200D MA — and its summary note) from nine metrics/four timing signals to **ten metrics/five timing signals**, and the AAII "confirm with RSI and 52W range" callout now also references the 200-day MA in the five-signal alignment check.

---

## Unversioned backlog (no plans yet by design)

- Growth/Value/Dividend standalone framework pages — remains backlog until the owner promotes it to a version.
- Explicitly not planned (owner decisions 2026-07-03): email/RSS changelog subscription, historical scoring backtests, options/crypto/forex coverage.
