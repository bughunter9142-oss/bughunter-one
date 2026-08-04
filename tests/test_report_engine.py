import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ai_report_module import ReportEngine, ReportConfig


def test_engine_builds_structured_report_without_ai(tmp_path):
    payload = {
        "target": {"host": "example.com"},
        "scan_statistics": {"hosts_discovered": 2, "ports_open": 3},
        "technologies": ["nginx", "linux"],
        "dns": {"records": ["A"]},
        "subdomains": ["www.example.com"],
        "live_hosts": ["example.com"],
        "open_ports": [{"port": 80, "service": "http"}],
        "robots": {"entries": ["/admin"]},
        "sitemap": {"entries": ["/sitemap.xml"]},
        "javascript": {"files": ["/app.js"]},
        "historical_urls": ["https://example.com/old"],
        "api_discovery": ["/api/v1"],
        "auth_surface": ["/login"],
        "parameters": [{"name": "id", "source": "query"}],
        "headers": {"server": "nginx"},
        "cookies": [{"name": "session"}],
        "ssl": {"tls_version": "1.3"},
        "interesting_resources": [{"url": "https://example.com/robots.txt"}],
        "metadata": {"scanner": "demo"},
    }

    config = ReportConfig(output_dir=tmp_path, provider="mock")
    engine = ReportEngine(config)
    report = engine.generate(payload)

    assert report["executive_summary"]
    assert report["sections"]["target_overview"]["host"] == "example.com"
    assert report["sections"]["scan_statistics"]["hosts_discovered"] == 2
    assert report["sections"]["technologies_detected"]["count"] == 2
    assert report["sections"]["scan_metadata"]["scanner"] == "demo"


def test_engine_writes_html_markdown_pdf_and_json(tmp_path):
    payload = {
        "target": {"host": "example.com"},
        "scan_statistics": {"hosts_discovered": 1, "ports_open": 1},
        "technologies": ["nginx"],
        "dns": {"records": ["A"]},
        "subdomains": [],
        "live_hosts": ["example.com"],
        "open_ports": [],
        "robots": {"entries": []},
        "sitemap": {"entries": []},
        "javascript": {"files": []},
        "historical_urls": [],
        "api_discovery": [],
        "auth_surface": [],
        "parameters": [],
        "headers": {},
        "cookies": [],
        "ssl": {},
        "interesting_resources": [],
        "metadata": {"scanner": "demo"},
    }

    config = ReportConfig(output_dir=tmp_path, provider="mock")
    engine = ReportEngine(config)
    report_paths = engine.write_reports(payload)

    assert report_paths["html"].exists()
    assert report_paths["markdown"].exists()
    assert report_paths["pdf"].exists()
    assert report_paths["json"].exists()

    data = json.loads(report_paths["json"].read_text(encoding="utf-8"))
    assert data["executive_summary"]
