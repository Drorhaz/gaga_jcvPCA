"""Tests for feature manifest discovery and generation."""

from __future__ import annotations

from pathlib import Path

import pytest

from gaga_jcvpca.config import load_config
from gaga_jcvpca.feature_manifest_gen import (
    TopologyKind,
    assess_topology,
    discover_missing_manifests,
    load_reference_hierarchies,
    parse_skeleton_hierarchy,
    resolve_manifest_path,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "data" / "feature_manifests"


@pytest.fixture(scope="module")
def config():
    return load_config()


def test_parse_651_topology_matches_671(config):
    skel = ROOT / "data/raw_skeleton/651/651_T1_P1_R1_Take 2026-01-15 04.35.25 PM_002.csv"
    if not skel.exists():
        pytest.skip("651 skeleton not present")
    h651 = parse_skeleton_hierarchy(skel)
    refs = load_reference_hierarchies(config)
    assessment = assess_topology(h651, refs)
    assert assessment.kind == TopologyKind.STYLE_671_14LINK
    assert assessment.bone_names_match_reference is True


def test_parse_790_topology_matches_252(config):
    skel = ROOT / "data/raw_skeleton/790/790_T1_P1_R1_Take 2026-04-26 06.09.29 PM_000.csv"
    if not skel.exists():
        pytest.skip("790 skeleton not present")
    h790 = parse_skeleton_hierarchy(skel)
    refs = load_reference_hierarchies(config)
    assessment = assess_topology(h790, refs)
    assert assessment.kind == TopologyKind.STYLE_252_16LINK
    assert assessment.bone_names_match_reference is True


def test_resolve_manifest_by_convention():
    path = resolve_manifest_path("651", MANIFEST_DIR)
    assert path is not None
    assert path.name == "group4_core_14link_within_651_feature_manifest.csv"


def test_discover_missing_excludes_known_participants(config):
    missing = discover_missing_manifests(config)
    pids = {r.participant for r in missing}
    assert "671" not in pids
    assert "252" not in pids
    assert "651" not in pids
    assert "790" not in pids
