"""Rep-sensitivity 2×2 panels: pooled single-rep longitudinal vs NV floor.

One figure per participant (4 total):
  rows = T2 | T3; cols = R1-matched | R2-matched longitudinal
  NV floor fixed: T1_R1 vs T1_R2 (signed EVR-weighted sum, all retained PCs)

Usage:
  PYTHONPATH=src .venv/bin/python scripts/plot_rep_sensitivity_nv_panels.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gaga_jcvpca import nv_profile
from gaga_jcvpca.config import load_config
from gaga_jcvpca.selection import load_selection, region_of_link

import observed_nv as nv_mod

PIDS = ("671", "252", "651", "790")
GROUP4 = nv_mod.GROUP4_IDS
COLOR_LONG = "#1a73e8"
COLOR_NV = "#ea4335"
COLOR_EXCEED = "#0d904f"

PANELS = (
    ("T2", "R1", "T1_R1 vs T2_R1"),
    ("T2", "R2", "T1_R2 vs T2_R2"),
    ("T3", "R1", "T1_R1 vs T3_R1"),
    ("T3", "R2", "T1_R2 vs T3_R2"),
)


def _configure_plt() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 160,
            "font.size": 9,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
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


def _excl_reason(excl: pd.DataFrame, pid: str, followup: str, link: str) -> str:
    cid = f"{pid}_T1_vs_{followup}"
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
        return f"{src}: {reason[:60]}"
    return reason[:70]


def _same_sign_exceed(long_v: float | None, nv_v: float | None) -> bool:
    if long_v is None or nv_v is None or long_v == 0 or nv_v == 0:
        return False
    return abs(long_v) > abs(nv_v) and np.sign(long_v) == np.sign(nv_v)


def _magnitude_exceed(long_v: float | None, nv_v: float | None) -> bool:
    if long_v is None or nv_v is None:
        return False
    return abs(long_v) > abs(nv_v)


def _long_r1(evidence: pd.DataFrame, pid: str, followup: str) -> dict[str, float]:
    cid = f"{pid}_T1_vs_{followup}"
    sub = evidence[(evidence["participant"].astype(str) == pid) & (evidence["comparison_id"] == cid)]
    return {str(r.link_id): float(r.long_signed_single) for r in sub.itertuples() if pd.notna(r.long_signed_single)}


def _long_r2_matched(
    pid: str,
    followup: str,
    config,
    features: list[str],
    vt: float,
    region_fn,
) -> dict[str, float]:
    comp = nv_mod._comp_on(
        pid,
        config,
        features,
        vt,
        region_fn,
        a_tp="T1",
        a_rep="R2",
        b_tp=followup,
        b_rep="R2",
        exercise_ids=GROUP4,
        comparison_id=f"{pid}_T1R2_vs_{followup}R2_ex09_13",
    )
    if comp is None:
        return {}
    return nv_profile.link_signed_value(comp.link_table, weighted=True).to_dict()


def _nv_floor(evidence: pd.DataFrame, pid: str) -> dict[str, float]:
    sub = evidence[evidence["participant"].astype(str) == pid]
    if sub.empty:
        return {}
    return {str(r.link_id): float(r.nv_signed_t1) for r in sub.itertuples() if pd.notna(r.nv_signed_t1)}


def _sort_links(
    links: list[str],
    panel_long: dict[str, float | None],
    nv_vals: dict[str, float],
    excl: dict[str, str],
) -> list[str]:
    def key(link: str) -> tuple[int, float]:
        if excl.get(link):
            return (3, 0.0)
        lv, nv = panel_long.get(link), nv_vals.get(link)
        if _same_sign_exceed(lv, nv):
            assert lv is not None and nv is not None
            return (0, -(abs(lv) - abs(nv)))
        if _magnitude_exceed(lv, nv):
            return (1, -abs(lv) if lv is not None else 0.0)
        return (2, -abs(lv) if lv is not None else 0.0)

    return sorted(links, key=key)


def _plot_panel(ax, links: list[str], long_vals, nv_vals, excl, title: str) -> None:
    y = np.arange(len(links))
    bar_h = 0.55
    labels = []
    for i, link in enumerate(links):
        reason = excl.get(link, "")
        exc = _same_sign_exceed(long_vals.get(link), nv_vals.get(link))
        mag = _magnitude_exceed(long_vals.get(link), nv_vals.get(link))
        mark = " ★" if exc else (" †" if mag else "")
        labels.append(f"{link}{mark}" if not reason else f"{link} [excl]")
        if reason:
            ax.barh(i, 0, height=bar_h, color="#e8e8e8", edgecolor="#999", hatch="///")
            continue
        lv = long_vals.get(link)
        nv = nv_vals.get(link)
        if lv is not None:
            ax.barh(
                i,
                lv,
                height=bar_h,
                color=COLOR_LONG,
                alpha=0.55,
                edgecolor=COLOR_EXCEED if exc else "white",
                linewidth=1.2 if exc else 0.4,
                label="longitudinal" if i == 0 else None,
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
    ax.set_yticklabels(labels, fontsize=5.5)
    ax.set_xlabel("signed Δ (EVR-weighted sum)")
    ax.set_title(title, fontsize=8)
    ax.invert_yaxis()


def build_participant_data(
    pid: str,
    evidence: pd.DataFrame,
    excl: pd.DataFrame,
    config,
    features: list[str],
    vt: float,
    region_fn,
) -> tuple[list[str], list[dict]]:
    nv = _nv_floor(evidence, pid)
    long_r2: dict[str, dict[str, float]] = {}
    for followup in ("T2", "T3"):
        long_r2[followup] = _long_r2_matched(pid, followup, config, features, vt, region_fn)

    all_links: set[str] = set(nv.keys())
    for followup in ("T2", "T3"):
        all_links |= set(_long_r1(evidence, pid, followup).keys())
        all_links |= set(long_r2[followup].keys())
        cid = f"{pid}_T1_vs_{followup}"
        sub = excl[(excl["participant"].astype(str) == pid) & (excl["comparison_id"] == cid)]
        all_links |= set(sub["link_id"].astype(str))

    panel_payloads: list[dict] = []
    for followup, rep, title in PANELS:
        comp_excl = {link: _excl_reason(excl, pid, followup, link) for link in all_links}
        if rep == "R1":
            long_map = _long_r1(evidence, pid, followup)
        else:
            long_map = long_r2[followup]
        long_vals = {link: long_map.get(link) for link in all_links}
        nv_vals = {link: nv.get(link) for link in all_links}
        ordered = _sort_links(sorted(all_links), long_vals, nv_vals, comp_excl)
        panel_payloads.append(
            {
                "followup": followup,
                "rep": rep,
                "title": f"{title}\nvs NV T1_R1↔R2",
                "links": ordered,
                "long": long_vals,
                "nv": nv_vals,
                "excl": comp_excl,
            }
        )

    shared = panel_payloads[0]["links"]
    for p in panel_payloads[1:]:
        for link in p["links"]:
            if link not in shared:
                shared.append(link)
    for p in panel_payloads:
        p["links"] = shared

    return shared, panel_payloads


def plot_participant(
    pid: str,
    evidence: pd.DataFrame,
    excl: pd.DataFrame,
    config,
    features: list[str],
    vt: float,
    region_fn,
    out_dir: Path,
) -> tuple[Path, Path]:
    _, panels = build_participant_data(pid, evidence, excl, config, features, vt, region_fn)
    n_links = len(panels[0]["links"])
    fig_h = max(7.0, 0.22 * n_links + 2.5)
    fig, axes = plt.subplots(2, 2, figsize=(12, fig_h), sharey=True)

    for ax, pdata in zip(axes.ravel(), panels):
        _plot_panel(ax, pdata["links"], pdata["long"], pdata["nv"], pdata["excl"], pdata["title"])

    star = mpatches.Patch(facecolor="white", edgecolor=COLOR_EXCEED, label="★ same-sign exceed")
    dag = mpatches.Patch(facecolor="white", edgecolor="#888", label="† magnitude exceed only")
    excl_p = mpatches.Patch(facecolor="#e8e8e8", edgecolor="#999", hatch="///", label="QC excluded")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(
        h + [star, dag, excl_p],
        l + ["★ same-sign exceed", "† |long|>|nv| only", "QC excluded"],
        loc="upper center",
        ncol=5,
        fontsize=7,
        bbox_to_anchor=(0.5, 1.01),
    )
    fig.suptitle(
        f"{pid} — repetition sensitivity · single-rep longitudinal vs NV floor\n"
        "Rows: T2 / T3 · Cols: R1-matched / R2-matched",
        y=1.04,
        fontsize=11,
        fontweight="bold",
    )
    fig.tight_layout()

    png = out_dir / f"{pid}_rep_sensitivity_nv_2x2.png"
    fig.savefig(png, bbox_inches="tight")
    plt.close(fig)

    rows = []
    for pdata in panels:
        for link in pdata["links"]:
            lv = pdata["long"].get(link)
            nv = pdata["nv"].get(link)
            rows.append(
                {
                    "participant": pid,
                    "panel": pdata["title"].split("\n")[0],
                    "followup": pdata["followup"],
                    "rep_match": pdata["rep"],
                    "link_id": link,
                    "long_signed": lv,
                    "nv_signed_t1": nv,
                    "magnitude_exceed": _magnitude_exceed(lv, nv),
                    "same_sign_exceed": _same_sign_exceed(lv, nv),
                    "qc_exclusion": pdata["excl"].get(link, ""),
                }
            )
    csv = out_dir / f"{pid}_rep_sensitivity_nv_flags.csv"
    pd.DataFrame(rows).to_csv(csv, index=False)
    return png, csv


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
        default=ROOT / "docs" / "rep_sensitivity_nv_panels",
    )
    args = parser.parse_args()

    _configure_plt()
    config = load_config()
    vt = float(config.get("pca.variance_threshold", 0.80))
    evidence = pd.read_csv(args.results_root / "step08_nv_and_stability" / "NV_EVIDENCE.csv")
    excl = _load_exclusions(args.results_root)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for pid in PIDS:
        sel_path = config.resolve_path("outputs.root") / "selections" / f"{pid}_{nv_mod.WINDOW}.yaml"
        selection = load_selection(sel_path)
        features = selection.feature_columns()
        region_fn = lambda link, c=config: region_of_link(link, c)
        png, csv = plot_participant(pid, evidence, excl, config, features, vt, region_fn, args.out_dir)
        written.extend([png, csv])
        print(f"  {png.name}")

    readme = args.out_dir / "README.md"
    readme.write_text(
        "# Repetition sensitivity — NV exceedance (2×2 per participant)\n\n"
        f"**Source:** `{args.results_root.name}` · `ex09_13_contiguous`\n\n"
        "## Layout (4 figures)\n\n"
        "One PNG per participant; **2×2 panels**:\n\n"
        "| | R1-matched | R2-matched |\n"
        "|---|---|---|\n"
        "| **T2** | T1_R1 vs T2_R1 | T1_R2 vs T2_R2 |\n"
        "| **T3** | T1_R1 vs T3_R1 | T1_R2 vs T3_R2 |\n\n"
        "**NV floor (all panels):** `T1_R1 vs T1_R2` — red bar\n\n"
        "**Values:** EVR-weighted signed sum across retained PCs (`NV_EVIDENCE` + on-the-fly R2–R2 comps)\n\n"
        "- **★** same-sign exceed (`|long|>|nv|`, same sign)\n"
        "- **†** magnitude exceed only\n"
        "- Links sorted with ★ first in each panel\n\n"
        "Companion CSV: `{pid}_rep_sensitivity_nv_flags.csv`\n",
        encoding="utf-8",
    )
    print(f"Wrote {len([p for p in written if p.suffix == '.png'])} figures → {args.out_dir}")


if __name__ == "__main__":
    main()
