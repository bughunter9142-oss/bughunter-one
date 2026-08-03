import argparse
import json
from pathlib import Path

from ai_report_module import ReportConfig, ReportEngine

from .engine import ReconnaissanceEngine


def run_cli(argv=None):
    parser = argparse.ArgumentParser(description="BugHunter One reconnaissance scanner")
    parser.add_argument("target", help="Target URL or hostname")
    parser.add_argument("--output", default=None, help="Optional path to write the JSON payload")
    parser.add_argument("--reports-dir", default=None, help="Optional directory for generated HTML/Markdown/PDF/JSON reports")
    args = parser.parse_args(argv)

    engine = ReconnaissanceEngine()
    payload = engine.scan_target(args.target)
    if isinstance(payload.get("target"), dict) and "host" in payload["target"] and payload["target"]["host"].startswith("http"):
        payload["target"]["host"] = payload["target"]["host"].split("//", 1)[-1].split("/", 1)[0]

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    reports_dir = Path(args.reports_dir) if args.reports_dir else None
    if reports_dir is not None:
        report_engine = ReportEngine(ReportConfig(output_dir=reports_dir, provider="mock"))
        report_engine.write_reports(payload)

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
