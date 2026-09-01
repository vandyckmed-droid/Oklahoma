"""Minimal Financial Modeling Prep client (standard library only)."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://financialmodelingprep.com/stable"

# The key is read from the environment; it is never written to disk or into
# any generated file.
API_KEY_ENV_VARS = ("FMP_API_KEY", "API_KEY")


class FMPError(RuntimeError):
    pass


def get_api_key() -> str:
    for name in API_KEY_ENV_VARS:
        value = os.environ.get(name)
        if value:
            return value
    raise FMPError(
        "No FMP API key found. Set FMP_API_KEY (or API_KEY) in the environment."
    )


def _request(path: str, params: dict, api_key: str, retries: int = 3) -> list | dict:
    query = dict(params)
    query["apikey"] = api_key
    url = f"{BASE_URL}/{path}?{urllib.parse.urlencode(query)}"

    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < retries - 1:
                time.sleep(2**attempt)
    # Redact the key before the URL can reach a log or a traceback.
    safe_url = url.replace(api_key, "***")
    raise FMPError(f"Request failed: {safe_url}: {last_error}")


def sp500_constituents(api_key: str) -> list[dict]:
    """Current S&P 500 membership: symbol, name, sector, sub-sector, CIK."""
    rows = _request("sp500-constituent", {}, api_key)
    if not isinstance(rows, list) or not rows:
        raise FMPError(f"Unexpected constituent response: {rows!r}")
    return rows


def batch_quotes(symbols: list[str], api_key: str, chunk: int = 100) -> dict[str, dict]:
    """Latest quote (price, market cap, exchange) for many symbols at once."""
    quotes: dict[str, dict] = {}
    for start in range(0, len(symbols), chunk):
        rows = _request(
            "batch-quote",
            {"symbols": ",".join(symbols[start : start + chunk])},
            api_key,
        )
        if not isinstance(rows, list):
            raise FMPError(f"Unexpected batch-quote response: {rows!r}")
        for row in rows:
            quotes[row["symbol"]] = row
    return quotes


def historical_prices(
    symbol: str, start: str, end: str, api_key: str
) -> list[dict]:
    """Adjusted end-of-day bars for one symbol, oldest first.

    Uses the dividend-adjusted endpoint: its `adjClose` is corrected for
    both splits and dividends, which is what makes returns comparable
    across time. The plain `full` endpoint has no adjusted column at all.
    """
    rows = _request(
        "historical-price-eod/dividend-adjusted",
        {"symbol": symbol, "from": start, "to": end},
        api_key,
    )
    if not isinstance(rows, list):
        raise FMPError(f"Unexpected history response for {symbol}: {rows!r}")
    # The API returns newest first; every consumer wants chronological order.
    return sorted(rows, key=lambda row: row["date"])
