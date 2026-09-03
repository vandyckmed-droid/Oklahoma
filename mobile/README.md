# Oklahoma on a phone — Expo Go client

An Expo app that runs in stock **Expo Go**, with no development build, no
desktop setup, and no Expo account.

## Open it

Tap this on your phone, then choose **Open in Expo Go** (or scan the QR the
page shows):

```
python3 mobile/snack-link.py        # prints the current link
```

The link is a [Snack](https://snack.expo.dev) that loads `mobile/App.js`
straight from this repository over HTTPS. Two consequences worth knowing:

- It works against an **unmerged branch**, so the app is testable while the
  pull request is still open.
- Snack re-fetches on every open, so the link **never goes stale**. Pushing to
  the branch changes what Expo Go runs, with nothing to republish. After the
  PR merges, regenerate the link with `--ref main`.

## What it is

A native shell around the generated page at `web/index.html` — **not** a second
implementation of the app.

Every number Oklahoma shows is computed once, in Python (`oklahoma/metrics.py`),
committed to `data/`, and rendered into `web/index.html` by the daily refresh
workflow. A native rewrite would have to re-implement fourteen metric
formatters in JavaScript, and would drift the first time the Python side
changed. This shell inherits the calculations exactly, and keeps inheriting
them: when the refresh workflow runs, the phone shows the new numbers with no
mobile work at all.

It also inherits the whole experience. The page is already mobile-first — a
390px design with a tab bar, safe-area insets and a light/dark palette — so the
core screens, the search, the sector cross-section, the detail sheets and the
watchlist all arrive intact. The watchlist keeps working because it lives in
`localStorage`, which the WebView persists.

### What the native layer adds

Only the things a browser tab cannot do:

| | |
|---|---|
| First-load state | Painted in the right theme, so there is no white flash into a dark page. |
| Offline and HTTP failures | A real error state with a retry, instead of a dead white frame. |
| Android hardware back | Walks the page's own history first, and only then leaves the app. |
| Safe areas | Owned by the shell, so the page never sits under a notch or a home indicator. |
| Outbound links | Open in the system browser rather than trapping you in a frame with no address bar. |
| Pull to refresh | On iOS, where the WebView supports it natively. |

### Expo Go safety

Everything imported ships **inside** Expo Go — all three native modules are in
Expo SDK 57's `bundledNativeModules.json`:

| Module | SDK 57 version |
|---|---|
| `react-native-webview` | 13.16.1 |
| `react-native-safe-area-context` | ~5.7.0 |
| `expo-status-bar` | ~57.0.1 |

No custom native code, no config plugins, no development build.

## Compromises

These are real, and worth weighing before anyone builds on this.

1. **It is a WebView shell, not a native rewrite.** That is the deliberate
   trade: one source of truth for every calculation, in exchange for a mobile
   app that feels like a very good website rather than a native one. There is
   no native list virtualisation, no native navigation transitions, and no
   platform-native controls. If the goal later becomes a genuinely native feel,
   the honest path is to publish the computed payload as JSON and build native
   screens against it — a much larger piece of work, and a second thing to keep
   in step with the Python.

2. **It needs a connection.** The page and its data come from GitHub Pages on
   every launch, with only the WebView's own HTTP cache in between. There is no
   offline snapshot. Your starred names survive offline; the numbers do not.

3. **The page is ~800 KB.** That is the committed `web/index.html` with its data
   inlined. Fine on wifi, noticeable on a poor connection, and it is fetched
   again whenever the cache expires.

4. **I could not run it on a device.** I have no phone and no Expo account, so
   what follows is what was actually checked, and what was not.

   Verified: `App.js` parses under Babel with the React preset; every import
   resolves to a module bundled in Expo Go; `raw.githubusercontent.com` serves
   the branch with `access-control-allow-origin: *` so Snack can fetch it; the
   GitHub Pages URL the app loads returns 200; the generated Snack URL returns
   200.

   Not verified: the Expo Go handoff itself, on-device rendering, and the
   gesture behaviour. Those need a phone.

5. **The Expo SDK version is deliberately not pinned.** Snack then uses the
   newest released SDK, which is what a freshly installed Expo Go speaks. If
   your Expo Go is older, add `&sdkVersion=57.0.0` to the link, or set it in
   `snack-link.py`.

6. **No app icon or splash image.** Those are binary assets; Expo's defaults are
   used instead. Adding them is a small, separate change.

## Pointing it somewhere else

`APP_URL` at the top of `App.js` is the only thing that decides what the app
shows. It currently points at the published page:

```js
const APP_URL = 'https://vandyckmed-droid.github.io/Oklahoma/web/';
```

Swap it for a branch preview, a local `python3 -m http.server` on your LAN, or
one of the prototypes under `prototypes/ui-exploration/` — the shell does not
care which.

## Running it from a desktop instead

Not required, and not exercised here, but the project is a standard Expo app:

```
cd mobile
npm install
npx expo start          # scan the QR with Expo Go on the same network
```

## What this does not touch

Nothing outside this folder. `web/`, `oklahoma/`, `data/` and `worker/` are
unchanged, the generated-UI CI check still passes, and the web app is
completely unaffected — it does not know this exists.
