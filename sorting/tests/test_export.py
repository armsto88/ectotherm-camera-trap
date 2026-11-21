"""Passes per survey day, and a season exported as a Camera Trap Data Package."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
from conftest import CardBuilder
from frictionless import Package
from jsonschema import Draft4Validator
from referencing import Registry, Resource

from trapsort.camtrapdp import BASE, PROFILE, ExportError, export_camtrap_dp
from trapsort.card import import_card, read_season
from trapsort.cli import main
from trapsort.labels import LabelStore
from trapsort.summary import passes_per_survey_day

SCHEMAS = Path(__file__).parent / "camtrap_dp"
PLACE = "latitude=49.4521\nlongitude=7.7541\n"


def camtrap_dp_problems(out: Path) -> list[str]:
    """What keeps an exported package from passing the Camtrap DP 1.0.1 checks: its description
    against the profile, and its tables, with their keys, against the table schemas."""
    descriptor = json.loads((out / "datapackage.json").read_text())

    def load(name: str) -> dict:
        return json.loads((SCHEMAS / name).read_text())

    geojson = Resource.from_contents(load("GeoJSON.json"))
    registry = Registry().with_resources(
        [
            ("https://specs.frictionlessdata.io/schemas/data-package.json",
             Resource.from_contents(load("data-package.json"))),
            ("http://json.schemastore.org/geojson.json", geojson),
            ("https://geojson.org/schema/GeoJSON.json", geojson),
        ]
    )  # fmt: skip
    profile = load("camtrap-dp-profile.json")
    validator = Draft4Validator(
        profile, registry=registry, format_checker=Draft4Validator.FORMAT_CHECKER
    )
    problems = [f"datapackage.json: {e.message}" for e in validator.iter_errors(descriptor)]
    if descriptor.get("profile") != PROFILE:
        problems.append("datapackage.json: not the Camtrap DP 1.0.1 profile")

    local = {k: v for k, v in descriptor.items() if k != "profile"}
    local["resources"] = []
    for resource in descriptor["resources"]:
        if resource["schema"] != f"{BASE}/{resource['name']}-table-schema.json":
            problems.append(f"{resource['name']}: not the Camtrap DP 1.0.1 table schema")
        local["resources"].append(
            resource | {"schema": load(f"{resource['name']}-table-schema.json")}
        )
    report = Package(local, basepath=str(out)).validate()
    for task in report.tasks:
        problems += [f"{task.name}: {error.message}" for error in task.errors]
    problems += [error.message for error in report.errors]
    return problems


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _season(card: CardBuilder, tmp_path: Path) -> Path:
    """A season of four passes: one a person sorted as lizard against the model's snake, one
    nobody sorted that the model called a snake, one marked empty, and one without a model."""
    day = "2026-05-14"
    card.add_pass(day, f"{day}T21:05:09Z", f"{day}T21:05:11Z", animal=[True, True],
                  model=("snake", 0.62, "m1.0.0"))  # fmt: skip
    card.add_pass(day, f"{day}T22:00:00Z", f"{day}T22:00:03Z", direction="BtoA",
                  model=("snake", 0.80, "m1.0.0"))  # fmt: skip
    card.add_pass(day, f"{day}T23:00:00Z", f"{day}T23:00:02Z", animal=[False],
                  direction="backA", model=("empty", 0.95, "m1.0.0"))  # fmt: skip
    card.add_pass("2026-05-15", "2026-05-15T20:00:00Z", "2026-05-15T20:00:02Z", pilot=True)
    season_dir = tmp_path / "season"
    season = import_card(card.root, season_dir)
    labels = LabelStore(season_dir / "labels.csv")
    for picture in season.passes[0].pictures:
        labels.set_group(picture.name, "lizard", "Ann")
        labels.set_name(picture.name, "Lacerta agilis", "Ann")
    labels.set_empty(season.passes[2].pictures[0].name, True, "Ann")
    labels.set_group(season.passes[3].pictures[0].name, "toad", "Ann")
    return season_dir


def _export(season_dir: Path) -> Path:
    """Exports the season; returns the folder the package is in, the season folder."""
    season = read_season(season_dir)
    labels = LabelStore(season_dir / "labels.csv")
    export_camtrap_dp(season, labels, project="Fence A", contact="Ann Smith")
    return season_dir


@pytest.fixture
def placed_card(tmp_path: Path) -> CardBuilder:
    return CardBuilder(tmp_path / "card", settings=PLACE + "placement=end\nside_a=pond side\n")


# spec: 0930417b
def test_a_season_is_summarised(placed_card: CardBuilder, tmp_path: Path, capsys) -> None:
    season_dir = _season(placed_card, tmp_path)
    counts = passes_per_survey_day(read_season(season_dir), LabelStore(season_dir / "labels.csv"))
    assert [(c.survey_day, c.name, c.direction, c.passes) for c in counts] == [
        ("2026-05-14", "Lacerta agilis", "AtoB", 1),
        ("2026-05-14", "empty", "backA", 1),
        ("2026-05-14", "unsorted", "BtoA", 1),
        ("2026-05-15", "toad", "AtoB", 1),
    ]
    assert main(["summarise", str(season_dir)]) == 0
    out = capsys.readouterr().out
    assert "passes, not animals" in out
    assert "survey_day,group_or_species,direction,passes" in out
    assert "2026-05-14,Lacerta agilis,AtoB,1" in out
    header = next(line for line in out.splitlines() if line.startswith("survey_day"))
    assert "animal" not in header


def test_one_animal_passing_twice_counts_as_two_passes(card: CardBuilder, tmp_path: Path) -> None:
    for start in ("2026-05-14T21:00:00Z", "2026-05-14T21:10:00Z"):
        card.add_pass("2026-05-14", start, start.replace(":00Z", ":02Z"), animal=[True, True])
    season_dir = tmp_path / "season"
    season = import_card(card.root, season_dir)
    labels = LabelStore(season_dir / "labels.csv")
    for picture in season.pictures:
        labels.set_group(picture.name, "frog", "Ann")
    counts = passes_per_survey_day(season, labels)
    assert [(c.name, c.passes) for c in counts] == [("frog", 2)]


# spec: f746b277
def test_a_season_is_exported_with_its_place(placed_card: CardBuilder, tmp_path: Path) -> None:
    out = _export(_season(placed_card, tmp_path))
    (deployment,) = _rows(out / "deployments.csv")
    assert (float(deployment["latitude"]), float(deployment["longitude"])) == (49.4521, 7.7541)
    package = json.loads((out / "datapackage.json").read_text())
    assert package["spatial"] == {"type": "Point", "coordinates": [7.7541, 49.4521]}


# spec: 2f5cb71e
def test_a_season_without_coordinates_is_not_exported(
    card: CardBuilder, tmp_path: Path, capsys
) -> None:
    season_dir = _season(card, tmp_path)
    with pytest.raises(ExportError, match="no latitude and longitude"):
        _export(season_dir)
    assert not (season_dir / "datapackage.json").exists()
    args = ["export", str(season_dir), "--project", "Fence A", "--contact", "Ann"]
    assert main(args) == 1
    assert "no latitude and longitude" in capsys.readouterr().err


# spec: dd89b648
def test_a_season_is_exported_with_its_placement(placed_card: CardBuilder, tmp_path: Path) -> None:
    out = _export(_season(placed_card, tmp_path))
    (deployment,) = _rows(out / "deployments.csv")
    assert deployment["deploymentTags"] == "placement:end|sideA:pond side"
    assert "at its end" in deployment["deploymentComments"]


# spec: c6aae0b1
def test_a_sorted_pass_is_exported(placed_card: CardBuilder, tmp_path: Path) -> None:
    out = _export(_season(placed_card, tmp_path))
    rows = {r["eventID"]: r for r in _rows(out / "observations.csv")}
    sorted_pass = rows["ECT_0A1B2C-2026-05-14-1"]
    assert sorted_pass["observationType"] == "animal"
    assert sorted_pass["scientificName"] == "Lacerta agilis"
    assert sorted_pass["observationTags"] == "group:lizard"
    assert sorted_pass["classificationMethod"] == "human"
    assert "snake" not in json.dumps(sorted_pass)


# spec: 3267db9c
def test_an_unsorted_pass_is_exported(placed_card: CardBuilder, tmp_path: Path) -> None:
    out = _export(_season(placed_card, tmp_path))
    rows = {r["eventID"]: r for r in _rows(out / "observations.csv")}
    unsorted = rows["ECT_0A1B2C-2026-05-14-2"]
    assert unsorted["observationType"] == "animal"
    assert unsorted["observationTags"] == "modelType:snake"
    assert unsorted["classificationMethod"] == "machine"
    assert float(unsorted["classificationProbability"]) == 0.8
    assert unsorted["classifiedBy"] == "trap model m1.0.0"


def test_an_exported_package_passes_the_camtrap_dp_checks(
    placed_card: CardBuilder, tmp_path: Path
) -> None:
    out = _export(_season(placed_card, tmp_path))
    assert camtrap_dp_problems(out) == []

    # Each media row names its picture in the season's card copy, timed from its pass.
    media = _rows(out / "media.csv")
    assert len(media) == 5
    assert media[0]["filePath"] == "card/pictures/2026-05-14/ECT_0A1B2C-2026-05-14-1_1.jpg"
    assert all((out / m["filePath"]).is_file() for m in media)
    assert [m["timestamp"] for m in media[:2]] == ["2026-05-14T21:05:09Z", "2026-05-14T21:05:09Z"]
    assert media[1]["mediaComments"] == "time estimated: the pass's start plus 0.5 s"
    observations = {r["eventID"]: r for r in _rows(out / "observations.csv")}
    assert observations["ECT_0A1B2C-2026-05-14-3"]["observationType"] == "blank"
    assert observations["ECT_0A1B2C-2026-05-14-3"]["classificationMethod"] == "human"
    assert observations["ECT_0A1B2C-2026-05-15-1"]["observationTags"] == "group:toad"


def test_the_export_command(placed_card: CardBuilder, tmp_path: Path, capsys) -> None:
    season_dir = _season(placed_card, tmp_path)
    args = ["export", str(season_dir), "--project", "Fence survey 2026", "--contact", "Ann Smith"]
    assert main(args) == 0
    assert "datapackage.json" in capsys.readouterr().out
    package = json.loads((season_dir / "datapackage.json").read_text())
    assert package["project"]["title"] == "Fence survey 2026"
    assert package["contributors"] == [{"title": "Ann Smith", "role": "contact"}]
    assert camtrap_dp_problems(season_dir) == []
    # The project and contact are required.
    with pytest.raises(SystemExit):
        main(["export", str(season_dir), "--project", "Fence survey 2026"])


def test_the_checks_catch_a_broken_package(placed_card: CardBuilder, tmp_path: Path) -> None:
    out = _export(_season(placed_card, tmp_path))
    package = json.loads((out / "datapackage.json").read_text())
    del package["project"]["samplingDesign"]
    (out / "datapackage.json").write_text(json.dumps(package))
    text = (out / "observations.csv").read_text()
    (out / "observations.csv").write_text(text.replace(",event,animal,", ",event,lizard,", 1))
    problems = camtrap_dp_problems(out)
    assert any("samplingDesign" in p for p in problems)
    assert any("observations" in p for p in problems)
