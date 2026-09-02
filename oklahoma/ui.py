"""Render the universe and its history into web/index.html.

`web/template.html` is a complete HTML document with two JSON placeholders;
rendering is a straight substitution. The page inlines per-name coverage
and thinned series, not the full history — enough to inspect what loaded
without shipping every bar.
"""

from __future__ import annotations

import json
import os
from math import exp

from .config import (
    SPARKLINE_POINTS,
    TRADING_DAYS_HALF,
    TRADING_DAYS_MONTH,
    TRADING_DAYS_QUARTER,
    UI_OUTPUT_PATH,
    UI_TEMPLATE_PATH,
)
from .history import load_series, thin, thin_indices
from .universe import load_changes
from .metrics import cumulative_returns, log_trend, rank_by_return, sector_summary

UNIVERSE_PLACEHOLDER = "__UNIVERSE_JSON__"
HISTORY_PLACEHOLDER = "__HISTORY_JSON__"


def _display(universe: dict, history_index: dict) -> dict:
    """The page's history payload, computed from the bar files.

    The index on disk is a coverage manifest; everything derivable — the
    window return, range, and the thinned cumulative-return series — is
    recomputed here from the bars, so the page can never disagree with the
    data it claims to show.
    """
    target = history_index["criteria"]["trading_days_target"]
    payload = {k: v for k, v in history_index.items() if k != "coverage"}
    payload["recent_changes"] = load_changes()["events"][-5:]
    sectors = {
        record["ticker"]: record["sector"] for record in universe["constituents"]
    }
    # A coverage name absent from the universe means the index and the
    # universe were built from different runs. Minting a fallback sector
    # would render a plausible row full of unreachable names; failing the
    # build (it runs in CI) makes the drift visible and the fix obvious.
    missing = {row["ticker"] for row in history_index["coverage"]} - sectors.keys()
    if missing:
        raise ValueError(
            f"coverage names absent from the universe: {sorted(missing)}; "
            "re-run `python -m oklahoma refresh` and `history` together"
        )
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
            # The short lens only exists where a full quarter of bars does;
            # measuring it over less would not be a 3-month number.
            if len(bars) >= TRADING_DAYS_HALF:
                half = cumulative_returns(bars, TRADING_DAYS_HALF)
                row["return_6m_pct"] = round(half[-1]["cum_return_pct"], 2)
            if len(bars) >= TRADING_DAYS_QUARTER:
                quarter = cumulative_returns(bars, TRADING_DAYS_QUARTER)
                row["return_3m_pct"] = round(quarter[-1]["cum_return_pct"], 2)
            if len(bars) >= TRADING_DAYS_MONTH:
                month = cumulative_returns(bars, TRADING_DAYS_MONTH)
                row["return_1m_pct"] = round(month[-1]["cum_return_pct"], 2)
            trend = log_trend(bars, target)
            if trend is not None:
                row["trend_ann_pct"] = trend["trend_ann_pct"]
                row["trend_r2"] = trend["r2"]
                row["quality_pct"] = trend["quality_pct"]
                # The fitted line, mapped into the chart's cumulative-return
                # space at the same thinned indices as the price series, so
                # the two curves align point for point. Straight in
                # log-price space, gently curved here — that is the honest
                # geometry of an exponential trend on a linear axis.
                window = bars[-len(series):]
                base = window[0]["adj_close"]
                row["fit_spark"] = [
                    round((exp(trend["intercept"] + trend["slope_daily"] * i)
                           / base - 1) * 100, 2)
                    for i in thin_indices(len(series), SPARKLINE_POINTS)
                ]
        payload["coverage"].append(row)

    # Cross-section over names with a full window: mixing a 55-day return
    # into 252-day sector medians would quietly corrupt the comparison.
    full_window = [
        {
            "ticker": row["ticker"],
            "sector": sectors[row["ticker"]],
            "return_pct": row["window_return_pct"],
        }
        for row in payload["coverage"]
        if row["sufficient"] and row.get("window_return_pct") is not None
    ]
    if full_window:
        payload["cross_section"] = dict(
            rank_by_return(full_window),
            sectors=sector_summary(full_window),
            names_used=len(full_window),
        )
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
    display = _display(universe, history_index) if history_index else None
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
