"""Automated render validation (RENDER_PLAN Phase 8 + signed_nv mode).

Cross-checks the rendered PNGs + meta JSON against the source tables and
``group_summary.csv``, then writes ``render_validation.md``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .config import (
    RENDER_MODE_MAGNITUDE,
    RENDER_MODE_SIGNED,
    RenderConfig,
    load_render_config,
)
from .discovery import discover_manifest
from .tables import _read_avatar_csv

_TOL = 1e-3


@dataclass
class Check:
    name: str
    passed: bool
    detail: str
    mode: str = "all"


def _load_meta(renders_dir: Path, view_id: str) -> dict | None:
    path = renders_dir / f"{view_id}.meta.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _validate_signed_tables(
    avatar_dir: Path,
    config: RenderConfig,
    manifest,
    mixed_sign_inventory: list[str],
) -> list[Check]:
    """Validate ``tables/signed_nv/`` exports against base tables and render logic."""
    checks: list[Check] = []
    signed_root = config.tables_dir_for_mode(avatar_dir, RENDER_MODE_SIGNED)
    base_root = avatar_dir / "tables"

    missing: list[str] = []
    count_mismatches: list[str] = []
    color_mismatches: list[str] = []
    mixed_csv_mismatches: list[str] = []

    expected_group = signed_root / "group_summary.csv"
    if not expected_group.exists():
        missing.append("group_summary.csv")

    csv_mixed_regions: list[str] = []

    for ts in manifest.table_sets:
        for subdir, suffix in (
            ("link_level", "_links.csv"),
            ("region_space", "_region_space.csv"),
            ("region_level", "_regions.csv"),
        ):
            base_name = f"{ts.comparison_id}{suffix}"
            signed_path = signed_root / subdir / base_name
            if subdir == "link_level":
                base_path = ts.link_level_csv
            elif subdir == "region_space":
                base_path = ts.region_space_csv
            else:
                base_path = base_root / "region_level" / base_name

            if not signed_path.exists():
                missing.append(str(signed_path.relative_to(avatar_dir)))
                continue
            if not base_path.exists():
                continue

            signed_df = _read_avatar_csv(signed_path)
            base_df = _read_avatar_csv(base_path)
            if len(signed_df) != len(base_df):
                count_mismatches.append(
                    f"{signed_path.name}: signed {len(signed_df)} vs base {len(base_df)}"
                )

            if subdir == "link_level" and len(signed_df):
                from .colors import link_style

                sample = signed_df.head(min(5, len(signed_df)))
                for _, row in sample.iterrows():
                    space = str(row["space"])
                    expected = link_style(row, space, config, mode=RENDER_MODE_SIGNED)
                    got = str(row.get("signed_fill_color", ""))
                    if got != expected.fill_color:
                        color_mismatches.append(
                            f"{row['link_id']}/{space}: csv {got} != {expected.fill_color}"
                        )

            if subdir == "region_space" and "mixed_sign" in signed_df.columns:
                for _, row in signed_df.iterrows():
                    if bool(row.get("mixed_sign")):
                        csv_mixed_regions.append(
                            f"{ts.comparison_id}_{row['space']}/{row['region_id']}"
                        )

    meta_mixed = set(mixed_sign_inventory)
    csv_mixed = set(csv_mixed_regions)
    if meta_mixed != csv_mixed:
        only_meta = sorted(meta_mixed - csv_mixed)
        only_csv = sorted(csv_mixed - meta_mixed)
        mixed_csv_mismatches.append(
            f"meta-only: {only_meta or 'none'}; csv-only: {only_csv or 'none'}"
        )

    checks.append(Check(
        "signed_nv_tables_exist",
        not missing,
        f"missing: {missing or 'none'}",
        mode=RENDER_MODE_SIGNED,
    ))
    checks.append(Check(
        "signed_nv_tables_row_counts_match_base",
        not count_mismatches,
        "; ".join(count_mismatches) or "all row counts match base tables",
        mode=RENDER_MODE_SIGNED,
    ))
    checks.append(Check(
        "signed_nv_tables_fill_color_spotcheck",
        not color_mismatches,
        "; ".join(color_mismatches) or "sample signed_fill_color values match link_style",
        mode=RENDER_MODE_SIGNED,
    ))
    checks.append(Check(
        "signed_nv_tables_mixed_sign_matches_meta",
        not mixed_csv_mismatches,
        "; ".join(mixed_csv_mismatches) or "mixed-sign inventory matches signed region_space CSVs",
        mode=RENDER_MODE_SIGNED,
    ))
    return checks


def _validate_mode(
    avatar_dir: Path,
    config: RenderConfig,
    mode: str,
) -> list[Check]:
    manifest = discover_manifest(avatar_dir)
    renders_dir = config.renders_dir_for_mode(avatar_dir, mode)
    checks: list[Check] = []
    views = manifest.views()

    missing = []
    for v in views:
        if not (renders_dir / f"{v.view_id}.png").exists():
            missing.append(f"{v.view_id}.png")
        if not (renders_dir / f"{v.view_id}.meta.json").exists():
            missing.append(f"{v.view_id}.meta.json")
    summary_name = "summary_2x2_combined.png"
    if not (renders_dir / summary_name).exists() and mode == RENDER_MODE_MAGNITUDE:
        missing.append(summary_name)
    checks.append(Check(
        f"{mode}_files_exist",
        not missing,
        f"{len(views)} views expected; missing: {missing or 'none'}",
        mode=mode,
    ))

    gs_path = manifest.tables_dir / "group_summary.csv"
    gs = _read_avatar_csv(gs_path) if gs_path.exists() else pd.DataFrame()

    region_mismatches: list[str] = []
    maxratio_mismatches: list[str] = []
    toplink_mismatches: list[str] = []
    dominance_mismatches: list[str] = []
    traceability_gaps: list[str] = []
    signed_color_mismatches: list[str] = []
    mixed_sign_inventory: list[str] = []

    for v in views:
        meta = _load_meta(renders_dir, v.view_id)
        if meta is None:
            continue
        ts = manifest.table_set(v.participant, v.comparison)
        links = _read_avatar_csv(ts.link_level_csv)
        links_space = links[links["space"] == v.space]

        if len(gs):
            gs_row = gs[(gs["participant"].astype(str) == v.participant)
                        & (gs["comparison_id"] == v.comparison_id)
                        & (gs["space"] == v.space)]
            if len(gs_row):
                expected = int(gs_row.iloc[0]["n_regions_exceeding_nv"])
                got = int(meta["stats"]["regions_above_nv"])
                if expected != got:
                    region_mismatches.append(f"{v.view_id}: expected {expected}, meta {got}")
                exp_links = int(gs_row.iloc[0]["n_links_exceeding_nv"])
                got_links = int(meta["stats"]["links_above_nv"])
                if exp_links != got_links:
                    region_mismatches.append(
                        f"{v.view_id}: links expected {exp_links}, meta {got_links}")

        exceeding = links_space[links_space["exceeds_nv"] == True]  # noqa: E712
        table_max = float(exceeding["effect_ratio_vs_nv"].max()) if len(exceeding) else 0.0
        if abs(table_max - float(meta["stats"]["max_ratio"])) > _TOL:
            maxratio_mismatches.append(
                f"{v.view_id}: table {table_max:.4f} vs meta {meta['stats']['max_ratio']}")

        top_expected = (
            exceeding.sort_values("effect_ratio_vs_nv", ascending=False)
            .head(config.top_n)["link_id"].astype(str).tolist()
        )
        top_meta = [t["link_id"] for t in meta["top_links"]]
        if top_expected != top_meta:
            toplink_mismatches.append(f"{v.view_id}: {top_meta} != {top_expected}")

        if v.space == "combined" and mode == RENDER_MODE_MAGNITUDE:
            for region in meta["regions"]:
                sl = region.get("strongest_link")
                if not sl:
                    continue
                lr = links_space[links_space["link_id"] == sl["link_id"]]
                if len(lr):
                    cat = str(lr.iloc[0]["avatar_color_category"])
                    if cat != region["dominance"]:
                        dominance_mismatches.append(
                            f"{v.view_id}/{region['region_id']}: {region['dominance']} != {cat}")

        for region in meta["regions"]:
            if region["exceeds_nv_region"] and not region.get("strongest_link"):
                traceability_gaps.append(f"{v.view_id}/{region['region_id']}")

        if mode == RENDER_MODE_SIGNED:
            from .colors import link_style

            for _, row in links_space.iterrows():
                expected_style = link_style(row, v.space, config, mode=mode)
                lid = str(row["link_id"])
                # signed colors validated via recompute (link styles not stored in meta per link)
                recomputed = expected_style.fill_color
                # meta doesn't store per-link colors; skip per-link meta check
                _ = recomputed

            for region in meta["regions"]:
                if region.get("mixed_sign"):
                    mixed_sign_inventory.append(f"{v.view_id}/{region['region_id']}")
                if region.get("mixed_sign") and not region.get("mixed_direction_warning"):
                    signed_color_mismatches.append(
                        f"{v.view_id}/{region['region_id']}: mixed_sign without warning")

            if meta.get("render_mode") != RENDER_MODE_SIGNED:
                signed_color_mismatches.append(f"{v.view_id}: missing render_mode in meta")

    checks.append(Check(
        f"{mode}_region_counts_match_group_summary",
        not region_mismatches,
        "; ".join(region_mismatches) or "all region/link counts match",
        mode=mode,
    ))
    checks.append(Check(
        f"{mode}_max_ratio_matches_table",
        not maxratio_mismatches,
        "; ".join(maxratio_mismatches) or "all max ratios match",
        mode=mode,
    ))
    checks.append(Check(
        f"{mode}_top_links_match_table",
        not toplink_mismatches,
        "; ".join(toplink_mismatches) or "all top-3 callouts match",
        mode=mode,
    ))
    if mode == RENDER_MODE_MAGNITUDE:
        checks.append(Check(
            f"{mode}_combined_dominance_matches_category",
            not dominance_mismatches,
            "; ".join(dominance_mismatches) or "all combined dominance matches",
            mode=mode,
        ))
    checks.append(Check(
        f"{mode}_region_traceability",
        not traceability_gaps,
        "; ".join(traceability_gaps) or "every above-NV region has a strongest_link",
        mode=mode,
    ))

    if mode == RENDER_MODE_MAGNITUDE:
        meta = _load_meta(renders_dir, "671_T1_vs_T2_functional")
        if meta is not None:
            hn = [r for r in meta["regions"] if r["region_id"] == "head_neck"]
            ok = bool(hn) and not hn[0]["exceeds_nv_region"]
            checks.append(Check(
                f"{mode}_spotcheck_671_functional_head_neck_neutral",
                ok,
                "head_neck within NV" if ok else "head_neck unexpectedly above NV",
                mode=mode,
            ))
            if "render_mode" in meta:
                checks.append(Check(
                    f"{mode}_meta_unchanged_no_render_mode_key",
                    False,
                    "magnitude meta should not contain render_mode key",
                    mode=mode,
                ))

    if mode == RENDER_MODE_SIGNED:
        checks.append(Check(
            f"{mode}_mixed_sign_documented",
            not signed_color_mismatches,
            "; ".join(signed_color_mismatches) or "all mixed-sign regions documented",
            mode=mode,
        ))
        checks.append(Check(
            f"{mode}_mixed_sign_inventory",
            True,
            f"{len(mixed_sign_inventory)} mixed-sign region(s): "
            + (", ".join(mixed_sign_inventory) if mixed_sign_inventory else "none"),
            mode=mode,
        ))
        checks.extend(
            _validate_signed_tables(avatar_dir, config, manifest, mixed_sign_inventory)
        )

    return checks


def validate(avatar_dir: Path, config: RenderConfig | None = None,
             modes: list[str] | None = None) -> list[Check]:
    config = config or load_render_config()
    if modes is None:
        modes = [RENDER_MODE_MAGNITUDE]
        signed_dir = config.renders_dir_for_mode(avatar_dir, RENDER_MODE_SIGNED)
        if signed_dir.exists() and any(signed_dir.glob("*.png")):
            modes.append(RENDER_MODE_SIGNED)

    checks: list[Check] = []
    for mode in modes:
        if mode == RENDER_MODE_SIGNED and not config.renders_dir_for_mode(
            avatar_dir, mode
        ).exists():
            continue
        checks.extend(_validate_mode(avatar_dir, config, mode))
    return checks


def _signed_nv_report_section(config: RenderConfig, checks: list[Check]) -> list[str]:
    signed_checks = [c for c in checks if c.mode == RENDER_MODE_SIGNED]
    if not signed_checks:
        return []

    mixed_inv = next(
        (c for c in signed_checks if c.name.endswith("_mixed_sign_inventory")), None
    )
    mixed_detail = mixed_inv.detail if mixed_inv else "none"

    return [
        "",
        "## Signed-NV render mode",
        "",
        "1. **Added as optional render mode** — default `magnitude_nv` is unchanged.",
        "2. **How to activate:** "
        "`python avater_671_252/render_avatars.py --all --render-mode signed_nv` "
        "or `--render-mode both`.",
        "3. **Color rules:** sign from `long_jcvpca_mean`; strength from "
        f"`effect_ratio_vs_nv` with moderate (1.0–{config.strong_ratio_threshold:.1f}× NV) "
        f"vs strong (>{config.strong_ratio_threshold:.1f}× NV). "
        "Dark/light blue = decreased contribution vs T1; yellow/red = increased; gray = within NV.",
        f"4. **Output location:** `renders/{config.signed_output_subdir}/{{view_id}}.png` "
        f"+ `.meta.json`, plus `summary_2x2_combined.png` in the same folder. "
        f"Signed table exports live under `tables/{config.signed_tables_subdir}/`.",
        f"5. **Mixed-sign regions:** {mixed_detail}.",
        "6. **Default mode unchanged:** magnitude outputs remain in `renders/` with "
        "the original E1 intensity legend.",
        "",
    ]


def write_report(
    avatar_dir: Path,
    config: RenderConfig | None = None,
    modes: list[str] | None = None,
) -> Path:
    config = config or load_render_config()
    if modes is None:
        modes = [RENDER_MODE_MAGNITUDE, RENDER_MODE_SIGNED]
    checks = validate(avatar_dir, config, modes=modes)
    all_pass = all(c.passed for c in checks)
    lines = [
        "# Render validation — 671 / 252 avatar views",
        "",
        f"**Overall: {'PASS' if all_pass else 'FAIL'}**",
        "",
        "| Check | Result | Detail |",
        "|---|---|---|",
    ]
    for c in checks:
        lines.append(f"| {c.name} | {'PASS' if c.passed else 'FAIL'} | {c.detail} |")
    lines.extend(_signed_nv_report_section(config, checks))
    path = avatar_dir / "render_validation.md"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return path
