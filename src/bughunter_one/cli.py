import argparse
import json
from pathlib import Path

from ai_report_module import ReportConfig, ReportEngine

from .config import load_config
from .engine import ReconnaissanceEngine
from .logging_utils import configure_logging
from .plugins import PluginManager


def run_cli(argv=None):
    parser = argparse.ArgumentParser(description="BugHunter One reconnaissance scanner")
    parser.add_argument("target", help="Target URL or hostname")
    parser.add_argument("--output", default=None, help="Optional path to write the JSON payload")
    parser.add_argument("--reports-dir", default=None, help="Optional directory for generated HTML/Markdown/PDF/JSON reports")
    parser.add_argument("--config", default=None, help="Optional TOML configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--version", action="version", version="BugHunter One 0.3.0")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    configure_logging("DEBUG" if args.debug else config.logging_level, config.log_file)
    # Retain the zero-argument construction path used by existing integrations.
    engine = ReconnaissanceEngine() if args.config is None else ReconnaissanceEngine(
        timeout=config.timeout, active_checks=config.active_checks,
        directory_rate_limit=config.rate_limit, user_agent=config.user_agent,
        retries=config.retries, concurrency=config.concurrency,
        enabled_modules=config.enabled_modules,
        plugin_manager=PluginManager.discover(config.enabled_plugins),
    )
    payload = engine.scan_target(args.target)
    if isinstance(payload.get("target"), dict) and "host" in payload["target"] and payload["target"]["host"].startswith("http"):
        payload["target"]["host"] = payload["target"]["host"].split("//", 1)[-1].split("/", 1)[0]

    output_path = Path(args.output) if args.output else None
    reports_dir = Path(args.reports_dir) if args.reports_dir else (config.report_output_dir if args.config else None)

    if reports_dir is not None:
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_engine = ReportEngine(ReportConfig(output_dir=reports_dir, provider="mock"))
        report_engine.write_reports(payload)

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if reports_dir is not None and output_path.resolve() == reports_dir.resolve():
            payload_path = reports_dir / "payload.json"
            payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        elif output_path.exists() and output_path.is_dir():
            payload_path = output_path / "payload.json"
            payload_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        else:
            output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
