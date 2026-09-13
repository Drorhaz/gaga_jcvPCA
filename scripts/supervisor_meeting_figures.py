"""Generate supervisor-meeting figures, organized by deck slide blocks.

Usage:
  PYTHONPATH=src .venv/bin/python scripts/supervisor_meeting_figures.py

Output root:
  docs/supervisor_meeting_figures_2026-07-18/
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = ROOT / "results_committee_case"
OUT = ROOT / "docs" / "supervisor_meeting_figures_2026-07-18"
STEP04 = DEFAULT_RESULTS / "step04_primary_runs"
STEP05 = DEFAULT_RESULTS / "step05_amplitude_vs_organization"
STEP06 = DEFAULT_RESULTS / "step06_underused_at_t1"
STEP07 = DEFAULT_RESULTS / "step07_contribution_distribution"
STEP08 = DEFAULT_RESULTS / "step08_nv_and_stability"
STEP09 = DEFAULT_RESULTS / "step09_persistence_t2_t3"
PIDS = ("671", "252", "651", "790")
WINDOW = "ex09_13_contiguous"


def _configure_paths(results_root: Path, out_dir: Path | None = None) -> None:
    global OUT, STEP04, STEP05, STEP06, STEP07, STEP08, STEP09
    OUT = out_dir or (ROOT / "docs" / f"supervisor_meeting_figures_{results_root.name}")
    STEP04 = results_root / "step04_primary_runs"
    STEP05 = results_root / "step05_amplitude_vs_organization"
    STEP06 = results_root / "step06_underused_at_t1"
    STEP07 = results_root / "step07_contribution_distribution"
    STEP08 = results_root / "step08_nv_and_stability"
    STEP09 = results_root / "step09_persistence_t2_t3"

TIER_COLORS = {"S0": "#9aa0a6", "S1": "#f9ab00", "S2": "#1a73e8", "S3": "#0d904f"}
plt.rcParams.update(
    {
        "figure.dpi": 140,
        "savefig.dpi": 160,
        "font.size": 11,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    }
)


def _save(fig: plt.Figure, folder: str, name: str) -> Path:
    d = OUT / folder
    d.mkdir(parents=True, exist_ok=True)
    path = d / name
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {path.relative_to(ROOT)}")
    return path


def _band(link: str) -> str:
    if any(x in link for x in ["_to_Ab", "Ab_to_", "Spine"]):
        return "trunk_core"
    if any(x in link for x in ["Chest_to_Neck", "Neck_to_", "Neck2"]):
        return "neck"
    if any(x in link for x in ["Shoulder", "UArm", "FArm", "Hand"]):
        return "arm"
    if any(x in link for x in ["Thigh", "Shin", "Foot"]):
        return "leg"
    return "other"


def plot_headline_a2(prof: pd.DataFrame) -> None:
    rows = []
    for pid in PIDS:
        for tp in ("T2", "T3"):
            g = prof[prof["comparison_id"] == f"{pid}_T1_vs_{tp}"]
            if g.empty:
                continue
            rows.append(
                {
                    "participant": pid,
                    "timepoint": tp,
                    "a2": int(g["a2_pass"].sum()),
                    "n": len(g),
                    "frac": g["a2_pass"].mean(),
                }
            )
    df = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(PIDS))
    w = 0.35
    t2 = df[df.timepoint == "T2"].set_index("participant").reindex(PIDS)
    t3 = df[df.timepoint == "T3"].set_index("participant").reindex(PIDS)
    ax.bar(x - w / 2, t2["frac"], w, label="T1→T2", color="#1a73e8")
    ax.bar(x + w / 2, t3["frac"], w, label="T1→T3", color="#ea4335")
    for i, pid in enumerate(PIDS):
        ax.text(
            i - w / 2,
            t2.loc[pid, "frac"] + 0.02,
            f"{int(t2.loc[pid, 'a2'])}/{int(t2.loc[pid, 'n'])}",
            ha="center",
            fontsize=8,
        )
        ax.text(
            i + w / 2,
            t3.loc[pid, "frac"] + 0.02,
            f"{int(t3.loc[pid, 'a2'])}/{int(t3.loc[pid, 'n'])}",
            ha="center",
            fontsize=8,
        )
    ax.set_xticks(x)
    ax.set_xticklabels(PIDS)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Fraction of links with A2 pass (S2/S3)")
    ax.set_title("Headline — signed A2 pass rate by participant")
    ax.legend()
    ax.axhline(0.5, color="#ddd", lw=1, zorder=0)
    _save(fig, "19_headline_signed_a2", "a2_pass_rate.png")


def plot_tier_counts(prof: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharey=True)
    for ax, tp in zip(axes, ("T2", "T3")):
        data = []
        for pid in PIDS:
            g = prof[prof["comparison_id"] == f"{pid}_T1_vs_{tp}"]
            counts = g["nv_profile_tier"].value_counts()
            data.append([counts.get(t, 0) for t in ("S0", "S1", "S2", "S3")])
        data = np.array(data, dtype=float)
        bottom = np.zeros(len(PIDS))
        for j, tier in enumerate(("S0", "S1", "S2", "S3")):
            ax.bar(PIDS, data[:, j], bottom=bottom, label=tier, color=TIER_COLORS[tier])
            bottom += data[:, j]
        ax.set_title(f"T1→{tp} signed tiers")
        ax.set_ylabel("# links")
    axes[1].legend(loc="upper right", fontsize=8)
    fig.suptitle("Signed NV profile tiers (S0–S3)", y=1.02)
    _save(fig, "17_18_signed_nv_tiers", "tier_stacked_counts.png")


def plot_coverage(prof: pd.DataFrame) -> None:
    rows = []
    for pid in PIDS:
        for tp in ("T2", "T3"):
            g = prof[prof["comparison_id"] == f"{pid}_T1_vs_{tp}"]
            if g.empty:
                continue
            rows.append(
                {
                    "participant": pid,
                    "timepoint": tp,
                    "coverage_rel": float(g["coverage_rel"].iloc[0]),
                    "band": g["coverage_band"].iloc[0],
                }
            )
    df = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(PIDS))
    w = 0.35
    t2 = df[df.timepoint == "T2"].set_index("participant").reindex(PIDS)
    t3 = df[df.timepoint == "T3"].set_index("participant").reindex(PIDS)
    colors_t2 = [
        "#0d904f" if b == "adequate" else "#f9ab00" if b == "limited" else "#d93025"
        for b in t2["band"]
    ]
    colors_t3 = [
        "#0d904f" if b == "adequate" else "#f9ab00" if b == "limited" else "#d93025"
        for b in t3["band"]
    ]
    ax.bar(x - w / 2, t2["coverage_rel"], w, color=colors_t2, label="T2")
    ax.bar(x + w / 2, t3["coverage_rel"], w, color=colors_t3, label="T3")
    ax.axhline(0.75, color="#0d904f", ls="--", lw=1, label="adequate ≥0.75")
    ax.axhline(0.50, color="#f9ab00", ls="--", lw=1, label="limited ≥0.50")
    ax.set_xticks(x)
    ax.set_xticklabels(PIDS)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("coverage_rel")
    ax.set_title("Reference-subspace coverage (longitudinal pairs)")
    ax.legend(fontsize=8)
    _save(fig, "13_16_sensitivity_nv", "coverage_rel.png")


def plot_matched_vs_pooled() -> None:
    ev = pd.read_csv(STEP08 / "NV_EVIDENCE.csv")
    ev["participant"] = ev["participant"].astype(str)
    rows = []
    for pid in PIDS:
        for tp in ("T2", "T3"):
            g = ev[ev["comparison_id"] == f"{pid}_T1_vs_{tp}"]
            if g.empty:
                continue
            rows.append(
                {
                    "participant": pid,
                    "timepoint": tp,
                    "matched": g["exceeds_observed_variability"].mean(),
                    "a2": g["a2_pass"].mean() if "a2_pass" in g.columns else np.nan,
                }
            )
    df = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(PIDS))
    w = 0.35
    for i, tp in enumerate(("T2", "T3")):
        sub = df[df.timepoint == tp].set_index("participant").reindex(PIDS)
        ax.bar(
            x + (i - 0.5) * w,
            sub["matched"],
            w,
            label=f"abs matched {tp}",
            alpha=0.85 if tp == "T2" else 0.55,
        )
    ax.set_xticks(x)
    ax.set_xticklabels(PIDS)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Fraction links exceeding (abs matched)")
    ax.set_title("NV sensitivity — abs matched exceed rate")
    ax.legend(fontsize=8)
    _save(fig, "13_16_sensitivity_nv", "abs_matched_exceed_rate.png")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for tp in ("T2", "T3"):
        sub = df[df.timepoint == tp].set_index("participant").reindex(PIDS)
        ax.plot(PIDS, sub["matched"], "o--", label=f"abs matched {tp}")
        ax.plot(PIDS, sub["a2"], "s-", label=f"signed A2 {tp}")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Fraction of links")
    ax.set_title("NV sensitivity — abs matched vs signed A2")
    ax.legend(fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3)
    _save(fig, "13_16_sensitivity_nv", "abs_vs_signed_a2.png")


def plot_robustness() -> None:
    rob = pd.read_csv(STEP04 / "robustness.csv")
    rob["participant"] = rob["participant"].astype(str)
    g = (
        rob.groupby(["participant", "comparison_id"])
        .agg(min_top5=("top5_overlap", "min"), label=("robustness_label", "first"))
        .reset_index()
    )
    g["tp"] = g["comparison_id"].str.extract(r"T1_vs_(T[23])")[0]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(PIDS))
    w = 0.35
    for i, tp in enumerate(("T2", "T3")):
        sub = g[g.tp == tp].set_index("participant").reindex(PIDS)
        colors = ["#0d904f" if lab == "stable" else "#f9ab00" for lab in sub["label"]]
        ax.bar(
            x + (i - 0.5) * w,
            sub["min_top5"],
            w,
            color=colors,
            edgecolor="black",
            linewidth=0.4,
        )
        for j, pid in enumerate(PIDS):
            ax.text(
                j + (i - 0.5) * w,
                float(sub.loc[pid, "min_top5"]) + 0.02,
                str(sub.loc[pid, "label"])[0].upper(),
                ha="center",
                fontsize=8,
            )
    ax.axhline(0.6, color="#333", ls="--", lw=1, label="0.6 heuristic")
    ax.set_xticks(x)
    ax.set_xticklabels(PIDS)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("min top-5 overlap (across axes)")
    ax.set_title("Sensitivity — ranking robustness (Step 4b)")
    ax.legend(fontsize=8)
    _save(fig, "13_16_sensitivity_robustness", "min_top5_overlap.png")

    if "pooled_vs_r1_overlap" in rob.columns and "pooled_vs_r1_overlap_p50" in rob.columns:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        rows = []
        for (pid, cid), gg in rob.groupby(["participant", "comparison_id"]):
            if "T1_vs" not in cid:
                continue
            filled = gg[gg["pooled_vs_r1_overlap_p50"].notna()]
            r = filled.iloc[0] if not filled.empty else gg.iloc[0]
            rows.append(
                {
                    "participant": str(pid),
                    "tp": "T3" if "T3" in cid else "T2",
                    "all": float(r["pooled_vs_r1_overlap"])
                    if pd.notna(r["pooled_vs_r1_overlap"])
                    else np.nan,
                    "p50": float(r["pooled_vs_r1_overlap_p50"])
                    if pd.notna(r["pooled_vs_r1_overlap_p50"])
                    else np.nan,
                }
            )
        df = pd.DataFrame(rows)
        if not df.empty and df["p50"].notna().any():
            for tp, marker in (("T2", "o"), ("T3", "s")):
                sub = df[df.tp == tp]
                ax.scatter(sub["all"], sub["p50"], s=80, marker=marker, label=tp)
                for _, r in sub.iterrows():
                    ax.annotate(
                        r["participant"],
                        (r["all"], r["p50"]),
                        textcoords="offset points",
                        xytext=(4, 4),
                        fontsize=8,
                    )
            ax.plot([0, 1], [0, 1], "--", color="#aaa")
            ax.axvline(0.6, color="#ddd", lw=1)
            ax.axhline(0.6, color="#ddd", lw=1)
            ax.set_xlim(0, 1.05)
            ax.set_ylim(0, 1.05)
            ax.set_xlabel("pooled↔R1 overlap (all PCs)")
            ax.set_ylabel("pooled↔R1 overlap (p50 band)")
            ax.set_title("Functional band vs full ranking (rep sensitivity)")
            ax.legend()
            _save(fig, "13_16_sensitivity_robustness", "p50_vs_all_rep_overlap.png")
        else:
            plt.close(fig)


def plot_participant_link_profile(prof: pd.DataFrame, pid: str) -> None:
    folder = f"20_27_case_{pid}"
    for tp in ("T2", "T3"):
        g = prof[prof["comparison_id"] == f"{pid}_T1_vs_{tp}"].copy()
        if g.empty:
            continue
        g = g.sort_values("long_signed_single", key=lambda s: s.abs(), ascending=True)
        fig, ax = plt.subplots(figsize=(8, max(4.5, 0.28 * len(g))))
        y = np.arange(len(g))
        colors = [TIER_COLORS.get(t, "#333") for t in g["nv_profile_tier"]]
        ax.barh(y, g["long_signed_single"], color=colors, alpha=0.9, label="long_signed")
        ax.scatter(
            g["nv_signed_t1"], y, color="black", s=18, zorder=3, label="nv_signed (floor)"
        )
        ax.axvline(0, color="#333", lw=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels(
            [f"{l} [{t}]" for l, t in zip(g["link_id"], g["nv_profile_tier"])], fontsize=8
        )
        ax.set_xlabel("Signed EVR-weighted Δ (long) vs NV floor (dots)")
        ax.set_title(f"{pid} T1→{tp} — within-link signed profile")
        ax.legend(fontsize=8, loc="lower right")
        _save(fig, folder, f"{pid}_T1_vs_{tp}_signed_profile.png")


def plot_functional_vs_null() -> None:
    rows = []
    for pid in PIDS:
        fun = pd.read_csv(STEP04 / pid / f"{WINDOW}_pooled" / "functional_space_results.csv")
        nul = pd.read_csv(STEP04 / pid / f"{WINDOW}_pooled" / "null_space_results.csv")
        for space, df in (("functional", fun), ("null", nul)):
            for _, r in df.iterrows():
                if "T1_vs" not in str(r["comparison_id"]):
                    continue
                rows.append(
                    {
                        "participant": pid,
                        "comparison_id": r["comparison_id"],
                        "space": space,
                        "band": _band(r["link_id"]),
                        "abs_mean": float(r["JcvPCA_abs_mean"]),
                    }
                )
    df = pd.DataFrame(rows)
    t3 = df[df.comparison_id.str.contains("T1_vs_T3")]
    bands = ["arm", "leg", "neck", "trunk_core"]
    fig, axes = plt.subplots(1, 4, figsize=(12, 4), sharey=True)
    for ax, pid in zip(axes, PIDS):
        sub = t3[t3.participant == pid]
        fun_m = [
            sub[(sub.band == b) & (sub.space == "functional")]["abs_mean"].mean() for b in bands
        ]
        nul_m = [sub[(sub.band == b) & (sub.space == "null")]["abs_mean"].mean() for b in bands]
        x = np.arange(len(bands))
        ax.bar(x - 0.2, fun_m, 0.4, label="functional", color="#1a73e8")
        ax.bar(x + 0.2, nul_m, 0.4, label="null", color="#ea4335")
        ax.set_xticks(x)
        ax.set_xticklabels(bands, rotation=45, ha="right", fontsize=8)
        ax.set_title(pid)
    axes[0].set_ylabel("mean |ΔJcvPCA|")
    axes[-1].legend(fontsize=8)
    fig.suptitle("Functional vs null space by body band (T1→T3)", y=1.02)
    _save(fig, "28_29_functional_vs_null", "fun_vs_null_by_band_T3.png")

    fig, ax = plt.subplots(figsize=(6, 4))
    sub = t3[t3.participant == "252"]
    for band in bands:
        f = sub[(sub.band == band) & (sub.space == "functional")]["abs_mean"].mean()
        n = sub[(sub.band == band) & (sub.space == "null")]["abs_mean"].mean()
        ax.plot(["functional", "null"], [f, n], "o-", label=band)
    ax.set_title("252 T1→T3 — |Δ| by space (arms functional, neck null)")
    ax.set_ylabel("mean |ΔJcvPCA|")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    _save(fig, "28_29_functional_vs_null", "252_T3_fun_vs_null_lines.png")


def plot_underused() -> None:
    path = STEP06 / "underused_link_results.csv"
    if not path.exists():
        return
    df = pd.read_csv(path)
    df["participant"] = df["participant"].astype(str)
    u = df[df["underused_at_t1"]]
    rows = []
    for pid in PIDS:
        for tp in ("T2", "T3"):
            g = u[u["comparison_id"] == f"{pid}_T1_vs_{tp}"]
            rows.append(
                {
                    "participant": pid,
                    "timepoint": tp,
                    "n": len(g),
                    "a2": int(g["beyond_nv_a2"].sum()) if len(g) else 0,
                }
            )
    d = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(PIDS))
    w = 0.35
    for i, tp in enumerate(("T2", "T3")):
        sub = d[d.timepoint == tp].set_index("participant").reindex(PIDS)
        ax.bar(
            x + (i - 0.5) * w,
            sub["a2"] / sub["n"].replace(0, np.nan),
            w,
            label=f"{tp} beyond-NV / underused",
        )
    ax.set_xticks(x)
    ax.set_xticklabels(PIDS)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Fraction of T1-underused links beyond NV (A2)")
    ax.set_title("Step 6 — underused-at-T1 links clearing A2")
    ax.legend(fontsize=8)
    _save(fig, "20_27_cross_cutting", "underused_a2_fraction.png")


def plot_distribution() -> None:
    path = STEP07 / "distribution_metrics.csv"
    if not path.exists():
        return
    df = pd.read_csv(path)
    df = df[df["comparison_id"].str.contains("T1_vs_")]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, col, title in (
        (axes[0], "top1_share_delta", "Δ top-1 share (follow-up − T1)"),
        (axes[1], "entropy_delta", "Δ normalized entropy (follow-up − T1)"),
    ):
        for pid in PIDS:
            sub = df[df["participant"].astype(str) == pid]
            tps = ["T2" if "T2" in c else "T3" for c in sub["comparison_id"]]
            ax.plot(tps, sub[col], "o-", label=pid)
        ax.axhline(0, color="#333", lw=0.8)
        ax.set_title(title)
        ax.set_ylim(-0.05, 0.05)
    axes[1].legend(fontsize=8)
    fig.suptitle("Step 7 — contribution distribution barely moves", y=1.02)
    _save(fig, "20_27_cross_cutting", "distribution_deltas.png")


def plot_persistence() -> None:
    path = STEP09 / "persistence_results.csv"
    if not path.exists():
        return
    df = pd.read_csv(path)
    df["participant"] = df["participant"].astype(str)
    cats = ["persistent", "emergent_T3", "transient_T2", "sign_flip", "none"]
    colors = {
        "persistent": "#0d904f",
        "emergent_T3": "#1a73e8",
        "transient_T2": "#f9ab00",
        "sign_flip": "#d93025",
        "none": "#9aa0a6",
    }
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bottom = np.zeros(len(PIDS))
    for cat in cats:
        vals = [int((df[df.participant == pid]["persistence"] == cat).sum()) for pid in PIDS]
        ax.bar(PIDS, vals, bottom=bottom, label=cat, color=colors[cat])
        bottom += np.array(vals, dtype=float)
    ax.set_ylabel("# links")
    ax.set_title("Step 9 — T2 vs T3 persistence of signed A2")
    ax.legend(fontsize=8, ncol=3)
    _save(fig, "20_27_cross_cutting", "persistence_stacks.png")


def plot_step5_org() -> None:
    path = STEP05 / "rom_rms_by_link.csv"
    if not path.exists():
        return
    df = pd.read_csv(path)
    df["participant"] = df["participant"].astype(str)
    if "exceeds_nv" in df.columns:
        df = df[df["exceeds_nv"] == True]  # noqa: E712
    if "classification" not in df.columns or df.empty:
        return
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
    if d.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sub = d[d.timepoint == "T3"].set_index("participant").reindex(PIDS).fillna(0)
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
    ax.set_ylabel("# NV-exceed links (Step 5 classif.)")
    ax.set_title("Step 5 — amplitude vs organization (T1→T3)")
    ax.legend(fontsize=8)
    _save(fig, "20_27_cross_cutting", "step5_org_vs_amp_T3.png")


def plot_pipeline_schematic() -> None:
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.axis("off")
    boxes = [
        (0.05, "Motive\nbone quats"),
        (0.28, "q_rel =\ninv(parent)×child"),
        (0.52, "sign continuity\n→ rotvec"),
        (0.75, "jcvPCA\nT1=A → Δ links"),
    ]
    for x, text in boxes:
        ax.add_patch(
            plt.Rectangle(
                (x, 0.35), 0.18, 0.4, fill=True, facecolor="#e8f0fe", edgecolor="#1a73e8", lw=2
            )
        )
        ax.text(x + 0.09, 0.55, text, ha="center", va="center", fontsize=10)
    for x in (0.23, 0.46, 0.70):
        ax.annotate(
            "",
            xy=(x + 0.05, 0.55),
            xytext=(x, 0.55),
            arrowprops=dict(arrowstyle="->", color="#333", lw=1.5),
        )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Feature pipeline — quaternion parent→child → rotvec → jcvPCA")
    _save(fig, "04_06_feature_pipeline", "pipeline_schematic.png")


def write_readme() -> None:
    paths = [(p.parent.name, p.name) for p in sorted(OUT.rglob("*.png"))]
    lines = [
        "# Supervisor meeting figures — 2026-07-18",
        "",
        "Generated by `scripts/supervisor_meeting_figures.py` from existing committee CSVs.",
        "Folders align with blocks in [`SUPERVISOR_MEETING_DECK_2026-07-18.md`](../SUPERVISOR_MEETING_DECK_2026-07-18.md).",
        "",
        "| Deck block / slides | Folder | Key figures |",
        "|---|---|---|",
        "| Feature pipeline (4–6) | `04_06_feature_pipeline/` | pipeline schematic |",
        "| Sensitivity NV (13–16) | `13_16_sensitivity_nv/` | coverage, abs vs signed A2 |",
        "| Sensitivity robustness (13–16) | `13_16_sensitivity_robustness/` | min top-5, p50 vs all |",
        "| Signed NV tiers (17–18) | `17_18_signed_nv_tiers/` | S0–S3 stacks |",
        "| Headline (19) | `19_headline_signed_a2/` | A2 pass rates |",
        "| Cases 671–790 (20–27) | `20_27_case_{pid}/` | per-link signed profiles |",
        "| Cross-cutting (Steps 5–7,9) | `20_27_cross_cutting/` | underused, distribution, persistence, org |",
        "| Functional vs null (28–29) | `28_29_functional_vs_null/` | band × space |",
        "",
        "## Index",
        "",
    ]
    for folder, name in paths:
        lines.append(f"- `{folder}/{name}`")
    lines.append("")
    (OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-root",
        type=Path,
        default=DEFAULT_RESULTS,
        help="Parent folder with step04..step09 subdirectories",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Figure output directory (default: docs/supervisor_meeting_figures_<results-root-name>)",
    )
    args = parser.parse_args()
    results_root = args.results_root.resolve()
    _configure_paths(results_root, args.out_dir.resolve() if args.out_dir else None)

    OUT.mkdir(parents=True, exist_ok=True)
    print(f"Output → {OUT.relative_to(ROOT)}")
    prof = pd.read_csv(STEP08 / "NV_PROFILE.csv")
    prof["participant"] = prof["participant"].astype(str)

    plot_pipeline_schematic()
    plot_headline_a2(prof)
    plot_tier_counts(prof)
    plot_coverage(prof)
    plot_matched_vs_pooled()
    plot_robustness()
    for pid in PIDS:
        plot_participant_link_profile(prof, pid)
    plot_functional_vs_null()
    plot_underused()
    plot_distribution()
    plot_persistence()
    plot_step5_org()
    write_readme()
    n = len(list(OUT.rglob("*.png")))
    print(f"\nDone — {n} figures + README")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
