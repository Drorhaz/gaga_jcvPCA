"""Marker label → skeleton bone token → jcvPCA link stems.

Primary source: Motive DataDescriptions ``Bone Marker`` rows.
Fallback: nearest bone Position channel in the skeleton CSV (for abbreviated
marker sets such as participant 252 / 790 without sidecar bone-marker tables).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from gaga_jcvpca import project_io
from gaga_jcvpca.qc_markers import (
    LinkSpec,
    links_for_marker,
    load_link_specs_for_participant,
    region_of_marker,
)


def bone_token(bone_name: str) -> str:
    base = bone_name.split(":", 1)[1] if ":" in bone_name else bone_name
    return base.rsplit("_", 1)[-1] if "_" in base else base


def marker_short(marker_name: str) -> str:
    return marker_name.split(":")[-1]


def load_marker_bone_map_from_descriptions(
    participant: str,
    descriptions_dir: Path,
) -> dict[str, str]:
    """marker label (no asset prefix) -> attachment bone token."""
    mapping: dict[str, str] = {}
    for path in sorted(descriptions_dir.glob(f"*{participant}*DataDescriptions.csv")):
        with open(path, newline="", encoding="utf-8", errors="replace") as fh:
            reader = csv.reader(fh)
            for row in reader:
                if not row or row[0].strip() != "Bone Marker" or len(row) < 3:
                    continue
                label = row[1].strip()
                bone_name = row[2].strip()
                if label and bone_name:
                    mapping[label] = bone_token(bone_name)
    return mapping


def _bone_position_column_indices(path: Path) -> dict[str, tuple[int, int, int]]:
    """Map Motive bone name -> CSV column indices for Position X,Y,Z."""
    rows = project_io._read_motive_header_rows(path, max_rows=12)
    type_row = rows[project_io._find_type_row(rows)]
    name_row = rows[project_io._find_type_row(rows) + 1]
    frame_row = rows[project_io._find_frame_row(rows)]

    out: dict[str, tuple[int, int, int]] = {}
    i = 0
    while i < len(type_row):
        if type_row[i].strip() != "Bone":
            i += 1
            continue
        name = name_row[i] if i < len(name_row) else ""
        group: list[int] = []
        while i < len(type_row) and type_row[i].strip() == "Bone" and name_row[i] == name:
            group.append(i)
            i += 1
        if len(group) >= 7:
            px, py, pz = group[-3], group[-2], group[-1]
            if (
                px < len(frame_row)
                and py < len(frame_row)
                and pz < len(frame_row)
                and frame_row[px] == "X"
                and frame_row[py] == "Y"
                and frame_row[pz] == "Z"
            ):
                out[name] = (px, py, pz)
    return out


def _positions_to_meters(raw: np.ndarray, length_units: str) -> np.ndarray:
    """Same mm→m axis remap as ``project_io.skeleton_marker_to_meters`` (single row)."""
    arr = np.asarray(raw, dtype=float)
    units = (length_units or "").strip().lower()
    if units.startswith("millimeter"):
        scaled = arr / 1000.0
        out = np.empty_like(scaled)
        out[..., 0] = -scaled[..., 0]
        out[..., 1] = scaled[..., 2]
        out[..., 2] = scaled[..., 1]
        return out
    return arr


def load_bone_positions_m(
    path: Path,
    bone_pos_cols: dict[str, tuple[int, int, int]],
    *,
    frame_start: int = 0,
    frame_end: Optional[int] = None,
    length_units: str = "",
) -> tuple[list[str], np.ndarray]:
    """Return bone names and positions (n_frames, n_bones, 3) in meters."""
    if not bone_pos_cols:
        return [], np.zeros((0, 0, 3))

    usecols = sorted({c for triple in bone_pos_cols.values() for c in triple})
    colmap = {col: ui for ui, col in enumerate(usecols)}
    frame_row_idx = project_io._find_frame_row(
        project_io._read_motive_header_rows(path, max_rows=12)
    )
    read_end = int(frame_end) if frame_end is not None else None
    df = pd.read_csv(
        path,
        skiprows=frame_row_idx + 1,
        header=None,
        usecols=usecols,
        nrows=read_end,
        low_memory=False,
    )
    if frame_start:
        df = df.iloc[int(frame_start) :]
    bone_names = list(bone_pos_cols.keys())
    n_frames = len(df)
    pos = np.full((n_frames, len(bone_names), 3), np.nan, dtype=float)
    for bi, bn in enumerate(bone_names):
        ix, iy, iz = bone_pos_cols[bn]
        raw = np.column_stack(
            [
                pd.to_numeric(df.iloc[:, colmap[ix]], errors="coerce"),
                pd.to_numeric(df.iloc[:, colmap[iy]], errors="coerce"),
                pd.to_numeric(df.iloc[:, colmap[iz]], errors="coerce"),
            ]
        )
        pos[:, bi, :] = _positions_to_meters(raw, length_units)
    return bone_names, pos


def infer_marker_bone_map_spatial(
    take: project_io.MotiveTake,
    skeleton_path: Path,
    *,
    frame_start: int,
    frame_end: int,
    min_present_frac: float = 0.05,
) -> dict[str, str]:
    """Assign each marker to the nearest bone by mean 3D distance in a frame window."""
    bone_pos_cols = _bone_position_column_indices(skeleton_path)
    bone_names, bone_pos = load_bone_positions_m(
        skeleton_path,
        bone_pos_cols,
        frame_start=frame_start,
        frame_end=frame_end,
        length_units=take.meta.get("Length Units", ""),
    )
    if bone_pos.size == 0:
        return {}

    w_start = max(0, int(frame_start))
    w_end = min(take.n_frames, int(frame_end))
    marker_pos = take.marker_positions_m[w_start:w_end]
    marker_pres = take.marker_presence[w_start:w_end]
    n_window = marker_pos.shape[0]
    if n_window == 0:
        return {}

    mapping: dict[str, str] = {}
    for mi, marker in enumerate(take.marker_names):
        present = marker_pres[:, mi]
        if present.mean() < min_present_frac:
            continue
        m_mean = np.nanmean(marker_pos[present, mi, :], axis=0)
        if not np.all(np.isfinite(m_mean)):
            continue

        best_bone = None
        best_dist = float("inf")
        for bi, bn in enumerate(bone_names):
            b_slice = bone_pos[:, bi, :]
            valid = present & np.all(np.isfinite(b_slice), axis=1)
            if valid.sum() < max(3, int(min_present_frac * n_window)):
                valid = np.all(np.isfinite(b_slice), axis=1)
            if valid.sum() == 0:
                continue
            b_mean = np.nanmean(b_slice[valid, :], axis=0)
            if not np.all(np.isfinite(b_mean)):
                continue
            dist = float(np.linalg.norm(m_mean - b_mean))
            if dist < best_dist:
                best_dist = dist
                best_bone = bn
        if best_bone is not None:
            mapping[marker_short(marker)] = bone_token(best_bone)
    return mapping


def merge_marker_bone_maps(*maps: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in maps:
        out.update(m)
    return out


def links_for_bone_token(token: str, link_specs: list[LinkSpec]) -> list[str]:
    stems: list[str] = []
    for stem, parent, child in link_specs:
        if parent == token or child == token:
            stems.append(stem)
    return sorted(set(stems))


def related_links_for_marker(
    marker_name: str,
    link_specs: list[LinkSpec],
    marker_bone_map: dict[str, str],
) -> str:
    short = marker_short(marker_name)
    if short.startswith("Unlabeled"):
        return f"unlabeled ({region_of_marker(marker_name)})"

    stems: set[str] = set()
    bone_tok = marker_bone_map.get(short)
    if bone_tok:
        stems.update(links_for_bone_token(bone_tok, link_specs))

    stems.update(links_for_marker(marker_name, link_specs))

    if not stems:
        if bone_tok:
            region = region_of_marker(marker_name)
            suffix = f"; region={region}" if region != "other" else ""
            return f"bone={bone_tok}; no manifest link{suffix}"
        region = region_of_marker(marker_name)
        if region != "other":
            return f"no link match; region={region}"
        return "no link match"
    return "; ".join(sorted(stems))


def build_participant_marker_bone_map(
    participant: str,
    config,
    *,
    reference_session_id: str,
    frame_start: int,
    frame_end: int,
    descriptions_dir: Path,
) -> dict[str, str]:
    desc_map = load_marker_bone_map_from_descriptions(participant, descriptions_dir)
    path = project_io.resolve_session_skeleton(config, reference_session_id)
    if path is None:
        return desc_map
    take = project_io.parse_motive_take(path)
    spatial = infer_marker_bone_map_spatial(
        take, path, frame_start=frame_start, frame_end=frame_end
    )
    return merge_marker_bone_maps(desc_map, spatial)
