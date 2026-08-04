"""Generate sample report artifacts from the committed example payload."""
import json
from pathlib import Path

from ai_report_module import ReportConfig, ReportEngine


def main() -> None:
    payload = json.loads(Path("examples/payload.json").read_text(encoding="utf-8"))
    ReportEngine(ReportConfig(output_dir=Path("artifacts/reports"))).write_reports(payload)


if __name__ == "__main__":
    main()
