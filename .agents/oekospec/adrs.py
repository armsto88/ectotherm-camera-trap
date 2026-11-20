"""Reading proposed and accepted ADRs."""

import re
from dataclasses import dataclass
from datetime import date

ACCEPTED = re.compile(r"(\d{4}-\d{2}-\d{2})-(.+)")
LIST = re.compile(r"(\w+):\s*\[(.*)\]\s*")


@dataclass
class Adr:
    """A proposed or accepted ADR; accepted ones carry the date of their name."""

    slug: str
    date: date | None
    title: str | None
    areas: list[str]
    supersedes: list[str]  # names of accepted ADRs
    sections: dict[str, int]  # heading → line
    path: str


def parse_adr(path: str, text: str) -> Adr:
    """Read an ADR's front matter, title and section headings."""
    name = path.rsplit("/", 1)[-1].removesuffix(".md")
    slug, day = name, None
    if path.startswith("docs/adr/") and (match := ACCEPTED.fullmatch(name)):
        try:
            slug, day = match[2], date.fromisoformat(match[1])
        except ValueError:
            pass
    lines = text.splitlines()
    front: dict[str, list[str]] = {}
    start = 0
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                start = index + 1
                break
            if match := LIST.fullmatch(line):
                front[match[1]] = [item.strip() for item in match[2].split(",") if item.strip()]
    title = None
    sections: dict[str, int] = {}
    fenced = False
    for number, line in enumerate(lines[start:], start + 1):
        if line.startswith("```"):
            fenced = not fenced
        elif fenced:
            continue
        elif line.startswith("# ") and title is None and not sections:
            title = line[2:].strip()
        elif line.startswith("## "):
            sections.setdefault(line[3:].strip(), number)
    return Adr(
        slug=slug,
        date=day,
        title=title,
        areas=front.get("areas", []),
        supersedes=front.get("supersedes", []),
        sections=sections,
        path=path,
    )


def adr_name(adr: Adr) -> str:
    """The name of an accepted ADR, `<date>-<slug>`, as `supersedes` and the index use it."""
    return f"{adr.date.isoformat()}-{adr.slug}" if adr.date else adr.slug
