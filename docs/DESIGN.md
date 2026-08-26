# DESIGN.md - Azqato Stock Methodology Site

**Version:** 2.1
**Status:** Active
**Last Updated:** 2026-08-25

---

## 1. Design Philosophy

This site is a methodology document, not a marketing page. The design should feel like infrastructure: something a developer or serious investor trusts because it does not try to impress them. Every visual decision defers to legibility and information density over decoration.

The aesthetic is GitHub Dark-inspired: deep backgrounds, high-contrast text, a single teal accent that carries all interactive meaning. This is the same visual language used across all Azqato properties (portfolio site, ComposerAtlas, leveraged strategies). Consistency across projects is a feature. The design should feel at home in that family.

Readers come here to learn. The typography, spacing, and navigation all serve slow, deliberate reading. Long-form content pages get anchor navigation, generous line height, and clear heading hierarchy. The screener app gets density and keyboard-friendly sortable columns. Different pages optimize for different tasks within the same visual system.

---

## 2. Color Palette

All colors are defined as CSS custom properties in `:root` in `style.css`. Never hardcode hex values outside of `:root`.

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-bg` | `#0d1117` | Page background on all pages |
| `--color-surface` | `#161b22` | Cards, sidebar background, modal backgrounds |
| `--color-border` | `#30363d` | All borders and dividers |
| `--color-accent` | `#00d4a0` | Primary interactive color: active nav links, hover borders, h2 accent bars, badge teal, range dot |
| `--color-accent-hover` | `#00e6b0` | Hover state for any accent-colored element |
| `--color-accent-light` | `rgba(0, 212, 160, 0.08)` | Tinted backgrounds: how-to-read boxes, accordion hover, FAQ teaser, card hover tint |
| `--color-tag-bg` | `#21262d` | Tag pills, hero badges, ticker tag backgrounds |
| `--color-card-hover` | `#1c2128` | Card hover background, table header background |
| `--color-text-primary` | `#eef3f7` | Body copy, headings, all primary reading text |
| `--color-text-secondary` | `#cbdae6` | Subtitles, captions, lead paragraphs, metric card definitions, sidebar inactive links |
| `--color-positive` | `#3fb950` | Positive values in tables, good-signal badges, hero badge text |
| `--color-negative` | `#f85149` | Negative values, red-flag badges, screener F tier (dark red) |
| `--color-warning` | `#ffa657` | Caution values, amber badges, caveat box borders |
| `--color-purple` | `#bc8cff` | Gradient endpoint on metric card hover top border only |
| `--color-tier-splus` | `#bc8cff` | Screener S+ tier (purple, a perfect 100 score): badge, score bar |
| `--color-tier-s` | `#2ea043` | Screener S tier (dark green): badge, score bar |
| `--color-tier-a` | `#7ee787` | Screener A tier (light green): badge, score bar |
| `--color-tier-b` | `#e3b341` | Screener B tier (yellow): badge, score bar |
| `--color-tier-c` | `#ffa198` | Screener C tier (light red): badge, score bar |

F tier reuses `--color-negative` (`#f85149`) directly; there is no separate `--color-tier-f` token (confirmed in `style.css`, v3.29.0).

`:root` defines 20 custom properties in total: the 19 tokens above plus `--sidebar-width: 220px` (see Section 4).

**Discrepancy (2026-08-25 audit, unresolved):** `.sidebar-brand-sub` (`style.css`) references `var(--color-text-muted)`, but `--color-text-muted` is never defined in `:root`. This is a dead custom-property reference in the current CSS, not a documentation error: the code is what's wrong here. Left as-is pending the author's decision on whether to define the token or point the rule at an existing one (`--color-text-secondary` is the nearest match). See the PRD's Risks and Open Questions section.

**Contrast:** Primary text on background is approximately 15:1. Secondary text on background is approximately 4.8:1. Both meet WCAG AA. Do not introduce new text colors that fall below 4.5:1.

**Do not deviate from `#00d4a0` as the accent.** It is the cross-project Azqato brand color. Changing it breaks visual continuity with the portfolio site and other Azqato properties.

---

## 3. Typography

### Font Stacks

```css
/* Sans-serif (body, UI, headings) */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;

/* Monospace (data values, ticker symbols, code) */
font-family: 'SF Mono', 'Consolas', 'Liberation Mono', 'Courier New', monospace;
```

No external font loading. No Google Fonts. No web font requests.

### Type Scale

| Role | Size | Weight | Line Height | Letter Spacing | Color | Notes |
|------|------|--------|-------------|----------------|-------|-------|
| H1 (page title) | 1.875rem | 700 | 1.2 | -0.3px | `--color-text-primary` | One per page |
| H2 (section) | 1.375rem | 700 | 1.3 | normal | `--color-text-primary` | Has `::before` teal accent bar |
| H2 (metric block) | 1.5rem | 700 | 1.3 | normal | `--color-text-primary` | Larger variant for metrics.html full entries |
| H3 (subsection) | 1.0625rem | 600 | 1.4 | normal | `--color-text-primary` | |
| Body | 1rem | 400 | 1.6 | normal | `--color-text-primary` | Default for all paragraph text |
| Lead / intro | 1rem | 400 | 1.65 | normal | `--color-text-secondary` | First paragraph of a page or section |
| Caption / note | 0.78rem | 400 | 1.5 | normal | `--color-text-secondary` | Table footnotes, small labels |
| Metric value / data | 0.85rem | 400 | 1.6 | normal | Contextual | Monospace stack |
| Ticker symbol | 0.875rem | 600 | 1.6 | normal | `--color-accent` | Monospace stack |
| Table header label | 0.6875rem | varies | — | uppercase | `--color-text-secondary` | Screener column headers |

**Mobile reduction:** H1 drops to 1.5rem below 768px. H2 drops to 1.2rem below 768px.

---

## 4. Spacing System

The design does not use a rigid 4px or 8px grid, but follows consistent spacing conventions:

| Use | Value |
|-----|-------|
| Page padding (desktop) | 32px top/bottom, 28px left/right |
| Page padding (mobile) | 20px top/bottom, 16px left/right |
| Between sections (margin-top h2) | 44px |
| Between elements in a card | 8px–16px |
| Card padding | 18px |
| Table cell padding | 10px 14px |
| Sidebar width | 220px (fixed) |
| Content max-width | 820px |
| Gap between flex/grid items | 6px, 8px, 12px, or 16px depending on context |
| Border radius (cards, modals) | 10px |
| Border radius (buttons, badges) | 999px (pill) |
| Border radius (table wrapper) | 8px |
| Border radius (info boxes) | 0 6px 6px 0 (left-flush) |

---

## 5. Breakpoints

| Breakpoint | Trigger | Changes |
|------------|---------|---------|
| Desktop | `>= 1024px` | 2-column grid (220px sidebar + 1fr content), sticky sidebar, active left-border on nav links, "On This Page" block visible |
| Tablet / Mobile | `< 1024px` (`max-width: 1023px`) | Sidebar collapses to a sticky top bar with `backdrop-filter: blur(12px)` and a **hamburger toggle** (CSS-only checkbox hack: ☰ / ✕) that drops the nav down as a vertical list; "On This Page" block hidden; the screener's `.app-table-wrap` gets a `max-height: 80vh` cap (not applied above this breakpoint; desktop lets the app flow and scroll with the page); the methodology/stock modal goes full-width (`width: 100%; max-width: none`) |
| Mobile | `< 768px` (`max-width: 767px`) | Metric cards grid collapses to 1 column, H1 → 1.5rem, H2 → 1.2rem, `.hero-thesis` → 1.375rem, padding reduces to 20px/16px |
| Mobile (Market Overview only) | `< 480px` | `market.html` carries its own inline `@media (max-width: 480px)` rule for its card grid, not defined in `style.css`; see Component Patterns below |
| Reduced motion | `prefers-reduced-motion: reduce` | Disables accordion and metric-card transitions sitewide (Section 8) |

**Correction (2026-08-25 audit):** the previous line here read "modals go full-width below 900px," sourced from the PATCHNOTES v3.19.0 entry ("popups widened to 65%/max 1100px; full-width under 900px"). The actual breakpoint in the current `screener.html` inline stylesheet is `max-width: 1023px`, matching the sidebar/layout breakpoint above, not 900px. Whether the modal's desktop width is still exactly 65vw/max 1100px was not re-verified pixel-for-pixel in this pass; treat that specific figure as unconfirmed until checked directly against `screener.html`.

---

## 6. Component Patterns

### Section Heading (h2)

Every `h2` renders a 3px wide, 1.1em tall vertical bar in `--color-accent` via `::before` pseudo-element using `display: flex; align-items: center; gap: 0.5rem`. This is the signature visual element shared with azqato.github.io. Do not suppress it.

---

### Metric Cards (index.html grid)

10 cards in a 2-column grid on desktop, 1-column on mobile.

```
Background:       --color-surface
Border:           1px solid --color-border
Border radius:    10px
Padding:          18px
Hover background: --color-card-hover
Hover border:     rgba(0, 212, 160, 0.5)
Hover transform:  translateY(-2px)
Hover shadow:     0 4px 12px rgba(0, 212, 160, 0.08)
Hover top border: 2px gradient (--color-accent → --color-purple) via ::before
Card name:        0.9375rem, weight 700, --color-accent
Card definition:  0.85rem, --color-text-secondary
```

---

### Tables

Used for metric comparisons, reference data, illustrative examples.

```
Wrapper:          border 1px solid --color-border, border-radius 8px, overflow hidden
Header row:       background --color-card-hover, text 0.6875rem uppercase, --color-text-secondary
Body rows:        alternating rgba(255, 255, 255, 0.02) on even rows
Row hover:        background --color-accent-light (teal tint)
Cell padding:     10px 14px
Number columns:   right-aligned, monospace font
Ticker column:    --color-accent, bold, monospace, nowrap
Positive values:  --color-positive (#3fb950)
Negative values:  --color-negative (#f85149)
Caution values:   --color-warning (#ffa657)
```

---

### 52-Week Range Bar

Inline range visualization used in tables.

```
Track:  4px height, background --color-border, border-radius 2px
Dot:    8px × 8px circle, background --color-accent, border-radius 50%
Position: left: var(--pos) CSS custom property set inline per row
Calculation: (price − low) / (high − low) as a percentage
```

---

### Accordion (faq.html)

```
Container:        border 1px solid --color-border, border-radius 10px, overflow hidden
Trigger:          background --color-surface, font 0.9375rem weight 500, no border
Trigger hover:    background --color-accent-light
Icon:             "+" / "−" in --color-accent, right-aligned
Transition:       max-height 0 → 6000px, 200ms ease-in-out
Content bg:       rgba(0, 212, 160, 0.04)
Content text:     --color-text-secondary
Palantir story:   border-left 3px solid --color-accent, text --color-text-primary
Behavior:         One item open at a time; opening one closes others
ARIA:             aria-expanded toggled on trigger; aria-controls links to body id
```

---

### Status Badges

Pill-shaped. Used for verdict labels, signal ranges, and descriptive tags.

```
Good:     background rgba(63, 185, 80, 0.12),  text --color-positive, border rgba(63, 185, 80, 0.3)
Caution:  background rgba(255, 166, 87, 0.12), text --color-warning,  border rgba(255, 166, 87, 0.3)
Negative: background rgba(248, 81, 73, 0.12),  text --color-negative, border rgba(248, 81, 73, 0.3)
Neutral:  background --color-tag-bg,            text --color-text-secondary, border --color-border
Border radius: 999px
Padding: 2px 10px (small) or 4px 12px (normal)
```

---

### How-to-Read Box

Used to explain how to interpret a metric or tool. Teal-tinted.

```
Background:   --color-accent-light (rgba teal 8%)
Border-left:  3px solid --color-accent
Border-radius: 0 6px 6px 0
Padding:      14px 18px
```

---

### Caveat Box

Used for warnings, edge cases, and limitations. Amber-tinted.

```
Background:   rgba(255, 166, 87, 0.08)
Border-left:  3px solid --color-warning
Border-radius: 0 6px 6px 0
Text:         --color-text-secondary
Strong labels: --color-warning
```

---

### Hero Badge

Pill badge appearing below the page description on every page.

```
Position:     Below .hero-sub, margin-top: 16px
Background:   --color-tag-bg
Border:       1px solid --color-border
Border-radius: 999px
Text:         --color-positive, 0.75rem
```

---

### Watchlist Ticker Tags

Used to display ticker symbols as interactive tags.

```
Font:         monospace
Background:   --color-tag-bg
Border:       1px solid --color-border
Border-radius: 6px
Text:         --color-accent, weight 600
Hover border: rgba(0, 212, 160, 0.5)
Hover bg:     --color-accent-light
```

---

### Modals (Screener)

Used for the Settings and Methodology popups on `screener.html`.

```
Backdrop:     fixed overlay, rgba(0,0,0,0.6)
Modal:        --color-surface background, 1px border --color-border, border-radius 10px
Width:        widened in v3.19.0 from the original 560px/90vw to accommodate the growing
              Methodology popup content; full-width (width: 100%, max-width: none,
              padding: 24px 20px) below 1023px. Exact desktop width figure not
              re-verified against current code in the 2026-08-25 audit. PATCHNOTES
              states 65vw/max 1100px at the time of the v3.19.0 change; confirm against
              screener.html before relying on the specific number.
Close button: top-right × button in --color-text-secondary
Behavior:     close on click outside, close on Escape key
```

---

### Market Overview Cards (`market.html`)

Introduced in v4.1.0, expanded through v4.1.6. These classes live in `market.html`'s own inline `<style>` block, not in `style.css`; they are not shared with any other page and were not part of this document until the 2026-08-25 audit.

```
.market-grid:          responsive card grid, one .market-section per category
.market-section:       category container; h2 heading, no ::before accent bar override
                        beyond the sitewide h2 rule
.market-card:           --color-surface background, standard card border, holds one
                        symbol's snapshot
  .market-card.up:      change value in --color-positive, ▲ arrow
  .market-card.down:    change value in --color-negative, ▼ arrow
  .market-card.flat:    change value in --color-text-secondary, no arrow
.market-card-name:     display name (e.g. "S&P 500"), primary text
.market-card-ticker:   ticker symbol, monospace, --color-accent; uses a slightly
                        different stack locally: ui-monospace, "SF Mono", Consolas,
                        monospace (not the sitewide monospace stack; flagged, not
                        corrected, since it renders equivalently on the target platforms)
.market-card-price:    current price/yield, monospace
.market-card-change:   point and percent change (or point change alone for yield cards,
                        unit: "pct" entries; see PRD Data Models)
.market-card-arrow:    ▲/▼ direction glyph
.market-card-missing:  "Data unavailable" fallback state for a symbol with no price
.market-stale-banner:  informational banner shown when the feed is stale (`.on` toggles
                        visibility); threshold is 4 days for this page (vs. a week for
                        the daily screener feeds), recalibrated for its intraday cadence
.market-asof:          "Last updated" hero-badge variant; local override
                        `margin: 16px 0 0` fixes double-padding since it sits inside
                        `.guide-intro`, which already carries its own bottom padding
```

A time-of-day emoji (🌅 shortly after the open, ☀️ midday, 🌆 shortly after close) prefixes the "Last updated" text, bucketed on the feed's own UTC refresh schedule rather than the viewer's local time.

---

### Sidebar Navigation

```
Inactive links:    --color-text-secondary, weight 500
Hover:             --color-text-primary
Active / current:  --color-accent, weight 600, 3px left border in --color-accent
"On This Page":    Smaller, indented sub-links; highlighted via IntersectionObserver scroll
Brand ("Azqato."): teal dot on period via <span>
Footer:            "Educational use only. Not financial advice." in --color-text-secondary
```

---

### Favicon

All pages use an emoji SVG data URI favicon. No external file required.

```html
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📈</text></svg>">
```

---

## 7. Accessibility Standards

**Target:** WCAG 2.1 AA.

- Primary text on background: approximately 15:1 contrast ratio
- Secondary text on background: approximately 4.8:1 contrast ratio
- All interactive elements have visible `:focus-visible` outline in `--color-accent`
- Accordion items use `aria-expanded` and `aria-controls` attributes
- Tables include `<caption class="visually-hidden">` and `<th scope>` attributes
- Emoji favicon is presentational only; no alt text required
- `prefers-reduced-motion`: disables card `translateY` transforms and accordion max-height transitions

---

## 8. Animation and Motion

Keep motion minimal and purposeful. Three allowed animations:

1. **Card hover lift** (`translateY(-2px)`) — signals interactivity on metric cards
2. **Accordion expand/collapse** (`max-height` transition, 200ms ease-in-out) — reveals content without layout jump
3. **Sidebar link highlight** (IntersectionObserver, no transition) — "you are here" scroll tracking

No other animations. No decorative motion. No loading spinners. No auto-playing anything.

`prefers-reduced-motion` disables items 1 and 2. Item 3 (IntersectionObserver highlight) is not animated and is unaffected.

---

## 9. Sidebar "On This Page" Navigation

The "On This Page" anchor block is the signature interaction pattern of the site. As the user scrolls, the corresponding sidebar link highlights in `--color-accent` teal.

**Implementation:** `script.js` uses `IntersectionObserver` with a root margin of `-15% 0 -65% 0`. It derives which sections to observe from the `href` attributes of `.metric-links a` elements on the page. No per-page configuration is needed.

**Present on:** index.html, philosophy.html, metrics.html, finviz.html, seekingalpha.html, indices.html.
**Absent on:** faq.html (accordion pattern), screener.html (app with no long-form sections).

Block position: below the Support link (last item in the main nav list), as a standalone `<li>`.

---

## 10. Social Cards (Open Graph)

Every page has Open Graph and Twitter Card meta tags so links render preview cards on Discord, X, and Slack.

**Convention:**
- `<title>` = page H1 text exactly. No "- Azqato" suffix. Ever.
- `og:title` = identical to `<title>`
- `og:description` = lead paragraph on the page exactly
- `<meta name="description">` = identical to `og:description`
- `twitter:title` and `twitter:description` mirror OG values

**Required tags (all pages):**

```html
<meta name="description" content="...">
<meta property="og:type" content="website">
<meta property="og:url" content="https://azqato.github.io/stocks/PAGE.html">
<meta property="og:title" content="Page Title">
<meta property="og:description" content="...">
<meta property="og:image" content="https://azqato.github.io/stocks/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Page Title">
<meta name="twitter:description" content="...">
<meta name="twitter:image" content="https://azqato.github.io/stocks/og-image.png">
```

**Per-page values:**

| Page | `og:title` / `<title>` | `og:description` / `<meta name="description">` |
|------|----------------------|-----------------------------------------------|
| `index.html` | Stock Picking Methodology | A disciplined, metrics-driven approach to long-term equity investing. No day trading. No panic selling. No noise. |
| `philosophy.html` | The Philosophy of Long-Term Conviction Investing | The concepts that sit behind every rule in this methodology. Understanding why the rules exist makes them easier to follow when markets are moving fast and the temptation to react is strongest. |
| `metrics.html` | Stock Evaluation Metrics Explained | Ten metrics. Each one earns its place. This page explains what each signal measures, why it matters for long-term investing decisions, and how to interpret the numbers. All examples are illustrative and use hypothetical figures to demonstrate how each metric works in practice. |
| `finviz.html` | How to Set Up a Finviz Stock Screener For Free | How to configure Finviz's free stock screener to surface candidates that align with the methodology. Use this as a discovery tool to find stocks worth evaluating further in Seeking Alpha. |
| `seekingalpha.html` | How to Build a Stock Watchlist in Seeking Alpha For Free | Step-by-step guide to creating a free Seeking Alpha account and configuring a portfolio to track individual stocks with the exact 12-column layout used in this methodology. |
| `screener.html` | Nasdaq 100 Screener | (not independently re-verified against DESIGN.md's own convention in this pass; see PRD's Documentation Versus Reality table) |
| `indices.html` | Indices & ETF Investing | A separate methodology for evaluating broad market indices and ETFs. Different assets require different frameworks. Where individual stock picking is driven primarily by company fundamentals, index investing is driven primarily by market sentiment, timing signals, and structural efficiency. |
| `faq.html` | Stock Investing Q&A | The thinking behind the strategy. Questions about how decisions are made, why certain rules exist, and what the long-term mindset actually looks like in practice. |
| `market.html` | Market Overview | A same-day market snapshot across indices, factors, sectors, commodities, yields, leveraged ETFs, and crypto, refreshed three times per trading day. Added 2026-08-25 audit: this row was missing entirely; the page (added v4.1.0, 2026-07-10) does carry full Open Graph/Twitter Card tags in the actual code, this table just hadn't been updated to list it. |

**Social card image:** `og-image.png` is a 1200x630 PNG at the site root. The 📈 emoji centered on `#0d1117` background, white monochrome. To regenerate:

```powershell
Add-Type -AssemblyName System.Drawing
$bmp = New-Object System.Drawing.Bitmap(1200, 630)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.Color]::FromArgb(255, 13, 17, 23))
$font = New-Object System.Drawing.Font("Segoe UI Emoji", 380, [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)
$sf = New-Object System.Drawing.StringFormat
$sf.Alignment = [System.Drawing.StringAlignment]::Center
$sf.LineAlignment = [System.Drawing.StringAlignment]::Center
$g.DrawString([System.Char]::ConvertFromUtf32(0x1F4C8), $font, (New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)), (New-Object System.Drawing.RectangleF(0,0,1200,630)), $sf)
$bmp.Save("og-image.png", [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
```

---

## 11. Content Philosophy

This site documents a methodology, not a live portfolio. All content is written to remain accurate indefinitely.

**Rules:**
- No real-time data references. No current prices, current RSI readings, or any value that will be stale within weeks.
- All illustrative examples use clearly hypothetical labels: "High-growth tech co.", "Slow-growth value co.", "Accelerating", "Decelerating".
- Moat-type examples use category descriptions, not named companies: "enterprise software platforms" not a specific ticker.
- The Palantir story ($9 buy, $45 sell, $150 outcome) is the one named historical exception. It is a first-person account, not a live recommendation.
- Historical references are acceptable when they clearly describe a past event.
- No em dashes anywhere in copy. All three forms are prohibited: ` -- ` (double hyphen with spaces), `—` (raw Unicode U+2014), and `&mdash;` (HTML entity). Use commas, colons, semicolons, parentheses, or periods instead.
- No "- Azqato" brand suffix on `<title>` or `og:title`. Title = H1 only.

---

## 12. What Not To Do

- No light or white backgrounds anywhere (dark theme only)
- No gradient backgrounds (the only gradient is the 2px card-hover top border)
- No external font loading
- No stock chart widgets or live data embeds in editorial content
- No animations beyond the three listed in Section 8
- No full-bleed hero images
- No em dashes in any copy (any form)
- No decorative motion or transitions for motion's sake
- Do not deviate from `#00d4a0` as the accent color
- No "- Azqato" suffix on any `<title>` or `og:title` tag

---

## 13. CSS File Structure

```
style.css (in order):
  :root                   → CSS custom properties (20 total: 19 color tokens + sidebar
                             width; corrected from "14" in the 2026-08-25 audit, since 5
                             tier color tokens were added in v3.29.0/v3.30.0 and this
                             line was never updated)
  Reset / base            → box-sizing, body, margins
  Layout                  → .site-wrapper flex, .site-layout grid
  Sidebar                 → brand, nav links, active states, footer
  Main content            → .main wrapper, content max-width
  Footer                  → border-top, text size, links
  Typography              → h1, h2 (::before bar), h3, body, lead, caption
  Tables                  → wrapper, thead, tbody, .ticker-cell, .num, value coloring, range bar
  Hero                    → .hero, .hero-badge, .hero-thesis, .hero-sub
  Section container       → .section-container spacing
  Metric cards            → index.html 2-column grid, hover effects
  Metric blocks           → metrics.html full entries
  Accordion               → faq.html expand/collapse, Palantir accent
  Badges                  → .badge-good, .badge-caution, .badge-negative, .badge
  How-to-read box         → .how-to-read
  Caveat box              → .caveat-box
  FAQ teaser              → .faq-teaser
  Guide components        → .guide-step, .step-num, .ui-text, .guide-note
  Ticker tags             → .watchlist-tickers, .ticker-tag
  Screener app            → .app, .screener-toolbar, .modal
  Media queries           → < 1024px (tablet), < 768px (mobile)
  Reduced motion          → @media (prefers-reduced-motion: reduce)
```

---

## 14. Version History

| Version | Date | Summary |
|---------|------|---------|
| 1.0 | 2026-06 | Initial design: light wiki theme, IBM Plex fonts, deep green `#1A6B4A` accent |
| 1.1 | 2026-06 | Dark theme rebrand: Azqato brand system, teal `#00d4a0` accent, system fonts, GitHub Dark palette, h2 accent bars, card hover, emoji favicon |
| 1.4 | 2026-06 | Content philosophy formalized: no real-time data in examples, hypothetical labels required, named company examples replaced with category descriptions |
| 1.5 | 2026-06 | Two setup guide pages (watchlist, screener). Nav expanded. Text readability improved. Guide component CSS system added. |
| 1.6 | 2026-06 | indices.html added. Nav restructured to 7 items. Sitewide readability: accordion/card/guide text to --color-text-primary. Capital gains content. |
| 1.7 | 2026-06 | Text color differentiation: --color-text-primary → #eef3f7, --color-text-secondary → #cbdae6 |
| 1.8 | 2026-06 | "On This Page" sidebar nav extended sitewide. IntersectionObserver generalized. Block moved to below Support link. |
| 1.9 | 2026-06 | Hero badge repositioned below .hero-sub. .hero padding-bottom reduced. |
| 3.0 | 2026-06 | "Leveraged Strategies" external nav link added sitewide. Nav is now 9 items. |
| 3.1 | 2026-06 | Philosophy page expanded from 7 to 9 sections (belief/long-game, hype/weak-hands). Content only. |
| 3.2 | 2026-06 | FAQ aligned with philosophy v3.1.0. 1 new question, 3 answers deepened, 1 cross-link added. |
| 3.3 | 2026-06 | DCA and Lump-Sum sections added to indices.html. New FAQ question. |
| 3.4 | 2026-06 | Interactive Nasdaq 100 screener added (screenapp.html). Dense full-width app layout using existing style.css tokens. Daily data pipeline introduced. |
| 3.5 | 2026-06 | File renames: screener.html → finviz.html, watchlist.html → seekingalpha.html, screenapp.html → screener.html. All references updated. |
| 3.6 | 2026-06 | Nav relabeled (Finviz, SeekingAlpha). Screener added to nav. Screener app adopts shared sidebar. Nav now 10 items. |
| 3.7 | 2026-06 | Data pipeline moved from FMP (Node) to yfinance (Python). Nasdaq 100 constituent list corrected. |
| 3.8 | 2026-06 | Cash/Debt ratio column added to screener Balance Sheet group. |
| 3.9 | 2026-06 | Forward metrics aligned to Seeking Alpha current-year basis. Pipeline/data only. |
| 3.10 | 2026-06 | Dual-class consolidation: removed GOOG, kept GOOGL. Multi-class rule established. Screener now 100 tickers. |
| 3.11 | 2026-06 | P/E FWD and PEG FWD switched to Yahoo direct fields for closer Seeking Alpha match. |
| 3.12 | 2026-06 | New scoring model: 5 forward factors, each 0–20, total /100. Verdict bands Pass 70 / Watch 40 / Fail <40. |
| 3.13 | 2026-06 | Methodology popup added to screener toolbar. Reuses modal component. Settings section reduced to pointer. |
| 3.15 | 2026-06-27 | Screener scoring switched to a relative percentile model (each stock ranked vs Nasdaq 100 peers, 0–20 per metric, bands Pass 65 / Watch 40 / Fail <40). Methodology popup rewritten to explain ranking. v3.15.1: negative forward P/E (unprofitable) now ranks worst on P/E vs Growth, not best. v3.15.2: same fix extended to PEG (ranks worst; column shows our own negative PEG instead of Yahoo's misleading positive). v3.15.3: shrinking forward earnings (EPS growth <=0) also rank worst on P/E vs Growth instead of being dropped. v3.15.4: negative forward P/E cell renders red. |
| 3.16 | 2026-06-27 | Screener cell colors switched from absolute thresholds to the relative percentile ranking (top quartile green, bottom red, middle amber). New per-stock breakdown popup (click a row; reuses the modal component). Data now loads directly from GitHub raw (works as a local file) with a localStorage offline cache. Removed the FMP bring-your-own-key UI (Settings modal, API-key input, Load Data button, progress bar). Negative P/E / PEG sort as worst (expensive), not cheap. |
| 3.17 | 2026-06-27 | Constituent list auto-syncs weekly from Wikipedia (`update_constituents.py` + `constituents.yml`). Screener derives its ticker universe from the feed (`universe()`), removing the embedded list — single source of truth. |
| 3.18 | 2026-06-27 | Screener's inline JS extracted to `screener.js` (`screener.html` is now markup + CSS). No behavior change. |
| 3.19 | 2026-06-28 | Mobile hamburger nav (CSS-only checkbox toggle; ☰/✕) replaces the cramped wrapping top bar on all pages under 1024px. Methodology/stock popups widened to 65% (max 1100px; full-width under 900px). |
| 3.20 | 2026-06-28 | Verdict bands tightened to Pass ≥ 80, Watch 50–79, Fail < 50 (was 65 / 40), applied to both verdict labels and score cell colors. |
| 3.21 | 2026-06-29 | Per-stock popup now lists only the five scored metrics; the two unscored TTM "(context)" rows (Revenue/EPS Growth TTM) were removed from the popup. |
| 3.22 | 2026-06-29 | "Expand to S&P 500" toggle added to the screener app-bar (right of the Azqato pill). Lazy-loads a second daily feed (`data/screener_sp500.json`) and re-ranks against the full S&P 500; toggles back to the Nasdaq 100. On-screen labels swap via `.universe-name` spans. New `data/sp500.json` constituent list; staggered CI (Nasdaq 23:00, S&P 500 23:30). |
| 3.23 | 2026-06-29 | CI schedule only: screener feeds run Mon-Fri (trading days); the weekly constituent sync moved to Saturday 23:00 UTC. No visual or UX change. |
| 2.0 | 2026-06-27 | Full DESIGN.md rewrite consolidating all design decisions, adding missing sections (spacing, breakpoints, motion, social cards, content philosophy), and bringing documentation to v3.13.0 parity. |
| n/a | 2026-07-03 (v3.29.0) | 4 new tier color tokens added: `--color-tier-splus` (`#bc8cff`), `--color-tier-s` (`#2ea043`), `--color-tier-a` (`#7ee787`), `--color-tier-b` (`#e3b341`), `--color-tier-c` (`#ffa198`). Screener verdict badges/score bars switched from Pass/Watch/Fail to rank-based S+/S/A/B/C/F tiers. F tier reuses the existing `--color-negative`, no dedicated token. (Not reflected in DESIGN.md's own palette table or token count until the 2026-08-25 audit.) |
| n/a | 2026-07-04 (v4.0.0) | Screener responsive redesign: live-resizing auto-hide column groups (no new tokens; a JS/layout behavior change, not a visual-language change), plus a second `min-width: auto` grid-track bug fix (`minmax(0, 1fr)` restored under the mobile media query). Site-wide device-width audit confirmed zero horizontal overflow 375-1920px across all 9 pages. |
| n/a | 2026-07-09 (v4.1.3) | Sidebar brand text resized 0.9rem → 1.125rem with -0.3px letter-spacing; new `.sidebar-brand-sub` muted sub-label class added (references `--color-text-muted`, a token that does not exist in `:root`; see the Color Palette discrepancy note above). Shipped without a DESIGN.md update at the time; backfilled here. |
| n/a | 2026-07-10 (v4.1.0-v4.1.6) | `market.html` (9th content page) introduced an entirely new component family not previously documented: card-grid layout, category sections, up/down/flat state cards, a stale-data banner, and a time-of-day emoji badge. See the new Market Overview Cards subsection under Component Patterns, and the added row in the Social Cards per-page table, both added in this 2026-08-25 audit. |
| 2.1 | 2026-08-25 | **Documentation audit.** No visual or component changes shipped alongside this entry: this is a docs-accuracy pass. Corrected: token count (14 → 20) in the CSS File Structure section; added the 5 tier tokens (present in the palette table since v3.29.0/v3.30.0 but never reflected in the file's own token-count line); added the Market Overview Cards component family; added `market.html` to the Social Cards table; corrected the modal full-width breakpoint (900px → 1023px, matching current code) and flagged its exact desktop width as unconfirmed; flagged the undefined `--color-text-muted` CSS reference as a code bug, not a doc error; extended this Version History table from v3.23 (2026-06-29) through the present, closing a roughly seven-week, 50-plus-release gap during which the file was not updated. See PRD.md's Documentation Versus Reality table for the full discrepancy record and PATCHNOTES.md for the corresponding entry. |
