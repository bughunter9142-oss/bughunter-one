"""Configuration loading for BugHunter One.

The configuration format intentionally uses TOML so Python 3.11+ can load it
without an additional runtime dependency.  Unknown keys are retained in the
raw mapping for forward compatibility.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # Python 3.10 compatibility
    import tomli as tomllib


@dataclass(frozen=True)
class ScanConfig:
    timeout: int = 5
    user_agent: str = "BugHunter-One/0.2.0"
    concurrency: int = 2
    report_output_dir: Path = Path("reports")
    logging_level: str = "INFO"
    log_file: Path | None = None
    active_checks: bool = False
    rate_limit: float = 0.2
    retries: int = 1
    enabled_modules: dict[str, bool] = field(default_factory=dict)

    def module_enabled(self, name: str) -> bool:
        return self.enabled_modules.get(name, True)


def load_config(path: str | Path | None = None) -> ScanConfig:
    """Load a TOML configuration file, returning safe defaults when omitted."""
    if path is None:
        return ScanConfig()
    config_path = Path(path)
    with config_path.open("rb") as handle:
        data: dict[str, Any] = tomllib.load(handle)
    scan = data.get("scan", {})
    reports = data.get("reports", {})
    logging = data.get("logging", {})
    modules = data.get("modules", {})
    return ScanConfig(
        timeout=int(scan.get("timeout", 5)),
        user_agent=str(scan.get("user_agent", "BugHunter-One/0.2.0")),
        concurrency=max(1, int(scan.get("concurrency", 2))),
        active_checks=bool(scan.get("active_checks", False)),
        rate_limit=max(0.0, float(scan.get("rate_limit", 0.2))),
        retries=max(0, int(scan.get("retries", 1))),
        report_output_dir=Path(reports.get("output_dir", "reports")),
        logging_level=str(logging.get("level", "INFO")).upper(),
        log_file=Path(logging["file"]) if logging.get("file") else None,
        enabled_modules={str(name): bool(enabled) for name, enabled in modules.items()},
    )
