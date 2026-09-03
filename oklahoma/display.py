"""The page's history payload, written to data/display.json.

web/index.html fetches data/universe.json and this file at load, so the
page itself is static and never has to be regenerated. The payload carries
per-name coverage and thinned series, not the full history — enough to
draw the page without shipping every bar.
"""

from __future__ import annotations

import json
import os
from math import exp

from .config import (
    DISPLAY_PATH,
    SPARKLINE_POINTS,
    TRADING_DAYS_HALF,
    TRADING_DAYS_MONTH,
    TRADING_DAYS_QUARTER,
)
from .history import load_series, thin, thin_indices
from .universe import load_changes
from .metrics import (
    cumulative_returns,
    log_trend,
    rank_by_return,
    sector_summary,
    skip_month_return,
)

def payload(universe: dict, history_index: dict) -> dict:
    """The page's history payload, computed from the bar files.

    The index on disk is a coverage manifest; everything derivable — the
    window return, range, and the thinned cumulative-return series — is
    recomputed here from the bars, so the page can never disagree with the
    data it claims to show.
    """
    target = history_index["criteria"]["trading_days_target"]
    out = {k: v for k, v in history_index.items() if k != "coverage"}
    out["recent_changes"] = load_changes()["events"][-5:]
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
    out["coverage"] = []
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
            # Each shorter lens exists only where its full window of bars
            # does; measuring 6, 3 or 1 months over less would not be
            # that number, so the field is absent instead.
            if len(bars) >= TRADING_DAYS_HALF:
                half = cumulative_returns(bars, TRADING_DAYS_HALF)
                row["return_6m_pct"] = round(half[-1]["cum_return_pct"], 2)
            if len(bars) >= TRADING_DAYS_QUARTER:
                quarter = cumulative_returns(bars, TRADING_DAYS_QUARTER)
                row["return_3m_pct"] = round(quarter[-1]["cum_return_pct"], 2)
            if len(bars) >= TRADING_DAYS_MONTH:
                month = cumulative_returns(bars, TRADING_DAYS_MONTH)
                row["return_1m_pct"] = round(month[-1]["cum_return_pct"], 2)
            # Momentum with the freshest month skipped (12-1, 6-1):
            # only where the full window exists, like the plain windows.
            mom = skip_month_return(bars, target, TRADING_DAYS_MONTH)
            if mom is not None:
                row["mom_12_1_pct"] = mom
            mom = skip_month_return(bars, TRADING_DAYS_HALF, TRADING_DAYS_MONTH)
            if mom is not None:
                row["mom_6_1_pct"] = mom
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
        out["coverage"].append(row)

    # Cross-section over names with a full window: mixing a 55-day return
    # into 252-day sector medians would quietly corrupt the comparison.
    full_window = [
        {
            "ticker": row["ticker"],
            "sector": sectors[row["ticker"]],
            "return_pct": row["window_return_pct"],
        }
        for row in out["coverage"]
        if row["sufficient"] and row.get("window_return_pct") is not None
    ]
    if full_window:
        out["cross_section"] = dict(
            rank_by_return(full_window),
            sectors=sector_summary(full_window),
            names_used=len(full_window),
        )
    return out


def build(
    universe: dict,
    history_index: dict | None = None,
    path: str = DISPLAY_PATH,
) -> str | None:
    """Write the payload to `path`; returns None (writing nothing) when
    there is no history yet, which the page reads as "market cap only"."""
    if history_index is None:
        return None
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        # Compact: the file is fetched on every page load, and two decimals
        # per point already bound the sparklines.
        json.dump(payload(universe, history_index), handle, separators=(",", ":"))
        handle.write("\n")
    return path
