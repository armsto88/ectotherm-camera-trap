"""The bench checks' own tests, on bench runs written here in the format of the rig and trap."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

from run import load_bench_run, match_plan, unplanned

PLAN_HEADER = "planned_at,model,body_length_mm,height_mm,speed_mm_s,temperature_c,light,direction\n"
PASS_HEADER = (
    "pass_id,start_utc,end_utc,direction,heights_a,heights_b,noticed_by,pictures,"
    "dropped_empty,judged_empty,pilot,model_type,model_confidence,model_version\n"
)


def write_run(folder: Path, planned: list[str], passes: list[str]) -> Path:
    """A run folder: plan.csv with the planned times, and a card with one pass per start time,
    each with one picture."""
    folder.mkdir(parents=True)
    (folder / "plan.csv").write_text(
        PLAN_HEADER + "".join(f"{t},flat 3 cm,30,3,60,15,dark,AtoB\n" for t in planned)
    )
    card = folder / "card"
    (card / "passes").mkdir(parents=True)
    (card / "trap.cfg").write_text("trap_id=ECT_BENCH1\n")
    rows = []
    for number, start in enumerate(passes, start=1):
        pass_id = f"ECT_BENCH1-2026-05-14-{number}"
        picture = card / "pictures" / "2026-05-14" / f"{pass_id}_1.jpg"
        picture.parent.mkdir(parents=True, exist_ok=True)
        Image.new("L", (16, 12), 128).save(picture, "JPEG")
        rows.append(
            f"{pass_id},{start},{start},AtoB,lowest,lowest,lasers,{picture.name},0,,true,,,\n"
        )
    (card / "passes" / "2026-05-14.csv").write_text(PASS_HEADER + "".join(rows))
    return folder


def test_a_recorded_run_is_paired_with_its_plan(tmp_path: Path) -> None:
    run = load_bench_run(
        write_run(
            tmp_path / "run",
            ["2026-05-14T21:00:00Z", "2026-05-14T21:01:00Z", "2026-05-14T21:02:00Z"],
            ["2026-05-14T21:00:01Z", "2026-05-14T21:00:59Z", "2026-05-14T21:02:02Z"],
        )
    )
    pairs = match_plan(run)
    assert [p.record.pass_id for p in pairs if p.record] == [
        "ECT_BENCH1-2026-05-14-1",
        "ECT_BENCH1-2026-05-14-2",
        "ECT_BENCH1-2026-05-14-3",
    ]
    assert [p.delay_s for p in pairs] == [1.0, -1.0, 2.0]
    assert all(len(p.pictures) == 1 and p.pictures[0].file.is_file() for p in pairs)
    assert unplanned(run, pairs) == []


def test_an_unmatched_planned_passage_shows_as_missing(tmp_path: Path) -> None:
    run = load_bench_run(
        write_run(
            tmp_path / "run",
            ["2026-05-14T21:00:00Z", "2026-05-14T21:01:00Z"],
            # The second planned passage left no pass; a pass five seconds later is not it.
            ["2026-05-14T21:00:01Z", "2026-05-14T21:01:05Z"],
        )
    )
    pairs = match_plan(run)
    assert [p.missing for p in pairs] == [False, True]
    assert pairs[1].pictures == [] and pairs[1].delay_s is None
    assert [r.pass_id for r in unplanned(run, pairs)] == ["ECT_BENCH1-2026-05-14-2"]
    # A wider window takes it.
    assert not any(p.missing for p in match_plan(run, window_s=6.0))


def test_two_planned_passages_never_share_a_pass(tmp_path: Path) -> None:
    run = load_bench_run(
        write_run(
            tmp_path / "run",
            ["2026-05-14T21:00:00Z", "2026-05-14T21:00:01Z"],
            ["2026-05-14T21:00:01Z"],
        )
    )
    assert [p.missing for p in match_plan(run)] == [False, True]


def test_a_malformed_run_raises(tmp_path: Path) -> None:
    folder = write_run(tmp_path / "run", ["2026-05-14T21:00:00Z"], ["2026-05-14T21:00:01Z"])
    (folder / "plan.csv").write_text("nonsense\n")
    with pytest.raises(Exception, match="expected the header"):
        load_bench_run(folder)


def test_the_bench_checks_on_a_recorded_run(tmp_path: Path) -> None:
    """The checks marked bench pass on a complete run and fail on one with a missing pass."""
    here = Path(__file__).parent.parent
    good = write_run(tmp_path / "good", ["2026-05-14T21:00:00Z"], ["2026-05-14T21:00:01Z"])
    bad = write_run(tmp_path / "bad", ["2026-05-14T21:00:00Z"], ["2026-05-14T21:00:09Z"])

    def bench(run: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-m", "pytest", "-m", "bench", "-q", "-p", "no:cacheprovider",
             "--bench-run", str(run), "test_bench_run.py"],
            check=False, cwd=here, capture_output=True, text=True,
        )  # fmt: skip

    assert bench(good).returncode == 0
    failed = bench(bad)
    assert failed.returncode == 1
    assert "1 planned passages left no pass" in failed.stdout
