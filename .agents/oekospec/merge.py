"""Applying a change's deltas and proposed ADRs to the project specs and ADRs, in memory."""

from datetime import date

from adrs import Adr, adr_name, parse_adr
from index import build_indexes
from model import Plan, Problem, Texts
from specs import BASE_COMMENT, Delta, Scenario, Spec, base_of, parse_delta, parse_spec
from validate import delta_texts, folder_texts


def merge_spec(spec: Spec | None, delta: Delta, spec_text: str) -> str | list[Problem]:
    """New text of one project spec: added appended, modified replaced in place, removed
    deleted; refuses stale bases, missing requirements and taken names."""
    if spec is None:
        head = f"# {delta.name}\n\n## Purpose\n{delta.purpose}\n\n"
        if delta.terms:
            head += f"## Terms\n{delta.terms}\n\n"
        return _join(head + "## Requirements\n", [r.text for r in delta.added])
    current = {requirement.name: requirement for requirement in spec.requirements}
    problems = [
        Problem(
            delta.path,
            requirement.line,
            f'requirement "{requirement.name}" already exists in {spec.path}',
        )
        for requirement in delta.added
        if requirement.name in current
    ]
    change = delta.path.split("/")[2]
    for requirement in delta.modified + delta.removed:
        if requirement.name not in current:
            problems.append(
                Problem(
                    delta.path,
                    requirement.line,
                    f'requirement "{requirement.name}" is not in {spec.path}',
                )
            )
        elif requirement.base != base_of(current[requirement.name].text):
            problems.append(
                Problem(
                    delta.path,
                    requirement.line,
                    f'requirement "{requirement.name}" in {spec.path} has changed '
                    "since its base was taken; see what changed with "
                    f"`git log -p {spec.path}`, carry what still applies into "
                    "the delta, then run "
                    f"`python3 .agents/oekospec refresh {change}`",
                )
            )
    if problems:
        return problems
    modified = {requirement.name: _without_base(requirement.text) for requirement in delta.modified}
    removed = {requirement.name for requirement in delta.removed}
    blocks = [
        modified.get(requirement.name, requirement.text)
        for requirement in spec.requirements
        if requirement.name not in removed
    ]
    blocks += [requirement.text for requirement in delta.added]
    return _join(_head(spec, spec_text), blocks)


def _join(head: str, blocks: list[str]) -> str:
    """A spec from its text before the first requirement and its requirement blocks."""
    parts = [head.rstrip("\n") + "\n"]
    parts += [block.rstrip("\n") + "\n" for block in blocks]
    return "\n".join(parts)


def _head(spec: Spec, spec_text: str) -> str:
    """The text of a spec before its first requirement."""
    if not spec.requirements:
        return spec_text
    return "".join(spec_text.splitlines(keepends=True)[: spec.requirements[0].line - 1])


def _without_base(block: str) -> str:
    """A requirement block with the base comment left out of its heading."""
    heading, newline, rest = block.partition("\n")
    return BASE_COMMENT.sub("", heading) + newline + rest


def merge_adrs(
    proposed: list[Adr], texts: Texts, accepted: dict[str, Adr], today: date
) -> Texts | list[Problem]:
    """Copies of the proposed ADRs as accepted ones named `<today>-<slug>.md`, left in the
    change too; refuses taken names and ADRs that are missing or already superseded."""
    problems = []
    write = {}
    successor = {old: name for name, adr in accepted.items() for old in adr.supersedes}
    claims: dict[str, list[Adr]] = {}
    for adr in proposed:
        name = f"{today.isoformat()}-{adr.slug}"
        if name in accepted:
            problems.append(Problem(adr.path, None, f"ADR {name} already exists in docs/adr"))
        for old in adr.supersedes:
            if old not in accepted:
                problems.append(
                    Problem(adr.path, None, f"supersedes {old}, which is not in docs/adr")
                )
            elif old in successor:
                problems.append(
                    Problem(
                        adr.path,
                        None,
                        f"supersedes {old}, which is already superseded by {successor[old]}",
                    )
                )
            claims.setdefault(old, []).append(adr)
        write[f"docs/adr/{name}.md"] = texts[adr.path]
    for old, adrs in claims.items():
        if len(adrs) > 1:
            names = " and ".join(adr.slug for adr in adrs)
            problems.append(
                Problem(
                    adrs[-1].path,
                    None,
                    f"{old} can be superseded only once, but {names} both supersede it",
                )
            )
    return problems or write


def merge(change: str, texts: Texts, today: date) -> Plan | list[Problem]:
    """All spec and ADR changes of a change together, both indexes rebuilt; refuses scenario
    IDs taken elsewhere. The plan has no move yet."""
    problems: list[Problem] = []
    write: Texts = {}
    deltas = [parse_delta(path, text)[0] for path, text in delta_texts(change, texts).items()]
    for delta in deltas:
        target = f"docs/specs/{delta.name}.md"
        spec = parse_spec(target, texts[target])[0] if target in texts else None
        result = merge_spec(spec, delta, texts.get(target, ""))
        if isinstance(result, list):
            problems += result
        else:
            write[target] = result
    if not problems:
        problems += _taken_ids(deltas, folder_texts("docs/specs", texts) | write, write)
    proposed = [
        parse_adr(path, text)
        for path, text in folder_texts(f"docs/changes/{change}/adr", texts).items()
    ]
    accepted = {
        adr_name(adr): adr
        for adr in (parse_adr(path, text) for path, text in folder_texts("docs/adr", texts).items())
    }
    merged_adrs = merge_adrs(proposed, texts, accepted, today)
    if isinstance(merged_adrs, list):
        problems += merged_adrs
    else:
        write |= merged_adrs
    if problems:
        return problems
    for path, text in build_indexes(texts | write).items():
        if texts.get(path) != text:
            write[path] = text
    return Plan(write=write, move=None)


def _taken_ids(deltas: list[Delta], specs: Texts, merged: Texts) -> list[Problem]:
    """IDs that the merged specs share with another scenario in the project specs."""
    uses: dict[str, list[tuple[str, Scenario]]] = {}
    for path, text in specs.items():
        for requirement in parse_spec(path, text)[0].requirements:
            for scenario in requirement.scenarios:
                if scenario.id:
                    uses.setdefault(scenario.id, []).append((path, scenario))
    in_delta = {
        scenario.id: (delta.path, scenario.line)
        for delta in deltas
        for requirement in delta.added + delta.modified
        for scenario in requirement.scenarios
        if scenario.id
    }
    problems = []
    for id, found in uses.items():
        if len(found) < 2 or not any(path in merged for path, _ in found):
            continue
        names = " and ".join(
            f'scenario "{scenario.name}" ({path}:{scenario.line})' for path, scenario in found
        )
        path, line = in_delta.get(id, (found[0][0], None))
        problems.append(Problem(path, line, f"ID {id} is used by {names}"))
    return problems
