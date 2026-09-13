"""Region-level signed body heatmaps from ``tables/signed_nv/region_space/``.

Each view paints entire analytic regions (head/neck, arms, legs) with one
continuous signed color derived from the region-space rollup — not per-link hues.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .config import RENDER_MODE_SIGNED, RenderConfig, load_render_config
from .discovery import RenderManifest, TableSet, discover_manifest
from .pipeline import ensure_pose
from .renderer import render_view
from .signed_tables import build_all_signed_tables
from .tables import load_view_tables
from .viewmodel import build_view_model


@dataclass
class RegionHeatmapResult:
    view_id: str
    png: str
    meta: str
    source_csv: str


def _signed_table_set(ts: TableSet, avatar_dir: Path, config: RenderConfig) -> TableSet:
    signed_root = config.tables_dir_for_mode(avatar_dir, RENDER_MODE_SIGNED)
    return TableSet(
        participant=ts.participant,
        comparison=ts.comparison,
        comparison_id=ts.comparison_id,
        link_level_csv=signed_root / "link_level" / ts.link_level_csv.name,
        region_space_csv=signed_root / "region_space" / ts.region_space_csv.name,
    )


def region_heatmap_out_dir(avatar_dir: Path, config: RenderConfig) -> Path:
    return avatar_dir / "renders" / config.region_heatmap_output_subdir


def render_all_region_heatmaps(
    avatar_dir: Path,
    config: RenderConfig | None = None,
    rebuild_pose: bool = False,
    rebuild_signed_tables: bool = False,
) -> list[RegionHeatmapResult]:
    """Render one region heatmap per participant × comparison × space view."""
    config = config or load_render_config()
    manifest = discover_manifest(avatar_dir)

    if rebuild_signed_tables:
        build_all_signed_tables(avatar_dir, config)

    signed_root = config.tables_dir_for_mode(avatar_dir, RENDER_MODE_SIGNED)
    if not signed_root.exists():
        build_all_signed_tables(avatar_dir, config)

    out_dir = region_heatmap_out_dir(avatar_dir, config)
    poses: dict[str, dict] = {}
    for pid in manifest.participants:
        poses[pid] = ensure_pose(pid, avatar_dir, config, rebuild=rebuild_pose)

    results: list[RegionHeatmapResult] = []
    for view in manifest.views():
        ts = manifest.table_set(view.participant, view.comparison)
        signed_ts = _signed_table_set(ts, avatar_dir, config)
        if not signed_ts.region_space_csv.exists():
            raise FileNotFoundError(f"Missing signed region_space CSV: {signed_ts.region_space_csv}")

        vt = load_view_tables(signed_ts, view)
        pose = poses[view.participant]
        vm = build_view_model(
            signed_ts,
            vt,
            pose.get("hierarchy", {}),
            config,
            mode=RENDER_MODE_SIGNED,
            avatar_dir=avatar_dir,
            region_fill=True,
        )
        png, meta = render_view(vm, pose, config, out_dir)
        results.append(
            RegionHeatmapResult(
                view_id=view.view_id,
                png=str(png),
                meta=str(meta),
                source_csv=str(signed_ts.region_space_csv),
            )
        )

    _update_manifest(avatar_dir, results, config)
    return results


def _update_manifest(avatar_dir: Path, results: list[RegionHeatmapResult], config: RenderConfig) -> None:
    path = avatar_dir / "render_manifest.json"
    existing: dict = {}
    if path.exists():
        with open(path, "r", encoding="utf-8") as fh:
            existing = json.load(fh)

    existing["region_heatmap"] = {
        "output_dir": str(Path("renders") / config.region_heatmap_output_subdir),
        "source_tables_dir": "tables/signed_nv/region_space",
        "n_views": len(results),
        "views": [
            {
                "view_id": r.view_id,
                "png": r.png,
                "meta": r.meta,
                "source_csv": r.source_csv,
            }
            for r in results
        ],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(existing, fh, indent=2)
