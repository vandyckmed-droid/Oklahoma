"""Render the universe and its history into web/index.html.

`web/template.html` is a complete HTML document with two JSON placeholders;
rendering is a straight substitution. The page inlines per-name coverage
and thinned series, not the full history — enough to inspect what loaded
without shipping every bar.
"""

from __future__ import annotations

import json
import os

from .config import SPARKLINE_POINTS, UI_OUTPUT_PATH, UI_TEMPLATE_PATH
from .history import load_series, thin
from .universe import load_changes
from .metrics import cumulative_returns

UNIVERSE_PLACEHOLDER = "__UNIVERSE_JSON__"
HISTORY_PLACEHOLDER = "__HISTORY_JSON__"


def _display(history_index: dict) -> dict:
    """The page's history payload, computed from the bar files.

    The index on disk is a coverage manifest; everything derivable — the
    window return, range, and the thinned cumulative-return series — is
    recomputed here from the bars, so the page can never disagree with the
    data it claims to show.
    """
    target = history_index["criteria"]["trading_days_target"]
    payload = {k: v for k, v in history_index.items() if k != "coverage"}
    payload["recent_changes"] = load_changes()["events"][-5:]
    payload["coverage"] = []
    for entry in history_index["coverage"]:
        bars = load_series(entry["ticker"])["bars"]
        row = dict(entry)
        if bars:
            row["last_adj_close"] = bars[-1]["adj_close"]
        series = cumulative_returns(bars, target)
        if len(series) >= 2:
            values = [point["cum_return_pct"] for point in series]
            closes = bars[-len(series):]
            row["window_trading_days"] = len(series)
            row["window_start_date"] = series[0]["date"]
            row["window_return_pct"] = round(values[-1], 2)
            row["window_low"] = min(bar["adj_close"] for bar in closes)
            row["window_high"] = max(bar["adj_close"] for bar in closes)
            # Two decimals is below visual resolution for an 18px chart
            # and keeps half a megabyte of page from growing further.
            row["cum_return_spark"] = [
                round(value, 2) for value in thin(values, SPARKLINE_POINTS)
            ]
        payload["coverage"].append(row)
    return payload


def _inline(payload) -> str:
    # `</` inside an inline JSON block would close the script tag early.
    return json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")


def render(
    universe: dict,
    history_index: dict | None = None,
    template_path: str = UI_TEMPLATE_PATH,
) -> str:
    with open(template_path, encoding="utf-8") as handle:
        template = handle.read()
    for placeholder in (UNIVERSE_PLACEHOLDER, HISTORY_PLACEHOLDER):
        if placeholder not in template:
            raise ValueError(f"{template_path} is missing {placeholder}")
    display = _display(history_index) if history_index else None
    return template.replace(UNIVERSE_PLACEHOLDER, _inline(universe)).replace(
        HISTORY_PLACEHOLDER, _inline(display)
    )


def build(
    universe: dict,
    history_index: dict | None = None,
    output_path: str = UI_OUTPUT_PATH,
    template_path: str = UI_TEMPLATE_PATH,
) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(render(universe, history_index, template_path))
    return output_path
