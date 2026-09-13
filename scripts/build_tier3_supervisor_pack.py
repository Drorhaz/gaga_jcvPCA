"""Tier 3 supervisor pack — appendix / QC (items 9–11).

Usage:
  PYTHONPATH=src .venv/bin/python scripts/build_tier3_supervisor_pack.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PIDS = ("671", "252", "651", "790")
POOL_RUN = "ex09_13_contiguous_pooled"
REGION_ORDER = (
    "head_neck",
    "trunk_spine",
    "left_arm",
    "right_arm",
    "left_leg",
    "right_leg",
    "other",
)
REGION_LABELS = {
    "head_neck": "Head/neck",
    "trunk_spine": "Trunk/spine",
    "left_arm": "Left arm",
    "right_arm": "Right arm",
    "left_leg": "Left leg",
    "right_leg": "Right leg",
    "other": "Other",
}


def _configure_plt() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 160,
            "font.size": 10,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def _evr_by_pc(jcv: pd.DataFrame, comparison_id: str) -> dict[int, float]:
    sub = jcv[jcv["comparison_id"] == comparison_id]
    if sub.empty:
        return {}
    return {int(pc): float(ev) for pc, ev in sub.groupby("pc")["explained_variance_A"].first().items()}


def _pooled_signed(link_level: pd.DataFrame, jcv: pd.DataFrame, cid: str) -> dict[str, float]:
    evr = _evr_by_pc(jcv, cid)
    m = int(link_level[link_level["comparison_id"] == cid]["pc"].max())
    out: dict[str, float] = {}
    sub = link_level[link_level["comparison_id"] == cid]
    for link, grp in sub.groupby("link_id"):
        out[str(link)] = float(
            sum(float(r.JcvPCA_link) * evr.get(int(r.pc), 0.0) for r in grp.itertuples())
        )
    return out


def build_pooled_vs_single(
    results_root: Path, out_dir: Path, tables_dir: Path
) -> tuple[Path, Path | None]:
    prof = pd.read_csv(results_root / "step08_nv_and_stability" / "NV_PROFILE.csv")
    prof["participant"] = prof["participant"].astype(str)
    step04 = results_root / "step04_primary_runs"

    link_rows: list[dict] = []
    for pid in PIDS:
        pool_dir = step04 / pid / POOL_RUN
        lt = pd.read_csv(pool_dir / "link_level_results.csv")
        jcv = pd.read_csv(pool_dir / "jcvpca_results.csv")
        for tp in ("T2", "T3"):
            cid = f"{pid}_T1_vs_{tp}"
            pooled = _pooled_signed(lt, jcv, cid)
            sub = prof[prof["comparison_id"] == cid]
            for r in sub.itertuples():
                ps = pooled.get(str(r.link_id), np.nan)
                ls = float(r.long_signed_single)
                link_rows.append(
                    {
                        "participant": pid,
                        "comparison": f"T1_vs_{tp}",
                        "link_id": r.link_id,
                        "pooled_signed_descriptive": round(ps, 6) if np.isfinite(ps) else np.nan,
                        "single_rep_long_signed": ls,
                        "nv_signed_t1": float(r.nv_signed_t1),
                        "a2_pass": bool(r.a2_pass),
                        "nv_profile_tier": r.nv_profile_tier,
                        "same_sign": bool(np.sign(ps) == np.sign(ls))
                        if np.isfinite(ps) and ps != 0 and ls != 0
                        else False,
                        "basis_note": "pooled T1(R1+R2) vs T{k}(R1+R2); A2 estimand T1_R1 vs T{k}_R1",
                    }
                )

    by_link = pd.DataFrame(link_rows)
    by_link.to_csv(tables_dir / "09_pooled_vs_single_by_link.csv", index=False)

    summary_rows = []
    for (pid, comp), g in by_link.groupby(["participant", "comparison"]):
        valid = g[g["pooled_signed_descriptive"].notna()]
        summary_rows.append(
            {
                "participant": pid,
                "comparison": comp,
                "n_links": len(g),
                "n_a2_single_rep": int(g["a2_pass"].sum()),
                "n_same_sign_pooled_single": int(valid["same_sign"].sum()) if len(valid) else 0,
                "n_sign_flip": int((~valid["same_sign"]).sum()) if len(valid) else 0,
                "mean_abs_pooled_signed": round(float(valid["pooled_signed_descriptive"].abs().mean()), 6)
                if len(valid)
                else np.nan,
                "mean_abs_single_signed": round(float(g["single_rep_long_signed"].abs().mean()), 6),
                "basis_caveat": "Pooled uses mixed T1 anchor; A2 uses T1_R1 only",
            }
        )
    headline = pd.DataFrame(summary_rows)
    headline.to_csv(tables_dir / "09_pooled_vs_single_headline.csv", index=False)

    fig, axes = plt.subplots(2, 2, figsize=(10, 9), sharex=True, sharey=True)
    for ax, pid in zip(axes.ravel(), PIDS):
        sub = by_link[(by_link.participant == pid) & (by_link.comparison == "T1_vs_T3")]
        sub = sub[sub["pooled_signed_descriptive"].notna()]
        if sub.empty:
            ax.set_title(pid)
            continue
        colors = ["#0d904f" if a else "#9aa0a6" for a in sub["a2_pass"]]
        ax.scatter(
            sub["pooled_signed_descriptive"],
            sub["single_rep_long_signed"],
            c=colors,
            s=40,
            alpha=0.85,
            edgecolors="white",
            linewidths=0.4,
        )
        lim = max(
            sub["pooled_signed_descriptive"].abs().max(),
            sub["single_rep_long_signed"].abs().max(),
            0.01,
        )
        ax.plot([-lim, lim], [-lim, lim], "--", color="#ccc", lw=0.8)
        ax.axhline(0, color="#333", lw=0.5)
        ax.axvline(0, color="#333", lw=0.5)
        ax.set_title(f"{pid} T1→T3")
    fig.supxlabel("Pooled signed Δ (descriptive headline)")
    fig.supylabel("Single-rep signed Δ (A2 estimand, T1_R1 anchor)")
    fig.suptitle(
        "Basis caveat — pooled vs single-rep (T1→T3)\n"
        "Green = A2 pass on single-rep footing",
        fontweight="bold",
        y=1.02,
    )
    fig.tight_layout()
    scatter_path = out_dir / "09_pooled_vs_single_T3_scatter.png"
    fig.savefig(scatter_path, bbox_inches="tight")
    plt.close(fig)
    return tables_dir / "09_pooled_vs_single_headline.csv", scatter_path


def build_per_exercise_nv(results_root: Path, out_dir: Path, tables_dir: Path) -> Path:
    src = results_root / "step08_nv_and_stability" / "exercise_level_nv.csv"
    df = pd.read_csv(src)
    df["participant"] = df["participant"].astype(str)
    df.to_csv(tables_dir / "10_per_exercise_nv_layer2.csv", index=False)

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    exercises = ["ex09", "ex10", "ex11", "ex12", "ex13"]
    for ax, pid in zip(axes.ravel(), PIDS):
        sub = df[df.participant == pid]
        for tp, marker in (("T1", "o"), ("T2", "s"), ("T3", "^")):
            s = sub[sub.timepoint == tp].set_index("exercise").reindex(exercises)
            ax.plot(
                range(len(exercises)),
                s["median_abs_nv"],
                marker=marker,
                label=tp,
                alpha=0.85,
            )
        ax.set_xticks(range(len(exercises)))
        ax.set_xticklabels(exercises, rotation=45, ha="right", fontsize=8)
        ax.set_title(pid)
        ax.set_ylabel("median mean(|ΔJcvPCA|) per link")
        ax.grid(alpha=0.3)
    axes[0, 1].legend(fontsize=8, loc="upper right")
    fig.suptitle(
        "Layer 2 (firewalled) — per-exercise observed NV\n"
        "T{k}_R1 vs T{k}_R2 (R1→R2); mean(|Δ|) over PCs, median over links — not for main A2 claims",
        fontweight="bold",
        y=1.02,
        fontsize=11,
    )
    fig.tight_layout()
    path = out_dir / "10_per_exercise_nv_layer2.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)

    ratio = df[df.exercise == "ex13"].pivot(index="participant", columns="timepoint", values="ex13_over_ex09_ratio")
    ratio.to_csv(tables_dir / "10_ex13_over_ex09_ratio.csv")
    return path


def build_exclusion_region_map(
    results_root: Path, out_dir: Path, tables_dir: Path
) -> Path:
    from gaga_jcvpca.config import load_config
    from gaga_jcvpca.selection import region_of_link

    config = load_config()
    excl = pd.read_csv(results_root / "tables_to_show" / "02_comparison_link_exclusions.csv")
    excl = excl[(excl["repetition_mode"] == "pooled") & (excl["link_id"].astype(str).str.len() > 0)].copy()
    excl["participant"] = excl["participant"].astype(str)
    excl["region"] = excl["link_id"].map(lambda lk: region_of_link(str(lk), config))

    # Unique link per participant (marker-gap audit)
    uniq = excl.drop_duplicates(subset=["participant", "link_id"])
    uniq["region_label"] = uniq["region"].map(REGION_LABELS).fillna("Other")

    by_reg = (
        uniq.groupby(["participant", "region", "region_label"])
        .size()
        .reset_index(name="n_links_excluded")
    )
    by_reg.to_csv(tables_dir / "11_exclusion_by_region.csv", index=False)

    pivot = (
        by_reg.pivot(index="region", columns="participant", values="n_links_excluded")
        .reindex(REGION_ORDER)
        .fillna(0)
        .astype(int)
    )
    pivot.to_csv(tables_dir / "11_exclusion_region_pivot.csv")

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(REGION_ORDER))
    w = 0.18
    colors = ["#1a73e8", "#ea4335", "#0d904f", "#f9ab00"]
    for i, pid in enumerate(PIDS):
        vals = pivot[pid].reindex(REGION_ORDER).values if pid in pivot.columns else np.zeros(len(REGION_ORDER))
        ax.bar(x + (i - 1.5) * w, vals, w, label=pid, color=colors[i % len(colors)], alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels([REGION_LABELS.get(r, r) for r in REGION_ORDER], rotation=30, ha="right")
    ax.set_ylabel("# unique links excluded (pooled)")
    ax.set_title("Marker-gap / QC exclusions by body region")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = out_dir / "11_exclusion_map_by_region.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results-root",
        type=Path,
        default=ROOT / "results_committee_case" / "marker_gap_policy_ex09_13",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "docs" / "supervisor_addendum" / "tier3",
    )
    args = parser.parse_args()

    _configure_plt()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    tables = args.results_root / "tables_to_show"
    tables.mkdir(parents=True, exist_ok=True)

    h, sc = build_pooled_vs_single(args.results_root, args.out_dir, tables)
    p10 = build_per_exercise_nv(args.results_root, args.out_dir, tables)
    p11 = build_exclusion_region_map(args.results_root, args.out_dir, tables)

    readme = args.out_dir / "README.md"
    readme.write_text(
        "# Tier 3 — appendix / QC (optional deck material)\n\n"
        f"**Source:** `{args.results_root.name}`\n\n"
        "| # | Figure | Table | When to show |\n"
        "|---|--------|-------|-------------|\n"
        "| 9 | `09_pooled_vs_single_T3_scatter.png` | `09_pooled_vs_single_headline.csv` | Basis caveat: pooled vs A2 estimand |\n"
        "| 10 | `10_per_exercise_nv_layer2.png` | `10_per_exercise_nv_layer2.csv` | **Layer 2 only** — protocol openness |\n"
        "| 11 | `11_exclusion_map_by_region.png` | `11_exclusion_by_region.csv` | QC narrative — regional drops |\n\n"
        "Detail link table: `tables_to_show/09_pooled_vs_single_by_link.csv`\n",
        encoding="utf-8",
    )
    print(f"Tier 3 → {args.out_dir}")
    print(f"  tables: {h.name}, 10_*, 11_*")
    if sc:
        print(f"  {sc.name}")
    print(f"  {p10.name}")
    print(f"  {p11.name}")


if __name__ == "__main__":
    main()
