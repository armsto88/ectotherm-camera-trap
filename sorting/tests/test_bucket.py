"""Animals found in the bucket behind the trap, matched to passes and stored as labels."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from conftest import CardBuilder

from trapsort.card import import_card, read_season
from trapsort.cli import main
from trapsort.evaluate import PlanError, match_bucket_checks, read_bucket_checks
from trapsort.labels import LabelStore

HEADER = "checked_at,trap_id,animal,name,group\n"


def _season(card: CardBuilder, tmp_path: Path, passes: list[tuple[str, str, str]]) -> Path:
    """A season of passes (start, direction, the group a person gave its pictures)."""
    for start, direction, _ in passes:
        card.add_pass("2026-05-14", start, start.replace(":00Z", ":02Z"), direction=direction)
    season_dir = tmp_path / "season"
    season = import_card(card.root, season_dir)
    labels = LabelStore(season_dir / "labels.csv")
    for record, (_, _, group) in zip(season.passes, passes):
        for picture in record.pictures:
            labels.set_group(picture.name, group, "Ann")
    return season_dir


def _checks(tmp_path: Path, rows: str) -> Path:
    path = tmp_path / "bucket_checks.csv"
    path.write_text(HEADER + rows)
    return path


# spec: 2a1668f9
def test_a_bucket_animal_labels_its_pictures(card: CardBuilder, tmp_path: Path, capsys) -> None:
    season_dir = _season(card, tmp_path, [("2026-05-14T21:05:00Z", "AtoB", "lizard")])
    checks = _checks(tmp_path, "2026-05-15T07:30:00Z,ECT_0A1B2C,1,Lacerta agilis,lizard\n")

    assert main(["bucket", str(season_dir), str(checks)]) == 0
    assert "1 matched to a pass (1 new labels)" in capsys.readouterr().out

    labels = LabelStore(season_dir / "labels.csv")
    checked = datetime(2026, 5, 15, 7, 30, tzinfo=UTC)
    assert labels.bucket_labels("ECT_0A1B2C-2026-05-14-1") == [
        ("Lacerta agilis", "lizard", checked)
    ]
    # The label belongs to the pass, and so to each of its pictures.
    season = read_season(season_dir)
    assert all(p.pass_id == "ECT_0A1B2C-2026-05-14-1" for p in season.passes[0].pictures)

    # Run again, it stores nothing twice.
    assert main(["bucket", str(season_dir), str(checks)]) == 0
    assert "(0 new labels)" in capsys.readouterr().out
    assert len(LabelStore(season_dir / "labels.csv").bucket_labels(season.passes[0].pass_id)) == 1


def test_the_earliest_pass_that_went_through_matches_first(
    card: CardBuilder, tmp_path: Path
) -> None:
    season_dir = _season(
        card,
        tmp_path,
        [
            ("2026-05-14T20:00:00Z", "backB", "toad"),  # turned back
            ("2026-05-14T21:00:00Z", "AtoB", "toad"),  # went through
            ("2026-05-14T22:00:00Z", "AtoB", "toad"),
            ("2026-05-14T23:00:00Z", "AtoB", "newt"),
        ],
    )
    checks = _checks(
        tmp_path,
        "2026-05-15T07:30:00Z,ECT_0A1B2C,1,Bufo bufo,toad\n"
        "2026-05-15T07:30:00Z,ECT_0A1B2C,2,Bufo bufo,toad\n"
        "2026-05-15T07:30:00Z,ECT_0A1B2C,3,Bufo bufo,toad\n"
        "2026-05-15T07:30:00Z,ECT_0A1B2C,4,Bufo bufo,toad\n",
    )
    season = read_season(season_dir)
    matches = match_bucket_checks(
        season, LabelStore(season_dir / "labels.csv"), read_bucket_checks(checks)
    )
    assert [m.pass_id for m in matches] == [
        "ECT_0A1B2C-2026-05-14-2",
        "ECT_0A1B2C-2026-05-14-3",
        "ECT_0A1B2C-2026-05-14-1",
        None,  # the newt pass shows no toad: this toad was missed
    ]


def test_only_passes_since_the_previous_check_match(card: CardBuilder, tmp_path: Path) -> None:
    season_dir = _season(
        card,
        tmp_path,
        [("2026-05-14T21:00:00Z", "AtoB", "frog"), ("2026-05-14T23:00:00Z", "AtoB", "frog")],
    )
    checks = _checks(
        tmp_path,
        # The evening check found nothing; the frog of the morning check came after it.
        "2026-05-14T22:00:00Z,ECT_0A1B2C,,,\n"
        "2026-05-15T07:30:00Z,ECT_0A1B2C,1,Rana temporaria,frog\n"
        "2026-05-15T07:30:00Z,ECT_0A1B2C,2,Rana temporaria,frog\n"
        "2026-05-15T07:30:00Z,ECT_OTHER,1,Rana temporaria,frog\n",  # another trap's bucket
    )
    season = read_season(season_dir)
    matches = match_bucket_checks(
        season, LabelStore(season_dir / "labels.csv"), read_bucket_checks(checks)
    )
    assert [(m.animal, m.pass_id) for m in matches] == [
        ("1", "ECT_0A1B2C-2026-05-14-2"),
        ("2", None),
    ]


@pytest.mark.parametrize(
    ("rows", "message"),
    [
        ("2026-05-15 07:30,ECT_0A1B2C,1,Bufo bufo,toad\n", "needs its time zone"),
        ("yesterday,ECT_0A1B2C,1,Bufo bufo,toad\n", "not a time"),
        ("2026-05-15T07:30:00Z,ECT_0A1B2C,1,Bufo bufo,dragon\n", "is not one of"),
        ("2026-05-15T07:30:00Z,ECT_0A1B2C,,Bufo bufo,toad\n", "needs its number"),
        ("2026-05-15T07:30:00Z,,1,Bufo bufo,toad\n", "trap_id is missing"),
        ("2026-05-15T07:30:00Z,ECT_0A1B2C,1,toad\n", "expected 5 fields"),
    ],
)
def test_malformed_bucket_checks_raise_plan_error(tmp_path: Path, rows: str, message: str) -> None:
    with pytest.raises(PlanError, match=message):
        read_bucket_checks(_checks(tmp_path, rows))


def test_bucket_command_reports_a_malformed_file(card: CardBuilder, tmp_path: Path, capsys) -> None:
    season_dir = _season(card, tmp_path, [("2026-05-14T21:05:00Z", "AtoB", "lizard")])
    checks = tmp_path / "bucket_checks.csv"
    checks.write_text("when,what\n")
    assert main(["bucket", str(season_dir), str(checks)]) == 1
    assert "expected the header" in capsys.readouterr().err
