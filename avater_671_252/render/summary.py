"""Investor 2x2 combined-space summary panel (RENDER_PLAN E6 / Phase 6)."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import RENDER_MODE_MAGNITUDE, RENDER_MODE_SIGNED, RenderConfig, load_render_config
from .discovery import ViewSpec, discover_manifest
from .geometry import pose_to_2d
from .pipeline import ensure_pose
from .renderer import _ARROW, _draw_avatar
from .tables import load_view_tables
from .viewmodel import build_view_model


def render_summary_2x2(
    avatar_dir: Path,
    config: RenderConfig | None = None,
    mode: str = RENDER_MODE_MAGNITUDE,
) -> Path:
    config = config or load_render_config()
    manifest = discover_manifest(avatar_dir)
    quadrants = config.get("summary_2x2.quadrant_order", []) or []

    poses = {pid: ensure_pose(pid, avatar_dir, config) for pid in manifest.participants}

    w = float(config.get("summary_2x2.figure_width_in", 14.0))
    h = float(config.get("summary_2x2.figure_height_in", 11.0))
    dpi = int(config.get("summary_2x2.dpi", 150))
    fig = plt.figure(figsize=(w, h), dpi=dpi,
                     facecolor=config.get("theme.background", "#FFFFFF"))
    gs = fig.add_gridspec(2, 2, left=0.04, right=0.96, top=0.9, bottom=0.14,
                          hspace=0.18, wspace=0.1)

    for idx, quad in enumerate(quadrants[:4]):
        participant = str(quad["participant"])
        comparison = str(quad["comparison"])
        view = ViewSpec(
            participant=participant, comparison=comparison, space="combined",
            comparison_id=f"{participant}_{comparison}",
        )
        ts = manifest.table_set(participant, comparison)
        vt = load_view_tables(ts, view)
        pose = poses[participant]
        vm = build_view_model(ts, vt, pose.get("hierarchy", {}), config, mode=mode)

        ax = fig.add_subplot(gs[idx // 2, idx % 2])
        _draw_avatar(ax, pose_to_2d(pose), vm, config)
        comp = f"T{view.reference_timepoint[1:]}{_ARROW}T{view.target_timepoint[1:]}"
        s = vm.stats
        if mode == RENDER_MODE_SIGNED:
            ax.set_title(
                f"{participant}   {comp}   (combined, signed)\n"
                f"regions {s['regions_above_nv']}/{s['regions_total']}   "
                f"links {s['links_above_nv']}/{s['links_total']}   "
                f"mixed {s.get('regions_mixed', 0)}   "
                f"max {s['max_ratio']:.1f}\u00d7 NV",
                fontsize=10, weight="bold",
            )
        else:
            ax.set_title(
                f"{participant}   {comp}   (combined)\n"
                f"regions {s['regions_above_nv']}/{s['regions_total']}   "
                f"links {s['links_above_nv']}/{s['links_total']}   "
                f"max {s['max_ratio']:.1f}\u00d7 NV",
                fontsize=10, weight="bold",
            )

    if mode == RENDER_MODE_SIGNED:
        title = config.get("signed_nv.summary_title", "JcvPCA signed contribution change vs T1")
    else:
        title = config.get("summary_2x2.title", "JcvPCA body change")
    fig.suptitle(title, fontsize=16, weight="bold", y=0.97)

    legend_lines = list(config.legend_lines_for_mode(mode))
    legend_lines.append(config.get("nv_source_line", ""))
    fig.text(0.04, 0.11, "   ".join(legend_lines[:4]), fontsize=8, family="monospace",
             color=config.get("theme.muted_text_color", "#666666"))
    footer = config.get("footer.disclaimer", "")
    t3 = config.get("footer.t3_confound_text", "")
    fig.text(0.5, 0.03, f"{footer}   |   {t3}", ha="center", fontsize=8,
             color=config.get("theme.muted_text_color", "#666666"))

    out_dir = config.renders_dir_for_mode(avatar_dir, mode)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "summary_2x2_combined.png"
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)
    return out_path
