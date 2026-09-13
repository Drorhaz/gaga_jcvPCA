"""What is consistent across the four participants, despite person-specific link patterns.

Left panel  — change runs from the body core outward: the share of joints that moved beyond
              the repetition floor rises from axial to distal.
Right panel — how many of the four participants show at least one changed link in each body
              region, at mid-course and at end of course.

Subdivided spine and neck chains are collapsed to one canonical joint each, so participants
whose marker set splits the trunk are not counted several times for the same rotation.

Outputs:
  docs/slide45_figures/slide05/v7_consistency.png (+ .pdf)
  docs/slide45_figures/slide05/v7_consistency.csv

Usage:
  PYTHONPATH=src .venv/bin/python scripts/build_consistency_figure.py
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "docs" / "slide45_figures" / "avatar_pooled" / "tables" / "link_level"
OUT_PATH = ROOT / "docs" / "slide45_figures" / "slide05" / "v7_consistency.png"

PARTICIPANTS = ("671", "252", "651", "790")
COMPARISONS = ("T1_vs_T2", "T1_vs_T3")
CMP_LABEL = {"T1_vs_T2": "Mid-course", "T1_vs_T3": "End of course"}

LEVELS = ("axial", "proximal", "middle", "distal")
LEVEL_LABEL = {
    "axial": "axial\ntrunk, neck",
    "proximal": "proximal\nshoulder, hip",
    "middle": "middle\nelbow, knee",
    "distal": "distal\nwrist, ankle",
}
DISTAL = ("LFArm_to_LHand", "RFArm_to_RHand", "LShin_to_LFoot", "RShin_to_RFoot")
MIDDLE = ("LUArm_to_LFArm", "RUArm_to_RFArm", "LThigh_to_LShin", "RThigh_to_RShin")
PROXIMAL = ("LShoulder_to_LUArm", "RShoulder_to_RUArm", "root_to_LThigh", "root_to_RThigh")
TRUNK_CHAIN = ("Ab_to_Chest", "Ab_to_Spine2", "Spine2_to_Spine3", "Spine3_to_Spine4", "Spine4_to_Chest")
NECK_CHAIN = ("Neck_to_Head", "Neck_to_Neck2", "Neck2_to_Head")

REGION_ORDER = ("Left arm", "Right arm", "Left leg", "Right leg", "Trunk / Spine", "Head / Neck")
PARTICIPANT_COLOR = {"671": "#7FA8C9", "252": "#8FBF9F", "651": "#D4A26A", "790": "#B79BC4"}
CMP_COLOR = {"T1_vs_T2": "#9ECAE1", "T1_vs_T3": "#2171B5"}


def _canonical(link_id: str) -> str:
    link = re.sub(r"^\d+_to_", "root_to_", link_id)
    if link in TRUNK_CHAIN:
        return "trunk"
    if link in NECK_CHAIN:
        return "neck_head"
    return link


def _level(canon: str) -> str:
    if canon in DISTAL:
        return "distal"
    if canon in MIDDLE:
        return "middle"
    if canon in PROXIMAL:
        return "proximal"
    return "axial"


def _region(link_id: str, region_label: str) -> str:
    """Fold the pelvis-to-abdomen and neck sub-links into the axial regions they belong to."""
    if re.match(r"^\d+_to_Ab$", link_id):
        return "Trunk / Spine"
    if link_id in NECK_CHAIN:
        return "Head / Neck"
    return region_label


def load() -> pd.DataFrame:
    frames = []
    for pid in PARTICIPANTS:
        for comparison in COMPARISONS:
            df = pd.read_csv(TABLES / f"{pid}_{comparison}_links.csv")
            df["participant"] = pid
            frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    df["canonical_joint"] = df["link_id"].map(_canonical)
    df["joint_level"] = df["canonical_joint"].map(_level)
    df["region"] = [_region(l, r) for l, r in zip(df["link_id"], df["region_label"])]
    return df


def joint_table(df: pd.DataFrame) -> pd.DataFrame:
    """One row per canonical joint: a subdivided chain counts once."""
    return (
        df.groupby(["participant", "comparison", "canonical_joint", "joint_level"], as_index=False)
        .agg(effect_ratio=("effect_ratio_vs_variability", "max"), above=("exceeds_variability", "max"))
    )


def plot(df: pd.DataFrame, joints: pd.DataFrame, out_path: Path) -> None:
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

    fig = plt.figure(figsize=(13.0, 6.2))
    gs = fig.add_gridspec(
        1, 2, width_ratios=[1.15, 1.0], left=0.075, right=0.975, top=0.775, bottom=0.175, wspace=0.26
    )
    ax_grad = fig.add_subplot(gs[0, 0])
    ax_region = fig.add_subplot(gs[0, 1])

    x = np.arange(len(LEVELS))
    for pid in PARTICIPANTS:
        sub = joints[joints.participant == pid]
        pct = [100 * sub[sub.joint_level == lvl]["above"].mean() for lvl in LEVELS]
        ax_grad.plot(
            x, pct, marker="o", markersize=5, linewidth=1.4, color=PARTICIPANT_COLOR[pid],
            label=f"Participant {pid}", zorder=3,
        )
    pooled = [100 * joints[joints.joint_level == lvl]["above"].mean() for lvl in LEVELS]
    ax_grad.plot(x, pooled, marker="o", markersize=8, linewidth=3.0, color="#08306B",
                 label="All four pooled", zorder=4)
    for xi, value in zip(x, pooled):
        ax_grad.annotate(f"{value:.0f}%", (xi, value), textcoords="offset points",
                         xytext=(0, 11), ha="center", fontsize=9, fontweight="bold", color="#08306B")

    ax_grad.set_xticks(x)
    ax_grad.set_xticklabels([LEVEL_LABEL[lvl] for lvl in LEVELS], fontsize=9, linespacing=1.5)
    ax_grad.set_ylabel("Joints that changed beyond the floor", fontsize=9.5)
    ax_grad.set_yticks([0, 25, 50, 75, 100])
    ax_grad.set_yticklabels(["0", "25", "50", "75", "100%"], fontsize=8.5)
    ax_grad.set_ylim(-6, 105)
    ax_grad.grid(axis="y", color="#EAEAEA", linewidth=0.7, zorder=0)
    ax_grad.set_axisbelow(True)
    for side in ("top", "right"):
        ax_grad.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax_grad.spines[side].set_color("#999999")
    ax_grad.legend(loc="upper left", frameon=False, fontsize=8.5, handlelength=1.6, labelspacing=0.4)
    ax_grad.set_title("Change runs from the core outward", fontsize=11, pad=10, color="#222222")

    y = np.arange(len(REGION_ORDER))[::-1]
    height = 0.36
    for i, comparison in enumerate(COMPARISONS):
        counts = []
        for region in REGION_ORDER:
            sub = df[(df.comparison == comparison) & df.exceeds_variability & (df.region == region)]
            counts.append(sub.participant.nunique())
        offset = (0.5 - i) * height
        bars = ax_region.barh(y + offset, counts, height=height * 0.9,
                              color=CMP_COLOR[comparison], edgecolor="#333333", linewidth=0.4,
                              label=CMP_LABEL[comparison], zorder=3)
        ax_region.bar_label(bars, fmt="%d", fontsize=8.5, padding=3, color="#444444")

    ax_region.set_yticks(y)
    ax_region.set_yticklabels(REGION_ORDER, fontsize=9.5)
    ax_region.set_xlim(0, 4.6)
    ax_region.set_xticks([0, 1, 2, 3, 4])
    ax_region.set_xticklabels(["0", "1", "2", "3", "4"], fontsize=8.5)
    ax_region.set_xlabel("Participants with a changed link in that region  (of 4)", fontsize=9.5)
    ax_region.grid(axis="x", color="#EAEAEA", linewidth=0.7, zorder=0)
    ax_region.set_axisbelow(True)
    for side in ("top", "right"):
        ax_region.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax_region.spines[side].set_color("#999999")
    ax_region.legend(loc="lower right", frameon=False, fontsize=8.5, handlelength=1.3)
    ax_region.set_title("The limbs change in nearly everyone", fontsize=11, pad=10, color="#222222")

    fig.suptitle(
        "Which links change is personal; where in the body they change is not",
        y=0.945,
        fontsize=14.5,
        fontweight="bold",
    )
    fig.text(
        0.5,
        0.865,
        "Same links, same variability floor, and same weighting as the main figure; "
        "both timepoints pooled on the left, shown separately on the right",
        ha="center",
        fontsize=9.5,
        color="#555555",
    )
    fig.text(
        0.5,
        0.030,
        "Subdivided spine and neck chains are collapsed to one joint each, so a finer marker set does not "
        "count the same rotation twice.\n"
        "790 is the exception to the gradient: its changes are axial rather than distal.",
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
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    args = parser.parse_args()

    df = load()
    joints = joint_table(df)
    joints.to_csv(args.out.with_suffix(".csv"), index=False)
    print(f"  wrote {args.out.with_suffix('.csv').relative_to(ROOT)}")

    for level in LEVELS:
        sub = joints[joints.joint_level == level]
        print(f"  {level:>9}: {100 * sub['above'].mean():.0f}% of joints above floor (n={len(sub)})")

    plot(df, joints, args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
