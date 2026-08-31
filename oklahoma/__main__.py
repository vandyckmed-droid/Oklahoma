"""Command line entry point: python -m oklahoma <command>."""

from __future__ import annotations

import argparse
import csv
import os
import sys

from .config import (
    HISTORY_DIR,
    HISTORY_INDEX_PATH,
    SPARKLINE_POINTS,
    UNIVERSE_PATH,
    HistoryConfig,
    UniverseConfig,
)
from .fmp import FMPError
from . import history as history_mod, metrics, ui, universe as universe_mod


def _millions(value: int) -> str:
    for unit, scale in (("T", 1e12), ("B", 1e9), ("M", 1e6)):
        if value >= scale:
            return f"{value / scale:,.1f}{unit}"
    return f"{value:,}"


def cmd_refresh(args: argparse.Namespace) -> int:
    config = UniverseConfig.from_env()
    if args.size:
        config.size = args.size
    if args.keep_all_share_classes:
        config.dedupe_share_classes = False

    data = universe_mod.build(config)
    universe_mod.save(data, args.output)
    print(f"Wrote {data['count']} names to {args.output}")
    if not args.no_ui:
        print(f"Wrote UI to {ui.build(data, _history_index())}")
    return 0


def _history_index() -> dict | None:
    """The saved history index, or None if history has not been pulled yet."""
    try:
        return history_mod.load_index()
    except FileNotFoundError:
        return None


def cmd_build_ui(args: argparse.Namespace) -> int:
    print(f"Wrote UI to {ui.build(universe_mod.load(args.output), _history_index())}")
    return 0


def cmd_history(args: argparse.Namespace) -> int:
    universe = universe_mod.load(args.output)
    tickers = [record["ticker"] for record in universe["constituents"]]

    config = HistoryConfig.from_env()
    if args.trading_days:
        config.trading_days = args.trading_days

    index = history_mod.build(
        tickers, config, sparkline_points=SPARKLINE_POINTS
    )
    history_mod.save_index(index)
    print(
        f"Wrote {index['count']} histories to {HISTORY_DIR} "
        f"({index['sufficient_count']} with >= {config.trading_days} trading days)"
    )
    print(f"Wrote index to {HISTORY_INDEX_PATH}")

    short = [e for e in index["coverage"] if not e["sufficient"]]
    for entry in short:
        print(
            f"  short history: {entry['ticker']} has {entry['trading_days']} "
            f"trading days from {entry['start_date']}"
        )
    for failure in index["failures"]:
        print(f"  failed: {failure['ticker']}: {failure['error']}", file=sys.stderr)

    if not args.no_ui:
        print(f"Wrote UI to {ui.build(universe, index)}")
    return 0


def cmd_export_returns(args: argparse.Namespace) -> int:
    universe = universe_mod.load(args.output)
    tickers = [record["ticker"] for record in universe["constituents"]]
    writer = csv.writer(sys.stdout)
    writer.writerow(["ticker", "date", "cum_return_pct"])
    for ticker in tickers:
        bars = history_mod.load_series(ticker)["bars"]
        for point in metrics.cumulative_returns(bars):
            writer.writerow([ticker, point["date"], point["cum_return_pct"]])
    return 0


def cmd_export_csv(args: argparse.Namespace) -> int:
    universe = universe_mod.load(args.output)
    tickers = [record["ticker"] for record in universe["constituents"]]
    writer = csv.writer(sys.stdout)
    writer.writerow(["ticker", "date", "adj_close"])
    writer.writerows(history_mod.iter_rows(tickers))
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    data = universe_mod.load(args.output)
    print(f"{data['count']} names as of {data['generated_at']}\n")
    for record in data["constituents"]:
        print(
            f"{record['rank']:>3}  {record['ticker']:<6} "
            f"{record['name'][:34]:<36} {record['sector'][:22]:<24} "
            f"{_millions(record['market_cap']):>8}"
        )
    print()
    for sector, count in universe_mod.sector_breakdown(data):
        print(f"{count:>3}  {sector}")

    index = _history_index()
    if index is None:
        print("\nNo price history yet. Run: python -m oklahoma history")
        return 0

    target = index["criteria"]["trading_days_target"]
    print(
        f"\nPrice history: {index['sufficient_count']}/{index['count']} names "
        f"have >= {target} trading days (as of {index['generated_at']})"
    )
    for entry in index["coverage"]:
        if not entry["sufficient"]:
            print(
                f"  {entry['ticker']}: {entry['trading_days']} days "
                f"from {entry['start_date']}"
            )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="oklahoma", description=__doc__)
    parser.add_argument(
        "--output", default=UNIVERSE_PATH, help="path to the universe JSON file"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    refresh = subparsers.add_parser(
        "refresh", help="pull the universe from FMP and rewrite the data file"
    )
    refresh.add_argument(
        "--size", type=int, help="how many names to keep (default 50)"
    )
    refresh.add_argument(
        "--keep-all-share-classes",
        action="store_true",
        help="give each share class its own slot instead of one row per company",
    )
    refresh.add_argument(
        "--no-ui", action="store_true", help="skip regenerating web/index.html"
    )
    refresh.set_defaults(func=cmd_refresh)

    subparsers.add_parser(
        "build-ui", help="regenerate web/index.html from the saved universe"
    ).set_defaults(func=cmd_build_ui)

    subparsers.add_parser(
        "show", help="print the saved universe to the terminal"
    ).set_defaults(func=cmd_show)

    hist = subparsers.add_parser(
        "history", help="pull end-of-day adjusted price history for every name"
    )
    hist.add_argument(
        "--trading-days",
        type=int,
        help="trading days each name should cover (default 252)",
    )
    hist.add_argument(
        "--no-ui", action="store_true", help="skip regenerating web/index.html"
    )
    hist.set_defaults(func=cmd_history)

    subparsers.add_parser(
        "export-csv",
        help="write the whole history as ticker,date,adj_close rows on stdout",
    ).set_defaults(func=cmd_export_csv)

    subparsers.add_parser(
        "export-returns",
        help="write 12-month daily cumulative returns as "
        "ticker,date,cum_return_pct rows on stdout",
    ).set_defaults(func=cmd_export_returns)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FMPError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except BrokenPipeError:
        # The reader (e.g. `head`) closed the pipe; that is not an error.
        # Point stdout at devnull so the interpreter's shutdown flush
        # doesn't raise a second time.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
