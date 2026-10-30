"""Process-local registration and lookup of declared operator plugins."""

from __future__ import annotations

from typing import Any

from copy import deepcopy

from controlplane_api.config.operator_plugins import PLUGINS, TENNESSEE_EMPTY_REASON


def plugin_registry() -> list[dict[str, Any]]:
    return deepcopy(PLUGINS)


def plugin_by_id(plugin_id: str) -> dict[str, Any] | None:
    for row in PLUGINS:
        if row["id"] == plugin_id:
            return deepcopy(row)
    return None


def registry_has_payments() -> bool:
    for row in PLUGINS:
        if "payment" in row["id"] or row["title"].lower() == "payments":
            return True
    return False


def known_action(plugin_id: str, action: str) -> bool:
    row = plugin_by_id(plugin_id)
    if row is None or row["kind"] != "builtin":
        return False
    return action in set(row.get("actions") or [])


def register_plugin(plugin: dict[str, Any]) -> None:
    """Register a trusted process-local declaration; reject duplicate IDs."""
    required = ("id", "title", "kind", "permission")
    if not all(isinstance(plugin.get(key), str) and plugin[key].strip() for key in required):
        raise ValueError("Plugin ID, title, kind and permission are required")
    if plugin["kind"] not in {"builtin", "slot"}:
        raise ValueError("Plugin kind must be builtin or slot")
    for key in ("reads", "actions"):
        if not isinstance(plugin.get(key), list) or not all(isinstance(item, str) for item in plugin[key]):
            raise ValueError("Plugin reads and actions must be lists of strings")
    if plugin_by_id(plugin["id"]) is not None:
        raise ValueError("Plugin ID is already registered")
    PLUGINS.append(deepcopy(plugin))

__all__ = ["PLUGINS", "TENNESSEE_EMPTY_REASON", "plugin_registry", "plugin_by_id", "registry_has_payments", "known_action", "register_plugin"]
