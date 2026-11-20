"""What `ids`, `modify`, `remove` and `refresh` do to the text of a delta."""

import secrets

from model import Problem
from specs import DELTA_SECTIONS, SCENARIO, base_of, parse_delta, parse_spec, spec_name


def new_id(taken: set[str]) -> str:
    """A random 8 hex character ID not in `taken`."""
    while (id := secrets.token_hex(4)) in taken:
        pass
    return id


def fill_ids(text: str, taken: set[str]) -> str:
    """The delta with a new ID on every scenario without one; existing IDs unchanged."""
    taken = set(taken)
    lines = []
    fenced = False
    for raw in text.splitlines(keepends=True):
        line = raw.rstrip("\r\n")
        if line.startswith("```"):
            fenced = not fenced
        match = None if fenced else SCENARIO.fullmatch(line)
        if match and "<!--" not in line:
            id = new_id(taken)
            taken.add(id)
            raw = f"{line.rstrip()} <!-- id: {id} -->{raw[len(line) :]}"
        lines.append(raw)
    return "".join(lines)


def refresh_bases(delta_path: str, delta_text: str, spec_text: str) -> str | list[Problem]:
    """The delta with the current base on every modified and removed requirement."""
    spec_path = f"docs/specs/{spec_name(delta_path)}.md"
    current = {r.name: r for r in parse_spec(spec_path, spec_text)[0].requirements}
    delta = parse_delta(delta_path, delta_text)[0]
    lines = delta_text.splitlines(keepends=True)
    problems = []
    for requirement in delta.modified + delta.removed:
        if requirement.name not in current:
            problems.append(
                Problem(
                    delta_path,
                    requirement.line,
                    f'requirement "{requirement.name}" is not in {spec_path}',
                )
            )
            continue
        line = lines[requirement.line - 1]
        lines[requirement.line - 1] = (
            _heading(requirement.name, base_of(current[requirement.name].text))
            + line[len(line.rstrip("\r\n")) :]
        )
    return problems or "".join(lines)


def take_modified(
    delta_path: str, spec_text: str, delta_text: str | None, requirement: str
) -> str | list[Problem]:
    """The delta with the whole requirement block copied under modified requirements, with
    its current base; creates the delta if `delta_text` is None."""
    return _take(delta_path, spec_text, delta_text, requirement, "MODIFIED Requirements")


def take_removed(
    delta_path: str, spec_text: str, delta_text: str | None, requirement: str
) -> str | list[Problem]:
    """The delta with the requirement's heading under removed requirements, with its current
    base and an empty reason."""
    return _take(delta_path, spec_text, delta_text, requirement, "REMOVED Requirements")


def _take(
    delta_path: str, spec_text: str, delta_text: str | None, name: str, section: str
) -> str | list[Problem]:
    spec_path = f"docs/specs/{spec_name(delta_path)}.md"
    current = {r.name: r for r in parse_spec(spec_path, spec_text)[0].requirements}
    if name not in current:
        return [Problem(spec_path, None, f'requirement "{name}" is not in {spec_path}')]
    if delta_text is not None:
        delta = parse_delta(delta_path, delta_text)[0]
        for title, key in DELTA_SECTIONS.items():
            if any(r.name == name for r in getattr(delta, key)):
                return [
                    Problem(
                        delta_path, None, f'requirement "{name}" is already in {title} of the delta'
                    )
                ]
    block = current[name].text
    heading = _heading(name, base_of(block))
    if section == "MODIFIED Requirements":
        block = heading + "\n" + block.split("\n", 1)[1].rstrip("\n") + "\n"
    else:
        block = heading + "\n**Reason:**\n"
    if delta_text is None:
        delta_text = f"# {spec_name(delta_path)}\n"
    return _insert(delta_text, section, block)


def _insert(text: str, section: str, block: str) -> str:
    """The delta with `block` at the end of `section`, adding the section in its place."""
    order = ["Purpose", "Terms", *DELTA_SECTIONS]
    lines = text.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    headings = []
    fenced = False
    for index, line in enumerate(lines):
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced and line.startswith("## "):
            headings.append((index, line[3:].strip()))
    found = [index for index, title in headings if title == section]
    if found:
        after = [index for index, _ in headings if index > found[0]]
        new = [block]
    else:
        after = [
            index
            for index, title in headings
            if title in order and order.index(title) > order.index(section)
        ]
        new = [f"## {section}\n", "\n", block]
    end = after[0] if after else len(lines)
    head, rest = lines[:end], lines[end:]
    while head and not head[-1].strip():
        head.pop()
    return "".join(head + ["\n"] + new + (["\n"] + rest if rest else []))


def _heading(name: str, base: str) -> str:
    return f"### Requirement: {name} <!-- base: {base} -->"
