"""The trapsort command."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from .card import CardError, import_card, read_season, write_sorting
from .empty import DEFAULT_THRESHOLD, mark_empty


def _import(args: argparse.Namespace) -> int:
    season = import_card(args.card, args.season)
    pictures = season.pictures
    print(
        f"Trap {season.trap_id}: {len(season.survey_days)} survey days, "
        f"{len(season.passes)} passes, {len(pictures)} pictures, "
        f"{len(season.faults)} faults, {len(season.summaries)} daily summaries"
    )
    per_day = Counter(record.survey_day for record in season.passes)
    for day in season.survey_days:
        views = len(season.empty_views.get(day, []))
        print(f"  {day}  {per_day[day]:5d} passes  {views} empty-view pictures")
    for fault in season.faults:
        print(f"  fault {fault['time_utc']:%Y-%m-%d %H:%M}Z {fault['fault']} {fault['detail']}")
    print(f"Copied into {Path(args.season) / 'card'}")
    return 0


def _sort(args: argparse.Namespace) -> int:
    season = read_season(args.season)
    mark_empty(season, args.threshold)
    write_sorting(season, args.season)
    pictures = season.pictures
    empty = sum(1 for p in pictures if p.empty)
    unjudged = sum(1 for p in pictures if p.empty is None)
    print(
        f"{len(pictures)} pictures: {empty} marked empty, "
        f"{len(pictures) - empty - unjudged} left for a person, "
        f"{unjudged} without an empty view of their day (also left for a person)"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="trapsort", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    importing = commands.add_parser(
        "import", help="check a trap's card and copy it into a new season folder"
    )
    importing.add_argument("card", type=Path, help="the card, or a folder holding a copy of it")
    importing.add_argument("season", type=Path, help="the season folder to copy it into")
    importing.set_defaults(run=_import)

    sorting = commands.add_parser(
        "sort", help="mark the pictures that look like their survey day's empty view"
    )
    sorting.add_argument("season", type=Path, help="the season folder")
    sorting.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help="largest difference from the empty view in any part of a picture still marked "
        f"empty, from 0 to 1 (default {DEFAULT_THRESHOLD})",
    )
    sorting.set_defaults(run=_sort)

    args = parser.parse_args(argv)
    try:
        return args.run(args)
    except CardError as error:
        print(f"trapsort: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
