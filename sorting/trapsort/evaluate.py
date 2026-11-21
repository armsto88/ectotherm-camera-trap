"""Evaluating a season against what is known to have passed: a bench run's plan, or the animals
found in a bucket behind the trap during the field phase.

bucket_checks.csv holds checked_at,trap_id,animal,name,group: one row per animal found in the
bucket at a check, with the time of the check in ISO 8601 with its time zone, the trap, the
animal's number at that check, its name as identified in the hand, and its group. A row with
animal, name and group left empty records a check that found nothing.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .labels import LabelStore
from .model import GROUPS, Group, PassRecord, Season

BUCKET_COLUMNS = ["checked_at", "trap_id", "animal", "name", "group"]

# Passes that went through the trap match a bucket animal before turned-back ones, and passes
# the PIR sensor alone noticed, whose direction is unknown, last.
_THROUGH = ("AtoB", "BtoA")
_TURNED_BACK = ("backA", "backB")


class PlanError(Exception):
    """A plan or bucket checks file is malformed."""


@dataclass
class BucketAnimal:
    """One row of bucket_checks.csv; animal, name and group are empty for a check that found
    nothing."""

    checked_at: datetime
    trap_id: str
    animal: str
    name: str
    group: Group | None


@dataclass
class BucketChecks:
    """Rows of bucket_checks.csv: the animals found in the bucket at each check."""

    rows: list[BucketAnimal]


@dataclass
class BucketMatch:
    """One animal found in the bucket, with the pass it matches, or None when none does."""

    checked_at: datetime
    animal: str
    name: str
    group: Group
    pass_id: str | None


def read_bucket_checks(path: Path) -> BucketChecks:
    """Reads bucket_checks.csv; raises PlanError on a malformed row."""
    path = Path(path)
    with path.open(newline="") as f:
        rows = list(csv.reader(f))
    if not rows or [c.strip() for c in rows[0]] != BUCKET_COLUMNS:
        raise PlanError(f"{path}:1: expected the header {','.join(BUCKET_COLUMNS)}")
    animals = []
    for number, row in enumerate(rows[1:], start=2):
        if not any(cell.strip() for cell in row):
            continue
        where = f"{path}:{number}"
        if len(row) != len(BUCKET_COLUMNS):
            raise PlanError(f"{where}: expected {len(BUCKET_COLUMNS)} fields, found {len(row)}")
        checked_at, trap_id, animal, name, group = (cell.strip() for cell in row)
        try:
            when = datetime.fromisoformat(checked_at)
        except ValueError:
            raise PlanError(f"{where}: checked_at is not a time: {checked_at!r}") from None
        if when.tzinfo is None:
            raise PlanError(f"{where}: checked_at needs its time zone, such as Z or +02:00")
        if not trap_id:
            raise PlanError(f"{where}: trap_id is missing")
        if animal or name or group:
            if not animal:
                raise PlanError(f"{where}: an animal found needs its number at the check")
            if group not in GROUPS:
                raise PlanError(f"{where}: group {group!r} is not one of {', '.join(GROUPS)}")
        animals.append(BucketAnimal(when, trap_id, animal, name, group or None))  # type: ignore[arg-type]
    return BucketChecks(animals)


def match_bucket_checks(
    season: Season, labels: LabelStore, checks: BucketChecks
) -> list[BucketMatch]:
    """Matches each animal of the season's trap to the earliest unmatched pass since the
    previous check whose pictures people gave its group; passes that went through come before
    turned-back ones. trapsort bucket stores the matches as bucket labels; evaluate counts the
    animals without a match as missed."""
    rows = sorted(
        (r for r in checks.rows if r.trap_id == season.trap_id), key=lambda r: r.checked_at
    )
    check_times = sorted({r.checked_at for r in rows})
    matched: set[str] = set()
    matches = []
    for row in rows:
        if row.group is None:
            continue  # a check that found nothing
        earlier = [t for t in check_times if t < row.checked_at]
        since = earlier[-1] if earlier else None
        candidates = [
            record
            for record in season.passes
            if record.pass_id not in matched
            and (since is None or record.start_utc > since)
            and record.start_utc <= row.checked_at
            and _shows(record, row.group, labels)
        ]
        best = min(candidates, key=_match_order, default=None)
        if best is not None:
            matched.add(best.pass_id)
        matches.append(
            BucketMatch(
                row.checked_at, row.animal, row.name, row.group, best.pass_id if best else None
            )
        )
    return matches


def _shows(record: PassRecord, group: Group, labels: LabelStore) -> bool:
    return any(labels.group(picture.name) == group for picture in record.pictures)


def _match_order(record: PassRecord) -> tuple[int, datetime]:
    if record.direction in _THROUGH:
        rank = 0
    elif record.direction in _TURNED_BACK:
        rank = 1
    else:
        rank = 2
    return rank, record.start_utc
