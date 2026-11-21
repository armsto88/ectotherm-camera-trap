"""Marking the pictures that look like their survey day's empty view."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops

from .model import Season

# Pictures are compared as small greyscale thumbnails, so that noise and a slight shift of the
# light do not count as an animal, and in patches, so that a small animal in one place counts as
# much as a large one: a 3 cm animal covers only about one percent of the view, which a
# difference averaged over the whole picture would miss. Patches overlap by half, so that an
# animal on the border between two still fills most of one.
THUMBNAIL = (64, 48)
CELL = 4  # thumbnail pixels per side of a cell; a patch is 2 by 2 cells, stepping one cell

# The largest patch difference still marked empty, from 0 to 1.
DEFAULT_THRESHOLD = 0.03


def thumbnail(path: Path) -> Image.Image:
    """The picture as a greyscale thumbnail."""
    with Image.open(path) as image:
        return image.convert("L").resize(THUMBNAIL, Image.Resampling.BOX)


def difference(a: Image.Image, b: Image.Image) -> float:
    """The largest mean absolute difference of two thumbnails over any patch, from 0 to 1."""
    width, height = THUMBNAIL[0] // CELL, THUMBNAIL[1] // CELL
    cells = ImageChops.difference(a, b).resize((width, height), Image.Resampling.BOX).tobytes()
    largest = 0
    for y in range(height - 1):
        for x in range(width - 1):
            at = y * width + x
            patch = cells[at] + cells[at + 1] + cells[at + width] + cells[at + width + 1]
            largest = max(largest, patch)
    return largest / (4 * 255)


def mark_empty(season: Season, threshold: float) -> None:
    """Marks pictures that differ from their survey day's empty view by less than threshold.

    A day with several empty-view pictures takes the one closest to the picture. Every other
    picture is marked as not empty, and a picture of a day without an empty view stays unjudged;
    both are left for a person.
    """
    views = {
        day: [thumbnail(view.file) for view in pictures]
        for day, pictures in season.empty_views.items()
    }
    for picture in season.pictures:
        day_views = views.get(picture.survey_day)
        if not day_views:
            picture.empty = None
            picture.difference = None
            continue
        shot = thumbnail(picture.file)
        picture.difference = min(difference(shot, view) for view in day_views)
        picture.empty = picture.difference < threshold
