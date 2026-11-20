"""The types the sorting tool works with."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .groups import Group

# The values the trap writes into its pass files and fault log.
DIRECTIONS = ("AtoB", "BtoA", "backA", "backB", "unknown")
HEIGHTS = ("lowest", "middle", "top")
NOTICED_BY = ("lasers", "pir", "both")
FAULT_KINDS = ("beam_blocked", "beam_clear", "battery_low", "storage_low", "camera_failed")


@dataclass
class Picture:
    """One stored picture: file, pass_id, survey day, empty mark, group and confidence."""

    file: Path
    pass_id: str | None  # None for the daily picture of the empty view
    survey_day: str
    empty: bool | None = None  # None until it has been judged
    group: Group | None = None
    confidence: float | None = None
    judged_empty_on_trap: bool = False  # marked by the trap's filter in pilot mode

    @property
    def name(self) -> str:
        return self.file.name


@dataclass
class PassRecord:
    """One row of a pass file, with its pictures."""

    pass_id: str
    survey_day: str
    start_utc: datetime
    end_utc: datetime
    direction: str
    heights_a: tuple[str, ...]
    heights_b: tuple[str, ...]
    noticed_by: str
    pictures: list[Picture]
    dropped_empty: int
    judged_empty: tuple[str, ...]


@dataclass
class Season:
    """Everything read from one card copy: passes, pictures, empty views, faults, summaries."""

    card: Path
    trap_id: str
    config: dict[str, str]
    passes: list[PassRecord]
    empty_views: dict[str, list[Picture]]  # by survey day, in time order
    faults: list[dict[str, Any]]  # time_utc (datetime), fault and detail
    summaries: list[dict[str, Any]]  # the daily FieldMesh readings as written

    @property
    def pictures(self) -> list[Picture]:
        """The pictures of all passes, in pass order."""
        return [picture for record in self.passes for picture in record.pictures]

    @property
    def survey_days(self) -> list[str]:
        days = {record.survey_day for record in self.passes} | set(self.empty_views)
        return sorted(days)


@dataclass
class LabelledPicture:
    """A picture with a group from a person's name or a bucket label."""

    file: Path
    group: Group
    name: str | None = None


class GroupModel:
    """A trained group model: predict(picture) gives a group and a confidence."""

    def predict(self, picture: Picture) -> tuple[Group, float]:
        raise NotImplementedError


@dataclass
class DayCount:
    """Passes in one survey day for one name or group and one direction."""

    survey_day: str
    name: str
    direction: str
    passes: int
