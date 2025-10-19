# servidor_backend/http_dashboard.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, os

try:
    from .state import ultimo, lock_ultimo
except ImportError:
    from state import ultimo, lock_ultimo

ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard_web")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == "/last":
                with lock_ultimo:
                    body = json.dumps(ultimo).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if self.path == "/" or self.path.startswith("/index.html"):
                return self._serve("index.html", "text/html; charset=utf-8")
            if self.path.startswith("/script.js"):
                return self._serve("script.js", "application/javascript; charset=utf-8")
            if self.path.startswith("/style.css"):
                return self._serve("style.css", "text/css; charset=utf-8")
            self.send_response(404); self.end_headers()
        except BrokenPipeError:
            pass

    def _serve(self, name, ctype):
        path = os.path.join(ROOT, name)
        if not os.path.isfile(path):
            self.send_response(404); self.end_headers(); return
        with open(path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def start_http(host="0.0.0.0", port=8000):
    httpd = HTTPServer((host, port), Handler)
    print(f"Dashboard em http://{host if host!='0.0.0.0' else 'localhost'}:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    start_http()
