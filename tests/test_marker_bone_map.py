"""Tests for marker → bone → link mapping."""

from __future__ import annotations

import pytest

from gaga_jcvpca import project_io
from gaga_jcvpca.config import load_config
from gaga_jcvpca.marker_bone_map import (
    build_participant_marker_bone_map,
    infer_marker_bone_map_spatial,
    links_for_bone_token,
    related_links_for_marker,
)
from gaga_jcvpca.qc_markers import load_link_specs_for_participant


@pytest.fixture
def config(project_root):
    return load_config()


def test_links_for_bone_token_luarm():
    specs = [("LUArm_to_LFArm", "LUArm", "LFArm"), ("LShoulder_to_LUArm", "LShoulder", "LUArm")]
    assert links_for_bone_token("LUArm", specs) == ["LShoulder_to_LUArm", "LUArm_to_LFArm"]


@pytest.mark.slow
def test_spatial_marker_bone_map_252(config, project_root):
    skel = project_root / "data/raw_skeleton/252/252_T1_P1_R1_Take 2026-04-28 04.15.00 PM_000.csv"
    if not skel.exists():
        pytest.skip("252 skeleton CSV not present")
    take = project_io.parse_motive_take(skel)
    # ex09-13 contiguous window for this take (matches gap-table builder)
    mapping = infer_marker_bone_map_spatial(take, skel, frame_start=15120, frame_end=21720)
    assert mapping.get("LUA") == "LUArm"
    assert mapping.get("RUA") in {"RUArm", "RFArm"}
    assert mapping.get("LFTC") == "LThigh"


@pytest.mark.slow
def test_build_participant_marker_bone_map_252_links_in_gap_table(config, project_root):
    skel = project_root / "data/raw_skeleton/252/252_T1_P1_R1_Take 2026-04-28 04.15.00 PM_000.csv"
    if not skel.exists():
        pytest.skip("252 skeleton CSV not present")
    desc_dir = project_root / "data/descriptions"
    mapping = build_participant_marker_bone_map(
        "252",
        config,
        reference_session_id="252_T1_P1_R1",
        frame_start=15120,
        frame_end=21720,
        descriptions_dir=desc_dir,
    )
    link_specs = load_link_specs_for_participant(config, "252")
    rel = related_links_for_marker("252:LUA", link_specs, mapping)
    assert "LUArm_to_LFArm" in rel
    assert "LShoulder_to_LUArm" in rel
