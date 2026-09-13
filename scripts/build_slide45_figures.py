"""Generate slide 4-5 presentation figures from verified marker-gap results.

Outputs under ``docs/slide45_figures/``:
  slide04/v1_openness_aggregate.png
  slide04/v3_nv_filter_671_T2.png
  slide05/v4_four_participant_avatars.png
  slide05/v6_org_vs_amplitude.png
  backup/  (copies of supporting figures + README)

Usage:
  PYTHONPATH=src .venv/bin/python scripts/build_slide45_figures.py
  PYTHONPATH=src .venv/bin/python scripts/build_slide45_figures.py --skip-avatar
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Circle
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "avater_671_252"))

from gaga_jcvpca.config import load_config

PIDS = ("671", "252", "651", "790")
COMPARISON = "T1_vs_T2"
DEFAULT_RESULTS = ROOT / "results_committee_case" / "marker_gap_policy_ex09_13"
OUT_ROOT = ROOT / "docs" / "slide45_figures"
AVATAR_POOLED_ROOT = OUT_ROOT / "avatar_pooled"

# Public-facing gradient palette (7 colors): grey + 3 decrease blues + 3 increase warm
GRADIENT_WITHIN = "#B0B0B0"
RATIO_CAP = 3.0
STRONG_RATIO = 2.0
ROM_FLAT_LO = 0.7
ROM_FLAT_HI = 1.3

# One diverging scale over the signed effect ratio; the neutral band spans |ratio| <= 1,
# so "inside the variability floor" is part of the same colour axis rather than a side legend.
_GREY_LO = (-1.0 + RATIO_CAP) / (2 * RATIO_CAP)
_GREY_HI = (1.0 + RATIO_CAP) / (2 * RATIO_CAP)
SIGNED_CMAP = LinearSegmentedColormap.from_list(
    "signed_effect_ratio",
    [
        (0.000, "#08306B"),
        (0.150, "#2171B5"),
        (_GREY_LO - 0.001, "#9ECAE1"),
        (_GREY_LO, GRADIENT_WITHIN),
        (_GREY_HI, GRADIENT_WITHIN),
        (_GREY_HI + 0.001, "#FEC44F"),
        (0.850, "#EC7014"),
        (1.000, "#99000D"),
    ],
)
SIGNED_NORM = Normalize(vmin=-RATIO_CAP, vmax=RATIO_CAP)
REGION_CHIP = {
    "left_arm": "Arms",
    "right_arm": "Arms",
    "left_leg": "Legs",
    "right_leg": "Legs",
    "trunk_spine": "Trunk",
    "head_neck": "Head",
}
REGION_CHIP_ORDER = ("Arms", "Legs", "Trunk", "Head")
EXERCISES = ["ex09", "ex10", "ex11", "ex12", "ex13"]
EX_LABELS = ["Hands", "Elbows", "Shoulders", "Nose", "Whole body"]

# A2 categorical palette (slide plan)
COLOR_WITHIN = "#B0B0B0"
COLOR_A2_INC = "#DC143C"
COLOR_A2_DEC = "#08519C"
COLOR_S3_INC = "#FF4500"
COLOR_S3_DEC = "#1E3A8A"
COLOR_PERSIST_RING = "#FFD700"
COLOR_BONE = "#404040"
COLOR_LAYOUT = "#9AA0A6"


def _configure_plt() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 400,
            "font.size": 11,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def _run_avatar_tables_pooled(results_root: Path, avatar_root: Path) -> None:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "build_avatar_tables_pooled.py"),
        "--results-root",
        str(results_root),
        "--output-root",
        str(avatar_root),
    ]
    subprocess.run(cmd, check=True, cwd=ROOT)


def _run_avatar_tables(results_root: Path, avatar_root: Path) -> None:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "build_avatar_tables_verified.py"),
        "--results-root",
        str(results_root),
        "--output-root",
        str(avatar_root),
    ]
    subprocess.run(cmd, check=True, cwd=ROOT)


def _ensure_poses(participants: tuple[str, ...], geometry_dir: Path) -> None:
    """Extract reference poses for participants missing geometry JSON."""
    from render.pose import extract_reference_pose

    config = load_config()
    geometry_dir.mkdir(parents=True, exist_ok=True)
    for pid in participants:
        out = geometry_dir / f"{pid}_reference_pose.json"
        if out.exists():
            continue
        print(f"  extracting pose for {pid}...")
        pose = extract_reference_pose(
            participant=pid,
            config=config,
            ex_window=(9, 13),
            reference_timepoint="T1",
            reference_repetition="R1",
            task_part="P1",
        )
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(pose, fh, indent=2)


def _signed_ratio(ratio: float, signed: float) -> float:
    """Effect ratio carried on the sign of the EVR-weighted signed change."""
    if not np.isfinite(ratio):
        return 0.0
    r = min(float(ratio), RATIO_CAP)
    return -r if signed < 0 else r


def _fill_color(ratio: float, signed: float) -> str:
    if not np.isfinite(ratio) or ratio <= 1.0:
        return GRADIENT_WITHIN
    return mcolors.to_hex(SIGNED_CMAP(SIGNED_NORM(_signed_ratio(ratio, signed))))


def _participant_caption(link_df: pd.DataFrame, participant: str) -> str:
    above = link_df[link_df["exceeds_variability"]] if "exceeds_variability" in link_df else link_df
    return f"Participant {participant}\n{len(above)} of {len(link_df)} links above floor"


def _draw_single_avatar_gradient(
    ax,
    participant: str,
    link_df: pd.DataFrame,
    pose_path: Path,
    *,
    row_label: str = "",
) -> None:
    from render.geometry import pose_to_2d
    from render.topology import TAG_ANALYTIC, TAG_LAYOUT_ONLY, TAG_PARTICIPANT_SPECIFIC, all_edges

    with open(pose_path, encoding="utf-8") as fh:
        pose_raw = json.load(fh)
    pose2d = pose_to_2d(pose_raw)
    edges = all_edges(link_df, participant, pose_raw.get("hierarchy", {}))
    styles = link_df.set_index("link_id").to_dict("index")

    for edge in edges:
        seg = pose2d.segment(edge.parent_joint, edge.child_joint)
        if seg is None:
            continue
        (x0, y0), (x1, y1) = seg
        if edge.tag == TAG_LAYOUT_ONLY:
            ax.plot([x0, x1], [y0, y1], linestyle="--", color=COLOR_LAYOUT, linewidth=1.2, zorder=1)
            continue
        if edge.link_id not in styles:
            ax.plot([x0, x1], [y0, y1], linestyle="--", color=COLOR_LAYOUT, linewidth=1.5, zorder=2)
            continue

        row = styles[edge.link_id]
        ratio = float(row.get("effect_ratio_vs_variability", np.nan))
        signed = float(row.get("long_signed", 0.0))
        if not np.isfinite(ratio) or ratio <= 1.0:
            ax.plot(
                [x0, x1], [y0, y1],
                color=GRADIENT_WITHIN,
                linewidth=7,
                solid_capstyle="round",
                zorder=2.5,
                alpha=0.85,
            )
            continue

        fill = _fill_color(ratio, signed)
        lw = 10.5 if ratio >= STRONG_RATIO else 9
        ax.plot(
            [x0, x1], [y0, y1],
            color="#2F2F2F",
            linewidth=lw + 2.0,
            solid_capstyle="round",
            zorder=2.8,
            alpha=0.45,
        )
        ax.plot([x0, x1], [y0, y1], color=fill, linewidth=lw, solid_capstyle="round", zorder=3)

    for _, (x, y) in pose2d.points.items():
        ax.scatter([x], [y], s=11, color=COLOR_BONE, zorder=6)

    ax.set_aspect("equal")
    ax.axis("off")
    xmin, xmax, ymin, ymax = pose2d.bounds
    padx = (xmax - xmin) * 0.15 + 1e-6
    pady = (ymax - ymin) * 0.08 + 1e-6
    ax.set_xlim(xmin - padx, xmax + padx)
    ax.set_ylim(ymin - pady, ymax + pady)

    ax.set_title(_participant_caption(link_df, participant), fontsize=10, pad=4)


def plot_v4_pooled_gradient_public(
    out_path: Path,
    avatar_root: Path,
    geometry_dir: Path,
) -> None:
    """Four participants × two follow-ups: signed coordination change on each link, scaled by
    that person's own between-repetition variability at baseline."""
    row_specs = [
        ("T1_vs_T2", "Mid-course\n(T2 vs T1)"),
        ("T1_vs_T3", "End of course\n(T3 vs T1)"),
    ]

    fig = plt.figure(figsize=(14.0, 9.4))
    gs = fig.add_gridspec(
        2,
        4,
        left=0.065,
        right=0.975,
        top=0.818,
        bottom=0.165,
        hspace=0.22,
        wspace=0.08,
    )

    tables = {}
    for r, (cmp_suffix, label) in enumerate(row_specs):
        for c, pid in enumerate(PIDS):
            link_df = pd.read_csv(avatar_root / "tables" / "link_level" / f"{pid}_{cmp_suffix}_links.csv")
            tables[(pid, cmp_suffix)] = link_df

            pose_path = geometry_dir / f"{pid}_reference_pose.json"
            if not pose_path.exists():
                alt = OUT_ROOT / "avatar_verified" / "geometry" / f"{pid}_reference_pose.json"
                if alt.exists():
                    pose_path = alt

            ax = fig.add_subplot(gs[r, c])
            _draw_single_avatar_gradient(ax, pid, link_df, pose_path)
            if c == 0:
                ax.annotate(
                    label,
                    xy=(-0.16, 0.5),
                    xycoords="axes fraction",
                    fontsize=10.5,
                    ha="center",
                    va="center",
                    rotation=90,
                    color="#222222",
                    linespacing=1.3,
                )

    pooled = pd.concat(tables.values())
    above = pooled[pooled["exceeds_variability"]]
    n_above = len(above)
    n_flat = int(above["amplitude_flat"].sum())
    n_inc = int((above["signed_direction"] == "increase").sum())
    n_dec = int((above["signed_direction"] == "decrease").sum())
    cax = fig.add_axes([0.365, 0.092, 0.30, 0.022])
    cbar = fig.colorbar(
        ScalarMappable(norm=SIGNED_NORM, cmap=SIGNED_CMAP),
        cax=cax,
        orientation="horizontal",
        ticks=[-RATIO_CAP, -1.0, 1.0, RATIO_CAP],
    )
    cap_label = f"{RATIO_CAP:g}×"
    cbar.ax.set_xticklabels([cap_label, "1×", "1×", cap_label], fontsize=8)
    cbar.outline.set_linewidth(0.6)
    cbar.outline.set_edgecolor("#666666")
    fig.text(
        0.515,
        0.127,
        "Coordination change, in multiples of the person's own repetition variability",
        ha="center",
        fontsize=9.5,
        color="#333333",
    )
    fig.text(0.362, 0.055, "◀ weaker coupling", ha="left", fontsize=9, color="#1F4E9C")
    fig.text(0.668, 0.055, "stronger coupling ▶", ha="right", fontsize=9, color="#A5121B")

    fig.legend(
        handles=[mpatches.Patch(facecolor=GRADIENT_WITHIN, edgecolor="none")],
        labels=["Within repetition variability"],
        loc="center left",
        bbox_to_anchor=(0.065, 0.100),
        frameon=False,
        fontsize=9,
        handlelength=2.4,
    )

    fig.suptitle(
        "Coordination reorganises without a change in movement amplitude",
        y=0.960,
        fontsize=16,
        fontweight="bold",
    )
    fig.text(
        0.5,
        0.917,
        f"{n_above} links shifted beyond the person's own repetition variability; "
        f"range of motion was unchanged in {n_flat} of them",
        ha="center",
        fontsize=11.5,
        color="#333333",
    )
    fig.text(
        0.5,
        0.884,
        "Pooled JcvPCA, exercises 09–13, all retained components  ·  "
        "variability floor = repetition 1 vs 2 at baseline  ·  four single-case series, descriptive",
        ha="center",
        fontsize=9,
        color="#666666",
    )
    fig.text(
        0.5,
        0.012,
        "1× = the link's coordination changed as much as it already differed between the two baseline "
        f"repetitions.  {cap_label} = three times that, where the scale is capped.\n"
        f"Above the floor: {n_inc} links strengthened, {n_dec} weakened.  "
        "Each component is weighted by the variance it explains, so low-variance components cannot drive the result.",
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


def _link_color(category: str) -> str:
    return {
        "within_nv": COLOR_WITHIN,
        "a2_increase": COLOR_A2_INC,
        "a2_decrease": COLOR_A2_DEC,
        "s3_increase": COLOR_S3_INC,
        "s3_decrease": COLOR_S3_DEC,
    }.get(category, COLOR_WITHIN)


def _draw_single_avatar(ax, participant: str, link_df: pd.DataFrame, pose_path: Path) -> None:
    from render.geometry import pose_to_2d
    from render.topology import TAG_ANALYTIC, TAG_LAYOUT_ONLY, TAG_PARTICIPANT_SPECIFIC, all_edges

    with open(pose_path, encoding="utf-8") as fh:
        pose_raw = json.load(fh)
    pose2d = pose_to_2d(pose_raw)
    edges = all_edges(link_df, participant, pose_raw.get("hierarchy", {}))

    styles = link_df.set_index("link_id").to_dict("index")

    for edge in edges:
        seg = pose2d.segment(edge.parent_joint, edge.child_joint)
        if seg is None:
            continue
        (x0, y0), (x1, y1) = seg
        if edge.tag == TAG_LAYOUT_ONLY:
            ax.plot([x0, x1], [y0, y1], linestyle="--", color=COLOR_LAYOUT, linewidth=1.2, zorder=1)
            continue
        if edge.tag == TAG_PARTICIPANT_SPECIFIC or edge.link_id not in styles:
            ax.plot([x0, x1], [y0, y1], linestyle="--", color=COLOR_LAYOUT, linewidth=1.5, zorder=2)
            continue

        row = styles[edge.link_id]
        fill = _link_color(str(row.get("display_category", "within_nv")))
        ax.plot([x0, x1], [y0, y1], color=fill, linewidth=8, solid_capstyle="round", zorder=3, alpha=0.9)

        if bool(row.get("persistent", False)):
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            ax.add_patch(
                Circle(
                    (mx, my),
                    radius=max(abs(x1 - x0), abs(y1 - y0)) * 0.18 + 8,
                    fill=False,
                    edgecolor=COLOR_PERSIST_RING,
                    linewidth=2.5,
                    zorder=5,
                )
            )

    for _, (x, y) in pose2d.points.items():
        ax.scatter([x], [y], s=12, color=COLOR_BONE, zorder=6)

    ax.set_aspect("equal")
    ax.axis("off")
    xmin, xmax, ymin, ymax = pose2d.bounds
    padx = (xmax - xmin) * 0.15 + 1e-6
    pady = (ymax - ymin) * 0.08 + 1e-6
    ax.set_xlim(xmin - padx, xmax + padx)
    ax.set_ylim(ymin - pady, ymax + pady)

    n_a2 = int(link_df["a2_pass"].sum()) if "a2_pass" in link_df.columns else 0
    ax.set_title(f"{participant}\nA2 pass: {n_a2}", fontsize=11, pad=6)


def plot_v4_four_participant_avatars(out_path: Path, avatar_root: Path, geometry_dir: Path) -> None:
    fig, axes = plt.subplots(1, 4, figsize=(14, 5))
    for ax, pid in zip(axes, PIDS):
        link_csv = avatar_root / "tables" / "link_level" / f"{pid}_{COMPARISON}_links.csv"
        link_df = pd.read_csv(link_csv)
        pose_path = geometry_dir / f"{pid}_reference_pose.json"
        if not pose_path.exists():
            src = ROOT / "avater_671_252" / "geometry" / f"{pid}_reference_pose.json"
            if src.exists():
                pose_path = src
        _draw_single_avatar(ax, pid, link_df, pose_path)

    legend = [
        mpatches.Patch(color=COLOR_WITHIN, label="Within NV"),
        mpatches.Patch(color=COLOR_A2_INC, label="A2 increase"),
        mpatches.Patch(color=COLOR_A2_DEC, label="A2 decrease"),
        mpatches.Patch(color=COLOR_S3_INC, label="S3 increase"),
        mpatches.Patch(facecolor="none", edgecolor=COLOR_PERSIST_RING, linewidth=2, label="Persistent T2→T3 (671)"),
    ]
    fig.legend(handles=legend, loc="lower center", ncol=5, fontsize=9, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("Reliable change in every participant, in different places (T1→T2, A2)", y=1.02, fontsize=13)
    fig.text(
        0.5,
        -0.06,
        "Categorical A2/S-tier only — magnitudes not compared across participants. n=4, descriptive.",
        ha="center",
        fontsize=8,
        color="#555",
    )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out_path.relative_to(ROOT)}")


def plot_v1_openness_aggregate(results_root: Path, out_path: Path) -> None:
    df = pd.read_csv(results_root / "step08_nv_and_stability" / "exercise_level_nv.csv")
    df["sess"] = df["participant"].astype(str) + "_" + df["timepoint"].astype(str)
    piv = df.pivot_table(index="sess", columns="exercise", values="median_abs_nv")[EXERCISES]
    norm = piv.div(piv.mean(axis=1), axis=0)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    x = np.arange(len(EXERCISES))
    for sess in norm.index:
        ax.plot(x, norm.loc[sess].values, color="#CCCCCC", linewidth=0.8, alpha=0.7, zorder=1)

    med = norm.median()
    q25 = norm.quantile(0.25)
    q75 = norm.quantile(0.75)
    ax.fill_between(x, q25.values, q75.values, color="#4A90D9", alpha=0.25, label="IQR (12 sessions)")
    ax.plot(x, med.values, color="#1a73e8", linewidth=2.5, marker="o", markersize=6, label="Median", zorder=3)
    ax.axhline(1.0, color="#888", linestyle=":", linewidth=1, label="Session average")

    slopes = [np.polyfit(np.arange(5), norm.loc[s].values, 1)[0] for s in norm.index]
    n_pos = sum(s > 0 for s in slopes)
    ax.text(0.98, 0.05, f"{n_pos}/12 sessions\nincrease ex09→ex13", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=9,
            bbox=dict(boxstyle="round", fc="#F5F5F5", ec="#CCC"))

    ax.set_xticks(x)
    ax.set_xticklabels([f"{e}\n{l}" for e, l in zip(EXERCISES, EX_LABELS)], fontsize=8)
    ax.set_ylabel("Within-session variability\n(relative to session average)")
    ax.set_title("Variability scales with openness")
    ax.legend(loc="upper left", fontsize=8)
    ax.text(0.02, 0.98, "Descriptive protocol context only; ex13 always last (order/fatigue confound).",
            transform=ax.transAxes, fontsize=7, va="top", color="#666")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out_path.relative_to(ROOT)}")


def plot_v3_nv_filter(results_root: Path, out_path: Path) -> None:
    prof = pd.read_csv(results_root / "step08_nv_and_stability" / "NV_PROFILE.csv")
    sub = prof[
        (prof["participant"].astype(str) == "671")
        & (prof["comparison_id"] == "671_T1_vs_T2")
    ].copy()
    sub = sub.sort_values("matched_abs_ratio", ascending=True)

    n_total = len(sub)
    n_mag = int(sub["magnitude_exceed"].sum())
    n_a2 = int(sub["a2_pass"].sum())
    n_s3 = int((sub["nv_profile_tier"] == "S3").sum())

    fig = plt.figure(figsize=(11, 6))
    gs = fig.add_gridspec(1, 5, width_ratios=[4, 0.15, 1.1, 0.05, 0.05], wspace=0.05)
    ax = fig.add_subplot(gs[0, 0])
    ax_funnel = fig.add_subplot(gs[0, 2])

    y = np.arange(len(sub))
    floor = sub["nv_signed_t1"].abs()
    long_v = sub["long_signed_single"]

    for i, (_, row) in enumerate(sub.iterrows()):
        f = float(row["nv_signed_t1"])
        lo, hi = min(f, float(row["long_signed_single"]), 0), max(f, float(row["long_signed_single"]), 0)
        ax.axhspan(i - 0.35, i + 0.35, xmin=0, xmax=1, color="#EEEEEE", zorder=0)
        ax.plot([f, f], [i - 0.35, i + 0.35], color="#EA4335", linewidth=2, zorder=1)
        ax.plot([-f, -f], [i - 0.35, i + 0.35], color="#EA4335", linewidth=1, alpha=0.4, zorder=1)

        tier = str(row["nv_profile_tier"])
        if tier in ("S2", "S3"):
            color = COLOR_A2_INC if float(row["long_signed_single"]) >= 0 else COLOR_A2_DEC
            if tier == "S3":
                color = COLOR_S3_INC if float(row["long_signed_single"]) >= 0 else COLOR_S3_DEC
        elif bool(row["magnitude_exceed"]):
            color = "#F9AB00"
        else:
            color = COLOR_WITHIN
        ax.barh(i, float(row["long_signed_single"]), color=color, height=0.55, zorder=2)

    ax.axvline(0, color="#333", linewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(sub["link_id"], fontsize=8)
    ax.set_xlabel("EVR-weighted signed ΔJcvPCA (671, T1→T2, matched R1)")
    ax.set_title("Only changes larger than the person's own repetition variability are kept")

    ax_funnel.axis("off")
    funnel = [
        ("Links analysed", n_total, "#666"),
        ("Exceed NV floor\n(magnitude)", n_mag, "#F9AB00"),
        ("A2 pass\n(exceed + direction stable)", n_a2, "#0d904f"),
    ]
    if n_s3:
        funnel.append((f"S3\n(+ org gate)", n_s3, "#6A1B9A"))

    y0 = 0.92
    for label, count, color in funnel:
        ax_funnel.text(0.5, y0, str(count), ha="center", va="top", fontsize=18, fontweight="bold", color=color)
        ax_funnel.text(0.5, y0 - 0.06, label, ha="center", va="top", fontsize=8, color="#333")
        y0 -= 0.22

    fig.text(
        0.02,
        0.01,
        "Red tick = NV floor (T1 R1 vs R2). Values are dimensionless contribution shares; interpret ratios, not raw magnitudes.",
        fontsize=7,
        color="#555",
    )
    fig.subplots_adjust(left=0.28, right=0.88, top=0.92, bottom=0.12)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out_path.relative_to(ROOT)}")


def plot_v6_org_vs_amplitude(results_root: Path, out_path: Path) -> None:
    rom = pd.read_csv(results_root / "step05_amplitude_vs_organization" / "rom_rms_by_link.csv")
    counts = rom["classification"].value_counts()
    org = int(counts.get("organization", 0))
    amp = int(counts.get("amplitude", 0))
    mixed = int(counts.get("mixed", 0))

    fig, ax = plt.subplots(figsize=(4.5, 2.2))
    labels = ["Organization\n(flat ROM)", "Amplitude\n(ROM shift)", "Mixed"]
    vals = [org, amp, mixed]
    colors = ["#0d904f", "#DC143C", "#F9AB00"]
    left = 0.0
    for lab, val, col in zip(labels, vals, colors):
        ax.barh(0, val, left=left, color=col, height=0.5, label=f"{lab} ({val})")
        ax.text(left + val / 2, 0, str(val), ha="center", va="center", fontsize=11, color="white", fontweight="bold")
        left += val

    ax.set_xlim(0, left * 1.15)
    ax.set_yticks([])
    ax.set_xlabel("Link × comparison classifications (all participants, T1→T2 and T1→T3)")
    ax.set_title("Above-NV changes are mostly reorganization, not more movement")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.42), ncol=3, fontsize=8, frameon=False)
    ax.text(
        0.5,
        -0.62,
        f"Remaining {len(rom) - org - amp - mixed} rows = within_variability or amplitude_only (not shown). "
        "Step-5 pooled NV footing.",
        transform=ax.transAxes,
        ha="center",
        fontsize=7,
        color="#666",
    )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out_path.relative_to(ROOT)}")


def assemble_backup(out_root: Path, results_root: Path) -> None:
    backup = out_root / "backup"
    backup.mkdir(parents=True, exist_ok=True)

    copies = [
        (ROOT / "docs" / "rep_sensitivity_nv_panels", backup / "rep_sensitivity_nv_panels"),
        (ROOT / "results_4supervisor" / "10_per_exercise_nv_layer2.png", backup / "10_per_exercise_nv_layer2.png"),
        (results_root.parent.parent / "docs" / "supervisor_meeting_figures_marker_gap_policy_ex09_13" / "13_16_sensitivity_nv" / "coverage_rel.png",
         backup / "coverage_rel.png"),
    ]
    # coverage path fallback
    cov_src = ROOT / "docs" / "supervisor_meeting_figures_marker_gap_policy_ex09_13" / "13_16_sensitivity_nv" / "coverage_rel.png"
    if cov_src.exists():
        shutil.copy2(cov_src, backup / "coverage_rel.png")

    for src, dst in copies:
        if not src.exists():
            continue
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    s3_md = backup / "S3_definition_and_caveat.md"
    s3_md.write_text(
        """# S3 tier definition and footing caveat (backup slide)

## Governing S3 definition

S3 = S2 + coverage adequate + repetition pass + Step-5 `classification == "organization"`.

Verified result: **4 S3 links**, all in **671 T1→T2**:
- `671_to_LThigh`, `LFArm_to_LHand`, `LShin_to_LFoot`, `LThigh_to_LShin`

## Footing asymmetry (documented, not resolved)

- **S2/A2** uses matched single-rep signed NV floor (T1_R1 vs T1_R2 vs T1_R1 vs T{k}_R1).
- **Step-5 organization** uses pooled longitudinal effect over single-rep floor on mean-|Δ|.

Both variants are in `NV_PROFILE.csv`: `nv_profile_tier` (governing) and `nv_profile_tier_romflat` (sensitivity).

## Presentation guidance

Treat S3 as supporting detail for 671 only. Headline = A2 pass counts per participant at T2.
""",
        encoding="utf-8",
    )

    readme = out_root / "README.md"
    readme.write_text(
        """# Slide 4–5 presentation figures

Generated from verified `marker_gap_policy_ex09_13` results.

## Slide 4 — method validation

| File | Role |
|---|---|
| `slide04/v1_openness_aggregate.png` | Task openness raises within-session NV (12/12 sessions) |
| `slide04/v3_nv_filter_671_T2.png` | NV filter + funnel (18→11→8→4) for participant 671 |

Add your external ex09–ex13 photo strip above these panels.

## Slide 5 — empirical findings

| File | Role |
|---|---|
| `slide05/v4_four_participant_avatars.png` | Pooled T1→T2 and T1→T3 gradient body maps (public-facing) |
| `slide05/v6_org_vs_amplitude.png` | 51 organization vs 4 amplitude vs 4 mixed |

## Backup

See `backup/` for rep-sensitivity 2×2 panels, raw per-participant NV curves, coverage gate, S3 caveat.

Regenerate:
```bash
PYTHONPATH=src .venv/bin/python scripts/build_slide45_figures.py
```
""",
        encoding="utf-8",
    )
    print(f"  wrote {readme.relative_to(ROOT)} and backup/")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--out-root", type=Path, default=OUT_ROOT)
    parser.add_argument("--skip-avatar", action="store_true")
    args = parser.parse_args()

    _configure_plt()
    results_root = args.results_root.resolve()
    out_root = args.out_root.resolve()
    avatar_pooled = out_root / "avatar_pooled"
    geometry_dir = out_root / "avatar_verified" / "geometry"
    if not geometry_dir.exists():
        geometry_dir = avatar_pooled / "geometry"

    if not args.skip_avatar:
        print("=== Avatar tables (pooled descriptive) ===")
        _run_avatar_tables_pooled(results_root, avatar_pooled)

        print("=== Reference poses ===")
        geometry_dir.mkdir(parents=True, exist_ok=True)
        _ensure_poses(PIDS, geometry_dir)
        for pid in PIDS:
            dst = geometry_dir / f"{pid}_reference_pose.json"
            if not dst.exists():
                src = ROOT / "avater_671_252" / "geometry" / f"{pid}_reference_pose.json"
                if src.exists():
                    shutil.copy2(src, dst)

        print("=== V4 four-participant avatars (pooled gradient) ===")
        plot_v4_pooled_gradient_public(
            out_root / "slide05" / "v4_four_participant_avatars.png",
            avatar_pooled,
            geometry_dir,
        )

    print("=== V1 openness aggregate ===")
    plot_v1_openness_aggregate(results_root, out_root / "slide04" / "v1_openness_aggregate.png")

    print("=== V3 NV filter (671 T2) ===")
    plot_v3_nv_filter(results_root, out_root / "slide04" / "v3_nv_filter_671_T2.png")

    print("=== V6 organization vs amplitude ===")
    plot_v6_org_vs_amplitude(results_root, out_root / "slide05" / "v6_org_vs_amplitude.png")

    print("=== V5 explained-variance sensitivity ===")
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_pc_sensitivity_figure.py"),
            "--results-root",
            str(results_root),
            "--out",
            str(out_root / "slide05" / "v5_pc_sensitivity.png"),
        ],
        check=True,
        cwd=ROOT,
    )

    print("=== V7 cross-participant consistency ===")
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_consistency_figure.py"),
            "--out",
            str(out_root / "slide05" / "v7_consistency.png"),
        ],
        check=True,
        cwd=ROOT,
    )

    print("=== Backup bundle ===")
    assemble_backup(out_root, results_root)

    print(f"\nDone — figures in {out_root.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
