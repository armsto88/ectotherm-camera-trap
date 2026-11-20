"""Reading the proposal, decision log and task list of a change."""

import re
from dataclasses import dataclass

CAPABILITY = re.compile(r"- ([^:\s]+):")
ENTRY = re.compile(r"## (\d+)\. (.*)")
FIELD = re.compile(r"- \*\*([^*]+):\*\*(.*)")
TASK = re.compile(r"- \[([ xX])\] (\d+(?:\.\d+)*) (.*)")


@dataclass
class Proposal:
    """The sections of a proposal and the capabilities it lists."""

    sections: dict[str, tuple[str, int]]  # heading → (text, line)
    new: list[str]
    modified: list[str]
    capabilities_reason: str | None  # the line explaining an empty Capabilities


@dataclass
class Entry:
    """One decision log entry: its number, question and labelled fields."""

    number: int
    question: str
    fields: dict[str, str]  # Date, Step, Decision, Reason, Rejected, Replaces
    line: int


@dataclass
class Task:
    """One checkbox in tasks.md."""

    number: str
    text: str
    done: bool
    line: int


def parse_proposal(path: str, text: str) -> Proposal:
    """Read a proposal's sections and its Capabilities."""
    sections = {title: ("\n".join(lines).strip(), line) for title, line, lines in _sections(text)}
    new: list[str] = []
    modified: list[str] = []
    reason = None
    current = None
    for line in sections.get("Capabilities", ("", 0))[0].splitlines():
        if line.strip() in ("New:", "Modified:"):
            current = new if line.strip() == "New:" else modified
        elif (match := CAPABILITY.match(line)) and current is not None:
            current.append(match[1].strip("`"))
        elif line.strip() and current is None and reason is None:
            reason = line.strip()
    if new or modified:
        reason = None
    return Proposal(sections=sections, new=new, modified=modified, capabilities_reason=reason)


def parse_decisions(path: str, text: str) -> list[Entry]:
    """Read the entries of a decision log in their order."""
    entries: list[Entry] = []
    label = None
    for number, line in _lines(text):
        if line.startswith("#"):
            label = None
            if match := ENTRY.fullmatch(line):
                entries.append(Entry(int(match[1]), match[2].strip(), {}, number))
        elif entries and (match := FIELD.fullmatch(line)):
            label = match[1]
            entries[-1].fields[label] = match[2].strip()
        elif entries and label and line.startswith("  ") and line.strip():
            entries[-1].fields[label] += " " + line.strip()
        elif not line.strip():
            label = None
    return entries


def parse_tasks(path: str, text: str) -> list[Task]:
    """Read the checkboxes of a task list; Progress notes are free text and skipped."""
    tasks: list[Task] = []
    notes = False
    for number, line in _lines(text):
        if line.startswith("## "):
            notes = line[3:].strip() == "Progress notes"
        elif not notes and (match := TASK.fullmatch(line)):
            tasks.append(Task(match[2], match[3].strip(), match[1] != " ", number))
    return tasks


def _lines(text: str):
    """Numbered lines outside fenced code blocks."""
    fenced = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            yield number, line


def _sections(text: str) -> list[tuple[str, int, list[str]]]:
    """Level-2 sections: title, heading line and the lines below it."""
    sections: list[tuple[str, int, list[str]]] = []
    for number, line in _lines(text):
        if line.startswith("## "):
            sections.append((line[3:].strip(), number, []))
        elif line.startswith("# "):
            continue
        elif sections:
            sections[-1][2].append(line)
    return sections
