# TODO: Azqato Stock Methodology Site

Ideas and planned work not yet in the PRD roadmap. Move an item into the PRD (with a version) when it is scheduled.

---

## 0. IN FLIGHT: where v4.9.x work stopped, 2026-09-28 21:30 UTC

**Read this first if you are picking the parts work back up.** Session paused on usage limits mid-phase, with real work uncommitted in the tree. v4.9.0 is shipped and pushed; v4.9.2 and v4.9.3 are built but unverified and uncommitted.

### Committed and pushed already

| Commit | What |
|---|---|
| `e0a1311` | v4.9.0: `build_universe.py`, `fetch_screener_data.py --part N`, `build_legacy_feeds.py`, `stock-data.yml` (dispatch-only), `constituents.yml` builds the index, alert + health-check wiring |
| `4269959` | Records that the statements half of the Phase 0 gate passed (520 files at 20:37 UTC, none truncated) |
| `363d10b` | `build_universe.py --changed-parts`, tested, **inert: nothing calls it until the cutover** |

### Uncommitted in the working tree, all of it deliberate

- **`data/vti.json`** (new, 3,465 tickers). From `sync_vti()`, added to `scripts/update_etf_constituents.py`. 3,507 raw Vanguard rows, 42 without a domestic ticker dropped, weight-sorted so the largest companies get the lowest part numbers. Keeps both share classes of an issuer (GOOG and GOOGL), unlike the top-100 lists.
- **`data/stocks/index.json` + `tickers.json`** (modified). **Now describe an 8-part, 3,575-ticker universe, while only parts 1 and 2 exist on disk.** This is the one genuinely inconsistent thing in the tree. Nothing reads the index yet, so it is harmless as it stands, but do not run `build_legacy_feeds.py` expecting clean output until parts 3 to 8 land: sp500 and the other lists are still fully inside parts 1 and 2, so the per-list feeds are actually fine, but the coverage report will show the VTI-only tickers as absent.
- **`screener.js`** + **`screener.html`** (modified). A "Total US market" universe that loads `data/stocks/index.json` plus the parts its list spans. **The other seven universes are untouched and still read their per-list feeds**, per the owner decision below. Opts out of localStorage caching (`cacheKey: null`) because 3 MB would blow the quota and evict the small universes' caches.
- **`scripts/fetch_statements.py`** (modified). `--universe` reads symbols from `data/stocks/tickers.json`; `--oldest-first N` fetches only the N symbols whose files are missing or least recently updated. Also writes a `"noStatements": true` file for stocks Yahoo has no statements for, **which is a bug fix, not a nicety**: without it those symbols look permanently missing and get refetched every night, starving everything else.
- **`scripts/update_etf_constituents.py`** (modified). `sync_vti()` plus its config and guard band (`VTI_MIN` 2800, `VTI_MAX` 4200). **Not yet called from `main()`**, so the weekly sync does not touch `data/vti.json` yet. Wiring that in is a remaining step.
- **`docs/PRD.md`** (modified). v4.9.1 rescoped (see below). Folder-structure and runbook entries for the new scripts and `data/stocks/` were already pushed in v4.9.0.
- **`data/statements/2330.TW.json`, `005930.KS.json`, `000660.KS.json`** (new). Real output from testing `--oldest-first 3`. Foreign statements in native currency, valid; safe to commit or delete.

### A background fetch was still running when the session stopped

`for p in 2 3 4 5 6 7 8; do python scripts/fetch_screener_data.py --part $p; done`, started 21:20 UTC, about 3,075 symbols, expected to finish around 22:30 UTC. If `data/stocks/part-03.json` through `part-08.json` exist, it finished; if it died partway, **rerun only the missing parts**, since each part is written atomically at the end of its own run. Part 1 is deliberately not refetched (`--changed-parts` reported `2 3 4 5 6 7 8`).

### Owner decisions taken this session

1. **v4.9.1 is rescoped and merged into v4.9.3.** The frontend keeps per-list feeds for the seven existing universes; only the whole-market universe reads parts. Measured first: reading parts made the default Nasdaq 100 view **4.8x heavier gzipped, 16.9 KB to 81.9 KB**, because part 1 holds 500 stocks and that list needs 100. A full six-universe session does get cheaper (164.4 KB to 113.3 KB), but most visits only load the default view, and v4.9.0 already committed to writing the per-list feeds permanently for v4.4.0's sparklines. Full reasoning is in PRD.md next to the design.
2. **The schedule cutover is on hold** "until everything is fully fleshed out and working locally." Nothing about the five per-list workflows or their crons has been touched.

### What is left to do, in order

1. **Finish or rerun the parts fetch** so parts 1 to 8 all exist.
2. **Measure the VTI tier distribution on real data** before the universe becomes selectable. This is the gate the PRD sets for v4.9.3, and the reason the frontend is not pushed yet. Expect most of the roughly 2,950 added stocks to take structural hard zeros on missing metrics and fill the F band (owner has accepted this: missing metrics score zero).
3. **Rerun the node harness** at `scratchpad/test_parts_loader.mjs` with all 8 parts present; with 2 of 8 it passed 10/10 including the missing-part degradation path. It runs the real `fetchFromParts` text out of screener.js with fetch stubbed, so it is worth keeping.
4. **Wire `sync_vti()` into `update_etf_constituents.py`'s `main()`**, so the weekly sync maintains `data/vti.json`.
5. **Update the places that enumerate the universes:** `screener.html`'s meta description, PRD.md's "Universe buttons" list (around line 833), and README.md if it lists them.
6. **Write PATCHNOTES entries** for v4.9.2 (rolling statements) and v4.9.3 (whole market), with the measured numbers.
7. **Then the cutover**, which is a separate decision and was blocked once by auto mode as a production deploy. The prepared patch is at `scratchpad/v491_cutover.py` and does five things: delete `screener-data.yml`, `-sp500`, `-gvd`, `-intl`; put `cron: "37 21 * * 1-5"` on `stock-data.yml`; replace `constituents.yml`'s four per-list regeneration blocks with one that calls `--changed-parts` and refetches only those; drop the four retired names from `alert-on-failure.yml`; drop them from `MAX_AGE_HOURS` in `check_workflow_health.py`. **Reverting that one commit is the rollback.** Note that the scratchpad is session-scoped and will be cleaned up, so treat that script as a description of the change rather than something to rerun.

### Two facts worth keeping

- **The Phase 0 gate is half met.** Statements passed (520 files, 20:37 UTC). The daily-feed half was pending tonight's 21:37 UTC run, which will be the first to carry v4.3.6's nine ratio fields.
- **The derived feeds are not committed on purpose.** v4.9.0 verified them locally and then restored the committed versions, so the live site is still served by the old pipeline. They were saved to a temp directory that will be cleaned up; regenerate with `python scripts/build_legacy_feeds.py` rather than hunting for them.

---

## 1. One stock-data job for every list, in 500-stock parts (SCHEDULED)

**Moved into the PRD roadmap on 2026-09-28 as v4.9.0 through v4.9.3**, per this file's own rule that a scheduled item moves out of here and into the roadmap with a version. See `docs/PRD.md`, Roadmap, Open Milestone Detail, "One Stock-Data Job For Every List, In 500-Stock Parts" for the implementation plan.

The plan there keeps the owner's original design intact (one master universe, one record per ticker per day, parts of up to 500 ordered by importance, lists reduced to pure membership) and adds what costing it out turned up: parallel parts do conflict on push and need a rebase-retry loop, a 500-stock part runs in about 10 minutes rather than 30 to 45, parts weigh about 380 KB rather than 250 KB, the ETF feed stays separate because its records share only 7 of 20 fields with stock records, and the legacy per-list feeds keep being written permanently because v4.4.0's score-history sparklines mine their git history. The three owner decisions recorded here on 2026-09-28 (International stays at 100, VTI becomes its own "Total US market" list, one daily run time for everything) carry over unchanged, joined by a fourth: missing metrics keep scoring zero, with no coverage gate for the whole-market universe.

Nothing further is tracked here for this item.
