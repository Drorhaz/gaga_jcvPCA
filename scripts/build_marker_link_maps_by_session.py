"""Per-session marker → bone → jcvPCA link maps for ex09-13 window.

One long CSV per participant (all T1_R1 … T3_R2) plus link-centric coverage tables.

Usage:
  PYTHONPATH=src .venv/bin/python scripts/build_marker_link_maps_by_session.py
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca.config import load_config  # noqa: E402
from gaga_jcvpca.inventory import build_inventory  # noqa: E402
from gaga_jcvpca import project_io  # noqa: E402
from gaga_jcvpca.marker_bone_map import (  # noqa: E402
    infer_marker_bone_map_spatial,
    load_marker_bone_map_from_descriptions,
    marker_short,
    merge_marker_bone_maps,
    related_links_for_marker,
)
from gaga_jcvpca.qc_markers import load_link_specs_for_participant  # noqa: E402

PARTICIPANTS = ("671", "252", "651", "790")
EXERCISE_IDS = (9, 10, 11, 12, 13)
OUT_DIR = ROOT / "results_committee_case" / "step02_link_mapping" / "marker_link_maps_ex09_13"


def ex09_13_frame_ranges(segments: list, n_session_frames: int) -> tuple[int, int]:
    wanted = set(EXERCISE_IDS)
    windows = sorted(
        (s for s in segments if int(s.exercise_id) in wanted),
        key=lambda s: int(s.start_frame),
    )
    if not windows:
        return 0, n_session_frames
    start = max(0, int(windows[0].start_frame))
    end = min(n_session_frames, int(windows[-1].end_frame))
    return start, end


def session_label(session_id: str) -> str:
    parts = session_id.split("_")
    if len(parts) >= 4:
        return f"{parts[1]}_{parts[3]}"
    return session_id


def mapping_status(related_links: str) -> str:
    if related_links.startswith("unlabeled"):
        return "unlabeled"
    if related_links.startswith("bone="):
        return "bone_no_manifest_link"
    if related_links.startswith("no link match"):
        return "no_link_match"
    return "manifest_link"


def bone_source_for_marker(
    short: str,
    desc_map: dict[str, str],
    spatial_map: dict[str, str],
    ref_map: dict[str, str],
) -> str:
    if short in desc_map:
        return "descriptions"
    if short in spatial_map:
        return "spatial"
    if short in ref_map:
        return "reference_session"
    return "none"


def _reference_session(participant: str, session_ids: list[str]) -> str:
    preferred = f"{participant}_T1_P1_R1"
    if preferred in session_ids:
        return preferred
    return session_ids[0]


def build_participant_maps(
    participant: str,
    config,
    inventory,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    link_specs = load_link_specs_for_participant(config, participant)
    try:
        desc_dir = config.resolve_path("data.descriptions")
    except KeyError:
        desc_dir = ROOT / "data" / "descriptions"
    desc_map = load_marker_bone_map_from_descriptions(participant, desc_dir)

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

    ref_sid = _reference_session(participant, session_ids)
    ref_spatial_map: dict[str, str] = {}
    ref_path = project_io.resolve_session_skeleton(config, ref_sid)
    if ref_path is not None:
        ref_take = project_io.parse_motive_take(ref_path)
        ref_w_start, ref_w_end = ex09_13_frame_ranges(
            segments_by_session.get(ref_sid, []), ref_take.n_frames
        )
        ref_spatial_map = infer_marker_bone_map_spatial(
            ref_take, ref_path, frame_start=ref_w_start, frame_end=ref_w_end
        )

    marker_rows: list[dict] = []
    link_rows: list[dict] = []

    for sid in session_ids:
        path = project_io.resolve_session_skeleton(config, sid)
        if path is None:
            continue
        take = project_io.parse_motive_take(path)
        w_start, w_end = ex09_13_frame_ranges(segments_by_session.get(sid, []), take.n_frames)
        spatial_map = infer_marker_bone_map_spatial(
            take, path, frame_start=w_start, frame_end=w_end
        )
        marker_bone_map = merge_marker_bone_maps(ref_spatial_map, spatial_map, desc_map)
        label = session_label(sid)

        by_link: dict[str, list[str]] = defaultdict(list)
        for marker in take.marker_names:
            short = marker_short(marker)
            related = related_links_for_marker(marker, link_specs, marker_bone_map)
            status = mapping_status(related)
            marker_rows.append(
                {
                    "participant": participant,
                    "session_id": sid,
                    "T_R": label,
                    "window": "ex09_13",
                    "marker_name": marker,
                    "attached_bone_token": marker_bone_map.get(short, ""),
                    "bone_source": bone_source_for_marker(
                        short, desc_map, spatial_map, ref_spatial_map
                    ),
                    "reference_session_for_fallback": ref_sid,
                    "related_links": related,
                    "mapping_status": status,
                    "n_related_links": len(related.split("; "))
                    if status == "manifest_link"
                    else 0,
                }
            )
            if status == "manifest_link":
                for stem in related.split("; "):
                    by_link[stem.strip()].append(marker)

        manifest_stems = sorted({stem for stem, _, _ in link_specs})
        for stem in manifest_stems:
            markers = sorted(by_link.get(stem, []))
            link_rows.append(
                {
                    "participant": participant,
                    "session_id": sid,
                    "T_R": label,
                    "link_stem": stem,
                    "n_markers": len(markers),
                    "markers": "; ".join(markers),
                }
            )

    return pd.DataFrame(marker_rows), pd.DataFrame(link_rows)


def write_readme(tables: dict[str, pd.DataFrame], link_tables: dict[str, pd.DataFrame]) -> None:
    lines = [
        "# Marker → link maps by session (ex09-13 window)",
        "",
        "Per participant, all sessions `T1_R1` … `T3_R2`. Spatial bone assignment is computed "
        "**per session** on that session's ex09-13 slice. When a session CSV lacks bone Position "
        "channels (e.g. some T3 takes), mapping falls back to the participant reference session "
        "(`T1_R1` when present) — see `bone_source=reference_session`. DataDescriptions rows are "
        "merged when present.",
        "",
        "## Files",
        "",
        "| File | Use when |",
        "|---|---|",
        "| `{pid}_marker_to_link_by_session.csv` | Audit a specific marker across sessions; filter by `mapping_status` |",
        "| `{pid}_link_to_markers_by_session.csv` | See which markers feed each jcvPCA link in each session |",
        "",
        "## Column guide (marker-centric CSV)",
        "",
        "- **`attached_bone_token`**: skeleton bone the marker is assigned to",
        "- **`bone_source`**: `descriptions` | `spatial` | `reference_session` | `none`",
        "- **`reference_session_for_fallback`**: session used when this row's bone came from reference fallback",
        "- **`related_links`**: manifest link stem(s) touching that bone (or status text if unmapped)",
        "- **`mapping_status`**: `manifest_link` | `bone_no_manifest_link` | `no_link_match` | `unlabeled`",
        "",
        "## Recommended ways to show this",
        "",
        "1. **Supervisor table (link-centric)** — open `{pid}_link_to_markers_by_session.csv`, "
        "pivot/filter on `link_stem` and scan `T_R` columns for marker coverage. Best for "
        "\"which links are supported in T3 vs T1?\"",
        "",
        "2. **QC audit (marker-centric)** — open `{pid}_marker_to_link_by_session.csv`, sort by "
        "`mapping_status != manifest_link`. Best for explaining unmapped finger/toe markers.",
        "",
        "3. **Slide figure (heatmap)** — rows = canonical link stems, columns = `T1_R1`…`T3_R2`, "
        "cell = `n_markers` from link-centric CSV (0 = gray, ≥1 = green). One panel per participant.",
        "",
        "4. **Do not** use a full marker×session matrix in slides — too sparse; use link-centric summary instead.",
        "",
        "## Participant summaries",
        "",
    ]

    for pid, df in tables.items():
        n_sessions = df["T_R"].nunique()
        n_markers = df.groupby("T_R")["marker_name"].nunique().mean()
        mapped = df[df["mapping_status"] == "manifest_link"]
        lines.append(f"### Participant {pid}")
        lines.append("")
        lines.append(f"- Sessions: **{n_sessions}**")
        lines.append(f"- Mean markers per session: **{n_markers:.0f}**")
        lines.append(
            f"- Rows with manifest link mapping: **{len(mapped)}/{len(df)}** "
            f"({100 * len(mapped) / max(len(df), 1):.0f}%)"
        )
        lines.append(
            f"- Marker CSV: [`{pid}_marker_to_link_by_session.csv`]({pid}_marker_to_link_by_session.csv)"
        )
        lines.append(
            f"- Link CSV: [`{pid}_link_to_markers_by_session.csv`]({pid}_link_to_markers_by_session.csv)"
        )
        by_session = (
            df.groupby("T_R")
            .agg(
                n_markers=("marker_name", "nunique"),
                n_manifest=("mapping_status", lambda s: int((s == "manifest_link").sum())),
            )
            .reset_index()
        )
        lines.append("")
        lines.append("| T_R | markers | manifest-mapped |")
        lines.append("|---|---:|---:|")
        for _, row in by_session.iterrows():
            lines.append(
                f"| {row['T_R']} | {int(row['n_markers'])} | {int(row['n_manifest'])} |"
            )
        lines.append("")

    (OUT_DIR / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    config = load_config()
    inventory = build_inventory(config)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    marker_tables: dict[str, pd.DataFrame] = {}
    link_tables: dict[str, pd.DataFrame] = {}

    for pid in PARTICIPANTS:
        marker_df, link_df = build_participant_maps(pid, config, inventory)
        marker_out = OUT_DIR / f"{pid}_marker_to_link_by_session.csv"
        link_out = OUT_DIR / f"{pid}_link_to_markers_by_session.csv"
        marker_df.to_csv(marker_out, index=False)
        link_df.to_csv(link_out, index=False)
        marker_tables[pid] = marker_df
        link_tables[pid] = link_df
        mapped = marker_df[marker_df["mapping_status"] == "manifest_link"]
        print(
            f"wrote {marker_out.name} ({len(marker_df)} rows; "
            f"manifest-mapped {len(mapped)}/{len(marker_df)})"
        )
        print(f"wrote {link_out.name} ({len(link_df)} rows)")

    write_readme(marker_tables, link_tables)
    print(f"wrote {OUT_DIR / 'README.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
