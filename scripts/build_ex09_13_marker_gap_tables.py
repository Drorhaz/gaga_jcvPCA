"""Per-participant marker gap tables for the pooled ex09-13 analysis window.

One CSV per participant (671, 252, 651, 790). Rows = session × marker with:
  - session label T1_R1 … T3_R2
  - marker name
  - count of contiguous missing runs longer than 0.5 s
  - % of ex09-13 window frames falling inside those large gaps
  - related jcvPCA link stem(s) derived from marker → bone attachment

Usage:
  PYTHONPATH=src .venv/bin/python scripts/build_ex09_13_marker_gap_tables.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca.config import load_config  # noqa: E402
from gaga_jcvpca.inventory import build_inventory  # noqa: E402
from gaga_jcvpca import project_io  # noqa: E402
from gaga_jcvpca.marker_bone_map import (  # noqa: E402
    build_participant_marker_bone_map,
    marker_short,
    related_links_for_marker,
)
from gaga_jcvpca.qc_markers import (  # noqa: E402
    detect_gaps,
    load_link_specs_for_participant,
    marker_data_from_take,
    velocity_artifact_counts_per_marker,
    _slice_marker_data,
)

PARTICIPANTS = ("671", "252", "651", "790")
EXERCISE_IDS = (9, 10, 11, 12, 13)
OUT_DIR = ROOT / "results_committee_case" / "step03_trunk_extension" / "marker_gap_tables_ex09_13"
MAP_DIR = ROOT / "data" / "link_mapping"


def ex09_13_frame_ranges(segments: list, n_session_frames: int) -> tuple[int, int, int]:
    """Return (start, end, n_window_frames) for ex09-13 contiguous slice."""
    wanted = set(EXERCISE_IDS)
    windows = sorted(
        (s for s in segments if int(s.exercise_id) in wanted),
        key=lambda s: int(s.start_frame),
    )
    if not windows:
        return 0, n_session_frames, n_session_frames
    start = max(0, int(windows[0].start_frame))
    end = min(n_session_frames, int(windows[-1].end_frame))
    n_window = max(0, end - start)
    return start, end, n_window


def session_label(session_id: str) -> str:
    """671_T1_P1_R1 -> T1_R1"""
    parts = session_id.split("_")
    if len(parts) >= 4:
        return f"{parts[1]}_{parts[3]}"
    return session_id


def _reference_session(participant: str, session_ids: list[str]) -> str:
    preferred = f"{participant}_T1_P1_R1"
    if preferred in session_ids:
        return preferred
    return session_ids[0]


def _write_marker_bone_audit(participant: str, mapping: dict[str, str], link_specs) -> None:
    from gaga_jcvpca.marker_bone_map import links_for_bone_token

    MAP_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for label in sorted(mapping):
        token = mapping[label]
        links = links_for_bone_token(token, link_specs)
        rows.append(
            {
                "participant": participant,
                "marker_label": label,
                "bone_token": token,
                "related_links": "; ".join(links) if links else "",
            }
        )
    pd.DataFrame(rows).to_csv(MAP_DIR / f"marker_bone_map_{participant}.csv", index=False)


def build_participant_table(
    participant: str,
    config,
    inventory,
    qc_cfg: dict,
) -> pd.DataFrame:
    frame_rate = float(qc_cfg["capture"]["frame_rate_hz"])
    large_gap_s = float(qc_cfg["gaps"]["large_gap_seconds"])
    link_specs = load_link_specs_for_participant(config, participant)
    try:
        desc_dir = config.resolve_path("data.descriptions")
    except KeyError:
        desc_dir = ROOT / "data" / "descriptions"

    segments_by_session: dict[str, list] = {}
    for seg in inventory.segments:
        segments_by_session.setdefault(seg.session.as_str(), []).append(seg)

    session_ids = sorted(
        sid
        for sid in segments_by_session
        if sid.startswith(f"{participant}_")
        and "_P1_" in sid
        and (sid.endswith("_R1") or sid.endswith("_R2"))
    )
    if not session_ids:
        return pd.DataFrame()

    ref_sid = _reference_session(participant, session_ids)
    ref_path = project_io.resolve_session_skeleton(config, ref_sid)
    ref_take = project_io.parse_motive_take(ref_path) if ref_path else None
    w_start, w_end, _ = ex09_13_frame_ranges(
        segments_by_session.get(ref_sid, []),
        ref_take.n_frames if ref_take else 0,
    )
    marker_bone_map = build_participant_marker_bone_map(
        participant,
        config,
        reference_session_id=ref_sid,
        frame_start=w_start,
        frame_end=w_end,
        descriptions_dir=desc_dir,
    )
    _write_marker_bone_audit(participant, marker_bone_map, link_specs)

    rows: list[dict] = []
    for sid in session_ids:
        path = project_io.resolve_session_skeleton(config, sid)
        if path is None:
            continue
        take = project_io.parse_motive_take(path)
        md_full = marker_data_from_take(take, frame_rate_hz=frame_rate)
        segs = segments_by_session.get(sid, [])
        w_start, w_end, n_window = ex09_13_frame_ranges(segs, md_full.n_frames)
        if n_window == 0:
            continue
        md = _slice_marker_data(md_full, w_start, w_end)
        if md is None:
            continue

        artifact_counts = velocity_artifact_counts_per_marker(md, qc_cfg)
        n_intervals = max(md.n_frames - 1, 1)

        label = session_label(sid)
        for mi, marker in enumerate(md.marker_names):
            presence_col = md.presence[:, mi : mi + 1]
            gaps = detect_gaps(presence_col, [marker], frame_start=0)
            large = [g for g in gaps if g.length_seconds(frame_rate) > large_gap_s]
            gap_mask = np.zeros(md.n_frames, dtype=bool)
            for g in large:
                gap_mask[g.start_frame : g.end_frame + 1] = True
            pct_window = 100.0 * float(gap_mask.sum()) / md.n_frames if md.n_frames else 0.0
            pct_session = (
                100.0 * float(gap_mask.sum()) / md_full.n_frames if md_full.n_frames else 0.0
            )
            short = marker_short(marker)
            n_artifacts = int(artifact_counts[mi])
            pct_artifact_window = round(100.0 * n_artifacts / n_intervals, 3)
            rows.append(
                {
                    "participant": participant,
                    "session_id": sid,
                    "T_R": label,
                    "window": "ex09_13",
                    "session_total_frames": md_full.n_frames,
                    "ex09_13_window_frames": n_window,
                    "marker_name": marker,
                    "attached_bone_token": marker_bone_map.get(short, ""),
                    "n_gaps_gt_0p5s": len(large),
                    "pct_frames_in_large_gaps_of_session": round(pct_session, 3),
                    "pct_frames_in_large_gaps_of_window": round(pct_window, 3),
                    "n_velocity_artifacts": n_artifacts,
                    "pct_velocity_artifacts_of_window": pct_artifact_window,
                    "related_links": related_links_for_marker(marker, link_specs, marker_bone_map),
                }
            )

    return pd.DataFrame(rows)


def write_markdown_summary(tables: dict[str, pd.DataFrame], out_dir: Path) -> None:
    lines = [
        "# Marker gap tables — ex09-13 window",
        "",
        "Per participant: all markers × sessions `T1_R1` … `T3_R2`.",
        "",
        "**Window:** contiguous ex09–ex13 (same slice as primary jcvPCA).",
        "",
        "**`n_gaps_gt_0p5s`:** contiguous missing-marker runs longer than 0.5 s.",
        "",
        "**`pct_frames_in_large_gaps_of_session`:** % of **full session** frames inside large gaps "
        "(gaps detected within the ex09-13 slice only).",
        "",
        "**`n_velocity_artifacts` / `pct_velocity_artifacts_of_window`:** frame intervals where "
        "this marker's speed exceeds the window's shared 99.97th-percentile threshold "
        "(same rule as segment QC; attributed per marker). Denominator = ex09-13 window intervals "
        "(n_frames − 1).",
        "",
        "**`related_links`:** jcvPCA link stems from marker→bone mapping "
        "(DataDescriptions when present; else nearest bone Position in skeleton CSV). "
        "Audit maps: `data/link_mapping/marker_bone_map_{pid}.csv`.",
        "",
        "Full CSVs: one file per participant in this folder.",
        "",
    ]
    for pid, df in tables.items():
        lines.append(f"## Participant {pid}")
        lines.append("")
        lines.append(f"- Markers per session: **{df['marker_name'].nunique()}**")
        lines.append(f"- Sessions: **{df['T_R'].nunique()}**")
        mapped = df[~df["related_links"].str.startswith(("no link match", "unlabeled", "bone="))]
        lines.append(
            f"- Rows with manifest link mapping: **{len(mapped)}/{len(df)}** "
            f"({100*len(mapped)/max(len(df),1):.0f}%)"
        )
        lines.append(f"- CSV: [`{pid}_ex09_13_marker_gaps.csv`]({pid}_ex09_13_marker_gaps.csv)")
        lines.append("")
        agg = (
            df.groupby("marker_name")
            .agg(
                max_pct=("pct_frames_in_large_gaps_of_window", "max"),
                total_large_gaps=("n_gaps_gt_0p5s", "sum"),
                related_links=("related_links", "first"),
            )
            .sort_values("max_pct", ascending=False)
        )
        flagged = agg[agg["total_large_gaps"] > 0].head(12)
        if not flagged.empty:
            lines.append("Markers with largest large-gap footprint (top 12 by max % window):")
            lines.append("")
            lines.append("| marker | max % window in large gaps | total large gaps (all sessions) | related links |")
            lines.append("|---|---:|---:|---|")
            for marker, row in flagged.iterrows():
                links = str(row["related_links"]).replace("|", "\\|")
                lines.append(
                    f"| `{marker}` | {row['max_pct']:.1f} | {int(row['total_large_gaps'])} | {links} |"
                )
            lines.append("")
    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    config = load_config()
    inventory = build_inventory(config)
    with open(ROOT / "configs" / "qc_thresholds.yaml", encoding="utf-8") as fh:
        qc_cfg = yaml.safe_load(fh)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tables: dict[str, pd.DataFrame] = {}
    for pid in PARTICIPANTS:
        df = build_participant_table(pid, config, inventory, qc_cfg)
        out = OUT_DIR / f"{pid}_ex09_13_marker_gaps.csv"
        df.to_csv(out, index=False)
        tables[pid] = df
        mapped = df[~df["related_links"].str.startswith(("no link match", "unlabeled", "bone="))]
        print(
            f"wrote {out} ({len(df)} rows; link-mapped {len(mapped)}/{len(df)})"
        )

    write_markdown_summary(tables, OUT_DIR)
    print(f"wrote {OUT_DIR / 'README.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
