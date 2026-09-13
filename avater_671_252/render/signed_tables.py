"""Build signed-NV table exports under ``tables/signed_nv/`` from base magnitude tables.

Derives signed render columns using the same rules as ``colors.py``; no JcvPCA re-run.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from . import colors
from .config import RENDER_MODE_SIGNED, RenderConfig, load_render_config
from .discovery import RenderManifest, discover_manifest
from .tables import _read_avatar_csv

_SPACES = ("functional", "null", "combined")
_MIXED_WARNING = (
    "Mixed-sign above-NV links in region; links retain individual signed colors."
)


@dataclass
class SignedTableExport:
    path: Path
    row_count: int


@dataclass
class SignedTablesResult:
    exports: list[SignedTableExport]
    group_summary: SignedTableExport | None


def _signed_strength(ratio: float, exceeds: bool, config: RenderConfig) -> str:
    if not exceeds:
        return "within_nv"
    if float(ratio) > config.strong_ratio_threshold + 1e-12:
        return "strong"
    return "moderate"


def _flatten_rollup(rollup: dict) -> dict:
    pos = rollup.get("strongest_positive_link") or {}
    neg = rollup.get("strongest_negative_link") or {}
    mixed = bool(rollup.get("mixed_sign"))
    return {
        "mixed_sign": mixed,
        "dominant_direction": rollup.get("dominant_direction", colors.DIRECTION_NEUTRAL),
        "n_links_increased": rollup.get("n_links_increased", 0),
        "n_links_decreased": rollup.get("n_links_decreased", 0),
        "strongest_positive_link_id": pos.get("link_id", ""),
        "strongest_positive_effect_ratio": pos.get("effect_ratio_vs_nv", ""),
        "strongest_positive_long_jcvpca_mean": pos.get("long_jcvpca_mean", ""),
        "strongest_negative_link_id": neg.get("link_id", ""),
        "strongest_negative_effect_ratio": neg.get("effect_ratio_vs_nv", ""),
        "strongest_negative_long_jcvpca_mean": neg.get("long_jcvpca_mean", ""),
        "mixed_direction_warning": _MIXED_WARNING if mixed else "",
    }


def enrich_link_level(links: pd.DataFrame, config: RenderConfig) -> pd.DataFrame:
    """Append signed render columns to a link-level table."""
    out = links.copy()
    signed_dirs: list[str] = []
    strengths: list[str] = []
    fill_colors: list[str] = []
    outlines: list[bool] = []

    for _, row in out.iterrows():
        space = str(row["space"])
        style = colors.link_style(row, space, config, mode=RENDER_MODE_SIGNED)
        ratio = float(row.get("effect_ratio_vs_nv") or 0.0)
        exceeds = bool(row.get("exceeds_nv"))
        signed_dirs.append(style.signed_direction)
        strengths.append(_signed_strength(ratio, exceeds, config))
        fill_colors.append(style.fill_color)
        outlines.append(style.outline)

    out["signed_direction"] = signed_dirs
    out["signed_strength"] = strengths
    out["signed_fill_color"] = fill_colors
    out["combined_outline"] = outlines
    return out


def enrich_region_space(
    region_space: pd.DataFrame,
    links: pd.DataFrame,
    config: RenderConfig,
) -> pd.DataFrame:
    """Append signed region rollup columns to a region-space table."""
    out = region_space.copy()
    rollup_rows: list[dict] = []

    for _, row in out.iterrows():
        space = str(row["space"])
        region_id = str(row["region_id"])
        links_space = links[links["space"] == space]
        rollup = colors.signed_region_rollup(links_space, region_id)
        rollup_rows.append(_flatten_rollup(rollup))

    rollup_df = pd.DataFrame(rollup_rows)
    return pd.concat([out.reset_index(drop=True), rollup_df], axis=1)


def derive_region_level(region_space_signed: pd.DataFrame) -> pd.DataFrame:
    """Combined-space region summary with signed columns (mirrors base builder)."""
    combined = region_space_signed[region_space_signed["space"] == "combined"].copy()
    return combined.rename(
        columns={
            "long_abs_mean_region": "long_jcvpca_abs_mean_region",
            "nv_abs_mean_region": "nv_jcvpca_abs_mean_region",
            "effect_ratio_vs_nv_region": "effect_ratio_vs_nv",
            "exceeds_nv_region": "exceeds_nv",
            "avatar_color_category_region": "avatar_color_category",
        }
    )


def _top_signed_links(links_space: pd.DataFrame) -> tuple[str, str]:
    exceeding = links_space[links_space["exceeds_nv"] == True]  # noqa: E712
    pos = exceeding[exceeding["long_jcvpca_mean"] > 0].sort_values(
        "effect_ratio_vs_nv", ascending=False
    )
    neg = exceeding[exceeding["long_jcvpca_mean"] < 0].sort_values(
        "effect_ratio_vs_nv", ascending=False
    )
    top_inc = str(pos.iloc[0]["link_id"]) if len(pos) else ""
    top_dec = str(neg.iloc[0]["link_id"]) if len(neg) else ""
    return top_inc, top_dec


def build_group_summary(
    manifest: RenderManifest,
    signed_dir: Path,
    config: RenderConfig,
) -> pd.DataFrame:
    """Build signed group summary mirroring base ``group_summary.csv`` plus signed counts."""
    base_gs_path = manifest.tables_dir / "group_summary.csv"
    base_gs = _read_avatar_csv(base_gs_path) if base_gs_path.exists() else pd.DataFrame()
    rows: list[dict] = []

    for ts in manifest.table_sets:
        links_path = signed_dir / "link_level" / ts.link_level_csv.name
        rs_path = signed_dir / "region_space" / ts.region_space_csv.name
        if not links_path.exists() or not rs_path.exists():
            continue
        links = _read_avatar_csv(links_path)
        region_space = _read_avatar_csv(rs_path)

        for space in _SPACES:
            links_space = links[links["space"] == space]
            rs_space = region_space[region_space["space"] == space]
            stats = colors.view_stats(links_space, rs_space, mode=RENDER_MODE_SIGNED)
            top_inc, top_dec = _top_signed_links(links_space)

            row: dict = {
                "participant": ts.participant,
                "comparison_id": ts.comparison_id,
                "space": space,
                "render_mode": RENDER_MODE_SIGNED,
                "n_links_increased": stats.get("links_increased", 0),
                "n_links_decreased": stats.get("links_decreased", 0),
                "n_regions_increased": stats.get("regions_increased", 0),
                "n_regions_decreased": stats.get("regions_decreased", 0),
                "n_regions_mixed": stats.get("regions_mixed", 0),
                "top_increased_link_id": top_inc,
                "top_decreased_link_id": top_dec,
            }

            if not base_gs.empty:
                match = base_gs[
                    (base_gs["participant"].astype(str) == ts.participant)
                    & (base_gs["comparison_id"] == ts.comparison_id)
                    & (base_gs["space"] == space)
                ]
                if len(match):
                    base_row = match.iloc[0].to_dict()
                    for key, val in base_row.items():
                        if key not in row:
                            row[key] = val

            rows.append(row)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    # Preserve base column order first, then signed extras.
    if not base_gs.empty:
        base_cols = list(base_gs.columns)
        extra = [
            c for c in df.columns
            if c not in base_cols and c != "render_mode"
        ]
        ordered = [c for c in base_cols if c in df.columns]
        if "render_mode" in df.columns:
            ordered.append("render_mode")
        ordered.extend(c for c in extra if c not in ordered)
        df = df[ordered]
    return df


def _write_csv(df: pd.DataFrame, path: Path) -> SignedTableExport:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return SignedTableExport(path=path, row_count=len(df))


def build_all_signed_tables(
    avatar_dir: Path,
    config: RenderConfig | None = None,
) -> SignedTablesResult:
    """Export signed-NV tables for every discovered comparison."""
    config = config or load_render_config()
    manifest = discover_manifest(avatar_dir)
    signed_root = config.tables_dir_for_mode(avatar_dir, RENDER_MODE_SIGNED)
    exports: list[SignedTableExport] = []

    for ts in manifest.table_sets:
        links = _read_avatar_csv(ts.link_level_csv)
        region_space = _read_avatar_csv(ts.region_space_csv)

        signed_links = enrich_link_level(links, config)
        signed_rs = enrich_region_space(region_space, links, config)
        signed_rl = derive_region_level(signed_rs)

        link_out = signed_root / "link_level" / ts.link_level_csv.name
        rs_out = signed_root / "region_space" / ts.region_space_csv.name
        rl_out = signed_root / "region_level" / f"{ts.comparison_id}_regions.csv"

        exports.append(_write_csv(signed_links, link_out))
        exports.append(_write_csv(signed_rs, rs_out))
        exports.append(_write_csv(signed_rl, rl_out))

    group_df = build_group_summary(manifest, signed_root, config)
    group_export: SignedTableExport | None = None
    if not group_df.empty:
        group_path = signed_root / "group_summary.csv"
        group_export = _write_csv(group_df, group_path)
        exports.append(group_export)

    update_provenance_manifest(avatar_dir, exports, config)
    return SignedTablesResult(exports=exports, group_summary=group_export)


def signed_table_paths_for_comparison(
    avatar_dir: Path,
    comparison_id: str,
    config: RenderConfig | None = None,
) -> list[str]:
    """Return absolute paths to signed table files for one comparison (meta JSON)."""
    config = config or load_render_config()
    signed_root = config.tables_dir_for_mode(avatar_dir, RENDER_MODE_SIGNED)
    return [
        str((signed_root / "link_level" / f"{comparison_id}_links.csv").resolve()),
        str((signed_root / "region_space" / f"{comparison_id}_region_space.csv").resolve()),
        str((signed_root / "region_level" / f"{comparison_id}_regions.csv").resolve()),
    ]


def update_provenance_manifest(
    avatar_dir: Path,
    exports: list[SignedTableExport],
    config: RenderConfig,
) -> None:
    """Register signed table outputs in ``provenance_manifest.json``."""
    prov_path = avatar_dir / "provenance_manifest.json"
    provenance: dict = {}
    if prov_path.exists():
        with open(prov_path, "r", encoding="utf-8") as fh:
            provenance = json.load(fh)

    project_root = avatar_dir.parent
    rel_paths = sorted(str(e.path.relative_to(project_root)) for e in exports)
    row_counts = {str(e.path.relative_to(project_root)): e.row_count for e in exports}

    signed_nv_meta = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "derived_from": "avater_671_252/tables/",
        "render_config": str(config.path.relative_to(project_root)),
        "render_mode": RENDER_MODE_SIGNED,
        "output_files": rel_paths,
        "row_counts": {p: row_counts[p] for p in rel_paths},
    }
    provenance["signed_nv_tables"] = signed_nv_meta

    base_outputs = list(provenance.get("output_files", []))
    for p in rel_paths:
        if p not in base_outputs:
            base_outputs.append(p)
    provenance["output_files"] = sorted(base_outputs)

    with open(prov_path, "w", encoding="utf-8") as fh:
        json.dump(provenance, fh, indent=2)


def signed_tables_manifest_entry(
    avatar_dir: Path,
    result: SignedTablesResult,
) -> dict:
    """Summary block for ``render_manifest.json``."""
    project_root = avatar_dir.parent
    return {
        "output_dir": "tables/signed_nv",
        "n_files": len(result.exports),
        "files": [
            {
                "path": str(e.path.relative_to(project_root)),
                "row_count": e.row_count,
            }
            for e in result.exports
        ],
    }
