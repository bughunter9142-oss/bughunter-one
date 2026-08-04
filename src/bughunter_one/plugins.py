"""Extensible, failure-isolated post-scan plugin support."""
from __future__ import annotations

import logging
from importlib import metadata
from typing import Any, Protocol


class ReconPlugin(Protocol):
    """Plugin contract for entry points in the ``bughunter_one.plugins`` group."""

    name: str

    def apply(self, payload: dict[str, Any]) -> None:
        """Enrich a completed scan payload in place without performing a scan."""


class PluginManager:
    """Registers and executes optional post-scan plugins safely."""

    def __init__(self, enabled: dict[str, bool] | None = None):
        self.enabled = enabled or {}
        self.plugins: dict[str, ReconPlugin] = {}
        self.logger = logging.getLogger("bughunter_one.plugins")

    @classmethod
    def discover(cls, enabled: dict[str, bool] | None = None) -> "PluginManager":
        manager = cls(enabled)
        try:
            entry_points = metadata.entry_points()
            candidates = entry_points.select(group="bughunter_one.plugins") if hasattr(entry_points, "select") else entry_points.get("bughunter_one.plugins", [])
        except Exception as exc:  # pragma: no cover - platform metadata failures are uncommon
            manager.logger.warning("plugin_discovery_failed error=%s", exc)
            return manager
        for entry_point in candidates:
            try:
                candidate = entry_point.load()
                plugin = candidate() if isinstance(candidate, type) else candidate
                manager.register(plugin)
            except Exception as exc:
                manager.logger.warning("plugin_load_failed plugin=%s error=%s", entry_point.name, exc)
        return manager

    def register(self, plugin: ReconPlugin) -> None:
        name = getattr(plugin, "name", "")
        apply = getattr(plugin, "apply", None)
        if not isinstance(name, str) or not name or not callable(apply):
            raise ValueError("Plugins must define a non-empty name and an apply(payload) method")
        self.plugins[name] = plugin

    def apply_all(self, payload: dict[str, Any]) -> None:
        for name, plugin in self.plugins.items():
            if not self.enabled.get(name, True):
                self.logger.debug("plugin_disabled plugin=%s", name)
                continue
            try:
                plugin.apply(payload)
            except Exception as exc:
                self.logger.error("plugin_failed plugin=%s error=%s", name, exc)
                payload.setdefault("metadata", {}).setdefault("plugin_errors", []).append({"plugin": name, "error": str(exc)})
