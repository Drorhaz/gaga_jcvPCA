"""Build supervisor addendum: 4 tables/figures for marker-gap run.

Usage:
  PYTHONPATH=src .venv/bin/python scripts/build_supervisor_addendum.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PIDS = ("671", "252", "651", "790")
RUN = "ex09_13_contiguous_pooled"
EVR_FUNCTIONAL_60 = 0.60
OLD_STEP04 = ROOT / "results_committee_case" / "step04_primary_runs"
OLD_STEP08 = ROOT / "results_committee_case" / "step08_nv_and_stability"


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


# ---------------------------------------------------------------------------
# 1. R1 vs R2 agreement
# ---------------------------------------------------------------------------


def build_r1_r2_agreement(flags_dir: Path, out_dir: Path) -> pd.DataFrame:
    frames = []
    for pid in PIDS:
        path = flags_dir / f"{pid}_rep_sensitivity_nv_flags.csv"
        if not path.exists():
            continue
        df = pd.read_csv(path)
        for followup in ("T2", "T3"):
            sub = df[df["followup"] == followup]
            if sub.empty:
                continue
            wide = sub.pivot_table(
                index="link_id",
                columns="rep_match",
                values="same_sign_exceed",
                aggfunc="first",
            )
            for col in ("R1", "R2"):
                if col not in wide.columns:
                    wide[col] = False
            wide = wide.fillna(False).astype(bool)
            qc = sub.groupby("link_id")["qc_exclusion"].first().fillna("")
            in_analysis = qc == ""
            w = wide[in_analysis.reindex(wide.index).fillna(False)]
            both = int((w["R1"] & w["R2"]).sum())
            r1_only = int((w["R1"] & ~w["R2"]).sum())
            r2_only = int((~w["R1"] & w["R2"]).sum())
            neither = int((~w["R1"] & ~w["R2"]).sum())
            n_links = len(w)
            frames.append(
                {
                    "participant": pid,
                    "followup": followup,
                    "n_links_in_analysis": n_links,
                    "exceed_both_R1_and_R2": both,
                    "exceed_R1_only": r1_only,
                    "exceed_R2_only": r2_only,
                    "exceed_neither": neither,
                    "rep_stable_fraction": round(both / n_links, 3) if n_links else np.nan,
                    "any_rep_fraction": round((both + r1_only + r2_only) / n_links, 3) if n_links else np.nan,
                }
            )
    out = pd.DataFrame(frames)
    out.to_csv(out_dir / "11_r1_r2_same_sign_exceed_agreement.csv", index=False)
    md = out_dir / "11_r1_r2_same_sign_exceed_agreement.md"
    lines = [
        "# R1 vs R2 agreement — same-sign NV exceed",
        "",
        "From `docs/rep_sensitivity_nv_panels/*_flags.csv`. "
        "Floor: `T1_R1 vs T1_R2`. Longitudinal: R1-matched vs R2-matched.",
        "",
        "See `11_r1_r2_same_sign_exceed_agreement.csv` for full table.",
        "",
    ]
    md.write_text("\n".join(lines), encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# 2. Functional / null same-sign exceed flags
# ---------------------------------------------------------------------------


def _evr_by_pc(jcv: pd.DataFrame, comparison_id: str) -> dict[int, float]:
    sub = jcv[jcv["comparison_id"] == comparison_id]
    if sub.empty:
        return {}
    return {int(pc): float(ev) for pc, ev in sub.groupby("pc")["explained_variance_A"].first().items()}


def _band_meta(bands: pd.DataFrame, jcv: pd.DataFrame, pid: str, comp: str, selected_m: int) -> tuple[int, int]:
    cid = f"{pid}_{comp}"
    row = bands[bands["comparison_id"] == cid]
    if not row.empty:
        return int(row.iloc[0]["p_functional_60"]), int(row.iloc[0]["selected_m"])
    evr = np.array([_evr_by_pc(jcv, cid).get(i, 0.0) for i in range(1, selected_m + 1)])
    cum = np.cumsum(evr)
    p60 = int(min(selected_m, np.searchsorted(cum, EVR_FUNCTIONAL_60) + 1))
    return p60, selected_m


def _band_signed(link_level, evr, cid, link, pc_lo, pc_hi) -> float | None:
    sub = link_level[
        (link_level["comparison_id"] == cid)
        & (link_level["link_id"] == link)
        & (link_level["pc"] >= pc_lo)
        & (link_level["pc"] <= pc_hi)
    ]
    if sub.empty:
        return None
    return float(sum(float(r.JcvPCA_link) * evr.get(int(r.pc), 0.0) for r in sub.itertuples()))


def _same_sign_exceed(long_v: float | None, nv_v: float | None) -> bool:
    if long_v is None or nv_v is None or long_v == 0 or nv_v == 0:
        return False
    return abs(long_v) > abs(nv_v) and np.sign(long_v) == np.sign(nv_v)


def build_band_exceed_table(results_root: Path, fig_dir: Path) -> pd.DataFrame:
    bands = pd.read_csv(results_root / "step04_primary_runs" / "functional_pc_bands.csv")
    rows: list[dict] = []

    for pid in PIDS:
        run_dir = results_root / "step04_primary_runs" / pid / RUN
        link_level = pd.read_csv(run_dir / "link_level_results.csv")
        jcv = pd.read_csv(run_dir / "jcvpca_results.csv")
        sel = pd.read_csv(run_dir / "selected_m_by_comparison.csv").set_index("comparison_id")

        cid_nv = f"{pid}_T1_R1_vs_R2"
        m_nv = int(sel.loc[cid_nv, "selected_m"])
        p60_nv, m_nv = _band_meta(bands[bands["participant"].astype(str) == pid], jcv, pid, "T1_R1_vs_R2", m_nv)
        evr_nv = _evr_by_pc(jcv, cid_nv)
        nv_fun = {
            lk: _band_signed(link_level, evr_nv, cid_nv, lk, 1, p60_nv)
            for lk in link_level[link_level["comparison_id"] == cid_nv]["link_id"].unique()
        }
        nv_null = {
            lk: _band_signed(link_level, evr_nv, cid_nv, lk, p60_nv + 1, m_nv)
            for lk in link_level[link_level["comparison_id"] == cid_nv]["link_id"].unique()
        }

        all_links: set[str] = set(nv_fun) | set(nv_null)
        for followup in ("T2", "T3"):
            comp = f"T1_vs_{followup}"
            cid = f"{pid}_{comp}"
            m = int(sel.loc[cid, "selected_m"])
            p60, m = _band_meta(bands[bands["participant"].astype(str) == pid], jcv, pid, comp, m)
            evr = _evr_by_pc(jcv, cid)
            all_links |= set(link_level[link_level["comparison_id"] == cid]["link_id"].unique())

        for link in sorted(all_links):
            flags: dict[str, bool] = {}
            for followup in ("T2", "T3"):
                comp = f"T1_vs_{followup}"
                cid = f"{pid}_{comp}"
                m = int(sel.loc[cid, "selected_m"])
                p60, m = _band_meta(bands[bands["participant"].astype(str) == pid], jcv, pid, comp, m)
                evr = _evr_by_pc(jcv, cid)
                lv_fun = _band_signed(link_level, evr, cid, link, 1, p60)
                lv_null = _band_signed(link_level, evr, cid, link, p60 + 1, m)
                flags[f"fun_{followup}"] = _same_sign_exceed(lv_fun, nv_fun.get(link))
                flags[f"null_{followup}"] = _same_sign_exceed(lv_null, nv_null.get(link))

            n_true = sum(flags.values())
            if n_true == 0:
                pattern = "none"
            elif flags["fun_T2"] and flags["fun_T3"] and not (flags["null_T2"] or flags["null_T3"]):
                pattern = "functional_only"
            elif (flags["null_T2"] or flags["null_T3"]) and not (flags["fun_T2"] or flags["fun_T3"]):
                pattern = "null_only"
            elif any(flags[k] for k in flags if k.startswith("fun_")) and any(
                flags[k] for k in flags if k.startswith("null_")
            ):
                pattern = "both_bands"
            else:
                pattern = "mixed"

            rows.append(
                {
                    "participant": pid,
                    "link_id": link,
                    "fun_T2": flags["fun_T2"],
                    "fun_T3": flags["fun_T3"],
                    "null_T2": flags["null_T2"],
                    "null_T3": flags["null_T3"],
                    "n_panels_exceed": n_true,
                    "pattern": pattern,
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(
        results_root / "tables_to_show" / "12_fun_null_same_sign_exceed_flags.csv",
        index=False,
    )

    # Heatmap: one row per participant (aggregate link counts per cell)
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    cols = ["fun_T2", "fun_T3", "null_T2", "null_T3"]
    col_labels = ["fun T2", "fun T3", "null T2", "null T3"]
    for ax, pid in zip(axes.ravel(), PIDS):
        sub = df[df["participant"] == pid].set_index("link_id")
        if sub.empty:
            continue
        mat = sub[cols].astype(int).values
        # sort: links with most flags first
        order = np.argsort(-mat.sum(axis=1))
        mat = mat[order]
        links = sub.index[order]
        im = ax.imshow(mat, aspect="auto", cmap="Blues", vmin=0, vmax=1)
        ax.set_xticks(range(4))
        ax.set_xticklabels(col_labels, rotation=45, ha="right", fontsize=8)
        ax.set_yticks(range(len(links)))
        ax.set_yticklabels(links, fontsize=5)
        ax.set_title(f"{pid} — same-sign exceed (n={int(mat.sum())} link×panel)")
    fig.suptitle("Functional 60% vs null 40% — same-sign NV exceed by link", y=1.02, fontweight="bold")
    fig.tight_layout()
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(fig_dir / "12_fun_null_same_sign_exceed_heatmap.png", bbox_inches="tight")
    plt.close(fig)

    summary = (
        df.groupby(["participant", "pattern"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    summary.to_csv(
        results_root / "tables_to_show" / "12_fun_null_same_sign_exceed_summary.csv",
        index=False,
    )
    return df


# ---------------------------------------------------------------------------
# 3. Coverage gate vs A2
# ---------------------------------------------------------------------------


def plot_coverage_a2_gate(results_root: Path, fig_dir: Path) -> pd.DataFrame:
    prof = pd.read_csv(results_root / "step08_nv_and_stability" / "NV_PROFILE.csv")
    rows = []
    for pid in PIDS:
        for tp in ("T2", "T3"):
            g = prof[
                (prof["participant"].astype(str) == pid)
                & (prof["comparison_id"] == f"{pid}_T1_vs_{tp}")
            ]
            if g.empty:
                continue
            n = len(g)
            a2 = int(g["a2_pass"].sum())
            s2_base = int((g["nv_profile_tier_base"] == "S2").sum())
            cov_lim = int((~g["coverage_ok"]).sum())
            s2_cov_blocked = int(
                ((g["nv_profile_tier_base"] == "S2") & (~g["coverage_ok"])).sum()
            )
            rows.append(
                {
                    "participant": pid,
                    "timepoint": tp,
                    "coverage_band": g["coverage_band"].iloc[0],
                    "coverage_rel": round(float(g["coverage_rel"].iloc[0]), 4),
                    "n_links": n,
                    "n_a2_pass": a2,
                    "n_s2_base": s2_base,
                    "n_coverage_limited_links": cov_lim,
                    "n_s2_blocked_by_coverage": s2_cov_blocked,
                }
            )
    df = pd.DataFrame(rows)
    df.to_csv(results_root / "tables_to_show" / "13_coverage_gate_vs_a2.csv", index=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(PIDS))
    w = 0.18
    for i, tp in enumerate(("T2", "T3")):
        sub = df[df["timepoint"] == tp].set_index("participant").reindex(PIDS)
        off = (i - 0.5) * (2 * w + 0.05)
        ax.bar(x + off, sub["n_a2_pass"], w, label=f"A2 pass {tp}", color="#0d904f", alpha=0.9)
        ax.bar(
            x + off + w,
            sub["n_s2_blocked_by_coverage"],
            w,
            label=f"S2 blocked (coverage) {tp}" if i == 0 else None,
            color="#f9ab00",
            alpha=0.85,
        )
        ax.bar(
            x + off + 2 * w,
            sub["n_coverage_limited_links"] - sub["n_s2_blocked_by_coverage"],
            w,
            bottom=sub["n_s2_blocked_by_coverage"],
            label=f"other coverage-limited {tp}" if i == 0 else None,
            color="#e0e0e0",
            alpha=0.9,
        )
    ax.set_xticks(x)
    ax.set_xticklabels(PIDS)
    ax.set_ylabel("Link count")
    ax.set_title("Coverage gate before A2 — pass vs blocked (single-rep estimand)")
    ax.legend(fontsize=8, ncol=2, loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(fig_dir / "13_coverage_gate_vs_a2.png", bbox_inches="tight")
    plt.close(fig)
    return df


# ---------------------------------------------------------------------------
# 4. Pre vs post marker-gap policy
# ---------------------------------------------------------------------------


def _tier_flips(old_prof: pd.DataFrame, new_prof: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for pid in PIDS:
        for tp in ("T2", "T3"):
            cid = f"{pid}_T1_vs_{tp}"
            o = old_prof[
                (old_prof["participant"].astype(str) == pid) & (old_prof["comparison_id"] == cid)
            ].set_index("link_id")
            n = new_prof[
                (new_prof["participant"].astype(str) == pid) & (new_prof["comparison_id"] == cid)
            ].set_index("link_id")
            for link in sorted(set(o.index) | set(n.index)):
                ot = o.loc[link, "nv_profile_tier"] if link in o.index else "—"
                nt = n.loc[link, "nv_profile_tier"] if link in n.index else "—"
                if ot != nt:
                    rows.append(
                        {
                            "participant": pid,
                            "comparison": f"T1_vs_{tp}",
                            "link_id": link,
                            "old_tier": ot,
                            "new_tier": nt,
                        }
                    )
    return pd.DataFrame(rows)


def plot_policy_delta(results_root: Path, fig_dir: Path) -> None:
    old_prof = pd.read_csv(OLD_STEP08 / "NV_PROFILE.csv")
    new_prof = pd.read_csv(results_root / "step08_nv_and_stability" / "NV_PROFILE.csv")
    flips = _tier_flips(old_prof, new_prof)
    flips.to_csv(results_root / "tables_to_show" / "14_policy_tier_flips.csv", index=False)

    def a2_table(prof):
        rows = []
        for pid in PIDS:
            for tp in ("T2", "T3"):
                g = prof[
                    (prof["participant"].astype(str) == pid)
                    & (prof["comparison_id"] == f"{pid}_T1_vs_{tp}")
                ]
                rows.append({"participant": pid, "tp": tp, "a2": int(g["a2_pass"].sum())})
        return pd.DataFrame(rows)

    old_a2 = a2_table(old_prof).rename(columns={"a2": "old_a2"})
    new_a2 = a2_table(new_prof).rename(columns={"a2": "new_a2"})
    a2 = old_a2.merge(new_a2, on=["participant", "tp"])
    a2["delta_a2"] = a2["new_a2"] - a2["old_a2"]

    excl_rows = []
    for pid in PIDS:
        path = results_root / "step04_primary_runs" / pid / RUN / "selected_m_by_comparison.csv"
        sm = pd.read_csv(path)
        excl_rows.append(
            {
                "participant": pid,
                "links_excluded_pooled": int(sm["n_excluded_links"].sum()),
                "links_included_pooled": int(sm["n_included_links"].sum()),
            }
        )
    excl = pd.DataFrame(excl_rows)
    a2 = a2.merge(excl, on="participant", how="left")
    a2.to_csv(results_root / "tables_to_show" / "14_policy_delta_summary.csv", index=False)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

    # A2 delta
    ax = axes[0]
    x = np.arange(len(PIDS))
    w = 0.35
    for i, tp in enumerate(("T2", "T3")):
        sub = a2[a2["tp"] == tp].set_index("participant").reindex(PIDS)
        colors = ["#0d904f" if d >= 0 else "#ea4335" for d in sub["delta_a2"]]
        ax.bar(x + (i - 0.5) * w, sub["delta_a2"], w, label=f"Δ A2 {tp}", color=colors, alpha=0.85)
    ax.axhline(0, color="#333", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(PIDS)
    ax.set_ylabel("Δ A2 (new − old)")
    ax.set_title("Signed NV A2 count change")
    ax.legend(fontsize=8)

    # Links excluded (pooled)
    ax = axes[1]
    ax.bar(PIDS, excl.set_index("participant").reindex(PIDS)["links_excluded_pooled"], color="#1a73e8")
    ax.set_ylabel("Pooled link-exclusion events")
    ax.set_title("Marker-gap exclusions (sum across comparisons)")

    # Tier flip counts
    ax = axes[2]
    if not flips.empty:
        flip_counts = flips.groupby(["participant", "comparison"]).size().unstack(fill_value=0)
        flip_counts = flip_counts.reindex(PIDS)
        flip_counts.plot(kind="bar", ax=ax, color=["#4285f4", "#ea4335"], alpha=0.85)
        ax.set_ylabel("# links tier changed")
        ax.set_title("NV tier flips (old → new)")
        ax.legend(title="", fontsize=8)
        ax.set_xticklabels(PIDS, rotation=0)
    else:
        ax.text(0.5, 0.5, "No tier flips", ha="center", transform=ax.transAxes)

    fig.suptitle("Pre vs post marker-gap policy — summary", fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(fig_dir / "14_pre_post_marker_gap_policy.png", bbox_inches="tight")
    plt.close(fig)

    top_flips = flips.head(20)
    md = results_root / "tables_to_show" / "14_policy_tier_flips_top20.md"
    md.write_text(
        "# Top tier flips (pre → post marker-gap policy)\n\n"
        + ("See `14_policy_tier_flips.csv` (" + str(len(flips)) + " rows).\n" if not flips.empty else "_No tier changes._\n"),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results-root",
        type=Path,
        default=ROOT / "results_committee_case" / "marker_gap_policy_ex09_13",
    )
    parser.add_argument(
        "--flags-dir",
        type=Path,
        default=ROOT / "docs" / "rep_sensitivity_nv_panels",
    )
    parser.add_argument(
        "--fig-dir",
        type=Path,
        default=ROOT / "docs" / "supervisor_addendum",
    )
    args = parser.parse_args()

    _configure_plt()
    tables = args.results_root / "tables_to_show"
    tables.mkdir(parents=True, exist_ok=True)
    args.fig_dir.mkdir(parents=True, exist_ok=True)

    build_r1_r2_agreement(args.flags_dir, tables)
    build_band_exceed_table(args.results_root, args.fig_dir)
    plot_coverage_a2_gate(args.results_root, args.fig_dir)
    plot_policy_delta(args.results_root, args.fig_dir)

    readme = args.fig_dir / "README.md"
    readme.write_text(
        "# Supervisor addendum figures\n\n"
        f"Companion tables in `{args.results_root.name}/tables_to_show/` (11–14).\n\n"
        "| Figure | Table |\n|---|---|\n"
        "| `12_fun_null_same_sign_exceed_heatmap.png` | `12_fun_null_same_sign_exceed_flags.csv` |\n"
        "| `13_coverage_gate_vs_a2.png` | `13_coverage_gate_vs_a2.csv` |\n"
        "| `14_pre_post_marker_gap_policy.png` | `14_policy_delta_summary.csv`, `14_policy_tier_flips.csv` |\n\n"
        "R1/R2 agreement: `11_r1_r2_same_sign_exceed_agreement.csv` (table only).\n",
        encoding="utf-8",
    )
    print(f"Tables → {tables}")
    print(f"Figures → {args.fig_dir}")


if __name__ == "__main__":
    main()
