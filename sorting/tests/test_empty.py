"""Marking pictures that look like their survey day's empty view, and trapsort sort."""

from __future__ import annotations

from pathlib import Path

from conftest import CardBuilder
from PIL import Image, ImageDraw

from trapsort.card import import_card, read_season
from trapsort.cli import main
from trapsort.empty import DEFAULT_THRESHOLD, mark_empty


def small_lizard_picture(path: Path, left: int, top: int) -> None:
    """The passage floor, 26 by 15 cm at 2 pixels per mm, with a lizard 3 cm long and 1 cm wide
    a little darker than the floor."""
    image = Image.new("L", (520, 300), 128)
    ImageDraw.Draw(image).ellipse((left, top, left + 60, top + 20), fill=75)
    image.save(path, "JPEG", quality=90)


# spec: 6e42dbca
def test_pictures_like_the_empty_view_are_marked(card: CardBuilder, tmp_path: Path) -> None:
    card.add_pass("2026-05-14", "2026-05-14T21:05:09Z", "2026-05-14T21:05:11Z", animal=[True])
    card.add_pass(
        "2026-05-14",
        "2026-05-14T22:10:00Z",
        "2026-05-14T22:10:04Z",
        noticed_by="pir",
        animal=[False, True, False],
    )
    card.add_empty_view("2026-05-14")
    season = import_card(card.root, tmp_path / "season")

    mark_empty(season, DEFAULT_THRESHOLD)

    assert [p.empty for p in season.pictures] == [False, True, False, True]
    animal, empty = season.pictures[0], season.pictures[1]
    assert empty.difference < DEFAULT_THRESHOLD < animal.difference


def test_a_small_animal_anywhere_is_left_for_a_person(card: CardBuilder, tmp_path: Path) -> None:
    # Wherever the lizard lies, also across the border of two patches, it is not marked empty.
    positions = [(10, 10), (230, 140), (250, 147), (452, 272), (96, 34)]
    for _ in positions:
        card.add_pass("2026-05-14", "2026-05-14T21:05:09Z", "2026-05-14T21:05:11Z")
    empty_view = card.root / "pictures" / "2026-05-14" / "empty_1200.jpg"
    Image.new("L", (520, 300), 128).save(empty_view, "JPEG", quality=90)
    season = import_card(card.root, tmp_path / "season")
    for picture, (left, top) in zip(season.pictures, positions):
        small_lizard_picture(picture.file, left, top)

    mark_empty(season, DEFAULT_THRESHOLD)

    assert [p.empty for p in season.pictures] == [False] * len(positions)


def test_the_closest_empty_view_of_the_day_counts(card: CardBuilder, tmp_path: Path) -> None:
    # The light changed during the day: the first daily picture is brighter than the second.
    card.add_pass("2026-05-14", "2026-05-14T21:05:09Z", "2026-05-14T21:05:11Z", animal=[False])
    card.add_empty_view("2026-05-14", "1200", shade=200)
    card.add_empty_view("2026-05-14", "1800", shade=128)
    season = import_card(card.root, tmp_path / "season")
    mark_empty(season, DEFAULT_THRESHOLD)
    assert season.pictures[0].empty is True


def test_a_day_without_an_empty_view_stays_unjudged(card: CardBuilder, tmp_path: Path) -> None:
    card.add_pass("2026-05-14", "2026-05-14T21:05:09Z", "2026-05-14T21:05:11Z", animal=[False])
    card.add_pass("2026-05-15", "2026-05-15T21:05:09Z", "2026-05-15T21:05:11Z", animal=[False])
    card.add_empty_view("2026-05-15")
    season = import_card(card.root, tmp_path / "season")
    mark_empty(season, DEFAULT_THRESHOLD)
    assert [(p.empty, p.difference is None) for p in season.pictures] == [
        (None, True),
        (True, False),
    ]


def test_sort_command_writes_the_marks(card: CardBuilder, tmp_path: Path, capsys) -> None:
    card.add_pass("2026-05-14", "2026-05-14T21:05:09Z", "2026-05-14T21:05:11Z", animal=[True])
    card.add_pass("2026-05-14", "2026-05-14T22:10:00Z", "2026-05-14T22:10:04Z", animal=[False])
    card.add_empty_view("2026-05-14")
    season_dir = tmp_path / "season"
    import_card(card.root, season_dir)

    assert main(["sort", str(season_dir)]) == 0
    assert "2 pictures: 1 marked empty, 1 left for a person" in capsys.readouterr().out
    assert [p.empty for p in read_season(season_dir).pictures] == [False, True]

    # A threshold above every difference marks both; sorting again writes the marks anew.
    assert main(["sort", str(season_dir), "--threshold", "0.99"]) == 0
    assert [p.empty for p in read_season(season_dir).pictures] == [True, True]
