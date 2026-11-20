"""The oekospec command line: `python3 .agents/oekospec <command>`."""

# Keep this part readable by old Pythons, so that they reach the version check below.
from __future__ import annotations

import sys

from pyversion import python_problem

if __name__ == "__main__":
    _problem = python_problem(tuple(sys.version_info[:3]))
    if _problem:
        print(_problem, file=sys.stderr)
        sys.exit(2)

# Imported only after the version check, since these modules need Python 3.11.
import argparse
import json
import re
import secrets
from datetime import date
from pathlib import Path
from typing import Any

from archive import plan_archive
from deltas import fill_ids, refresh_bases, take_modified, take_removed
from index import build_indexes, compare_index
from installer import check_installed, check_section
from layout import check_layout
from model import Plan, Problem, UsageError
from pageserver import WAIT_SECONDS, serve, session_folder
from repo import WriteFailed, apply, find_root, git_files, read_installed, read_texts
from rounds import build_page, read_round, review_round
from templates import kinds_text, template_path
from validate import check_formats, delta_texts, validate

IDS = re.compile(r"<!-- id: ([0-9a-f]{8}) -->")
PAGES = Path(__file__).parent / "pages"


def _change_texts(root: Path, change: str) -> dict[str, str]:
    """The texts of a change folder, docs/specs and docs/adr; stops on an unknown change."""
    if (
        "/" in change
        or change in ("archive", ".", "..")
        or not (root / "docs/changes" / change).is_dir()
    ):
        raise UsageError(f"no change {change} in docs/changes")
    return read_texts(root, f"docs/changes/{change}", "docs/specs", "docs/adr")


def _validate(root: Path, args: argparse.Namespace) -> list[Problem]:
    return validate(args.change, _change_texts(root, args.change), archive=args.archive)


def _ids(root: Path, args: argparse.Namespace) -> list[Problem]:
    texts = _change_texts(root, args.change)
    deltas = delta_texts(args.change, texts)
    taken = {
        id
        for path, text in texts.items()
        if path.startswith("docs/specs/") or path in deltas
        for id in IDS.findall(text)
    }
    write = {}
    for path, text in deltas.items():
        filled = fill_ids(text, taken)
        if filled != text:
            write[path] = filled
            taken |= set(IDS.findall(filled))
    apply(root, Plan(write=write, move=None))
    return []


def _refresh(root: Path, args: argparse.Namespace) -> list[Problem]:
    texts = _change_texts(root, args.change)
    problems = []
    write = {}
    for path, text in delta_texts(args.change, texts).items():
        spec = texts.get(f"docs/specs/{path.rsplit('/', 1)[-1]}", "")
        result = refresh_bases(path, text, spec)
        if isinstance(result, list):
            problems += result
        elif result != text:
            write[path] = result
    if not problems:
        apply(root, Plan(write=write, move=None))
    return problems


def _take(root: Path, args: argparse.Namespace) -> list[Problem]:
    texts = _change_texts(root, args.change)
    spec = f"docs/specs/{args.spec}.md"
    if "/" in args.spec or spec not in texts:
        return [Problem(spec, None, f"no spec {args.spec} in docs/specs")]
    delta = f"docs/changes/{args.change}/specs/{args.spec}.md"
    take = take_modified if args.command == "modify" else take_removed
    result = take(delta, texts[spec], texts.get(delta), args.requirement)
    if isinstance(result, list):
        return result
    apply(root, Plan(write={delta: result}, move=None))
    return []


def _index(root: Path, args: argparse.Namespace) -> list[Problem]:
    texts = read_texts(root, "docs/specs", "docs/adr")
    write = {path: text for path, text in build_indexes(texts).items() if texts.get(path) != text}
    apply(root, Plan(write=write, move=None))
    return []


def _check(root: Path, args: argparse.Namespace) -> list[Problem]:
    texts = read_texts(root, "docs/specs", "docs/adr")
    problems = check_layout(root, git_files(root))
    for path, wanted in build_indexes(texts).items():
        problems += compare_index(path, texts.get(path), wanted)
    installed = read_installed(root)
    problems += check_section(installed.agents) + check_installed(installed)
    return problems + check_formats(texts)


def _archive(root: Path, args: argparse.Namespace) -> list[Problem]:
    changes = root / "docs/changes"
    open_changes = _folders(changes) - {"archive"}
    archived = _folders(changes / "archive")
    folders = ["docs/specs", "docs/adr"]
    if args.change in open_changes:
        folders.append(f"docs/changes/{args.change}")
    texts = read_texts(root, *folders)
    result = plan_archive(args.change, texts, open_changes, archived, date.today())
    if isinstance(result, list):
        return result
    try:
        apply(root, result)
    except WriteFailed as failed:
        written = [
            Problem(path, None, f"changed before archiving failed; undo with `git restore {path}`")
            if path in texts
            else Problem(path, None, "created before archiving failed; delete it")
            for path in failed.written
        ]
        return written + [
            Problem(
                f"docs/changes/{args.change}",
                None,
                f"archiving failed: {failed.__cause__}; undo the files "
                "listed above, then compare with `git status`",
            )
        ]
    return []


def _template(root: Path, args: argparse.Namespace) -> list[Problem]:
    """Print the template of the given kind, or the kinds without one; returns no problems."""
    if args.kind is None:
        print(kinds_text())
    else:
        print(template_path(args.kind).read_text(encoding="utf-8"), end="")
    return []


def _page(root: Path, args: argparse.Namespace) -> list[Problem]:
    """Put a round file, or with --review a change's proposal and decision log, on a page and
    print the answers; returns the problems that kept it from being shown or answered."""
    labels = json.loads((PAGES / "labels.json").read_text(encoding="utf-8"))
    if (args.round_file is None) == (args.review is None):
        raise UsageError("page takes either a round file or --review <change>")
    if args.review is None:
        if args.language is not None:
            raise UsageError("--language goes with --review; a round file names its language")
        result = _read_round(root, args.round_file, labels)
        if isinstance(result, list):
            return result
        round = result
    else:
        language = args.language or "en"
        texts = _change_texts(root, args.review)
        folder = f"docs/changes/{args.review}"
        missing = [
            Problem(f"{folder}/{name}", None, "missing")
            for name in ("proposal.md", "decisions.md")
            if f"{folder}/{name}" not in texts
        ]
        if missing:
            return missing
        if language not in labels:
            raise UsageError(f"no labels in {language}; the review page is in {', '.join(labels)}")
        round = review_round(
            args.review, texts[f"{folder}/proposal.md"], texts[f"{folder}/decisions.md"], language
        )
    page_id = secrets.token_hex(8)
    page = build_page((PAGES / "page.html").read_text(encoding="utf-8"), labels, round, page_id)
    session = session_folder(root)
    (session / "page.html").write_text(page, encoding="utf-8")
    answers = serve(page, page_id, session)
    if answers is None:
        hours = WAIT_SECONDS // 3600
        return [Problem(str(session / "page.html"), None, f"no answers within {hours} hours")]
    text = json.dumps(answers, ensure_ascii=False, indent=2)
    (session / "answers.json").write_text(text + "\n", encoding="utf-8")
    print(text)
    return []


def _read_round(
    root: Path, name: str, labels: dict[str, dict[str, str]]
) -> dict[str, Any] | list[Problem]:
    """The checked round in the file `name`, or the problems that keep it off a page."""
    path = Path(name).resolve()
    if path.is_relative_to(root.resolve()):
        return [
            Problem(
                name,
                None,
                "the round file is inside the repository; write it to the system's temp "
                "folder instead",
            )
        ]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        return [Problem(name, None, f"cannot be read: {error.strerror}")]
    return read_round(name, text, labels)


def _folders(folder: Path) -> set[str]:
    return {path.name for path in folder.iterdir() if path.is_dir()} if folder.is_dir() else set()


_COMMANDS = {
    "validate": _validate,
    "ids": _ids,
    "modify": _take,
    "remove": _take,
    "refresh": _refresh,
    "archive": _archive,
    "index": _index,
    "check": _check,
    "template": _template,
    "page": _page,
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="oekospec")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="report problems at review or archive level")
    validate.add_argument("change")
    validate.add_argument("--archive", action="store_true")
    commands.add_parser("ids", help="give scenarios without an ID a new one").add_argument("change")
    for name, text in [
        ("modify", "copy a requirement into the delta"),
        ("remove", "mark a requirement for removal"),
    ]:
        command = commands.add_parser(name, help=text)
        command.add_argument("change")
        command.add_argument("spec")
        command.add_argument("requirement")
    commands.add_parser("refresh", help="record current bases in the deltas").add_argument("change")
    archive = commands.add_parser("archive", help="validate, merge, move to the archive")
    archive.add_argument("change")
    commands.add_parser("index", help="rebuild both indexes")
    commands.add_parser("check", help="report layout problems and stale indexes")
    template = commands.add_parser(
        "template", help="show the template of one kind of file in a change, or list the kinds"
    )
    template.add_argument("kind", nargs="?")
    page = commands.add_parser(
        "page", help="show a round of questions on a decision page and print the answers"
    )
    page.add_argument("round_file", nargs="?", help="the round, a JSON file outside the repo")
    page.add_argument("--review", metavar="CHANGE", help="review a change's proposal and log")
    page.add_argument("--language", help="the review page's language, such as en or de")
    return parser


def _line(problem: Problem) -> str:
    if problem.line is None:
        return f"{problem.path}: {problem.message}"
    return f"{problem.path}:{problem.line}: {problem.message}"


def main(argv: list[str]) -> int:
    """Run one command on the repo of the current directory; returns the exit code."""
    try:
        args = _parser().parse_args(argv)
    except SystemExit as exit:
        return int(exit.code or 0)
    try:
        root = find_root(Path.cwd())
        problems = _COMMANDS[args.command](root, args)
    except UsageError as error:
        print(f"oekospec: {error}", file=sys.stderr)
        return 2
    for problem in problems:
        print(_line(problem))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
