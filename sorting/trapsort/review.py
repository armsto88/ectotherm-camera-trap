"""The local review page on which people sort passes and name the species."""

from __future__ import annotations

import html
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, unquote, urlparse

from .labels import LabelError, LabelStore
from .model import GROUPS, PassRecord, Picture, Season

PASSES_PER_PAGE = 25

# Which passes a view shows.
VIEWS = {
    "open": "To sort",
    "sorted": "Sorted",
    "empty": "Marked empty",
}

MODEL_TYPE_TEXT = {
    "empty": "empty",
    "frog_or_toad": "frog or toad",
    "lizard": "lizard",
    "snake": "snake",
    "other": "other animal",
}
SUGGESTED_GROUPS = {
    "frog_or_toad": ("frog", "toad"),
    "lizard": ("lizard",),
    "snake": ("snake",),
    "other": ("other",),
    "empty": (),
}


def is_empty(picture: Picture, labels: LabelStore) -> bool:
    """A person's empty mark where there is one, otherwise the computer's."""
    person = labels.empty(picture.name)
    return person if person is not None else bool(picture.empty)


def view_of(record: PassRecord, labels: LabelStore) -> str:
    """open: a picture not marked empty still needs a group or a "can't tell" mark; sorted:
    every picture not marked empty has one; empty: every picture is marked empty."""
    shown = [p for p in record.pictures if not is_empty(p, labels)]
    if not shown:
        return "empty"
    done = all(labels.group(p.name) or labels.unclear(p.name) for p in shown)
    return "sorted" if done else "open"


def serve_review(season: Season, labels: LabelStore, port: int = 8765) -> None:
    """Serves the local review page until stopped: each pass with a picture not marked empty,
    its pictures side by side; a group and name are saved for every picture of the pass at
    once, or picture by picture, and each mark is saved at once. A pass recorded outside pilot
    mode shows its model type as a suggestion; one recorded in pilot mode does not."""
    server = review_server(season, labels, port)
    print(f"Review page: http://127.0.0.1:{server.server_port}/  (stop with Ctrl+C)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def review_server(season: Season, labels: LabelStore, port: int) -> ThreadingHTTPServer:
    """The review page's server on the computer only, not yet serving; port 0 picks a free one."""
    pictures = {p.name: p for p in season.pictures}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            pass

        def do_GET(self) -> None:
            url = urlparse(self.path)
            if url.path == "/":
                query = parse_qs(url.query)
                view = query.get("view", ["open"])[0]
                page = query.get("page", ["1"])[0]
                if view not in VIEWS or not page.isdigit() or int(page) < 1:
                    return self._send(HTTPStatus.NOT_FOUND, "text/plain", b"No such page")
                body = render_page(season, labels, view, int(page)).encode()
                return self._send(HTTPStatus.OK, "text/html; charset=utf-8", body)
            if url.path.startswith("/picture/"):
                picture = pictures.get(unquote(url.path[len("/picture/") :]))
                if picture is None:
                    return self._send(HTTPStatus.NOT_FOUND, "text/plain", b"No such picture")
                return self._send(HTTPStatus.OK, "image/jpeg", picture.file.read_bytes())
            self._send(HTTPStatus.NOT_FOUND, "text/plain", b"Not found")

        def do_POST(self) -> None:
            if urlparse(self.path).path != "/label":
                return self._send(HTTPStatus.NOT_FOUND, "text/plain", b"Not found")
            try:
                length = int(self.headers.get("Content-Length", "0"))
                save_label(json.loads(self.rfile.read(length)), pictures, labels)
            except (ValueError, TypeError, LabelError) as error:
                body = json.dumps({"error": str(error)}).encode()
                return self._send(HTTPStatus.BAD_REQUEST, "application/json", body)
            self._send(HTTPStatus.OK, "application/json", b'{"ok":true}')

        def _send(self, status: HTTPStatus, content_type: str, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def save_label(request: object, pictures: dict[str, Picture], labels: LabelStore) -> None:
    """Saves what the page sent: for the named pictures a group, a name, an empty mark or a
    "can't tell" mark, each given by the person named in by."""
    if not isinstance(request, dict):
        raise TypeError("expected a JSON object")
    by = request.get("by")
    names = request.get("pictures")
    if not isinstance(by, str) or not by.strip():
        raise ValueError("enter your name before sorting")
    if not isinstance(names, list) or not names or not all(n in pictures for n in names):
        raise ValueError("unknown pictures")
    group, name = request.get("group"), request.get("name")
    empty, unclear = request.get("empty"), request.get("unclear")
    if group is not None and group not in GROUPS:
        raise ValueError(f"{group!r} is not a group")
    if name is not None and not isinstance(name, str):
        raise ValueError("a name is text")
    if empty is not None and not isinstance(empty, bool):
        raise ValueError("empty is true or false")
    for picture in names:
        if empty is not None:
            labels.set_empty(picture, empty, by)
        if unclear:
            labels.set_unclear(picture, by)
        if group is not None:
            labels.set_group(picture, group, by)
        if name is not None:
            labels.set_name(picture, name, by)


# --- The page ---------------------------------------------------------------------------------


def render_page(season: Season, labels: LabelStore, view: str, page: int) -> str:
    records = [r for r in season.passes if view_of(r, labels) == view]
    counts = {v: 0 for v in VIEWS}
    for record in season.passes:
        counts[view_of(record, labels)] += 1
    pages = max(1, -(-len(records) // PASSES_PER_PAGE))
    shown = records[(page - 1) * PASSES_PER_PAGE : page * PASSES_PER_PAGE]

    tabs = " ".join(
        f'<a class="tab{" on" if v == view else ""}" href="/?view={v}">'
        f"{html.escape(text)} <span>{counts[v]}</span></a>"
        for v, text in VIEWS.items()
    )
    paging = ""
    if pages > 1:
        links = [
            f'<a href="/?view={view}&page={n}"{" class=on" if n == page else ""}>{n}</a>'
            for n in range(1, pages + 1)
        ]
        paging = f'<nav class="paging">{" ".join(links)}</nav>'
    body = "".join(_render_pass(r, labels) for r in shown) or '<p class="none">Nothing here.</p>'
    return PAGE.format(
        trap=html.escape(season.trap_id), tabs=tabs, paging=paging, passes=body, script=SCRIPT
    )


def _render_pass(record: PassRecord, labels: LabelStore) -> str:
    names = [p.name for p in record.pictures]
    groups = {labels.group(n) for n in names if labels.group(n)}
    pass_group = groups.pop() if len(groups) == 1 else None
    pass_names = {labels.name(n) for n in names if labels.name(n)}
    pass_name = pass_names.pop() if len(pass_names) == 1 else ""
    one_by_one = len(groups) > 1 or len(pass_names) > 1

    suggestion = ""
    suggested: tuple[str, ...] = ()
    if not record.pilot and record.model_type:
        suggested = SUGGESTED_GROUPS[record.model_type]
        sure = f" ({record.model_confidence:.0%} sure)" if record.model_confidence else ""
        suggestion = (
            f'<p class="suggestion" data-suggestion="{record.model_type}">'
            f"The trap's model suggests: {MODEL_TYPE_TEXT[record.model_type]}{sure}. "
            "Pick a group to confirm or change it.</p>"
        )

    buttons = "".join(
        f'<button class="group{" chosen" if g == pass_group else ""}'
        f'{" suggested" if g in suggested else ""}" data-group="{g}">{g}</button>'
        for g in GROUPS
    )
    pictures = "".join(_render_picture(p, labels) for p in record.pictures)
    when = record.start_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"""
<section class="pass{" one-by-one" if one_by_one else ""}" data-pictures='{json.dumps(names)}'>
  <header>
    <h2>{html.escape(record.pass_id)}</h2>
    <span>{when} · {html.escape(record.direction)} · noticed by {
        html.escape(record.noticed_by)
    }</span>
    <label class="switch"><input type="checkbox" class="one-by-one-switch"{
        " checked" if one_by_one else ""
    }> label pictures one by one</label>
  </header>
  {suggestion}
  <div class="whole">
    <div class="groups">{buttons}</div>
    <input class="name" placeholder="Species name, as far as the pictures allow"
           value="{html.escape(pass_name or "")}">
  </div>
  <div class="pictures">{pictures}</div>
  <p class="status"></p>
</section>"""


def _render_picture(picture: Picture, labels: LabelStore) -> str:
    empty = is_empty(picture, labels)
    group = labels.group(picture.name)
    unclear = labels.unclear(picture.name)
    state = "empty" if empty else "can't tell" if unclear else group or ""
    options = "".join(
        f'<option value="{g}"{" selected" if g == group else ""}>{g}</option>' for g in GROUPS
    )
    name = html.escape(labels.name(picture.name) or "")
    src = "/picture/" + quote(picture.name)
    classes = "picture is-empty" if empty else "picture"
    return f"""
    <figure class="{classes}" data-picture="{html.escape(picture.name)}">
      <img src="{src}" alt="{html.escape(picture.name)}" loading="lazy">
      <figcaption>
        <span class="state">{html.escape(state)}</span>
        <button class="mark" data-mark="empty">Empty</button>
        <button class="mark" data-mark="not-empty">Not empty</button>
        <button class="mark" data-mark="unclear">Can't tell</button>
        <div class="single">
          <select class="picture-group"><option value="">group</option>{options}</select>
          <input class="picture-name" placeholder="Species name" value="{name}">
        </div>
      </figcaption>
    </figure>"""


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sorting {trap}</title>
<style>
  :root {{ --fg: #1d2125; --muted: #5f6b76; --line: #d5dbe0; --bg: #f6f7f8; --card: #fff;
          --accent: #2f6f4f; --hint: #e7f3ec; }}
  body {{ font: 15px/1.4 system-ui, sans-serif; color: var(--fg); background: var(--bg);
         margin: 0 auto; max-width: 1400px; padding: 16px; }}
  header.top {{ display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }}
  .tab {{ padding: 6px 10px; border-radius: 6px; color: var(--fg); text-decoration: none; }}
  .tab.on {{ background: var(--accent); color: #fff; }}
  .pass {{ background: var(--card); border: 1px solid var(--line); border-radius: 8px;
          padding: 12px; margin: 12px 0; }}
  .pass header {{ display: flex; gap: 12px; align-items: baseline; flex-wrap: wrap; }}
  .pass h2 {{ font-size: 15px; margin: 0; }}
  .pass header span {{ color: var(--muted); }}
  .switch {{ margin-left: auto; color: var(--muted); }}
  .suggestion {{ background: var(--hint); padding: 6px 10px; border-radius: 6px; }}
  .groups {{ display: flex; gap: 6px; flex-wrap: wrap; margin: 8px 0; }}
  button {{ font: inherit; padding: 4px 10px; border: 1px solid var(--line); border-radius: 6px;
           background: #fff; cursor: pointer; }}
  button.suggested {{ border-color: var(--accent); }}
  button.chosen {{ background: var(--accent); color: #fff; }}
  input.name {{ width: min(480px, 100%); font: inherit; padding: 4px 8px; }}
  .pictures {{ display: flex; gap: 10px; overflow-x: auto; margin-top: 8px; }}
  figure {{ margin: 0; flex: 0 0 auto; }}
  figure img {{ height: 260px; display: block; border-radius: 4px; }}
  figure.is-empty img {{ opacity: .45; }}
  figcaption {{ display: flex; gap: 6px; flex-wrap: wrap; margin-top: 4px; align-items: center; }}
  .state {{ min-width: 70px; color: var(--muted); }}
  .single {{ display: none; gap: 6px; }}
  .one-by-one .single {{ display: flex; }}
  .one-by-one .whole {{ display: none; }}
  .status {{ color: var(--muted); min-height: 1.2em; margin: 4px 0 0; }}
  .paging a {{ margin-right: 6px; }} .paging a.on {{ font-weight: bold; }}
</style></head>
<body>
<header class="top">
  <strong>Trap {trap}</strong>
  <nav>{tabs}</nav>
  <label>Your name <input id="by" placeholder="needed to save labels"></label>
</header>
{paging}
{passes}
{paging}
<script>{script}</script>
</body></html>
"""

SCRIPT = """
const by = document.getElementById('by');
try { by.value = localStorage.getItem('trapsort-by') || ''; } catch (e) {}
by.addEventListener('change', () => {
  try { localStorage.setItem('trapsort-by', by.value); } catch (e) {}
});

async function save(section, label) {
  const status = section.querySelector('.status');
  if (!by.value.trim()) { status.textContent = 'Enter your name at the top first.'; return false; }
  const response = await fetch('/label', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(Object.assign({by: by.value}, label)),
  });
  const answer = await response.json();
  status.textContent = response.ok ? 'Saved.' : 'Not saved: ' + answer.error;
  return response.ok;
}

for (const section of document.querySelectorAll('.pass')) {
  const all = JSON.parse(section.dataset.pictures);
  const name = section.querySelector('input.name');
  section.querySelector('.one-by-one-switch').addEventListener('change', (e) => {
    section.classList.toggle('one-by-one', e.target.checked);
  });
  for (const button of section.querySelectorAll('button.group')) {
    button.addEventListener('click', async () => {
      if (await save(section, {pictures: all, group: button.dataset.group, name: name.value})) {
        section.querySelectorAll('button.group').forEach((b) => b.classList.remove('chosen'));
        button.classList.add('chosen');
      }
    });
  }
  name.addEventListener('change', () => save(section, {pictures: all, name: name.value}));
  for (const figure of section.querySelectorAll('figure')) {
    const picture = [figure.dataset.picture];
    const state = figure.querySelector('.state');
    for (const button of figure.querySelectorAll('button.mark')) {
      button.addEventListener('click', async () => {
        const mark = button.dataset.mark;
        const label = mark === 'unclear' ? {unclear: true} : {empty: mark === 'empty'};
        if (await save(section, Object.assign({pictures: picture}, label))) {
          figure.classList.toggle('is-empty', mark === 'empty');
          state.textContent = mark === 'empty' ? 'empty' : mark === 'unclear' ? "can't tell" : '';
        }
      });
    }
    figure.querySelector('.picture-group').addEventListener('change', (e) => {
      if (e.target.value) save(section, {pictures: picture, group: e.target.value});
    });
    figure.querySelector('.picture-name').addEventListener('change', (e) => {
      save(section, {pictures: picture, name: e.target.value});
    });
  }
}
"""
