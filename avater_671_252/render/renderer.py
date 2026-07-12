"""Annotated avatar renderer (RENDER_PLAN Phase 3 + 5 + signed_nv mode).

Composes one matplotlib figure per view: the 2D skeleton with per-link intensity
fills and null-space outline rings, plus the E3 top-link callouts, E4 legend,
E5 corner stats, E7 dashed unavailable segments, and E9 null-space side strip.
Writes ``{view_id}.png`` and ``{view_id}.meta.json``.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import RENDER_MODE_SIGNED, RenderConfig
from .geometry import Pose2D, pose_to_2d
from .topology import TAG_ANALYTIC, TAG_LAYOUT_ONLY, TAG_PARTICIPANT_SPECIFIC
from .viewmodel import ViewModel

_ARROW = "\u2192"      # →
_DAGGER = "\u2020"     # †


def _title(view, mode: str, region_fill: bool = False) -> str:
    comp = f"T{view.reference_timepoint[1:]}{_ARROW}T{view.target_timepoint[1:]}"
    if region_fill:
        return f"Participant {view.participant}   {comp}   ({view.space})   region heatmap"
    suffix = " signed-NV" if mode == RENDER_MODE_SIGNED else ""
    return f"Participant {view.participant}   {comp}   ({view.space}){suffix}"


def _link_fill(vm: ViewModel, edge, config: RenderConfig) -> tuple[str, bool]:
    """Return (fill_color, outline) for one analytic edge."""
    neutral = config.get("intensity.neutral_color", "#B0B0B0")
    if vm.region_fill and edge.region_id:
        rs = vm.region_styles.get(edge.region_id)
        if rs is not None:
            return rs.fill_color, False
        return neutral, False
    style = vm.link_styles.get(edge.link_id) if edge.link_id else None
    if style is None:
        return neutral, False
    return style.fill_color, style.outline


def _draw_avatar(ax, pose2d: Pose2D, vm: ViewModel, config: RenderConfig) -> bool:
    """Draw skeleton edges + joints. Returns whether any participant-specific
    (dashed) edge was drawn, so the caller can show the † footnote."""
    joint_color = config.get("theme.joint_color", "#303030")
    joint_size = float(config.get("theme.joint_size", 18))
    capsule_alpha = float(config.get("theme.capsule_alpha", 0.85))
    outline_color = config.get("dominance.outline_color", "#4A90D9")
    outline_width = float(config.get("dominance.outline_width", 3.0))
    unavail_style = config.get("unavailable.line_style", "--")
    unavail_color = config.get("unavailable.line_color", "#9AA0A6")
    unavail_width = float(config.get("unavailable.line_width", 1.5))

    capsule_width = 9.0
    used_dagger = False

    for edge in vm.edges:
        seg = pose2d.segment(edge.parent_joint, edge.child_joint)
        if seg is None:
            continue
        (x0, y0), (x1, y1) = seg
        if edge.tag == TAG_LAYOUT_ONLY:
            ax.plot([x0, x1], [y0, y1], linestyle=unavail_style, color=unavail_color,
                    linewidth=unavail_width, zorder=1)

    for edge in vm.edges:
        if edge.tag == TAG_LAYOUT_ONLY:
            continue
        seg = pose2d.segment(edge.parent_joint, edge.child_joint)
        if seg is None:
            continue
        (x0, y0), (x1, y1) = seg
        fill_color, outline = _link_fill(vm, edge, config)

        if edge.tag == TAG_PARTICIPANT_SPECIFIC or (
            not vm.region_fill and vm.link_styles.get(edge.link_id) is None
        ):
            ax.plot([x0, x1], [y0, y1], linestyle=unavail_style, color=unavail_color,
                    linewidth=unavail_width + 0.5, zorder=2)
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            ax.annotate(_DAGGER, (mx, my), color=unavail_color,
                        fontsize=9, ha="center", va="center", zorder=6)
            used_dagger = True
            continue

        if outline:
            ax.plot([x0, x1], [y0, y1], color=outline_color,
                    linewidth=capsule_width + outline_width * 2,
                    solid_capstyle="round", zorder=3, alpha=0.9)
        ax.plot([x0, x1], [y0, y1], color=fill_color, linewidth=capsule_width,
                solid_capstyle="round", zorder=4, alpha=capsule_alpha)

    for _, (x, y) in pose2d.points.items():
        ax.scatter([x], [y], s=joint_size, color=joint_color, zorder=5)

    ax.set_aspect("equal")
    ax.axis("off")
    xmin, xmax, ymin, ymax = pose2d.bounds
    padx = (xmax - xmin) * 0.12 + 1e-6
    pady = (ymax - ymin) * 0.06 + 1e-6
    ax.set_xlim(xmin - padx, xmax + padx)
    ax.set_ylim(ymin - pady, ymax + pady)
    return used_dagger


def _draw_stats(fig, vm: ViewModel, config: RenderConfig) -> None:
    s = vm.stats
    fs = float(config.get("layout.stats_fontsize", 11))
    if vm.mode == RENDER_MODE_SIGNED:
        text = (
            f"Regions above NV: {s['regions_above_nv']}/{s['regions_total']}\n"
            f"Links above NV:   {s['links_above_nv']}/{s['links_total']}\n"
            f"Increased links:  {s.get('links_increased', 0)}\n"
            f"Decreased links:  {s.get('links_decreased', 0)}\n"
            f"Mixed regions:    {s.get('regions_mixed', 0)}\n"
            f"Max ratio:        {s['max_ratio']:.1f}\u00d7 NV"
        )
    else:
        text = (
            f"Regions above NV: {s['regions_above_nv']}/{s['regions_total']}\n"
            f"Links above NV:   {s['links_above_nv']}/{s['links_total']}\n"
            f"Max ratio:        {s['max_ratio']:.1f}\u00d7 NV"
        )
    fig.text(0.985, 0.965, text, ha="right", va="top", fontsize=fs, family="monospace",
             color=config.get("theme.text_color", "#1A1A1A"),
             bbox=dict(boxstyle="round", fc="#F5F5F5", ec="#CCCCCC"))


def _draw_top_links(fig, vm: ViewModel, config: RenderConfig) -> None:
    fs = float(config.get("layout.callout_fontsize", 10))
    lines: list[str] = []
    if vm.mode == RENDER_MODE_SIGNED:
        lines.append("Strongest signed above-NV links:")
        sc = vm.signed_callouts
        inc = sc.get("strongest_increased")
        dec = sc.get("strongest_decreased")
        if inc:
            lines.append(
                f"\u2191 {inc['canonical_link_name']}, "
                f"{inc['effect_ratio_vs_nv']:.1f}\u00d7 NV"
            )
        if dec:
            lines.append(
                f"\u2193 {dec['canonical_link_name']}, "
                f"{dec['effect_ratio_vs_nv']:.1f}\u00d7 NV"
            )
        if not inc and not dec:
            lines.append("(none above NV)")
        lines.append("")
        lines.append("Top above-NV links (by ratio):")
        if vm.top_links:
            for t in vm.top_links:
                sign = "+" if t.get("signed_direction") == "increased" else (
                    "-" if t.get("signed_direction") == "decreased" else " "
                )
                lines.append(
                    f"{t['rank']}. [{sign}] {t['canonical_link_name']}, "
                    f"{t['effect_ratio_vs_nv']:.1f}\u00d7 NV"
                )
        else:
            lines.append("(none above NV)")
        if vm.mixed_sign_regions:
            lines.append("")
            lines.append(f"Mixed-sign regions: {', '.join(vm.mixed_sign_regions)}")
    else:
        lines = ["Top above-NV links:"]
        if vm.top_links:
            for t in vm.top_links:
                lines.append(
                    f"{t['rank']}. {t['canonical_link_name']}, "
                    f"{t['effect_ratio_vs_nv']:.1f}\u00d7 NV"
                )
        else:
            lines.append("(none above NV)")

    fig.text(0.985, 0.55, "\n".join(lines), ha="right", va="top", fontsize=fs,
             family="monospace", color=config.get("theme.text_color", "#1A1A1A"),
             bbox=dict(boxstyle="round", fc="#FBFBFB", ec="#DDDDDD"))


def _draw_null_strip(fig, vm: ViewModel, config: RenderConfig) -> None:
    if vm.view.space != "null" or not vm.null_dominant:
        return
    fs = float(config.get("layout.side_strip_fontsize", 8))
    lines = ["Null-space dominant links", "\u2500" * 25]
    for d in vm.null_dominant:
        if vm.mode == RENDER_MODE_SIGNED:
            sign = "+" if d.get("long_jcvpca_mean", 0) > 0 else (
                "-" if d.get("long_jcvpca_mean", 0) < 0 else " "
            )
            lines.append(
                f"\u2022 [{sign}] {d['canonical_link_name']}  "
                f"({d['effect_ratio_vs_nv']:.2f}\u00d7 NV)"
            )
        else:
            lines.append(
                f"\u2022 {d['canonical_link_name']}  ({d['effect_ratio_vs_nv']:.2f}\u00d7 NV)"
            )
    fig.text(0.015, 0.9, "\n".join(lines), ha="left", va="top", fontsize=fs,
             family="monospace", color=config.get("theme.text_color", "#1A1A1A"),
             bbox=dict(boxstyle="round", fc="#F0F4FA", ec="#4A90D9"))


def _draw_region_colorbar(fig, config: RenderConfig) -> None:
    """Continuous signed gradient strip for region heatmap mode."""
    import matplotlib.colors as mcolors
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import LinearSegmentedColormap

    pal = config.signed_palette()
    strong = config.strong_ratio_threshold
    colors_list = [
        pal.get("dark_blue", "#08519C"),
        pal.get("neutral", "#B0B0B0"),
        pal.get("moderate_positive", "#FFD700"),
        pal.get("strong_positive", "#DC143C"),
    ]
    cmap = LinearSegmentedColormap.from_list("signed_nv_region", colors_list, N=256)
    sm = ScalarMappable(cmap=cmap, norm=mcolors.Normalize(vmin=-strong, vmax=strong))
    sm.set_array([])
    cax = fig.add_axes([0.015, 0.02, 0.22, 0.025])
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cb.set_ticks([-strong, -1.0, 0.0, 1.0, strong])
    cb.set_ticklabels(
        [f"-{strong:.0f}×", "-1×", "NV", "+1×", f"+{strong:.0f}×"]
    )
    cb.ax.tick_params(labelsize=7)
    cb.set_label("Region ratio vs NV (signed direction)", fontsize=7)


def _draw_legend_and_footer(fig, vm: ViewModel, config: RenderConfig,
                            used_dagger: bool) -> None:
    fs = float(config.get("layout.legend_fontsize", 8))
    if vm.region_fill:
        legend_lines = list(config.get("region_heatmap.legend_lines", []) or [])
        if not legend_lines:
            legend_lines = [
                "Full-region fill from signed region_space tables.",
                "Blue gradient  = decreased JcvPCA vs T1, beyond NV.",
                "Yellow/red     = increased JcvPCA vs T1, beyond NV.",
                "Gray           = within natural variability.",
                "Intensity      = continuous ratio vs NV (1×–3×+).",
            ]
    else:
        legend_lines = list(config.legend_lines_for_mode(vm.mode))
    legend_lines.append(config.get("nv_source_line", ""))
    if vm.mode == RENDER_MODE_SIGNED:
        caption = config.get("signed_nv.caption", "")
        if caption:
            legend_lines.append(caption)
    fig.text(0.015, 0.16, "\n".join(legend_lines), ha="left", va="top", fontsize=fs,
             family="monospace", color=config.get("theme.muted_text_color", "#666666"),
             bbox=dict(boxstyle="round", fc="#FAFAFA", ec="#DDDDDD"))

    if vm.region_fill:
        _draw_region_colorbar(fig, config)

    footer_fs = float(config.get("layout.footer_fontsize", 8))
    footer_parts = [config.get("footer.disclaimer", "")]
    if used_dagger:
        footer_parts.append(config.get("unavailable.footnote", ""))
    if vm.t3_confound:
        footer_parts.append(config.get("footer.t3_confound_text", ""))
    fig.text(0.5, 0.02, "   |   ".join(p for p in footer_parts if p),
             ha="center", va="bottom", fontsize=footer_fs,
             color=config.get("theme.muted_text_color", "#666666"), wrap=True)


def build_figure(vm: ViewModel, pose: dict, config: RenderConfig):
    """Compose the full annotated matplotlib Figure for one view (no disk write)."""
    pose2d = pose_to_2d(pose)
    w = float(config.get("layout.figure_width_in", 12.0))
    h = float(config.get("layout.figure_height_in", 8.0))
    dpi = int(config.get("layout.dpi", 150))

    fig = plt.figure(figsize=(w, h), dpi=dpi,
                     facecolor=config.get("theme.background", "#FFFFFF"))
    ax = fig.add_axes([0.24, 0.16, 0.54, 0.76])
    used_dagger = _draw_avatar(ax, pose2d, vm, config)

    fig.suptitle(_title(vm.view, vm.mode, region_fill=vm.region_fill), fontsize=float(config.get("layout.title_fontsize", 15)),
                 x=0.5, y=0.985, ha="center", weight="bold")
    _draw_stats(fig, vm, config)
    _draw_top_links(fig, vm, config)
    _draw_null_strip(fig, vm, config)
    _draw_legend_and_footer(fig, vm, config, used_dagger)
    return fig


def render_view(
    vm: ViewModel,
    pose: dict,
    config: RenderConfig,
    out_dir: Path,
) -> tuple[Path, Path]:
    """Render one view to PNG + meta JSON. Returns (png_path, meta_path)."""
    dpi = int(config.get("layout.dpi", 150))
    fig = build_figure(vm, pose, config)

    out_dir.mkdir(parents=True, exist_ok=True)
    png_path = out_dir / f"{vm.view.view_id}.png"
    meta_path = out_dir / f"{vm.view.view_id}.meta.json"
    fig.savefig(png_path, dpi=dpi)
    plt.close(fig)

    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(vm.meta_dict(), fh, indent=2)
    return png_path, meta_path
