# Oklahoma on a phone — Expo Go client

An Expo app that runs in stock **Expo Go**, with no development build. It is
published by a GitHub Actions workflow, so nothing needs a computer: the
one-time setup is two pastes in a phone browser, explained below.

## Opening it — read this first

**The Snack link does not work with a current Expo Go, and cannot be made to.**
This was my mistake, and the cause is worth stating precisely.

Snack pins its own SDK ceiling, independent of the Expo SDK released on npm.
From `snack-content` 3.6.2, published 2026-04-01:

```js
defaultSdkVersion = '54.0.0'
newestSdkVersion  = '54.0.0'
```

Expo Go from the app stores runs **only the newest SDK** — 57 at the time of
writing. So a Snack is capped three SDKs below what Expo Go will load, and
opening one raises *"Selected Snack uses unsupported SDK (54)"*. No query
parameter fixes it: `sdkVersion=57.0.0` is not a version Snack can build. And
because Expo Go ships a single SDK, there is no older Expo Go to install on
iOS either.

`snack-link.py` is kept — the mechanism is sound and free to carry, so the
moment Snack ships SDK 57 the zero-setup path returns — but it now prints a
warning saying the link will fail.

### How to open it — no computer needed

Expo Go can load any project published with **EAS Update**, as long as the
account signed in to Expo Go owns the project. The workflow at
`.github/workflows/mobile-update.yml` does the publishing, on GitHub's
machines. One-time setup, all from a phone browser:

1. **Make a token.** `https://expo.dev/settings/access-tokens` → *Create token*.
   Copy it.
2. **Give it to GitHub.**
   `https://github.com/vandyckmed-droid/Oklahoma/settings/secrets/actions` →
   *New repository secret* → name `EXPO_TOKEN`, paste, save.
3. **Run the workflow.** GitHub → *Actions* → *Publish mobile app to Expo Go* →
   *Run workflow*. It takes about two minutes.

Then, on the phone signed in to that same Expo account, open **Expo Go →
Projects → Oklahoma**. The run's summary also prints a tappable
`exp://u.expo.dev/…` link and the dashboard page with a QR.

After that, every push to `mobile/` republishes automatically.

How it stays compatible: `app.config.js` sets `runtimeVersion` to the
`sdkVersion` policy, which resolves to `exposdk:57.0.0` — exactly what Expo Go
for SDK 57 accepts. (Leaving the field out does *not* do this: EAS then falls
back to the app version, `1.0.0`, which Expo Go rejects; the first real publish
proved it.) `eas update:configure` would write an `appVersion` policy and break
it the same way, so it is not run; `app.config.js` also adds the project id and
`updates.url` from the environment.

### Other routes

- **A development server**, if you have a computer on the same wifi:
  `cd mobile && npm install && npx expo start`, then scan with Expo Go.
  `--tunnel` works too; `@expo/ngrok` is a devDependency.
- **Or skip Expo entirely.** Because this app is a WebView shell, adding
  `https://vandyckmed-droid.github.io/Oklahoma/web/` to the home screen
  (Safari → Share → Add to Home Screen) gets substantially the same thing,
  permanently, with no tooling at all.

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

4. **The publish workflow has not run yet.** It needs `EXPO_TOKEN`, which only
   the account owner can create. Everything short of that is verified: the
   app bundles with Metro against SDK 57 / React Native 0.86 (598 modules,
   1.5 MB of Hermes bytecode, clean exit); `app.config.js` produces the
   right config with and without a project id; the workflow parses; and every
   `eas` flag it uses exists in eas-cli 23.2.0. The first real run is the
   remaining test, and its summary will say plainly if anything fails.

5. **The SDK is pinned to 57** in `package.json`, matching current Expo Go.
   When Expo ships SDK 58, Expo Go will follow and this needs bumping —
   `npx expo install --check` reports what to change.

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

## What this does not touch

Nothing outside this folder. `web/`, `oklahoma/`, `data/` and `worker/` are
unchanged, the generated-UI CI check still passes, and the web app is
completely unaffected — it does not know this exists.
