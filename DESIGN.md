---
name: Oklahoma
description: A brokerage-register stocks list for one owner, light and dark, one green accent, red only for losses.
colors:
  ground: "#ffffff"
  ground-2: "#f3f4f6"
  ground-3: "#e8eaed"
  hairline: "#eceef0"
  hairline-2: "#d4d8dc"
  ink: "#1b1b1b"
  ink-2: "#6b6f74"
  ink-3: "#767a7e"
  up: "#00c805"
  up-text: "#00891c"
  up-soft: "rgba(0, 200, 5, 0.12)"
  down: "#ff5000"
  down-text: "#d84200"
  down-soft: "rgba(255, 80, 0, 0.12)"
  on-pill: "#0a1f0c"
  on-pill-down: "#2a0e00"
  scrim: "rgba(0, 0, 0, 0.45)"
  ground-dark: "#000000"
  ground-2-dark: "#161616"
  ground-3-dark: "#242424"
  hairline-dark: "#1f1f1f"
  hairline-2-dark: "#333333"
  ink-dark: "#ffffff"
  ink-2-dark: "#a1a5a9"
  ink-3-dark: "#808488"
  up-text-dark: "#00c805"
  down-text-dark: "#ff5000"
typography:
  display:
    fontFamily: "Inter, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "34px"
    fontWeight: 700
    lineHeight: "40px"
    letterSpacing: "-0.02em"
    fontFeature: "tabular-nums"
  headline:
    fontFamily: "Inter, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "20px"
    fontWeight: 700
    lineHeight: "24px"
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Inter, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "17px"
    fontWeight: 700
    lineHeight: "24px"
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Inter, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: "20px"
    fontFeature: "tabular-nums"
  secondary:
    fontFamily: "Inter, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: "18px"
  caption:
    fontFamily: "Inter, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: "16px"
  micro:
    fontFamily: "Inter, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "11px"
    fontWeight: 500
    lineHeight: "14px"
  group-label:
    fontFamily: "Inter, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 600
    lineHeight: "18px"
    letterSpacing: "0.04em"
  mono:
    fontFamily: "ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: "18px"
rounded:
  track: "3px"
  pill: "8px"
  search: "12px"
  chip: "16px"
  control: "18px"
  sheet: "20px"
  button: "24px"
  round: "50%"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  cell: "14px"
  lg: "16px"
  section: "22px"
  xl: "24px"
components:
  range-pill:
    textColor: "{colors.ink-2}"
    typography: "{typography.secondary}"
    rounded: "{rounded.control}"
    height: "36px"
  range-pill-selected:
    backgroundColor: "{colors.up}"
    textColor: "{colors.on-pill}"
    rounded: "{rounded.control}"
    height: "36px"
  range-pill-selected-negative:
    backgroundColor: "{colors.down}"
    textColor: "{colors.on-pill-down}"
    rounded: "{rounded.control}"
    height: "36px"
  chip:
    textColor: "{colors.ink}"
    rounded: "{rounded.chip}"
    padding: "0 14px"
    height: "32px"
  chip-selected:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.ground}"
    rounded: "{rounded.chip}"
    padding: "0 14px"
    height: "32px"
  pill-up:
    backgroundColor: "{colors.up}"
    textColor: "{colors.on-pill}"
    rounded: "{rounded.pill}"
    padding: "1px 8px"
  pill-down:
    backgroundColor: "{colors.down}"
    textColor: "{colors.on-pill-down}"
    rounded: "{rounded.pill}"
    padding: "1px 8px"
  pill-flat:
    backgroundColor: "{colors.ground-3}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "1px 8px"
  pill-none:
    textColor: "{colors.ink-3}"
    rounded: "{rounded.pill}"
    padding: "1px 8px"
  search:
    backgroundColor: "{colors.ground-2}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.search}"
    padding: "0 14px"
    height: "44px"
  watch-button:
    textColor: "{colors.up-text}"
    rounded: "{rounded.button}"
    height: "48px"
    width: "100%"
  watch-button-pressed:
    backgroundColor: "{colors.up}"
    textColor: "{colors.on-pill}"
    rounded: "{rounded.button}"
    height: "48px"
    width: "100%"
  text-button:
    textColor: "{colors.up-text}"
  segmented:
    backgroundColor: "{colors.ground-2}"
    rounded: "{rounded.control}"
    padding: "3px"
  segmented-option-selected:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.ground}"
    rounded: "{rounded.control}"
    height: "30px"
    padding: "0 12px"
  xchip:
    backgroundColor: "{colors.ground-2}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0 10px"
    height: "30px"
  tab-badge:
    backgroundColor: "{colors.up}"
    textColor: "{colors.on-pill}"
    rounded: "{rounded.pill}"
    height: "16px"
  sheet-card:
    backgroundColor: "{colors.ground}"
    rounded: "{rounded.sheet}"
    padding: "8px 16px 24px"
  close-button:
    backgroundColor: "{colors.ground-2}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sheet}"
    height: "44px"
    width: "100%"
  stale-band:
    backgroundColor: "{colors.down}"
    textColor: "{colors.on-pill-down}"
    padding: "10px 16px"
---

# Design System: Oklahoma

## Overview

**Creative North Star: "The Brokerage Watchlist, Played Straight"**

Oklahoma is a consumer-brokerage stocks list executed at that category's craft level and refusing everything else: no metaphor, no ornament, no mascot, no call to act. The page looks like the app a person already keeps on their phone, with the one thing a broker cannot show, a universe median as the hero figure and honest return windows as the range selector. Its personality lives in precision: tabular figures, true minus signs, hairline dividers, and a single green that means either "gain" or "you can act here".

The system is a flat, two-theme world. Light sits on pure white; dark sits on true black with two lifted greys. Both are first-class and are driven by `prefers-color-scheme` with a `data-theme` override chosen in Settings (System / Light / Dark). Nothing is elevated at rest; depth exists only when a sheet slides over the page. Density is phone-first: one column, 16px gutters, 760px container on a laptop, rows that read in a single glance (ticker and name, sparkline, price and a coloured return pill).

The build follows the direction contract's OWN-WORLD block closely. The one place it landed differently from the plain reading of "outline pill buttons" is that outline treatment is reserved for the watchlist button and the sector chips; range pills, segmented controls and the close button are filled tonal shapes with no border.

**Key Characteristics:**
- Pure white or true black ground, hairline dividers, no cards
- Inter 400–700 with tabular figures everywhere, real minus signs
- One green accent for actions and gains; red appears only on losses and the stale-data band
- Fully rounded pills, chips and buttons; 20px sheets; 8px return pills
- Sparklines in every row, one large chart in the hero and on each name page
- Authored 24px stroke icons in an inline SVG sprite; no icon font, no glyphs

## Colors

A monochrome ground with one saturated signal green and one reserved loss orange-red, each in a fill form and a text form.

### Primary
- **Signal Green** (`up`): the only accent. Fills the selected range pill, positive return pills, the pressed watch button, the tab badge, the breadth bar, the switch when on, and every focus ring, caret and selection tint (`up-soft`). Also the stroke of any rising line chart.
- **Green Ink** (`up-text`): green as text on the light ground: sort control, "Copy tickers" text buttons, the watchlist star, the outline watch button label, and any `.up` figure. In dark it collapses to Signal Green because pure `#00c805` on black is legible while on white it is not.

### Neutral
- **Ground** (`ground` / `ground-dark`): the page, the tab bar, sticky table headers, the sheet card, the switch knob.
- **Ground 2** (`ground-2` / `ground-2-dark`): the search field, segmented-control tracks, extreme chips, formula blocks, row and table hover.
- **Ground 3** (`ground-3` / `ground-3-dark`): the flat pill, the switch track when off, the breadth-bar track, hover on an extreme chip.
- **Hairline** (`hairline` / `hairline-dark`): every list divider, the range selector's underline, the tab bar's top edge.
- **Hairline 2** (`hairline-2` / `hairline-2-dark`): chip and select outlines, the "no data" pill outline, the sheet handle, the chart's dashed zero line, the dotted underline under explain labels, the scrollbar thumb.
- **Ink** (`ink` / `ink-dark`): primary text, the selected chip and segmented option fill, the scrub dot.
- **Ink 2** (`ink-2` / `ink-2-dark`): company names, subtitles, table headers, unselected controls, placeholders, the scrub line.
- **Ink 3** (`ink-3` / `ink-3-dark`): captions, "—" placeholders, chevrons, the footer, flat sparklines, the dashed trend overlay.

### Loss
- **Loss Red** (`down`): fills negative return pills, a negative selected range pill, and the stale-data band. Also the stroke of a falling line chart.
- **Red Ink** (`down-text`): negative figures as text on light; collapses to Loss Red in dark.
- **Pill Ink** (`on-pill`, `on-pill-down`): near-black green and near-black red for text sitting on the coloured fills. Coloured pills never carry white text.

### Named Rules
**The One Accent Rule.** Green is the only accent and it carries two meanings, gain and action; red carries exactly one, loss (plus the broken-refresh band). Neutral metrics (market cap, R², last close) render in the flat grey pill, never in colour.

**The Two Greens Rule.** `up` is a fill, `up-text` is text. Green text on the light ground always uses `up-text`; the same holds for `down` and `down-text`. Dark mode collapses each pair to the fill colour.

**The Dark Ink on Colour Rule.** Anything sitting on a green or red fill uses `on-pill` / `on-pill-down`, never white.

**The True Black Rule.** Dark mode is `#000000`, not a charcoal; the lifted surfaces are `#161616` and `#242424`. The `theme-color` meta follows the ground exactly.

## Typography

**Display Font:** Inter (with -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial)
**Body Font:** Inter (same stack)
**Label/Mono Font:** ui-monospace / SF Mono / Menlo / Consolas, used only for data endpoints and the explain-sheet formula

**Character:** One family, four weights (400, 500, 600, 700), tabular figures on the body so every column of numbers aligns. Hierarchy comes from weight and size, with a slight negative tracking on the largest sizes; there is no italic and no second face.

### Hierarchy
- **Display** (700, 34px/40px, -0.02em): the hero median figure and the ticker on a name page. Bold, tight, coloured green or red by sign in the hero.
- **Headline** (700, 20px/24px, -0.01em): section heads ("Stocks", "Key stats", "About the numbers"); the explain sheet's heading is the same voice at 22px/28px.
- **Title** (700, 17px/24px, -0.01em): the title bar's app name, paired with a 13px/20px `ink-2` subtitle on the same baseline.
- **Body** (400, 15px/20px): row tickers at 600, prices at 500, stat values at 500, settings labels at 400, the watch button at 600. 15px is also the search input and sheet paragraphs (at 22px leading, max 60ch).
- **Secondary** (400, 13px/18px): company names, subtitles, meta lines, stat labels, chip and range labels (at 500–600), the table's cell text.
- **Caption** (400, 12px/16px): stat sub-lines, chart footers, watch-tool notes, uppercase Settings group titles (600, 0.06em).
- **Micro** (500, 11px/14px): tab bar labels (600 when selected). The tab badge and the row's short-history mark go to 10px/16px.
- **Group Label** (600, 13px/18px, 0.04em, uppercase): collapsible sector group headers in the grouped list.

### Named Rules
**The Tabular Rule.** Figures are tabular everywhere; a price column never jitters as values change.

**The True Minus Rule.** Negative figures use U+2212 "−", never a hyphen; "—" is the only placeholder for missing data.

**The Weight Carries Hierarchy Rule.** Ticker vs company, price vs return, selected vs unselected tab: the difference is weight (600 vs 400/500) before it is size or colour.

## Layout

Single column, phone first. The shell is `max-width: 760px` centred with 16px side padding; full-bleed elements (the chip rail, the stale band, the table scroller) pull out with negative 16px margins. The body reserves `72px + env(safe-area-inset-bottom)` under a fixed 64px tab bar.

Row grid: `minmax(0,1fr) 64px auto` with a 14px column gap and 12px vertical padding, used identically by stock rows and sector rows so sparklines and figures align down the page. The key-stats grid is two columns with a 14px row gap and 24px column gap. Sections open with a 22px top / 8px bottom heading; settings rows are 56px minimum with a hairline under each.

Rhythm is a loose 4px scale: 4 (gaps in tight controls), 8 (chip gaps, pill radius, group gaps), 12 (search top margin, chip rail bottom, control padding), 14 (cell gaps, chip padding), 16 (gutter), 22–24 (section heads, sheet padding, watch button radius).

One breakpoint at 720px: the hero chart's aspect changes from 358:140 to 728:220, and sheets move from bottom-anchored full-height pages to centred cards (max 640px wide, `100dvh - 48px` tall, 20px radius on all corners). Hover treatments are gated by `(hover: hover)`; on touch the row shows no hover state.

## Elevation & Depth

Flat by default. Surfaces separate by hairline (`hairline`) and by tonal step (`ground` → `ground-2` → `ground-3`), never by shadow. The single shadow token appears only on the sheet card lifted over the scrim; the switch knob carries a 1px 3px lift so it reads as a physical toggle; the sticky table header uses a 1px inset line as its edge.

### Shadow Vocabulary
- **Sheet lift** (`box-shadow: 0 10px 30px rgba(0,0,0,0.14), 0 1px 0 var(--line-2)`; dark: `0 10px 30px rgba(0,0,0,0.6), 0 1px 0 var(--line-2)`): the sheet card only.
- **Knob** (`box-shadow: 0 1px 3px rgba(0,0,0,0.25)`): the switch knob only.
- **Sticky edge** (`box-shadow: inset 0 -1px 0 var(--line-2)`): table header row while it sticks.

### Named Rules
**The Hairline Rule.** At rest the page has one plane. Anything that needs an edge gets a 1px `hairline`; anything that needs a surface gets the next grey step. Shadows appear only under a sheet above the scrim.

**The Scrim Stack Rule.** Sheets sit at z-index 30 over a 45% black scrim; the explain sheet at 40 so it can open above a name page; the tab bar at 20 below both.

## Shapes

Everything interactive is a rounded capsule: range pills and segmented options at half their height (18px on 36px, 15px on 30px), chips at 16px on 32px, the watch button at 24px on 48px, the close button at 22px on 44px, the switch at 14px on 28px. Non-interactive containers use small radii: return pills 8px, the search field 12px, formula blocks 10px, sheets 20px on the top corners (all corners when centred). Tracks (breadth bar, scrollbar, sheet handle) are 2–3px rounded bars.

Borders are 1px `hairline-2` on chips, selects and the icon button, and 1.5px `up` on the outline watch button. The selected state of a neutral control (chip, segmented option) inverts to `ink` on `ground`; the selected state of a signed control (range pill, watch button) fills green (or red for a negative window).

Lines in charts are 2px (big) or 1.6px (sparkline) with round joins and caps; short-history series are dashed `3 3`, the trend overlay is dashed `4 4` in `ink-3`, the zero line dashed `2 4` in `hairline-2`. The big chart ends in a 3.5px dot in the line's colour.

## Components

### Buttons
- **Shape:** capsule (radius half of height).
- **Watch (outline, 48px, 24px radius):** 1.5px `up` border, `up-text` label at 600 15px with an 18px star, full width. Pressed: fills `up`, label `on-pill`, star switches to the filled symbol. 120ms ease-out on background and colour.
- **Text button:** `up-text` at 600 14px, no box; hover underlines with a 3px offset. Used for "Copy tickers" / "Paste tickers".
- **Close (44px, 22px radius):** `ground-2` fill, `ink` label at 600 15px, full width at the foot of the explain sheet.
- **Icon button (36px round, 1px `hairline-2` border):** the sort-direction arrow in Settings.
- **Focus:** every control gets a 2px `up` outline offset 2px via `:focus-visible`.

### Chips
- **Sector filter chip (32px, 16px radius):** transparent with a 1px `hairline-2` border, `ink` label at 500 13px with the count in `ink-2`. Selected: `ink` fill, `ground` text, count at 70% opacity. Chips live in a horizontally scrolling rail with hidden scrollbar.
- **Extreme chip (30px, 15px radius):** `ground-2` fill, ticker at 600 13px and value at 500; hover lifts to `ground-3`. Used for sector leaders and laggards.
- **Watch mix tag (24px, 12px radius):** `ground-2` fill, `ink-2` 500 12px with the bold part in `ink`.

### Pills
- **Return pill (8px radius, 1px 8px padding, 600 12px):** `up` / `on-pill` for gains, `down` / `on-pill-down` for losses, `ground-3` / `ink` for flat and neutral metrics, transparent with a `hairline-2` border and `ink-3` text for "—". Direction is decided at ±0.005; "Off 1-year high" reads "At high" above −0.5%.
- **Tab badge (16px, 8px radius, 700 10px):** `up` fill with `on-pill` count, pinned to the upper right of the Watchlist tab icon.

### Range Selector
Four equal-width capsules (36px, 18px radius) in a row with a 4px gap, under the chart and above a hairline. Unselected: `ink-2` at 600 13px. Selected: `up` fill with `on-pill` text; if that window's return is negative the fill is `down`. On a name page the selector is the tall variant (48px) with the window's return under each label at 500 12px. Selecting a window re-bases the chart and swaps the headline figure.

### Search
44px field, 12px radius, `ground-2` fill, 16px search icon in `ink-2`, 15px input with `ink-2` placeholder and a green caret. No border, no focus ring on the input itself (the field is the target).

### Rows
- **Stock row:** the three-column grid; ticker at 600 15px with an optional 14px `up-text` star and a 10px outlined short-history mark; company name and cap at 13px `ink-2` with ellipsis; a 64×26 sparkline coloured by the 12-month sign (dashed when history is short, a dashed hairline when absent); price at 500 15px right-aligned over the return pill. Hover (pointer devices only): `ground-2` fill bleeding 8px past the row edges at 8px radius.
- **Sector row:** the same grid; sector name at 600 15px, a meta line at 12px `ink-2` with a 44×6 breadth bar (`ground-3` track, `up` fill), the median sparkline, and a return pill.
- **Group header:** uppercase 600 13px `ink` label with a 12px chevron in `ink-3` that rotates −90° when collapsed (160ms) and the count right-aligned in `ink-2`.
- **Settings row:** 56px minimum, 15px label left, control right, hairline below; navigational rows end in a 14px chevron.

### Segmented Control and Switch
- **Segmented (`ground-2` track, 18px radius, 3px padding):** options are 30px capsules at 500 13px `ink-2`; the selected option inverts to `ink` on `ground`. Used for Theme and View.
- **Select:** 36px capsule with a 1px `hairline-2` border and an inline chevron; same voice as a chip.
- **Switch (48×28, 14px radius):** `ground-3` track, `ground` knob with the knob shadow; on: `up` track, knob translated 20px, 160ms ease-out.

### Navigation
Fixed bottom tab bar, `ground` fill with a hairline top edge, four equal cells 64px tall, each a 24px authored stroke icon over an 11px label in `ink-2` at 500; the selected tab turns `ink` at 600. Arrow keys move between tabs. The title bar above each panel is a 17px bold name with a 13px `ink-2` subtitle on the same baseline.

### Sheets
- **Name page (`.sheet-card.page`):** on a phone a full-height, square-cornered page rising 24px over 240ms while the scrim fades in over 160ms; at ≥720px a centred 640px card with 20px corners. Top bar: "Back" text with a chevron left, 40px star button right. Then ticker (display), a meta line, the return line, the big chart with its date footer and optional trend-line toggle, the tall range selector, "Key stats", the watch button with a one-line context under it, "About the numbers".
- **Explain sheet (`#explain-pop`):** the same card at z-index 40 with a 36×4 handle, a 22px heading, 15px/22px paragraphs at 60ch, a `ground-2` formula block in mono, an optional definition list, and the close button. Opened from any dotted-underline explain label.
- Both trap focus, close on Escape, return focus to the opener, and lock page scroll with `html.sheet-open`.

### Key Stats
Two-column grid of stat cells: a 13px label (a dotted-underlined `ink-2` button when it has an explanation, plain `ink-2` otherwise), a 15px value at 500 coloured by sign (or `ink-3` when missing), and a 12px `ink-3` sub-line. Hover on an explain label lifts it to `ink` and darkens the underline.

### Line Chart (signature)
`lineChart()` draws a thinned cumulative-return series into a `preserveAspectRatio: none` SVG with non-scaling strokes. Sparklines are 64×26 at 1.6px; big charts fill the hero or page at 2px with a dashed zero line, an end dot, and an optional dashed trend overlay. The stroke is `up`, `down` or `ink-3` by the sign of the window's return. A shorter window is produced by `rebase()`: the tail of the same series re-based to its own start, so chart and headline agree on what zero means. On first paint the line draws in over 560ms ease-out via stroke-dashoffset; under `prefers-reduced-motion` the finished line appears at once, and the sheet's rise and fade are also removed. `attachScrub()` adds pointer scrubbing to big charts: a crosshair cursor, a vertical `ink-2` line with an `ink` dot, the headline swapping to the value under the pointer with an approximate ("≈") interpolated date, and release restoring the window's own figure.

### Stale Band
When the data is more than five days old a full-bleed `down` band with `on-pill-down` 600 13px text sits above the title bar. It is the only red surface that is not a loss figure, and it is meant to look broken.

### Browser Surfaces
Text selection tints `up-soft`; the search caret and every focus ring are `up`; scrollbars are 6px thin with a `hairline-2` thumb; the `color-scheme` meta declares both themes.

## Do's and Don'ts

### Do:
- **Do** keep both themes first-class: every new colour needs a light value and a dark value, and the dark ground stays `#000000`.
- **Do** use `up-text` / `down-text` for coloured text on the light ground and the fill colours only on fills, lines and dark-mode text.
- **Do** put `on-pill` / `on-pill-down` ink on any green or red fill.
- **Do** set figures tabular and negatives with a true minus; use "—" for missing values in `ink-3`.
- **Do** separate surfaces with 1px hairlines or the next grey step; reserve the shadow for a sheet over the scrim.
- **Do** make interactive shapes capsules (radius = half height) and keep return pills at 8px.
- **Do** author icons as 24-viewBox stroke paths (1.6–1.8px, round caps) in the inline sprite.
- **Do** give every control a 2px green `:focus-visible` outline and respect `prefers-reduced-motion` on any new animation.
- **Do** colour a chart line by the sign of its window and draw short-history series dashed.

### Don't:
- **Don't** add a second accent or use green and red for anything but action/gain and loss/broken-refresh.
- **Don't** colour neutral metrics (market cap, R², last close); they take the flat grey pill.
- **Don't** put white text on a coloured pill or use `#00c805` as text on white.
- **Don't** use shadows, cards or borders to lift resting content; the page is one plane.
- **Don't** add buy or sell buttons, trade nudges, mascots or characters (owner's binding negatives).
- **Don't** introduce a second typeface, italics, or an icon font; Inter and the authored SVG sprite are the whole vocabulary.
- **Don't** add eyebrow labels above headings; the only uppercase text is the collapsible group header and the Settings group title.
- **Don't** write a hyphen where a minus belongs, or a decimal-free return where the row shows two places.
