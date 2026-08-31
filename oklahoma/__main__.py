"""Command line entry point: python -m oklahoma <command>."""

from __future__ import annotations

import argparse
import sys

from .config import UNIVERSE_PATH, UniverseConfig
from .fmp import FMPError
from . import ui, universe as universe_mod


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
        print(f"Wrote UI to {ui.build(data)}")
    return 0


def cmd_build_ui(args: argparse.Namespace) -> int:
    print(f"Wrote UI to {ui.build(universe_mod.load(args.output))}")
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

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FMPError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
