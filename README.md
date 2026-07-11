# Azqato — Individual Stock Methodology

A static educational website documenting Azqato's fundamentals-driven, long-term equity investing methodology. Covers stock evaluation, index/ETF timing signals, setup guides for Finviz and Seeking Alpha, and an interactive Nasdaq 100 screener.

**Live site:** [azqato.github.io/stocks](https://azqato.github.io/stocks/)

---

## Tech Stack

| Layer | Technology | Version / Notes |
|-------|-----------|----------------|
| HTML | HTML5 semantic | 9 pages, no preprocessor |
| CSS | CSS3 custom properties | 850+ lines, single file |
| JavaScript | Vanilla ES6 | `script.js` (content pages) + `screener.js` (screener app), no framework |
| Fonts | System fonts only | No external loading |
| Data pipeline | Python 3 + yfinance | Python 3.12, yfinance 1.4.1 (pinned) |
| Hosting | GitHub Pages | Serves from repo root |
| CI/CD | GitHub Actions | Staggered Mon-Fri crons from 21:30 UTC |
| Data format | JSON | Feeds + constituent lists in `data/` |

No npm. No build tools. No frontend dependencies.

---

## Prerequisites

- Any modern browser (Chrome, Firefox, Safari, Edge) for local viewing
- Python 3.12+ only if running or modifying the data pipeline
- `pip` for the single backend dependency (`yfinance`)

Node.js is not required.

---

## Installation

```bash
git clone https://github.com/Azqato/stocks.git
cd stocks
```

For the data pipeline only:

```bash
pip install yfinance
```

---

## Running Locally

No build step required. Open `index.html` directly in a browser, or serve with Python:

```bash
python3 -m http.server 8080
```

Then visit `http://localhost:8080`. The screener fetches its data feed directly from GitHub (`raw.githubusercontent.com`), so it also works when `screener.html` is opened straight from disk as a `file://` URL — no local server required.

---

## Environment Variables

None. The frontend has no environment variables, and the yfinance data pipeline needs no API key or secret. (The legacy `FMP_API_KEY` GitHub Actions secret from an earlier version was deleted on 2026-07-03.)

---

## Build and Deploy

This is a static site. There is no build step.

**Deploy:** Push to `main`. GitHub Pages serves directly from the repository root.

**Data pipeline (automated):** GitHub Actions runs `scripts/fetch_screener_data.py` on trading days (Mon-Fri) at 21:30 UTC, commits `data/screener.json` to the repo, and GitHub Pages serves the updated file immediately. The schedule is deliberately anchored 30 minutes after the *latest* possible US market close in UTC terms (4:00pm US Eastern is 21:00 UTC in winter/EST, 20:00 UTC in summer/EDT — GitHub Actions cron doesn't observe DST, so this guarantees at least a 30-minute buffer after close year-round, growing to 90 minutes in summer). The ETFs feed (`scripts/fetch_etf_data.py`, a fixed 10-fund list) follows at 22:00 UTC, the S&P 500 feed at 22:30 UTC, the combined Growth/Value/Dividend feed at 23:00 UTC, and the International feed (top 100 VXUS holdings) at 23:30 UTC — each 30 minutes after the last, all same calendar day. The constituent sync (Wikipedia for the indices, Vanguard's holdings API for the VUG/VTV/VIG/VXUS lists — VXUS holdings are additionally resolved from ISIN to a Yahoo symbol via `data/vxus_map.json`; the ETFs list is hand-curated and never synced) runs Saturdays at 23:00 UTC.

**Data pipeline (manual):** Go to Actions → "Refresh Screener Data" → Run workflow. Or run locally:

```bash
python3 scripts/fetch_screener_data.py
```

Output is written to `data/screener.json`.

---

## Project Structure

```
stocks/
├── README.md                         ← This file
├── index.html                        ← Home: strategy overview, metric grid, reference table
├── philosophy.html                   ← Conceptual foundation (12 sections)
├── metrics.html                      ← 12-metric glossary with examples
├── screener.html                     ← Interactive Nasdaq 100 screener (markup + CSS)
├── screener.js                       ← Screener logic (data load, scoring, render, popup)
├── market.html                       ← Market Overview: daily benchmark price/change snapshot (self-contained)
├── finviz.html                       ← Finviz screener setup guide
├── seekingalpha.html                 ← Seeking Alpha watchlist setup guide
├── indices.html                      ← Index/ETF methodology and timing signals
├── faq.html                          ← Q&A accordion (37 items)
├── style.css                         ← Full design system stylesheet
├── script.js                         ← Accordion + IntersectionObserver sidebar
├── og-image.png                      ← Social card image (1200x630)
├── data/
│   ├── nasdaq100.json                ← Canonical Nasdaq 100 constituent list (100 tickers)
│   ├── sp500.json                    ← Canonical S&P 500 constituent list (~500 tickers)
│   ├── vug.json                      ← Growth list: top 100 VUG holdings
│   ├── vtv.json                      ← Value list: top 100 VTV holdings
│   ├── vig.json                      ← Dividend list: top 100 VIG holdings
│   ├── etfs.json                     ← ETFs list: fixed, owner-curated 10 funds (hand-edited only)
│   ├── vxus.json                     ← International list: top 100 VXUS holdings (Yahoo symbols)
│   ├── vxus_map.json                 ← ISIN → Yahoo symbol resolution cache + manual overrides
│   ├── market_overview_list.json     ← Market Overview list: owner-curated 61 symbols/7 categories (hand-edited, or rebuilt from market_overview_categories.xlsx)
│   ├── market_overview_categories.xlsx ← Owner's editable Category/Ticker/Display Name spreadsheet (source of truth for reorganizing market_overview_list.json)
│   ├── screener.json                 ← Generated Nasdaq 100 feed (Mon-Fri metrics)
│   ├── screener_sp500.json           ← Generated S&P 500 feed (Mon-Fri metrics)
│   ├── screener_gvd.json             ← Generated combined Growth/Value/Dividend feed
│   ├── screener_etfs.json            ← Generated ETFs feed (technicals/returns/yield/cost)
│   ├── screener_intl.json            ← Generated International feed (six-metric stock model, native currency)
│   └── market_overview.json          ← Generated Market Overview feed (price/change snapshot, 61 symbols/7 categories)
├── scripts/
│   ├── fetch_screener_data.py        ← Python pipeline: yfinance → stock feeds (--list/--out, --combined)
│   ├── fetch_etf_data.py             ← Python pipeline: yfinance → ETFs feed (returns, RSI, MAs, yield, ER, AUM)
│   ├── fetch_market_overview.py      ← Python pipeline: yfinance → Market Overview feed (price/change only)
│   ├── update_constituents.py        ← Weekly auto-sync: Wikipedia → nasdaq100.json + sp500.json
│   └── update_etf_constituents.py    ← Weekly auto-sync: Vanguard API → vug/vtv/vig/vxus.json
├── .github/
│   └── workflows/
│       ├── screener-data.yml         ← Nasdaq 100 feed (Mon-Fri 21:30 UTC)
│       ├── screener-data-etfs.yml    ← ETFs feed (Mon-Fri 22:00 UTC)
│       ├── screener-data-sp500.yml   ← S&P 500 feed (Mon-Fri 22:30 UTC)
│       ├── screener-data-gvd.yml     ← Growth/Value/Dividend feed (Mon-Fri 23:00 UTC)
│       ├── screener-data-intl.yml    ← International feed (Mon-Fri 23:30 UTC)
│       ├── market-overview.yml       ← Market Overview feed (Mon-Fri 22:05 UTC)
│       └── constituents.yml          ← Constituent sync, indices + ETFs (Sat 23:00 UTC)
└── docs/
    ├── PRD.md                        ← Product requirements, architecture, runbook
    ├── DESIGN.md                     ← Design system specification
    ├── PATCHNOTES.md                 ← Full changelog (v1.0.0 → present)
    └── ROADMAP.md                    ← Implementation plans for planned releases
```

---

## Full Documentation

- [docs/PRD.md](docs/PRD.md) — Product requirements, architecture, runbook, roadmap, FAQ
- [docs/DESIGN.md](docs/DESIGN.md) — Design system, color tokens, typography, component patterns
- [docs/PATCHNOTES.md](docs/PATCHNOTES.md) — Full changelog (v1.0.0 to present)
- [docs/ROADMAP.md](docs/ROADMAP.md) — Detailed implementation plans for every planned roadmap item
