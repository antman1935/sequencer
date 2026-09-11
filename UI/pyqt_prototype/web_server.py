"""Local-only HTTP host used by both the browser and Qt desktop shell."""
import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from UI.pyqt_prototype.schema import execute_request, ui_schema
from UI.pyqt_prototype.theme import web_stylesheet

ASSETS = Path(__file__).with_name("web")


class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Queries capture stdout; HTTP access logs must never enter their results.
        if sys.stderr is not None:
            super().log_message(format, *args)

    def respond(self, status, body, content_type="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False)
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def allowed_host(self):
        return self.headers.get("Host") in self.server.allowed_hosts

    def do_GET(self):
        if not self.allowed_host():
            return self.respond(403, {"error": "Only local requests are supported."})
        route = urlsplit(self.path).path
        if route == "/api/schema":
            return self.respond(200, ui_schema())
        if route == "/theme.css":
            return self.respond(200, web_stylesheet(), "text/css; charset=utf-8")
        assets = {"/": ("index.html", "text/html"), "/index.html": ("index.html", "text/html"),
                  "/app.js": ("app.js", "text/javascript"), "/app.css": ("app.css", "text/css")}
        if route not in assets:
            return self.respond(404, {"error": "Not found."})
        name, mime = assets[route]
        self.respond(200, (ASSETS / name).read_bytes(), mime + "; charset=utf-8")

    def do_POST(self):
        origin = self.headers.get("Origin")
        if not self.allowed_host() or (origin is not None and origin not in self.server.allowed_origins):
            return self.respond(403, {"error": "Only requests from this app are supported."})
        if urlsplit(self.path).path != "/api/query":
            return self.respond(404, {"error": "Not found."})
        if self.headers.get_content_type() != "application/json":
            return self.respond(415, {"error": "Send queries as JSON."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 1024 * 1024:
                return self.respond(413, {"error": "Query body must be between 1 byte and 1 MB."})
            payload = json.loads(self.rfile.read(length))
            result = execute_request(payload)
        except (ValueError, AssertionError, TypeError, KeyError, RecursionError) as exc:
            return self.respond(400, {"error": str(exc) or "Invalid query."})
        except Exception as exc:
            return self.respond(500, {"error": f"Query failed: {exc}"})
        self.respond(200, result)


class SequencerServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port=0):
        super().__init__(("127.0.0.1", port), RequestHandler)
        port = self.server_address[1]
        self.allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        self.allowed_origins = {f"http://{host}" for host in self.allowed_hosts}
        self.url = f"http://127.0.0.1:{port}/"

    def start(self):
        thread = Thread(target=self.serve_forever, daemon=True, name="sequencer-http")
        thread.start()
        return self

    def stop(self):
        self.shutdown()
        self.server_close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    with SequencerServer(args.port) as server:
        print(f"Sequencer: {server.url}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
