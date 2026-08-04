import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bughunter_one.config import load_config
from bughunter_one.dashboard import load_payload, render_dashboard
from bughunter_one.engine import ReconnaissanceEngine


def test_toml_configuration_loads_all_supported_options(tmp_path):
    config_file = tmp_path / "bughunter.toml"
    config_file.write_text("""[scan]\ntimeout = 9\nuser_agent = "TestAgent"\nconcurrency = 4\nactive_checks = true\nrate_limit = 0.5\nretries = 2\n[reports]\noutput_dir = "out"\n[logging]\nlevel = "DEBUG"\nfile = "logs/app.jsonl"\n[modules]\ndns = false\n""", encoding="utf-8")
    config = load_config(config_file)
    assert (config.timeout, config.user_agent, config.concurrency, config.retries) == (9, "TestAgent", 4, 2)
    assert config.active_checks and not config.module_enabled("dns")
    assert config.report_output_dir == Path("out")


def test_dashboard_renders_existing_payload_only(tmp_path):
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps({"target": {"host": "example.com"}, "headers": {"server": "nginx"}}), encoding="utf-8")
    page = render_dashboard(load_payload(payload_path))
    assert "example.com" in page and "HTTP headers" in page and "nginx" in page


def test_disabled_dns_module_preserves_schema(monkeypatch):
    engine = ReconnaissanceEngine(enabled_modules={"dns": False})
    monkeypatch.setattr(engine, "_fetch_text_resource", lambda url: None)
    monkeypatch.setattr(engine, "_fetch_url", lambda url: {"status_code": 0, "headers": {}, "body": "", "final_url": url, "cookies": []})
    payload = engine.scan_target("example.com")
    assert payload["dns"] == {"records": {"A": []}}
