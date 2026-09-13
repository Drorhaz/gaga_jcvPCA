"""Build a live avatar figure for interactive use (Streamlit tab, Phase 7).

Reuses the exact discovery / view-model / figure code path as the batch PNG
exporter, so the on-screen figure and the saved PNG are identical.
"""

from __future__ import annotations

from pathlib import Path

from .config import RENDER_MODE_MAGNITUDE, RENDER_MODES, RenderConfig, load_render_config
from .discovery import RenderManifest, ViewSpec, discover_manifest
from .pipeline import ensure_pose
from .renderer import build_figure
from .tables import load_view_tables
from .viewmodel import build_view_model

SPACES = ("functional", "null", "combined")


def get_manifest(avatar_dir: Path) -> RenderManifest:
    return discover_manifest(avatar_dir)


def render_live_figure(
    avatar_dir: Path,
    participant: str,
    comparison: str,
    space: str,
    config: RenderConfig | None = None,
    mode: str = RENDER_MODE_MAGNITUDE,
):
    """Return (matplotlib Figure, meta dict) for one view selection."""
    if mode not in RENDER_MODES:
        raise ValueError(f"Unknown render mode: {mode}")
    config = config or load_render_config()
    manifest = discover_manifest(avatar_dir)
    view = ViewSpec(
        participant=participant, comparison=comparison, space=space,
        comparison_id=f"{participant}_{comparison}",
    )
    ts = manifest.table_set(participant, comparison)
    vt = load_view_tables(ts, view)
    pose = ensure_pose(participant, avatar_dir, config)
    vm = build_view_model(ts, vt, pose.get("hierarchy", {}), config, mode=mode)
    fig = build_figure(vm, pose, config)
    return fig, vm.meta_dict()
