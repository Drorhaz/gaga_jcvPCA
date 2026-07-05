"""Quaternion -> rotation-vector conversion (ported, byte-faithful math).

Ported faithfully from the validated Layer 2 pipeline (Stages 06-08):
  * relative link quaternion   q_rel = inv(q_parent) * q_child   (SciPy composition)
  * sign-continuity correction along time
  * SO(3) log-map to rotation vectors  (Rotation.from_quat([x,y,z,w]).as_rotvec())
  * Butterworth low-pass in the tangent space (zero-phase sosfiltfilt)

Adds processing flags (frame/link/segment) and an include/exclude recommendation
without stopping the pipeline unless the issue is fatal. Filter settings feed a
cache key so changing them forces recomputation (decision 5).

No z-scoring, no normalization of features — only what the validated pipeline does.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt
from scipy.spatial.transform import Rotation

PI = float(np.pi)
AXIS_SUFFIXES = ("_rx", "_ry", "_rz")


# --- filter settings + cache key ---

@dataclass(frozen=True)
class FilterSettings:
    cutoff_hz: float = 10.0
    order: int = 4
    filter_type: str = "butterworth_lowpass"
    jump_context_window_frames: int = 30
    frame_rate_hz: float = 120.0

    @classmethod
    def from_config(cls, config) -> "FilterSettings":
        return cls(
            cutoff_hz=float(config.get("filter.cutoff_hz", 10.0)),
            order=int(config.get("filter.order", 4)),
            filter_type=str(config.get("filter.filter_type", "butterworth_lowpass")),
            jump_context_window_frames=int(config.get("filter.jump_context_window_frames", 30)),
            frame_rate_hz=float(config.get("capture.frame_rate_hz", 120.0)),
        )

    def cache_key(self) -> str:
        blob = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


# --- ported core math ---

def quat_rows_to_rotvec(quats: np.ndarray) -> np.ndarray:
    """Convert SciPy-order quaternion rows [x,y,z,w] to rotation vectors."""
    return Rotation.from_quat(np.asarray(quats, dtype=float).copy()).as_rotvec()


def compute_relative_quaternions(parent_quats: np.ndarray, child_quats: np.ndarray) -> np.ndarray:
    """q_rel = inv(q_parent) * q_child for aligned (n, 4) SciPy-order arrays."""
    parent_quats = np.asarray(parent_quats, dtype=float)
    child_quats = np.asarray(child_quats, dtype=float)
    if parent_quats.shape != child_quats.shape or parent_quats.ndim != 2 or parent_quats.shape[1] != 4:
        raise ValueError("parent_quats and child_quats must both have shape (n, 4)")
    r_parent = Rotation.from_quat(parent_quats)
    r_child = Rotation.from_quat(child_quats)
    return (r_parent.inv() * r_child).as_quat()


def apply_sign_continuity(quats: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Correct quaternion sign flips along time; returns corrected quats and flip mask."""
    quats = np.asarray(quats, dtype=float)
    if quats.ndim != 2 or quats.shape[1] != 4:
        raise ValueError("quats must have shape (n, 4)")
    corrected = quats.copy()
    flip_mask = np.zeros(len(quats), dtype=bool)
    for i in range(1, len(quats)):
        if float(np.dot(corrected[i], corrected[i - 1])) < 0.0:
            corrected[i] = -corrected[i]
            flip_mask[i] = True
    return corrected, flip_mask


def frame_to_frame_rotvec_jumps(rotvecs: np.ndarray) -> np.ndarray:
    """Euclidean norm of consecutive rotation-vector differences (length n-1)."""
    rotvecs = np.asarray(rotvecs, dtype=float)
    if len(rotvecs) < 2:
        return np.array([], dtype=float)
    return np.linalg.norm(np.diff(rotvecs, axis=0), axis=1)


def design_butterworth_sos(cutoff_hz: float, sampling_rate_hz: float, order: int) -> np.ndarray:
    wn = cutoff_hz / (sampling_rate_hz / 2.0)
    return np.asarray(butter(order, wn, btype="low", output="sos"), dtype=float)


def _min_filtfilt_length(sos: np.ndarray) -> int:
    # Mirror scipy.signal.sosfiltfilt's default padlen so short segments are
    # skipped rather than crashing: padlen = 3 * ntaps, where
    # ntaps = 2*n_sections + 1 - min(#(b2==0), #(a2==0)).
    n_sections = sos.shape[0]
    ntaps = 2 * n_sections + 1
    ntaps -= min((sos[:, 2] == 0).sum(), (sos[:, 5] == 0).sum())
    return 3 * int(ntaps) + 1


def filter_rotvec_components(components: np.ndarray, sos: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Zero-phase Butterworth on rx/ry/rz; returns filtered array + per-row applied mask.

    Only contiguous finite segments long enough for sosfiltfilt are filtered; other
    rows are left NaN (never fed NaNs). Faithful to the Layer 2 Stage 08 behaviour.
    """
    components = np.asarray(components, dtype=float)
    if components.ndim != 2 or components.shape[1] != 3:
        raise ValueError("components must have shape (n_frames, 3)")
    row_finite = np.all(np.isfinite(components), axis=1)
    out = np.full_like(components, np.nan)
    applied = np.zeros(len(components), dtype=bool)
    min_len = _min_filtfilt_length(sos)

    # contiguous finite segments
    start = None
    for idx in range(len(row_finite) + 1):
        val = row_finite[idx] if idx < len(row_finite) else False
        if val and start is None:
            start = idx
        elif not val and start is not None:
            seg = components[start:idx]
            if seg.shape[0] >= min_len:
                for axis in range(3):
                    out[start:idx, axis] = sosfiltfilt(sos, seg[:, axis])
                applied[start:idx] = True
            start = None
    return out, applied


# --- flags + result container ---

@dataclass
class LinkRotvec:
    """Filtered rotation-vector time series for one parent-child link."""

    link_id: str            # canonical stem, e.g. "Chest_to_Neck"
    rx: np.ndarray
    ry: np.ndarray
    rz: np.ndarray
    frame_flags: pd.DataFrame  # per-frame boolean flags
    link_flags: dict = field(default_factory=dict)

    def to_feature_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            {f"{self.link_id}_rx": self.rx, f"{self.link_id}_ry": self.ry, f"{self.link_id}_rz": self.rz}
        )


def convert_link(
    link_id: str,
    parent_quats: np.ndarray,
    child_quats: np.ndarray,
    settings: FilterSettings,
    present_mask: Optional[np.ndarray] = None,
    qc_thresholds: Optional[dict] = None,
) -> LinkRotvec:
    """Full per-link conversion: relative quat -> sign continuity -> rotvec -> filter,
    with frame/link processing flags. Never raises on soft issues.
    """
    n = len(parent_quats)
    thr = qc_thresholds or {}
    jump_fail = float(thr.get("jump_fail_rad", 1.0))
    near_pi_fraction = float(thr.get("near_pi_warning_fraction", 0.95))

    # quaternion validity (norm ~ 1)
    q_norms_parent = np.linalg.norm(parent_quats, axis=1)
    q_norms_child = np.linalg.norm(child_quats, axis=1)
    quat_invalid = (~np.isfinite(q_norms_parent)) | (~np.isfinite(q_norms_child)) | (q_norms_parent < 1e-6) | (q_norms_child < 1e-6)

    rel = compute_relative_quaternions(
        np.nan_to_num(parent_quats, nan=0.0) + np.where(quat_invalid[:, None], [0, 0, 0, 1.0], 0.0),
        np.nan_to_num(child_quats, nan=0.0) + np.where(quat_invalid[:, None], [0, 0, 0, 1.0], 0.0),
    )
    rel, _flip = apply_sign_continuity(rel)
    rotvec = quat_rows_to_rotvec(rel)  # (n, 3) raw
    # invalidate frames with bad quaternions
    rotvec[quat_invalid] = np.nan

    rotvec_norm = np.linalg.norm(rotvec, axis=1)
    jumps = frame_to_frame_rotvec_jumps(rotvec)
    jump_flag = np.zeros(n, dtype=bool)
    if jumps.size:
        jump_flag[1:] = jumps > jump_fail
    near_pi_flag = np.isfinite(rotvec_norm) & (rotvec_norm > near_pi_fraction * PI)

    missing_flag = ~present_mask if present_mask is not None else np.zeros(n, dtype=bool)

    # Butterworth low-pass in tangent (rotvec) space
    sos = design_butterworth_sos(settings.cutoff_hz, settings.frame_rate_hz, settings.order)
    filtered, applied = filter_rotvec_components(rotvec, sos)

    frame_flags = pd.DataFrame(
        {
            "frame_flag_missing_marker": missing_flag,
            "frame_flag_quaternion_invalid": quat_invalid,
            "frame_flag_rotation_jump": jump_flag,
            "frame_flag_near_pi_branch_cut": near_pi_flag,
            "filter_applied": applied,
        }
    )
    link_flags = {
        "link_flag_low_confidence": bool(missing_flag.mean() > 0.10 or quat_invalid.mean() > 0.05),
        "n_frames": int(n),
        "n_filtered": int(applied.sum()),
        "n_jump_frames": int(jump_flag.sum()),
    }
    return LinkRotvec(
        link_id=link_id,
        rx=filtered[:, 0],
        ry=filtered[:, 1],
        rz=filtered[:, 2],
        frame_flags=frame_flags,
        link_flags=link_flags,
    )


def build_link_map_from_bones(bones) -> dict[str, tuple[str, str]]:
    """From DataDescriptions bones, build canonical link_id -> (parent_name, child_name).

    Canonical link stem strips the participant prefix, e.g.
    ('671_Chest','671_Neck') -> 'Chest_to_Neck'.
    """
    by_index = {b.index: b for b in bones}
    links: dict[str, tuple[str, str]] = {}
    for b in bones:
        parent = by_index.get(b.parent_index)
        if parent is None or parent.index == b.index:
            continue
        child_short = b.name.split("_", 1)[1] if "_" in b.name else b.name
        parent_short = parent.name.split("_", 1)[1] if "_" in parent.name else parent.name
        links[f"{parent_short}_to_{child_short}"] = (parent.name, b.name)
    return links


# Manifest canonical stems that may appear under alternate session-native names.
CANONICAL_LINK_ALIASES: dict[str, tuple[str, ...]] = {
    "Neck_to_Head": ("Neck2_to_Head",),
}


def resolve_link_pair(
    link_id: str, link_map: dict[str, tuple[str, str]]
) -> tuple[str, str] | None:
    """Return parent/child bone names for a manifest link stem, honoring aliases."""
    if link_id in link_map:
        return link_map[link_id]
    for alt in CANONICAL_LINK_ALIASES.get(link_id, ()):
        if alt in link_map:
            return link_map[alt]
    return None


def convert_session_take(
    take,
    link_map: dict[str, tuple[str, str]],
    settings: FilterSettings,
    qc_thresholds: Optional[dict] = None,
    link_ids: Optional[list[str]] = None,
) -> dict[str, LinkRotvec]:
    """Convert all requested links from a parsed MotiveTake."""
    bone_idx: dict[str, int] = {}
    for i, name in enumerate(take.bone_names):
        bone_idx[name] = i
        if ":" in name:
            bone_idx.setdefault(name.replace(":", "_", 1), i)
        elif "_" in name:
            bone_idx.setdefault(name.replace("_", ":", 1), i)
    targets = link_ids if link_ids is not None else sorted(link_map.keys())
    out: dict[str, LinkRotvec] = {}
    for link_id in targets:
        pair = resolve_link_pair(link_id, link_map)
        if pair is None:
            continue
        parent_name, child_name = pair
        if parent_name not in bone_idx or child_name not in bone_idx:
            continue
        pi, ci = bone_idx[parent_name], bone_idx[child_name]
        out[link_id] = convert_link(
            link_id,
            take.bone_quaternions[:, pi, :],
            take.bone_quaternions[:, ci, :],
            settings,
            present_mask=None,
            qc_thresholds=qc_thresholds,
        )
    return out
