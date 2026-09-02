# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

One user: the repository owner, a physician in internal medicine who manages a personal investment portfolio. Not a professional investor and not building for anyone else. The page is public on GitHub Pages, but no other audience is designed for.

Situation (confirmed 2026-09-02): seated, under a desk lamp or in daylight, in the evening after the U.S. close, in a short session of a few minutes. The phone is the primary device; a laptop is a plausible second screen but not the design target.

## Product Purpose

Oklahoma is a U.S. equity universe (currently the S&P 500 membership, refreshed daily) with a year of dividend- and split-adjusted price history and a page for inspecting it.

The job of the page is **shortlisting for further research**. A good session ends with a few starred names in the watchlist that the owner then researches elsewhere before any trade. The page never places, sizes, or recommends trades. Success is leaving in minutes with a shortlist, trusting the numbers.

## Positioning

A personal research instrument, not a brokerage screener, a news feed, or a product for sale. What a neighboring tool could not truthfully copy:

- Membership is delegated to a published index committee, so there is no home-grown selection logic and the index's entry/exit buffer supplies turnover hysteresis for free.
- Every derived figure is recomputed from committed bar files at build time, so the page can never disagree with the data it claims to show. CI fails if the generated page drifts from the data.
- Every figure is tap-to-explain with a plain-language sentence and its formula.
- The refresh fails loudly: the offline test suite gates each data commit, and the page shows a stale banner when its data is more than five days old.

## Operating Context

- **Data source:** Financial Modeling Prep. S&P 500 constituents from `stable/sp500-constituent`; end-of-day bars from the dividend-adjusted endpoint, with `adj_close` as the canonical series. The API key lives in `FMP_API_KEY` and is never written to disk or into generated files.
- **Refresh ritual:** GitHub Actions runs at 01:30 UTC Tue–Sat (after each U.S. session), pulls universe and history, runs the tests, and commits to `main` only when something changed. GitHub Pages serves `web/` from `main`.
- **Owner ritual:** open the page after the close; scan the cross-section, sort and filter the list, open per-name detail, star names to the browser-local watchlist; research the shortlist in other tools (brokerage, filings, news) before acting.
- **CLI:** `python -m oklahoma refresh | history | show | build-ui | export-csv | export-returns`.
- **Runs anywhere:** the generated page works from disk, from a static host, or over `python -m http.server`. No backend.

## Capabilities and Constraints

**Universe membership (owner decision, 2026-09-02):** the former hard rule that the universe must be exactly the S&P 500 is dropped. The current implementation uses the S&P 500, and no custom selection logic exists today, but future work may adopt another published index or a custom universe with the owner's agreement. Delegating membership to an authoritative source remains the preferred approach until the owner decides otherwise.

**Implementation constraints (owner relaxed all of these on 2026-09-02).** They describe the current state and may be changed when the result is clearly better:

- Python 3.10+ standard library only for the data pipeline; no third-party dependencies. A small, well-justified dependency is acceptable.
- One self-contained `web/index.html`, rendered from `web/template.html` by substituting two JSON placeholders (`__UNIVERSE_JSON__`, `__HISTORY_JSON__`). Build tooling or a bundler is acceptable if it does not break the from-disk and GitHub Pages deployment.
- No JS frameworks or chart libraries in the page; Google Fonts is the only external resource. A vanilla library or a chart library is acceptable.
- Watchlist and settings live in `localStorage`. No accounts, no sync, no server-side state.
- Existing features may be cut or merged when a simpler page shortlists better; no feature is protected by itself.

**Confirmed capabilities (current implementation):**

- Universe list with rank, sector, industry, exchange, market cap, CIK, share classes, and date first added.
- Return windows: 12-month (252 sessions), 6-month (126), 3-month (63), 1-month (21), each measured only where its full window of bars exists; otherwise a dash.
- Log trend over 12 months (annualized slope and R²) and quality momentum (trend × R²).
- Distance from 12-month high and return vs sector median.
- Cross-section: per-sector median return and breadth, plus the five leaders and laggards, over names with a full window.
- Per-name detail sheet with cumulative-return chart and optional fitted trend line.
- Cards and table views, search, sector chips, sort by any column, group by sector, view/figure/sort remembered per device.
- Watchlist with copy/paste tools and a per-name note of sector concentration in the current watchlist.
- Membership change log (joined, left, renamed by CIK) and a stale-data banner.
- Light and dark themes.

**Terminology to keep:** universe, constituent, coverage, sufficient, window, `adj_close`, cross-section, breadth, quality momentum, share classes, CIK.

## Brand Commitments

- Name: **Oklahoma**; page title **Oklahoma Universe**.
- Voice (in README and page): plain language, precise, shows its reasoning, no hype, no advice. Keep it.
- No logo or brand assets exist.
- **Binding negatives (owner, 2026-09-02):** no buy or sell buttons, no trade nudges, and no mascots or characters. Anything that reads as a brokerage call to action or a consumer-fintech personality is wrong regardless of polish.
- **Standing visual preference (owner, 2026-09-02):** the page follows the conventions of consumer brokerage apps, Robinhood first among them, executed at their craft level: a light ground with a true-black dark theme, one green accent with red reserved for negative figures, a hero figure over a large line chart, sparkline rows with a price and a coloured return, and per-name pages with a 1M / 3M / 6M / 1Y range selector and a key-stats grid. Both light and dark themes are first-class. The owner reviewed and declined an ECG-strip world and a lab-report world in favour of this familiar register; a future redesign should start from this preference, not from a novelty search.
- The earlier look (IBM Plex Sans/Mono and Newsreader, teal accent on pale ground) is gone and is not a commitment.

## Evidence on Hand

- Real data: `data/universe.json` (503 names as of 2026-09-01), `data/history/*.json` (about 300 bars per name), `data/history/index.json` (coverage manifest), `data/changes.json` (membership change log).
- Generated page `web/index.html` and its source `web/template.html`, carrying the incumbent visual system described above, not documented in a DESIGN.md.
- Offline tests in `tests/` with fixtures; CI on Python 3.10 and 3.13 plus a generated-page drift check.
- **Absent, never fabricate:** the owner's actual holdings (the page does not know what is owned), testimonials or other users, backtests or performance claims, buy/sell recommendations.

## Product Principles

1. **Trustworthy before pretty.** Every figure is recomputed from committed data, explained on tap, and dated. Nothing on the page is a number the data cannot back.
2. **Shortlist, never decide.** The page ends at a starred name, not at a trade. No advice language, no sizing, no urgency, no buttons that act on money.
3. **Minutes, seated, mostly on a phone.** Scanability and one-thumb operation outrank exploration; a laptop must not be broken, but the phone decides.
4. **Delegate what should not be invented.** Adjusted prices, refresh timing, and, for now, index membership come from authoritative sources; the tool's job is honest derivation and presentation.
5. **Fail loudly, never quietly stale.** A broken refresh must look broken.
6. **An instrument, not a product.** One owner, no audience to persuade; the design serves the reading, and its personality lives in precision rather than charm.
