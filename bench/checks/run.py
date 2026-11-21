"""A bench run: the plan of the rig and the copy of the trap's card from that run.

A run folder holds plan.csv, written for the rig, and card/, a copy of the trap's memory card
after the run. The checks pair each planned passage with the pass it produced.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from trapsort.card import read_card
from trapsort.evaluate import PlannedPassage, read_plan
from trapsort.model import PassRecord, Picture, Season


@dataclass
class BenchRun:
    """A bench run: its plan and the season read from its card copy."""

    folder: Path
    plan: list[PlannedPassage]
    season: Season


@dataclass
class PlannedPass:
    """One planned passage with the pass record and pictures it produced, or none."""

    planned: PlannedPassage
    record: PassRecord | None

    @property
    def pictures(self) -> list[Picture]:
        return self.record.pictures if self.record else []

    @property
    def missing(self) -> bool:
        """True when the trap recorded no pass for this planned passage."""
        return self.record is None

    @property
    def delay_s(self) -> float | None:
        """Seconds from the planned passage to the start of its pass."""
        if self.record is None:
            return None
        return (self.record.start_utc - self.planned.planned_at).total_seconds()


def load_bench_run(run: Path) -> BenchRun:
    """Reads plan.csv and the card copy in run with trapsort; raises on either error."""
    run = Path(run)
    return BenchRun(
        folder=run, plan=read_plan(run / "plan.csv").rows, season=read_card(run / "card")
    )


def match_plan(run: BenchRun, window_s: float = 2.0) -> list[PlannedPass]:
    """Pairs each planned passage with the pass that started within window_s of it.

    Planned passages are taken in time order, each with the closest pass not yet paired; a
    planned passage without one is missing, and a pass paired with none was not planned."""
    taken: set[str] = set()
    pairs = []
    for planned in sorted(run.plan, key=lambda p: p.planned_at):
        candidates = [
            record
            for record in run.season.passes
            if record.pass_id not in taken
            and abs((record.start_utc - planned.planned_at).total_seconds()) <= window_s
        ]
        record = min(
            candidates,
            key=lambda r: abs((r.start_utc - planned.planned_at).total_seconds()),
            default=None,
        )
        if record is not None:
            taken.add(record.pass_id)
        pairs.append(PlannedPass(planned, record))
    return pairs


def unplanned(run: BenchRun, pairs: list[PlannedPass]) -> list[PassRecord]:
    """The passes the trap recorded that no planned passage accounts for."""
    paired = {pair.record.pass_id for pair in pairs if pair.record}
    return [record for record in run.season.passes if record.pass_id not in paired]
