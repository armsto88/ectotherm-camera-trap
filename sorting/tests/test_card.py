"""Reading a card copy, and the trapsort import command."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from conftest import SUMMARY_LINE, CardBuilder

from trapsort.card import CardError, read_card
from trapsort.cli import main


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
        (lambda t: t.replace(",lasers,", ",lasers,extra,"), "expected 10 fields"),
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


def test_malformed_fault_log_and_summary_raise_card_error(card: CardBuilder) -> None:
    card.add_fault("2026-05-14T23:00:00Z,on_fire,\n")
    with pytest.raises(CardError, match="unknown fault"):
        read_card(card.root)
    (card.root / "faults.csv").unlink()
    card.add_summary("{not json\n")
    with pytest.raises(CardError, match="not a JSON reading"):
        read_card(card.root)


def test_import_command_reports_the_card(card: CardBuilder, capsys) -> None:
    assert main(["import", str(bench_run_card(card).root)]) == 0
    out = capsys.readouterr().out
    assert "Trap ECT_0A1B2C: 2 survey days, 3 passes, 4 pictures, 1 faults" in out
    assert "2026-05-14      2 passes  1 empty-view pictures" in out


def test_import_command_fails_on_malformed_card(card: CardBuilder, capsys) -> None:
    bench_run_card(card)
    (card.root / "passes" / "2026-05-14.csv").write_text("nonsense\n")
    assert main(["import", str(card.root)]) == 1
    assert "trapsort:" in capsys.readouterr().err
