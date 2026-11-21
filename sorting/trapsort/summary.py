"""Passes per survey day: an index of how common animals are, never a number of animals."""

from __future__ import annotations

from collections import Counter

from .labels import LabelStore
from .model import DayCount, PassRecord, Season

UNSORTED = "unsorted"  # a pass with a picture nobody has sorted yet
CANT_TELL = "can't tell"  # every picture shown was marked "can't tell"
EMPTY = "empty"  # every picture is marked empty


def pass_names(record: PassRecord, labels: LabelStore) -> list[str]:
    """What a pass showed: the species names people gave its pictures, or their groups where no
    name was given; each counted once per pass, even when several pictures show it."""
    names: list[str] = []
    waiting = False
    shown = 0
    for picture in record.pictures:
        person_empty = labels.empty(picture.name)
        if person_empty if person_empty is not None else picture.empty:
            continue
        shown += 1
        name = labels.name(picture.name) or labels.group(picture.name)
        if name:
            if name not in names:
                names.append(name)
        elif not labels.unclear(picture.name):
            waiting = True
    if shown == 0:
        return [EMPTY]
    if waiting:
        return names + [UNSORTED]
    return names or [CANT_TELL]


def passes_per_survey_day(season: Season, labels: LabelStore) -> list[DayCount]:
    """Passes per survey day by group or species and direction; never called animals."""
    counts: Counter[tuple[str, str, str]] = Counter()
    for record in season.passes:
        for name in pass_names(record, labels):
            counts[(record.survey_day, name, record.direction)] += 1
    return [
        DayCount(survey_day=day, name=name, direction=direction, passes=n)
        for (day, name, direction), n in sorted(counts.items())
    ]
