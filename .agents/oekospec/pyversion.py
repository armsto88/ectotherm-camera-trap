"""The Python version check, readable by old Pythons so that they reach it."""

from __future__ import annotations


def python_problem(version: tuple[int, ...]) -> str | None:
    """The message to stop with on a Python older than 3.11, or None if it is new enough."""
    if version >= (3, 11):
        return None
    found = ".".join(str(part) for part in version)
    return (
        f"oekospec needs Python 3.11 or newer, but python3 is {found}. "
        "Install a newer one (on macOS: brew install python) and run it again."
    )
