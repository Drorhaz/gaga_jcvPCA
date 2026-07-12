"""Canonical reference-pose extraction (RENDER_PLAN E2 / E10).

One pose per participant, taken as the mean bone position over the T1 R1
ex10-15 window, reused for every view of that participant so T1->T2 and T1->T3
are directly comparable. Output: ``geometry/{participant}_reference_pose.json``.

Motive skeleton exports carry a per-bone global ``Position`` (X/Y/Z) alongside
the rotation quaternion. The project's ``parse_motive_take`` only extracts the
quaternion channel, so bone positions are read here directly from the same
header layout helpers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd

from gaga_jcvpca import project_io
from gaga_jcvpca.config import Config, load_config
from gaga_jcvpca.naming import NamingMap
from gaga_jcvpca.project_io import (
    _find_frame_row,
    _find_type_row,
    _read_motive_header_rows,
    parse_motive_meta,
)

_POSITION_AXES = ("X", "Y", "Z")


def _load_exclude_tokens(config: Config) -> list[str]:
    """Distal segment tokens to drop from the avatar (fingers/thumbs/toes).

    Read from ``configs/body_regions.yaml`` so it stays consistent with the
    analysis scope and requires no per-participant edits.
    """
    try:
        regions_path = config.resolve_path("body_regions_config")
    except KeyError:
        regions_path = config.project_root / "configs" / "body_regions.yaml"
    if not regions_path.exists():
        return ["Finger", "Thumb", "Toe", "Pinky", "Index", "Middle", "Ring"]
    import yaml
    with open(regions_path, "r", encoding="utf-8") as fh:
        spec = yaml.safe_load(fh) or {}
    return list(spec.get("exclude_tokens", []) or [])


def _is_excluded(token: str, exclude_tokens: list[str]) -> bool:
    low = token.lower()
    return any(tok.lower() in low for tok in exclude_tokens)


def _short_token(bone_name: str) -> str:
    """Motive bone name -> short joint token (``671:LUArm`` -> ``LUArm``)."""
    if ":" in bone_name:
        return bone_name.split(":", 1)[1]
    if "_" in bone_name:
        return bone_name.split("_", 1)[1]
    return bone_name


@dataclass(frozen=True)
class PoseWindow:
    session_id: str
    ex_start: int
    ex_end: int
    start_frame: int
    end_frame: int
    n_frames: int


def _bone_position_columns(rows: list[list[str]]) -> tuple[list[str], dict[str, dict[str, int]]]:
    """Return bone order and a {bone_name: {axis: col_index}} map for Position.

    Uses the ``Type`` row to find Bone columns, the following ``Name`` row for
    the bone name, the ``Parent`` sub-header block for Position/Rotation, and the
    ``Frame`` row for the X/Y/Z axis label.
    """
    type_idx = _find_type_row(rows)
    frame_idx = _find_frame_row(rows)
    type_row = rows[type_idx]
    name_row = rows[type_idx + 1]
    frame_row = rows[frame_idx]
    # The row directly above Frame carries "Position"/"Rotation" channel labels.
    channel_row = rows[frame_idx - 1]

    order: list[str] = []
    pos_cols: dict[str, dict[str, int]] = {}
    for i, token in enumerate(type_row):
        if token.strip() != "Bone":
            continue
        channel = channel_row[i].strip() if i < len(channel_row) else ""
        if channel != "Position":
            continue
        name = name_row[i].strip() if i < len(name_row) else f"col{i}"
        axis = frame_row[i].strip() if i < len(frame_row) else ""
        if axis not in _POSITION_AXES:
            continue
        if name not in pos_cols:
            order.append(name)
            pos_cols[name] = {}
        pos_cols[name][axis] = i
    return order, pos_cols


def _resolve_window(config: Config, participant: str, session_id: str,
                    ex_start: int, ex_end: int, task_part: str) -> PoseWindow:
    seg_dir = config.resolve_path("data.segmentation")
    workbooks = project_io.find_segmentation_workbooks(seg_dir)
    if participant not in workbooks:
        raise FileNotFoundError(f"No segmentation workbook for participant {participant}")
    naming = NamingMap(config)
    segments = project_io.load_segments_for_workbook(
        workbooks[participant], naming, task_part_scope=task_part
    )
    window_segs = [
        s for s in segments
        if s.session.as_str() == session_id and ex_start <= s.exercise_id <= ex_end
    ]
    if not window_segs:
        raise ValueError(
            f"No ex{ex_start}-ex{ex_end} segments for {session_id} in the workbook"
        )
    start = min(int(s.start_frame) for s in window_segs)
    end = max(int(s.end_frame) for s in window_segs)
    return PoseWindow(
        session_id=session_id, ex_start=ex_start, ex_end=ex_end,
        start_frame=start, end_frame=end, n_frames=end - start,
    )


def extract_reference_pose(
    participant: str,
    config: Config | None = None,
    ex_window: tuple[int, int] = (10, 15),
    reference_timepoint: str = "T1",
    reference_repetition: str = "R1",
    task_part: str = "P1",
) -> dict:
    """Build the mean-pose dict for one participant from its raw skeleton take."""
    config = config or load_config()
    session_id = f"{participant}_{reference_timepoint}_{task_part}_{reference_repetition}"

    skel_path = project_io.resolve_session_skeleton(config, session_id)
    if skel_path is None:
        raise FileNotFoundError(f"No raw skeleton CSV for {session_id}")

    window = _resolve_window(
        config, participant, session_id, ex_window[0], ex_window[1], task_part
    )

    rows = _read_motive_header_rows(skel_path)
    meta = parse_motive_meta(rows[0])
    order, pos_cols = _bone_position_columns(rows)
    if not order:
        raise ValueError(f"No bone Position columns found in {skel_path}")

    frame_idx = _find_frame_row(rows)
    usecols = sorted({c for axes in pos_cols.values() for c in axes.values()})
    data_start = frame_idx + 1
    df = pd.read_csv(
        skel_path, skiprows=data_start, header=None, usecols=usecols, low_memory=False
    )
    # Clip the window to the frames actually present in the take.
    lo = max(0, window.start_frame)
    hi = min(len(df), window.end_frame)
    frame_slice = df.iloc[lo:hi]

    exclude_tokens = _load_exclude_tokens(config)

    hierarchy_full = project_io.read_skeleton_hierarchy_from_take(skel_path)
    hierarchy = {
        _short_token(child): _short_token(parent)
        for child, parent in hierarchy_full.items()
        if not _is_excluded(_short_token(child), exclude_tokens)
        and not _is_excluded(_short_token(parent), exclude_tokens)
    }

    joints: dict[str, list[float]] = {}
    for bone in order:
        token = _short_token(bone)
        if _is_excluded(token, exclude_tokens):
            continue
        axes = pos_cols[bone]
        coords = []
        for axis in _POSITION_AXES:
            col = axes.get(axis)
            if col is None:
                coords.append(float("nan"))
                continue
            vals = pd.to_numeric(frame_slice[col], errors="coerce")
            coords.append(float(np.nanmean(vals)))
        joints[token] = coords

    return {
        "participant": participant,
        "session_id": session_id,
        "reference_timepoint": reference_timepoint,
        "reference_repetition": reference_repetition,
        "window": asdict(window),
        "length_units": meta.get("Length Units", ""),
        "up_axis": "Y",
        "joints": joints,
        "hierarchy": hierarchy,
        "source_csv": skel_path.name,
    }


def write_reference_pose(participant: str, avatar_dir: Path,
                         config: Config | None = None, **kwargs) -> Path:
    pose = extract_reference_pose(participant, config=config, **kwargs)
    geom_dir = avatar_dir / "geometry"
    geom_dir.mkdir(parents=True, exist_ok=True)
    out_path = geom_dir / f"{participant}_reference_pose.json"
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(pose, fh, indent=2)
    return out_path


def load_reference_pose(participant: str, avatar_dir: Path) -> dict:
    path = avatar_dir / "geometry" / f"{participant}_reference_pose.json"
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)
