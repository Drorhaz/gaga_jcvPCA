"""Functional (60% EVR) / null (remainder) — pooled T2 & T3 vs NV, overlapped bars.

8 figures: 4 participants × (functional | null).
Each figure: 2 panels — T1 vs T3 | T1 vs T2, each with pooled vs NV on the same link row.

Usage:
  PYTHONPATH=src .venv/bin/python scripts/plot_fun_null_t3_nv_by_link.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PIDS = ("671", "252", "651", "790")
RUN = "ex09_13_contiguous_pooled"
EVR_FUNCTIONAL_60 = 0.60
COMP_T2 = "T1_vs_T2"
COMP_T3 = "T1_vs_T3"
COMP_NV = "T1_R1_vs_R2"

COLOR_LONG = "#1a73e8"
COLOR_NV = "#ea4335"
COLOR_EXCEED = "#0d904f"


def _configure_plt() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 160,
            "font.size": 10,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )


def _load_exclusions(results_root: Path) -> pd.DataFrame:
    path = results_root / "comparison_link_exclusions.csv"
    if not path.exists():
        return pd.DataFrame()
    ex = pd.read_csv(path)
    return ex[(ex["repetition_mode"] == "pooled") & (ex["link_id"].astype(str).str.len() > 0)]


def _excl_reason(excl: pd.DataFrame, pid: str, comp_suffix: str, link: str) -> str:
    cid = f"{pid}_{comp_suffix}"
    sub = excl[
        (excl["participant"].astype(str) == pid)
        & (excl["comparison_id"] == cid)
        & (excl["link_id"] == link)
    ]
    if sub.empty:
        return ""
    r = sub.iloc[0]
    reason = str(r.get("exclusion_reason", "")).replace("marker_gap_policy: ", "", 1)
    src = str(r.get("exclusion_source", ""))
    if src and src != "none":
        return f"{src}: {reason[:65]}"
    return reason[:75]


def _evr_by_pc(jcv: pd.DataFrame, comparison_id: str) -> dict[int, float]:
    sub = jcv[jcv["comparison_id"] == comparison_id]
    if sub.empty:
        return {}
    return {int(pc): float(ev) for pc, ev in sub.groupby("pc")["explained_variance_A"].first().items()}


def _band_meta(
    bands: pd.DataFrame,
    jcv: pd.DataFrame,
    pid: str,
    comp_suffix: str,
    selected_m: int,
) -> tuple[int, int]:
    cid = f"{pid}_{comp_suffix}"
    row = bands[bands["comparison_id"] == cid]
    if not row.empty:
        p60 = int(row.iloc[0]["p_functional_60"])
        m = int(row.iloc[0]["selected_m"])
        return p60, m
    evr = np.array([_evr_by_pc(jcv, cid).get(i, 0.0) for i in range(1, selected_m + 1)])
    cum = np.cumsum(evr)
    p60 = int(min(selected_m, np.searchsorted(cum, EVR_FUNCTIONAL_60) + 1))
    return p60, selected_m


def _band_signed(
    link_level: pd.DataFrame,
    evr: dict[int, float],
    comparison_id: str,
    link: str,
    pc_lo: int,
    pc_hi: int,
) -> float | None:
    sub = link_level[
        (link_level["comparison_id"] == comparison_id)
        & (link_level["link_id"] == link)
        & (link_level["pc"] >= pc_lo)
        & (link_level["pc"] <= pc_hi)
    ]
    if sub.empty:
        return None
    total = 0.0
    for r in sub.itertuples():
        w = evr.get(int(r.pc), 0.0)
        total += float(r.JcvPCA_link) * w
    return total


def _same_sign_exceed(long_v: float | None, nv_v: float | None) -> bool:
    if long_v is None or nv_v is None:
        return False
    if long_v == 0 or nv_v == 0:
        return False
    return abs(long_v) > abs(nv_v) and np.sign(long_v) == np.sign(nv_v)


def _sort_links(
    links: list[str],
    long_vals: dict[str, float | None],
    nv_vals: dict[str, float | None],
    excl_long: dict[str, str],
) -> list[str]:
    def tier(link: str) -> tuple[int, float]:
        if excl_long.get(link):
            return (3, 0.0)
        if _same_sign_exceed(long_vals.get(link), nv_vals.get(link)):
            lv, nv = long_vals[link], nv_vals[link]
            assert lv is not None and nv is not None
            return (0, -(abs(lv) - abs(nv)))
        lv = long_vals.get(link)
        nv = nv_vals.get(link)
        if lv is not None and nv is not None and abs(lv) > abs(nv):
            return (1, -abs(lv))
        return (2, -abs(lv) if lv is not None else 0.0)

    return sorted(links, key=tier)


def _plot_overlap_panel(
    ax,
    links: list[str],
    long_vals: dict[str, float | None],
    nv_vals: dict[str, float | None],
    excl_long: dict[str, str],
    title: str,
) -> None:
    y = np.arange(len(links))
    bar_h = 0.55
    ylabels: list[str] = []

    for i, link in enumerate(links):
        reason = excl_long.get(link, "")
        exceeds = _same_sign_exceed(long_vals.get(link), nv_vals.get(link))
        mark = " ★" if exceeds else ""
        ylabels.append(f"{link}{mark}" if not reason else f"{link} [excl]")

        if reason:
            ax.barh(i, 0, height=bar_h, color="#e8e8e8", edgecolor="#999", hatch="///")
            continue

        lv = long_vals.get(link)
        nv = nv_vals.get(link)
        edge_long = COLOR_EXCEED if exceeds else "white"
        if lv is not None:
            ax.barh(
                i,
                lv,
                height=bar_h,
                color=COLOR_LONG,
                alpha=0.55,
                edgecolor=edge_long,
                linewidth=1.2 if exceeds else 0.4,
                label="pooled longitudinal" if i == 0 else None,
            )
        if nv is not None:
            ax.barh(
                i,
                nv,
                height=bar_h * 0.72,
                color=COLOR_NV,
                alpha=0.55,
                edgecolor="white",
                linewidth=0.4,
                label="NV T1_R1 vs R2" if i == 0 else None,
            )

    ax.axvline(0, color="#333", lw=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(ylabels, fontsize=6.5)
    ax.set_xlabel("EVR-weighted signed Δ (band sum)")
    ax.set_title(title, fontsize=9)
    ax.invert_yaxis()


def plot_figure(
    results_root: Path,
    excl: pd.DataFrame,
    pid: str,
    band: str,
    out_dir: Path,
) -> Path:
    run_dir = results_root / "step04_primary_runs" / pid / RUN
    link_level = pd.read_csv(run_dir / "link_level_results.csv")
    jcv = pd.read_csv(run_dir / "jcvpca_results.csv")
    sel = pd.read_csv(run_dir / "selected_m_by_comparison.csv").set_index("comparison_id")
    bands = pd.read_csv(results_root / "step04_primary_runs" / "functional_pc_bands.csv")
    bands = bands[bands["participant"].astype(str) == pid]

    cid_nv = f"{pid}_{COMP_NV}"
    m_nv = int(sel.loc[cid_nv, "selected_m"])
    p60_nv, m_nv = _band_meta(bands, jcv, pid, COMP_NV, m_nv)
    evr_nv = _evr_by_pc(jcv, cid_nv)

    panels: list[tuple[str, str, int, int, int]] = []
    for comp_suffix, label in ((COMP_T3, "T1 vs T3"), (COMP_T2, "T1 vs T2")):
        cid = f"{pid}_{comp_suffix}"
        m = int(sel.loc[cid, "selected_m"])
        p60, m = _band_meta(bands, jcv, pid, comp_suffix, m)
        if band == "functional":
            pc_lo, pc_hi, n_pcs = 1, p60, p60
            band_label = f"functional 60% · PC1–{p60} (n={n_pcs})"
        else:
            pc_lo, pc_hi = p60 + 1, m
            n_pcs = max(0, m - p60)
            band_label = f"null / secondary 40% · PC{p60 + 1}–{m} (n={n_pcs})"
        panels.append((comp_suffix, f"{label} pooled\n{band_label}", pc_lo, pc_hi, p60))

    all_links: set[str] = set()
    for comp_suffix, _, _, _, _ in panels:
        cid = f"{pid}_{comp_suffix}"
        all_links |= set(link_level[link_level["comparison_id"] == cid]["link_id"].unique())
        sub = excl[(excl["participant"].astype(str) == pid) & (excl["comparison_id"] == cid)]
        all_links |= set(sub["link_id"].astype(str))

    # NV band uses NV comparison's p60 cut
    if band == "functional":
        nv_lo, nv_hi = 1, p60_nv
    else:
        nv_lo, nv_hi = p60_nv + 1, m_nv

    panel_data: list[dict] = []
    for comp_suffix, title, pc_lo, pc_hi, p60 in panels:
        cid = f"{pid}_{comp_suffix}"
        evr = _evr_by_pc(jcv, cid)
        long_vals: dict[str, float | None] = {}
        nv_vals: dict[str, float | None] = {}
        excl_long: dict[str, str] = {}
        for link in all_links:
            excl_long[link] = _excl_reason(excl, pid, comp_suffix, link)
            if excl_long[link]:
                long_vals[link] = None
            else:
                long_vals[link] = _band_signed(link_level, evr, cid, link, pc_lo, pc_hi)
            excl_nv = _excl_reason(excl, pid, COMP_NV, link)
            nv_vals[link] = (
                None
                if excl_nv
                else _band_signed(link_level, evr_nv, cid_nv, link, nv_lo, nv_hi)
            )
        ordered = _sort_links(sorted(all_links), long_vals, nv_vals, excl_long)
        panel_data.append(
            {
                "title": title,
                "links": ordered,
                "long": long_vals,
                "nv": nv_vals,
                "excl": excl_long,
            }
        )

    # Shared y: union order — sort by left panel (T3) tiers
    shared_links = panel_data[0]["links"]
    for link in panel_data[1]["links"]:
        if link not in shared_links:
            shared_links.append(link)

    fig_h = max(6.0, 0.30 * len(shared_links) + 2.0)
    fig, axes = plt.subplots(1, 2, figsize=(13, fig_h), sharey=True)

    for ax, pdata in zip(axes, panel_data):
        _plot_overlap_panel(
            ax,
            shared_links,
            pdata["long"],
            pdata["nv"],
            pdata["excl"],
            pdata["title"],
        )

    star_patch = mpatches.Patch(facecolor="white", edgecolor=COLOR_EXCEED, label="★ same-sign NV exceed")
    excl_patch = mpatches.Patch(facecolor="#e8e8e8", edgecolor="#999", hatch="///", label="QC excluded")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles + [star_patch, excl_patch],
        labels + ["★ same-sign NV exceed", "QC excluded"],
        loc="upper center",
        ncol=4,
        fontsize=8,
        bbox_to_anchor=(0.5, 1.01),
    )

    band_title = "Functional (60% T1 EVR)" if band == "functional" else "Null / secondary (~40% EVR tail)"
    fig.suptitle(
        f"{pid} — {band_title} · pooled vs NV (overlapped)\n"
        f"NV floor: T1_R1 vs T1_R2 · PC cut p60={p60_nv}, m={m_nv}",
        y=1.05,
        fontsize=11,
        fontweight="bold",
    )
    fig.tight_layout()

    suffix = "functional_60pct" if band == "functional" else "null_40pct"
    fname = f"{pid}_{suffix}_T2_T3_vs_NV.png"
    out_path = out_dir / fname
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    return out_path


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
        default=ROOT / "docs" / "fun_null_t3_nv_by_link",
    )
    args = parser.parse_args()

    _configure_plt()
    excl = _load_exclusions(args.results_root)
    written: list[Path] = []
    for pid in PIDS:
        for band in ("functional", "null"):
            written.append(plot_figure(args.results_root, excl, pid, band, args.out_dir))

    # Remove legacy per-PC figures if present
    for old in args.out_dir.glob("*_by_pc.png"):
        old.unlink(missing_ok=True)

    readme = args.out_dir / "README.md"
    readme.write_text(
        "# Functional / null bands — pooled vs NV (8 figures)\n\n"
        f"**Source:** `{args.results_root.name}` · `{RUN}`\n\n"
        "## Layout\n\n"
        "**8 figures** = 4 participants × 2 band types.\n\n"
        "Each figure has **2 panels** (side by side):\n"
        "- **Left (1A / 2A):** T1 vs T3 pooled overlapped with NV (T1_R1 vs T1_R2)\n"
        "- **Right (1B / 2B):** T1 vs T2 pooled overlapped with NV\n\n"
        "| Figure | Band |\n|--------|------|\n"
        "| `{pid}_functional_60pct_T2_T3_vs_NV.png` | PC1…`p_functional_60` (60% T1 EVR) |\n"
        "| `{pid}_null_40pct_T2_T3_vs_NV.png` | PC(`p60`+1)…`selected_m` (~40% tail) |\n\n"
        "- **Values:** EVR-weighted signed sum of `JcvPCA_link` across PCs in band\n"
        "- **Blue:** pooled longitudinal · **Red:** NV floor (semi-transparent overlap)\n"
        "- **★ top:** same-sign exceed (`|long|>|nv|` same sign), sorted first\n"
        "- **Grey hatch:** QC / marker-gap excluded\n\n"
        "## Files\n\n"
        + "\n".join(f"- `{p.name}`" for p in written)
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(written)} figures → {args.out_dir}")
    for p in written:
        print(f"  {p.name}")


if __name__ == "__main__":
    main()
