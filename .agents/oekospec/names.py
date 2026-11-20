"""The one naming rule for specs, changes and ADRs."""

import re
from datetime import date

NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")  # lowercase words joined by hyphens
DATED = re.compile(r"(\d{4}-\d{2}-\d{2})-(.+)")


def is_name(name: str) -> bool:
    """Whether `name` is in kebab-case."""
    return NAME.fullmatch(name) is not None


def is_adr_name(name: str) -> bool:
    """Whether `name` is a valid ISO date, a hyphen and a name in kebab-case."""
    match = DATED.fullmatch(name)
    if match is None or not is_name(match[2]):
        return False
    try:
        date.fromisoformat(match[1])
    except ValueError:
        return False
    return True
