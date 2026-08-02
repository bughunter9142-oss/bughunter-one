from __future__ import annotations

from typing import Any, Dict


class ProviderError(RuntimeError):
    pass


class AIProvider:
    name = "base"

    def generate_report(self, payload: Dict[str, Any]) -> str:
        raise NotImplementedError
