"""Checking a change at review or archive level, from the texts of its files."""

import re

from adrs import Adr, parse_adr
from change import Entry, Proposal, parse_decisions, parse_proposal, parse_tasks
from model import Problem, Texts
from names import is_adr_name, is_name
from specs import Delta, Spec, base_of, parse_delta, parse_spec, spec_name

REQUIRED_FILES = ("proposal.md", "decisions.md", "tasks.md")
PROPOSAL_SECTIONS = (
    "Context and driving forces",
    "What changes",
    "Capabilities",
    "Open questions",
    "Out of scope",
    "References",
)
ENTRY_FIELDS = ("Date", "Step", "Decision", "Reason")
ADR_SECTIONS = ("Context", "Options considered", "Decision", "Consequences")
CODE_SPAN = re.compile(r"(`+).+?\1")
COMMENT = re.compile(r"<!--.*?-->")
LINK = re.compile(r"<[A-Za-z][A-Za-z0-9+.-]*:[^<>\s]*>|\]\(<[^<>]*>")
PLACEHOLDER = re.compile(r"<[^<>]+>")


def validate(change: str, texts: Texts, archive: bool = False) -> list[Problem]:
    """All problems of a change; `texts` holds the change folder, docs/specs and docs/adr."""
    folder = f"docs/changes/{change}"
    problems = check_files(change, texts)
    parsed = {
        spec_name(path): parse_spec(path, text)
        for path, text in folder_texts("docs/specs", texts).items()
    }
    specs = {name: spec for name, (spec, _) in parsed.items()}
    deltas = {}
    for path, text in delta_texts(change, texts).items():
        delta, found = parse_delta(path, text)
        problems += found + check_delta(delta, specs.get(delta.name)) + check_whitespace(path, text)
        if delta.name in parsed:
            problems += parsed[delta.name][1]
        deltas[delta.name] = delta
    path = f"{folder}/proposal.md"
    if path in texts:
        proposal = parse_proposal(path, texts[path])
        problems += check_proposal(path, proposal)
        problems += check_capabilities(path, proposal, list(deltas.values()), set(specs))
    problems += check_ids(deltas, specs)
    path = f"{folder}/decisions.md"
    if path in texts:
        problems += check_decisions(path, parse_decisions(path, texts[path]))
    accepted = {spec_name(path) for path in folder_texts("docs/adr", texts)}
    for path, text in folder_texts(f"{folder}/adr", texts).items():
        problems += check_adr(parse_adr(path, text), accepted) + check_whitespace(path, text)
    checked = [f"{folder}/{name}" for name in REQUIRED_FILES if f"{folder}/{name}" in texts]
    checked += [*delta_texts(change, texts), *folder_texts(f"{folder}/adr", texts)]
    for path in checked:
        problems += check_placeholders(path, texts[path])
    if archive:
        problems += check_archive_level(change, texts)
    return sorted(problems, key=lambda problem: (problem.path, problem.line or 0))


def delta_texts(change: str, texts: Texts) -> Texts:
    """The spec deltas of a change, by path."""
    return folder_texts(f"docs/changes/{change}/specs", texts)


def folder_texts(folder: str, texts: Texts) -> Texts:
    """The Markdown files directly in a folder, its generated index left out."""
    return {
        path: text
        for path, text in texts.items()
        if path.startswith(folder + "/")
        and "/" not in path[len(folder) + 1 :]
        and path != f"{folder}/index.md"
    }


def check_files(change: str, texts: Texts) -> list[Problem]:
    """Missing proposal.md, decisions.md or tasks.md."""
    folder = f"docs/changes/{change}"
    return [
        Problem(f"{folder}/{name}", None, "file is missing")
        for name in REQUIRED_FILES
        if f"{folder}/{name}" not in texts
    ]


def check_proposal(path: str, proposal: Proposal) -> list[Problem]:
    """Missing or empty sections, and an empty Capabilities without a reason."""
    problems = [
        Problem(path, None, f"missing section {title}")
        for title in PROPOSAL_SECTIONS
        if title not in proposal.sections
    ]
    for title in ("Context and driving forces", "What changes"):
        if title in proposal.sections and not proposal.sections[title][0]:
            problems.append(Problem(path, proposal.sections[title][1], f"section {title} is empty"))
    if "Capabilities" in proposal.sections and not (
        proposal.new or proposal.modified or proposal.capabilities_reason
    ):
        problems.append(
            Problem(
                path,
                proposal.sections["Capabilities"][1],
                "Capabilities lists no capability and gives no reason",
            )
        )
    return problems


def check_capabilities(
    path: str, proposal: Proposal, deltas: list[Delta], specs: set[str]
) -> list[Problem]:
    """Capabilities and spec files that don't match, New or Modified listed wrongly, and a
    spec named `index`."""
    line = proposal.sections.get("Capabilities", ("", None))[1]
    listed = proposal.new + proposal.modified
    files = {delta.name for delta in deltas}
    problems = []
    for delta in deltas:
        if delta.name == "index":
            problems.append(
                Problem(
                    delta.path,
                    None,
                    "index is a reserved name: docs/specs/index.md is the spec index",
                )
            )
        elif delta.name not in listed:
            problems.append(
                Problem(
                    delta.path, None, f"{delta.name} is not listed in the proposal's Capabilities"
                )
            )
    for name in listed:
        if name not in files:
            problems.append(Problem(path, line, f"capability {name} has no spec file"))
    for name in proposal.new:
        if name in specs:
            problems.append(
                Problem(
                    path, line, f"{name} exists in docs/specs and must be listed under Modified"
                )
            )
    for name in proposal.modified:
        if name not in specs:
            problems.append(
                Problem(path, line, f"{name} is not in docs/specs and must be listed under New")
            )
    return problems


def check_delta(delta: Delta, spec: Spec | None) -> list[Problem]:
    """Format of one delta: sections, bases, reasons, scenarios and steps, unchanged copies."""
    path = delta.path
    problems = []
    if spec is None:
        if delta.purpose is None:
            problems.append(Problem(path, None, "a delta for a new spec needs a Purpose"))
        for requirement in delta.modified + delta.removed:
            problems.append(
                Problem(
                    path,
                    requirement.line,
                    f'requirement "{requirement.name}" can only be added: '
                    f"docs/specs/{delta.name}.md does not exist",
                )
            )
    else:
        for title, text in (("Purpose", delta.purpose), ("Terms", delta.terms)):
            if text is not None:
                problems.append(
                    Problem(
                        path,
                        None,
                        f"edit the {title} in {spec.path} instead; "
                        "a delta for an existing spec holds only requirements",
                    )
                )
    if not (delta.added or delta.modified or delta.removed):
        problems.append(Problem(path, None, "delta holds no requirements"))
    for kind, requirements in (("modified", delta.modified), ("removed", delta.removed)):
        for requirement in requirements:
            if requirement.base is None:
                problems.append(
                    Problem(
                        path,
                        requirement.line,
                        f'{kind} requirement "{requirement.name}" has no base',
                    )
                )
    for requirement in delta.removed:
        if not requirement.reason:
            problems.append(
                Problem(
                    path,
                    requirement.line,
                    f'removed requirement "{requirement.name}" gives no reason',
                )
            )
    for requirement in delta.added + delta.modified:
        if not requirement.scenarios:
            problems.append(
                Problem(path, requirement.line, f'requirement "{requirement.name}" has no scenario')
            )
        for scenario in requirement.scenarios:
            keywords = {step.split(" ", 1)[0] for step in scenario.steps}
            if not {"When", "Then"} <= keywords:
                problems.append(
                    Problem(
                        path, scenario.line, f'scenario "{scenario.name}" needs a When and a Then'
                    )
                )
    for requirement in delta.modified:
        if requirement.base is not None and base_of(requirement.text) == requirement.base:
            problems.append(
                Problem(
                    path,
                    requirement.line,
                    f'modified requirement "{requirement.name}" is unchanged; '
                    "edit it or delete it from the delta",
                )
            )
    return problems


def check_ids(deltas: dict[str, Delta], specs: dict[str, Spec]) -> list[Problem]:
    """Scenarios without an ID and IDs used twice; a modified requirement may keep its IDs."""
    problems = []
    project: dict[str, list[tuple]] = {}
    for spec in specs.values():
        for requirement in spec.requirements:
            for scenario in requirement.scenarios:
                if scenario.id:
                    project.setdefault(scenario.id, []).append(
                        (spec.path, scenario, (spec.name, requirement.name))
                    )
    changed: dict[str, list[tuple]] = {}
    for delta in deltas.values():
        for kind, requirements in (("added", delta.added), ("modified", delta.modified)):
            for requirement in requirements:
                for scenario in requirement.scenarios:
                    if scenario.id is None:
                        change = delta.path.split("/")[2]
                        problems.append(
                            Problem(
                                delta.path,
                                scenario.line,
                                f'scenario "{scenario.name}" has no ID; run '
                                f"`python3 .agents/oekospec ids {change}`",
                            )
                        )
                        continue
                    keeps = (delta.name, requirement.name) if kind == "modified" else None
                    changed.setdefault(scenario.id, []).append((delta.path, scenario, keeps))
    for id, uses in changed.items():
        kept = {keeps for _, _, keeps in uses if keeps}
        others = [use for use in project.get(id, []) if use[2] not in kept] + uses
        first_path, first, _ = others[0]
        for path, scenario, _ in others[1:]:
            if path.startswith("docs/specs/") and first_path.startswith("docs/specs/"):
                continue
            problems.append(
                Problem(
                    path,
                    scenario.line,
                    f'ID {id} is used by scenario "{first.name}" '
                    f'({first_path}:{first.line}) and scenario "{scenario.name}"',
                )
            )
    return problems


def check_decisions(path: str, entries: list[Entry]) -> list[Problem]:
    """Gaps in the numbering and entries missing Date, Step, Decision or Reason."""
    problems = []
    previous = 0
    for entry in entries:
        if entry.number != previous + 1:
            if previous == 0:
                message = "entries must be numbered from 1"
            elif entry.number > previous + 1:
                message = f"gap in the numbering after entry {previous}"
            else:
                message = f"entry {entry.number} is out of order after entry {previous}"
            problems.append(Problem(path, entry.line, message))
        previous = entry.number
        for name in ENTRY_FIELDS:
            if not entry.fields.get(name):
                problems.append(Problem(path, entry.line, f"entry {entry.number} has no {name}"))
    return problems


def check_adr(adr: Adr, accepted: set[str]) -> list[Problem]:
    """Missing title or section, and superseded ADRs not in docs/adr."""
    problems = []
    if not adr.title:
        problems.append(Problem(adr.path, None, "ADR has no title"))
    for title in ADR_SECTIONS:
        if title not in adr.sections:
            problems.append(Problem(adr.path, None, f"ADR has no section {title}"))
    for name in adr.supersedes:
        if name not in accepted:
            problems.append(Problem(adr.path, None, f"supersedes {name}, which is not in docs/adr"))
    return problems


def check_placeholders(path: str, text: str) -> list[Problem]:
    """Angle-bracket text outside code, HTML comments and links, one problem per line."""
    problems = []
    fenced = False
    comment = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if comment:
            if "-->" not in line:
                continue
            line = line[line.index("-->") + 3 :]
            comment = False
        line = COMMENT.sub("", CODE_SPAN.sub("", line))
        if "<!--" in line:
            line, comment = line[: line.index("<!--")], True
        found = PLACEHOLDER.findall(LINK.sub("", line))
        if found:
            problems.append(Problem(path, number, f"fill in or delete {' '.join(found)}"))
    return problems


def check_whitespace(path: str, text: str) -> list[Problem]:
    """Trailing whitespace, tabs, carriage returns, double blank lines, a wrong file end."""
    problems = []
    lines = text.split("\n")
    for number, line in enumerate(lines[:-1], 1):
        if "\r" in line:
            problems.append(Problem(path, number, "line holds a carriage return"))
        if "\t" in line:
            problems.append(Problem(path, number, "line holds a tab"))
        if line.replace("\r", "") != line.replace("\r", "").rstrip():
            problems.append(Problem(path, number, "line ends in whitespace"))
        if number > 1 and not line.strip() and not lines[number - 2].strip():
            problems.append(Problem(path, number, "second blank line in a row"))
    if not text.endswith("\n") or text.endswith("\n\n"):
        problems.append(Problem(path, None, "file must end in exactly one newline"))
    return problems


def check_archive_level(change: str, texts: Texts) -> list[Problem]:
    """Unchecked tasks, open questions and stale bases."""
    folder = f"docs/changes/{change}"
    problems = []
    tasks = f"{folder}/tasks.md"
    if tasks in texts:
        for task in parse_tasks(tasks, texts[tasks]):
            if not task.done:
                problems.append(Problem(tasks, task.line, f"task {task.number} is not done"))
    proposal = f"{folder}/proposal.md"
    if proposal in texts:
        questions = parse_proposal(proposal, texts[proposal]).sections.get("Open questions")
        if questions and questions[0]:
            problems.append(Problem(proposal, questions[1], "Open questions is not empty"))
    for path, text in delta_texts(change, texts).items():
        spec_path = f"docs/specs/{spec_name(path)}.md"
        if spec_path not in texts:
            continue
        spec = {r.name: r for r in parse_spec(spec_path, texts[spec_path])[0].requirements}
        delta = parse_delta(path, text)[0]
        for requirement in delta.modified + delta.removed:
            current = spec.get(requirement.name)
            if current is None:
                problems.append(
                    Problem(
                        path,
                        requirement.line,
                        f'requirement "{requirement.name}" is not in {spec_path}',
                    )
                )
            elif requirement.base and base_of(current.text) != requirement.base:
                problems.append(
                    Problem(
                        path,
                        requirement.line,
                        f'requirement "{requirement.name}" in {spec_path} has '
                        "changed since its base was taken; see what changed "
                        f"with `git log -p {spec_path}`, carry what still "
                        "applies into the delta, then run "
                        f"`python3 .agents/oekospec refresh {change}`",
                    )
                )
    return problems


def check_formats(texts: Texts) -> list[Problem]:
    """One problem per folder of docs/specs and docs/adr with files that don't follow the
    naming rule or the format, naming how many."""
    specs = folder_texts("docs/specs", texts)
    adrs = folder_texts("docs/adr", texts)
    accepted = {spec_name(path) for path in adrs}
    other_specs = [
        path
        for path, text in specs.items()
        if not is_name(spec_name(path)) or parse_spec(path, text)[1]
    ]
    other_adrs = [
        path
        for path, text in adrs.items()
        if not is_adr_name(spec_name(path)) or check_adr(parse_adr(path, text), accepted)
    ]
    return [
        Problem(folder, None, _formats_message(len(other), len(all), kind))
        for folder, kind, other, all in (
            ("docs/specs", "spec", other_specs, specs),
            ("docs/adr", "ADR", other_adrs, adrs),
        )
        if other
    ]


def _formats_message(other: int, total: int, kind: str) -> str:
    kinds = kind if total == 1 else f"{kind}s"
    verb = "doesn't" if other == 1 else "don't"
    return f"{other} of {total} {kinds} {verb} follow oekospec's format or file names"
