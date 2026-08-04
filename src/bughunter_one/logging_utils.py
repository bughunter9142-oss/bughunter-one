"""Small structured logging helper shared by the CLI and scanner."""
from __future__ import annotations

import json
import logging
from pathlib import Path


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({"level": record.levelname, "message": record.getMessage(), "logger": record.name})


def configure_logging(level: str = "INFO", log_file: Path | None = None) -> None:
    logger = logging.getLogger("bughunter_one")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()
    console = logging.StreamHandler()
    console.setFormatter(JsonFormatter())
    logger.addHandler(console)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
