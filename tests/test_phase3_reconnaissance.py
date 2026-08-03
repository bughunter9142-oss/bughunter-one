import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ai_report_module import ReportConfig, ReportEngine
from bughunter_one.engine import ReconnaissanceEngine


def test_phase3_modules_enrich_payload(monkeypatch):
    engine = ReconnaissanceEngine(timeout=1)

    monkeypatch.setattr(engine, "_call_dns_resolver", lambda host: {"A": ["93.184.216.34"]})
    monkeypatch.setattr(engine, "_fetch_text_resource", lambda url: "User-agent: *\nAllow: /\n" if "robots" in url else "<urlset><loc>https://example.com/</loc></urlset>")
    monkeypatch.setattr(engine, "_fetch_url", lambda url, timeout=5: {
        "status_code": 200,
        "headers": {"server": "nginx"},
        "body": "<html><script src=\"/app.js\"></script><a href=\"/login\">Login</a></html>",
        "final_url": url,
        "cookies": [],
    })
    monkeypatch.setattr(engine, "_discover_subdomains", lambda host, body: ["www.example.com", "mail.example.com"])
    monkeypatch.setattr(engine, "_collect_historical_urls", lambda host, body: ["https://web.archive.org/web/20200101000000/https://example.com/"])
    monkeypatch.setattr(engine, "_discover_public_directories", lambda base_url, wordlist, rate_limit, timeout: ["/admin", "/login"])
    monkeypatch.setattr(engine, "_discover_api_endpoints", lambda body, robots_entries, sitemap_entries: ["/api/v1", "/graphql"])
    monkeypatch.setattr(engine, "_discover_auth_surface", lambda body, urls: ["/login", "/signup"])
    monkeypatch.setattr(engine, "_identify_public_ports_and_services", lambda host, response, parsed, active=False: [{"port": 443, "service": "https", "status": "open"}])

    payload = engine.scan_target("https://example.com")

    assert "www.example.com" in payload["subdomains"]
    assert payload["historical_urls"] == ["https://web.archive.org/web/20200101000000/https://example.com/"]
    assert "/api/v1" in payload["api_discovery"]
    assert "/login" in payload["auth_surface"]
    assert payload["javascript"]["files"] == ["/app.js"]
    assert payload["public_directories"] == ["/admin", "/login"]
    assert payload["public_ports"][0]["service"] == "https"


def test_phase3_report_sections_include_new_modules():
    payload = {
        "target": {"host": "example.com"},
        "scan_statistics": {"hosts_discovered": 1, "ports_open": 1},
        "technologies": ["nginx"],
        "dns": {"records": {"A": ["93.184.216.34"]}},
        "subdomains": ["www.example.com"],
        "live_hosts": ["example.com"],
        "open_ports": [{"port": 443, "service": "https"}],
        "robots": {"entries": []},
        "sitemap": {"entries": []},
        "javascript": {"files": ["/app.js"]},
        "historical_urls": ["https://web.archive.org/web/20200101000000/https://example.com/"],
        "api_discovery": ["/api/v1"],
        "auth_surface": ["/login"],
        "parameters": [],
        "headers": {"server": "nginx"},
        "cookies": [],
        "ssl": {"tls_version": "1.3"},
        "interesting_resources": [],
        "metadata": {"scanner": "demo"},
        "public_ports": [{"port": 443, "service": "https", "status": "open"}],
        "public_directories": ["/login"],
    }

    report = ReportEngine(ReportConfig(output_dir=Path("reports"), provider="mock")).generate(payload)

    sections = report["sections"]
    assert "subdomain_enumeration" in sections
    assert "public_port_and_service_identification" in sections
    assert "public_directory_discovery" in sections
    assert "historical_public_urls" in sections
    assert "api_endpoint_discovery" in sections
    assert "authentication_surface" in sections
