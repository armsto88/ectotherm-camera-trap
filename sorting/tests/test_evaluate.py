"""Evaluating a run: the three outcomes, missed animals, sensing and the model's agreement."""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import CardBuilder

from trapsort.card import import_card, read_season
from trapsort.cli import main
from trapsort.evaluate import PlanError, evaluate, read_bucket_checks, read_plan
from trapsort.labels import LabelStore

PLAN_HEADER = "planned_at,model,body_length_mm,height_mm,speed_mm_s,temperature_c,light,direction\n"


def _plan(tmp_path: Path, rows: list[str]) -> Path:
    path = tmp_path / "plan.csv"
    path.write_text(PLAN_HEADER + "".join(rows))
    return path


def _bench_run(card: CardBuilder, tmp_path: Path) -> tuple[Path, Path]:
    """A bench run of four planned passages of known animals: the first named and identified,
    the second only grouped, the third with a blurred picture, the fourth not noticed; and a
    PIR-only pass the plan does not hold."""
    day = "2026-05-14"
    card.add_pass(day, f"{day}T21:00:01Z", f"{day}T21:00:03Z", pilot=True,
                  model=("lizard", 0.9, "m1"))  # fmt: skip
    card.add_pass(day, f"{day}T21:05:00Z", f"{day}T21:05:02Z", noticed_by="both", pilot=True,
                  model=("other", 0.7, "m1"))  # fmt: skip
    card.add_pass(day, f"{day}T21:10:02Z", f"{day}T21:10:04Z", pilot=True,
                  model=("snake", 0.6, "m1"))  # fmt: skip
    card.add_pass(day, f"{day}T21:30:00Z", f"{day}T21:30:02Z", noticed_by="pir", pilot=True,
                  direction="unknown", heights_a="", heights_b="")  # fmt: skip
    season_dir = tmp_path / "season"
    season = import_card(card.root, season_dir)
    labels = LabelStore(season_dir / "labels.csv")
    first, second, third, fourth = (r.pictures[0].name for r in season.passes)
    labels.set_group(first, "lizard", "Ann")
    labels.set_name(first, "Zootoca vivipara", "Ann")
    labels.set_group(second, "toad", "Ann")
    labels.set_unclear(third, "Ann")
    labels.set_empty(fourth, True, "Ann")
    plan = _plan(
        tmp_path,
        [
            f"{day}T21:00:00Z,Zootoca vivipara,45,8,60,15,dark,AtoB\n",
            f"{day}T21:05:00Z,Bufo bufo,80,30,40,12,dark,AtoB\n",
            f"{day}T21:10:00Z,Natrix natrix,300,15,120,18,daylight,BtoA\n",
            f"{day}T21:20:00Z,Triturus cristatus,60,10,30,10,dark,AtoB\n",
        ],
    )
    return season_dir, plan


# spec: 36e16dab
def test_results_of_a_test_run(card: CardBuilder, tmp_path: Path, capsys) -> None:
    season_dir, plan = _bench_run(card, tmp_path)
    report = evaluate(
        read_season(season_dir), LabelStore(season_dir / "labels.csv"), read_plan(plan)
    )
    assert report.animals == 4
    assert (report.noticed, report.usable, report.identified) == (3, 2, 1)
    assert (report.share(report.noticed), report.share(report.usable)) == (0.75, 0.5)
    assert report.share(report.identified) == 0.25
    assert len(report.missed) == 2  # the blurred one and the one not noticed
    assert report.fully_sorted

    assert main(["evaluate", str(season_dir), "--plan", str(plan)]) == 0
    out = capsys.readouterr().out
    assert "noticed                   3 of 4 animals  75%" in out
    assert "with a usable picture     2 of 4 animals  50%" in out
    assert "identified                1 of 4 animals  25%" in out
    assert "picture" not in out.split("animals passed")[0]


def test_a_run_not_fully_sorted_says_so(card: CardBuilder, tmp_path: Path, capsys) -> None:
    card.add_pass("2026-05-14", "2026-05-14T21:00:01Z", "2026-05-14T21:00:03Z")
    season_dir = tmp_path / "season"
    import_card(card.root, season_dir)
    plan = _plan(tmp_path, ["2026-05-14T21:00:00Z,Zootoca vivipara,45,8,60,15,dark,AtoB\n"])
    assert main(["evaluate", str(season_dir), "--plan", str(plan)]) == 0
    assert "Not fully sorted: 1 pictures nobody has looked at yet" in capsys.readouterr().out


# spec: f2e7b606
def test_passes_by_what_noticed_them(card: CardBuilder, tmp_path: Path) -> None:
    season_dir, plan = _bench_run(card, tmp_path)
    report = evaluate(
        read_season(season_dir), LabelStore(season_dir / "labels.csv"), read_plan(plan)
    )
    assert (report.by_lasers_only, report.by_pir_only, report.by_both) == (2, 1, 1)


# spec: 9426c4fa
def test_model_agreement_of_a_test_run(card: CardBuilder, tmp_path: Path) -> None:
    season_dir, plan = _bench_run(card, tmp_path)
    report = evaluate(
        read_season(season_dir), LabelStore(season_dir / "labels.csv"), read_plan(plan)
    )
    # The lizard pass agrees; the toad pass, which the model called other, does not. The
    # blurred pass and the empty one have no group from people, so they do not count.
    assert (report.agreement.agreed, report.agreement.n) == (1, 2)
    assert report.agreement.share == 0.5
    assert (report.agreement_by_type["lizard"].agreed, report.agreement_by_type["lizard"].n) == (
        1,
        1,
    )
    assert report.agreement_by_type["frog_or_toad"].n == 1
    assert report.agreement_by_type["frog_or_toad"].agreed == 0
    assert report.agreement_by_type["snake"].share is None
    assert report.left_out_of_agreement == 0


# spec: d7c82910
def test_passes_sorted_with_the_suggestion_shown(card: CardBuilder, tmp_path: Path, capsys) -> None:
    day = "2026-05-14"
    card.add_pass(day, f"{day}T21:00:01Z", f"{day}T21:00:03Z", model=("lizard", 0.9, "m1"))
    card.add_pass(day, f"{day}T21:05:00Z", f"{day}T21:05:02Z", model=("snake", 0.9, "m1"))
    season_dir = tmp_path / "season"
    season = import_card(card.root, season_dir)
    labels = LabelStore(season_dir / "labels.csv")
    for record in season.passes:
        labels.set_group(record.pictures[0].name, "lizard", "Ann")
    plan = _plan(tmp_path, [f"{day}T21:00:00Z,Zootoca vivipara,45,8,60,15,dark,AtoB\n"])
    report = evaluate(read_season(season_dir), labels, read_plan(plan))
    assert report.agreement.n == 0
    assert report.left_out_of_agreement == 2
    assert "shown as a suggestion" in report.left_out_reason

    assert main(["evaluate", str(season_dir), "--plan", str(plan)]) == 0
    out = capsys.readouterr().out
    assert "left out: 2 passes sorted with the model's type shown as a suggestion" in out


def _field_phase(card: CardBuilder, tmp_path: Path) -> tuple[Path, Path]:
    """Two nights at a fence with a bucket behind the trap: a lizard photographed and sorted,
    and a newt that reached the bucket with no pass showing a newt."""
    card.add_pass("2026-05-14", "2026-05-14T21:00:00Z", "2026-05-14T21:00:02Z")
    card.add_pass("2026-05-14", "2026-05-14T23:00:00Z", "2026-05-14T23:00:02Z", animal=[False])
    season_dir = tmp_path / "season"
    season = import_card(card.root, season_dir)
    labels = LabelStore(season_dir / "labels.csv")
    labels.set_group(season.passes[0].pictures[0].name, "lizard", "Ann")
    labels.set_empty(season.passes[1].pictures[0].name, True, "Ann")
    checks = tmp_path / "bucket_checks.csv"
    checks.write_text(
        "checked_at,trap_id,animal,name,group\n"
        "2026-05-15T07:30:00Z,ECT_0A1B2C,1,Zootoca vivipara,lizard\n"
        "2026-05-15T07:30:00Z,ECT_0A1B2C,2,Lissotriton vulgaris,newt\n"
    )
    return season_dir, checks


# spec: fb3c43de
def test_an_animal_in_the_bucket_without_a_matching_picture(
    card: CardBuilder, tmp_path: Path
) -> None:
    season_dir, checks = _field_phase(card, tmp_path)
    report = evaluate(
        read_season(season_dir), LabelStore(season_dir / "labels.csv"), read_bucket_checks(checks)
    )
    assert report.animals == 2
    assert report.missed == ["2026-05-15 07:30 animal 2 Lissotriton vulgaris"]


# spec: 9df1ab87
def test_an_animal_in_the_bucket_with_a_matching_picture(
    card: CardBuilder, tmp_path: Path, capsys
) -> None:
    season_dir, checks = _field_phase(card, tmp_path)
    assert main(["bucket", str(season_dir), str(checks)]) == 0
    labels = LabelStore(season_dir / "labels.csv")
    report = evaluate(read_season(season_dir), labels, read_bucket_checks(checks))
    assert (report.noticed, report.usable) == (1, 1)
    # Its identification in the hand is the label of that pass.
    assert labels.bucket_labels("ECT_0A1B2C-2026-05-14-1")[0][:2] == (
        "Zootoca vivipara",
        "lizard",
    )
    assert main(["evaluate", str(season_dir), "--bucket-checks", str(checks)]) == 0
    assert "missed: 1 animals" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("row", "message"),
    [
        ("2026-05-14 21:00,Bufo bufo,80,30,40,12,dark,AtoB\n", "needs its time zone"),
        ("2026-05-14T21:00:00Z,,80,30,40,12,dark,AtoB\n", "model is missing"),
        ("2026-05-14T21:00:00Z,Bufo bufo,80,30,40,12,dusk,AtoB\n", "not dark or daylight"),
        ("2026-05-14T21:00:00Z,Bufo bufo,80,30,40,12,dark,backA\n", "not AtoB or BtoA"),
        ("2026-05-14T21:00:00Z,Bufo bufo,eight,30,40,12,dark,AtoB\n", "are numbers"),
        ("2026-05-14T21:00:00Z,Bufo bufo,80,30\n", "expected 8 fields"),
    ],
)
def test_malformed_plans_raise_plan_error(tmp_path: Path, row: str, message: str) -> None:
    with pytest.raises(PlanError, match=message):
        read_plan(_plan(tmp_path, [row]))
