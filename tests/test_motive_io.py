"""Tests for Motive skeleton CSV parsing (markers + bone quaternions)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from gaga_jcvpca import project_io

SKELETON_252_T1 = (
    Path(__file__).resolve().parents[1]
    / "data/raw_skeleton/252/T1/252_T1_P1_R1_Take 2026-04-28 04.15.00 PM_000.csv"
)


@pytest.fixture(scope="module")
def take_252_sample():
    if not SKELETON_252_T1.exists():
        pytest.skip("252 T1 skeleton CSV not present in data/")
    return project_io.parse_motive_take(SKELETON_252_T1, max_frames=500)


def test_parse_motive_take_shapes(take_252_sample):
    take = take_252_sample
    assert take.n_frames == 500
    assert take.marker_positions_m.shape == (500, len(take.marker_names), 3)
    assert take.marker_presence.shape == (500, len(take.marker_names))
    assert take.bone_quaternions.shape == (500, len(take.bone_names), 4)
    assert take.frame_rate_hz == pytest.approx(120.0)


def test_marker_positions_in_meters(take_252_sample):
    take = take_252_sample
    assert "252:LAH" in take.marker_names
    mi = take.marker_names.index("252:LAH")
    # Frame 100 in file should have finite marker data after warm-up frames.
    assert take.marker_presence[100:, mi].any()
    vals = take.marker_positions_m[100, mi]
    assert np.all(np.isfinite(vals))
    assert np.all(np.abs(vals) < 5.0)


def test_skeleton_marker_transform_millimeters():
    raw = np.array([[[167.64, 1551.96, 277.32]]])
    out = project_io.skeleton_marker_to_meters(raw, "Millimeters")
    expected = np.array([[[-0.16764, 0.27732, 1.55196]]])
    np.testing.assert_allclose(out, expected, atol=1e-5)


def test_skeleton_marker_transform_meters_identity():
    raw = np.array([[[-0.1, 0.2, 1.5]]])
    out = project_io.skeleton_marker_to_meters(raw, "Meters")
    np.testing.assert_allclose(out, raw)


def test_bone_quaternion_norms_reasonable(take_252_sample):
    take = take_252_sample
    norms = np.linalg.norm(take.bone_quaternions, axis=2)
    finite = norms[np.isfinite(norms)]
    assert finite.size > 0
    assert np.median(finite) == pytest.approx(1.0, abs=0.05)


def test_resolve_session_skeleton(config):
    path = project_io.resolve_session_skeleton(config, "252_T1_P1_R1")
    if SKELETON_252_T1.exists():
        assert path is not None
        assert path.name.startswith("252_T1_P1_R1")
    else:
        assert path is None or path.exists()
