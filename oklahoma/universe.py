"""Build, save and load the stock universe.

The universe is the current S&P 500 membership, enriched with live quotes
and ranked by market cap. Constituent rows carry the company's CIK — the
durable SEC identifier — so a ticker rename can never sever a company from
its own history.
"""

from __future__ import annotations

import datetime as dt
import json
import os

from .config import CHANGES_PATH, SCHEMA_VERSION, UNIVERSE_PATH, UniverseConfig
from .fmp import batch_quotes, get_api_key, sp500_constituents

UNKNOWN_SECTOR = "Unclassified"


def _normalize(constituent: dict, quote: dict) -> dict:
    """One constituent row plus its quote, mapped onto the universe fields."""
    return {
        "ticker": constituent["symbol"],
        "name": (constituent.get("name") or constituent["symbol"]).strip(),
        "sector": (constituent.get("sector") or "").strip() or UNKNOWN_SECTOR,
        "industry": (constituent.get("subSector") or "").strip() or None,
        "cik": constituent.get("cik"),
        "date_first_added": constituent.get("dateFirstAdded"),
        "exchange": quote.get("exchange"),
        "market_cap": int(quote.get("marketCap") or 0),
        "price": quote.get("price"),
        "volume": quote.get("volume"),
        "share_classes": [constituent["symbol"]],
    }


def _company_key(record: dict) -> str:
    return record["cik"] or record["name"].casefold()


def collapse_share_classes(records: list[dict]) -> list[dict]:
    """Optionally keep one row per company: the most traded share class.

    Companies are grouped by CIK, so Alphabet's two listings collapse even
    though their tickers share nothing.
    """
    by_company: dict[str, dict] = {}
    for record in records:
        key = _company_key(record)
        incumbent = by_company.get(key)
        if incumbent is None:
            by_company[key] = record
            continue
        challenger_wins = (record["volume"] or 0, record["market_cap"]) > (
            incumbent["volume"] or 0,
            incumbent["market_cap"],
        )
        winner, loser = (record, incumbent) if challenger_wins else (incumbent, record)
        winner["share_classes"] = sorted(
            set(winner["share_classes"]) | set(loser["share_classes"])
        )
        by_company[key] = winner
    return list(by_company.values())


def rank(records: list[dict], size: int | None = None) -> list[dict]:
    ordered = sorted(records, key=lambda r: r["market_cap"], reverse=True)
    if size is not None:
        ordered = ordered[:size]
    for position, record in enumerate(ordered, start=1):
        record["rank"] = position
    return ordered


def build(config: UniverseConfig | None = None, api_key: str | None = None) -> dict:
    config = config or UniverseConfig.from_env()
    api_key = api_key or get_api_key()

    constituents = sp500_constituents(api_key)
    quotes = batch_quotes([row["symbol"] for row in constituents], api_key)
    records = [
        _normalize(row, quotes.get(row["symbol"], {})) for row in constituents
    ]
    if config.collapse_share_classes:
        records = collapse_share_classes(records)

    ranked = rank(records, config.size)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "source": {
            "provider": "Financial Modeling Prep",
            "endpoint": "stable/sp500-constituent",
            "index": "S&P 500",
        },
        "criteria": config.as_dict(),
        "count": len(ranked),
        "constituents": ranked,
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


def diff_membership(old: dict, new: dict) -> dict:
    """What changed between two universes, keyed by CIK.

    Comparing by CIK rather than ticker means a symbol change shows up as a
    rename, not as one company leaving and a stranger arriving.
    """
    def by_cik(universe: dict) -> dict[str, dict]:
        return {
            record["cik"]: record
            for record in universe["constituents"]
            if record.get("cik")
        }

    old_members, new_members = by_cik(old), by_cik(new)

    def entry(record: dict) -> dict:
        return {"ticker": record["ticker"], "name": record["name"], "cik": record["cik"]}

    joined = [entry(new_members[cik]) for cik in sorted(new_members.keys() - old_members.keys())]
    left = [entry(old_members[cik]) for cik in sorted(old_members.keys() - new_members.keys())]
    renamed = [
        {
            "cik": cik,
            "name": new_members[cik]["name"],
            "from_ticker": old_members[cik]["ticker"],
            "to_ticker": new_members[cik]["ticker"],
        }
        for cik in sorted(old_members.keys() & new_members.keys())
        if old_members[cik]["ticker"] != new_members[cik]["ticker"]
    ]
    return {"joined": joined, "left": left, "renamed": renamed}


def load_changes(path: str = CHANGES_PATH) -> dict:
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return {"schema_version": 1, "events": []}


def record_changes(diff: dict, generated_at: str, path: str = CHANGES_PATH) -> bool:
    """Append one membership event; no-ops when nothing changed.

    The log is append-only: each entry is a committee decision (or a
    rename) observed at a refresh, which is exactly the record that cannot
    be reconstructed later from a current-state snapshot.
    """
    if not (diff["joined"] or diff["left"] or diff["renamed"]):
        return False
    log = load_changes(path)
    log["events"].append(dict({"observed_at": generated_at}, **diff))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(log, handle, indent=2)
        handle.write("\n")
    return True
