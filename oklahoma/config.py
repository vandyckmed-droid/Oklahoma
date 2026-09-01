"""Universe selection rules.

Everything that decides *which* names land in the universe lives here, so
growing past 50 is a matter of changing one number (or passing --size).
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# Where the universe file and the generated UI are written.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIVERSE_PATH = os.path.join(ROOT, "data", "universe.json")
HISTORY_DIR = os.path.join(ROOT, "data", "history")
HISTORY_INDEX_PATH = os.path.join(HISTORY_DIR, "index.json")
UI_TEMPLATE_PATH = os.path.join(ROOT, "web", "template.html")
UI_OUTPUT_PATH = os.path.join(ROOT, "web", "index.html")

SCHEMA_VERSION = 2
HISTORY_SCHEMA_VERSION = 2


@dataclass
class UniverseConfig:
    """Selection rules for one universe build.

    The universe is the S&P 500 as its committee defines it. Delegating
    membership to the index provider gives entry/exit hysteresis for free
    and removes any selection logic of our own; the daily refresh simply
    mirrors whatever the index currently holds.
    """

    source: str = "sp500"
    # Optional cap for experiments (UNIVERSE_SIZE=50 keeps the old shape);
    # None mirrors the full index.
    size: int | None = None
    # The index itself lists some companies twice (GOOG and GOOGL, FOX and
    # FOXA). Mirroring the index keeps both; collapsing to one row per
    # company (by CIK, keeping the most traded class) is opt-in.
    collapse_share_classes: bool = False

    @classmethod
    def from_env(cls) -> "UniverseConfig":
        cfg = cls()
        if os.environ.get("UNIVERSE_SIZE"):
            cfg.size = int(os.environ["UNIVERSE_SIZE"])
        return cfg

    def as_dict(self) -> dict:
        return {
            "source": self.source,
            "size": self.size,
            "collapse_share_classes": self.collapse_share_classes,
        }


# --- price history -----------------------------------------------------

# The window every downstream calculation is sized against. 252 is the
# conventional trading-day count for one year.
TRADING_DAYS_TARGET = 252

# How many points the UI carries per name. The full series lives in
# data/history/; the page only needs enough to show a shape.
SPARKLINE_POINTS = 60

# Concurrent history requests. Enough to make 50 names quick, low enough
# to stay polite to the API.
HISTORY_WORKERS = 6


def calendar_days_for(trading_days: int) -> int:
    """Calendar days to request to be confident of `trading_days` sessions.

    Markets trade roughly 252 of 365 days. The 1.5x factor plus a fixed
    buffer covers holiday clustering and long weekends at the edges.
    """
    return int(trading_days * 1.5) + 60


@dataclass
class HistoryConfig:
    """Selection rules for one history build."""

    trading_days: int = TRADING_DAYS_TARGET
    workers: int = HISTORY_WORKERS

    @classmethod
    def from_env(cls) -> "HistoryConfig":
        cfg = cls()
        if os.environ.get("HISTORY_TRADING_DAYS"):
            cfg.trading_days = int(os.environ["HISTORY_TRADING_DAYS"])
        return cfg

    @property
    def calendar_days(self) -> int:
        return calendar_days_for(self.trading_days)

    def as_dict(self) -> dict:
        return {
            "trading_days_target": self.trading_days,
            "calendar_days_requested": self.calendar_days,
        }
