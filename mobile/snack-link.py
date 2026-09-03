#!/usr/bin/env python3
"""Build the Expo Snack URL that opens this app in Expo Go.

Snack can load a Snack's files from any publicly readable URL
(the documented `files` query parameter, with `{"type": "CODE", "url": ...}`),
so the link below points at App.js on raw.githubusercontent.com. That has two
useful consequences:

  * The link works against an unmerged branch, so the app is testable while
    the pull request is still open.
  * Snack re-fetches on every open, so the link never goes stale — pushing to
    the branch updates what Expo Go runs, with nothing to republish.

No Expo account and no desktop are involved: opening the URL on a phone hands
straight off to Expo Go.

    python3 mobile/snack-link.py                  # current branch
    python3 mobile/snack-link.py --ref main       # after the PR merges
"""

from __future__ import annotations

import argparse
import json
import subprocess
from urllib.parse import urlencode

REPO = "vandyckmed-droid/Oklahoma"
RAW = "https://raw.githubusercontent.com/{repo}/{ref}/{path}"

# Every one of these ships inside Expo Go (they are in Expo SDK 57's
# bundledNativeModules.json), so the Snack runs without a development build.
DEPENDENCIES = [
    "react-native-webview",
    "react-native-safe-area-context",
    "expo-status-bar",
]


def current_ref() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True
        ).strip()
    except Exception:
        return "main"


def build(ref: str) -> str:
    files = {
        "App.js": {
            "type": "CODE",
            "url": RAW.format(repo=REPO, ref=ref, path="mobile/App.js"),
        }
    }
    query = {
        "name": "Oklahoma",
        "description": "The S&P 500 universe, as computed by the Oklahoma pipeline.",
        # "mydevice" opens on the Expo Go tab rather than the web preview.
        "platform": "mydevice",
        "dependencies": ",".join(DEPENDENCIES),
        "files": json.dumps(files, separators=(",", ":")),
        # Deliberately no sdkVersion: Snack then uses the newest released SDK,
        # which is what a freshly installed Expo Go from the store speaks.
    }
    return "https://snack.expo.dev/?" + urlencode(query)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default=None, help="branch, tag or commit (default: current branch)")
    args = parser.parse_args()
    print(build(args.ref or current_ref()))
