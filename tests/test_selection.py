"""Segment/link selection + persisted analysis_selection.yaml."""

from __future__ import annotations

import numpy as np

from gaga_jcvpca import project_io, selection
from gaga_jcvpca.schemas import QCFinding, Recommendation, Severity


def _manifest(config):
    md = config.resolve_path("data.feature_manifests")
    return project_io.load_feature_manifest(md / "group4_core_14link_within_671_feature_manifest.csv")


def test_link_stem():
    assert selection.link_stem("Chest_to_Neck_rx") == "Chest_to_Neck"
    assert selection.link_stem("LThigh_to_LShin_rz") == "LThigh_to_LShin"


def test_region_of_link(config):
    assert selection.region_of_link("LShoulder_to_LUArm", config) == "left_arm"
    assert selection.region_of_link("RShin_to_RFoot", config) == "right_leg"
    assert selection.region_of_link("Neck_to_Head", config) == "head_neck"


def test_default_selection_includes_all_clean_links(config):
    sel = selection.default_selection("test_sel", "671", _manifest(config), config)
    assert len(sel.links) == 14  # 14-link manifest
    assert len(sel.included_links()) == 14
    assert len(sel.feature_columns()) == 42
    assert sel.exercise_ids == [9, 10, 11, 12, 13]  # Group4 default


def test_qc_exclude_recommendation_excludes_region(config):
    finding = QCFinding(
        resolution="link",
        scope="671_T1_P1_R1::ex09::left_arm",
        metric="marker_missing_percent",
        value=30.0,
        severity=Severity.SOFT_WARNING,
        recommendation=Recommendation.EXCLUDE,
        message="left arm badly gapped",
    )
    sel = selection.default_selection(
        "test_sel", "671", _manifest(config), config, qc_findings=[finding]
    )
    left_arm = [c for c in sel.links if c.region == "left_arm"]
    assert left_arm and all(not c.included for c in left_arm)
    # other regions still included
    assert any(c.included for c in sel.links if c.region == "right_arm")
    # excluded links carry a reason
    assert all(c.reason for c in sel.excluded_links())


def test_selection_roundtrip_yaml(config, tmp_path):
    sel = selection.default_selection("roundtrip_sel", "671", _manifest(config), config)
    path = selection.save_selection(sel, tmp_path)
    loaded = selection.load_selection(path)
    assert loaded.name == sel.name
    assert loaded.included_links() == sel.included_links()
    assert loaded.exercise_ids == sel.exercise_ids
    assert selection.list_selections(tmp_path) == [path]


def test_shared_link_intersection(config):
    md = config.resolve_path("data.feature_manifests")
    m671 = project_io.load_feature_manifest(md / "group4_core_14link_within_671_feature_manifest.csv")
    m252 = project_io.load_feature_manifest(md / "group4_core_16link_within_252_feature_manifest.csv")
    a = selection.default_selection("a", "671", m671, config)
    b = selection.default_selection("b", "252", m252, config)
    shared = selection.shared_link_intersection(a, b)
    assert shared  # non-empty
    assert set(shared).issubset(set(a.included_links()))
    assert set(shared).issubset(set(b.included_links()))
