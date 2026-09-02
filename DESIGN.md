---
name: Oklahoma
description: The S&P 500 universe read as an ECG strip; every figure a measured trace on ruled paper.
colors:
  paper: "#fdfcfa"
  paper-2: "#f5f2ec"
  paper-3: "#ebe6dd"
  rule: "#f0d1c8"
  rule-heavy: "#e0a191"
  hair: "#d8cfc1"
  ink: "#181510"
  ink-2: "#5c564c"
  ink-3: "#726a5e"
  pen: "#1d3f9e"
  pen-soft: "rgba(29, 63, 158, 0.10)"
  pencil: "#c6432b"
  pencil-soft: "rgba(198, 67, 43, 0.12)"
typography:
  display:
    fontFamily: "Barlow Condensed, Arial Narrow, Helvetica Neue, Arial, sans-serif"
    fontSize: "44px"
    fontWeight: 700
    lineHeight: "44px"
    letterSpacing: "0.01em"
  headline:
    fontFamily: "Barlow Condensed, Arial Narrow, Helvetica Neue, Arial, sans-serif"
    fontSize: "32px"
    fontWeight: 700
    lineHeight: "36px"
    letterSpacing: "0.01em"
  title:
    fontFamily: "Chivo Mono, ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "28px"
    fontWeight: 700
    lineHeight: "32px"
    letterSpacing: "0.01em"
  figure:
    fontFamily: "Chivo Mono, ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "18px"
    fontWeight: 500
    lineHeight: "24px"
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Barlow, Helvetica Neue, Arial, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: "20px"
    letterSpacing: "normal"
  label:
    fontFamily: "Barlow Condensed, Arial Narrow, Helvetica Neue, Arial, sans-serif"
    fontSize: "11px"
    fontWeight: 600
    lineHeight: "16px"
    letterSpacing: "0.06em"
  meta:
    fontFamily: "Chivo Mono, ui-monospace, SF Mono, Menlo, Consolas, monospace"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: "16px"
    letterSpacing: "normal"
rounded:
  none: "0px"
  hair: "1px"
  sm: "2px"
  pill: "12px"
spacing:
  box: "4px"
  2x: "8px"
  3x: "12px"
  4x: "16px"
  big: "20px"
  6x: "24px"
  8x: "32px"
  row-phone: "60px"
  row-desktop: "80px"
components:
  lead-chip:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "0 10px"
    height: "28px"
  lead-chip-pressed:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.sm}"
    padding: "0 10px"
    height: "28px"
  button-outline:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: "0 12px"
    height: "32px"
  button-text:
    backgroundColor: "transparent"
    textColor: "{colors.pen}"
    padding: "0"
  button-watch:
    backgroundColor: "transparent"
    textColor: "{colors.pencil}"
    rounded: "{rounded.sm}"
    padding: "0 14px"
    height: "40px"
  button-watch-pressed:
    backgroundColor: "{colors.pencil-soft}"
    textColor: "{colors.pencil}"
    rounded: "{rounded.sm}"
    padding: "0 14px"
    height: "40px"
  input-search:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0"
    height: "40px"
  band-row:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "8px 10px"
  sheet-card:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "12px 16px 24px"
    width: "640px"
  tabbar:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-3}"
    height: "56px"
  stale-band:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    padding: "10px 16px"
---

# Design System: Oklahoma

## Overview

**Creative North Star: "The ECG Strip"**

Oklahoma is one page, read by one owner after the U.S. close, on a phone under a desk lamp. The build treats the universe as a strip chart coming off a recording machine: warm-white paper, a printed masthead, a ruled search line, and then one name per ruled row with a calibrated trace in the middle. Nothing on the page is decorative; the salmon ECG grid exists so every sparkline has a stated scale (a printed gain in percent per heavy box and a one-box calibration pulse), which is what turns a sparkline into a measurement.

The world is single and light. The dark theme that PRODUCT.md lists as an incumbent capability was cut on purpose for the desk-lamp scene; `<meta name="color-scheme" content="light">` is shipped and no dark tokens exist. Colour carries function only: near-black thermal ink for everything printed, ballpoint blue for anything tappable, red grease pencil for the owner's own mark. Sector hue coding and green/red sign coding are absent; the sign is carried by the glyph itself (a true minus, U+2212) and by the trace's direction, and sectors are named by three-letter lead codes (TEC, FIN, HLT) in mono.

Density is instrument-grade: one 4px box rules type sizes, line heights, gaps and row heights, and the traces' grid is the same ruler at 20px per heavy box, so figures and traces read against one scale. Surfaces are flat; the only shadow on the page is the sheet lifting off the paper.

**Key Characteristics:**
- Warm-white paper ground with salmon rules confined to SVG trace panels
- Three inks (thermal near-black, ballpoint blue, grease-pencil red), each with one job
- Barlow Condensed uppercase heads, Barlow body, Chivo Mono figures with true signs
- A 4px box ruler shared by type, spacing, row heights and the trace grid
- Calibrated traces: fixed time per box, printed gain, one-box pulse, dashed when history is short
- Flat, ruled surfaces; 1px hairlines and 2px ink rules instead of cards
- Bottom sheets with one authored entrance; the stylus writes traces in at constant speed

## Colors

A paper-and-ink palette: three warm-white paper tones, two salmon rules, a hairline, three ink weights, and two functional accents that never decorate.

### Primary
- **Ballpoint Pen** (`pen`): the colour of anything tappable that is not a bordered button: explain links under measurement labels (`.xl`), text buttons, the fit-toggle, the search line and its icon on focus, the focus ring, the search caret, and the dashed fitted-trend overlay inside a trace. If it is pen-blue, tapping it does something.
- **Pen Soft** (`pen-soft`): the pen at 10% alpha. Declared as a token and reserved for pen-tinted fills; the build currently uses the pen's own colour at 50% alpha only for the resting underline of explain links.

### Secondary
- **Grease Pencil** (`pencil`): one job. The watchlist mark: the stroked star drawn on a strip, the count badge on the Watchlist tab, and the "Mark for the watchlist" button's border and text. Never used for emphasis, warnings, or negative figures.
- **Pencil Soft** (`pencil-soft`): the pencil at 12% alpha; the pressed fill of the watch button.

### Neutral
- **Paper** (`paper`): the page ground, the tab bar, sheet cards, sticky table heads, the switch track and select fill. Also the text colour on ink-filled controls and the stale band.
- **Paper 2** (`paper-2`): hover and grouped-section header tint; formula code blocks in the explain sheet.
- **Paper 3** (`paper-3`): pressed state of a strip row; the count digits inside a pressed lead chip.
- **Rule** (`rule`): the fine 1mm rule of the ECG grid, stroke 0.6 inside `#ecg-grid`; also the text-selection highlight.
- **Rule Heavy** (`rule-heavy`): the 5mm heavy rule, stroke 1, and the hairline that closes the sheet shadow at the top of a sheet.
- **Hair** (`hair`): the warm hairline between rows, table cells, band cells and settings rows; the sheet handle; resting border of leader/laggard chips.
- **Thermal Ink** (`ink`): all primary text, traces with full history, 1px and 2px structural rules, filled pressed controls, the breadth bar, the stale band background.
- **Ink 2** (`ink-2`): secondary text (company names, mast line, result line, explain body), the calibration pulse, dashed short-history traces.
- **Ink 3** (`ink-3`): tertiary text (rank, units, gain labels, placeholders, dashes for missing figures), resting tab labels, chevrons, the scrollbar thumb.

### Named Rules
**The Rules Stay On The Paper Rule.** Salmon rules appear only inside an SVG trace panel via the `#ecg-grid` pattern (a 20-unit tile with fine rules every 4 units and a heavy rule on the tile edge). Page dividers are ink or hairline, never salmon; the grid is a scale, not a texture.

**The Three Inks Rule.** Ink prints, pen taps, pencil marks. No other hue may appear: no sector colours, no green/red for sign, no status tints. A negative figure looks exactly like a positive one apart from its minus sign.

**The Pressed Is Filled Rule.** A selected chip, segment or switch inverts to ink fill with paper text. Selection is never shown by a tint or a coloured border.

## Typography

**Display Font:** Barlow Condensed (with Arial Narrow, Helvetica Neue, Arial)
**Body Font:** Barlow (with Helvetica Neue, Arial)
**Label/Mono Font:** Chivo Mono (with ui-monospace, SF Mono, Menlo, Consolas)

**Character:** A printout. Condensed uppercase heads set like a machine's stencilled nameplate, a plain grotesk for the few sentences, and a wide monospace for every figure, code and calibration line. Tabular numerals are on for the whole body. Signed figures use `+` and a true minus (U+2212); missing figures print an em dash.

### Hierarchy
- **Display** (700, 44px/44px phone; 56px/52px from 720px, uppercase, 0.01em): the masthead "OKLAHOMA" only.
- **Headline** (700, 32px/36px, uppercase, 0.01em): panel titles (Sectors, Watchlist, Settings) over a 2px ink rule. Explain-sheet titles step down to 26px/28px.
- **Title** (700 mono, 28px/32px, 0.01em): the ticker at the head of the detail sheet. Tickers in strips are the same voice at 15px/20px, 0.02em; in tables 12px.
- **Figure** (500 mono, 18px/24px, -0.01em): measurement values in band cells and sector stats. The strip's own figure is 15px/20px; desktop side windows 400 at 13px/20px.
- **Body** (400, 15px/20px): setting labels, explain prose (22px leading, max 60ch), detail company name.
- **Label** (600 condensed, 11px/16px, uppercase, 0.06em): band-cell and stat labels, table heads. Section labels widen to 0.08em (rhythm title, tab labels, Leaders/Laggards) and 0.10em (settings group titles at ink-3).
- **Meta** (400 mono, 12px/16px): mast line, calibration line, fact line, axis dates, units under figures; 11px/16px for rank, gain labels and window labels; 9px/10px for the gain printed in a trace's corner.

### Named Rules
**The Figures Are Mono Rule.** Every number, ticker, sector code, date and formula is set in Chivo Mono; Barlow never carries a figure. Units and windows sit under or beside the value in a smaller mono at ink-3.

**The True Sign Rule.** Positive figures carry `+`, negatives carry U+2212, never a hyphen, and the sign is never coloured; missing values are an em dash at ink-3.

**The Condensed Is Uppercase Rule.** Barlow Condensed appears only uppercase with tracking (0.01em at display size, 0.04-0.10em at label size). It is never used for running text.

## Layout

One centred shell, max 960px, with 16px side padding; full-bleed elements (stale band, chip rail, table wrap) pull out with -16px margins. The page is a single column of ruled rows; there is no card grid anywhere. The body keeps `64px + safe-area` clear for the fixed tab bar.

**The box ruler.** `--box` is 4px and `--big` is 20px (five boxes). Observed rhythm: 2, 4, 6, 8, 10, 12, 16, 20, 24, 32px gaps and paddings; control heights of 28, 32, 40, 56 and 60/80px; line heights of 10, 14, 16, 20, 24, 28, 32, 36, 44 and 52px. The trace grid uses the same 20px heavy box in SVG user units.

**Breakpoint.** One, at 720px (`min-width: 720px`; the same media query drives JS via `DESKTOP`). Below it the masthead stacks and the strip row is 60px tall with columns `28px | name | 128px trace | 76px figure` at 8px gutters; the market-cap sub-line is hidden. From 720px the masthead becomes a two-column grid with the mast lines right-aligned, the strip row grows to 80px with columns `32px | name (min 160px) | 250px trace | 3 × 84px shorter windows | 120px figure` at 12px gutters, and the sector leads grid goes to three columns with 24px gutters.

**Strip row anatomy.** Rank at ink-3 right-aligned, ticker bold mono over company name in body at ink-2, the trace, then the signed figure with its window and gain label stacked right. On phone the trace is 6 heavy boxes wide by 2 tall (130×40 display px), one box = two months; on desktop 12 by 3 (250×60), one box = one month, with 1-, 3- and 6-month figures printed beside. The result line above the list carries the ruler statement (`1 box = 2 mo × gain` or `1 box = 1 mo × gain`) as an explain link.

**Table view.** A dense measurement table (12px mono, 32px rows, hairline row rules), sticky condensed-uppercase heads with an inset ink rule, sticky first column, minimum width 760px scrolling inside a -16px bleed, capped at `100dvh - 180px`.

**Sheets.** Detail and explain open as bottom sheets: a scrim of ink at 38%, the card at full width up to 640px, max height `100dvh - 40px`, 12px/16px padding plus 24px + safe-area at the bottom, scrolling internally while the page is locked.

## Elevation & Depth

Flat by default. Depth is drawn, not lit: 1px hairlines between rows, 1px ink borders around controls and band rows, and 2px ink rules under the masthead and panel titles. Hover on pointer devices tints a row to paper-2; press tints it to paper-3. The one shadow in the system belongs to the sheet card as it lifts off the page.

### Shadow Vocabulary
- **Sheet lift** (`box-shadow: 0 -8px 28px rgba(24, 21, 16, 0.18), 0 -1px 0 #e0a191`): the detail and explain sheets only, paired with a 2px ink top border and a 38% ink scrim behind.
- **Table head rule** (`box-shadow: inset 0 -1px 0 #181510`): the sticky table header's bottom rule; a rule drawn with a shadow, not an elevation.

### Named Rules
**The One Shadow Rule.** Nothing but a sheet casts a shadow. Buttons, chips, rows, bands and the tab bar are flat and bordered.

## Shapes

Square paper. Corners are 0 on rows, bands, tables, sheets and the tab bar; bordered controls (chips, outline buttons, selects, icon buttons, the watch button, the warn tag) take a 2px radius, just enough to keep 1px ink borders from looking chipped; the segment's inner buttons take 1px. The only round forms are the 24px switch (12px radius, 16px circular knob) and the 6px scrollbar thumb (3px). Borders are 1px in ink for controls, 1px hair for dividers, 2px ink for section rules; borders never carry colour except the pencil-bordered watch button and the pen-bordered warn tag.

The trace's silhouettes are the signature geometry: a rectangular calibration pulse two units wide and one heavy box tall at the left edge of every trace, and an end dot of radius 2. The pencil mark is one open stroke, a slightly overshooting star rotated -9°, drawn at stroke 1.7 with round joins.

## Components

### Buttons
- **Shape:** near-square (2px radius), 1px border, no fill at rest.
- **Outline** (`.dp-close`, `.ep-close`, `.icon-btn`, `select`): 32px tall, ink border, ink text, condensed uppercase 13px at 0.06em for word buttons, mono 13px for selects; icon buttons are a 32px square holding a 14px stroked SVG.
- **Text** (`.text-btn`, `.fit-toggle`, `.xl`): pen text with a 1px underline offset 3px; hover thickens the underline to 2px (text buttons) or darkens it from 50% alpha to full pen (explain links). A pressed fit-toggle goes to ink with no underline.
- **Watch** (`.watch-btn`): 40px tall, pencil border and text, 14px body, the pencil-mark star at 16px inside; pressed fills with pencil-soft. This is the only pencil-coloured control.
- **Focus:** a 2px pen outline offset 2px on every focusable element.
- **Motion:** background and colour transitions at 120ms on `--ease-out` (`cubic-bezier(0.2, 0.8, 0.2, 1)`).

### Chips
- **Lead chip** (`.lead-btn`): 28px tall, 1px ink border, 2px radius, three-part label: mono 700 code, condensed uppercase name, mono count at ink-3. Pressed inverts to ink fill with paper text. Rails scroll horizontally with hidden scrollbars.
- **Leader/laggard chip** (`.xchip`): 28px, hairline border, mono 700 ticker with a 400-weight figure at ink-2; hover raises the border to ink and tints paper-2.
- **Warn tag** (`.warn`): 10px mono at pen with a pen border, for short-history flags on the ticker line.

### Segment and switch
- **Segment** (`.seg`): a 1px ink frame with 3px inset holding 28px condensed-uppercase buttons; the selected one fills ink.
- **Switch** (`.switch`): 44×24 ink-bordered pill; checked fills ink and slides the paper knob 20px over 160ms.

### Inputs / Fields
- **Search** (`.search`): no box; a 40px line with a 1px ink rule beneath, a 16px stroked search icon at ink-3, 16px body input on transparent, placeholder at ink-3. Focus turns the rule, icon and caret pen; the input's own outline is suppressed in favour of the line.

### Containers
- **Strip row** (`.strip`): the list item; see Layout for anatomy. No border of its own; rows are separated by hair rules with an ink rule opening the list.
- **Band row** (`.band-row`): the measurement bands of the detail sheet: one 1px ink frame divided into two, three or four cells by hairlines, each cell a pen explain-label (label voice) over a figure over a mono unit line at ink-3. Adjoining cells belong to one family (four windows; off-high and vs-sector; trend, R² and quality).
- **Grouped lead head** (`.lead-head`): a 40px paper-2 bar with a rotating chevron, code, condensed name and count.
- **Stale band** (`.band`): ink fill, paper mono uppercase 12px at 0.04em, printed full-bleed across the top only when the data is more than five days old.

### Navigation
- **Tab bar** (`.tabbar`): fixed at the bottom, paper fill, 1px ink top rule, four equal 56px cells plus safe-area. Each cell stacks a 22px authored stroked SVG icon (`#i-strips`, `#i-leads`, `#i-star-o`, `#i-settings`; stroke 1.6, no fill) over a condensed uppercase 11px label at 0.08em. Resting cells are ink-3; the selected cell is ink with a 2px ink bar across the middle 60% of its top edge. The Watchlist cell carries a pencil-coloured mono count badge when the list is non-empty.

### Sheets
- **Bottom sheet** (`.sheet` + `.sheet-card`): scrim fades in over 160ms while the card rises 24px from 60% opacity over 240ms on `--ease-out`; one entrance, no exit animation, none at all under reduced motion. A 40×4 hair handle heads the card. The detail sheet stacks head (ticker title, company, close button), fact line, band rows, the rhythm strip, the trend band, the watch row and detail meta; the explain sheet stacks a headline, a body paragraph, a formula block (hair border on paper-2, mono 12px) and an optional definition list.

### Trace (signature)
`trace(series, boxesW, boxesH, opts)` builds an SVG whose viewBox is `10 + boxesW × 20` by `boxesH × 20`, filled with the `#ecg-grid` pattern. Time per box is fixed by the strip's width. The gain is the smallest of a fixed set (5, 10, 25, 50, 100, 250, 500, 1000 %/box) that fits the series with its zero line on a heavy rule; it is printed as `N%/box` beside the figure (strips), in the lead line (sectors) and in the rhythm title (`252 sessions · 1 box = 21 sessions × N%`). A calibration pulse one box tall stands at the left in ink-2, stroke 1. The trace is ink at 1.5 with round joins and ends in a radius-2 dot; short-history names are drawn dashed (3 3) in ink-2 at 1.25; the fitted trend overlay is pen, dashed (4 3), 1.25. All strokes are `vector-effect: non-scaling-stroke`. On insertion the trace writes itself in: `stroke-dasharray`/`stroke-dashoffset` set to the measured path length and animated to zero over 640ms `linear` (constant, not eased, like a stylus); dashed traces and reduced-motion viewers get the finished trace. Sizes in use: 6×2 (phone strip), 12×3 (desktop strip), 12×4 (sector lead and rhythm strip).

### Pencil mark (signature)
`pencilMark()` returns a 20-unit SVG with one open star path rotated -9°, stroke 1.7 round-joined, in pencil at 88% opacity. It sits inside a strip's trace at the corner the trace leaves clear (`clearCorner`: bottom-left when the zero line is in the top half, else top-left; 18px on phone, 22px on desktop, inset 12-14px), beside the ticker in a strip at 16px, beside the detail title at 24px, and inside the watch button at 18px (60% opacity when unpressed). When drawn on a star tap it writes in over 320ms linear.

## Do's and Don'ts

### Do:
- **Do** size everything on the 4px box; use 20px (`--big`) for the heavy box in traces and for section paddings.
- **Do** put every figure in Chivo Mono with `+` / U+2212 signs and an em dash for missing values, unit and window below or beside at ink-3.
- **Do** keep salmon rules inside `#ecg-grid` trace panels; divide the page with 1px hair, 1px ink or 2px ink rules.
- **Do** print a gain label and a one-box calibration pulse on every trace, and draw short-history traces dashed in ink-2.
- **Do** reserve pen for tappable text, focus rings, the caret and the fitted overlay; reserve pencil for the watchlist mark and its button.
- **Do** invert to ink fill with paper text for any selected chip, segment or switch.
- **Do** open secondary content as a bottom sheet with the single rise-and-fade entrance and the sheet-lift shadow.
- **Do** honour `prefers-reduced-motion`: finished traces, no sheet animation, no chevron or knob transitions.

### Don't:
- **Don't** add a dark theme or any second world; the page ships `color-scheme: light` and one token set.
- **Don't** colour sectors or signs; no green/red, no per-sector hues, no status tints. Sectors are three-letter mono codes.
- **Don't** put a shadow on anything but a sheet, or a radius above 2px on anything but the switch and scrollbar.
- **Don't** draw a sparkline without its grid, gain and pulse; an uncalibrated trace is decoration.
- **Don't** ease the stylus; trace and pencil write-ins are `linear`.
- **Don't** use Barlow Condensed in sentence case or for running text, or Barlow for a number.
- **Don't** add cards, pills or badges; the row, the band and the chip are the only containers.
- **Don't** add buy or sell actions, trade nudges, mascots or characters.
