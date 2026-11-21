"""Reading a card copy, and the trapsort import command."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from conftest import SUMMARY_LINE, CardBuilder

from trapsort.card import CardError, import_card, read_card, read_season, write_sorting
from trapsort.cli import main
from trapsort.model import GROUPS, model_type_of


def bench_run_card(card: CardBuilder) -> CardBuilder:
    """A card as a short bench run leaves it: passes on two survey days, a PIR-only pass marked
    in pilot mode, daily pictures, a fault and a summary."""
    card.add_pass("2026-05-14", "2026-05-14T21:05:09Z", "2026-05-14T21:05:11Z", animal=[True, True])
    card.add_pass(
        "2026-05-14",
        "2026-05-14T22:10:00Z",
        "2026-05-14T22:10:04Z",
        direction="unknown",
        heights_a="",
        heights_b="",
        noticed_by="pir",
        animal=[False],
        judged_empty=[1],
    )
    card.add_pass(
        "2026-05-15",
        "2026-05-15T20:00:00Z",
        "2026-05-15T20:00:03Z",
        direction="backB",
        heights_a="",
        heights_b="lowest;middle",
        noticed_by="both",
    )
    card.add_empty_view("2026-05-14")
    card.add_empty_view("2026-05-15")
    card.add_fault('2026-05-14T23:00:00Z,beam_blocked,"point A, lowest"\n')
    card.add_summary(SUMMARY_LINE)
    return card


def test_reads_card_copy_of_a_bench_run(card: CardBuilder) -> None:
    season = read_card(bench_run_card(card).root)

    assert season.trap_id == "ECT_0A1B2C"
    assert season.config["utc_offset_min"] == "60"
    assert season.survey_days == ["2026-05-14", "2026-05-15"]
    assert [r.pass_id for r in season.passes] == [
        "ECT_0A1B2C-2026-05-14-1",
        "ECT_0A1B2C-2026-05-14-2",
        "ECT_0A1B2C-2026-05-15-1",
    ]

    first = season.passes[0]
    assert first.start_utc == datetime(2026, 5, 14, 21, 5, 9, tzinfo=UTC)
    assert first.direction == "AtoB"
    assert first.heights_a == ("lowest",)
    assert first.noticed_by == "lasers"
    assert [p.name for p in first.pictures] == [
        "ECT_0A1B2C-2026-05-14-1_1.jpg",
        "ECT_0A1B2C-2026-05-14-1_2.jpg",
    ]
    assert all(p.file.is_file() and p.pass_id == first.pass_id for p in first.pictures)

    pir_only = season.passes[1]
    assert pir_only.direction == "unknown"
    assert pir_only.heights_a == ()
    assert pir_only.pictures[0].judged_empty_on_trap

    assert season.passes[2].heights_b == ("lowest", "middle")
    assert len(season.pictures) == 4
    assert [p.name for p in season.empty_views["2026-05-14"]] == ["empty_1200.jpg"]
    assert season.faults == [
        {
            "time_utc": datetime(2026, 5, 14, 23, 0, tzinfo=UTC),
            "fault": "beam_blocked",
            "detail": "point A, lowest",
        }
    ]
    assert season.summaries[0]["trapPasses"] == 143


def test_empty_card_has_no_passes(tmp_path) -> None:
    season = read_card(tmp_path)
    assert season.passes == [] and season.trap_id == "ECT_UNSET"


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda t: t.replace("pass_id,", "id,", 1), "expected the header"),
        (lambda t: t.replace(",AtoB,", ",sideways,"), "unknown direction"),
        (lambda t: t.replace("2026-05-14T21:05:09Z", "2026-05-14 21:05"), "not a UTC time"),
        (lambda t: t.replace(",lasers,", ",lasers,extra,"), "expected 14 fields"),
        (lambda t: t.replace(",lasers,", ",camera,"), "unknown noticed_by"),
        (lambda t: t.replace(",lowest,", ",ankle,", 1), "unknown beam height"),
        (lambda t: t.replace("_2.jpg", "_9.jpg"), "is missing"),
    ],
)
def test_malformed_pass_file_raises_card_error(card: CardBuilder, change, message) -> None:
    bench_run_card(card)
    path = card.root / "passes" / "2026-05-14.csv"
    path.write_text(change(path.read_text()))
    with pytest.raises(CardError, match=message):
        read_card(card.root)


def test_model_columns_with_and_without_a_model(card: CardBuilder) -> None:
    card.add_pass("2026-05-14", "2026-05-14T21:05:09Z", "2026-05-14T21:05:11Z", pilot=True)
    card.add_pass(
        "2026-05-14",
        "2026-05-14T21:30:00Z",
        "2026-05-14T21:30:02Z",
        model=("lizard", 0.87, "m1.0.0"),
    )
    without, with_model = read_card(card.root).passes
    assert without.pilot is True
    assert (without.model_type, without.model_confidence, without.model_version) == (
        None,
        None,
        None,
    )
    assert with_model.pilot is False
    assert (with_model.model_type, with_model.model_confidence, with_model.model_version) == (
        "lizard",
        0.87,
        "m1.0.0",
    )


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda t: t.replace(",lizard,", ",newt,"), "unknown model type"),
        (lambda t: t.replace(",0.87,", ",high,"), "model_confidence is not a number"),
        (lambda t: t.replace(",0.87,", ",1.20,"), "not between 0 and 1"),
        (lambda t: t.replace(",lizard,", ",,"), "without a model type"),
        (lambda t: t.replace(",false,lizard", ",no,lizard"), "pilot is not true or false"),
    ],
)
def test_malformed_model_columns_raise_card_error(card: CardBuilder, change, message) -> None:
    card.add_pass(
        "2026-05-14",
        "2026-05-14T21:30:00Z",
        "2026-05-14T21:30:02Z",
        model=("lizard", 0.87, "m1.0.0"),
    )
    path = card.root / "passes" / "2026-05-14.csv"
    path.write_text(change(path.read_text()))
    with pytest.raises(CardError, match=message):
        read_card(card.root)


def test_settings_for_placement_and_place(tmp_path: Path) -> None:
    card = CardBuilder(
        tmp_path / "card",
        settings="placement=end\nside_a=pond side\nlatitude=49.4521\nlongitude=7.7541\n"
        "send_every_h=24\nlink_timeout_s=180\nconfig_version=3\n",
    )
    season = read_card(card.root)
    assert season.placement == "end"
    assert season.side_a == "pond side"
    assert season.coordinates == (49.4521, 7.7541)
    assert season.config["config_version"] == "3"

    plain = read_card(CardBuilder(tmp_path / "plain").root)
    assert (plain.placement, plain.side_a, plain.coordinates) == ("line", "", None)


@pytest.mark.parametrize(
    ("settings", "message"),
    [
        ("placement=middle\n", "not line or end"),
        ("latitude=91\nlongitude=7\n", "out of range"),
        ("latitude=north\n", "not a number"),
    ],
)
def test_malformed_settings_raise_card_error(tmp_path: Path, settings: str, message: str) -> None:
    card = CardBuilder(tmp_path / "card", settings=settings)
    with pytest.raises(CardError, match=message):
        read_card(card.root)


def test_model_type_of_a_group() -> None:
    assert [model_type_of(g) for g in GROUPS] == [
        "frog_or_toad",
        "frog_or_toad",
        "other",
        "lizard",
        "snake",
        "other",
        "other",
    ]


def test_malformed_fault_log_and_summary_raise_card_error(card: CardBuilder) -> None:
    card.add_fault("2026-05-14T23:00:00Z,link_failed,no network\n")
    card.add_fault("2026-05-14T23:10:00Z,update_failed,model m1.1.0: file\n")
    assert [f["fault"] for f in read_card(card.root).faults] == ["link_failed", "update_failed"]
    card.add_fault("2026-05-14T23:00:00Z,on_fire,\n")
    with pytest.raises(CardError, match="unknown fault"):
        read_card(card.root)
    (card.root / "faults.csv").unlink()
    card.add_summary("{not json\n")
    with pytest.raises(CardError, match="not a JSON reading"):
        read_card(card.root)


def _files(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_an_imported_card_equals_the_original(card: CardBuilder, tmp_path: Path) -> None:
    bench_run_card(card)
    season = import_card(card.root, tmp_path / "season")
    copy = tmp_path / "season" / "card"
    assert _files(copy) == _files(card.root)
    assert not (tmp_path / "season" / "card.partial").exists()
    # The season read back points into the copy, not at the card.
    assert all(p.file.is_relative_to(copy) for p in season.pictures)
    assert len(season.passes) == 3


def test_a_second_import_into_the_same_season_is_refused(card: CardBuilder, tmp_path: Path) -> None:
    bench_run_card(card)
    import_card(card.root, tmp_path / "season")
    before = _files(tmp_path / "season" / "card")
    card.add_pass("2026-05-16", "2026-05-16T20:00:00Z", "2026-05-16T20:00:02Z")
    with pytest.raises(CardError, match="already holds a card"):
        import_card(card.root, tmp_path / "season")
    assert _files(tmp_path / "season" / "card") == before


def test_a_malformed_card_is_not_copied(card: CardBuilder, tmp_path: Path) -> None:
    bench_run_card(card)
    (card.root / "passes" / "2026-05-14.csv").write_text("nonsense\n")
    with pytest.raises(CardError):
        import_card(card.root, tmp_path / "season")
    assert not (tmp_path / "season" / "card").exists()


def test_read_season_reads_back_what_write_sorting_wrote(card: CardBuilder, tmp_path: Path) -> None:
    bench_run_card(card)
    season_dir = tmp_path / "season"
    season = import_card(card.root, season_dir)
    first, second, third, fourth = season.pictures
    first.empty, first.difference = False, 0.2125
    second.empty, second.difference = False, 0.1875
    third.empty, third.difference = True, 0.0125
    # The fourth picture has not been judged.
    write_sorting(season, season_dir)

    back = read_season(season_dir)
    assert [(p.name, p.empty, p.difference) for p in back.pictures] == [
        (first.name, False, 0.2125),
        (second.name, False, 0.1875),
        (third.name, True, 0.0125),
        (fourth.name, None, None),
    ]
    lines = (season_dir / "sorting.csv").read_text().splitlines()
    assert lines[0] == "picture,pass_id,survey_day,empty,difference"
    assert lines[3] == f"{third.name},{third.pass_id},2026-05-14,true,0.0125"


def test_a_season_without_sorting_has_no_marks(card: CardBuilder, tmp_path: Path) -> None:
    bench_run_card(card)
    import_card(card.root, tmp_path / "season")
    assert all(p.empty is None for p in read_season(tmp_path / "season").pictures)
    with pytest.raises(CardError, match="not a season folder"):
        read_season(tmp_path / "elsewhere")


@pytest.mark.parametrize(
    ("row", "message"),
    [
        ("nobody.jpg,X-1,2026-05-14,true,0.01", "is not on the card"),
        ("{name},{pass_id},2026-05-14,maybe,0.01", "empty is not true or false"),
        ("{name},{pass_id},2026-05-14,true,small", "difference is not a number"),
        ("{name},{pass_id},true", "expected 5 fields"),
    ],
)
def test_malformed_sorting_raises_card_error(
    card: CardBuilder, tmp_path: Path, row: str, message: str
) -> None:
    bench_run_card(card)
    season = import_card(card.root, tmp_path / "season")
    picture = season.pictures[0]
    (tmp_path / "season" / "sorting.csv").write_text(
        "picture,pass_id,survey_day,empty,difference\n"
        + row.format(name=picture.name, pass_id=picture.pass_id)
        + "\n"
    )
    with pytest.raises(CardError, match=message):
        read_season(tmp_path / "season")


def test_groups_include_turtles() -> None:
    assert GROUPS == ("frog", "toad", "newt", "lizard", "snake", "turtle", "other")


def test_import_command_reports_and_copies_the_card(
    card: CardBuilder, tmp_path: Path, capsys
) -> None:
    season_dir = tmp_path / "season"
    assert main(["import", str(bench_run_card(card).root), str(season_dir)]) == 0
    out = capsys.readouterr().out
    assert "Trap ECT_0A1B2C: 2 survey days, 3 passes, 4 pictures, 1 faults" in out
    assert "2026-05-14      2 passes  1 empty-view pictures" in out
    assert (season_dir / "card" / "trap.cfg").is_file()


def test_import_command_fails_on_malformed_card(card: CardBuilder, tmp_path: Path, capsys) -> None:
    bench_run_card(card)
    (card.root / "passes" / "2026-05-14.csv").write_text("nonsense\n")
    assert main(["import", str(card.root), str(tmp_path / "season")]) == 1
    assert "trapsort:" in capsys.readouterr().err
