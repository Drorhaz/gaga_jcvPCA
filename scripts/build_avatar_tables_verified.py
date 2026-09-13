"""Build avatar-ready tables from verified ex09_13 marker-gap NV_PROFILE.

Unlike ``build_avatar_tables_671_252.py`` (ex10_15 pooled exploration runs),
this script reads the committee-case Step-8 profile and encodes the A2/S-tier
estimand for slide-5 body maps.

Usage:
  PYTHONPATH=src .venv/bin/python scripts/build_avatar_tables_verified.py
  PYTHONPATH=src .venv/bin/python scripts/build_avatar_tables_verified.py \\
      --output-root docs/slide45_figures/avatar_verified
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca.config import load_config
from gaga_jcvpca.feature_manifest_gen import DEFAULT_MANIFEST_BY_PARTICIPANT, resolve_manifest_path
from gaga_jcvpca import project_io
from gaga_jcvpca.selection import link_stem, load_selection

PARTICIPANTS = ("671", "252", "651", "790")
COMPARISON = "T1_vs_T2"
WINDOW = "ex09_13_contiguous"
DEFAULT_RESULTS = ROOT / "results_committee_case" / "marker_gap_policy_ex09_13"
INTERPRETATION = (
    "Matched single-rep A2/S-tier from marker-gap ex09_13 run; "
    "descriptive only — not a treatment effect."
)


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


def _display_category(row: pd.Series) -> str:
    if not bool(row.get("a2_pass", False)):
        return "within_nv"
    signed = float(row.get("long_signed_single", 0.0))
    tier = str(row.get("nv_profile_tier", ""))
    if signed >= 0:
        return "s3_increase" if tier == "S3" else "a2_increase"
    return "s3_decrease" if tier == "S3" else "a2_decrease"


def build_participant_tables(
    config,
    participant: str,
    profile: pd.DataFrame,
    persistence: pd.DataFrame,
    out_tables: Path,
) -> pd.DataFrame:
    sel_path = config.resolve_path("outputs.root") / "selections" / f"{participant}_{WINDOW}.yaml"
    selection = load_selection(sel_path)
    joints = _joint_map(config, participant)
    region_labels = _region_labels(config)

    cmp_id = f"{participant}_{COMPARISON}"
    prof = profile[
        (profile["participant"].astype(str) == participant)
        & (profile["comparison_id"] == cmp_id)
    ].copy()
    prof_by_link = prof.set_index("link_id") if not prof.empty else pd.DataFrame().T

    persist_links: set[str] = set()
    if not persistence.empty:
        persist_links = set(
            persistence[
                (persistence["participant"].astype(str) == participant)
                & (persistence["persistence"] == "persistent")
            ]["link_id"].astype(str)
        )

    rows: list[dict] = []
    for link in selection.links:
        if not link.included:
            continue
        link_id = link.link
        meta = joints.get(link_id, {})
        pr = prof_by_link.loc[link_id] if link_id in prof_by_link.index else None

        if pr is not None and isinstance(pr, pd.DataFrame):
            pr = pr.iloc[0]

        base = {
            "participant": participant,
            "comparison_id": cmp_id,
            "reference_timepoint": "T1",
            "target_timepoint": "T2",
            "repetition_mode": "matched_single_R1",
            "exercise_window": WINDOW,
            "link_id": link_id,
            "parent_joint": meta.get("parent_joint", ""),
            "child_joint": meta.get("child_joint", ""),
            "canonical_link_name": meta.get("canonical_link_name", link_id),
            "region_id": link.region,
            "region_label": region_labels.get(link.region, link.region),
            "space": "combined",
            "interpretation": INTERPRETATION,
            "validation_strength": "A2 matched single-rep (Step 8)",
            "persistent": link_id in persist_links,
        }

        if pr is not None:
            long_signed = float(pr["long_signed_single"])
            nv_signed = float(pr["nv_signed_t1"])
            ratio = float(pr["matched_abs_ratio"]) if pd.notna(pr["matched_abs_ratio"]) else float("nan")
            a2 = bool(pr["a2_pass"])
            base.update(
                {
                    "long_jcvpca_mean": round(long_signed, 6),
                    "long_jcvpca_abs_mean": round(abs(long_signed), 6),
                    "nv_jcvpca_abs_mean": round(abs(nv_signed), 6),
                    "nv_signed_t1": round(nv_signed, 6),
                    "nv_source": "T1_R1 vs T1_R2 matched single-rep floor",
                    "nv_comparison_id": f"{participant}_T1_R1vsR2",
                    "effect_ratio_vs_nv": round(ratio, 4) if pd.notna(ratio) else float("nan"),
                    "exceeds_nv": a2,
                    "a2_pass": a2,
                    "magnitude_exceed": bool(pr["magnitude_exceed"]),
                    "sign_reference_stable": bool(pr["sign_reference_stable"]),
                    "nv_profile_tier": str(pr["nv_profile_tier"]),
                    "nv_profile_tier_base": str(pr.get("nv_profile_tier_base", pr["nv_profile_tier"])),
                    "selected_m": int(pr.get("selected_m", 0)) if pd.notna(pr.get("selected_m")) else 0,
                    "coverage_band": str(pr.get("coverage_band", "")),
                    "rep_pass": bool(pr.get("rep_pass", False)),
                }
            )
        else:
            base.update(
                {
                    "long_jcvpca_mean": float("nan"),
                    "long_jcvpca_abs_mean": float("nan"),
                    "nv_jcvpca_abs_mean": float("nan"),
                    "nv_signed_t1": float("nan"),
                    "nv_source": "T1_R1 vs T1_R2 matched single-rep floor",
                    "nv_comparison_id": f"{participant}_T1_R1vsR2",
                    "effect_ratio_vs_nv": float("nan"),
                    "exceeds_nv": False,
                    "a2_pass": False,
                    "magnitude_exceed": False,
                    "sign_reference_stable": False,
                    "nv_profile_tier": "untested",
                    "nv_profile_tier_base": "untested",
                    "selected_m": 0,
                    "coverage_band": "",
                    "rep_pass": False,
                }
            )

        base["display_category"] = _display_category(pd.Series(base))
        base["avatar_color_category"] = "a2_pass" if base["a2_pass"] else "neutral"
        rows.append(base)

    link_df = pd.DataFrame(rows).sort_values("link_id").reset_index(drop=True)

    link_dir = out_tables / "link_level"
    region_dir = out_tables / "region_space"
    link_dir.mkdir(parents=True, exist_ok=True)
    region_dir.mkdir(parents=True, exist_ok=True)

    link_path = link_dir / f"{participant}_{COMPARISON}_links.csv"
    link_df.to_csv(link_path, index=False)

    region_rows: list[dict] = []
    for region_id, grp in link_df.groupby("region_id"):
        a2_grp = grp[grp["a2_pass"] == True]  # noqa: E712
        top = grp.sort_values("effect_ratio_vs_nv", ascending=False).iloc[0]
        long_mean = float(grp["long_jcvpca_abs_mean"].mean()) if grp["long_jcvpca_abs_mean"].notna().any() else float("nan")
        nv_mean = float(grp["nv_jcvpca_abs_mean"].mean()) if grp["nv_jcvpca_abs_mean"].notna().any() else float("nan")
        ratio = long_mean / nv_mean if nv_mean and nv_mean > 0 else float("nan")
        region_rows.append(
            {
                "participant": participant,
                "comparison_id": cmp_id,
                "reference_timepoint": "T1",
                "target_timepoint": "T2",
                "space": "combined",
                "region_id": region_id,
                "region_label": grp["region_label"].iloc[0],
                "n_links_in_region": len(grp),
                "n_a2_links": int(len(a2_grp)),
                "long_abs_mean_region": round(long_mean, 6) if pd.notna(long_mean) else float("nan"),
                "nv_abs_mean_region": round(nv_mean, 6) if pd.notna(nv_mean) else float("nan"),
                "effect_ratio_vs_nv_region": round(ratio, 4) if pd.notna(ratio) else float("nan"),
                "exceeds_nv_region": bool(len(a2_grp)),
                "top_link_id": top["link_id"],
                "top_link_effect_ratio": top["effect_ratio_vs_nv"],
                "avatar_color_category_region": "colored" if len(a2_grp) else "neutral",
                "interpretation": INTERPRETATION,
            }
        )

    region_df = pd.DataFrame(region_rows)
    region_path = region_dir / f"{cmp_id}_region_space.csv"
    region_df.to_csv(region_path, index=False)
    return link_df


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-root",
        type=Path,
        default=DEFAULT_RESULTS,
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "docs" / "slide45_figures" / "avatar_verified",
    )
    args = parser.parse_args()

    config = load_config()
    results_root = args.results_root.resolve()
    out_root = args.output_root.resolve()
    tables_dir = out_root / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    profile = pd.read_csv(results_root / "step08_nv_and_stability" / "NV_PROFILE.csv")
    persist_path = results_root / "step09_persistence_t2_t3" / "persistence_results.csv"
    persistence = pd.read_csv(persist_path) if persist_path.exists() else pd.DataFrame()

    summaries: list[dict] = []
    for pid in PARTICIPANTS:
        df = build_participant_tables(config, pid, profile, persistence, tables_dir)
        n_a2 = int(df["a2_pass"].sum())
        n_persist = int(df["persistent"].sum())
        summaries.append({"participant": pid, "n_links": len(df), "n_a2": n_a2, "n_persistent": n_persist})
        print(f"  {pid}: {len(df)} links, A2={n_a2}, persistent={n_persist}")

    manifest = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_nv_profile": str(results_root / "step08_nv_and_stability" / "NV_PROFILE.csv"),
        "comparison": COMPARISON,
        "exercise_window": WINDOW,
        "estimand": "A2 matched single-rep (a2_pass)",
        "participants": summaries,
    }
    with open(out_root / "provenance_manifest.json", "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    print(f"\nWrote tables under {tables_dir.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
