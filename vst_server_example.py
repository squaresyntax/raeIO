"""Minimal VST analysis server implemented with the standard library."""

from __future__ import annotations

import json
import cgi
from http.server import BaseHTTPRequestHandler, HTTPServer


class VSTRequestHandler(BaseHTTPRequestHandler):
    """Handle ``/analyze`` requests for the VST example server."""

    def do_POST(self) -> None:  # noqa: N802 (method name required by BaseHTTPRequestHandler)
        if self.path != "/analyze":
            self.send_error(404)
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": self.headers.get("Content-Type"),
            },
        )

        analysis_type = form.getvalue("type", "audio")
        file_item = form["file"] if "file" in form else None
        if file_item is None or not file_item.file:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "no file provided"}).encode())
            return

        data = file_item.file.read()
        result = {
            "analysis_type": analysis_type,
            "size": len(data),
            "message": f"Processed {analysis_type} file",
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())


def create_server(port: int = 5005) -> HTTPServer:
    """Create an ``HTTPServer`` instance for the example server."""

    return HTTPServer(("localhost", port), VSTRequestHandler)


if __name__ == "__main__":  # pragma: no cover - manual run only
    create_server().serve_forever()

