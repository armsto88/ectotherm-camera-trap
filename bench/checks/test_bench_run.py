"""Checks every bench run passes: each planned passage is recorded, and nothing unplanned is."""

from __future__ import annotations

import pytest

from run import BenchRun, match_plan, unplanned


def _describe(pairs) -> str:
    return "\n".join(
        f"  {p.planned.planned_at:%H:%M:%S} {p.planned.model} {p.planned.direction}" for p in pairs
    )


@pytest.mark.bench
def test_every_planned_passage_is_recorded(bench_run: BenchRun) -> None:
    missing = [p for p in match_plan(bench_run) if p.missing]
    assert not missing, f"{len(missing)} planned passages left no pass:\n{_describe(missing)}"


@pytest.mark.bench
def test_no_pass_without_a_planned_passage(bench_run: BenchRun) -> None:
    extra = unplanned(bench_run, match_plan(bench_run))
    assert not extra, "passes no planned passage accounts for: " + ", ".join(
        r.pass_id for r in extra
    )
