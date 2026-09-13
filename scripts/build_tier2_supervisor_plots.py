"""Generate Tier 2 supervisor plots (sensitivity / methods story).

Usage:
  PYTHONPATH=src .venv/bin/python scripts/build_tier2_supervisor_plots.py
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
SINGLE_RUN = "ex09_13_contiguous_single"
EVR_P50 = 0.50
EVR_P60 = 0.60
TIER_COLORS = {"S0": "#9aa0a6", "S1": "#f9ab00", "S2": "#1a73e8", "S3": "#0d904f"}


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


def plot_p50_p60_vs_all(step04: Path, out: Path) -> Path:
    rob = pd.read_csv(step04 / "robustness.csv")
    rep = rob[rob["axis"] == "repetition_mode"].copy()
    rep["participant"] = rep["participant"].astype(str)
    rep["tp"] = rep["comparison_id"].str.extract(r"T1_vs_(T[23])")[0]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    metrics = [
        ("pooled_vs_r1_overlap", "all PCs", "#5f6368"),
        ("pooled_vs_r1_overlap_p50", "p50 band", "#1a73e8"),
        ("pooled_vs_r1_overlap_p60", "p60 band", "#4285f4"),
    ]
    for ax, tp in zip(axes, ("T2", "T3")):
        sub = rep[rep["tp"] == tp].set_index("participant").reindex(PIDS)
        x = np.arange(len(PIDS))
        w = 0.22
        for j, (col, label, color) in enumerate(metrics):
            vals = sub[col].astype(float).values
            ax.bar(x + (j - 1) * w, vals, w, label=label, color=color, alpha=0.9)
            for k, pid in enumerate(PIDS):
                v = vals[k]
                if np.isfinite(v):
                    ax.text(x[k] + (j - 1) * w, v + 0.02, f"{v:.1f}", ha="center", fontsize=7)
        ax.axhline(0.6, color="#333", ls="--", lw=1, alpha=0.7)
        ax.set_xticks(x)
        ax.set_xticklabels(PIDS)
        ax.set_ylim(0, 1.12)
        ax.set_title(f"T1→{tp} — pooled↔R1 top-5 overlap")
        ax.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("Top-5 overlap")
    axes[1].legend(fontsize=8, loc="lower right")
    fig.suptitle(
        "Step 4b — dominant band (p50/p60) vs full ranking (all PCs)\n"
        "252 T3: all=0.6 but p50=p60=0.8 → fringe instability, stable dominant mode",
        y=1.05,
        fontweight="bold",
        fontsize=11,
    )
    fig.tight_layout()
    path = out / "05_p50_p60_vs_all_pc_overlap.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)

    rep[
        [
            "participant",
            "comparison_id",
            "pooled_vs_r1_overlap",
            "pooled_vs_r1_overlap_p50",
            "pooled_vs_r1_overlap_p60",
            "robustness_label",
        ]
    ].to_csv(out / "05_p50_p60_vs_all_pc_overlap.csv", index=False)
    return path


def _evr_by_pc(jcv: pd.DataFrame, comparison_id: str) -> dict[int, float]:
    sub = jcv[jcv["comparison_id"] == comparison_id]
    if sub.empty:
        return {}
    return {int(pc): float(ev) for pc, ev in sub.groupby("pc")["explained_variance_A"].first().items()}


def _p_at(evr: dict[int, float], selected_m: int, threshold: float) -> int:
    cum = np.cumsum([evr.get(i, 0.0) for i in range(1, selected_m + 1)])
    return int(min(selected_m, np.searchsorted(cum, threshold) + 1))


def _band_signed(
    link_level: pd.DataFrame,
    evr: dict[int, float],
    comparison_id: str,
    pc_hi: int,
    *,
    pc_lo: int = 1,
) -> dict[str, float]:
    sub = link_level[
        (link_level["comparison_id"] == comparison_id)
        & (link_level["pc"] >= pc_lo)
        & (link_level["pc"] <= pc_hi)
    ]
    out: dict[str, float] = {}
    for link, grp in sub.groupby("link_id"):
        out[str(link)] = float(
            sum(float(r.JcvPCA_link) * evr.get(int(r.pc), 0.0) for r in grp.itertuples())
        )
    return out


def _same_sign_exceed(long_v: float | None, nv_v: float | None) -> bool:
    if long_v is None or nv_v is None or long_v == 0 or nv_v == 0:
        return False
    return abs(long_v) > abs(nv_v) and np.sign(long_v) == np.sign(nv_v)


def _signed_overlap_row(
    pid: str,
    tp: str,
    band: str,
    pc_hi: int,
    pooled_lt: pd.DataFrame,
    single_lt: pd.DataFrame,
    pooled_jcv: pd.DataFrame,
    single_jcv: pd.DataFrame,
    bands: pd.DataFrame,
) -> dict:
    comp = f"T1_vs_{tp}"
    cid_pool = f"{pid}_{comp}"
    cid_single = f"{pid}_{comp}"
    cid_nv = f"{pid}_T1_R1_vs_R2"

    m_pool = int(pooled_lt[pooled_lt["comparison_id"] == cid_pool]["pc"].max())
    m_nv = int(single_lt[single_lt["comparison_id"] == cid_nv]["pc"].max())

    evr_pool = _evr_by_pc(pooled_jcv, cid_pool)
    evr_single = _evr_by_pc(single_jcv, cid_single)
    evr_nv = _evr_by_pc(single_jcv, cid_nv)

    if band == "all":
        hi_pool = m_pool
        hi_single = int(single_lt[single_lt["comparison_id"] == cid_single]["pc"].max())
        hi_nv = m_nv
    elif band == "p50":
        row = bands[bands["comparison_id"] == cid_pool]
        hi_pool = int(row.iloc[0]["p_functional_50"]) if not row.empty else _p_at(evr_pool, m_pool, EVR_P50)
        hi_single = hi_pool
        hi_nv = _p_at(evr_nv, m_nv, EVR_P50)
    else:  # p60
        row = bands[bands["comparison_id"] == cid_pool]
        hi_pool = int(row.iloc[0]["p_functional_60"]) if not row.empty else _p_at(evr_pool, m_pool, EVR_P60)
        hi_single = hi_pool
        hi_nv = _p_at(evr_nv, m_nv, EVR_P60)

    long_pool = _band_signed(pooled_lt, evr_pool, cid_pool, hi_pool)
    long_r1 = _band_signed(single_lt, evr_single, cid_single, hi_single)
    nv = _band_signed(single_lt, evr_nv, cid_nv, hi_nv)

    links = sorted(set(long_pool) | set(long_r1) | set(nv))
    pool_ex = {lk for lk in links if _same_sign_exceed(long_pool.get(lk), nv.get(lk))}
    r1_ex = {lk for lk in links if _same_sign_exceed(long_r1.get(lk), nv.get(lk))}
    both = pool_ex & r1_ex
    recall = len(both) / len(pool_ex) if pool_ex else np.nan

    return {
        "participant": pid,
        "timepoint": tp,
        "band": band,
        "pc_hi": hi_pool,
        "n_pooled_same_sign_exceed": len(pool_ex),
        "n_r1_same_sign_exceed": len(r1_ex),
        "n_both": len(both),
        "signed_recall_pooled_to_r1": round(recall, 3) if np.isfinite(recall) else np.nan,
        "pooled_only": len(pool_ex - r1_ex),
        "r1_only": len(r1_ex - pool_ex),
    }


def plot_signed_pooled_vs_r1_overlap(step04: Path, out: Path) -> Path:
    bands = pd.read_csv(step04 / "functional_pc_bands.csv")
    rows: list[dict] = []
    for pid in PIDS:
        pool_dir = step04 / pid / POOL_RUN
        single_dir = step04 / pid / SINGLE_RUN
        pooled_lt = pd.read_csv(pool_dir / "link_level_results.csv")
        single_lt = pd.read_csv(single_dir / "link_level_results.csv")
        pooled_jcv = pd.read_csv(pool_dir / "jcvpca_results.csv")
        single_jcv = pd.read_csv(single_dir / "jcvpca_results.csv")
        for tp in ("T2", "T3"):
            for band in ("all", "p50", "p60"):
                rows.append(
                    _signed_overlap_row(
                        pid, tp, band, 0, pooled_lt, single_lt, pooled_jcv, single_jcv, bands
                    )
                )
    df = pd.DataFrame(rows)
    df.to_csv(out / "05_signed_pooled_vs_r1_same_sign_exceed.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    band_cfg = [
        ("all", "all PCs (EVR sum)", "#5f6368"),
        ("p50", "p50 band", "#1a73e8"),
        ("p60", "p60 band", "#4285f4"),
    ]
    for ax, tp in zip(axes, ("T2", "T3")):
        x = np.arange(len(PIDS))
        w = 0.22
        for j, (band, label, color) in enumerate(band_cfg):
            vals = []
            for pid in PIDS:
                r = df[(df.participant == pid) & (df.timepoint == tp) & (df.band == band)]
                vals.append(float(r.iloc[0]["signed_recall_pooled_to_r1"]) if not r.empty else np.nan)
            vals = np.array(vals, dtype=float)
            ax.bar(x + (j - 1) * w, vals, w, label=label, color=color, alpha=0.9)
            for k, pid in enumerate(PIDS):
                v = vals[k]
                if np.isfinite(v):
                    sub = df[(df.participant == pid) & (df.timepoint == tp) & (df.band == band)].iloc[0]
                    ax.text(
                        x[k] + (j - 1) * w,
                        v + 0.02,
                        f"{v:.1f}\n({int(sub['n_both'])}/{int(sub['n_pooled_same_sign_exceed'])})",
                        ha="center",
                        fontsize=6,
                    )
        ax.axhline(0.6, color="#333", ls="--", lw=1, alpha=0.7)
        ax.set_xticks(x)
        ax.set_xticklabels(PIDS)
        ax.set_ylim(0, 1.12)
        ax.set_title(f"T1→{tp} — signed same-sign exceed agreement")
        ax.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("Recall: pooled exceed links also exceed on R1")
    axes[1].legend(fontsize=8, loc="lower right")
    fig.suptitle(
        "Signed evidence — pooled vs R1 single-rep (same-sign NV exceed)\n"
        "Bar = fraction of pooled same-sign exceed links that replicate on T1_R1 vs T{k}_R1 "
        "(labels: both / pooled)",
        y=1.08,
        fontweight="bold",
        fontsize=10,
    )
    fig.tight_layout()
    path = out / "05_signed_pooled_vs_r1_same_sign_exceed.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_signed_profiles(prof: pd.DataFrame, out: Path) -> list[Path]:
    subdir = out / "06_signed_profiles"
    subdir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for pid in PIDS:
        for tp in ("T2", "T3"):
            g = prof[prof["comparison_id"] == f"{pid}_T1_vs_{tp}"].copy()
            if g.empty:
                continue
            g = g.sort_values("long_signed_single", key=lambda s: s.abs(), ascending=True)
            fig, ax = plt.subplots(figsize=(8, max(4.5, 0.28 * len(g))))
            y = np.arange(len(g))
            colors = [TIER_COLORS.get(t, "#333") for t in g["nv_profile_tier"]]
            ax.barh(y, g["long_signed_single"], color=colors, alpha=0.9)
            ax.scatter(g["nv_signed_t1"], y, color="black", s=20, zorder=3, label="NV floor")
            ax.axvline(0, color="#333", lw=0.8)
            ax.set_yticks(y)
            ax.set_yticklabels(
                [f"{l} [{t}]" for l, t in zip(g["link_id"], g["nv_profile_tier"])],
                fontsize=8,
            )
            ax.set_xlabel("Signed EVR-weighted Δ (long) vs NV floor (dots)")
            ax.set_title(f"{pid} T1→{tp} — signed profile (S0–S3 colours)")
            ax.legend(fontsize=8, loc="lower right")
            fname = f"{pid}_T1_vs_{tp}_signed_profile.png"
            path = subdir / fname
            fig.tight_layout()
            fig.savefig(path, bbox_inches="tight")
            plt.close(fig)
            written.append(path)
    return written


def plot_persistence(step09: Path, out: Path) -> Path:
    df = pd.read_csv(step09 / "persistence_results.csv")
    df["participant"] = df["participant"].astype(str)
    cats = ["persistent", "emergent_T3", "transient_T2", "sign_flip", "none"]
    colors = {
        "persistent": "#0d904f",
        "emergent_T3": "#1a73e8",
        "transient_T2": "#f9ab00",
        "sign_flip": "#d93025",
        "none": "#9aa0a6",
    }
    fig, ax = plt.subplots(figsize=(9, 4.5))
    bottom = np.zeros(len(PIDS))
    for cat in cats:
        vals = [int((df[df.participant == pid]["persistence"] == cat).sum()) for pid in PIDS]
        ax.bar(PIDS, vals, bottom=bottom, label=cat, color=colors[cat])
        bottom += np.array(vals, dtype=float)
    ax.set_ylabel("# links")
    ax.set_title("Step 9 — T2 vs T3 persistence of signed A2 links")
    ax.legend(fontsize=8, ncol=3, loc="upper right")
    fig.tight_layout()
    path = out / "07_persistence_t2_t3_stacks.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    df.to_csv(out / "07_persistence_t2_t3.csv", index=False)
    return path


def plot_step5_org_amp(step05: Path, out: Path) -> Path:
    df = pd.read_csv(step05 / "rom_rms_by_link.csv")
    df["participant"] = df["participant"].astype(str)
    if "exceeds_nv" in df.columns:
        df = df[df["exceeds_nv"] == True]  # noqa: E712
    rows = []
    for pid in PIDS:
        for tp in ("T2", "T3"):
            g = df[(df.participant == pid) & (df["followup_timepoint"] == tp)]
            if g.empty:
                continue
            vc = g["classification"].value_counts()
            rows.append(
                {
                    "participant": pid,
                    "timepoint": tp,
                    "organization": int(vc.get("organization", 0)),
                    "amplitude": int(vc.get("amplitude", 0)),
                    "mixed": int(vc.get("mixed", 0)),
                }
            )
    d = pd.DataFrame(rows)
    d.to_csv(out / "08_amplitude_vs_organization_counts.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, tp in zip(axes, ("T2", "T3")):
        sub = d[d.timepoint == tp].set_index("participant").reindex(PIDS).fillna(0)
        x = np.arange(len(PIDS))
        ax.bar(x, sub["organization"], label="organization", color="#0d904f")
        ax.bar(x, sub["amplitude"], bottom=sub["organization"], label="amplitude", color="#ea4335")
        ax.bar(
            x,
            sub["mixed"],
            bottom=sub["organization"] + sub["amplitude"],
            label="mixed",
            color="#f9ab00",
        )
        ax.set_xticks(x)
        ax.set_xticklabels(PIDS)
        ax.set_title(f"Step 5 — T1→{tp} (NV-exceed links)")
    axes[0].set_ylabel("# links by classification")
    axes[1].legend(fontsize=8, loc="upper right")
    fig.suptitle("Amplitude vs organization (Step 5)", y=1.02, fontweight="bold")
    fig.tight_layout()
    path = out / "08_step5_org_vs_amp.png"
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
        default=ROOT / "docs" / "supervisor_addendum" / "tier2",
    )
    args = parser.parse_args()

    _configure_plt()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rr = args.results_root

    prof = pd.read_csv(rr / "step08_nv_and_stability" / "NV_PROFILE.csv")
    prof["participant"] = prof["participant"].astype(str)

    step04 = rr / "step04_primary_runs"
    p5 = plot_p50_p60_vs_all(step04, args.out_dir)
    p5s = plot_signed_pooled_vs_r1_overlap(step04, args.out_dir)
    profiles = plot_signed_profiles(prof, args.out_dir)
    p7 = plot_persistence(rr / "step09_persistence_t2_t3", args.out_dir)
    p8 = plot_step5_org_amp(rr / "step05_amplitude_vs_organization", args.out_dir)

    readme = args.out_dir / "README.md"
    readme.write_text(
        "# Tier 2 — sensitivity / methods figures\n\n"
        f"**Source:** `{rr.name}`\n\n"
        "| # | File | Use when… |\n"
        "|---|------|----------|\n"
        "| 5a | `05_p50_p60_vs_all_pc_overlap.png` | Abs top-5 ranking overlap (legacy / appendix) |\n"
        "| 5b | `05_signed_pooled_vs_r1_same_sign_exceed.png` | **Signed** same-sign exceed — pooled vs R1 |\n"
        "| 6 | `06_signed_profiles/{pid}_T1_vs_{T2,T3}_signed_profile.png` | Case walk-through with S0–S3 colours |\n"
        "| 7 | `07_persistence_t2_t3_stacks.png` | Acute vs sustained A2 (T2→T3) |\n"
        "| 8 | `08_step5_org_vs_amp.png` | Mechanism — organization vs amplitude |\n\n"
        "Companion CSVs alongside each figure.\n",
        encoding="utf-8",
    )
    print(f"Tier 2 → {args.out_dir}")
    print(f"  {p5.name}")
    print(f"  {p5s.name}")
    print(f"  {len(profiles)} signed profiles")
    print(f"  {p7.name}")
    print(f"  {p8.name}")


if __name__ == "__main__":
    main()
