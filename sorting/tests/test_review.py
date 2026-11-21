"""People's labels, and the review page on which they sort passes and name the species."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from conftest import CardBuilder

from trapsort.card import import_card, read_season, write_sorting
from trapsort.labels import LabelError, LabelStore
from trapsort.model import Season
from trapsort.review import review_server, view_of

LIZARD = ("lizard", 0.87, "m1.0.0")


class Page:
    """The review page served on a free port, as a person's browser uses it."""

    def __init__(self, season: Season, labels: LabelStore) -> None:
        self.server = review_server(season, labels, 0)
        self.base = f"http://127.0.0.1:{self.server.server_port}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def get(self, path: str = "/") -> str:
        with urllib.request.urlopen(self.base + path) as response:
            return response.read().decode()

    def post(self, label: dict) -> int:
        request = urllib.request.Request(
            self.base + "/label",
            data=json.dumps({"by": "Tom", **label}).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request) as response:
                return response.status
        except urllib.error.HTTPError as error:
            return error.code

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture
def season_dir(card: CardBuilder, tmp_path: Path) -> Path:
    """A season of three passes: a lizard in two pictures, a blurred one, and one recorded in
    pilot mode whose single picture the computer marked empty."""
    card.add_pass(
        "2026-05-14",
        "2026-05-14T21:05:09Z",
        "2026-05-14T21:05:11Z",
        animal=[True, True],
        model=LIZARD,
    )
    card.add_pass(
        "2026-05-14", "2026-05-14T22:00:00Z", "2026-05-14T22:00:02Z", pilot=True, model=LIZARD
    )
    card.add_pass("2026-05-14", "2026-05-14T23:00:00Z", "2026-05-14T23:00:02Z", animal=[False])
    season_dir = tmp_path / "season"
    season = import_card(card.root, season_dir)
    season.pictures[-1].empty = True
    write_sorting(season, season_dir)
    return season_dir


@pytest.fixture
def page(season_dir: Path) -> Iterator[Page]:
    page = Page(read_season(season_dir), LabelStore(season_dir / "labels.csv"))
    yield page
    page.close()


def _section(page_html: str, pass_id: str) -> str:
    start = page_html.index(f"<h2>{pass_id}</h2>")
    end = page_html.find('<section class="pass', start)
    return page_html[start : end if end >= 0 else len(page_html)]


# spec: 016374dd
def test_a_person_sorts_and_names_a_pass(page: Page, season_dir: Path) -> None:
    pass_id = "ECT_0A1B2C-2026-05-14-1"
    pictures = [f"{pass_id}_1.jpg", f"{pass_id}_2.jpg"]
    assert page.post({"pictures": pictures, "group": "lizard", "name": "Lacerta agilis"}) == 200

    labels = LabelStore(season_dir / "labels.csv")
    assert [labels.group(p) for p in pictures] == ["lizard", "lizard"]
    assert [labels.name(p) for p in pictures] == ["Lacerta agilis", "Lacerta agilis"]
    # Stored with the pass record too: every row names its pass.
    rows = (season_dir / "labels.csv").read_text().splitlines()[1:]
    assert len(rows) == 4 and all(f",{pass_id}," in row for row in rows)
    assert all(",Tom," in row for row in rows)
    # The pass now counts as sorted.
    season = read_season(season_dir)
    assert view_of(season.passes[0], labels) == "sorted"
    assert "Lacerta agilis" in page.get("/?view=sorted")


# spec: f93d49ef
def test_a_person_cant_tell(page: Page, season_dir: Path) -> None:
    picture = "ECT_0A1B2C-2026-05-14-2_1.jpg"
    assert page.post({"pictures": [picture], "unclear": True}) == 200
    labels = LabelStore(season_dir / "labels.csv")
    assert labels.unclear(picture) is True
    assert labels.group(picture) is None
    # Looked at: the pass no longer waits to be sorted.
    assert view_of(read_season(season_dir).passes[1], labels) == "sorted"


# spec: 2cde2e6f
def test_a_person_corrects_an_empty_mark(page: Page, season_dir: Path) -> None:
    pass_id = "ECT_0A1B2C-2026-05-14-3"
    assert pass_id in page.get("/?view=empty")
    assert pass_id not in page.get("/?view=open")

    assert page.post({"pictures": [f"{pass_id}_1.jpg"], "empty": False}) == 200

    labels = LabelStore(season_dir / "labels.csv")
    assert labels.empty(f"{pass_id}_1.jpg") is False
    assert pass_id in page.get("/?view=open")
    assert pass_id not in page.get("/?view=empty")


# spec: 251da24f
def test_a_pass_with_two_different_animals(page: Page, season_dir: Path) -> None:
    first, second = "ECT_0A1B2C-2026-05-14-1_1.jpg", "ECT_0A1B2C-2026-05-14-1_2.jpg"
    assert page.post({"pictures": [first], "group": "toad", "name": "Bufo bufo"}) == 200
    assert page.post({"pictures": [second], "group": "newt", "name": "Triturus cristatus"}) == 200
    labels = LabelStore(season_dir / "labels.csv")
    assert (labels.group(first), labels.name(first)) == ("toad", "Bufo bufo")
    assert (labels.group(second), labels.name(second)) == ("newt", "Triturus cristatus")
    # Shown again, the pass opens picture by picture.
    assert 'class="pass one-by-one"' in page.get("/?view=sorted")


# spec: 4296a7e0
def test_the_model_type_is_hidden_in_the_pilot(page: Page) -> None:
    section = _section(page.get(), "ECT_0A1B2C-2026-05-14-2")
    assert "suggest" not in section
    assert "0.87" not in section and "87%" not in section
    assert 'button class="group" data-group="lizard"' in section  # an ordinary group button


# spec: 37dd1930
def test_the_model_type_is_suggested_after_the_pilot(page: Page, season_dir: Path) -> None:
    section = _section(page.get(), "ECT_0A1B2C-2026-05-14-1")
    assert 'data-suggestion="lizard"' in section
    assert "The trap's model suggests: lizard (87% sure)" in section
    assert 'class="group suggested" data-group="lizard"' in section
    # Showing the suggestion stores nothing; only what the person picks is their label.
    assert not (season_dir / "labels.csv").exists()
    picture = "ECT_0A1B2C-2026-05-14-1_1.jpg"
    assert page.post({"pictures": [picture], "group": "snake"}) == 200
    assert LabelStore(season_dir / "labels.csv").group(picture) == "snake"


def test_the_page_serves_pictures_and_refuses_bad_labels(page: Page) -> None:
    picture = "ECT_0A1B2C-2026-05-14-1_1.jpg"
    with urllib.request.urlopen(f"{page.base}/picture/{picture}") as response:
        assert response.headers["Content-Type"] == "image/jpeg"
        assert response.read()[:2] == b"\xff\xd8"
    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(f"{page.base}/picture/..%2Ftrap.cfg")
    assert page.post({"pictures": ["nobody.jpg"], "group": "lizard"}) == 400
    assert page.post({"pictures": [picture], "group": "dragon"}) == 400
    assert page.post({"pictures": [picture], "group": "lizard", "by": " "}) == 400
    assert page.post({"pictures": [picture], "empty": "yes"}) == 400


def test_the_latest_label_of_each_kind_counts(tmp_path: Path) -> None:
    labels = LabelStore(tmp_path / "labels.csv")
    picture = "T-2026-05-14-1_1.jpg"
    labels.set_group(picture, "frog", "Ann")
    labels.set_unclear(picture, "Bea")
    assert (labels.group(picture), labels.unclear(picture)) == (None, True)
    labels.set_group(picture, "toad", "Ann")
    labels.set_name(picture, "Bufo bufo", "Ann")
    labels.set_empty(picture, True, "Ann")
    labels.set_empty(picture, False, "Ann")
    again = LabelStore(tmp_path / "labels.csv")  # read back from the file
    assert (again.group(picture), again.unclear(picture)) == ("toad", False)
    assert (again.name(picture), again.empty(picture)) == ("Bufo bufo", False)
    assert again.empty("T-2026-05-14-1_2.jpg") is None


def test_bucket_labels_name_the_pass(tmp_path: Path) -> None:
    labels = LabelStore(tmp_path / "labels.csv")
    checked = datetime(2026, 5, 15, 7, 30, tzinfo=UTC)
    labels.add_bucket_label("T-2026-05-14-1", "Lacerta agilis", "lizard", checked)
    again = LabelStore(tmp_path / "labels.csv")
    assert again.bucket_labels("T-2026-05-14-1") == [("Lacerta agilis", "lizard", checked)]
    assert again.bucket_labels("T-2026-05-14-2") == []


def test_labels_that_the_store_refuses(tmp_path: Path) -> None:
    labels = LabelStore(tmp_path / "labels.csv")
    with pytest.raises(LabelError):
        labels.set_group("T-2026-05-14-1_1.jpg", "dragon", "Ann")  # type: ignore[arg-type]
    with pytest.raises(LabelError):
        labels.set_name("photo.jpg", "x", "Ann")
    (tmp_path / "bad.csv").write_text("picture,pass_id,kind,value,by,at\nx,y,colour,red,A,now\n")
    with pytest.raises(LabelError, match="unknown kind"):
        LabelStore(tmp_path / "bad.csv")
