"""Card copies for the tests, written in the format the trap's firmware writes."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

PASS_HEADER = (
    "pass_id,start_utc,end_utc,direction,heights_a,heights_b,noticed_by,pictures,"
    "dropped_empty,judged_empty,pilot,model_type,model_confidence,model_version\n"
)


def floor_picture(path: Path, animal: bool, shade: int = 128) -> None:
    """A small grey picture of the passage floor, with a dark animal-shaped blob if asked."""
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("L", (160, 120), shade)
    if animal:
        ImageDraw.Draw(image).ellipse((50, 50, 110, 70), fill=30)
    image.save(path, "JPEG", quality=90)


@dataclass
class CardBuilder:
    """Writes a card copy one pass at a time."""

    root: Path
    trap_id: str = "ECT_0A1B2C"
    settings: str = ""  # more trap.cfg lines
    _rows: dict[str, list[str]] = field(default_factory=dict)
    _numbers: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "trap.cfg").write_text(
            f"trap_id={self.trap_id}\nutc_offset_min=60\n{self.settings}"
        )

    def add_pass(
        self,
        day: str,
        start: str,
        end: str,
        direction: str = "AtoB",
        heights_a: str = "lowest",
        heights_b: str = "lowest",
        noticed_by: str = "lasers",
        animal: list[bool] | None = None,
        dropped_empty: int = 0,
        judged_empty: list[int] | None = None,
        pilot: bool = False,
        model: tuple[str, float, str] | None = None,
    ) -> str:
        """Adds a pass with one picture per entry of animal, and the model's type, confidence
        and version when model is given; returns its pass_id."""
        animal = [True] if animal is None else animal
        number = self._numbers.get(day, 0) + 1
        self._numbers[day] = number
        pass_id = f"{self.trap_id}-{day}-{number}"
        names = [f"{pass_id}_{n}.jpg" for n in range(1, len(animal) + 1)]
        for name, has_animal in zip(names, animal):
            floor_picture(self.root / "pictures" / day / name, has_animal)
        judged = [names[i - 1] for i in (judged_empty or [])]
        model_columns = f"{model[0]},{model[1]:.2f},{model[2]}" if model else ",,"
        self._rows.setdefault(day, []).append(
            f"{pass_id},{start},{end},{direction},{heights_a},{heights_b},{noticed_by},"
            f"{';'.join(names)},{dropped_empty},{';'.join(judged)},{str(pilot).lower()},"
            f"{model_columns}\n"
        )
        self._write_pass_file(day)
        return pass_id

    def add_empty_view(self, day: str, hhmm: str = "1200", shade: int = 128) -> Path:
        path = self.root / "pictures" / day / f"empty_{hhmm}.jpg"
        floor_picture(path, animal=False, shade=shade)
        return path

    def add_fault(self, line: str) -> None:
        path = self.root / "faults.csv"
        if not path.exists():
            path.write_text("time_utc,fault,detail\n")
        with path.open("a") as f:
            f.write(line)

    def add_summary(self, line: str) -> None:
        path = self.root / "state" / "summaries.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as f:
            f.write(line)

    def _write_pass_file(self, day: str) -> None:
        path = self.root / "passes" / f"{day}.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(PASS_HEADER + "".join(self._rows[day]))


@pytest.fixture
def card(tmp_path: Path) -> CardBuilder:
    return CardBuilder(tmp_path / "card")


SUMMARY_LINE = (
    '{"datetime":"2026-05-14T10:00:00Z","nodeId":"ECT_0A1B2C","seqNum":12,'
    '"sensorPresent":0,"qualityFlags":0,"configVersion":1,"batVoltage":3.98,'
    '"airTemp":17.50,"latitude":null,"longitude":null,"trapKind":"state","trapPasses":143,'
    '"trapFreeMB":98112,"trapViewClear":true}\n'
)
