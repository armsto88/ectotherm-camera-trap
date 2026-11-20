"""The templates of the files in a change, kept as Markdown files next to this module."""

from pathlib import Path

from model import UsageError

KINDS = {
    "proposal": "proposal.md: why the change is needed and what it changes",
    "decision": "one entry to append to decisions.md, which starts with `# Decisions`",
    "spec": "a spec delta that creates a new spec",
    "delta": "a spec delta that adds requirements to an existing spec",
    "design": "design.md: how the change is built",
    "adr": "one architecture decision record in the change's adr folder",
    "tasks": "tasks.md: the tasks that build the change, one commit each",
}


def kinds_text() -> str:
    """The kinds, one per line with what each is for."""
    width = max(len(kind) for kind in KINDS) + 2
    return "\n".join(f"{kind:<{width}}{text}" for kind, text in KINDS.items())


def template_path(kind: str) -> Path:
    """The template file of a kind; raises UsageError for an unknown kind, listing the kinds."""
    if kind not in KINDS:
        raise UsageError(f"no template {kind}; the kinds are:\n{kinds_text()}")
    return Path(__file__).parent / "templates" / f"{kind}.md"
