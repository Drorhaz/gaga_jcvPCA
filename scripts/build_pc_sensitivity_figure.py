"""Sensitivity of the avatar result to how much movement variance is kept.

Re-runs the pooled link-level comparison while keeping only the leading principal
components needed to explain 50%, 60% and 70% of movement variance, and contrasts each
with the full retained set used in the main figure. Both the magnitude ratio and the
signed direction use the same explained-variance weighting as the main figure.

Outputs:
  docs/slide45_figures/slide05/v5_pc_sensitivity.png (+ .pdf)
  docs/slide45_figures/slide05/v5_pc_sensitivity.csv

Usage:
  PYTHONPATH=src .venv/bin/python scripts/build_pc_sensitivity_figure.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = ROOT / "results_committee_case" / "marker_gap_policy_ex09_13"
OUT_PATH = ROOT / "docs" / "slide45_figures" / "slide05" / "v5_pc_sensitivity.png"

PARTICIPANTS = ("671", "252", "651", "790")
COMPARISONS = ("T1_vs_T2", "T1_vs_T3")
CMP_LABEL = {"T1_vs_T2": "mid-course", "T1_vs_T3": "end of course"}
RUN_SUFFIX = "ex09_13_contiguous_pooled"
THRESHOLDS = (0.50, 0.60, 0.70, None)
EPS = 1e-9

BAR_COLORS = {50: "#C6DBEF", 60: "#6BAED6", 70: "#2171B5", "all": "#08306B"}


def _threshold_key(threshold: float | None) -> int | str:
    return "all" if threshold is None else int(round(threshold * 100))


def _n_components(evr: pd.Series, threshold: float | None) -> int:
    """Leading components needed to reach the threshold, including the one that crosses it."""
    if threshold is None:
        return int(evr.index.max())
    cumulative = evr.sort_index().cumsum()
    reached = cumulative[cumulative >= threshold]
    return int(reached.index[0]) if len(reached) else int(evr.index.max())


def _aggregate(
    link_level: pd.DataFrame,
    evr: pd.Series,
    comparison_id: str,
    kind: str,
    n_pc: int,
) -> tuple[pd.Series, pd.Series]:
    """EVR-weighted signed sum and EVR-weighted mean |Δ| over the leading components."""
    sub = link_level[
        (link_level["comparison_id"] == comparison_id)
        & (link_level["kind"] == kind)
        & (link_level["pc"] <= n_pc)
    ]
    if sub.empty:
        return pd.Series(dtype=float), pd.Series(dtype=float)
    weights = sub["pc"].map(evr)
    signed = (sub["JcvPCA_link"] * weights).groupby(sub["link_id"]).sum()
    numerator = (sub["JcvPCA_link"].abs() * weights).groupby(sub["link_id"]).sum()
    denominator = weights.groupby(sub["link_id"]).sum()
    return signed, numerator / denominator.replace(0.0, np.nan)


def collect(results_root: Path) -> pd.DataFrame:
    rows: list[dict] = []
    for pid in PARTICIPANTS:
        run_dir = results_root / "step04_primary_runs" / pid / RUN_SUFFIX
        link_level = pd.read_csv(run_dir / "link_level_results.csv")
        jcvpca = pd.read_csv(run_dir / "jcvpca_results.csv")

        nv_id = f"{pid}_T1_R1_vs_R2"
        evr_nv = jcvpca[jcvpca["comparison_id"] == nv_id].groupby("pc")[
            "explained_variance_A"
        ].first().sort_index()

        for comparison in COMPARISONS:
            cmp_id = f"{pid}_{comparison}"
            evr_long = jcvpca[jcvpca["comparison_id"] == cmp_id].groupby("pc")[
                "explained_variance_A"
            ].first().sort_index()

            for threshold in THRESHOLDS:
                k_long = _n_components(evr_long, threshold)
                k_nv = _n_components(evr_nv, threshold)
                signed, long_abs = _aggregate(link_level, evr_long, cmp_id, "longitudinal", k_long)
                _, nv_abs = _aggregate(link_level, evr_nv, nv_id, "natural_variability", k_nv)

                shared = long_abs.index.intersection(nv_abs.index)
                for link_id in shared:
                    ratio = float(long_abs[link_id] / (nv_abs[link_id] + EPS))
                    rows.append(
                        {
                            "participant": pid,
                            "comparison": comparison,
                            "variance_kept": _threshold_key(threshold),
                            "n_components_longitudinal": k_long,
                            "n_components_variability": k_nv,
                            "link_id": link_id,
                            "effect_ratio": round(ratio, 4),
                            "signed": round(float(signed[link_id]), 6),
                            "above_floor": ratio > 1.0,
                            "direction": "increase" if signed[link_id] > 0 else "decrease",
                        }
                    )
    return pd.DataFrame(rows)


def plot(df: pd.DataFrame, out_path: Path) -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 400,
            "font.size": 10,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    keys = [50, 60, 70, "all"]
    panels = [(p, c) for p in PARTICIPANTS for c in COMPARISONS]

    fig = plt.figure(figsize=(13.5, 6.4))
    gs = fig.add_gridspec(
        1, 2, width_ratios=[2.35, 1.0], left=0.06, right=0.98, top=0.795, bottom=0.175, wspace=0.20
    )
    ax_counts = fig.add_subplot(gs[0, 0])
    ax_stab = fig.add_subplot(gs[0, 1])

    width = 0.20
    positions = np.arange(len(panels))
    comp_range = {}
    for i, key in enumerate(keys):
        counts = []
        for pid, comparison in panels:
            sub = df[
                (df.participant == pid)
                & (df.comparison == comparison)
                & (df.variance_kept == key)
            ]
            counts.append(int(sub.above_floor.sum()))
        ks = df[df.variance_kept == key]["n_components_longitudinal"]
        comp_range[key] = (int(ks.min()), int(ks.max()))
        offset = (i - 1.5) * width
        bars = ax_counts.bar(
            positions + offset,
            counts,
            width=width * 0.92,
            color=BAR_COLORS[key],
            edgecolor="#333333",
            linewidth=0.4,
            zorder=3,
        )
        ax_counts.bar_label(bars, fontsize=7, padding=1.5, color="#444444")

    lo, hi = comp_range["all"]
    labels = [
        f"50% of variance  ({comp_range[50][0]}–{comp_range[50][1]} components)",
        f"60% of variance  ({comp_range[60][0]}–{comp_range[60][1]} components)",
        f"70% of variance  ({comp_range[70][0]}–{comp_range[70][1]} components)",
        f"all retained  ({lo}–{hi} components, ≈80%)",
    ]
    ax_counts.legend(
        labels=labels,
        loc="upper right",
        frameon=True,
        framealpha=0.95,
        edgecolor="#DDDDDD",
        fontsize=8.5,
        handlelength=1.3,
        labelspacing=0.5,
    )

    ax_counts.set_xticks(positions)
    ax_counts.set_xticklabels(
        [f"{pid}\n{CMP_LABEL[c]}" for pid, c in panels], fontsize=8.5, linespacing=1.4
    )
    ax_counts.set_ylabel("Links above the variability floor", fontsize=9.5)
    ax_counts.set_ylim(0, max(df[df.above_floor].groupby(
        ["participant", "comparison", "variance_kept"]).size().max() + 3, 8))
    ax_counts.grid(axis="y", color="#E4E4E4", linewidth=0.7, zorder=0)
    ax_counts.set_axisbelow(True)
    for side in ("top", "right"):
        ax_counts.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax_counts.spines[side].set_color("#999999")

    reference = df[df.variance_kept == "all"].set_index(["participant", "comparison", "link_id"])
    reference = reference[reference.above_floor]
    retained_pct, direction_pct = [], []
    for key in [50, 60, 70]:
        sub = df[df.variance_kept == key].set_index(["participant", "comparison", "link_id"])
        common = reference.index.intersection(sub.index)
        retained_pct.append(100 * sub.loc[common, "above_floor"].mean())
        direction_pct.append(
            100 * (reference.loc[common, "direction"] == sub.loc[common, "direction"]).mean()
        )

    x = np.arange(3)
    b1 = ax_stab.bar(x - 0.19, retained_pct, width=0.36, color="#9ECAE1",
                     edgecolor="#333333", linewidth=0.4, zorder=3)
    b2 = ax_stab.bar(x + 0.19, direction_pct, width=0.36, color="#FDBB84",
                     edgecolor="#333333", linewidth=0.4, zorder=3)
    ax_stab.bar_label(b1, fmt="%.0f%%", fontsize=7.5, padding=1.5, color="#444444")
    ax_stab.bar_label(b2, fmt="%.0f%%", fontsize=7.5, padding=1.5, color="#444444")
    ax_stab.set_xticks(x)
    ax_stab.set_xticklabels(["50%", "60%", "70%"], fontsize=9)
    ax_stab.set_xlabel("variance kept", fontsize=9)
    ax_stab.set_ylim(0, 138)
    ax_stab.set_yticks([0, 25, 50, 75, 100])
    ax_stab.set_yticklabels(["0", "25", "50", "75", "100%"], fontsize=8)
    ax_stab.grid(axis="y", color="#E4E4E4", linewidth=0.7, zorder=0)
    ax_stab.set_axisbelow(True)
    for side in ("top", "right"):
        ax_stab.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax_stab.spines[side].set_color("#999999")
    ax_stab.legend(
        [b1, b2],
        ["still above the floor", "same direction"],
        loc="upper center",
        ncol=2,
        frameon=False,
        fontsize=8.5,
        handlelength=1.3,
        columnspacing=1.2,
    )
    ax_stab.set_title(
        f"Agreement with the full set  (n = {len(reference)} links)",
        fontsize=9.5,
        pad=8,
        color="#333333",
    )

    fig.suptitle(
        "The result does not depend on how much movement variance is kept",
        y=0.955,
        fontsize=14.5,
        fontweight="bold",
    )
    fig.text(
        0.5,
        0.885,
        "Each threshold keeps only the leading components explaining that share of movement variance, "
        "then repeats the whole comparison",
        ha="center",
        fontsize=9.5,
        color="#555555",
    )
    fig.text(
        0.5,
        0.035,
        "Components are selected per participant and per comparison, so the same threshold can mean a "
        "different number of components for different people.\n"
        "Participant 790 is the exception: most of its links sit close to the floor, so small changes "
        "in the retained set move them across it.",
        ha="center",
        va="bottom",
        fontsize=8.5,
        color="#555555",
        linespacing=1.7,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path)
    fig.savefig(out_path.with_suffix(".pdf"))
    plt.close(fig)
    print(f"  wrote {out_path.relative_to(ROOT)} (+ .pdf)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    args = parser.parse_args()

    df = collect(args.results_root.resolve())
    csv_path = args.out.with_suffix(".csv")
    df.to_csv(csv_path, index=False)
    print(f"  wrote {csv_path.relative_to(ROOT)}")

    for key in [50, 60, 70, "all"]:
        sub = df[df.variance_kept == key]
        print(f"  {str(key):>3}: {int(sub.above_floor.sum())} links above floor")

    plot(df, args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
