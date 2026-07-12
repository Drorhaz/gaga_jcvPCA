"""Orchestrate discovery -> pose -> per-view render, plus the render manifest."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from gaga_jcvpca.config import load_config

from .config import RENDER_MODE_MAGNITUDE, RENDER_MODE_SIGNED, RenderConfig, load_render_config
from .discovery import RenderManifest, discover_manifest
from .pose import load_reference_pose, write_reference_pose
from .renderer import render_view
from .signed_tables import build_all_signed_tables, signed_tables_manifest_entry
from .tables import load_view_tables
from .viewmodel import build_view_model


@dataclass
class RenderResult:
    view_id: str
    mode: str
    png: str
    meta: str


def ensure_pose(participant: str, avatar_dir: Path, config: RenderConfig,
                rebuild: bool = False) -> dict:
    """Return the participant's reference pose, extracting it on first use (E10)."""
    path = avatar_dir / "geometry" / f"{participant}_reference_pose.json"
    if path.exists() and not rebuild:
        return load_reference_pose(participant, avatar_dir)
    ex_window = tuple(config.get("pose.exercise_window", [10, 15]))
    write_reference_pose(
        participant,
        avatar_dir,
        config=load_config(),
        ex_window=(int(ex_window[0]), int(ex_window[1])),
        reference_timepoint=config.get("pose.reference_timepoint", "T1"),
        reference_repetition=config.get("pose.reference_repetition", "R1"),
        task_part=config.get("pose.task_part", "P1"),
    )
    return load_reference_pose(participant, avatar_dir)


def render_all(
    avatar_dir: Path,
    config: RenderConfig | None = None,
    rebuild_pose: bool = False,
    mode: str = RENDER_MODE_MAGNITUDE,
) -> list[RenderResult]:
    config = config or load_render_config()
    manifest = discover_manifest(avatar_dir)
    renders_dir = config.renders_dir_for_mode(avatar_dir, mode)

    signed_tables_result = None
    if mode == RENDER_MODE_SIGNED:
        signed_tables_result = build_all_signed_tables(avatar_dir, config)

    poses: dict[str, dict] = {}
    for pid in manifest.participants:
        poses[pid] = ensure_pose(pid, avatar_dir, config, rebuild=rebuild_pose)

    results: list[RenderResult] = []
    mixed_sign_summary: dict[str, list[str]] = {}

    for view in manifest.views():
        ts = manifest.table_set(view.participant, view.comparison)
        vt = load_view_tables(ts, view)
        pose = poses[view.participant]
        vm = build_view_model(
            ts, vt, pose.get("hierarchy", {}), config, mode=mode, avatar_dir=avatar_dir,
        )
        png, meta = render_view(vm, pose, config, renders_dir)
        results.append(RenderResult(view.view_id, mode, str(png), str(meta)))
        if mode == RENDER_MODE_SIGNED and vm.mixed_sign_regions:
            mixed_sign_summary[vm.view.view_id] = vm.mixed_sign_regions

    _update_render_manifest(
        avatar_dir, manifest, mode, results, mixed_sign_summary, signed_tables_result,
    )
    return results


def _load_manifest_file(avatar_dir: Path) -> dict:
    path = avatar_dir / "render_manifest.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def _update_render_manifest(
    avatar_dir: Path,
    manifest: RenderManifest,
    mode: str,
    results: list[RenderResult],
    mixed_sign_summary: dict[str, list[str]],
    signed_tables_result=None,
) -> None:
    existing = _load_manifest_file(avatar_dir)
    modes = existing.get("modes", {})

    mode_entry = {
        "output_dir": str(config_renders_subdir(avatar_dir, mode)),
        "n_views": len(results),
        "views": [{"view_id": r.view_id, "png": r.png, "meta": r.meta} for r in results],
    }
    if mode == RENDER_MODE_SIGNED:
        mode_entry["mixed_sign_regions_by_view"] = mixed_sign_summary
        mode_entry["strong_ratio_threshold"] = load_render_config().strong_ratio_threshold
        if signed_tables_result is not None:
            mode_entry["signed_nv_tables"] = signed_tables_manifest_entry(
                avatar_dir, signed_tables_result,
            )

    modes[mode] = mode_entry

    out = {
        "participants": manifest.participants,
        "modes": modes,
    }
    if signed_tables_result is not None and "signed_nv_tables" not in out:
        out["signed_nv_tables"] = signed_tables_manifest_entry(
            avatar_dir, signed_tables_result,
        )
    if RENDER_MODE_MAGNITUDE in modes:
        out["summary_2x2_magnitude_nv"] = "renders/summary_2x2_combined.png"
    if RENDER_MODE_SIGNED in modes:
        out["summary_2x2_signed_nv"] = f"renders/{load_render_config().signed_output_subdir}/summary_2x2_combined.png"

    path = avatar_dir / "render_manifest.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)


def config_renders_subdir(avatar_dir: Path, mode: str) -> str:
    cfg = load_render_config()
    rel = cfg.renders_dir_for_mode(avatar_dir, mode).relative_to(avatar_dir)
    return str(rel)
