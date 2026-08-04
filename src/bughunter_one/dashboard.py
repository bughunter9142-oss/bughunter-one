"""Local, read-only dashboard for existing BugHunter One JSON payloads."""
from __future__ import annotations

import argparse
import html
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


SECTIONS = (
    ("Scan summary", "scan_statistics"), ("DNS information", "dns"),
    ("Technologies detected", "technologies"), ("Subdomains", "subdomains"),
    ("Live hosts", "live_hosts"), ("Open ports and services", "public_ports"),
    ("JavaScript assets", "javascript"), ("Historical URLs", "historical_urls"),
    ("API endpoints", "api_discovery"), ("Authentication pages", "auth_surface"),
    ("HTTP headers", "headers"), ("Cookies", "cookies"), ("SSL information", "ssl"),
)


def render_dashboard(payload: dict[str, Any]) -> str:
    """Render a self-contained, escaped HTML dashboard without scanning."""
    target = payload.get("target", {}).get("host", "Unknown target")
    blocks = []
    for title, key in SECTIONS:
        value = payload.get(key, [] if key not in {"dns", "javascript", "ssl", "scan_statistics", "headers"} else {})
        rendered = html.escape(json.dumps(value, indent=2, ensure_ascii=False, default=str))
        blocks.append(f"<section><h2>{html.escape(title)}</h2><pre>{rendered}</pre></section>")
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>BugHunter One Dashboard</title>
<style>body{{font:16px system-ui;margin:2rem;background:#f6f8fa;color:#1f2328}}main{{max-width:1100px;margin:auto}}section{{background:white;padding:1rem 1.25rem;margin:1rem 0;border-radius:8px;box-shadow:0 1px 3px #0002}}pre{{overflow:auto;white-space:pre-wrap}}h1{{margin-bottom:.2rem}}</style></head>
<body><main><h1>BugHunter One Dashboard</h1><p>Read-only results for <strong>{html.escape(str(target))}</strong></p>{''.join(blocks)}</main></body></html>"""


def load_payload(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Dashboard input must be a JSON object")
    return data


def serve_dashboard(payload_path: str | Path, host: str = "127.0.0.1", port: int = 8765) -> None:
    page = render_dashboard(load_payload(payload_path)).encode("utf-8")
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            if self.path not in {"/", "/index.html"}:
                self.send_error(404)
                return
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page))); self.end_headers(); self.wfile.write(page)
        def log_message(self, format, *args):
            return
    print(f"Dashboard: http://{host}:{port} (reading {payload_path})")
    ThreadingHTTPServer((host, port), Handler).serve_forever()


def run_dashboard_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Serve a read-only BugHunter One dashboard")
    parser.add_argument("payload", help="Existing scan payload JSON")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    serve_dashboard(args.payload, args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_dashboard_cli())
