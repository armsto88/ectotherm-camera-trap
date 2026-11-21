"""Evaluating a season against what is known to have passed: a bench run's plan, or the animals
found in a bucket behind the trap during the field phase.

plan.csv holds planned_at,model,body_length_mm,height_mm,speed_mm_s,temperature_c,light,direction:
one row per planned passage of the rig, with its time in ISO 8601 with its time zone and the
model animal or known animal that passed, by the name a person sorting should give it.

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
from typing import cast

from .labels import LabelStore
from .model import GROUPS, MODEL_TYPES, Group, ModelType, PassRecord, Season, model_type_of

BUCKET_COLUMNS = ["checked_at", "trap_id", "animal", "name", "group"]
PLAN_COLUMNS = [
    "planned_at", "model", "body_length_mm", "height_mm", "speed_mm_s", "temperature_c", "light",
    "direction",
]  # fmt: skip
LIGHTS = ("dark", "daylight")
PLAN_DIRECTIONS = ("AtoB", "BtoA")

# A planned passage matches the pass that started closest to it within this many seconds.
PLAN_WINDOW_S = 2.0

SUGGESTION_SHOWN = (
    "sorted with the model's type shown as a suggestion, so people's groups may follow the model"
)

# Passes that went through the trap match a bucket animal before turned-back ones, and passes
# the PIR sensor alone noticed, whose direction is unknown, last.
_THROUGH = ("AtoB", "BtoA")
_TURNED_BACK = ("backA", "backB")


class PlanError(Exception):
    """A plan or bucket checks file is malformed."""


@dataclass
class PlannedPassage:
    """One row of plan.csv."""

    planned_at: datetime
    model: str
    body_length_mm: int
    height_mm: int
    speed_mm_s: float
    temperature_c: float
    light: str
    direction: str


@dataclass
class BenchPlan:
    """Rows of a bench run's plan.csv: what passed when, at which size, speed and light."""

    rows: list[PlannedPassage]


@dataclass
class Agreement:
    """Passes whose model type matched the type people's group counts as, out of n."""

    agreed: int = 0
    n: int = 0

    @property
    def share(self) -> float | None:
        return self.agreed / self.n if self.n else None


@dataclass
class Report:
    """Shares noticed, with a usable picture and identified; missed animals; passes by sensing;
    model agreement in total and per model type, from passes sorted in pilot mode only.
    A pass has a usable picture when a person gave any of its pictures a group or a name, and is
    identified when that name matches the animal the reference names."""

    reference: str  # "bench plan" or "bucket checks"
    animals: int
    noticed: int
    usable: int
    identified: int
    missed: list[str]
    by_lasers_only: int
    by_pir_only: int
    by_both: int
    unsorted_pictures: int
    agreement: Agreement
    agreement_by_type: dict[ModelType, Agreement]
    left_out_of_agreement: int  # passes with a model type sorted with the suggestion shown
    left_out_reason: str

    def share(self, count: int) -> float | None:
        return count / self.animals if self.animals else None

    @property
    def fully_sorted(self) -> bool:
        return self.unsorted_pictures == 0


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


def read_plan(path: Path) -> BenchPlan:
    """Reads plan.csv; raises PlanError on a malformed row."""
    path = Path(path)
    with path.open(newline="") as f:
        rows = list(csv.reader(f))
    if not rows or [c.strip() for c in rows[0]] != PLAN_COLUMNS:
        raise PlanError(f"{path}:1: expected the header {','.join(PLAN_COLUMNS)}")
    passages = []
    for number, row in enumerate(rows[1:], start=2):
        if not any(cell.strip() for cell in row):
            continue
        where = f"{path}:{number}"
        if len(row) != len(PLAN_COLUMNS):
            raise PlanError(f"{where}: expected {len(PLAN_COLUMNS)} fields, found {len(row)}")
        values = dict(zip(PLAN_COLUMNS, (cell.strip() for cell in row)))
        when = _aware_time(values["planned_at"], "planned_at", where)
        if not values["model"]:
            raise PlanError(f"{where}: model is missing")
        if values["light"] not in LIGHTS:
            raise PlanError(f"{where}: light is {values['light']!r}, not dark or daylight")
        if values["direction"] not in PLAN_DIRECTIONS:
            raise PlanError(f"{where}: direction is {values['direction']!r}, not AtoB or BtoA")
        try:
            passage = PlannedPassage(
                planned_at=when,
                model=values["model"],
                body_length_mm=int(values["body_length_mm"]),
                height_mm=int(values["height_mm"]),
                speed_mm_s=float(values["speed_mm_s"]),
                temperature_c=float(values["temperature_c"]),
                light=values["light"],
                direction=values["direction"],
            )
        except ValueError:
            raise PlanError(f"{where}: sizes, speed and temperature are numbers") from None
        passages.append(passage)
    return BenchPlan(passages)


def _aware_time(text: str, column: str, where: str) -> datetime:
    try:
        when = datetime.fromisoformat(text)
    except ValueError:
        raise PlanError(f"{where}: {column} is not a time: {text!r}") from None
    if when.tzinfo is None:
        raise PlanError(f"{where}: {column} needs its time zone, such as Z or +02:00")
    return when


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
        when = _aware_time(checked_at, "checked_at", where)
        if not trap_id:
            raise PlanError(f"{where}: trap_id is missing")
        if animal or name or group:
            if not animal:
                raise PlanError(f"{where}: an animal found needs its number at the check")
            if group not in GROUPS:
                raise PlanError(f"{where}: group {group!r} is not one of {', '.join(GROUPS)}")
        animals.append(
            BucketAnimal(when, trap_id, animal, name, cast("Group | None", group or None))
        )
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


def evaluate(season: Season, labels: LabelStore, reference: BenchPlan | BucketChecks) -> Report:
    """The three outcomes as shares of the animals the reference says passed, the missed
    animals, and the passes noticed by the lasers only, the PIR sensor only and both.

    With a bench plan, each planned passage matches the pass that started closest to it within
    PLAN_WINDOW_S. With bucket checks, an animal matches a pass as trapsort bucket matches it,
    which needs a usable picture of its group, so an animal counts as noticed only with one."""
    animals: list[tuple[str, str, PassRecord | None]] = []  # what passed, its name, its pass
    by_id = {record.pass_id: record for record in season.passes}
    if isinstance(reference, BenchPlan):
        kind = "bench plan"
        taken: set[str] = set()
        for row in sorted(reference.rows, key=lambda r: r.planned_at):
            record = _closest_pass(season, row.planned_at, taken)
            if record is not None:
                taken.add(record.pass_id)
            what = f"{row.planned_at:%Y-%m-%d %H:%M:%S} {row.model} {row.direction}"
            animals.append((what, row.model, record))
    else:
        kind = "bucket checks"
        for match in match_bucket_checks(season, labels, reference):
            what = f"{match.checked_at:%Y-%m-%d %H:%M} animal {match.animal} {match.name}".strip()
            record = by_id[match.pass_id] if match.pass_id else None
            animals.append((what, match.name or match.group, record))

    noticed = sum(1 for _, _, record in animals if record is not None)
    usable = sum(1 for _, _, record in animals if record and _usable(record, labels))
    identified = sum(
        1 for _, name, record in animals if record and _identified(record, name, labels)
    )
    missed = [what for what, _, record in animals if not (record and _usable(record, labels))]

    agreement = Agreement()
    by_type: dict[ModelType, Agreement] = {t: Agreement() for t in MODEL_TYPES if t != "empty"}
    left_out = 0
    for record in season.passes:
        types = _people_types(record, labels)
        if not types or record.model_type is None:
            continue
        if not record.pilot:
            left_out += 1
            continue
        agreed = record.model_type in types
        agreement.n += 1
        agreement.agreed += agreed
        for t in types:
            by_type[t].n += 1
            by_type[t].agreed += record.model_type == t

    return Report(
        reference=kind,
        animals=len(animals),
        noticed=noticed,
        usable=usable,
        identified=identified,
        missed=missed,
        by_lasers_only=sum(1 for r in season.passes if r.noticed_by == "lasers"),
        by_pir_only=sum(1 for r in season.passes if r.noticed_by == "pir"),
        by_both=sum(1 for r in season.passes if r.noticed_by == "both"),
        unsorted_pictures=_unsorted_pictures(season, labels),
        agreement=agreement,
        agreement_by_type=by_type,
        left_out_of_agreement=left_out,
        left_out_reason=SUGGESTION_SHOWN if left_out else "",
    )


def _closest_pass(season: Season, when: datetime, taken: set[str]) -> PassRecord | None:
    candidates = [
        r
        for r in season.passes
        if r.pass_id not in taken and abs((r.start_utc - when).total_seconds()) <= PLAN_WINDOW_S
    ]
    return min(candidates, key=lambda r: abs((r.start_utc - when).total_seconds()), default=None)


def _usable(record: PassRecord, labels: LabelStore) -> bool:
    return any(labels.group(p.name) or labels.name(p.name) for p in record.pictures)


def _identified(record: PassRecord, name: str, labels: LabelStore) -> bool:
    wanted = name.strip().casefold()
    return bool(wanted) and any(
        (labels.name(p.name) or "").strip().casefold() == wanted for p in record.pictures
    )


def _people_types(record: PassRecord, labels: LabelStore) -> set[ModelType]:
    """The model types people's groups for the pass's pictures count as."""
    return {
        model_type_of(group)
        for picture in record.pictures
        if (group := labels.group(picture.name)) is not None
    }


def _unsorted_pictures(season: Season, labels: LabelStore) -> int:
    """Pictures not marked empty that nobody has given a group, a name or "can't tell"."""
    count = 0
    for picture in season.pictures:
        person_empty = labels.empty(picture.name)
        if person_empty if person_empty is not None else picture.empty:
            continue
        name = picture.name
        if not (labels.group(name) or labels.name(name) or labels.unclear(name)):
            count += 1
    return count
