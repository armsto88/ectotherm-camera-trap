"""Exporting a season as a Camera Trap Data Package (Camtrap DP 1.0.1).

The package is written into the season folder, next to card/, since Camtrap DP names a picture
only by a path inside the package's folder or by a web address: each picture is named as
card/pictures/<day>/<file>, and nothing is copied. One deployment per trap season, placed at the
coordinates in the card's trap.cfg and tagged with its placement and side A; one media row per
picture of a pass; and one event-level observation per pass and animal shown. People's groups
and names are classified by a person: a species name goes into scientificName, the broad group
into the tag group:<group>. A pass nobody has sorted takes the model type of the trap, classified
by machine with the model version and how sure it was, in the tag modelType:<type>.
"""

from __future__ import annotations

import csv
import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .labels import LabelStore
from .model import PassRecord, Picture, Season

VERSION = "1.0.1"
BASE = f"https://raw.githubusercontent.com/tdwg/camtrap-dp/{VERSION}"
PROFILE = f"{BASE}/camtrap-dp-profile.json"

DEPLOYMENT_FIELDS = [
    "deploymentID", "locationID", "locationName", "latitude", "longitude",
    "coordinateUncertainty", "deploymentStart", "deploymentEnd", "setupBy", "cameraID",
    "cameraModel", "cameraDelay", "cameraHeight", "cameraDepth", "cameraTilt", "cameraHeading",
    "detectionDistance", "timestampIssues", "baitUse", "featureType", "habitat",
    "deploymentGroups", "deploymentTags", "deploymentComments",
]  # fmt: skip
MEDIA_FIELDS = [
    "mediaID", "deploymentID", "captureMethod", "timestamp", "filePath", "filePublic",
    "fileName", "fileMediatype", "exifData", "favorite", "mediaComments",
]  # fmt: skip
OBSERVATION_FIELDS = [
    "observationID", "deploymentID", "mediaID", "eventID", "eventStart", "eventEnd",
    "observationLevel", "observationType", "cameraSetupType", "scientificName", "count",
    "lifeStage", "sex", "behavior", "individualID", "individualPositionRadius",
    "individualPositionAngle", "individualSpeed", "bboxX", "bboxY", "bboxWidth", "bboxHeight",
    "classificationMethod", "classifiedBy", "classificationTimestamp",
    "classificationProbability", "observationTags", "observationComments",
]  # fmt: skip

DIRECTION_TEXT = {
    "AtoB": "from side A to side B",
    "BtoA": "from side B to side A",
    "backA": "entered from side A and turned back",
    "backB": "entered from side B and turned back",
    "unknown": "direction unknown (noticed by the PIR sensor alone)",
}


class ExportError(Exception):
    """The season cannot be exported, such as without the trap's coordinates."""


def _time(t: datetime) -> str:
    return t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def export_camtrap_dp(season: Season, labels: LabelStore, *, project: str, contact: str) -> None:
    """Writes datapackage.json, deployments.csv, media.csv and observations.csv into the season
    folder, next to card/, with the project title and contact, the placement and side A in the
    deployment; people's labels as classified by a person, the model type of an unsorted pass
    as classified by machine; raises ExportError when the card's trap.cfg holds no
    coordinates."""
    coordinates = season.coordinates
    if coordinates is None:
        raise ExportError(
            "the card's trap.cfg holds no latitude and longitude; the export needs the trap's "
            "place, which is entered in trap.cfg when the trap is set up"
        )
    times = [t for r in season.passes for t in (r.start_utc, r.end_utc)]
    times += [f["time_utc"] for f in season.faults]
    if not times:
        raise ExportError("the card holds no passes to export")
    start, end = min(times), max(times)
    deployment_id = f"{season.trap_id}-{start:%Y-%m-%d}"

    if not project.strip() or not contact.strip():
        raise ExportError("the export needs the project's title and a contact person")
    out = season.card.parent
    tags = [f"placement:{season.placement}"]
    if season.side_a:
        tags.append(f"sideA:{season.side_a}")
    _write(
        out / "deployments.csv",
        DEPLOYMENT_FIELDS,
        [
            {
                "deploymentID": deployment_id,
                "locationID": season.trap_id,
                "locationName": season.trap_id,
                "latitude": coordinates[0],
                "longitude": coordinates[1],
                "deploymentStart": _time(start),
                "deploymentEnd": _time(end),
                "cameraID": season.trap_id,
                "cameraModel": "ectotherm passage camera trap",
                "timestampIssues": "false",
                "baitUse": "false",
                "deploymentTags": "|".join(tags),
                "deploymentComments": "A passage trap set into a drift fence "
                + ("at its end" if season.placement == "end" else "in its line")
                + "; directions are given by side A and side B of the fence.",
            }
        ],
    )

    media = []
    for record in season.passes:
        for index, picture in enumerate(record.pictures):
            media.append(_media_row(record, index, picture, deployment_id, out))
    _write(out / "media.csv", MEDIA_FIELDS, media)

    observations = []
    for record in season.passes:
        observations.extend(_observations(record, labels, deployment_id))
    _write(out / "observations.csv", OBSERVATION_FIELDS, observations)

    names = sorted({str(o["scientificName"]) for o in observations if o.get("scientificName")})
    package = {
        "name": deployment_id.lower(),
        "title": f"Ectotherm camera trap {season.trap_id}, {start:%Y-%m-%d} to {end:%Y-%m-%d}",
        "profile": PROFILE,
        "created": _time(datetime.now(UTC)),
        "contributors": [{"title": contact, "role": "contact"}],
        "project": {
            "title": project,
            "samplingDesign": "targeted",
            "captureMethod": ["activityDetection"],
            "individualAnimals": False,
            "observationLevel": ["event"],
        },
        "spatial": {"type": "Point", "coordinates": [coordinates[1], coordinates[0]]},
        "temporal": {"start": f"{start:%Y-%m-%d}", "end": f"{end:%Y-%m-%d}"},
        "taxonomic": [{"scientificName": name} for name in names],
        "resources": [
            {
                "name": name,
                "path": f"{name}.csv",
                "profile": "tabular-data-resource",
                "format": "csv",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": f"{BASE}/{name}-table-schema.json",
            }
            for name in ("deployments", "media", "observations")
        ],
    }
    (out / "datapackage.json").write_text(json.dumps(package, indent=2) + "\n")


def _media_row(
    record: PassRecord, index: int, picture: Picture, deployment_id: str, out: Path
) -> dict[str, object]:
    # Pictures follow each other about half a second apart; their own times are not recorded.
    offset = index / 2
    timestamp = record.start_utc + timedelta(seconds=int(offset))
    return {
        "mediaID": picture.file.stem,
        "deploymentID": deployment_id,
        "captureMethod": "activityDetection",
        "timestamp": _time(timestamp),
        "filePath": Path(os.path.relpath(picture.file, out)).as_posix(),
        "filePublic": "false",
        "fileName": picture.name,
        "fileMediatype": "image/jpeg",
        "mediaComments": f"time estimated: the pass's start plus {offset:g} s",
    }


def _observations(
    record: PassRecord, labels: LabelStore, deployment_id: str
) -> list[dict[str, object]]:
    shown = []
    person_empty = False
    for picture in record.pictures:
        mark = labels.empty(picture.name)
        person_empty = person_empty or mark is not None
        if not (mark if mark is not None else picture.empty):
            shown.append(picture)
    # Each animal a person named or grouped, once per pass.
    animals: list[tuple[str | None, str | None]] = []
    unclear = waiting = False
    for picture in shown:
        name, group = labels.name(picture.name), labels.group(picture.name)
        if name or group:
            if (name, group) not in animals:
                animals.append((name, group))
        elif labels.unclear(picture.name):
            unclear = True
        else:
            waiting = True

    base = {
        "deploymentID": deployment_id,
        "eventID": record.pass_id,
        "eventStart": _time(record.start_utc),
        "eventEnd": _time(record.end_utc),
        "observationLevel": "event",
        "observationComments": f"pass {DIRECTION_TEXT[record.direction]}",
    }
    rows: list[dict[str, object]] = []
    if animals:
        for name, group in animals:
            rows.append(
                base
                | {
                    "observationType": "animal",
                    "scientificName": name or "",
                    "classificationMethod": "human",
                    "observationTags": f"group:{group}" if group else "",
                }
            )
    elif not shown:
        rows.append(
            base
            | {
                "observationType": "blank",
                "classificationMethod": "human" if person_empty else "machine",
                "classifiedBy": "" if person_empty else "trapsort, compared with the empty view",
            }
        )
    elif unclear and not waiting:
        rows.append(base | {"observationType": "unknown", "classificationMethod": "human"})
    elif record.model_type:
        rows.append(
            base
            | {
                "observationType": "blank" if record.model_type == "empty" else "animal",
                "classificationMethod": "machine",
                "classifiedBy": f"trap model {record.model_version}",
                "classificationProbability": record.model_confidence,
                "observationTags": f"modelType:{record.model_type}",
            }
        )
    else:
        rows.append(base | {"observationType": "unclassified"})
    for number, row in enumerate(rows, start=1):
        row["observationID"] = f"{record.pass_id}-{number}"
    return rows


def _write(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fields, lineterminator="\n", restval="")
        writer.writeheader()
        writer.writerows(rows)
