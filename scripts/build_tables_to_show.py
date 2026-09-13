"""Regenerate the NV-derived curated tables in ``tables_to_show/``.

Tables 05, 06 and 09 are pure projections of Step 8 output. They were previously
hand-copied, which let them drift from ``step08_nv_and_stability/`` (the S3 column
in table 05 went stale when Step 8 was re-run after Step 5). This script rebuilds
them from the authoritative sources so a refresh is one command.

Usage:
  PYTHONPATH=src .venv/bin/python scripts/build_tables_to_show.py \
      --results-root results_committee_case/marker_gap_policy_ex09_13
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca import nv_profile

PIDS = ("671", "252", "651", "790")
TIMEPOINTS = ("T2", "T3")
TIERS = (nv_profile.TIER_S0, nv_profile.TIER_S1, nv_profile.TIER_S2, nv_profile.TIER_S3)


def _require(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required Step-8 source missing: {path}")
    return pd.read_csv(path)


def build_05_signed_tiers(profile: pd.DataFrame, tables_dir: Path) -> Path:
    out = tables_dir / "05_nv_profile_signed_tiers.csv"
    profile.to_csv(out, index=False)
    return out


def build_06_coverage_gate(coverage: pd.DataFrame, tables_dir: Path) -> Path:
    cols = [
        "participant", "comparison_id", "timepoint", "coverage_abs",
        "coverage_rel", "coverage_band", "selected_m", "n_rows_a", "n_rows_b",
    ]
    sub = coverage[coverage["comparison_id"].astype(str).str.endswith("_single_R1")]
    out = tables_dir / "06_coverage_gate_a2_estimand.csv"
    sub[[c for c in cols if c in sub.columns]].to_csv(out, index=False)
    return out


def build_09_headline_a2(profile: pd.DataFrame, tables_dir: Path) -> Path:
    has_romflat = "nv_profile_tier_romflat" in profile.columns
    rows: list[dict] = []
    for pid in PIDS:
        for tp in TIMEPOINTS:
            g = profile[
                (profile["participant"].astype(str) == pid)
                & (profile["comparison_id"] == f"{pid}_T1_vs_{tp}")
            ]
            if g.empty:
                continue
            counts = g["nv_profile_tier"].value_counts()
            row = {
                "participant": pid,
                "comparison": f"T1_vs_{tp}",
                "n_links": len(g),
                "A2_S2_pass": int(g["a2_pass"].sum()),
                **{t: int(counts.get(t, 0)) for t in TIERS},
                "coverage_band": g["coverage_band"].iloc[0],
                "coverage_rel": round(float(g["coverage_rel"].iloc[0]), 4),
                "rep_pass": bool(g["rep_pass"].iloc[0]),
            }
            if has_romflat:
                row["S3_romflat_sensitivity"] = int(
                    (g["nv_profile_tier_romflat"] == nv_profile.TIER_S3).sum()
                )
            rows.append(row)
    out = tables_dir / "09_headline_a2_summary.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-root",
        type=Path,
        default=ROOT / "results_committee_case" / "marker_gap_policy_ex09_13",
    )
    args = parser.parse_args()

    results_root = args.results_root.resolve()
    step08 = results_root / "step08_nv_and_stability"
    tables_dir = results_root / "tables_to_show"
    tables_dir.mkdir(parents=True, exist_ok=True)

    profile = _require(step08 / "NV_PROFILE.csv")
    coverage = _require(step08 / "coverage.csv")

    if "step5_organization" in profile.columns and not profile["step5_organization"].any():
        print(
            "  WARNING: step5_organization is False for every row — S3 cannot be reached. "
            "Re-run Step 5 then Step 8 before trusting these tables."
        )

    written = [
        build_05_signed_tiers(profile, tables_dir),
        build_06_coverage_gate(coverage, tables_dir),
        build_09_headline_a2(profile, tables_dir),
    ]
    for p in written:
        print(f"Wrote {p.relative_to(ROOT)}")

    tiers = profile["nv_profile_tier"].value_counts().to_dict()
    print(f"Tier totals: {tiers}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
