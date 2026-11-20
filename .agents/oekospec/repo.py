"""The only part besides the layout check that touches the disk or runs git."""

import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from installer import LINK, MANIFEST, Installed, InstallPlan, Release, parse_manifest
from model import Plan, Texts, UsageError


def find_root(cwd: Path) -> Path:
    """Top level of the git repo or worktree of `cwd`; raises UsageError outside one."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        raise UsageError("git is not installed") from None
    if result.returncode != 0:
        raise UsageError(f"{cwd} is not inside a git repository")
    return Path(result.stdout.strip())


def read_texts(root: Path, *folders: str) -> Texts:
    """Every Markdown file under the given folders, keyed by its path from the root."""
    texts = {}
    for folder in folders:
        for path in sorted((root / folder).rglob("*.md")):
            if path.is_file():
                # newline="" keeps carriage returns, which validation reports
                with open(path, encoding="utf-8", newline="") as file:
                    texts[path.relative_to(root).as_posix()] = file.read()
    return texts


def git_files(root: Path) -> list[str]:
    """Tracked and untracked files that git does not ignore, from one `git ls-files` call."""
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return [path for path in result.stdout.split("\0") if path]


SOURCES = {"skills/": ".agents/skills/", "lib/oekospec/": ".agents/oekospec/"}
SECTION = "lib/oekospec/agents-section.md"


def read_release(checkout: Path) -> Release:
    """The files git tracks under skills/ and lib/oekospec/ of `checkout`, its version and the
    section text."""
    files = {}
    skills = set()
    for path in _git(checkout, "ls-files", "-z", "--", *SOURCES).split("\0"):
        for source, target in SOURCES.items():
            if path.startswith(source):
                with open(checkout / path, encoding="utf-8", newline="") as file:
                    files[target + path[len(source) :]] = file.read()
                if source == "skills/" and "/" in path[len(source) :]:
                    skills.add(path[len(source) :].split("/", 1)[0])
    files[".agents/oekospec/VERSION"] = version_of(checkout) + "\n"
    with open(checkout / SECTION, encoding="utf-8", newline="") as file:
        section = file.read()
    return Release(files=files, skills=sorted(skills), section=section)


def version_of(checkout: Path) -> str:
    """The `v*` tag on HEAD, or the short commit followed by `-dev`."""
    tags = _git(checkout, "tag", "--points-at", "HEAD", "--list", "v*", "--sort=-v:refname")
    if tags.split():
        return tags.split()[0]
    return _git(checkout, "rev-parse", "--short", "HEAD").strip() + "-dev"


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
    ).stdout


def read_installed(target: Path) -> Installed:
    """The manifest, the current hashes of its files, the skill names, AGENTS.md and CLAUDE.md."""
    manifest_file = target / MANIFEST
    manifest = (
        parse_manifest(manifest_file.read_text(encoding="utf-8")) if manifest_file.is_file() else {}
    )
    current = {path: _current_hash(target / path) for path in manifest}
    skills: set[str] = set()
    for folder in (".agents/skills", ".claude/skills"):
        if (target / folder).is_dir():
            skills |= {
                entry.name
                for entry in (target / folder).iterdir()
                if entry.is_dir() or entry.is_symlink()
            }
    agents_file = target / "AGENTS.md"
    agents = None
    if agents_file.is_file():
        with open(agents_file, encoding="utf-8", newline="") as file:
            agents = file.read()
    claude_file = target / "CLAUDE.md"
    if claude_file.is_symlink():
        claude = "link"
    elif claude_file.exists():
        claude = "file"
    else:
        claude = "missing"
    return Installed(
        manifest=manifest,
        current=current,
        skills=sorted(skills),
        agents=agents,
        claude=claude,
    )


def _current_hash(path: Path) -> str | None:
    """The hash an installed file has now, LINK for a symlink, None if it is missing."""
    if path.is_symlink():
        return LINK
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


class WriteFailed(Exception):
    """Writing a plan failed midway."""

    def __init__(self, written: list[str]):
        super().__init__(written)
        self.written = written  # files already changed, from the root


def apply(root: Path, plan: Plan) -> None:
    """Write each file through a temporary file and a rename, then move the folder;
    raises WriteFailed listing the files already changed."""
    written: list[str] = []
    for path, text in plan.write.items():
        try:
            _write(root / path, text)
        except OSError as error:
            raise WriteFailed(written) from error
        written.append(path)
    if plan.move is not None:
        source, target = plan.move
        try:
            (root / target).parent.mkdir(parents=True, exist_ok=True)
            if (root / target).exists():
                raise FileExistsError(f"{target} exists")
            (root / source).rename(root / target)
        except OSError as error:
            raise WriteFailed(written) from error


def apply_install(target: Path, plan: InstallPlan) -> None:
    """Write each file through a temporary file and a rename, create the links, then delete;
    raises WriteFailed listing the paths already changed."""
    changed: list[str] = []
    try:
        for path, text in plan.write.items():
            _write(target / path, text)
            changed.append(path)
        for path, link in plan.links.items():
            full = target / path
            if full.is_symlink() and os.readlink(full) == link:
                continue
            full.parent.mkdir(parents=True, exist_ok=True)
            if full.is_symlink():
                full.unlink()
            os.symlink(link, full)
            changed.append(path)
        for path in plan.delete:
            full = target / path
            if full.is_symlink() or full.is_file():
                full.unlink()
            elif full.is_dir():
                shutil.rmtree(full)
            else:
                continue
            changed.append(path)
            _remove_empty_parents(target, full.parent)
    except OSError as error:
        raise WriteFailed(changed) from error


def _remove_empty_parents(target: Path, folder: Path) -> None:
    """Remove `folder` and its parents while they are empty, up to `target`."""
    while folder != target and folder.is_dir() and not any(folder.iterdir()):
        folder.rmdir()
        folder = folder.parent


def _write(target: Path, text: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.")
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="") as file:
            file.write(text)
        os.chmod(temporary, _mode(target))
        os.replace(temporary, target)
    except BaseException:
        os.unlink(temporary)
        raise


def _mode(target: Path) -> int:
    """The mode of the file being replaced, or what a new file would get."""
    try:
        return target.stat().st_mode & 0o777
    except FileNotFoundError:
        umask = os.umask(0)
        os.umask(umask)
        return 0o666 & ~umask
