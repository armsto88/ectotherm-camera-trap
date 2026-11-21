"""The types the sorting tool works with."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

# The broad groups people sort passes into.
Group = Literal["frog", "toad", "newt", "lizard", "snake", "turtle", "other"]
GROUPS: tuple[Group, ...] = ("frog", "toad", "newt", "lizard", "snake", "turtle", "other")

# The types the model on the trap gives a pass.
ModelType = Literal["empty", "frog_or_toad", "lizard", "snake", "other"]
MODEL_TYPES: tuple[ModelType, ...] = ("empty", "frog_or_toad", "lizard", "snake", "other")


def model_type_of(group: Group) -> ModelType:
    """The model type a person's group counts as: frog and toad as frog_or_toad; newt, turtle
    and other as other."""
    if group in ("frog", "toad"):
        return "frog_or_toad"
    if group in ("lizard", "snake"):
        return group
    return "other"


# The values the trap writes into its pass files and fault log.
DIRECTIONS = ("AtoB", "BtoA", "backA", "backB", "unknown")
HEIGHTS = ("lowest", "middle", "top")
NOTICED_BY = ("lasers", "pir", "both")
FAULT_KINDS = (
    "beam_blocked",
    "beam_clear",
    "battery_low",
    "storage_low",
    "camera_failed",
    "link_failed",
    "update_failed",
)
PLACEMENTS = ("line", "end")


@dataclass
class Picture:
    """One stored picture: file, pass_id, survey day and empty mark."""

    file: Path
    pass_id: str | None  # None for the daily picture of the empty view
    survey_day: str
    empty: bool | None = None  # the computer's empty mark; None until it has been judged
    difference: float | None = None  # from its survey day's empty view, when judged
    judged_empty_on_trap: bool = False  # marked by the trap's filter in pilot mode

    @property
    def name(self) -> str:
        return self.file.name


@dataclass
class PassRecord:
    """One row of a pass file, with its pictures, whether it was recorded in pilot mode, and
    the model type, confidence and model version, None when the trap had no model."""

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
    pilot: bool = False
    model_type: ModelType | None = None
    model_confidence: float | None = None
    model_version: str | None = None


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
    def placement(self) -> str:
        """Where the trap sat: "line" in the fence line, "end" at a fence end."""
        return self.config.get("placement", "line")

    @property
    def side_a(self) -> str:
        """Side A in words, as the trap's settings describe it; "" when not given."""
        return self.config.get("side_a", "")

    @property
    def coordinates(self) -> tuple[float, float] | None:
        """Latitude and longitude from the trap's settings, or None when either is not set."""
        if "latitude" not in self.config or "longitude" not in self.config:
            return None
        return float(self.config["latitude"]), float(self.config["longitude"])

    @property
    def survey_days(self) -> list[str]:
        days = {record.survey_day for record in self.passes} | set(self.empty_views)
        return sorted(days)


@dataclass
class DayCount:
    """Passes in one survey day for one name or group and one direction."""

    survey_day: str
    name: str
    direction: str
    passes: int
