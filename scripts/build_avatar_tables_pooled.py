"""Build avatar tables from pooled ex09_13 Step-4 runs (descriptive, no A2/S tiers).

Reads ``step04_primary_runs/{pid}/ex09_13_contiguous_pooled/`` and emits
link-level tables suitable for public-facing gradient body maps:
  - signed change in each link's coordination contribution (pooled T1 vs T2/T3)
  - comparison to the person's own between-repetition variability at T1

Usage:
  PYTHONPATH=src .venv/bin/python scripts/build_avatar_tables_pooled.py
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca.config import load_config
from gaga_jcvpca.feature_manifest_gen import DEFAULT_MANIFEST_BY_PARTICIPANT, resolve_manifest_path
from gaga_jcvpca import project_io
from gaga_jcvpca.selection import link_stem, load_selection

PARTICIPANTS = ("671", "252", "651", "790")
COMPARISONS = ("T1_vs_T2", "T1_vs_T3")
WINDOW = "ex09_13_contiguous"
RUN_SUFFIX = "ex09_13_contiguous_pooled"
DEFAULT_RESULTS = ROOT / "results_committee_case" / "marker_gap_policy_ex09_13"
EPS = 1e-9
# Amplitude treated as unchanged inside this range-of-motion ratio band (Step 5 convention).
ROM_FLAT_LO = 0.7
ROM_FLAT_HI = 1.3


def _joint_map(config, participant: str) -> dict[str, dict]:
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
                "canonical_link_name": str(row.get("canonical_link_name", stem)),
            }
    return out


def _region_labels(config) -> dict[str, str]:
    regions = config.get("regions", {}) or {}
    return {rid: spec.get("label", rid) for rid, spec in regions.items()}


def _signed_mean(link_level: pd.DataFrame, comparison_id: str, kind: str) -> pd.Series:
    sub = link_level[(link_level["comparison_id"] == comparison_id) & (link_level["kind"] == kind)]
    if sub.empty:
        return pd.Series(dtype=float)
    return sub.groupby("link_id")["JcvPCA_link"].mean()


def _evr_weights(run_dir: Path, comparison_id: str) -> pd.Series:
    """explained_variance_A per retained PC for one comparison."""
    path = run_dir / "jcvpca_results.csv"
    if not path.exists():
        return pd.Series(dtype=float)
    df = pd.read_csv(path)
    sub = df[df["comparison_id"] == comparison_id]
    if sub.empty:
        return pd.Series(dtype=float)
    return sub.groupby("pc")["explained_variance_A"].first()


def _evr_weighted_signed(
    link_level: pd.DataFrame,
    comparison_id: str,
    kind: str,
    weights: pd.Series,
) -> pd.Series:
    """Locked per-link signed aggregation: Sum_pc weight_A_pc * JcvPCA_link.

    See MASTER_EXECUTION_PLAN "Signed per-link aggregation": never mean(|d|), never a
    naive signed mean across PCs (cancels), never a cross-link average. Falls back to a
    plain signed sum when EVR weights are unavailable, per the same lock.
    """
    sub = link_level[(link_level["comparison_id"] == comparison_id) & (link_level["kind"] == kind)]
    if sub.empty:
        return pd.Series(dtype=float)
    if weights.empty:
        return sub.groupby("link_id")["JcvPCA_link"].sum()
    w = sub["pc"].map(weights)
    contrib = sub["JcvPCA_link"] * w
    return contrib.groupby(sub["link_id"]).sum()


def _evr_weighted_abs(
    link_level: pd.DataFrame,
    comparison_id: str,
    kind: str,
    weights: pd.Series,
) -> pd.Series:
    """Per-link magnitude as an explained-variance-weighted mean of |JcvPCA_link|.

    The unweighted mean gives a component explaining 3% of variance the same vote as one
    explaining 19%; weighting here keeps the magnitude on the same footing as the signed
    aggregation, so both are dominated by the components that carry the movement.
    """
    sub = link_level[(link_level["comparison_id"] == comparison_id) & (link_level["kind"] == kind)]
    if sub.empty:
        return pd.Series(dtype=float)
    if weights.empty:
        return sub.groupby("link_id")["JcvPCA_link"].apply(lambda s: s.abs().mean())
    w = sub["pc"].map(weights)
    num = (sub["JcvPCA_link"].abs() * w).groupby(sub["link_id"]).sum()
    den = w.groupby(sub["link_id"]).sum()
    return num / den.replace(0.0, np.nan)


def _load_ratios(validation_path: Path, comparison_id: str) -> dict[str, float]:
    if not validation_path.exists():
        return {}
    df = pd.read_csv(validation_path)
    nv = df[(df["method"] == "natural_variability") & (df["metric"] == "effect_ratio_vs_nv")]
    out: dict[str, float] = {}
    for _, row in nv.iterrows():
        scope = str(row["scope"])
        if "@" not in scope:
            continue
        link_id, cmp_id = scope.split("@", 1)
        if cmp_id == comparison_id:
            out[link_id] = float(row["value"])
    return out


def _load_rom(results_root: Path, comparison_id: str) -> pd.DataFrame:
    """Per-link range-of-motion ratio + amplitude/organization classification (Step 5)."""
    path = results_root / "step05_amplitude_vs_organization" / "rom_rms_by_link.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    sub = df[df["comparison_id"] == comparison_id]
    if sub.empty:
        return pd.DataFrame()
    return sub.set_index("link_id")[["rom_ratio", "rms_ratio", "classification"]]


def _load_sign_stability(results_root: Path, comparison_id: str) -> pd.Series:
    """Reference-direction stability flag per link (NV_PROFILE, single-rep basis)."""
    path = results_root / "step08_nv_and_stability" / "NV_PROFILE.csv"
    if not path.exists():
        return pd.Series(dtype=object)
    df = pd.read_csv(path)
    sub = df[df["comparison_id"] == comparison_id]
    if sub.empty:
        return pd.Series(dtype=object)
    return sub.set_index("link_id")["sign_reference_stable"]


def build_participant_comparison(
    config,
    participant: str,
    comparison_suffix: str,
    run_dir: Path,
    out_tables: Path,
    results_root: Path,
) -> pd.DataFrame:
    cmp_id = f"{participant}_{comparison_suffix}"
    nv_cmp_id = f"{participant}_T1_R1_vs_R2"

    link_level = pd.read_csv(run_dir / "link_level_results.csv")
    ratios = _load_ratios(run_dir / "validation_results.csv", cmp_id)
    rom = _load_rom(results_root, cmp_id)
    sign_stable = _load_sign_stability(results_root, cmp_id)

    long_w = _evr_weights(run_dir, cmp_id)
    nv_w = _evr_weights(run_dir, nv_cmp_id)

    long_mean = _signed_mean(link_level, cmp_id, "longitudinal")
    long_signed = _evr_weighted_signed(link_level, cmp_id, "longitudinal", long_w)
    nv_signed = _evr_weighted_signed(link_level, nv_cmp_id, "natural_variability", nv_w)
    long_abs = _evr_weighted_abs(link_level, cmp_id, "longitudinal", long_w)
    nv_abs = _evr_weighted_abs(link_level, nv_cmp_id, "natural_variability", nv_w)

    sel_path = config.resolve_path("outputs.root") / "selections" / f"{participant}_{WINDOW}.yaml"
    selection = load_selection(sel_path)
    joints = _joint_map(config, participant)
    region_labels = _region_labels(config)

    rows: list[dict] = []
    for link in selection.links:
        if not link.included:
            continue
        link_id = link.link
        meta = joints.get(link_id, {})
        ls_mean = float(long_mean.get(link_id, np.nan))
        ls = float(long_signed.get(link_id, np.nan))
        if not np.isfinite(ls) and np.isfinite(ls_mean):
            ls = ls_mean
        ns = float(nv_signed.get(link_id, np.nan))

        long_mag = float(long_abs.get(link_id, np.nan))
        nv_mag = float(nv_abs.get(link_id, np.nan))
        ratio = (
            long_mag / (nv_mag + EPS)
            if np.isfinite(long_mag) and np.isfinite(nv_mag) and nv_mag > 0
            else np.nan
        )
        ratio_unweighted = ratios.get(link_id, np.nan)

        exceeds = bool(ratio > 1.0) if np.isfinite(ratio) else False

        rom_ratio = np.nan
        rms_ratio = np.nan
        classification = ""
        if not rom.empty and link_id in rom.index:
            rom_ratio = float(rom.at[link_id, "rom_ratio"])
            rms_ratio = float(rom.at[link_id, "rms_ratio"])
            classification = str(rom.at[link_id, "classification"])
        amplitude_flat = (
            bool(ROM_FLAT_LO <= rom_ratio <= ROM_FLAT_HI) if np.isfinite(rom_ratio) else False
        )

        stable = sign_stable.get(link_id, None)
        direction_resolved = bool(stable) if stable is not None and pd.notna(stable) else False

        rows.append(
            {
                "participant": participant,
                "comparison_id": cmp_id,
                "comparison": comparison_suffix,
                "reference_timepoint": "T1",
                "target_timepoint": comparison_suffix.split("_vs_")[1],
                "repetition_mode": "pooled",
                "exercise_window": WINDOW,
                "link_id": link_id,
                "parent_joint": meta.get("parent_joint", ""),
                "child_joint": meta.get("child_joint", ""),
                "canonical_link_name": meta.get("canonical_link_name", link_id),
                "region_id": link.region,
                "region_label": region_labels.get(link.region, link.region),
                "space": "combined",
                "long_signed_mean_pc": round(ls_mean, 6) if np.isfinite(ls_mean) else np.nan,
                "long_signed": round(ls, 6) if np.isfinite(ls) else np.nan,
                "long_signed_rule": "evr_weighted_signed_sum",
                "nv_signed_t1": round(ns, 6) if np.isfinite(ns) else np.nan,
                "long_abs_evr_weighted": round(long_mag, 6) if np.isfinite(long_mag) else np.nan,
                "nv_abs_evr_weighted": round(nv_mag, 6) if np.isfinite(nv_mag) else np.nan,
                "effect_ratio_vs_variability": round(float(ratio), 4) if np.isfinite(ratio) else np.nan,
                "effect_ratio_rule": "evr_weighted_abs_mean",
                "effect_ratio_unweighted": (
                    round(float(ratio_unweighted), 4) if np.isfinite(ratio_unweighted) else np.nan
                ),
                "exceeds_variability": exceeds,
                "signed_direction": "increase" if ls > 0 else ("decrease" if ls < 0 else "neutral"),
                "direction_resolved": direction_resolved,
                "rom_ratio": round(rom_ratio, 4) if np.isfinite(rom_ratio) else np.nan,
                "rms_ratio": round(rms_ratio, 4) if np.isfinite(rms_ratio) else np.nan,
                "amplitude_flat": amplitude_flat,
                "step5_classification": classification,
            }
        )

    df = pd.DataFrame(rows).sort_values("link_id").reset_index(drop=True)
    link_dir = out_tables / "link_level"
    link_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(link_dir / f"{participant}_{comparison_suffix}_links.csv", index=False)
    return df


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "docs" / "slide45_figures" / "avatar_pooled",
    )
    args = parser.parse_args()

    config = load_config()
    results_root = args.results_root.resolve()
    out_root = args.output_root.resolve()
    tables_dir = out_root / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    summary: list[dict] = []
    for pid in PARTICIPANTS:
        run_dir = results_root / "step04_primary_runs" / pid / RUN_SUFFIX
        if not run_dir.exists():
            raise FileNotFoundError(f"Missing pooled run: {run_dir}")
        for cmp in COMPARISONS:
            df = build_participant_comparison(config, pid, cmp, run_dir, tables_dir, results_root)
            above = df[df["exceeds_variability"]]
            n_ex = len(above)
            n_flat = int(above["amplitude_flat"].sum())
            n_unresolved = int((~above["direction_resolved"]).sum())
            summary.append(
                {
                    "participant": pid,
                    "comparison": cmp,
                    "n_links": len(df),
                    "n_above_variability": n_ex,
                    "n_increase": int((above["signed_direction"] == "increase").sum()),
                    "n_decrease": int((above["signed_direction"] == "decrease").sum()),
                    "n_amplitude_flat": n_flat,
                    "n_direction_unresolved": n_unresolved,
                }
            )
            print(
                f"  {pid} {cmp}: {len(df)} links, {n_ex} above own variability "
                f"({n_flat} with unchanged range of motion, {n_unresolved} direction unresolved)"
            )

    manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": str(results_root / "step04_primary_runs"),
        "run_suffix": RUN_SUFFIX,
        "estimand": (
            "pooled combined all-PC JcvPCA: EVR-weighted |Δ|/|NV| magnitude ratio + EVR-weighted "
            "signed sum for direction (MASTER_EXECUTION_PLAN signed-aggregation lock); "
            "unweighted pipeline ratio retained as effect_ratio_unweighted"
        ),
        "amplitude_reference": "step05_amplitude_vs_organization/rom_rms_by_link.csv",
        "rom_flat_band": [ROM_FLAT_LO, ROM_FLAT_HI],
        "direction_stability_source": "step08_nv_and_stability/NV_PROFILE.csv:sign_reference_stable",
        "comparisons": list(COMPARISONS),
        "summary": summary,
    }
    with open(out_root / "provenance_manifest.json", "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    print(f"\nWrote {tables_dir.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
