"""Step 7 — Contribution distribution (dominance vs breadth), post-hoc.

Tests "less single-joint dominance / more distributed participation" with simple,
static distribution metrics on Step-4 pooled link tables (no dynamics, no rerun):

- **top-1 share** = fraction of total link contribution carried by the top link.
- **Shannon entropy** (normalized to [0,1] by log N) across links.

Computed on the T1 reference structure (``JRW_A_link``) and the T2/T3 structure
(``JRW_B_link``), plus the change distribution (``|JcvPCA_link|``). Redistribution
direction = did top-1 share fall / entropy rise from T1 to the follow-up?

Usage: PYTHONPATH=src .venv/bin/python scripts/step07_contribution_distribution.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PARTICIPANTS = ("671", "252", "651", "790")
WINDOW = "ex09_13_contiguous"


def _top1_share(values: np.ndarray) -> float:
    total = float(np.sum(values))
    return float(np.max(values) / total) if total > 0 else float("nan")


def _norm_entropy(values: np.ndarray) -> float:
    total = float(np.sum(values))
    if total <= 0 or len(values) <= 1:
        return float("nan")
    p = values / total
    p = p[p > 0]
    h = -float(np.sum(p * np.log(p)))
    return h / np.log(len(values))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--step04-root",
        type=Path,
        default=ROOT / "results_committee_case" / "step04_primary_runs",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "results_committee_case" / "step07_contribution_distribution",
    )
    args = parser.parse_args()
    step04 = args.step04_root.resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for pid in PARTICIPANTS:
        path = step04 / pid / f"{WINDOW}_pooled" / "link_level_results.csv"
        if not path.exists():
            continue
        lt = pd.read_csv(path)
        for comp_id, g in lt.groupby("comparison_id"):
            jrw_a = g.groupby("link_id")["JRW_A_link"].mean().to_numpy()
            jrw_b = g.groupby("link_id")["JRW_B_link"].mean().to_numpy()
            delta = g.groupby("link_id")["JcvPCA_link"].mean().abs().to_numpy()
            top1_a, top1_b = _top1_share(jrw_a), _top1_share(jrw_b)
            ent_a, ent_b = _norm_entropy(jrw_a), _norm_entropy(jrw_b)
            rows.append(
                {
                    "participant": pid,
                    "comparison_id": comp_id,
                    "n_links": int(g["link_id"].nunique()),
                    "top1_share_t1": round(top1_a, 4),
                    "top1_share_followup": round(top1_b, 4),
                    "top1_share_delta": round(top1_b - top1_a, 4),
                    "entropy_t1": round(ent_a, 4),
                    "entropy_followup": round(ent_b, 4),
                    "entropy_delta": round(ent_b - ent_a, 4),
                    "top1_change_link": g.groupby("link_id")["JcvPCA_link"].mean().abs().idxmax(),
                    "redistribution": (
                        "more_distributed"
                        if (ent_b > ent_a and top1_b < top1_a)
                        else "more_concentrated"
                        if (ent_b < ent_a and top1_b > top1_a)
                        else "mixed"
                    ),
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "distribution_metrics.csv", index=False)

    lines = [
        "# Step 7 — Contribution distribution (dominance vs breadth)",
        "",
        "Static distribution of link contribution to the shared subspace. `top1_share` = "
        "fraction carried by the single top link; `entropy` = Shannon entropy normalized to [0,1]. "
        "T1 = `JRW_A` structure, follow-up = `JRW_B` structure.",
        "",
        "| participant | comparison | top1 T1→fu | entropy T1→fu | direction |",
        "|---|---|---|---|---|",
    ]
    for _, r in df.iterrows():
        lines.append(
            f"| {r['participant']} | {r['comparison_id'].split('_', 1)[1]} | "
            f"{r['top1_share_t1']:.2f}→{r['top1_share_followup']:.2f} | "
            f"{r['entropy_t1']:.2f}→{r['entropy_followup']:.2f} | {r['redistribution']} |"
        )
    lines += [
        "",
        "## Reading",
        "",
        "- **entropy ↑ + top-1 ↓** → *more distributed participation* (careful wording, supervisor-gated).",
        "- **entropy ↓ or top-1 ↑** → do not claim broader participation; report redistribution toward specific links.",
        "- These describe the retained subspace structure only; pair with S2/S3 links from `NV_PROFILE.csv`.",
        "",
    ]
    (out_dir / "distribution_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_dir.relative_to(ROOT)} ({len(df)} rows)")
    print("\n".join(lines[4:6 + len(df)]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
