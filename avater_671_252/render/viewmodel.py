"""Assemble a per-view model shared by the PNG renderer and the meta JSON (E8).

Computing styles, stats, callouts, and region roll-ups in one place guarantees
the image and its metadata never disagree (a validation requirement).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from . import colors
from .config import RENDER_MODE_MAGNITUDE, RENDER_MODE_SIGNED, RenderConfig
from .discovery import TableSet, ViewSpec
from .tables import ViewTables
from .signed_tables import signed_table_paths_for_comparison
from .topology import Edge, all_edges


@dataclass
class RegionMeta:
    region_id: str
    region_label: str
    exceeds_nv_region: bool
    dominance: str
    fill_color: str
    outline: bool
    effect_ratio_vs_nv_region: float
    strongest_link: dict | None
    # signed_nv-only (optional on magnitude views)
    dominant_direction: str | None = None
    mixed_sign: bool = False
    strongest_positive_link: dict | None = None
    strongest_negative_link: dict | None = None
    mixed_direction_warning: str | None = None


@dataclass
class ViewModel:
    view: ViewSpec
    mode: str
    edges: list[Edge]
    link_styles: dict[str, colors.LinkStyle]
    stats: dict
    top_links: list[dict]
    null_dominant: list[dict]
    regions: list[RegionMeta]
    warnings_text: str
    source_tables: list[str]
    t3_confound: bool
    derived_tables: list[str] = field(default_factory=list)
    signed_callouts: dict = field(default_factory=dict)
    mixed_sign_regions: list[str] = field(default_factory=list)
    extras: dict = field(default_factory=dict)
    region_fill: bool = False
    region_styles: dict[str, colors.RegionStyle] = field(default_factory=dict)

    def meta_dict(self) -> dict:
        v = self.view
        base = {
            "view_id": v.view_id,
            "participant": v.participant,
            "comparison_id": v.comparison_id,
            "comparison": v.comparison,
            "reference_timepoint": v.reference_timepoint,
            "target_timepoint": v.target_timepoint,
            "space": v.space,
            "regions": [self._region_dict(r) for r in self.regions],
            "top_links": self.top_links,
            "null_dominant_links": self.null_dominant,
            "stats": self.stats,
            "warnings": self.warnings_text,
            "t3_confound": self.t3_confound,
            "source_tables": self.source_tables,
        }
        if self.mode == RENDER_MODE_SIGNED:
            base["render_mode"] = RENDER_MODE_SIGNED
            base["signed_callouts"] = self.signed_callouts
            base["mixed_sign_regions"] = self.mixed_sign_regions
            base["strong_ratio_threshold"] = self.extras.get("strong_ratio_threshold")
            if self.derived_tables:
                base["derived_tables"] = self.derived_tables
        if self.region_fill:
            base["region_fill"] = True
            base["region_styles"] = {
                rid: {
                    "fill_color": rs.fill_color,
                    "exceeds_nv": rs.exceeds_nv,
                    "effect_ratio_vs_nv_region": rs.effect_ratio_vs_nv_region,
                    "signed_value": rs.signed_value,
                    "signed_direction": rs.signed_direction,
                    "mixed_sign": rs.mixed_sign,
                    "dominant_direction": rs.dominant_direction,
                }
                for rid, rs in self.region_styles.items()
            }
        return base

    @staticmethod
    def _region_dict(r: RegionMeta) -> dict:
        d = {
            "region_id": r.region_id,
            "region_label": r.region_label,
            "exceeds_nv_region": r.exceeds_nv_region,
            "dominance": r.dominance,
            "fill_color": r.fill_color,
            "outline": r.outline,
            "effect_ratio_vs_nv_region": r.effect_ratio_vs_nv_region,
            "strongest_link": r.strongest_link,
        }
        if r.dominant_direction is not None:
            d["dominant_direction"] = r.dominant_direction
            d["mixed_sign"] = r.mixed_sign
            d["strongest_positive_link"] = r.strongest_positive_link
            d["strongest_negative_link"] = r.strongest_negative_link
            if r.mixed_direction_warning:
                d["mixed_direction_warning"] = r.mixed_direction_warning
        return d


def _num(value, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _region_meta_magnitude(
    vt: ViewTables,
    space: str,
    config: RenderConfig,
    link_styles: dict[str, colors.LinkStyle],
) -> list[RegionMeta]:
    out: list[RegionMeta] = []
    rs = vt.region_space
    for _, row in rs.iterrows():
        region_id = str(row["region_id"])
        exceeds = bool(row.get("exceeds_nv_region"))
        region_ratio = _num(row.get("effect_ratio_vs_nv_region"))
        top_link_id = str(row.get("top_link_id")) if not pd.isna(row.get("top_link_id")) else None

        strongest = None
        dominance = colors.NEUTRAL
        outline = False
        if top_link_id:
            link_rows = vt.links_space[vt.links_space["link_id"] == top_link_id]
            if len(link_rows):
                lr = link_rows.iloc[0]
                dominance = str(lr.get("avatar_color_category", colors.NEUTRAL))
                strongest = {
                    "link_id": top_link_id,
                    "canonical_link_name": str(lr.get("canonical_link_name", top_link_id)),
                    "effect_ratio_vs_nv": round(_num(row.get("top_link_effect_ratio")), 4),
                    "nv_source": str(lr.get("nv_source", "")),
                    "nv_comparison_id": str(lr.get("nv_comparison_id", "")),
                }
                style = link_styles.get(top_link_id)
                if style is not None:
                    outline = style.outline

        fill = config.intensity_color(region_ratio) if exceeds else config.get(
            "intensity.neutral_color", "#B0B0B0"
        )
        out.append(
            RegionMeta(
                region_id=region_id,
                region_label=str(row.get("region_label", region_id)),
                exceeds_nv_region=exceeds,
                dominance=dominance,
                fill_color=fill,
                outline=outline,
                effect_ratio_vs_nv_region=round(region_ratio, 4),
                strongest_link=strongest,
            )
        )
    order = config.regions_order
    out.sort(key=lambda r: order.index(r.region_id) if r.region_id in order else len(order))
    return out


def _region_meta_signed(
    vt: ViewTables,
    config: RenderConfig,
    link_styles: dict[str, colors.LinkStyle],
) -> list[RegionMeta]:
    out: list[RegionMeta] = []
    rs = vt.region_space
    for _, row in rs.iterrows():
        region_id = str(row["region_id"])
        exceeds = bool(row.get("exceeds_nv_region"))
        region_ratio = _num(row.get("effect_ratio_vs_nv_region"))
        rollup = colors.signed_region_rollup(vt.links_space, region_id)

        # Region capsule fill uses dominant signed link when unambiguous; mixed -> gray + warning.
        mixed = rollup["mixed_sign"]
        warning = None
        fill = config.get("intensity.neutral_color", "#B0B0B0")
        outline = False
        dominance = colors.NEUTRAL

        if exceeds and not mixed:
            dom = rollup["dominant_direction"]
            if dom == colors.DIRECTION_INCREASED and rollup["strongest_positive_link"]:
                lid = rollup["strongest_positive_link"]["link_id"]
                style = link_styles.get(lid)
                if style:
                    fill = style.fill_color
                    outline = style.outline
                    dominance = style.dominance
            elif dom == colors.DIRECTION_DECREASED and rollup["strongest_negative_link"]:
                lid = rollup["strongest_negative_link"]["link_id"]
                style = link_styles.get(lid)
                if style:
                    fill = style.fill_color
                    outline = style.outline
                    dominance = style.dominance
        elif exceeds and mixed:
            warning = (
                f"Region {region_id}: mixed-sign above-NV links "
                f"({rollup['n_links_increased']} increased, {rollup['n_links_decreased']} decreased); "
                "links retain individual signed colors."
            )

        strongest = rollup["strongest_positive_link"] or rollup["strongest_negative_link"]
        out.append(
            RegionMeta(
                region_id=region_id,
                region_label=str(row.get("region_label", region_id)),
                exceeds_nv_region=exceeds,
                dominance=dominance,
                fill_color=fill,
                outline=outline,
                effect_ratio_vs_nv_region=round(region_ratio, 4),
                strongest_link=strongest,
                dominant_direction=rollup["dominant_direction"],
                mixed_sign=mixed,
                strongest_positive_link=rollup["strongest_positive_link"],
                strongest_negative_link=rollup["strongest_negative_link"],
                mixed_direction_warning=warning,
            )
        )
    order = config.regions_order
    out.sort(key=lambda r: order.index(r.region_id) if r.region_id in order else len(order))
    return out


def _region_meta_region_heatmap(
    vt: ViewTables,
    config: RenderConfig,
    region_styles: dict[str, colors.RegionStyle],
) -> list[RegionMeta]:
    """Region capsule colors driven entirely by signed ``region_space`` rows."""
    out: list[RegionMeta] = []
    rs = vt.region_space
    for _, row in rs.iterrows():
        region_id = str(row["region_id"])
        rs_style = region_styles.get(region_id)
        if rs_style is None:
            rs_style = colors.region_style_from_row(row, config)
        exceeds = bool(row.get("exceeds_nv_region"))
        region_ratio = _num(row.get("effect_ratio_vs_nv_region"))
        mixed = bool(row.get("mixed_sign"))
        warning = None
        if mixed:
            warning = (
                f"Region {region_id}: mixed-sign above-NV links "
                f"({int(row.get('n_links_increased', 0))} increased, "
                f"{int(row.get('n_links_decreased', 0))} decreased); "
                "region color uses dominant signed direction."
            )
        strongest = None
        if rs_style.signed_direction == colors.DIRECTION_INCREASED:
            pos_id = row.get("strongest_positive_link_id")
            if pos_id and not pd.isna(pos_id):
                strongest = {
                    "link_id": str(pos_id),
                    "effect_ratio_vs_nv": round(_num(row.get("strongest_positive_effect_ratio")), 4),
                    "long_jcvpca_mean": round(_num(row.get("strongest_positive_long_jcvpca_mean")), 6),
                }
        elif rs_style.signed_direction == colors.DIRECTION_DECREASED:
            neg_id = row.get("strongest_negative_link_id")
            if neg_id and not pd.isna(neg_id):
                strongest = {
                    "link_id": str(neg_id),
                    "effect_ratio_vs_nv": round(_num(row.get("strongest_negative_effect_ratio")), 4),
                    "long_jcvpca_mean": round(_num(row.get("strongest_negative_long_jcvpca_mean")), 6),
                }
        out.append(
            RegionMeta(
                region_id=region_id,
                region_label=str(row.get("region_label", region_id)),
                exceeds_nv_region=exceeds,
                dominance=str(row.get("avatar_color_category_region", colors.NEUTRAL)),
                fill_color=rs_style.fill_color,
                outline=False,
                effect_ratio_vs_nv_region=round(region_ratio, 4),
                strongest_link=strongest,
                dominant_direction=str(row.get("dominant_direction", colors.DIRECTION_NEUTRAL)),
                mixed_sign=mixed,
                mixed_direction_warning=warning,
            )
        )
    order = config.regions_order
    out.sort(key=lambda r: order.index(r.region_id) if r.region_id in order else len(order))
    return out


def build_view_model(
    table_set: TableSet,
    vt: ViewTables,
    pose_hierarchy: dict[str, str],
    config: RenderConfig,
    mode: str = RENDER_MODE_MAGNITUDE,
    avatar_dir: Path | None = None,
    *,
    region_fill: bool = False,
) -> ViewModel:
    view = vt.view
    styles = colors.link_styles_for_space(vt.links_space, view.space, config, mode=mode)
    edges = all_edges(vt.links_all_spaces, view.participant, pose_hierarchy)
    stats = colors.view_stats(vt.links_space, vt.region_space, mode=mode)
    tops = colors.top_links(vt.links_space, config, mode=mode)
    nulls = colors.null_dominant_links(vt.links_all_spaces)

    if mode == RENDER_MODE_SIGNED:
        region_styles = colors.region_styles_for_space(vt.region_space, config)
        if region_fill:
            regions = _region_meta_region_heatmap(vt, config, region_styles)
        else:
            regions = _region_meta_signed(vt, config, styles)
        signed_callouts = colors.top_signed_links(vt.links_space, config)
        mixed_regions = [r.region_id for r in regions if r.mixed_sign]
    else:
        region_styles = {}
        regions = _region_meta_magnitude(vt, view.space, config, styles)
        signed_callouts = {}
        mixed_regions = []

    extras = {}
    derived_tables: list[str] = []
    if mode == RENDER_MODE_SIGNED:
        extras["strong_ratio_threshold"] = config.strong_ratio_threshold
        if avatar_dir is not None:
            derived_tables = signed_table_paths_for_comparison(
                avatar_dir, view.comparison_id, config,
            )

    return ViewModel(
        view=view,
        mode=mode,
        edges=edges,
        link_styles=styles,
        stats=stats,
        top_links=tops,
        null_dominant=nulls,
        regions=regions,
        warnings_text=vt.warnings_text,
        source_tables=[
            str(table_set.region_space_csv.as_posix()),
            str(table_set.link_level_csv.as_posix()),
        ],
        t3_confound=config.is_t3_confound(view.participant),
        derived_tables=derived_tables,
        signed_callouts=signed_callouts,
        mixed_sign_regions=mixed_regions,
        extras=extras,
        region_fill=region_fill,
        region_styles=region_styles,
    )
