import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bughunter_one import ReconnaissanceEngine, run_cli


def test_scan_target_builds_payload_compatible_with_report_engine(monkeypatch):
    def fake_resolve_dns(host):
        return {"A": ["93.184.216.34"], "AAAA": ["2606:2800:220:1:248:1893:25c8:1946"]}

    def fake_fetch_url(url, timeout=5):
        return {
            "status_code": 200,
            "headers": {"Server": "nginx", "Set-Cookie": "session=abc123; Path=/"},
            "body": "<!doctype html><html></html>",
            "final_url": url,
            "cookies": [{"name": "session", "value": "abc123"}],
        }

    monkeypatch.setattr("bughunter_one.engine.ReconnaissanceEngine._resolve_dns", fake_resolve_dns)
    monkeypatch.setattr("bughunter_one.engine.ReconnaissanceEngine._fetch_url", lambda self, url, timeout=5: fake_fetch_url(url, timeout))

    engine = ReconnaissanceEngine()
    payload = engine.scan_target("https://example.com")

    assert payload["target"]["host"] == "example.com"
    assert payload["scan_statistics"]["hosts_discovered"] == 1
    assert payload["dns"]["records"]["A"] == ["93.184.216.34"]
    assert payload["robots"]["url"].endswith("/robots.txt")
    assert payload["sitemap"]["url"].endswith("/sitemap.xml")
    assert payload["headers"]["server"] == "nginx"
    assert payload["cookies"][0]["name"] == "session"
    assert "nginx" in payload["technologies"]


def test_cli_writes_json_payload(tmp_path, monkeypatch):
    monkeypatch.setattr("bughunter_one.cli.ReconnaissanceEngine.scan_target", lambda self, target: {"target": {"host": target}, "metadata": {"scanner": "cli"}})

    output_path = tmp_path / "payload.json"
    exit_code = run_cli(["https://example.com", "--output", str(output_path)])

    assert exit_code == 0
    assert output_path.exists()
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["target"]["host"] == "example.com"
    assert data["metadata"]["scanner"] == "cli"


def test_cli_generates_reports_from_payload(tmp_path, monkeypatch):
    monkeypatch.setattr("bughunter_one.cli.ReconnaissanceEngine.scan_target", lambda self, target: {"target": {"host": target}, "metadata": {"scanner": "cli"}})

    reports_dir = tmp_path / "reports"
    exit_code = run_cli(["https://example.com", "--reports-dir", str(reports_dir)])

    assert exit_code == 0
    assert (reports_dir / "report.json").exists()
    assert (reports_dir / "report.html").exists()
    assert (reports_dir / "report.md").exists()
    assert (reports_dir / "report.pdf").exists()
