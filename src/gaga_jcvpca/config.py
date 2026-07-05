"""Configuration loading and the science_hash.

A single load path composes ``configs/default.yaml`` with its ``includes`` into
one nested dict. There are no hidden thresholds in code: every tunable value is
read from here. ``science_hash`` fingerprints the science-affecting subset so a
run can be tied to the exact configuration that produced it.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


def _project_root() -> Path:
    # src/gaga_jcvpca/config.py -> project root is three parents up.
    return Path(__file__).resolve().parents[2]


def _deep_merge(base: dict, overlay: dict) -> dict:
    out = dict(base)
    for key, value in overlay.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


@dataclass(frozen=True)
class Config:
    """Loaded configuration with dot-ish access and a science hash."""

    data: dict[str, Any]
    project_root: Path

    def get(self, dotted_key: str, default: Any = None) -> Any:
        node: Any = self.data
        for part in dotted_key.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return default
        return node

    def resolve_path(self, dotted_key: str) -> Path:
        """Resolve a path value from config against the project root."""
        raw = self.get(dotted_key)
        if raw is None:
            raise KeyError(f"No path configured at '{dotted_key}'")
        p = Path(raw)
        return p if p.is_absolute() else (self.project_root / p)

    @property
    def science_hash(self) -> str:
        non_science = set(self.data.get("non_science_keys", []) or [])
        science_view = {k: v for k, v in self.data.items() if k not in non_science}
        blob = json.dumps(science_view, sort_keys=True, default=str)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def load_config(config_path: str | Path | None = None) -> Config:
    """Load ``configs/default.yaml`` and merge its includes.

    ``config_path`` may point at an alternative top-level YAML (used in tests).
    """
    root = _project_root()
    if config_path is None:
        config_path = root / "configs" / "default.yaml"
    config_path = Path(config_path)
    configs_dir = config_path.parent

    with open(config_path, "r", encoding="utf-8") as fh:
        top = yaml.safe_load(fh) or {}

    merged: dict[str, Any] = {}
    for include in top.get("includes", []):
        with open(configs_dir / include, "r", encoding="utf-8") as fh:
            merged = _deep_merge(merged, yaml.safe_load(fh) or {})

    # Top-level keys (other than 'includes') override included values.
    top_wo_includes = {k: v for k, v in top.items() if k != "includes"}
    merged = _deep_merge(merged, top_wo_includes)

    return Config(data=merged, project_root=root)
