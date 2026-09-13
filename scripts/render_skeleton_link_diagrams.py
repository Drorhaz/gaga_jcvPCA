"""Stick-figure skeleton diagrams with labeled link arrows.

One PNG per committee participant (each uses its T1 R1 reference pose and
feature-manifest link stems). Output also includes Setup A/B reference copies
(671 and 252) for the two skeleton baselines in Step 2.

Usage:
  PYTHONPATH=src .venv/bin/python scripts/render_skeleton_link_diagrams.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import yaml
from matplotlib.patches import FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "avater_671_252"))

from gaga_jcvpca.config import load_config  # noqa: E402
from gaga_jcvpca.qc_markers import load_link_specs_for_participant  # noqa: E402
from render.geometry import Pose2D, pose_to_2d  # noqa: E402
from render.pose import extract_reference_pose, load_reference_pose  # noqa: E402

PARTICIPANTS = ("671", "252", "651", "790")
SETUP_BY_PARTICIPANT = {"671": "A", "651": "A", "252": "B", "790": "B"}
SETUP_REFERENCE = {"A": "671", "B": "252"}
OUT_DIR = ROOT / "results_committee_case" / "step02_link_mapping" / "skeleton_link_diagrams"
AVATAR_DIR = ROOT / "avater_671_252"

REGION_COLORS = {
    "trunk_spine": "#8B5E3C",
    "head_neck": "#5B5EA6",
    "left_arm": "#1B9AAA",
    "right_arm": "#C44D58",
    "left_leg": "#2D936C",
    "right_leg": "#E8871E",
    "other": "#6C757D",
}


def _load_region_rules() -> list[tuple[str, list[str]]]:
    path = ROOT / "configs" / "body_regions.yaml"
    with open(path, encoding="utf-8") as fh:
        spec = yaml.safe_load(fh) or {}
    return [(rid, list(meta.get("match_any", []) or [])) for rid, meta in spec["regions"].items()]


REGION_RULES = _load_region_rules()


def region_for_stem(stem: str) -> str:
    for region_id, tokens in REGION_RULES:
        if any(tok in stem for tok in tokens):
            return region_id
    return "other"


def load_pose(participant: str, config) -> dict:
    json_path = AVATAR_DIR / "geometry" / f"{participant}_reference_pose.json"
    if json_path.exists():
        return load_reference_pose(participant, AVATAR_DIR)
    return extract_reference_pose(participant, config=config)


def layout_edges(hierarchy: dict[str, str], link_pairs: set[tuple[str, str]]) -> list[tuple[str, str]]:
    pairs = set(link_pairs)
    pairs |= {(b, a) for a, b in link_pairs}
    out: list[tuple[str, str]] = []
    for child, parent in hierarchy.items():
        if not parent or parent == child:
            continue
        if (parent, child) in pairs:
            continue
        out.append((parent, child))
    return out


def _offset_for_region(region_id: str, dx: float, dy: float, idx: int) -> tuple[float, float]:
    length = float(np.hypot(dx, dy)) or 1.0
    nx, ny = -dy / length, dx / length
    side = 1.0 if idx % 2 == 0 else -1.0
    if region_id == "left_arm":
        return 18.0, 12.0
    if region_id == "right_arm":
        return -18.0, 12.0
    if region_id == "left_leg":
        return 16.0, -10.0
    if region_id == "right_leg":
        return -16.0, -10.0
    if region_id == "head_neck":
        return 0.0, 22.0 + 6.0 * (idx % 3)
    if region_id == "trunk_spine":
        return side * 28.0, 8.0 + 5.0 * (idx % 4)
    return side * nx * 14.0, side * ny * 14.0


def render_diagram(participant: str, pose: dict, link_specs: list[tuple[str, str, str]], out_path: Path) -> None:
    pose2d: Pose2D = pose_to_2d(pose)
    hierarchy = pose.get("hierarchy", {})
    setup = SETUP_BY_PARTICIPANT[participant]
    ref_pid = SETUP_REFERENCE[setup]

    unique_links: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for stem, parent, child in link_specs:
        if stem in seen:
            continue
        seen.add(stem)
        unique_links.append((stem, parent, child))

    link_pairs = {(p, c) for _, p, c in unique_links}

    fig, ax = plt.subplots(figsize=(11, 14), dpi=150)
    ax.set_facecolor("#FAFAFA")

    for parent, child in layout_edges(hierarchy, link_pairs):
        seg = pose2d.segment(parent, child)
        if seg is None:
            continue
        (x0, y0), (x1, y1) = seg
        ax.plot([x0, x1], [y0, y1], color="#B8BEC6", linewidth=1.2, linestyle="--", zorder=1)

    region_counts: dict[str, int] = {}
    missing: list[str] = []
    for stem, parent, child in unique_links:
        seg = pose2d.segment(parent, child)
        if seg is None:
            missing.append(stem)
            continue
        (x0, y0), (x1, y1) = seg
        region_id = region_for_stem(stem)
        color = REGION_COLORS.get(region_id, REGION_COLORS["other"])
        idx = region_counts.get(region_id, 0)
        region_counts[region_id] = idx + 1

        arrow = FancyArrowPatch(
            (x0, y0),
            (x1, y1),
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=2.8,
            color=color,
            alpha=0.92,
            zorder=3,
            shrinkA=8,
            shrinkB=8,
        )
        ax.add_patch(arrow)

        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        ox, oy = _offset_for_region(region_id, x1 - x0, y1 - y0, idx)
        label = stem.replace("_to_", "\n→ ")
        ax.annotate(
            label,
            xy=(mx, my),
            xytext=(mx + ox, my + oy),
            fontsize=6.5,
            ha="center",
            va="center",
            color="#1F2933",
            bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": color, "alpha": 0.92, "lw": 0.8},
            arrowprops={"arrowstyle": "-", "color": color, "lw": 0.6, "shrinkA": 0, "shrinkB": 0},
            zorder=5,
        )

    for _, (x, y) in pose2d.points.items():
        ax.scatter([x], [y], s=14, color="#303030", zorder=4)

    ax.set_aspect("equal")
    ax.axis("off")
    xmin, xmax, ymin, ymax = pose2d.bounds
    padx = (xmax - xmin) * 0.28 + 1e-6
    pady = (ymax - ymin) * 0.10 + 1e-6
    ax.set_xlim(xmin - padx, xmax + padx)
    ax.set_ylim(ymin - pady, ymax + pady)

    title = (
        f"Participant {participant} — Setup {setup} skeleton reference\n"
        f"Link stems from feature manifest ({len(unique_links)} links, T1 R1 mean pose)"
    )
    ax.set_title(title, fontsize=12, pad=12)

    legend_handles = [
        matplotlib.patches.Patch(color=color, label=rid.replace("_", " "))
        for rid, color in REGION_COLORS.items()
        if rid != "other"
    ]
    ax.legend(handles=legend_handles, loc="upper right", fontsize=7, framealpha=0.9, title="Region")

    footnote = f"Reference pose: {pose.get('session_id', '')} | source: {pose.get('source_csv', '')}"
    if missing:
        footnote += f"\nMissing joints for {len(missing)} link(s): {', '.join(missing[:4])}"
        if len(missing) > 4:
            footnote += ", …"
    fig.text(0.5, 0.02, footnote, ha="center", va="bottom", fontsize=7, color="#52606D")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> int:
    config = load_config()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for pid in PARTICIPANTS:
        pose = load_pose(pid, config)
        link_specs = load_link_specs_for_participant(config, pid)
        out = OUT_DIR / f"{pid}_skeleton_link_map.png"
        render_diagram(pid, pose, link_specs, out)
        print(f"wrote {out}")

    for setup, ref_pid in SETUP_REFERENCE.items():
        pose = load_pose(ref_pid, config)
        link_specs = load_link_specs_for_participant(config, ref_pid)
        out = OUT_DIR / f"setup_{setup.lower()}_{ref_pid}_reference_link_map.png"
        render_diagram(ref_pid, pose, link_specs, out)
        print(f"wrote {out} (Setup {setup} skeleton reference)")

    readme = OUT_DIR / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# Skeleton link diagrams",
                "",
                "Stick-figure reference pose (T1 R1 mean, ex10–15) with arrows labeled by "
                "jcvPCA **link stem** from each participant's feature manifest.",
                "",
                "## Files",
                "",
                "| PNG | Description |",
                "|---|---|",
                "| `{pid}_skeleton_link_map.png` | Per-participant diagram (correct `{pid}_to_*` pelvis labels) |",
                "| `setup_a_671_reference_link_map.png` | Setup A (671-style) skeleton reference |",
                "| `setup_b_252_reference_link_map.png` | Setup B (252-style) skeleton reference |",
                "",
                "Gray dashed segments = bone hierarchy connectors (layout only). "
                "Colored arrows = analytic links used in jcvPCA.",
                "",
                "Regenerate:",
                "```bash",
                "PYTHONPATH=src .venv/bin/python scripts/render_skeleton_link_diagrams.py",
                "```",
            ]
        ),
        encoding="utf-8",
    )
    print(f"wrote {readme}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
