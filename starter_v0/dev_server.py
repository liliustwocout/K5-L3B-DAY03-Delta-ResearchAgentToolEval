"""Chạy UI web trên máy: python dev_server.py  ->  http://localhost:8000

Phục vụ public/index.html và POST /api/chat (cùng logic với bản Vercel).
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from webapp.core import handle_chat

INDEX = Path(__file__).parent / "public" / "index.html"


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, ctype: str, data: bytes) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            self._send(200, "text/html; charset=utf-8", INDEX.read_bytes())
        elif self.path == "/versions.json":
            self._send(200, "application/json; charset=utf-8", (INDEX.parent / "versions.json").read_bytes())
        else:
            self._send(404, "text/plain; charset=utf-8", b"Not found")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/chat":
            self._send(404, "text/plain; charset=utf-8", b"Not found")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            code, body = 400, {"error": "JSON không hợp lệ"}
        else:
            code, body = handle_chat(payload)
        self._send(code, "application/json; charset=utf-8", json.dumps(body, ensure_ascii=False).encode("utf-8"))


if __name__ == "__main__":
    print("UI: http://localhost:8000  (Ctrl+C để dừng)")
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
