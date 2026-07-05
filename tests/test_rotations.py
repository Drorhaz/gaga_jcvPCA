"""Rotation-vector conversion: faithfulness + flags + filter controls."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from gaga_jcvpca import rotations as rot

# Path to the original validated Layer 2 implementation, for numeric parity.
_ORIG_SRC = Path("/Users/drorhazan/Desktop/gaga_psilo/projects/3Layers_project/Layer2_Motive_Kinematics/src")


def _random_unit_quats(n, seed=0):
    rng = np.random.default_rng(seed)
    q = rng.normal(size=(n, 4))
    return q / np.linalg.norm(q, axis=1, keepdims=True)


def test_rotvec_matches_scipy():
    q = _random_unit_quats(50, seed=1)
    got = rot.quat_rows_to_rotvec(q)
    expected = Rotation.from_quat(q).as_rotvec()
    np.testing.assert_allclose(got, expected, rtol=1e-12, atol=1e-12)


def test_relative_reconstruction_roundtrip():
    parent = _random_unit_quats(30, seed=2)
    child = _random_unit_quats(30, seed=3)
    rel = rot.compute_relative_quaternions(parent, child)
    # parent * rel should reconstruct child (up to double cover)
    recon = (Rotation.from_quat(parent) * Rotation.from_quat(rel)).as_quat()
    ang = (Rotation.from_quat(child).inv() * Rotation.from_quat(recon)).magnitude()
    np.testing.assert_allclose(ang, 0.0, atol=1e-9)


@pytest.mark.skipif(not _ORIG_SRC.exists(), reason="original Layer 2 source not present")
def test_parity_with_original_layer2():
    import sys

    if str(_ORIG_SRC) not in sys.path:
        sys.path.insert(0, str(_ORIG_SRC))
    from layer2_motive import rotvec as orig_rotvec
    from layer2_motive import relative_rotation as orig_rel
    from layer2_motive import quaternion_continuity as orig_sign

    parent = _random_unit_quats(40, seed=4)
    child = _random_unit_quats(40, seed=5)

    np.testing.assert_allclose(
        rot.quat_rows_to_rotvec(parent), orig_rotvec.quat_rows_to_rotvec(parent), atol=1e-12
    )
    np.testing.assert_allclose(
        rot.compute_relative_quaternions(parent, child),
        orig_rel.compute_relative_quaternions(parent, child),
        atol=1e-12,
    )
    corrected_new, _ = rot.apply_sign_continuity(parent.copy())
    corrected_old, _ = orig_sign.apply_sign_continuity(parent.copy())
    np.testing.assert_allclose(corrected_new, corrected_old, atol=1e-12)


def test_sign_continuity_removes_flips():
    q = _random_unit_quats(20, seed=6)
    q[5] = -q[5]  # inject a flip
    corrected, flip = rot.apply_sign_continuity(q)
    dots = np.sum(corrected[1:] * corrected[:-1], axis=1)
    assert np.all(dots >= -1e-9)


def test_butterworth_is_zero_phase_and_smooths():
    fr = 120.0
    t = np.arange(0, 5, 1 / fr)
    clean = np.sin(2 * np.pi * 1.0 * t)  # 1 Hz
    noise = 0.3 * np.sin(2 * np.pi * 40.0 * t)  # 40 Hz noise
    comp = np.stack([clean + noise, clean, clean], axis=1)
    sos = rot.design_butterworth_sos(10.0, fr, 4)
    filtered, applied = rot.filter_rotvec_components(comp, sos)
    assert applied.all()
    # filtered rx should be closer to the clean 1 Hz signal than the noisy input
    err_before = np.mean((comp[:, 0] - clean) ** 2)
    err_after = np.mean((filtered[:, 0] - clean) ** 2)
    assert err_after < err_before


def test_convert_link_flags_missing_and_jumps():
    n = 400
    parent = _random_unit_quats(n, seed=7)
    # child mostly smooth, but insert a large jump at frame 200
    child = _random_unit_quats(n, seed=8)
    settings = rot.FilterSettings(cutoff_hz=10.0, order=4, frame_rate_hz=120.0)
    present = np.ones(n, dtype=bool)
    present[100:110] = False  # missing markers
    qc = {"jump_fail_rad": 1.0, "near_pi_warning_fraction": 0.95}
    link = rot.convert_link("Chest_to_Neck", parent, child, settings, present_mask=present, qc_thresholds=qc)
    ff = link.frame_flags
    assert ff["frame_flag_missing_marker"].sum() == 10
    assert set(link.to_feature_frame().columns) == {
        "Chest_to_Neck_rx",
        "Chest_to_Neck_ry",
        "Chest_to_Neck_rz",
    }
    assert link.link_flags["n_frames"] == n


def test_invalid_quaternion_flagged_not_fatal():
    n = 60
    parent = _random_unit_quats(n, seed=9)
    child = _random_unit_quats(n, seed=10)
    child[10] = [0.0, 0.0, 0.0, 0.0]  # invalid (zero) quaternion
    settings = rot.FilterSettings(frame_rate_hz=120.0)
    link = rot.convert_link("Chest_to_Neck", parent, child, settings)
    assert bool(link.frame_flags["frame_flag_quaternion_invalid"].iloc[10])
    # pipeline did not raise; result exists
    assert len(link.rx) == n


def test_filter_cache_key_changes_with_settings():
    a = rot.FilterSettings(cutoff_hz=10.0)
    b = rot.FilterSettings(cutoff_hz=6.0)
    assert a.cache_key() != b.cache_key()
    assert a.cache_key() == rot.FilterSettings(cutoff_hz=10.0).cache_key()


def test_build_link_map_from_bones():
    from gaga_jcvpca.project_io import SkeletonBone

    bones = [
        SkeletonBone("671_671", 1, 0),
        SkeletonBone("671_Chest", 3, 2),
        SkeletonBone("671_Neck", 4, 3),
    ]
    links = rot.build_link_map_from_bones(bones)
    assert "Neck_to_Head" not in links
    assert ("671_Chest", "671_Neck") == links["Chest_to_Neck"]


def test_convert_session_take_synthetic():
    from gaga_jcvpca.project_io import MotiveTake

    n = 80
    parent = _random_unit_quats(n, seed=11)
    child = _random_unit_quats(n, seed=12)
    take = MotiveTake(
        path=Path("synthetic.csv"),
        meta={"Length Units": "Meters"},
        n_frames=n,
        frame_rate_hz=120.0,
        marker_names=[],
        marker_positions_m=np.zeros((n, 0, 3)),
        marker_presence=np.zeros((n, 0), dtype=bool),
        bone_names=["671_Chest", "671_Neck"],
        bone_quaternions=np.stack([parent, child], axis=1),
    )
    link_map = {"Chest_to_Neck": ("671_Chest", "671_Neck")}
    settings = rot.FilterSettings(frame_rate_hz=120.0)
    out = rot.convert_session_take(take, link_map, settings)
    assert "Chest_to_Neck" in out
    assert len(out["Chest_to_Neck"].rx) == n
