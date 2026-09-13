"""Color + dominance mapping (RENDER_PLAN E1, E2, E3, E9 + signed_nv mode).

All numeric inputs come from the link-level and region-space tables; this module
only maps them to visual attributes using thresholds from ``render_config.yaml``.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .config import RENDER_MODE_MAGNITUDE, RENDER_MODE_SIGNED, RenderConfig

# Combined-view dominance categories (per-link, from ``avatar_color_category``).
FUNCTIONAL_ONLY = "functional_only"
NULL_ONLY = "null_only"
FUNCTIONAL_AND_NULL = "functional_and_null"
COMBINED_ONLY = "combined_only"
NEUTRAL = "neutral"

DIRECTION_INCREASED = "increased"
DIRECTION_DECREASED = "decreased"
DIRECTION_NEUTRAL = "neutral"
DIRECTION_MIXED = "mixed"


@dataclass(frozen=True)
class RegionStyle:
    """Resolved visual attributes for one analytic region in region-fill mode."""

    region_id: str
    fill_color: str
    exceeds_nv: bool
    effect_ratio_vs_nv_region: float
    signed_value: float
    signed_direction: str
    mixed_sign: bool = False
    dominant_direction: str = DIRECTION_NEUTRAL


@dataclass(frozen=True)
class LinkStyle:
    """Resolved visual attributes for one analytic link in one view."""

    link_id: str
    fill_color: str
    outline: bool          # draw the null-space ring (combined view only)
    exceeds_nv: bool
    effect_ratio_vs_nv: float
    dominance: str         # avatar_color_category
    signed_value: float = 0.0
    signed_direction: str = DIRECTION_NEUTRAL


def _num(value, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _signed_direction(value: float) -> str:
    if value > 0:
        return DIRECTION_INCREASED
    if value < 0:
        return DIRECTION_DECREASED
    return DIRECTION_NEUTRAL


def _fill_for_row(row: pd.Series, space: str, config: RenderConfig, mode: str) -> str:
    ratio = _num(row.get("effect_ratio_vs_nv"))
    exceeds = bool(row.get("exceeds_nv"))
    neutral = config.get("intensity.neutral_color", "#B0B0B0")
    dominance = str(row.get("avatar_color_category", NEUTRAL))

    if mode == RENDER_MODE_SIGNED:
        signed_val = _num(row.get("long_jcvpca_mean"))
        if space != "combined":
            return config.signed_color(signed_val, ratio, exceeds)
        fill_cats = set(config.get("dominance.fill_categories", []) or [])
        has_fill = dominance in fill_cats
        if has_fill and exceeds:
            return config.signed_color(signed_val, ratio, exceeds)
        return neutral

    if space != "combined":
        return config.intensity_color(ratio) if exceeds else neutral

    fill_cats = set(config.get("dominance.fill_categories", []) or [])
    has_fill = dominance in fill_cats
    return config.intensity_color(ratio) if (has_fill and exceeds) else neutral


def link_style(
    row: pd.Series,
    space: str,
    config: RenderConfig,
    mode: str = RENDER_MODE_MAGNITUDE,
) -> LinkStyle:
    """Fill + outline for a single link row in the active space.

    * magnitude_nv: E1 intensity scale; combined view uses E2 dual encoding.
    * signed_nv: signed contribution vs T1 thresholded by NV; combined keeps E2 outline.
    """
    ratio = _num(row.get("effect_ratio_vs_nv"))
    exceeds = bool(row.get("exceeds_nv"))
    dominance = str(row.get("avatar_color_category", NEUTRAL))
    signed_val = _num(row.get("long_jcvpca_mean"))
    fill = _fill_for_row(row, space, config, mode)

    outline = False
    if space == "combined":
        outline_cats = set(config.get("dominance.outline_categories", []) or [])
        outline = dominance in outline_cats

    return LinkStyle(
        link_id=str(row.get("link_id")),
        fill_color=fill,
        outline=outline,
        exceeds_nv=exceeds,
        effect_ratio_vs_nv=ratio,
        dominance=dominance,
        signed_value=signed_val,
        signed_direction=_signed_direction(signed_val) if exceeds else DIRECTION_NEUTRAL,
    )


def link_styles_for_space(
    links_space: pd.DataFrame,
    space: str,
    config: RenderConfig,
    mode: str = RENDER_MODE_MAGNITUDE,
) -> dict[str, LinkStyle]:
    return {
        str(row["link_id"]): link_style(row, space, config, mode=mode)
        for _, row in links_space.iterrows()
    }


def _link_callout_dict(row: pd.Series, rank: int) -> dict:
    return {
        "rank": rank,
        "link_id": str(row["link_id"]),
        "canonical_link_name": str(row.get("canonical_link_name", row["link_id"])),
        "effect_ratio_vs_nv": round(_num(row["effect_ratio_vs_nv"]), 4),
        "long_jcvpca_mean": round(_num(row["long_jcvpca_mean"]), 6),
        "signed_direction": _signed_direction(_num(row["long_jcvpca_mean"])),
    }


def top_links(
    links_space: pd.DataFrame,
    config: RenderConfig,
    n: int | None = None,
    mode: str = RENDER_MODE_MAGNITUDE,
) -> list[dict]:
    """Top-N above-NV links for the active space, sorted by ratio desc (E3)."""
    n = n or config.top_n
    eligible = links_space[links_space["exceeds_nv"] == True].copy()  # noqa: E712
    eligible = eligible.sort_values("effect_ratio_vs_nv", ascending=False)
    out: list[dict] = []
    for rank, (_, row) in enumerate(eligible.head(n).iterrows(), start=1):
        item = _link_callout_dict(row, rank)
        if mode == RENDER_MODE_MAGNITUDE:
            item.pop("long_jcvpca_mean", None)
            item.pop("signed_direction", None)
        out.append(item)
    return out


def top_signed_links(links_space: pd.DataFrame, config: RenderConfig) -> dict:
    """Strongest above-NV increased and decreased links (signed_nv callouts)."""
    eligible = links_space[links_space["exceeds_nv"] == True].copy()  # noqa: E712
    pos = eligible[eligible["long_jcvpca_mean"] > 0].sort_values(
        "effect_ratio_vs_nv", ascending=False
    )
    neg = eligible[eligible["long_jcvpca_mean"] < 0].sort_values(
        "effect_ratio_vs_nv", ascending=False
    )
    out: dict = {"strongest_increased": None, "strongest_decreased": None}
    if len(pos):
        out["strongest_increased"] = _link_callout_dict(pos.iloc[0], 1)
    if len(neg):
        out["strongest_decreased"] = _link_callout_dict(neg.iloc[0], 1)
    return out


def null_dominant_links(links_all_spaces: pd.DataFrame) -> list[dict]:
    """Every null-space exceeding link, sorted by ratio desc (E9 side strip)."""
    null_rows = links_all_spaces[
        (links_all_spaces["space"] == "null")
        & (links_all_spaces["exceeds_nv"] == True)  # noqa: E712
    ].copy()
    null_rows = null_rows.sort_values("effect_ratio_vs_nv", ascending=False)
    return [
        {
            "link_id": str(row["link_id"]),
            "canonical_link_name": str(row.get("canonical_link_name", row["link_id"])),
            "effect_ratio_vs_nv": round(_num(row["effect_ratio_vs_nv"]), 4),
            "long_jcvpca_mean": round(_num(row["long_jcvpca_mean"]), 6),
        }
        for _, row in null_rows.iterrows()
    ]


def _region_signed_value(row: pd.Series) -> float:
    """Best-effort signed JcvPCA value for a region-space row."""
    dom = str(row.get("dominant_direction", DIRECTION_NEUTRAL))
    if dom == DIRECTION_INCREASED:
        return _num(row.get("strongest_positive_long_jcvpca_mean"))
    if dom == DIRECTION_DECREASED:
        return _num(row.get("strongest_negative_long_jcvpca_mean"))
    if bool(row.get("mixed_sign")):
        pos_r = _num(row.get("strongest_positive_effect_ratio"))
        neg_r = _num(row.get("strongest_negative_effect_ratio"))
        if pos_r >= neg_r:
            return _num(row.get("strongest_positive_long_jcvpca_mean"))
        return _num(row.get("strongest_negative_long_jcvpca_mean"))
    return 0.0


def region_style_from_row(row: pd.Series, config: RenderConfig) -> RegionStyle:
    """Continuous signed region fill from a signed ``region_space`` CSV row."""
    region_id = str(row["region_id"])
    exceeds = bool(row.get("exceeds_nv_region"))
    ratio = _num(row.get("effect_ratio_vs_nv_region"))
    signed_val = _region_signed_value(row)
    mixed = bool(row.get("mixed_sign"))
    dom = str(row.get("dominant_direction", DIRECTION_NEUTRAL))
    fill = config.signed_color_continuous(signed_val, ratio, exceeds)
    return RegionStyle(
        region_id=region_id,
        fill_color=fill,
        exceeds_nv=exceeds,
        effect_ratio_vs_nv_region=ratio,
        signed_value=signed_val,
        signed_direction=_signed_direction(signed_val) if exceeds else DIRECTION_NEUTRAL,
        mixed_sign=mixed,
        dominant_direction=dom,
    )


def region_styles_for_space(
    region_space: pd.DataFrame,
    config: RenderConfig,
) -> dict[str, RegionStyle]:
    return {
        str(row["region_id"]): region_style_from_row(row, config)
        for _, row in region_space.iterrows()
    }


def signed_region_rollup(links_space: pd.DataFrame, region_id: str) -> dict:
    """Per-region signed summary: strongest +/- links, dominance, mixed_sign."""
    region_links = links_space[links_space["region_id"] == region_id]
    exceeding = region_links[region_links["exceeds_nv"] == True]  # noqa: E712
    pos = exceeding[exceeding["long_jcvpca_mean"] > 0]
    neg = exceeding[exceeding["long_jcvpca_mean"] < 0]
    mixed_sign = bool(len(pos) and len(neg))

    def _strongest(df: pd.DataFrame) -> dict | None:
        if df.empty:
            return None
        row = df.sort_values("effect_ratio_vs_nv", ascending=False).iloc[0]
        return {
            "link_id": str(row["link_id"]),
            "canonical_link_name": str(row.get("canonical_link_name", row["link_id"])),
            "effect_ratio_vs_nv": round(_num(row["effect_ratio_vs_nv"]), 4),
            "long_jcvpca_mean": round(_num(row["long_jcvpca_mean"]), 6),
            "nv_source": str(row.get("nv_source", "")),
            "nv_comparison_id": str(row.get("nv_comparison_id", "")),
        }

    strongest_pos = _strongest(pos)
    strongest_neg = _strongest(neg)

    if mixed_sign:
        pos_ratio = _num(strongest_pos["effect_ratio_vs_nv"]) if strongest_pos else 0.0
        neg_ratio = _num(strongest_neg["effect_ratio_vs_nv"]) if strongest_neg else 0.0
        if pos_ratio > neg_ratio:
            dominant_direction = DIRECTION_INCREASED
        elif neg_ratio > pos_ratio:
            dominant_direction = DIRECTION_DECREASED
        else:
            dominant_direction = DIRECTION_MIXED
    elif len(pos):
        dominant_direction = DIRECTION_INCREASED
    elif len(neg):
        dominant_direction = DIRECTION_DECREASED
    else:
        dominant_direction = DIRECTION_NEUTRAL

    return {
        "mixed_sign": mixed_sign,
        "dominant_direction": dominant_direction,
        "strongest_positive_link": strongest_pos,
        "strongest_negative_link": strongest_neg,
        "n_links_increased": int(len(pos)),
        "n_links_decreased": int(len(neg)),
    }


def view_stats(
    links_space: pd.DataFrame,
    region_space: pd.DataFrame,
    mode: str = RENDER_MODE_MAGNITUDE,
) -> dict:
    """Corner stats (E5): regions above NV, links above NV, global max ratio."""
    links_total = int(links_space["link_id"].nunique())
    links_above = int((links_space["exceeds_nv"] == True).sum())  # noqa: E712
    regions_total = int(region_space["region_id"].nunique())
    regions_above = int((region_space["exceeds_nv_region"] == True).sum())  # noqa: E712
    exceeding = links_space[links_space["exceeds_nv"] == True]  # noqa: E712
    max_ratio = float(exceeding["effect_ratio_vs_nv"].max()) if len(exceeding) else 0.0
    stats = {
        "regions_above_nv": regions_above,
        "regions_total": regions_total,
        "links_above_nv": links_above,
        "links_total": links_total,
        "max_ratio": round(max_ratio, 4),
    }
    if mode == RENDER_MODE_SIGNED:
        regions_increased = 0
        regions_decreased = 0
        regions_mixed = 0
        for region_id in region_space["region_id"].unique():
            rollup = signed_region_rollup(links_space, str(region_id))
            if not rollup["mixed_sign"]:
                if rollup["dominant_direction"] == DIRECTION_INCREASED:
                    regions_increased += 1
                elif rollup["dominant_direction"] == DIRECTION_DECREASED:
                    regions_decreased += 1
            else:
                regions_mixed += 1
        stats["regions_increased"] = regions_increased
        stats["regions_decreased"] = regions_decreased
        stats["regions_mixed"] = regions_mixed
        stats["links_increased"] = int((exceeding["long_jcvpca_mean"] > 0).sum())
        stats["links_decreased"] = int((exceeding["long_jcvpca_mean"] < 0).sum())
    return stats
