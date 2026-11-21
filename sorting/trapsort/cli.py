"""The trapsort command."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from .camtrapdp import ExportError, export_camtrap_dp
from .card import CardError, import_card, read_season, write_sorting
from .empty import DEFAULT_THRESHOLD, mark_empty
from .evaluate import (
    PlanError,
    Report,
    evaluate,
    match_bucket_checks,
    read_bucket_checks,
    read_plan,
)
from .labels import LabelError, LabelStore
from .review import serve_review
from .summary import passes_per_survey_day


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


def _review(args: argparse.Namespace) -> int:
    season = read_season(args.season)
    serve_review(season, LabelStore(args.season / "labels.csv"), args.port)
    return 0


def _bucket(args: argparse.Namespace) -> int:
    season = read_season(args.season)
    labels = LabelStore(args.season / "labels.csv")
    matches = match_bucket_checks(season, labels, read_bucket_checks(args.checks))
    stored = 0
    for match in matches:
        if match.pass_id is None:
            continue
        label = (match.name, match.group, match.checked_at)
        if label not in labels.bucket_labels(match.pass_id):
            labels.add_bucket_label(match.pass_id, match.name, match.group, match.checked_at)
            stored += 1
    matched = sum(1 for m in matches if m.pass_id)
    print(
        f"{len(matches)} animals from the bucket for trap {season.trap_id}: {matched} matched to "
        f"a pass ({stored} new labels), {len(matches) - matched} without a matching pass"
    )
    for match in matches:
        if match.pass_id is None:
            print(
                f"  no pass: {match.checked_at:%Y-%m-%d %H:%M} animal {match.animal} {match.name}"
            )
    return 0


def _summarise(args: argparse.Namespace) -> int:
    season = read_season(args.season)
    counts = passes_per_survey_day(season, LabelStore(args.season / "labels.csv"))
    print(f"Passes per survey day at trap {season.trap_id}; passes, not animals: one animal can")
    print("pass several times.")
    print("survey_day,group_or_species,direction,passes")
    for count in counts:
        print(f"{count.survey_day},{count.name},{count.direction},{count.passes}")
    return 0


def _export(args: argparse.Namespace) -> int:
    season = read_season(args.season)
    labels = LabelStore(args.season / "labels.csv")
    export_camtrap_dp(season, labels, project=args.project, contact=args.contact)
    print(
        f"Exported trap {season.trap_id} as a Camera Trap Data Package: "
        f"{args.season / 'datapackage.json'} and its three tables"
    )
    return 0


def _percent(share: float | None) -> str:
    return "-" if share is None else f"{share:.0%}"


def print_report(report: Report) -> None:
    n = report.animals
    print(f"Against the {report.reference}: {n} animals passed")
    for label, count in (
        ("noticed", report.noticed),
        ("with a usable picture", report.usable),
        ("identified", report.identified),
    ):
        print(f"  {label:22} {count:4d} of {n} animals  {_percent(report.share(count))}")
    print(f"  missed: {len(report.missed)} animals")
    for what in report.missed:
        print(f"    {what}")
    print(
        f"Passes noticed by the lasers only: {report.by_lasers_only}, by the PIR sensor only: "
        f"{report.by_pir_only}, by both: {report.by_both}"
    )
    agreement = report.agreement
    print(
        f"Model agreement: {agreement.agreed} of {agreement.n} passes "
        f"{_percent(agreement.share)}, from passes sorted in pilot mode"
    )
    for model_type, by_type in report.agreement_by_type.items():
        print(f"  {model_type:14} {by_type.agreed:4d} of {by_type.n}  {_percent(by_type.share)}")
    if report.left_out_of_agreement:
        print(f"  left out: {report.left_out_of_agreement} passes {report.left_out_reason}")
    if not report.fully_sorted:
        print(
            f"Not fully sorted: {report.unsorted_pictures} pictures nobody has looked at yet; "
            "the shares can still change."
        )


def _evaluate(args: argparse.Namespace) -> int:
    season = read_season(args.season)
    labels = LabelStore(args.season / "labels.csv")
    if args.plan:
        reference = read_plan(args.plan)
    else:
        reference = read_bucket_checks(args.bucket_checks)
    print_report(evaluate(season, labels, reference))
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

    reviewing = commands.add_parser(
        "review", help="serve the page on which people sort the passes and name the species"
    )
    reviewing.add_argument("season", type=Path, help="the season folder")
    reviewing.add_argument("--port", type=int, default=8765, help="port on this computer")
    reviewing.set_defaults(run=_review)

    bucket = commands.add_parser(
        "bucket", help="store the identifications of animals found in the bucket as labels"
    )
    bucket.add_argument("season", type=Path, help="the season folder")
    bucket.add_argument("checks", type=Path, help="bucket_checks.csv of the field phase")
    bucket.set_defaults(run=_bucket)

    summarising = commands.add_parser(
        "summarise", help="passes per survey day by group or species and direction"
    )
    summarising.add_argument("season", type=Path, help="the season folder")
    summarising.set_defaults(run=_summarise)

    exporting = commands.add_parser(
        "export", help="export a season as a Camera Trap Data Package, into its season folder"
    )
    exporting.add_argument("season", type=Path, help="the season folder")
    exporting.add_argument("--project", required=True, help="the title of the survey project")
    exporting.add_argument("--contact", required=True, help="the person to ask about the data")
    exporting.set_defaults(run=_export)

    evaluating = commands.add_parser(
        "evaluate", help="report the three outcomes and the model agreement of a test run"
    )
    evaluating.add_argument("season", type=Path, help="the season folder of the run")
    reference = evaluating.add_mutually_exclusive_group(required=True)
    reference.add_argument("--plan", type=Path, help="plan.csv of a bench run")
    reference.add_argument(
        "--bucket-checks", type=Path, help="bucket_checks.csv of the field phase"
    )
    evaluating.set_defaults(run=_evaluate)

    args = parser.parse_args(argv)
    try:
        return args.run(args)
    except (CardError, LabelError, PlanError, ExportError) as error:
        print(f"trapsort: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
