"""Reading project specs and deltas into requirements and scenarios."""

import hashlib
import itertools
import re
from dataclasses import dataclass, field

from model import Problem

REQUIREMENT = re.compile(r"### Requirement: (?P<name>.*?)(?:\s*<!-- base: (?P<base>.*?) -->)?\s*")
SCENARIO = re.compile(r"#### Scenario: (?P<name>.*?)(?:\s*<!-- id: (?P<id>.*?) -->)?\s*")
STEP = re.compile(r"- \*\*(Given|When|Then|And)\*\* (.*)")
REASON = re.compile(r"\*\*Reason:\*\*(.*)")
HEX8 = re.compile(r"[0-9a-f]{8}")
BASE_COMMENT = re.compile(r"\s*<!-- base: .*? -->")
DELTA_SECTIONS = {
    "ADDED Requirements": "added",
    "MODIFIED Requirements": "modified",
    "REMOVED Requirements": "removed",
}


@dataclass
class Scenario:
    """One scenario with its ID and steps."""

    name: str
    id: str | None
    steps: list[str]  # one per Given, When, Then and And line
    line: int


@dataclass
class Requirement:
    """One requirement block, from its heading to the next requirement or section heading."""

    name: str
    base: str | None  # only in deltas
    reason: str | None  # only for removed requirements
    scenarios: list[Scenario]
    text: str  # the block exactly as written
    line: int


@dataclass
class Spec:
    """A project spec in docs/specs."""

    path: str
    name: str
    purpose: str
    terms: str | None
    requirements: list[Requirement]


@dataclass
class Delta:
    """A spec delta in a change; Purpose and Terms only when it creates a new spec."""

    path: str
    name: str
    purpose: str | None
    terms: str | None
    added: list[Requirement]
    modified: list[Requirement]
    removed: list[Requirement]


@dataclass
class _Section:
    title: str
    line: int
    lines: list[str] = field(default_factory=list)  # text lines, for Purpose and Terms
    requirements: list[Requirement] = field(default_factory=list)


def parse_spec(path: str, text: str) -> tuple[Spec, list[Problem]]:
    """Read a project spec; problems name what doesn't fit the format."""
    sections, problems = _read(path, text, {"Purpose", "Terms", "Requirements"})
    for title in ("Purpose", "Requirements"):
        if title not in sections:
            problems.append(Problem(path, None, f"missing section {title}"))
    spec = Spec(
        path=path,
        name=spec_name(path),
        purpose=_text(sections.get("Purpose")) or "",
        terms=_text(sections.get("Terms")),
        requirements=sections["Requirements"].requirements if "Requirements" in sections else [],
    )
    return spec, problems


def parse_delta(path: str, text: str) -> tuple[Delta, list[Problem]]:
    """Read a delta; problems name what doesn't fit the format."""
    sections, problems = _read(path, text, {"Purpose", "Terms", *DELTA_SECTIONS})
    order = ["Purpose", "Terms", *DELTA_SECTIONS]
    found = [title for title in order if title in sections]
    for before, after in itertools.pairwise(found):
        if sections[after].line < sections[before].line:
            problems.append(
                Problem(path, sections[after].line, f"section {after} must come after {before}")
            )
    lists = {
        key: sections[title].requirements if title in sections else []
        for title, key in DELTA_SECTIONS.items()
    }
    delta = Delta(
        path=path,
        name=spec_name(path),
        purpose=_text(sections.get("Purpose")),
        terms=_text(sections.get("Terms")),
        **lists,
    )
    return delta, problems


def spec_name(path: str) -> str:
    """The name of a spec or delta: its file name without `.md`."""
    return path.rsplit("/", 1)[-1].removesuffix(".md")


def base_of(block: str) -> str:
    """Fingerprint of a requirement block: 8 hex characters, blind to trailing whitespace,
    blank lines and the base comment."""
    lines = block.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if lines:
        lines[0] = BASE_COMMENT.sub("", lines[0])
    kept = [line.rstrip() for line in lines if line.strip()]
    return hashlib.sha256("\n".join(kept).encode("utf-8")).hexdigest()[:8]


def _text(section: _Section | None) -> str | None:
    if section is None:
        return None
    return "\n".join(section.lines).strip()


def _read(path: str, text: str, allowed: set[str]) -> tuple[dict[str, _Section], list[Problem]]:
    """Split a spec or delta into its sections, with the requirement blocks of each."""
    problems: list[Problem] = []
    sections: dict[str, _Section] = {}
    lines = text.splitlines(keepends=True)
    title_seen = False
    section: _Section | None = None
    block: list[str] = []  # lines of the open requirement block
    block_start = 0
    fenced = False

    def close_block(section: _Section) -> None:
        if block:
            section.requirements.append(_requirement(path, "".join(block), block_start, problems))
            block.clear()

    for number, raw in enumerate(lines, 1):
        line = raw.rstrip("\r\n")
        if line.startswith("```"):
            fenced = not fenced
        heading = not fenced and line.startswith("#")
        if heading and line.startswith("## "):
            if section is not None:
                close_block(section)
            title = line[3:].strip()
            if title not in allowed:
                problems.append(Problem(path, number, f"unknown section {title}"))
                section = _Section(title, number)
            elif title in sections:
                problems.append(Problem(path, number, f"section {title} appears twice"))
                section = sections[title]
            else:
                section = sections[title] = _Section(title, number)
            continue
        if heading and line.startswith("# "):
            expected = f"# {spec_name(path)}"
            if title_seen or section is not None:
                problems.append(Problem(path, number, "title must be the first line"))
            elif line.strip() != expected:
                problems.append(Problem(path, number, f"title must be {expected}"))
            title_seen = True
            continue
        if heading and line.startswith("### "):
            if section is None or section.title in ("Purpose", "Terms"):
                problems.append(Problem(path, number, f"heading outside the format: {line}"))
                continue
            close_block(section)
            block_start = number
            block.append(raw)
            continue
        if block:
            block.append(raw)
        elif section is not None and section.title in ("Purpose", "Terms"):
            section.lines.append(line)
        elif line.strip() and section is not None:
            problems.append(
                Problem(path, number, f"text outside a requirement in section {section.title}")
            )
        elif line.strip():
            problems.append(Problem(path, number, "text before the first section"))
    if section is not None:
        close_block(section)
    if not title_seen:
        problems.append(Problem(path, 1, f"missing title # {spec_name(path)}"))
    return sections, problems


def _requirement(path: str, text: str, start: int, problems: list[Problem]) -> Requirement:
    """Read one requirement block, which starts with a level-3 heading."""
    lines = text.splitlines()
    match = REQUIREMENT.fullmatch(lines[0])
    if match is None:
        problems.append(Problem(path, start, f"heading outside the format: {lines[0]}"))
        name, base = lines[0].removeprefix("### ").strip(), None
    else:
        name, base = match["name"], match["base"]
        if base is not None and not HEX8.fullmatch(base):
            problems.append(Problem(path, start, f'requirement "{name}" has a malformed base'))
            base = None
    reason = None
    scenarios: list[Scenario] = []
    fenced = False
    for offset, line in enumerate(lines[1:], 1):
        number = start + offset
        if line.startswith("```"):
            fenced = not fenced
        if fenced or line.startswith("```"):
            continue
        if line.startswith("#"):
            scenario = SCENARIO.fullmatch(line)
            if scenario is None:
                problems.append(Problem(path, number, f"heading outside the format: {line}"))
                continue
            id = scenario["id"]
            if id is not None and not HEX8.fullmatch(id):
                problems.append(
                    Problem(path, number, f'scenario "{scenario["name"]}" has a malformed ID')
                )
                id = None
            scenarios.append(Scenario(scenario["name"], id, [], number))
            continue
        if not scenarios:
            found = REASON.fullmatch(line)
            if found is not None:
                reason = found[1].strip()
            continue
        step = STEP.fullmatch(line)
        current = scenarios[-1]
        if step is not None:
            current.steps.append(f"{step[1]} {step[2]}")
        elif line.startswith("  ") and current.steps:
            current.steps[-1] += " " + line.strip()
        elif line.strip():
            problems.append(
                Problem(path, number, f'scenario "{current.name}" holds a line that is not a step')
            )
    return Requirement(
        name=name, base=base, reason=reason, scenarios=scenarios, text=text, line=start
    )
