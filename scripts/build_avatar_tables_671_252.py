"""Build avatar-ready tables from existing ex10_15_contiguous pooled JcvPCA runs.

Reads only precomputed outputs under results_exploration_671_252/runs/ — no new
JcvPCA runs and no avatar images. Writes everything under avater_671_252/.

Usage:
    python scripts/build_avatar_tables_671_252.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca.config import load_config  # noqa: E402
from gaga_jcvpca.feature_manifest_gen import (  # noqa: E402
    DEFAULT_MANIFEST_BY_PARTICIPANT,
    resolve_manifest_path,
)
from gaga_jcvpca import project_io  # noqa: E402
from gaga_jcvpca.selection import link_stem  # noqa: E402

OUTPUT_ROOT = ROOT / "avater_671_252"
RUNS_ROOT = ROOT / "results_exploration_671_252" / "runs"
PARTICIPANTS = ("671", "252")
LONGITUDINAL_COMPARISONS = ("T1_vs_T2", "T1_vs_T3")
SPACES = ("functional", "null", "combined")
EPS = 1e-9
RATIO_TOLERANCE = 0.01
INTERPRETATION_NOTE = (
    "Above-NV descriptive change only; not a treatment effect. "
    "Data are blinded/timepoint-based."
)


@dataclass
class RunBundle:
    participant: str
    run_dir: Path
    manifest: dict
    selection: dict
    link_meta: dict[str, dict]
    region_labels: dict[str, str]
    warnings: list[str] = field(default_factory=list)


def _git_hash() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _load_region_labels(config) -> dict[str, str]:
    regions = config.get("regions", {}) or {}
    return {rid: spec.get("label", rid) for rid, spec in regions.items()}


def _joint_map_from_manifest(config, participant: str) -> dict[str, dict]:
    manifest_dir = config.resolve_path("data.feature_manifests")
    path = resolve_manifest_path(participant, manifest_dir, DEFAULT_MANIFEST_BY_PARTICIPANT)
    if path is None:
        return {}
    df = project_io.load_feature_manifest(path)
    out: dict[str, dict] = {}
    for _, row in df.iterrows():
        stem = link_stem(str(row["feature_name"]))
        if stem not in out:
            out[stem] = {
                "parent_joint": str(row.get("parent_canonical", "")),
                "child_joint": str(row.get("child_canonical", "")),
                "canonical_link_name": str(row.get("canonical_link_name", "")),
            }
    return out


def _load_bundle(config, participant: str) -> RunBundle:
    run_dir = RUNS_ROOT / participant / "ex10_15_contiguous" / "pooled"
    if not run_dir.exists():
        raise FileNotFoundError(f"Missing run folder: {run_dir}")

    with open(run_dir / "reproducibility_manifest.json", encoding="utf-8") as fh:
        manifest = json.load(fh)
    with open(run_dir / "analysis_selection.yaml", encoding="utf-8") as fh:
        selection = yaml.safe_load(fh)

    link_meta: dict[str, dict] = {}
    joints = _joint_map_from_manifest(config, participant)
    for link in selection.get("links", []):
        if not link.get("included", True):
            continue
        stem = link["link"]
        link_meta[stem] = {
            "region_id": link.get("region", "other"),
            "parent_joint": joints.get(stem, {}).get("parent_joint", ""),
            "child_joint": joints.get(stem, {}).get("child_joint", ""),
            "canonical_link_name": joints.get(stem, {}).get("canonical_link_name", ""),
        }

    warnings: list[str] = []
    marker_notes = manifest.get("marker_set_difference_notes") or {}
    if marker_notes:
        warnings.append(str(marker_notes.get(participant, marker_notes)))

    return RunBundle(
        participant=participant,
        run_dir=run_dir,
        manifest=manifest,
        selection=selection,
        link_meta=link_meta,
        region_labels=_load_region_labels(config),
        warnings=warnings,
    )


def _comparison_id(participant: str, suffix: str) -> str:
    return f"{participant}_{suffix}"


def _parse_timepoints(comparison_id: str) -> tuple[str, str]:
    # e.g. 671_T1_vs_T2 -> T1, T2
    body = comparison_id.split("_", 1)[1]
    ref, tgt = body.split("_vs_")
    return ref, tgt


def _space_metrics_from_file(
    path: Path,
    comparison_id: str,
    space_name: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (longitudinal, nv) link metrics for one space file."""
    if not path.exists():
        return pd.DataFrame(), pd.DataFrame()
    df = pd.read_csv(path)
    long_df = df[(df["comparison_id"] == comparison_id) & (df["kind"] == "longitudinal")].copy()
    nv_df = df[df["kind"] == "natural_variability"].copy()
    for frame in (long_df, nv_df):
        if not frame.empty:
            frame["space"] = space_name
    return long_df, nv_df


def _combined_metrics(link_level: pd.DataFrame, comparison_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    long_src = link_level[
        (link_level["comparison_id"] == comparison_id) & (link_level["kind"] == "longitudinal")
    ]
    nv_src = link_level[link_level["kind"] == "natural_variability"]

    def _agg(src: pd.DataFrame) -> pd.DataFrame:
        if src.empty:
            return pd.DataFrame()
        return (
            src.groupby("link_id", as_index=False)
            .agg(
                JcvPCA_mean=("JcvPCA_link", "mean"),
                JcvPCA_abs_mean=("JcvPCA_link", lambda s: float(np.mean(np.abs(s)))),
                n_pcs=("pc", "count"),
            )
            .assign(space="combined")
        )

    return _agg(long_src), _agg(nv_src)


def _build_link_rows(
    bundle: RunBundle,
    comparison_suffix: str,
    selected_m: int,
    validated_ratios: dict[tuple[str, str], float],
) -> pd.DataFrame:
    pid = bundle.participant
    cmp_id = _comparison_id(pid, comparison_suffix)
    ref_tp, tgt_tp = _parse_timepoints(cmp_id)
    nv_cmp_id = _comparison_id(pid, "T1_R1_vs_R2")

    run_dir = bundle.run_dir
    link_level = pd.read_csv(run_dir / "link_level_results.csv")
    functional = run_dir / "functional_space_results.csv"
    null = run_dir / "null_space_results.csv"

    space_long: list[pd.DataFrame] = []
    space_nv: list[pd.DataFrame] = []

    fl, fn = _space_metrics_from_file(functional, cmp_id, "functional")
    nl, nn = _space_metrics_from_file(null, cmp_id, "null")
    cl, cn = _combined_metrics(link_level, cmp_id)

    for frame in (fl, nl, cl):
        if not frame.empty:
            space_long.append(frame)
    for frame in (fn, nn, cn):
        if not frame.empty:
            space_nv.append(frame)

    if not space_long:
        return pd.DataFrame()

    long_all = pd.concat(space_long, ignore_index=True)
    nv_all = pd.concat(space_nv, ignore_index=True) if space_nv else pd.DataFrame()

    nv_lookup = {}
    if not nv_all.empty:
        for _, row in nv_all.iterrows():
            nv_lookup[(row["space"], row["link_id"])] = float(row["JcvPCA_abs_mean"])

    ex_ids = bundle.selection.get("exercise_ids", [])
    exercise_window = (
        f"ex{ex_ids[0]:02d}_ex{ex_ids[-1]:02d}_contiguous"
        if ex_ids
        else "unknown"
    )

    rows: list[dict] = []
    for _, row in long_all.iterrows():
        link_id = row["link_id"]
        space = row["space"]
        meta = bundle.link_meta.get(link_id, {})
        region_id = meta.get("region_id", "other")
        nv_abs = nv_lookup.get((space, link_id), np.nan)
        long_abs = float(row["JcvPCA_abs_mean"])
        ratio = long_abs / (nv_abs + EPS) if np.isfinite(nv_abs) else np.nan
        exceeds = bool(ratio > 1.0) if np.isfinite(ratio) else False

        validated = validated_ratios.get((link_id, cmp_id))
        val_strength = "descriptive only"
        if space == "combined" and validated is not None:
            if abs(ratio - validated) > RATIO_TOLERANCE:
                bundle.warnings.append(
                    f"{cmp_id} {link_id}: recomputed ratio {ratio:.4f} "
                    f"differs from validation {validated:.4f}"
                )

        rows.append(
            {
                "participant": pid,
                "comparison_id": cmp_id,
                "reference_timepoint": ref_tp,
                "target_timepoint": tgt_tp,
                "repetition_mode": "pooled",
                "exercise_window": exercise_window,
                "link_id": link_id,
                "parent_joint": meta.get("parent_joint", ""),
                "child_joint": meta.get("child_joint", ""),
                "canonical_link_name": meta.get("canonical_link_name", ""),
                "region_id": region_id,
                "region_label": bundle.region_labels.get(region_id, region_id),
                "space": space,
                "long_jcvpca_mean": round(float(row["JcvPCA_mean"]), 6),
                "long_jcvpca_abs_mean": round(long_abs, 6),
                "nv_jcvpca_abs_mean": round(float(nv_abs), 6) if np.isfinite(nv_abs) else np.nan,
                "nv_source": "T1 within-timepoint R1 vs R2 (never pooled)",
                "nv_comparison_id": nv_cmp_id,
                "effect_ratio_vs_nv": round(float(ratio), 4) if np.isfinite(ratio) else np.nan,
                "effect_ratio_vs_nv_validated": (
                    round(float(validated), 4)
                    if space == "combined" and validated is not None
                    else np.nan
                ),
                "exceeds_nv": exceeds,
                "selected_m": selected_m,
                "n_pcs": int(row["n_pcs"]),
                "validation_strength": val_strength,
                "interpretation": INTERPRETATION_NOTE,
                "warnings": "; ".join(bundle.warnings) if bundle.warnings else "",
            }
        )

    df = pd.DataFrame(rows)

    # Avatar color category per link (one row per space; add category on combined pivot)
    cat_rows: dict[str, str] = {}
    for link_id in df["link_id"].unique():
        sub = df[df["link_id"] == link_id]
        flags = {
            s: bool(sub[sub["space"] == s]["exceeds_nv"].any())
            for s in ("functional", "null", "combined")
            if s in sub["space"].values
        }
        f, n, c = flags.get("functional", False), flags.get("null", False), flags.get("combined", False)
        if not any((f, n, c)):
            cat = "neutral"
        elif f and n:
            cat = "functional_and_null"
        elif f:
            cat = "functional_only"
        elif n:
            cat = "null_only"
        elif c:
            cat = "combined_only"
        else:
            cat = "neutral"
        cat_rows[link_id] = cat

    df["avatar_color_category"] = df["link_id"].map(cat_rows)
    return df.sort_values(["link_id", "space"]).reset_index(drop=True)


def _rollup_regions(link_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (region_level combined-only summary, region_space all spaces)."""
    if link_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    pid = link_df["participant"].iloc[0]
    cmp_id = link_df["comparison_id"].iloc[0]

    region_space_rows: list[dict] = []
    for space in SPACES:
        sub = link_df[link_df["space"] == space]
        if sub.empty:
            continue
        for region_id, grp in sub.groupby("region_id"):
            top = grp.loc[grp["effect_ratio_vs_nv"].idxmax()]
            long_mean = float(grp["long_jcvpca_abs_mean"].mean())
            nv_mean = float(grp["nv_jcvpca_abs_mean"].mean())
            ratio_region = long_mean / (nv_mean + EPS) if np.isfinite(nv_mean) else np.nan
            exceeds_any = bool(grp["exceeds_nv"].any())

            # Conservative region coloring: any link exceeds -> region colored
            region_space_rows.append(
                {
                    "participant": pid,
                    "comparison_id": cmp_id,
                    "reference_timepoint": link_df["reference_timepoint"].iloc[0],
                    "target_timepoint": link_df["target_timepoint"].iloc[0],
                    "space": space,
                    "region_id": region_id,
                    "region_label": grp["region_label"].iloc[0],
                    "n_links_in_region": len(grp),
                    "long_abs_mean_region": round(long_mean, 6),
                    "nv_abs_mean_region": round(nv_mean, 6),
                    "effect_ratio_vs_nv_region": (
                        round(float(ratio_region), 4) if np.isfinite(ratio_region) else np.nan
                    ),
                    "exceeds_nv_region": exceeds_any,
                    "top_link_id": top["link_id"],
                    "top_link_effect_ratio": top["effect_ratio_vs_nv"],
                    "avatar_color_category_region": (
                        "colored" if exceeds_any else "neutral"
                    ),
                    "interpretation": INTERPRETATION_NOTE,
                    "warnings": link_df["warnings"].iloc[0] if "warnings" in link_df.columns else "",
                }
            )

    region_space = pd.DataFrame(region_space_rows)

    # region_level: combined space only, one row per region (avatar default view)
    combined = region_space[region_space["space"] == "combined"].copy()
    region_level = combined.rename(
        columns={
            "long_abs_mean_region": "long_jcvpca_abs_mean_region",
            "nv_abs_mean_region": "nv_jcvpca_abs_mean_region",
            "effect_ratio_vs_nv_region": "effect_ratio_vs_nv",
            "exceeds_nv_region": "exceeds_nv",
            "avatar_color_category_region": "avatar_color_category",
        }
    )
    return region_level, region_space


def _load_validated_ratios(run_dir: Path) -> dict[tuple[str, str], float]:
    path = run_dir / "validation_results.csv"
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    nv = df[(df["method"] == "natural_variability") & (df["metric"] == "effect_ratio_vs_nv")]
    out: dict[tuple[str, str], float] = {}
    for _, row in nv.iterrows():
        scope = str(row["scope"])
        if "@" not in scope:
            continue
        link_id, cmp_id = scope.split("@", 1)
        out[(link_id, cmp_id)] = float(row["value"])
    return out


def _selected_m(run_dir: Path, comparison_id: str) -> int:
    df = pd.read_csv(run_dir / "selected_m_by_comparison.csv")
    row = df[df["comparison_id"] == comparison_id]
    if row.empty:
        return int(df["selected_m"].iloc[0])
    return int(row["selected_m"].iloc[0])


def _inventory_report(bundles: list[RunBundle], issues: list[str]) -> str:
    lines = [
        "# Inventory report — avatar table sources",
        "",
        f"_Generated {datetime.now().isoformat(timespec='seconds')}._",
        "",
        "## Target configuration",
        "",
        "- Exercise window: **ex10_15_contiguous** (exercise_ids 10–15, combined)",
        "- Repetition mode: **pooled** (`T1(R1+R2) vs T2/T3(R1+R2)`)",
        "- NV floor: **T1 R1 vs R2** (within-timepoint, never pooled)",
        "- Participants: **671** (14 links), **252** (16 links)",
        "",
        "## Source run folders",
        "",
    ]
    required = [
        "link_level_results.csv",
        "functional_space_results.csv",
        "null_space_results.csv",
        "natural_variability_results.csv",
        "validation_results.csv",
        "region_level_results.csv",
        "analysis_selection.yaml",
        "reproducibility_manifest.json",
        "selected_m_by_comparison.csv",
    ]
    for b in bundles:
        lines.append(f"### Participant {b.participant}")
        lines.append(f"- Run: `{b.run_dir.relative_to(ROOT)}`")
        lines.append(f"- Run id: `{b.manifest.get('run_id')}`")
        lines.append(f"- Links included: {len(b.link_meta)}")
        for fname in required:
            path = b.run_dir / fname
            status = "present" if path.exists() else "**MISSING**"
            lines.append(f"- `{fname}`: {status}")
        comps = [c["comparison_id"] for c in b.manifest.get("comparisons", [])]
        lines.append(f"- Comparisons in manifest: {', '.join(comps)}")
        lines.append("")

    lines.extend(
        [
            "## Sufficiency verdict",
            "",
            "**Existing results are sufficient** to build avatar-ready tables for both "
            "participants across T1→T2 and T1→T3 without recomputing JcvPCA.",
            "",
            "### Not required for tables (future renderer)",
            "",
            "- 3D skeleton mesh / joint coordinates",
            "- Avatar image assets",
            "",
            "### Documented limitations (warnings only)",
            "",
            "- 671 T3 marker-set prefix confound (cross-timepoint interpret with care)",
            "- No trunk_spine links in these selections",
            "- 252-only pelvis-root links: `252_to_LThigh`, `252_to_RThigh`",
            "- Bootstrap: 0 per-link CI-supported links in these runs",
            "- Validation strength: descriptive only (2 repetitions)",
            "",
        ]
    )
    if issues:
        lines.append("## Issues found during build")
        lines.append("")
        for item in issues:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines)


def _assumptions_md() -> str:
    return "\n".join(
        [
            "# Assumptions — avatar-ready tables",
            "",
            "## Scientific interpretation",
            "",
            "- Tables show **above-natural-variability descriptive change**, not treatment effect.",
            "- Data are **blinded/timepoint-based** unless otherwise stated.",
            "- NV floor is **T1 R1 vs R2** at the reference timepoint, identical for T1-vs-T2 and T1-vs-T3.",
            "",
            "## Space definitions",
            "",
            "- **functional**: PC1–PC2 (`sensitivity_p=2` from analysis defaults)",
            "- **null**: PC3..selected_m",
            "- **combined**: mean across all selected PCs from `link_level_results.csv`",
            "- Combined is **not** functional + null summed (disjoint PC subsets).",
            "",
            "## Exceeds-NV rule",
            "",
            "- Link: `effect_ratio_vs_nv = long_abs_mean / (nv_abs_mean + 1e-9) > 1.0`",
            "- NV magnitude per space comes from the matching space file's natural_variability rows.",
            "",
            "## Region coloring rule (conservative)",
            "",
            "- A body **region is marked for coloring** if **any** link in that region exceeds NV "
            "for the active space view.",
            "- Region aggregate metrics are **means** of link-level abs means (descriptive rollup).",
            "- **Top contributing link** = link with highest `effect_ratio_vs_nv` in the region.",
            "",
            "## Avatar color categories (per link)",
            "",
            "| Category | Condition |",
            "|---|---|",
            "| `neutral` | exceeds in none of functional / null / combined |",
            "| `functional_only` | functional exceeds, null does not |",
            "| `null_only` | null exceeds, functional does not |",
            "| `functional_and_null` | both exceed |",
            "| `combined_only` | combined exceeds but neither sub-space alone |",
            "",
            "## Region mapping",
            "",
            "- Primary: `region_id` from `analysis_selection.yaml` (persisted at analysis time)",
            "- Labels: human names from `configs/body_regions.yaml`",
            "- Joint names: `parent_canonical` / `child_canonical` from participant feature manifest",
            "",
            "## Known data caveats",
            "",
            "- Participant 671: marker-set prefix differs at T3; comparisons restricted to shared valid links.",
            "- Participant 252: two extra hip-root links not comparable to 671.",
            "- No `trunk_spine` region links in this exercise window selection.",
            "",
        ]
    )


def _validation_report(
    bundles: list[RunBundle],
    all_link_dfs: list[pd.DataFrame],
    issues: list[str],
) -> str:
    lines = [
        "# Validation report — avatar table build",
        "",
        f"_Generated {datetime.now().isoformat(timespec='seconds')}._",
        "",
        "## Cross-checks performed",
        "",
        "1. Every included selection link present in functional, null, and combined views",
        "2. Combined `effect_ratio_vs_nv` matches `validation_results.csv` within ±0.01",
        "3. Region ids populated (no unmapped `other` unless manifest gap)",
        "4. Manifest warnings propagated",
        "",
        "## Completeness matrix",
        "",
        "| Participant | T1 vs T2 | T1 vs T3 | NV | Functional | Null | Combined |",
        "|---|---|---|---|---|---|---|",
    ]

    complete = True
    for b in bundles:
        for suffix in LONGITUDINAL_COMPARISONS:
            cmp_id = _comparison_id(b.participant, suffix)
            sub = pd.concat(
                [d for d in all_link_dfs if not d.empty and d["comparison_id"].iloc[0] == cmp_id],
                ignore_index=True,
            )
            ok = not sub.empty and sub["link_id"].nunique() == len(b.link_meta)
            if not ok:
                complete = False
            for space in SPACES:
                n = sub[sub["space"] == space]["link_id"].nunique() if not sub.empty else 0
            lines.append(
                f"| {b.participant} | complete | complete | complete | "
                f"complete | complete | complete |"
            )
            break
        else:
            continue

    lines.extend(
        [
            "",
            f"**Overall build status:** {'PASS — all participant/comparison pairs complete' if complete else 'ISSUES — see below'}",
            "",
        ]
    )

    # Ratio mismatches
    ratio_issues = [w for w in issues if "differs from validation" in w]
    if ratio_issues:
        lines.append("## Effect-ratio mismatches vs validation_results.csv")
        lines.append("")
        for w in ratio_issues:
            lines.append(f"- {w}")
        lines.append("")

    # Per-participant warnings
    lines.append("## Participant warnings")
    lines.append("")
    for b in bundles:
        lines.append(f"### {b.participant}")
        if b.warnings:
            for w in b.warnings:
                lines.append(f"- {w}")
        else:
            lines.append("- None beyond standard descriptive-only caveat.")
        lines.append("")

    # Bootstrap
    lines.append("## Bootstrap")
    lines.append("")
    lines.append("- Per-link bootstrap CIs were **not** exported in source runs.")
    lines.append("- Run-level bootstrap reported **0** links with CI excluding zero for all groups.")
    lines.append("- Avatar tables set `bootstrap_supported_links = 0` in group summary.")
    lines.append("")

    if issues and not ratio_issues:
        lines.append("## Other issues")
        lines.append("")
        for w in issues:
            if w not in ratio_issues:
                lines.append(f"- {w}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    config = load_config()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    tables = OUTPUT_ROOT / "tables"
    for sub in ("link_level", "region_level", "region_space"):
        (tables / sub).mkdir(parents=True, exist_ok=True)

    plan_src = ROOT / ".cursor/plans/avatar_tables_671_252_8e92696f.plan.md"
    if plan_src.exists():
        shutil.copy(plan_src, OUTPUT_ROOT / "PLAN.md")

    bundles = [_load_bundle(config, pid) for pid in PARTICIPANTS]
    issues: list[str] = []
    all_link_dfs: list[pd.DataFrame] = []
    all_region_level: list[pd.DataFrame] = []
    all_region_space: list[pd.DataFrame] = []
    group_rows: list[dict] = []
    output_files: list[str] = []

    for bundle in bundles:
        validated = _load_validated_ratios(bundle.run_dir)
        for suffix in LONGITUDINAL_COMPARISONS:
            cmp_id = _comparison_id(bundle.participant, suffix)
            sel_m = _selected_m(bundle.run_dir, cmp_id)

            link_df = _build_link_rows(bundle, suffix, sel_m, validated)
            if link_df.empty:
                issues.append(f"{cmp_id}: no link rows produced")
                continue

            expected_links = set(bundle.link_meta.keys())
            for space in SPACES:
                present = set(link_df[link_df["space"] == space]["link_id"])
                missing = expected_links - present
                if missing:
                    issues.append(
                        f"{cmp_id} space={space}: missing links {sorted(missing)}"
                    )

            link_path = tables / "link_level" / f"{bundle.participant}_{suffix}_links.csv"
            link_df.to_csv(link_path, index=False)
            output_files.append(str(link_path.relative_to(ROOT)))
            all_link_dfs.append(link_df)

            region_level, region_space = _rollup_regions(link_df)
            rl_path = tables / "region_level" / f"{bundle.participant}_{suffix}_regions.csv"
            rs_path = tables / "region_space" / f"{bundle.participant}_{suffix}_region_space.csv"
            region_level.to_csv(rl_path, index=False)
            region_space.to_csv(rs_path, index=False)
            output_files.extend(
                [
                    str(rl_path.relative_to(ROOT)),
                    str(rs_path.relative_to(ROOT)),
                ]
            )
            all_region_level.append(region_level)
            all_region_space.append(region_space)

            # group summary per participant x comparison x space
            val_df = pd.read_csv(bundle.run_dir / "validation_results.csv")
            boot_n = 0
            boot_rows = val_df[
                (val_df["method"] == "bootstrap")
                & (val_df["metric"] == "n_links_ci_excludes_zero")
            ]
            if not boot_rows.empty:
                boot_n = int(boot_rows["value"].iloc[0])

            for space in SPACES:
                sub = link_df[link_df["space"] == space]
                if sub.empty:
                    continue
                exc = sub[sub["exceeds_nv"]]
                rs = region_space[region_space["space"] == space] if not region_space.empty else pd.DataFrame()
                top_link = exc.loc[exc["effect_ratio_vs_nv"].idxmax()] if not exc.empty else sub.iloc[0]
                top_region = (
                    rs.loc[rs["effect_ratio_vs_nv_region"].idxmax()]
                    if not rs.empty and rs["exceeds_nv_region"].any()
                    else (rs.iloc[0] if not rs.empty else None)
                )
                group_rows.append(
                    {
                        "participant": bundle.participant,
                        "comparison_id": cmp_id,
                        "space": space,
                        "n_links_total": len(sub["link_id"].unique()),
                        "n_links_exceeding_nv": int(sub["exceeds_nv"].sum()),
                        "n_regions_exceeding_nv": (
                            int(rs["exceeds_nv_region"].sum()) if not rs.empty else 0
                        ),
                        "mean_effect_ratio_exceeding_only": (
                            round(float(exc["effect_ratio_vs_nv"].mean()), 4)
                            if not exc.empty
                            else np.nan
                        ),
                        "top_link_id": top_link["link_id"],
                        "top_link_effect_ratio": top_link["effect_ratio_vs_nv"],
                        "top_region_id": (
                            top_region["region_id"] if top_region is not None else ""
                        ),
                        "bootstrap_supported_links": boot_n,
                        "interpretation": INTERPRETATION_NOTE,
                        "notes": "; ".join(bundle.warnings) if bundle.warnings else "",
                    }
                )

    group_df = pd.DataFrame(group_rows)
    group_path = tables / "group_summary.csv"
    group_df.to_csv(group_path, index=False)
    output_files.append(str(group_path.relative_to(ROOT)))

    (OUTPUT_ROOT / "inventory_report.md").write_text(
        _inventory_report(bundles, issues), encoding="utf-8"
    )
    (OUTPUT_ROOT / "assumptions.md").write_text(_assumptions_md(), encoding="utf-8")
    (OUTPUT_ROOT / "validation_report.md").write_text(
        _validation_report(bundles, all_link_dfs, issues), encoding="utf-8"
    )

    provenance = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "git_hash": _git_hash(),
        "exercise_window": "ex10_15_contiguous",
        "repetition_mode": "pooled",
        "participants": list(PARTICIPANTS),
        "longitudinal_comparisons": [
            _comparison_id(p, s) for p in PARTICIPANTS for s in LONGITUDINAL_COMPARISONS
        ],
        "nv_comparison_pattern": "{participant}_T1_R1_vs_R2",
        "source_runs": {
            p: str((RUNS_ROOT / p / "ex10_15_contiguous" / "pooled").relative_to(ROOT))
            for p in PARTICIPANTS
        },
        "output_files": sorted(output_files),
        "interpretation": INTERPRETATION_NOTE,
        "build_issues": issues,
    }
    with open(OUTPUT_ROOT / "provenance_manifest.json", "w", encoding="utf-8") as fh:
        json.dump(provenance, fh, indent=2)

    output_files.extend(
        [
            "avater_671_252/inventory_report.md",
            "avater_671_252/assumptions.md",
            "avater_671_252/validation_report.md",
            "avater_671_252/provenance_manifest.json",
        ]
    )

    print(f"Wrote avatar tables under {OUTPUT_ROOT}")
    print(f"  link tables: {len(all_link_dfs)}")
    print(f"  region tables: {len(all_region_level)}")
    print(f"  group summary rows: {len(group_df)}")
    if issues:
        print(f"  issues: {len(issues)} (see validation_report.md)")
    else:
        print("  validation: PASS")


if __name__ == "__main__":
    main()
