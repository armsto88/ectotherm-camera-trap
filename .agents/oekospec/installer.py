"""The installer's logic, texts in and texts out, and its command."""

import hashlib
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from model import Problem, Texts

START = "<!-- oekospec:start -->"
END = "<!-- oekospec:end -->"
LINK = "link"  # the manifest's hash field for a symlink
MANIFEST = ".agents/oekospec/MANIFEST"
FEEDBACK = "installed files belong to oekospec; send changes to the oekospec repo as feedback"


@dataclass
class Release:
    """What a checkout ships, keyed by path in the target repo."""

    files: Texts  # skills, library and VERSION
    skills: list[str]
    section: str  # the text of agents-section.md


@dataclass
class Installed:
    """What the target repo holds before the installer changes it."""

    manifest: dict[str, str]  # path → sha256 or LINK, empty without a manifest
    current: dict[str, str | None]  # path → sha256 of each manifest file now, None if missing
    skills: list[str]  # names in .agents/skills and .claude/skills
    agents: str | None  # the root AGENTS.md
    claude: str  # the root CLAUDE.md: "missing", "link" or "file"


@dataclass
class InstallPlan:
    """Everything an install or uninstall changes, worked out before anything is written."""

    write: Texts  # installed files, MANIFEST and AGENTS.md
    delete: list[str]  # files, skill links and folders, deleted after writing
    links: dict[str, str]  # symlink path → target
    dropped: list[str]  # installed files whose local edits are overwritten or deleted


def sha256(text: str) -> str:
    """The hex SHA-256 of the UTF-8 bytes of `text`."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_manifest(text: str) -> dict[str, str]:
    """path → sha256 or LINK; lines that don't fit the format are skipped."""
    entries = {}
    for line in text.splitlines():
        hash, separator, path = line.partition("  ")
        if separator and path and (hash == LINK or _is_sha256(hash)):
            entries[path] = hash
    return entries


def manifest_text(entries: dict[str, str]) -> str:
    """The manifest, one `<hash>  <path>` line per entry, sorted by path."""
    return "".join(f"{entries[path]}  {path}\n" for path in sorted(entries))


def own_skills(installed: Installed) -> list[str]:
    """Skill names in .agents/skills or .claude/skills that the manifest doesn't list."""
    listed = {
        path.split("/")[2] for path in installed.manifest if path.startswith(".agents/skills/")
    }
    return [name for name in installed.skills if name not in listed]


def plan_install(
    release: Release, installed: Installed, section: bool
) -> InstallPlan | list[Problem]:
    """The plan for an install or update; problems naming each clashing own skill instead."""
    clashes = [name for name in own_skills(installed) if name in release.skills]
    if clashes:
        return [
            Problem(
                name,
                None,
                f"an own skill has the name of the oekospec skill {name}; "
                "rename or remove it, then run the installer again",
            )
            for name in clashes
        ]
    write = dict(release.files)
    manifest = {path: sha256(text) for path, text in write.items()}
    links = {f".claude/skills/{name}": f"../../.agents/skills/{name}" for name in release.skills}
    agents = installed.agents
    if section:
        agents = with_section(agents, release.section)
        if agents != installed.agents:
            write["AGENTS.md"] = agents
    if agents is not None and (
        installed.claude == "missing"
        or (installed.claude == "link" and installed.manifest.get("CLAUDE.md") == LINK)
    ):
        links["CLAUDE.md"] = "AGENTS.md"
        manifest["CLAUDE.md"] = LINK
    write[MANIFEST] = manifest_text(manifest)
    files = {path: hash for path, hash in installed.manifest.items() if hash != LINK}
    gone = sorted({skill for path in files if (skill := _skill_of(path))} - set(release.skills))
    delete = [path for path in sorted(files) if path not in write and _skill_of(path) not in gone]
    for name in gone:
        delete += [f".agents/skills/{name}", f".claude/skills/{name}"]
    dropped = [
        path
        for path, hash in sorted(files.items())
        if installed.current.get(path) not in (None, hash)
    ]
    return InstallPlan(write=write, delete=delete, links=links, dropped=dropped)


def with_section(agents: str | None, section: str) -> str:
    """AGENTS.md with the section between the markers: replaced in place, or appended."""
    block = f"{START}\n{section.rstrip(chr(10))}\n{END}"
    markers = _markers(agents)
    if agents is not None and markers is not None:
        start, end = markers
        return agents[:start] + block + agents[end:]
    if not agents or not agents.strip():
        return block + "\n"
    return agents.rstrip("\n") + "\n\n" + block + "\n"


def without_section(agents: str) -> str:
    """AGENTS.md without the markers and the text between them."""
    markers = _markers(agents)
    if markers is None:
        return agents
    start, end = markers
    before, after = agents[:start].rstrip("\n"), agents[end:].lstrip("\n")
    if before and after:
        return f"{before}\n\n{after}"
    return f"{before}\n" if before else after


def plan_uninstall(installed: Installed) -> InstallPlan:
    """The plan that removes everything the manifest lists, the skill links, the section and
    .agents/oekospec; an AGENTS.md left empty goes too."""
    write: Texts = {}
    delete = []
    skills = sorted({skill for path in installed.manifest if (skill := _skill_of(path))})
    for path, hash in sorted(installed.manifest.items()):
        if hash == LINK and installed.current.get(path) == LINK:
            delete.append(path)  # the CLAUDE.md link, unless replaced by a file of their own
    for name in skills:
        delete += [f".agents/skills/{name}", f".claude/skills/{name}"]
    delete.append(".agents/oekospec")
    if installed.agents is not None and has_section(installed.agents):
        agents = without_section(installed.agents)
        if agents.strip():
            write["AGENTS.md"] = agents
        else:
            delete.append("AGENTS.md")
    dropped = [
        path
        for path, hash in sorted(installed.manifest.items())
        if hash != LINK and installed.current.get(path) not in (None, hash)
    ]
    return InstallPlan(write=write, delete=delete, links={}, dropped=dropped)


def check_installed(installed: Installed) -> list[Problem]:
    """Installed files that are edited or missing, pointing to the oekospec repo."""
    problems = []
    for path, hash in sorted(installed.manifest.items()):
        current = installed.current.get(path)
        if current is None:
            problems.append(
                Problem(path, None, "installed file is missing; run the install command again")
            )
        elif current != hash:
            problems.append(Problem(path, None, f"installed file was edited; {FEEDBACK}"))
    return problems


def has_section(agents: str | None) -> bool:
    """Whether AGENTS.md holds both markers, the start before the end."""
    return _markers(agents) is not None


def check_section(agents: str | None) -> list[Problem]:
    """A problem when the root AGENTS.md is missing or holds no workflow section."""
    if agents is None:
        return [
            Problem(
                "AGENTS.md",
                None,
                "file is missing, so the workflow section is missing; "
                "run the install command and accept the section",
            )
        ]
    if not has_section(agents):
        return [
            Problem(
                "AGENTS.md",
                None,
                f"the workflow section between {START} and {END} is missing; "
                "run the install command and accept the section",
            )
        ]
    return []


def _markers(agents: str | None) -> tuple[int, int] | None:
    """Where the start marker begins and the end marker ends, if both are there in order."""
    if agents is None or (start := agents.find(START)) < 0:
        return None
    end = agents.find(END, start + len(START))
    return None if end < 0 else (start, end + len(END))


def _skill_of(path: str) -> str | None:
    """The skill an installed file belongs to, or None for the library."""
    parts = path.split("/")
    return parts[2] if path.startswith(".agents/skills/") and len(parts) > 3 else None


def _is_sha256(text: str) -> bool:
    return len(text) == 64 and all(char in "0123456789abcdef" for char in text)


def run(checkout: Path, target: Path, yes: bool, uninstall: bool) -> int:
    """The install command: read, ask for the section, plan, write, run the check and print;
    returns the exit code."""
    import repo  # repo reads and writes the types above, so it is imported only here

    root = repo.find_root(target)
    installed = repo.read_installed(root)
    if uninstall:
        return _uninstall(root, installed)
    release = repo.read_release(checkout)
    plan = plan_install(release, installed, section=_wants_section(release, installed, yes))
    if isinstance(plan, list):
        print("oekospec: nothing was installed:", file=sys.stderr)
        for problem in plan:
            print(_line(problem), file=sys.stderr)
        return 1
    try:
        repo.apply_install(root, plan)
    except repo.WriteFailed as failed:
        print(f"oekospec: installing failed: {failed.__cause__}", file=sys.stderr)
        for path in failed.written:
            print(f"{path}: changed before installing failed", file=sys.stderr)
        return 1
    version = release.files[".agents/oekospec/VERSION"].strip()
    print(f"Installed oekospec {version} into {root}.")
    if plan.dropped:
        print(f"These installed files had local edits, which were dropped; {FEEDBACK}:")
        for path in plan.dropped:
            print(f"  {path}")
    _check(root)
    return 0


def _uninstall(root: Path, installed: Installed) -> int:
    """Remove what the manifest lists, the skill links and the section; returns the exit code."""
    import repo

    if not installed.manifest:
        print(f"Nothing to uninstall: {root} has no {MANIFEST}.")
        return 0
    plan = plan_uninstall(installed)
    try:
        repo.apply_install(root, plan)
    except repo.WriteFailed as failed:
        print(f"oekospec: uninstalling failed: {failed.__cause__}", file=sys.stderr)
        for path in failed.written:
            print(f"{path}: changed before uninstalling failed", file=sys.stderr)
        return 1
    print(f"Uninstalled oekospec from {root}.")
    if plan.dropped:
        print("These installed files had local edits, which were removed with them:")
        for path in plan.dropped:
            print(f"  {path}")
    return 0


def _wants_section(release: Release, installed: Installed, yes: bool) -> bool:
    """Whether to add or update the workflow section: with --yes, when AGENTS.md already holds
    it, or when the developer accepts it at the prompt; without a terminal, it is declined."""
    if yes or has_section(installed.agents):
        return True
    if not sys.stdin.isatty():
        print(
            "The workflow section was not added to AGENTS.md: there is no terminal to ask. "
            "Run the installer again with --yes to add it."
        )
        return False
    print("oekospec can add this workflow section to AGENTS.md, so every agent knows it:\n")
    print(release.section)
    answer = input("Add the workflow section to AGENTS.md? [y/N] ")
    return answer.strip().lower() in ("y", "yes")


def _check(root: Path) -> None:
    """Run the installed library's check in `root` and show its report; -B leaves no
    bytecode behind."""
    result = subprocess.run(
        [sys.executable, "-B", ".agents/oekospec", "check"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        print("The check finds no problems.")
    else:
        print("The check reports:")
        print(result.stdout + result.stderr, end="")


def _line(problem: Problem) -> str:
    if problem.line is None:
        return f"{problem.path}: {problem.message}"
    return f"{problem.path}:{problem.line}: {problem.message}"
