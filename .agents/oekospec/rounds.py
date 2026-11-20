"""Decision pages without the disk: checking a round file, building the review round and the page.

A round is the content of one decision page, written by the agent as JSON. The page itself is a
fixed template that ships with the library; the round and its labels go into its one slot.
"""

import json
import re
from typing import Any

from model import Problem

STEPS = ("discuss", "propose", "implement")
SLOT = "__PAGE_DATA__"
CHAT = "chat"  # the choice "rather discuss in the chat", so no option may take this id
ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]*\Z")

# The fields of each part of a round: required ones first, then optional ones. Every field
# holds text, except an open question's options.
Fields = tuple[tuple[str, ...], tuple[str, ...]]
_QUESTION: Fields = (("id", "title", "context"), ("more", "free"))
_OPTION: Fields = (("id", "label", "text", "weak"), ())
_CONFIRM: Fields = (("id", "title", "body"), ("weak", "rejected"))
_COLLAPSED: Fields = (("id", "title", "why"), ("alt",))


def read_round(
    path: str, text: str, labels: dict[str, dict[str, str]]
) -> dict[str, Any] | list[Problem]:
    """The round that `text`, a round file at `path`, holds; returns problems instead when it is
    not a JSON object, lacks a required field, repeats an id, has an open question without
    exactly one recommended option or with an option lacking its weakness, or names a language
    missing from `labels` without bringing labels for every key."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        return [Problem(path, error.lineno, f"not valid JSON: {error.msg}")]
    if not isinstance(data, dict):
        return [Problem(path, None, "a round file holds one JSON object")]
    found: list[str] = []
    _fields(data, (("language", "change", "title"), ("intro",)), "the round", found)
    if data.get("step") not in STEPS:
        found.append(f"the round: step must be one of {', '.join(STEPS)}")
    number = data.get("round")
    if not isinstance(number, int) or isinstance(number, bool) or number < 1:
        found.append("the round: round must be a whole number from 1")
    found += _labels(data, labels)
    parts = {}
    for part in ("open", "confirm", "collapsed"):
        items = data.get(part, [])
        if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
            found.append(f"the round: {part} must be a list of objects")
            items = []
        parts[part] = items
    if not any(parts.values()):
        found.append("the round holds no open question and no point")
    ids: list[str] = []
    for question in parts["open"]:
        where = _where("question", question)
        _fields(question, _QUESTION, where, found)
        found += _options(question, where)
        ids.append(question.get("id"))
    for part, fields in (("confirm", _CONFIRM), ("collapsed", _COLLAPSED)):
        for point in parts[part]:
            _fields(point, fields, _where("point", point), found)
            ids.append(point.get("id"))
    found += _repeated(ids, "the round")
    if found:
        return [Problem(path, None, message) for message in found]
    return {**data, **parts}


def review_round(change: str, proposal: str, decisions: str, language: str) -> dict[str, Any]:
    """The round of discuss's review page: each section of `proposal` and each entry of
    `decisions` as a review item holding its Markdown exactly as in the file."""
    sections = _sections(proposal)
    items = [
        {
            "id": f"p{number}",
            "group": "proposal",
            "title": _heading(section),
            "markdown": section,
            "folded": False,
        }
        for number, section in enumerate(sections)
    ]
    entries = [part for part in _sections(decisions) if part.startswith("## ")]
    for number, entry in enumerate(entries, start=1):
        found = re.match(r"## (\d+)\.", entry)
        decision = re.search(r"(?m)^- \*\*Decision:\*\* (.*(?:\n  .*)*)", entry)
        items.append(
            {
                "id": f"d{found.group(1) if found else number}",
                "group": "decisions",
                "title": _heading(entry),
                "subtitle": " ".join(decision.group(1).split()) if decision else "",
                "markdown": entry,
                "folded": True,
            }
        )
    return {
        "language": language,
        "step": "discuss",
        "change": change,
        "round": None,
        "title": _heading(sections[0]) if sections else change,
        "review": items,
    }


def _sections(text: str) -> list[str]:
    """The text split before each `## ` heading, the part before the first one included, each
    without the blank lines that separate it from the next."""
    parts = re.split(r"(?m)^(?=## )", text)
    return [part.rstrip("\n") for part in parts if part.strip()]


def _heading(section: str) -> str:
    return section.split("\n", 1)[0].lstrip("#").strip()


def build_page(
    template: str, labels: dict[str, dict[str, str]], round: dict[str, Any], page_id: str
) -> str:
    """The template with the round, its labels and `page_id` put into its slots, as JSON that
    cannot close the script tag it sits in."""
    language = round.get("language", "en")
    page_labels = {**labels.get(language, labels["en"]), **round.get("labels", {})}
    data = json.dumps(
        {"page_id": page_id, "labels": page_labels, "round": round}, ensure_ascii=False
    )
    # <, > and & only occur inside JSON strings, where their \u escapes mean the same.
    for char in "&<>":
        data = data.replace(char, f"\\u{ord(char):04x}")
    return template.replace(SLOT, data)


def _where(kind: str, item: dict[str, Any]) -> str:
    id = item.get("id")
    return f"{kind} {id}" if isinstance(id, str) and id else f"a {kind} without an id"


def _fields(item: dict[str, Any], fields: Fields, where: str, found: list[str]) -> None:
    """Adds a problem for each required field that is missing or empty and each field that holds
    no text, and for an id that a page cannot use."""
    required, optional = fields
    for name in required:
        value = item.get(name)
        if value is None or isinstance(value, str) and not value.strip():
            found.append(f"{where}: lacks {_name(name)}")
        elif not isinstance(value, str):
            found.append(f"{where}: {name} must be text")
    for name in optional:
        if name in item and not isinstance(item[name], str):
            found.append(f"{where}: {name} must be text")
    id = item.get("id")
    if "id" in required and isinstance(id, str) and id and not ID.match(id):
        found.append(f"{where}: an id starts with a letter and holds only letters, digits, - and _")


def _name(field: str) -> str:
    return "its weakness (weak)" if field == "weak" else field


def _options(question: dict[str, Any], where: str) -> list[str]:
    options = question.get("options")
    if not isinstance(options, list) or not all(isinstance(option, dict) for option in options):
        return [f"{where}: lacks options, a list of objects"]
    found: list[str] = []
    if len(options) < 2:
        found.append(f"{where}: needs at least two options")
    for option in options:
        option_where = f"{where}, {_where('option', option)}"
        _fields(option, _OPTION, option_where, found)
        if option.get("id") == CHAT:
            found.append(f"{option_where}: the id {CHAT} is kept for “rather discuss in the chat”")
        if option.get("rec") is True:
            why = option.get("why")
            if not isinstance(why, str) or not why.strip():
                found.append(f"{option_where}: the recommended option lacks why")
        elif "rec" in option and option["rec"] is not False:
            found.append(f"{option_where}: rec must be true or false")
    recommended = sum(option.get("rec") is True for option in options)
    if recommended != 1:
        found.append(f"{where}: needs exactly one recommended option, has {recommended}")
    found += _repeated([option.get("id") for option in options], where)
    return found


def _repeated(ids: list[Any], where: str) -> list[str]:
    texts = [id for id in ids if isinstance(id, str)]
    repeated = sorted({id for id in texts if texts.count(id) > 1})
    return [f"{where}: the id {id} is used more than once" for id in repeated]


def _labels(data: dict[str, Any], labels: dict[str, dict[str, str]]) -> list[str]:
    own = data.get("labels")
    if own is not None and (
        not isinstance(own, dict) or not all(isinstance(text, str) for text in own.values())
    ):
        return ["the round: labels must map each key to a text"]
    language = data.get("language")
    if not isinstance(language, str) or language in labels:
        return []
    missing = sorted(set(labels["en"]) - set(own or {}))
    if not missing:
        return []
    message = (
        f"the round: the template has no labels in {language}, so the round brings its own "
        f"under labels; missing: {', '.join(missing)}"
    )
    return [message]
