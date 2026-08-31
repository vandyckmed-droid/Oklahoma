"""Build, save and load the stock universe."""

from __future__ import annotations

import datetime as dt
import json
import os

from .config import MARKET_CAP_FLOORS, SCHEMA_VERSION, UNIVERSE_PATH, UniverseConfig
from .fmp import FMPError, get_api_key, screen

UNKNOWN_SECTOR = "Unclassified"


def _normalize(row: dict) -> dict:
    """Map one screener row onto the fields the universe promises to carry."""
    return {
        "ticker": row["symbol"],
        "name": (row.get("companyName") or row["symbol"]).strip(),
        "sector": (row.get("sector") or "").strip() or UNKNOWN_SECTOR,
        "industry": (row.get("industry") or "").strip() or None,
        "exchange": row.get("exchangeShortName") or row.get("exchange"),
        "market_cap": int(row.get("marketCap") or 0),
        "price": row.get("price"),
        "avg_volume": row.get("avgVolume"),
        "share_classes": [row["symbol"]],
    }


def _company_key(record: dict) -> str:
    return record["name"].casefold()


def collapse_share_classes(records: list[dict]) -> list[dict]:
    """Keep one row per company: the most liquid share class.

    Berkshire's A and B shares are one company holding two universe slots.
    The class actually worth trading is the liquid one, so that is the row we
    keep; the others are listed under `share_classes`.
    """
    by_company: dict[str, dict] = {}
    for record in records:
        key = _company_key(record)
        incumbent = by_company.get(key)
        if incumbent is None:
            by_company[key] = record
            continue
        challenger_wins = (record["avg_volume"] or 0, record["market_cap"]) > (
            incumbent["avg_volume"] or 0,
            incumbent["market_cap"],
        )
        winner, loser = (
            (record, incumbent) if challenger_wins else (incumbent, record)
        )
        winner["share_classes"] = sorted(
            set(winner["share_classes"]) | set(loser["share_classes"])
        )
        by_company[key] = winner
    return list(by_company.values())


def fetch_candidates(config: UniverseConfig, api_key: str) -> list[dict]:
    """Pull enough of the market to cover `config.size` after filtering.

    Walks down the market-cap ladder until the pool is comfortably larger
    than the target, so asking for 500 names works the same as asking for 50.
    """
    target_pool = max(config.size * 2, config.size + 25)
    records: list[dict] = []

    for floor in MARKET_CAP_FLOORS:
        rows: list[dict] = []
        for exchange in config.exchanges:
            rows += screen(
                exchange=exchange,
                market_cap_more_than=floor,
                limit=max(config.size * 4, 200),
                api_key=api_key,
                country=config.country,
            )
        records = [
            _normalize(row)
            for row in rows
            # A dot in the symbol marks a foreign cross-listing of the same
            # company (NVDA.NE); we want the primary U.S. line only.
            if row.get("symbol") and "." not in row["symbol"]
        ]
        if config.dedupe_share_classes:
            records = collapse_share_classes(records)
        if len(records) >= target_pool:
            break

    if len(records) < config.size:
        raise FMPError(
            f"Only {len(records)} names matched; need {config.size}. "
            "Widen the exchange list or lower the market-cap floor."
        )
    return records


def rank(records: list[dict], size: int) -> list[dict]:
    ordered = sorted(records, key=lambda r: r["market_cap"], reverse=True)[:size]
    for position, record in enumerate(ordered, start=1):
        record["rank"] = position
    return ordered


def build(config: UniverseConfig | None = None, api_key: str | None = None) -> dict:
    config = config or UniverseConfig.from_env()
    api_key = api_key or get_api_key()
    constituents = rank(fetch_candidates(config, api_key), config.size)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "source": {
            "provider": "Financial Modeling Prep",
            "endpoint": "stable/company-screener",
        },
        "criteria": config.as_dict(),
        "count": len(constituents),
        "constituents": constituents,
    }


def save(universe: dict, path: str = UNIVERSE_PATH) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(universe, handle, indent=2)
        handle.write("\n")
    return path


def load(path: str = UNIVERSE_PATH) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def sector_breakdown(universe: dict) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for record in universe["constituents"]:
        counts[record["sector"]] = counts.get(record["sector"], 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
