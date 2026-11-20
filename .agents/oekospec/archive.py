"""Planning the archive of a change: validation, merge and the archive folder name."""

from datetime import date

from merge import merge
from model import Plan, Problem, Texts
from validate import validate


def plan_archive(
    change: str, texts: Texts, open_changes: set[str], archived: set[str], today: date
) -> Plan | list[Problem]:
    """The full plan for archiving a change, or every reason it is refused, including a
    change that is unknown, already archived or archived under the same name today."""
    folder = f"docs/changes/{change}"
    if change not in open_changes:
        days = sorted(name[:10] for name in archived if name[11:] == change)
        if days:
            return [
                Problem(
                    folder,
                    None,
                    f"{change} was archived on {days[-1]}: "
                    f"docs/changes/archive/{days[-1]}-{change}",
                )
            ]
        return [Problem(folder, None, f"no change {change} in docs/changes")]
    target = f"{today.isoformat()}-{change}"
    problems = validate(change, texts, archive=True)
    if target in archived:
        problems.append(
            Problem(
                f"docs/changes/archive/{target}",
                None,
                "a change of that name was archived today already",
            )
        )
    if problems:
        return problems
    result = merge(change, texts, today)
    if isinstance(result, list):
        return result
    result.move = (folder, f"docs/changes/archive/{target}")
    return result
