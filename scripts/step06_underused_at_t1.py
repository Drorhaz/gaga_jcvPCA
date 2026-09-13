"""Step 6 — "Underused at T1" link analysis (post-hoc, no pipeline rerun).

Operationalizes the Gaga "previously underused joints become more involved" idea
WITHOUT dormant-motor language:

1. T1 baseline contribution per link = mean ``JRW_A_link`` across retained PCs
   (A = T1 reference side of the Step-4 pooled comparison; identical for T2 and T3).
2. Underused at T1 = **bottom tertile** of baseline JRW_A within participant.
3. For each underused link, read the v6 matched single-rep signed effect from
   ``NV_PROFILE.csv``: sign (increase/decrease) and A2 tier (S2/S3 = beyond NV).

Sources: step04 pooled ``link_level_results.csv`` + step08 ``NV_PROFILE.csv``.

Usage: PYTHONPATH=src .venv/bin/python scripts/step06_underused_at_t1.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PARTICIPANTS = ("671", "252", "651", "790")
WINDOW = "ex09_13_contiguous"
TERTILE = 1.0 / 3.0


def _t1_baseline(participant: str, step04: Path) -> pd.Series:
    """Mean JRW_A_link across retained PCs (T1 reference side)."""
    path = step04 / participant / f"{WINDOW}_pooled" / "link_level_results.csv"
    if not path.exists():
        return pd.Series(dtype=float)
    lt = pd.read_csv(path)
    # JRW_A is the T1 side and is identical across comparisons; use one.
    comp = lt["comparison_id"].iloc[0]
    lt = lt[lt["comparison_id"] == comp]
    return lt.groupby("link_id")["JRW_A_link"].mean()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--step04-root",
        type=Path,
        default=ROOT / "results_committee_case" / "step04_primary_runs",
    )
    parser.add_argument(
        "--step08-root",
        type=Path,
        default=ROOT / "results_committee_case" / "step08_nv_and_stability",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "results_committee_case" / "step06_underused_at_t1",
    )
    args = parser.parse_args()
    step04 = args.step04_root.resolve()
    step08 = args.step08_root.resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    profile = pd.read_csv(step08 / "NV_PROFILE.csv")
    profile["participant"] = profile["participant"].astype(str)

    rows: list[dict] = []
    for pid in PARTICIPANTS:
        baseline = _t1_baseline(pid, step04)
        if baseline.empty:
            continue
        cutoff = baseline.quantile(TERTILE)
        underused = set(baseline[baseline <= cutoff].index)
        prof = profile[profile["participant"] == pid]
        for link in sorted(baseline.index):
            for comp_id, g in prof[prof["link_id"] == link].groupby("comparison_id"):
                r = g.iloc[0]
                rows.append(
                    {
                        "participant": pid,
                        "comparison_id": comp_id,
                        "link_id": link,
                        "t1_baseline_jrw_a": round(float(baseline[link]), 6),
                        "underused_at_t1": link in underused,
                        "long_signed_single": r["long_signed_single"],
                        "increased_contribution": bool(r["long_signed_single"] > 0),
                        "nv_profile_tier": r["nv_profile_tier"],
                        "beyond_nv_a2": bool(r["a2_pass"]),
                    }
                )

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "underused_link_results.csv", index=False)

    # summary
    lines = [
        "# Step 6 — Underused-at-T1 link analysis",
        "",
        "**Underused at T1** = bottom tertile of mean `JRW_A_link` (T1 reference) within participant.",
        "**Beyond NV** = v6 matched single-rep signed A2 pass (tier S2/S3). "
        "**Increased** = `long_signed_single > 0`.",
        "",
        "| participant | comparison | N underused | N increased | N beyond-NV (A2) |",
        "|---|---|---:|---:|---:|",
    ]
    for pid in PARTICIPANTS:
        for comp_id in sorted(df[df["participant"] == pid]["comparison_id"].unique()):
            sub = df[(df["participant"] == pid) & (df["comparison_id"] == comp_id) & (df["underused_at_t1"])]
            n_u = len(sub)
            n_inc = int(sub["increased_contribution"].sum())
            n_bnv = int(sub["beyond_nv_a2"].sum())
            lines.append(f"| {pid} | {comp_id.split('_', 1)[1]} | {n_u} | {n_inc} | {n_bnv} |")

    lines += [
        "",
        "## Committee phrasing gate",
        "",
        "- Several underused links ↑ beyond NV → *consistent with broader-participation hypothesis* (interpretive, supervisor-gated).",
        "- Only high-baseline links change → do **not** claim underused activation.",
        "- Cross-check Step 5: underused ↑ with flat ROM = organization (stronger), with ROM ↑ = amplitude.",
        "- n=1 rep-pair NV floor; T3 coverage-limited for 671/252/651 — interpret those cautiously.",
        "",
    ]
    (out_dir / "underused_definition.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_dir.relative_to(ROOT)} ({len(df)} rows)")
    print("\n".join(lines[5:5 + 2 + len(PARTICIPANTS) * 2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
