"""People's labels and bucket labels in a season's labels.csv.

The file is only ever appended to: picture,pass_id,kind,value,by,at, where kind is name, group,
empty (value true or false), unclear (a picture marked "can't tell"), bucket (the name an animal
caught in the bucket was given in the hand) or bucket_group (its group). Bucket rows name the pass
and leave picture empty. For each picture the latest label of each kind counts; a group and a
"can't tell" mark replace each other.
"""

from __future__ import annotations

import csv
from datetime import UTC, datetime
from pathlib import Path

from .model import GROUPS, Group

COLUMNS = ["picture", "pass_id", "kind", "value", "by", "at"]
KINDS = ("name", "group", "empty", "unclear", "bucket", "bucket_group")


class LabelError(Exception):
    """labels.csv is malformed, or a label is not one the store takes."""


def pass_id_of(picture: str) -> str:
    """The pass a picture belongs to, from its file name <pass_id>_<n>.jpg."""
    stem = picture.rsplit(".", 1)[0]
    pass_id, sep, number = stem.rpartition("_")
    if not sep or not number.isdigit():
        raise LabelError(f"{picture} is not the picture of a pass")
    return pass_id


class LabelStore:
    """Names, groups, empty and can't-tell marks and bucket labels in a season's labels.csv;
    the latest label of each kind counts."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._rows: list[dict[str, str]] = []
        if self.path.exists():
            self._read()

    # --- Setting labels ----------------------------------------------------------------------

    def set_name(self, picture: str, name: str, by: str) -> None:
        self._add(picture, "name", name.strip(), by)

    def set_group(self, picture: str, group: Group, by: str) -> None:
        if group not in GROUPS:
            raise LabelError(f"{group!r} is not a group")
        self._add(picture, "group", group, by)

    def set_empty(self, picture: str, empty: bool, by: str) -> None:
        self._add(picture, "empty", "true" if empty else "false", by)

    def set_unclear(self, picture: str, by: str) -> None:
        self._add(picture, "unclear", "true", by)

    def add_bucket_label(self, pass_id: str, name: str, group: Group, checked_at: datetime) -> None:
        if group not in GROUPS:
            raise LabelError(f"{group!r} is not a group")
        at = _time_text(checked_at)
        self._append(
            [
                {
                    "picture": "",
                    "pass_id": pass_id,
                    "kind": "bucket",
                    "value": name,
                    "by": "bucket",
                    "at": at,
                },
                {
                    "picture": "",
                    "pass_id": pass_id,
                    "kind": "bucket_group",
                    "value": group,
                    "by": "bucket",
                    "at": at,
                },
            ]
        )

    # --- Reading labels ----------------------------------------------------------------------

    def name(self, picture: str) -> str | None:
        row = self._latest(picture, "name")
        return row["value"] or None if row else None

    def group(self, picture: str) -> Group | None:
        row = self._latest(picture, "group", "unclear")
        return row["value"] if row and row["kind"] == "group" else None  # type: ignore[return-value]

    def empty(self, picture: str) -> bool | None:
        row = self._latest(picture, "empty")
        return row["value"] == "true" if row else None

    def unclear(self, picture: str) -> bool:
        row = self._latest(picture, "group", "unclear")
        return bool(row) and row["kind"] == "unclear"

    def bucket_labels(self, pass_id: str) -> list[tuple[str, Group, datetime]]:
        labels = []
        rows = [r for r in self._rows if r["pass_id"] == pass_id and not r["picture"]]
        for name_row, group_row in zip(rows[::2], rows[1::2]):
            labels.append(
                (name_row["value"], group_row["value"], _parse_time(group_row["at"], self.path))
            )
        return labels  # type: ignore[return-value]

    # --- The file ----------------------------------------------------------------------------

    def _latest(self, picture: str, *kinds: str) -> dict[str, str] | None:
        for row in reversed(self._rows):
            if row["picture"] == picture and row["kind"] in kinds:
                return row
        return None

    def _add(self, picture: str, kind: str, value: str, by: str) -> None:
        if not by.strip():
            raise LabelError("a label needs the name of who gave it")
        row = {
            "picture": picture,
            "pass_id": pass_id_of(picture),
            "kind": kind,
            "value": value,
            "by": by.strip(),
            "at": _time_text(datetime.now(UTC)),
        }
        self._append([row])

    def _append(self, rows: list[dict[str, str]]) -> None:
        new_file = not self.path.exists()
        with self.path.open("a", newline="") as f:
            writer = csv.DictWriter(f, COLUMNS, lineterminator="\n")
            if new_file:
                writer.writeheader()
            writer.writerows(rows)
        self._rows.extend(rows)

    def _read(self) -> None:
        with self.path.open(newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header != COLUMNS:
                raise LabelError(f"{self.path}:1: expected the header {','.join(COLUMNS)}")
            for number, row in enumerate(reader, start=2):
                if not row:
                    continue
                where = f"{self.path}:{number}"
                if len(row) != len(COLUMNS):
                    raise LabelError(f"{where}: expected {len(COLUMNS)} fields, found {len(row)}")
                values = dict(zip(COLUMNS, row))
                if values["kind"] not in KINDS:
                    raise LabelError(f"{where}: unknown kind {values['kind']!r}")
                _parse_time(values["at"], where)
                self._rows.append(values)


def _time_text(t: datetime) -> str:
    return t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_time(text: str, where: object) -> datetime:
    try:
        return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError:
        raise LabelError(f"{where}: not a UTC time: {text!r}") from None
