import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bughunter_one import cli as cli_module


class DummyEngine:
    def scan_target(self, target):
        return {"target": {"host": target}, "subdomains": []}


class DummyReportEngine:
    def __init__(self, config):
        self.config = config

    def write_reports(self, payload):
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        (self.config.output_dir / "report.html").write_text("<html></html>", encoding="utf-8")


def test_run_cli_writes_payload_into_reports_dir_when_output_matches_reports_dir(tmp_path, monkeypatch):
    reports_dir = tmp_path / "artifacts"

    monkeypatch.setattr(cli_module, "ReconnaissanceEngine", lambda: DummyEngine())
    monkeypatch.setattr(cli_module, "ReportEngine", DummyReportEngine)

    exit_code = cli_module.run_cli([
        "https://example.com",
        "--output",
        str(reports_dir),
        "--reports-dir",
        str(reports_dir),
    ])

    assert exit_code == 0
    assert (reports_dir / "payload.json").exists()
    assert (reports_dir / "report.html").exists()
