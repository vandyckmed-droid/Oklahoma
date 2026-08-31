"""Universe selection rules.

Everything that decides *which* names land in the universe lives here, so
growing past 50 is a matter of changing one number (or passing --size).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

# Where the universe file and the generated UI are written.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNIVERSE_PATH = os.path.join(ROOT, "data", "universe.json")
HISTORY_DIR = os.path.join(ROOT, "data", "history")
HISTORY_INDEX_PATH = os.path.join(HISTORY_DIR, "index.json")
UI_TEMPLATE_PATH = os.path.join(ROOT, "web", "template.html")
UI_OUTPUT_PATH = os.path.join(ROOT, "web", "index.html")

SCHEMA_VERSION = 1
HISTORY_SCHEMA_VERSION = 1

# The screener needs a market-cap floor to page against. A floor that works
# for a top-50 universe is far too high for a top-500 one, so we walk down
# this ladder until enough names come back.
MARKET_CAP_FLOORS = [
    100_000_000_000,
    50_000_000_000,
    15_000_000_000,
    5_000_000_000,
    1_000_000_000,
    200_000_000,
]


@dataclass
class UniverseConfig:
    """Selection rules for one universe build."""

    size: int = 50
    exchanges: list[str] = field(default_factory=lambda: ["NASDAQ", "NYSE", "AMEX"])
    country: str = "US"
    # Berkshire and Alphabet each list two share classes. Keeping both would
    # spend two universe slots on one company, so by default we keep only the
    # most liquid class and record the others alongside it.
    dedupe_share_classes: bool = True

    @classmethod
    def from_env(cls) -> "UniverseConfig":
        cfg = cls()
        if os.environ.get("UNIVERSE_SIZE"):
            cfg.size = int(os.environ["UNIVERSE_SIZE"])
        if os.environ.get("UNIVERSE_EXCHANGES"):
            cfg.exchanges = [
                x.strip().upper()
                for x in os.environ["UNIVERSE_EXCHANGES"].split(",")
                if x.strip()
            ]
        return cfg

    def as_dict(self) -> dict:
        return {
            "size": self.size,
            "exchanges": list(self.exchanges),
            "country": self.country,
            "dedupe_share_classes": self.dedupe_share_classes,
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
