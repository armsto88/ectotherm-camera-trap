"""Types that every part of the library passes around."""

from dataclasses import dataclass

Texts = dict[str, str]  # path relative to the repo root → file text


@dataclass
class Problem:
    """One thing wrong, printed as `path:line: message`, or `path: message` without a line."""

    path: str
    line: int | None  # None for a problem with the whole file, such as a missing one
    message: str


@dataclass
class Plan:
    """Everything archive will change on disk, worked out before anything is written."""

    write: Texts  # new or changed files
    move: tuple[str, str] | None  # change folder → its folder in the archive


class UsageError(Exception):
    """Wrong usage or no git repo: the command stops with exit code 2."""
