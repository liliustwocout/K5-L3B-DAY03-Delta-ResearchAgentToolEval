"""Vercel serverless function: POST /api/chat."""
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from webapp.core import handle_chat  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def _reply(self, code: int, body: dict) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:  # noqa: N802
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 50_000:
                self._reply(400, {"error": "Nội dung yêu cầu không hợp lệ"})
                return
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            self._reply(400, {"error": "JSON không hợp lệ"})
            return
        code, body = handle_chat(payload)
        self._reply(code, body)

    def do_GET(self) -> None:  # noqa: N802
        self._reply(405, {"error": "Dùng POST"})
