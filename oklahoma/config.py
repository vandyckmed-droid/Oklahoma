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
UI_TEMPLATE_PATH = os.path.join(ROOT, "web", "template.html")
UI_OUTPUT_PATH = os.path.join(ROOT, "web", "index.html")

SCHEMA_VERSION = 1

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
