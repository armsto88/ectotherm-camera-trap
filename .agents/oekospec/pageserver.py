"""Decision pages on the user's machine: the session folder, the local server and the browser.

The server answers only on 127.0.0.1 and only under a random token in the path. The page posts
its answers to `answers` next to itself. Once sent, it keeps asking `waiting` whether the next
round is there, so that the next page can load in the same tab.
"""

import hashlib
import json
import os
import secrets
import sys
import tempfile
import threading
import time
import webbrowser
from collections.abc import Callable
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

WAIT_SECONDS = 4 * 3600
TAB_SECONDS = 5.0  # how long a tab still open from the last page has to ask for the next one
HOST = "127.0.0.1"
MAX_BODY_BYTES = 5_000_000
SESSION = "session.json"


@dataclass(frozen=True)
class Session:
    """The address of the last page of a repository, kept so the next round can reuse its tab."""

    port: int
    token: str  # random, part of every path the server answers


def session_folder(root: Path) -> Path:
    """The folder in the system's temp folder for the repository at `root`: its pages, answers
    and session; never inside a repository."""
    key = hashlib.sha256(f"{Path.home()}\0{root.resolve()}".encode()).hexdigest()[:12]
    folder = Path(tempfile.gettempdir()) / f"oekospec-{root.name}-{key}"
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    return folder


def serve(
    page: str,
    page_id: str,
    folder: Path,
    wait_seconds: float = WAIT_SECONDS,
    open_tab: Callable[[str], bool] = webbrowser.open,
) -> dict[str, Any] | None:
    """Serve `page` on 127.0.0.1 only, under the session saved in `folder` when its port is
    free, otherwise under a new one it saves; let a tab still open from the last page load it,
    or open a new tab when none asks within a few seconds; return the answers once the page
    sends them, or None after `wait_seconds`."""
    deadline = time.monotonic() + wait_seconds
    round = _Round(page.encode("utf-8"), page_id)
    saved = _load(folder)
    server, session = _bind(round, saved)
    round.token = session.token
    _save(folder, session)
    url = f"http://{HOST}:{session.port}/{session.token}/"
    print(f"Decision page: {url}", file=sys.stderr, flush=True)
    threading.Thread(target=server.serve_forever, args=(0.05,), daemon=True).start()
    try:
        # Only a tab of the same session can still be open, waiting for the next round.
        tab_waits = session == saved and round.asked.wait(min(TAB_SECONDS, wait_seconds))
        if not tab_waits and round.claim() and not open_tab(url):
            print(f"No browser opened; open {url} by hand.", file=sys.stderr, flush=True)
        round.answered.wait(max(0.0, deadline - time.monotonic()))
    finally:
        server.shutdown()
        server.server_close()
    return round.answers


class _Round:
    """What the server shares between its requests while one page waits for its answers."""

    def __init__(self, page: bytes, page_id: str):
        self.page = page
        self.page_id = page_id
        self.token = ""
        self.answers: dict[str, Any] | None = None
        self.asked = threading.Event()  # a tab of the last page asked for this one
        self.answered = threading.Event()
        self._lock = threading.Lock()
        self._claimed = False  # a tab of the last page loads this one, or a new tab opened

    def claim(self) -> bool:
        """Whether this call is the first to claim the page for a tab."""
        with self._lock:
            claimed, self._claimed = self._claimed, True
            return not claimed

    def waiting(self, page_id: str) -> str:
        """What a sent page with `page_id` does next: wait, reload to show this round, or stop
        because this round shows elsewhere."""
        if page_id == self.page_id:
            return "wait"
        if self.claim():
            self.asked.set()
            return "reload"
        return "elsewhere"


class _Server(ThreadingHTTPServer):
    # On Windows, reusing an address lets a second server take a port that is in use.
    allow_reuse_address = os.name != "nt"
    daemon_threads = True


def _bind(round: _Round, saved: Session | None) -> tuple[_Server, Session]:
    handler = _handler(round)
    if saved is not None:
        try:
            return _Server((HOST, saved.port), handler), saved
        except OSError:
            pass  # the port is taken: a new address, and a new tab
    server = _Server((HOST, 0), handler)
    return server, Session(server.server_address[1], secrets.token_urlsafe(16))


def _load(folder: Path) -> Session | None:
    try:
        data = json.loads((folder / SESSION).read_text(encoding="utf-8"))
        return Session(int(data["port"]), str(data["token"]))
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _save(folder: Path, session: Session) -> None:
    text = json.dumps({"port": session.port, "token": session.token})
    (folder / SESSION).write_text(text + "\n", encoding="utf-8")


def _handler(round: _Round) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            url = urlsplit(self.path)
            if url.path == f"/{round.token}/":
                self._reply(200, "text/html; charset=utf-8", round.page)
            elif url.path == f"/{round.token}/waiting":
                page_id = parse_qs(url.query).get("page", [""])[0]
                self._json(200, {"state": round.waiting(page_id)})
            else:
                self.send_error(404)

        def do_POST(self) -> None:
            content_type = self.headers.get("Content-Type", "").split(";")[0].strip()
            if self.path != f"/{round.token}/answers" or content_type != "application/json":
                self.send_error(404)
                return
            try:
                length = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                length = 0
            if not 0 < length <= MAX_BODY_BYTES:
                self.send_error(413)
                return
            try:
                answers = json.loads(self.rfile.read(length))
            except ValueError:
                self.send_error(400)
                return
            if not isinstance(answers, dict) or answers.get("page_id") != round.page_id:
                self._json(409, {"error": "this page is not the one waiting for answers"})
                return
            self._json(200, {"ok": True})
            round.answers = answers
            round.answered.set()

        def _json(self, status: int, data: dict[str, Any]) -> None:
            self._reply(status, "application/json", json.dumps(data).encode("utf-8"))

        def _reply(self, status: int, content_type: str, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            pass  # the command prints only the answers

    return Handler
