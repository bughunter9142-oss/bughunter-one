from __future__ import annotations

from typing import Any, Dict

from .base import AIProvider


class MockProvider(AIProvider):
    name = "mock"

    def generate_report(self, payload: Dict[str, Any]) -> str:
        host = payload.get("target", {}).get("host", "unknown")
        return (
            f"Mock report for {host}: the scanner supplied structured reconnaissance data. "
            "The AI component summarized it for presentation without making security decisions."
        )
