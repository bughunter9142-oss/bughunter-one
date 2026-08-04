import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bughunter_one.plugins import PluginManager
from bughunter_one.engine import ReconnaissanceEngine


class TagPlugin:
    name = "tagger"

    def apply(self, payload):
        payload["plugin_tag"] = "applied"


class BrokenPlugin:
    name = "broken"

    def apply(self, payload):
        raise RuntimeError("expected plugin failure")


def test_registered_plugin_enriches_payload():
    manager = PluginManager()
    manager.register(TagPlugin())
    payload = {"metadata": {}}
    manager.apply_all(payload)
    assert payload["plugin_tag"] == "applied"


def test_disabled_plugin_is_not_run():
    manager = PluginManager(enabled={"tagger": False})
    manager.register(TagPlugin())
    payload = {"metadata": {}}
    manager.apply_all(payload)
    assert "plugin_tag" not in payload


def test_plugin_errors_do_not_break_a_completed_payload():
    manager = PluginManager()
    manager.register(BrokenPlugin())
    payload = {"metadata": {}}
    manager.apply_all(payload)
    assert payload["metadata"]["plugin_errors"][0]["plugin"] == "broken"


def test_engine_runs_plugins_after_existing_scan_pipeline(monkeypatch):
    manager = PluginManager()
    manager.register(TagPlugin())
    engine = ReconnaissanceEngine(plugin_manager=manager)
    monkeypatch.setattr(engine, "_call_dns_resolver", lambda host: {"A": []})
    monkeypatch.setattr(engine, "_fetch_standard_resources", lambda payload: (None, None))
    monkeypatch.setattr(engine, "_fetch_url", lambda url: {"status_code": 0, "headers": {}, "body": "", "final_url": url, "cookies": []})
    monkeypatch.setattr(engine, "_collect_historical_urls", lambda host, body: [])
    payload = engine.scan_target("example.com")
    assert payload["plugin_tag"] == "applied"
