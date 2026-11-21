"""Reading a copy of the trap's memory card.

The card holds:

    trap.cfg                   key=value lines
    passes/YYYY-MM-DD.csv      one pass file per survey day (noon to noon, local)
    pictures/YYYY-MM-DD/       <pass_id>_<n>.jpg, and empty_<HHMM>.jpg for the daily picture
    faults.csv                 time_utc,fault,detail
    state/summaries.jsonl      one FieldMesh reading per line, one line per day

A season on the computer is a folder:

    card/                      the card copy, as import_card copied it; never changed
    sorting.csv                the computer's empty marks, written again by each sort
"""

from __future__ import annotations

import csv
import json
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path

from .model import DIRECTIONS, FAULT_KINDS, HEIGHTS, NOTICED_BY, PassRecord, Picture, Season

PASS_COLUMNS = [
    "pass_id",
    "start_utc",
    "end_utc",
    "direction",
    "heights_a",
    "heights_b",
    "noticed_by",
    "pictures",
    "dropped_empty",
    "judged_empty",
]
FAULT_COLUMNS = ["time_utc", "fault", "detail"]
SORTING_COLUMNS = ["picture", "pass_id", "survey_day", "empty", "difference"]
DEFAULT_TRAP_ID = "ECT_UNSET"

_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_EMPTY_VIEW = re.compile(r"^empty_\d{4}\.jpg$")


class CardError(Exception):
    """The card copy is incomplete or holds a malformed file."""


def read_card(card: Path) -> Season:
    """Reads pass records, pictures, faults and summaries from a card copy; raises CardError."""
    card = Path(card)
    if not card.is_dir():
        raise CardError(f"{card}: not a folder")
    config = _read_config(card / "trap.cfg")
    passes: list[PassRecord] = []
    passes_dir = card / "passes"
    if passes_dir.is_dir():
        for path in sorted(passes_dir.glob("*.csv")):
            passes.extend(_read_pass_file(card, path))
    return Season(
        card=card,
        trap_id=config.get("trap_id", DEFAULT_TRAP_ID),
        config=config,
        passes=passes,
        empty_views=_read_empty_views(card),
        faults=_read_faults(card / "faults.csv"),
        summaries=_read_summaries(card / "state" / "summaries.jsonl"),
    )


def import_card(card: Path, season_dir: Path) -> Season:
    """Checks a card with read_card and copies it into season_dir/card; raises CardError, also
    when the season already holds a card."""
    read_card(card)
    season_dir = Path(season_dir)
    target = season_dir / "card"
    if target.exists():
        raise CardError(f"{season_dir}: the season already holds a card; use a new season folder")
    season_dir.mkdir(parents=True, exist_ok=True)
    # Copied under another name first, so that a copy broken off never looks like a card.
    partial = season_dir / "card.partial"
    if partial.exists():
        shutil.rmtree(partial)
    shutil.copytree(card, partial)
    partial.rename(target)
    return read_card(target)


def read_season(season_dir: Path) -> Season:
    """Reads season_dir/card and, where present, the empty marks in sorting.csv."""
    season_dir = Path(season_dir)
    if not (season_dir / "card").is_dir():
        raise CardError(f"{season_dir}: not a season folder; it holds no card/")
    season = read_card(season_dir / "card")
    path = season_dir / "sorting.csv"
    if path.exists():
        _read_sorting(path, season)
    return season


def write_sorting(season: Season, season_dir: Path) -> None:
    """Writes each picture's empty mark and difference to season_dir/sorting.csv."""
    path = Path(season_dir) / "sorting.csv"
    partial = path.with_suffix(".partial")
    with partial.open("w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(SORTING_COLUMNS)
        for picture in season.pictures:
            writer.writerow(
                [
                    picture.name,
                    picture.pass_id,
                    picture.survey_day,
                    "" if picture.empty is None else str(picture.empty).lower(),
                    "" if picture.difference is None else f"{picture.difference:.4f}",
                ]
            )
    partial.replace(path)


def _read_sorting(path: Path, season: Season) -> None:
    by_name = {picture.name: picture for picture in season.pictures}
    with path.open(newline="") as f:
        rows = list(csv.reader(f))
    if not rows or rows[0] != SORTING_COLUMNS:
        raise CardError(f"{path}:1: expected the header {','.join(SORTING_COLUMNS)}")
    for number, row in enumerate(rows[1:], start=2):
        if not row:
            continue
        where = f"{path}:{number}"
        if len(row) != len(SORTING_COLUMNS):
            raise CardError(f"{where}: expected {len(SORTING_COLUMNS)} fields, found {len(row)}")
        values = dict(zip(SORTING_COLUMNS, row))
        picture = by_name.get(values["picture"])
        if picture is None:
            raise CardError(f"{where}: picture {values['picture']} is not on the card")
        if values["empty"] not in ("true", "false", ""):
            raise CardError(f"{where}: empty is not true or false")
        picture.empty = None if values["empty"] == "" else values["empty"] == "true"
        try:
            picture.difference = float(values["difference"]) if values["difference"] else None
        except ValueError:
            raise CardError(f"{where}: difference is not a number") from None


def _read_config(path: Path) -> dict[str, str]:
    config: dict[str, str] = {}
    if not path.exists():
        return config
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if not sep:
            raise CardError(f"{path}:{number}: expected key=value")
        config[key.strip()] = value.strip()
    return config


def _utc(text: str, where: str) -> datetime:
    try:
        return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError:
        raise CardError(f"{where}: not a UTC time: {text!r}") from None


def _names(text: str) -> tuple[str, ...]:
    return tuple(name for name in text.split(";") if name)


def _read_pass_file(card: Path, path: Path) -> list[PassRecord]:
    day = path.stem
    if not _DAY.match(day):
        raise CardError(f"{path}: pass files are named after their survey day, YYYY-MM-DD.csv")
    with path.open(newline="") as f:
        rows = list(csv.reader(f))
    if not rows or rows[0] != PASS_COLUMNS:
        raise CardError(f"{path}:1: expected the header {','.join(PASS_COLUMNS)}")

    records = []
    for number, row in enumerate(rows[1:], start=2):
        where = f"{path}:{number}"
        if not row:
            continue
        if len(row) != len(PASS_COLUMNS):
            raise CardError(f"{where}: expected {len(PASS_COLUMNS)} fields, found {len(row)}")
        values = dict(zip(PASS_COLUMNS, row))
        if values["direction"] not in DIRECTIONS:
            raise CardError(f"{where}: unknown direction {values['direction']!r}")
        if values["noticed_by"] not in NOTICED_BY:
            raise CardError(f"{where}: unknown noticed_by {values['noticed_by']!r}")
        heights_a, heights_b = _names(values["heights_a"]), _names(values["heights_b"])
        for height in heights_a + heights_b:
            if height not in HEIGHTS:
                raise CardError(f"{where}: unknown beam height {height!r}")
        try:
            dropped = int(values["dropped_empty"])
        except ValueError:
            raise CardError(f"{where}: dropped_empty is not a number") from None

        judged_empty = _names(values["judged_empty"])
        pictures = []
        for name in _names(values["pictures"]):
            file = card / "pictures" / day / name
            if not file.is_file():
                raise CardError(f"{where}: picture {name} is missing from {file.parent}")
            pictures.append(
                Picture(
                    file=file,
                    pass_id=values["pass_id"],
                    survey_day=day,
                    judged_empty_on_trap=name in judged_empty,
                )
            )
        records.append(
            PassRecord(
                pass_id=values["pass_id"],
                survey_day=day,
                start_utc=_utc(values["start_utc"], where),
                end_utc=_utc(values["end_utc"], where),
                direction=values["direction"],
                heights_a=heights_a,
                heights_b=heights_b,
                noticed_by=values["noticed_by"],
                pictures=pictures,
                dropped_empty=dropped,
                judged_empty=judged_empty,
            )
        )
    return records


def _read_empty_views(card: Path) -> dict[str, list[Picture]]:
    views: dict[str, list[Picture]] = {}
    pictures_dir = card / "pictures"
    if not pictures_dir.is_dir():
        return views
    for day_dir in sorted(p for p in pictures_dir.iterdir() if p.is_dir()):
        files = sorted(f for f in day_dir.iterdir() if _EMPTY_VIEW.match(f.name))
        if files:
            views[day_dir.name] = [
                Picture(file=f, pass_id=None, survey_day=day_dir.name, empty=True) for f in files
            ]
    return views


def _read_faults(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        rows = list(csv.reader(f))
    if not rows or rows[0] != FAULT_COLUMNS:
        raise CardError(f"{path}:1: expected the header {','.join(FAULT_COLUMNS)}")
    faults = []
    for number, row in enumerate(rows[1:], start=2):
        if not row:
            continue
        where = f"{path}:{number}"
        if len(row) != 3:
            raise CardError(f"{where}: expected 3 fields, found {len(row)}")
        if row[1] not in FAULT_KINDS:
            raise CardError(f"{where}: unknown fault {row[1]!r}")
        faults.append({"time_utc": _utc(row[0], where), "fault": row[1], "detail": row[2]})
    return faults


def _read_summaries(path: Path) -> list[dict]:
    if not path.exists():
        return []
    summaries = []
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            summary = json.loads(line)
        except json.JSONDecodeError:
            raise CardError(f"{path}:{number}: not a JSON reading") from None
        if not isinstance(summary, dict):
            raise CardError(f"{path}:{number}: not a JSON reading")
        summaries.append(summary)
    return summaries
