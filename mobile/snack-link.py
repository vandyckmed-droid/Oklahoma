#!/usr/bin/env python3
"""Build an Expo Snack URL for this app.

    WARNING — this will not open in a current Expo Go.

Snack pins its own SDK ceiling, independent of the Expo SDK on npm. As of
snack-content 3.6.2 (published 2026-04-01):

    defaultSdkVersion = '54.0.0'
    newestSdkVersion  = '54.0.0'

Expo Go from the app stores runs only the newest SDK — 57 at the time of
writing. A Snack is therefore capped three SDKs below what Expo Go will load,
and opening one raises "Selected Snack uses unsupported SDK (54)". No query
parameter fixes this: `sdkVersion=57.0.0` is not a version Snack can build.

The script is kept because the mechanism is sound and costs nothing to carry:
Snack loads files from any public URL, so the moment Snack ships SDK 57 this
link becomes the zero-setup path again. Until then, use a development server —
see mobile/README.md.

    python3 mobile/snack-link.py                  # current branch
    python3 mobile/snack-link.py --ref main       # after the PR merges
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from urllib.parse import urlencode

REPO = "vandyckmed-droid/Oklahoma"

# The ceiling Snack can build, from snack-content's own defaults.js. Raise this
# when Snack ships a newer SDK; check with:
#   npm view snack-content dist-tags.latest
SNACK_MAX_SDK = "54.0.0"

# What Expo Go from the app stores actually runs. Expo Go supports exactly one
# SDK — the newest — so a Snack is only openable while these two agree.
EXPO_GO_SDK = "57.0.0"
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
        # Snack ignores anything above its own newestSdkVersion, so this is
        # pinned to what Snack can actually build rather than to what Expo Go
        # wants. The two do not currently meet.
        "sdkVersion": SNACK_MAX_SDK,
    }
    return "https://snack.expo.dev/?" + urlencode(query)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default=None, help="branch, tag or commit (default: current branch)")
    args = parser.parse_args()
    print(build(args.ref or current_ref()))
    if SNACK_MAX_SDK != EXPO_GO_SDK:
        print(
            "\nWARNING: Snack builds SDK %s at most; Expo Go runs SDK %s only.\n"
            "This link will fail with \"unsupported SDK\". Use a development\n"
            "server instead — see mobile/README.md." % (SNACK_MAX_SDK, EXPO_GO_SDK),
            file=sys.stderr,
        )
