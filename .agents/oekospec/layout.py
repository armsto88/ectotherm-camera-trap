"""Reporting agent file layout problems from what is on disk."""

import os
from pathlib import Path

from model import Problem


def check_layout(root: Path, files: list[str]) -> list[Problem]:
    """All layout problems; `files` is what git does not ignore."""
    return check_claude_md(root, files) + check_skill_links(root) + check_foreign_entries(root)


def check_claude_md(root: Path, files: list[str]) -> list[Problem]:
    """CLAUDE.md files that are not a symlink to the AGENTS.md next to them."""
    problems = []
    for path in files:
        if path.rsplit("/", 1)[-1] != "CLAUDE.md" or not os.path.lexists(root / path):
            continue
        claude = root / path
        folder = os.path.dirname(path) or "."
        if not os.path.lexists(claude.parent / "AGENTS.md"):
            problems.append(Problem(path, None, f"{folder} has a CLAUDE.md but no AGENTS.md"))
        elif not claude.is_symlink():
            problems.append(Problem(path, None, "CLAUDE.md must be a symlink to AGENTS.md"))
        elif os.path.normpath(os.path.join(folder, os.readlink(claude))) != os.path.normpath(
            os.path.join(folder, "AGENTS.md")
        ):
            problems.append(
                Problem(
                    path, None, f"CLAUDE.md points to {os.readlink(claude)} instead of AGENTS.md"
                )
            )
    return problems


def check_skill_links(root: Path) -> list[Problem]:
    """Skills in .agents/skills without a correct link in .claude/skills."""
    problems = []
    for name in _skills(root):
        link = root / ".claude/skills" / name
        expected = f"../../.agents/skills/{name}"
        if not os.path.lexists(link):
            problems.append(
                Problem(
                    f".agents/skills/{name}",
                    None,
                    f"skill {name} has no link .claude/skills/{name}",
                )
            )
        elif link.is_symlink() and os.readlink(link) != expected:
            target = os.readlink(link)
            problems.append(
                Problem(
                    f".claude/skills/{name}",
                    None,
                    f"link {name} points to {target} instead of {expected}",
                )
            )
    return problems


def check_foreign_entries(root: Path) -> list[Problem]:
    """Entries in .claude/skills that are not skill links; .gitkeep is ignored."""
    folder = root / ".claude/skills"
    if not folder.is_dir():
        return []
    skills = set(_skills(root))
    problems = []
    for entry in sorted(folder.iterdir()):
        name = entry.name
        path = f".claude/skills/{name}"
        if name == ".gitkeep":
            continue
        if entry.is_symlink():
            target = os.readlink(entry)
            if name in skills:
                continue  # check_skill_links reports a wrong target
            if not entry.exists():
                problems.append(Problem(path, None, f"{name} is a broken link to {target}"))
            else:
                problems.append(
                    Problem(
                        path,
                        None,
                        f"{name} links to {target}, which is not the skill .agents/skills/{name}",
                    )
                )
        elif entry.is_dir():
            problems.append(
                Problem(
                    path,
                    None,
                    f"{name} is a folder; skills belong in .agents/skills/{name}, linked from here",
                )
            )
        else:
            problems.append(Problem(path, None, f"{name} is not a skill link"))
    return problems


def _skills(root: Path) -> list[str]:
    folder = root / ".agents/skills"
    if not folder.is_dir():
        return []
    return sorted(path.name for path in folder.iterdir() if path.is_dir())
