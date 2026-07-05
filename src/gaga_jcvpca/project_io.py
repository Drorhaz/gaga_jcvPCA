"""Input/output helpers.

Reads the standalone project's own data (segmentation workbooks, DataDescriptions
sidecars, feature manifests, raw Motive CSV headers) and writes run outputs. This
module never repairs, fills, or interpolates data; it only reads and organizes it.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional, TYPE_CHECKING

import numpy as np
import pandas as pd

from gaga_jcvpca.naming import NamingMap, canonical_label, parse_session_id, parse_sheet_name

if TYPE_CHECKING:
    from gaga_jcvpca.config import Config
from gaga_jcvpca.schemas import ExerciseSegment, SessionKey

SEGMENTATION_GLOB = "*_ex_segmentatios_frames.xlsx"
DESCRIPTION_SUFFIX = "_DataDescriptions.csv"
AXIS_SUFFIXES = ("_rx", "_ry", "_rz")

# Segmentation workbooks are hand-authored and their column layout varies between
# sheets (e.g. 'end_frame' vs 'end_frame_exclusive', duplicated annotation blocks).
# We resolve the end-frame column tolerantly and record when a non-standard layout
# was used so the inventory can surface it.
_END_FRAME_CANDIDATES = ("end_frame", "end_frame_exclusive")
_START_FRAME_CANDIDATES = ("start_frame",)


def _resolve_column(columns, candidates) -> str | None:
    for cand in candidates:
        if cand in columns:
            return cand
    return None


def _as_int(value) -> int | None:
    """Best-effort int; returns None for NaN / blank / non-numeric annotations."""
    if pd.isna(value):
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


# --- segmentation workbooks ---

def find_segmentation_workbooks(segmentation_dir: Path) -> dict[str, Path]:
    """Map participant id -> segmentation workbook path."""
    out: dict[str, Path] = {}
    if not segmentation_dir.exists():
        return out
    for path in sorted(segmentation_dir.glob(SEGMENTATION_GLOB)):
        pid = path.name.split("_", 1)[0]
        out[pid] = path
    return out


def load_segments_for_workbook(
    path: Path,
    naming: NamingMap,
    task_part_scope: Optional[str] = "P1",
) -> list[ExerciseSegment]:
    """Read every sheet of a segmentation workbook into ExerciseSegment rows.

    ``exercise_id`` is authoritative. If ``task_part_scope`` is given, only sheets
    whose task part matches are returned (V1 = P1).
    """
    xls = pd.ExcelFile(path)
    segments: list[ExerciseSegment] = []
    for sheet in xls.sheet_names:
        key = parse_sheet_name(sheet)
        if key is None:
            continue
        if task_part_scope is not None and key.task_part != task_part_scope:
            continue
        df = xls.parse(sheet)
        start_col = _resolve_column(df.columns, _START_FRAME_CANDIDATES)
        end_col = _resolve_column(df.columns, _END_FRAME_CANDIDATES)
        if "exercise_id" not in df.columns or start_col is None or end_col is None:
            continue
        name_col = "exercise_name" if "exercise_name" in df.columns else None
        for _, row in df.iterrows():
            ex_id_v = _as_int(row["exercise_id"])
            start_v = _as_int(row[start_col])
            end_v = _as_int(row[end_col])
            if ex_id_v is None or start_v is None or end_v is None:
                continue  # blank / non-numeric annotation rows are skipped
            ex_id = ex_id_v
            ex_name = str(row[name_col]) if name_col else ""
            segments.append(
                ExerciseSegment(
                    session=key,
                    exercise_id=ex_id,
                    canonical_label=canonical_label(ex_id),
                    exercise_name=ex_name,
                    start_frame=start_v,
                    end_frame=end_v,
                    group_id=naming.group_of(ex_id),
                    gaga_alias=naming.gaga_alias_of(ex_id),
                )
            )
    return segments


def segmentation_sheet_names(path: Path) -> list[str]:
    """Return raw sheet names of a workbook (for naming checks)."""
    return list(pd.ExcelFile(path).sheet_names)


# --- DataDescriptions sidecars ---

@dataclass(frozen=True)
class SkeletonBone:
    name: str          # e.g. "671_LUArm"
    index: int
    parent_index: int


def find_description_files(descriptions_dir: Path) -> list[Path]:
    if not descriptions_dir.exists():
        return []
    return sorted(descriptions_dir.glob(f"*{DESCRIPTION_SUFFIX}"))


def load_skeleton_bones(path: Path) -> list[SkeletonBone]:
    """Parse the bone hierarchy from a Motive DataDescriptions CSV.

    Rows begin with a type token; ``Bone`` rows carry name, index, parent index.
    """
    bones: list[SkeletonBone] = []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for parts in csv.reader(fh):
            if not parts or parts[0] != "Bone":
                continue
            # Bone,<name>,<index>,<parent_index>,<offsets...>,<skeleton>
            try:
                bones.append(
                    SkeletonBone(
                        name=parts[1],
                        index=int(parts[2]),
                        parent_index=int(parts[3]),
                    )
                )
            except (ValueError, IndexError):
                continue
    return bones


def marker_set_prefix(path: Path) -> Optional[str]:
    """Infer the marker/asset prefix (e.g. '671' vs 'T3_671') from a description.

    Used for the cross-timepoint marker-set comparability check (671 T3 confound).
    """
    for bone in load_skeleton_bones(path):
        # Bone names look like "<prefix>_<segment>"; the skeleton token is the prefix.
        if "_" in bone.name:
            return bone.name.split("_", 1)[0]
    return None


# --- feature manifests ---

def load_feature_manifest(path: Path) -> pd.DataFrame:
    """Load a per-participant feature manifest (link -> rx/ry/rz feature columns)."""
    return pd.read_csv(path)


def feature_names_from_manifest(df: pd.DataFrame) -> list[str]:
    """Ordered feature column names from a manifest (rx/ry/rz)."""
    if "feature_name" in df.columns:
        return [str(x) for x in df["feature_name"].tolist()]
    return [c for c in df.columns if str(c).endswith(AXIS_SUFFIXES)]


# --- raw Motive CSV headers (cheap, no full load) ---

def raw_csv_type(path: Path) -> Optional[str]:
    """Return the Motive export type token ('Marker' / 'Bone') from the header."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for line in fh:
                cells = line.split(",")
                for cell in cells:
                    token = cell.strip()
                    if token in ("Marker", "Bone"):
                        return token
                # only inspect the first few header lines
                if fh.tell() > 20000:
                    break
    except OSError:
        return None
    return None


def iter_matrix_columns(path: Path) -> Iterator[str]:
    """Yield column names of a parquet/csv matrix without loading all rows."""
    if path.suffix.lower() == ".parquet":
        import pyarrow.parquet as pq

        for name in pq.ParquetFile(path).schema.names:
            yield name
    else:
        yield from pd.read_csv(path, nrows=0).columns


# --- Motive solved-skeleton CSV (markers + bone quaternions in one file) ---

_MARKER_AXIS = ("X", "Y", "Z")
_BONE_AXIS = ("X", "Y", "Z", "W")


@dataclass
class MotiveTake:
    """Parsed Motive export: marker QC data and bone quaternions from one CSV."""

    path: Path
    meta: dict[str, str]
    n_frames: int
    frame_rate_hz: float
    marker_names: list[str]
    marker_positions_m: np.ndarray  # (n_frames, n_markers, 3)
    marker_presence: np.ndarray  # (n_frames, n_markers)
    bone_names: list[str]
    bone_quaternions: np.ndarray  # (n_frames, n_bones, 4) SciPy [x,y,z,w]


def parse_motive_meta(row0: list[str]) -> dict[str, str]:
    meta: dict[str, str] = {}
    for i in range(0, len(row0) - 1, 2):
        key = row0[i].strip()
        if key:
            meta[key] = row0[i + 1]
    return meta


def _read_motive_header_rows(path: Path, max_rows: int = 12) -> list[list[str]]:
    rows: list[list[str]] = []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            rows.append(next(csv.reader([line])))
            if i >= max_rows:
                break
    return rows


def _find_type_row(rows: list[list[str]]) -> int:
    for i, row in enumerate(rows):
        if len(row) > 1 and row[1].strip() == "Type":
            return i
    raise ValueError("Could not find Motive 'Type' header row")


def _find_frame_row(rows: list[list[str]]) -> int:
    for i, row in enumerate(rows):
        if row and row[0].strip() == "Frame":
            return i
    raise ValueError("Could not find Motive 'Frame' header row")


def _group_axis_columns(
    type_row: list[str],
    name_row: list[str],
    frame_row: list[str],
    channel_type: str,
    axis_labels: tuple[str, ...],
) -> tuple[list[str], list[list[int]]]:
    """Group columns by channel name; map axes using the Frame header row."""
    order: list[str] = []
    cols_by_name: dict[str, list[tuple[int, str]]] = {}
    for i, token in enumerate(type_row):
        if token.strip() != channel_type:
            continue
        name = name_row[i] if i < len(name_row) else f"col{i}"
        if name not in cols_by_name:
            order.append(name)
            cols_by_name[name] = []
        axis = frame_row[i].strip() if i < len(frame_row) else ""
        cols_by_name[name].append((i, axis))

    indices: list[list[int]] = []
    for name in order:
        pairs = cols_by_name[name]
        ordered: list[int] = []
        for axis in axis_labels:
            for col, ax in pairs:
                if ax == axis:
                    ordered.append(col)
                    break
        if len(ordered) < len(axis_labels):
            ordered = [col for col, _ in pairs[: len(axis_labels)]]
        indices.append(ordered)
    return order, indices


def skeleton_marker_to_meters(positions: np.ndarray, length_units: str) -> np.ndarray:
    """Convert skeleton Marker columns to marker-export meter coordinates."""
    units = (length_units or "").strip().lower()
    if units.startswith("millimeter"):
        scaled = positions / 1000.0
        out = np.empty_like(scaled)
        out[..., 0] = -scaled[..., 0]
        out[..., 1] = scaled[..., 2]
        out[..., 2] = scaled[..., 1]
        return out
    return positions


def parse_motive_take(path: str | Path, max_frames: Optional[int] = None) -> MotiveTake:
    """Parse marker and bone-quaternion channels from a Motive skeleton CSV."""
    path = Path(path)
    rows = _read_motive_header_rows(path)
    meta = parse_motive_meta(rows[0])
    type_row_idx = _find_type_row(rows)
    frame_row_idx = _find_frame_row(rows)
    type_row = rows[type_row_idx]
    name_row = rows[type_row_idx + 1]
    frame_row = rows[frame_row_idx]

    marker_names, marker_cols = _group_axis_columns(
        type_row, name_row, frame_row, "Marker", _MARKER_AXIS
    )
    bone_names, bone_cols = _group_axis_columns(
        type_row, name_row, frame_row, "Bone", _BONE_AXIS
    )

    usecols = sorted(
        {c for group in marker_cols + bone_cols for c in group}
    )
    if not usecols:
        raise ValueError(f"No Marker or Bone columns found in {path}")

    colmap = {col: ui for ui, col in enumerate(usecols)}
    df = pd.read_csv(
        path,
        skiprows=frame_row_idx + 1,
        header=None,
        usecols=usecols,
        nrows=max_frames,
        low_memory=False,
    )
    n_frames = len(df)

    marker_raw = np.full((n_frames, len(marker_names), 3), np.nan, dtype=float)
    marker_presence = np.zeros((n_frames, len(marker_names)), dtype=bool)
    for mi, cols in enumerate(marker_cols):
        for ai, col in enumerate(cols):
            marker_raw[:, mi, ai] = pd.to_numeric(
                df.iloc[:, colmap[col]], errors="coerce"
            )
        marker_presence[:, mi] = np.all(np.isfinite(marker_raw[:, mi, :]), axis=1)

    marker_positions_m = skeleton_marker_to_meters(
        marker_raw, meta.get("Length Units", "")
    )

    bone_quaternions = np.full((n_frames, len(bone_names), 4), np.nan, dtype=float)
    for bi, cols in enumerate(bone_cols):
        for ai, col in enumerate(cols):
            bone_quaternions[:, bi, ai] = pd.to_numeric(
                df.iloc[:, colmap[col]], errors="coerce"
            )

    frame_rate = float(meta.get("Export Frame Rate", meta.get("Capture Frame Rate", 120.0)))

    return MotiveTake(
        path=path,
        meta=meta,
        n_frames=n_frames,
        frame_rate_hz=frame_rate,
        marker_names=marker_names,
        marker_positions_m=marker_positions_m,
        marker_presence=marker_presence,
        bone_names=bone_names,
        bone_quaternions=bone_quaternions,
    )


def _resolve_session_csv_in_dir(dir_path: Path, session_id: str) -> Optional[Path]:
    """Return the first matching Motive CSV for a session id under ``dir_path``."""
    if not dir_path or not dir_path.exists():
        return None
    for path in dir_path.rglob("*.csv"):
        if path.stat().st_size == 0 or "DataDescriptions" in path.name:
            continue
        key = parse_session_id(path.name)
        if key is not None and key.as_str() == session_id:
            return path
    return None


def resolve_session_marker_csv(config: "Config", session_id: str) -> Optional[Path]:
    """Return the marker CSV path for a session (dedicated export or skeleton fallback)."""
    try:
        marker_dir = config.resolve_path("data.raw_markers")
    except KeyError:
        marker_dir = None
    if marker_dir is not None:
        found = _resolve_session_csv_in_dir(marker_dir, session_id)
        if found is not None:
            return found

    skel = resolve_session_skeleton(config, session_id)
    if skel is not None and raw_csv_type(skel) in (None, "Marker", "Bone"):
        # Skeleton exports embed Type=Marker columns alongside bones.
        return skel
    return None


def resolve_session_skeleton(config: "Config", session_id: str) -> Optional[Path]:
    """Return the raw skeleton CSV path for a canonical session id, if present."""
    try:
        skeleton_dir = config.resolve_path("data.raw_skeleton")
    except KeyError:
        return None
    return _resolve_session_csv_in_dir(skeleton_dir, session_id)
