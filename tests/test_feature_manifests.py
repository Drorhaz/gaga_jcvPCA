"""Validation tests for participant core feature manifests."""

from __future__ import annotations

from pathlib import Path

import pytest

from gaga_jcvpca import project_io
from gaga_jcvpca.selection import link_stem

MANIFEST_COLUMNS = [
    "feature_name",
    "canonical_link_name",
    "parent_canonical",
    "child_canonical",
    "axis",
    "source_layer2_column",
    "include_in_pilot",
    "feature_scope",
    "notes",
]
FEATURE_AXES = ("rx", "ry", "rz")

MANIFEST_DIR = Path(__file__).resolve().parents[1] / "data" / "feature_manifests"

EXPECTED = {
    "group4_core_14link_within_671_feature_manifest.csv": (14, 42),
    "group4_core_14link_within_651_feature_manifest.csv": (14, 42),
    "group4_core_16link_within_252_feature_manifest.csv": (16, 48),
    "group4_core_16link_within_790_feature_manifest.csv": (16, 48),
}


def _validate_manifest(path: Path) -> None:
    df = project_io.load_feature_manifest(path)
    missing = [col for col in MANIFEST_COLUMNS if col not in df.columns]
    assert not missing, f"{path.name} missing columns: {missing}"

    links: set[str] = set()
    for _, row in df.iterrows():
        parent = str(row["parent_canonical"])
        child = str(row["child_canonical"])
        axis = str(row["axis"])
        expected_name = f"{parent}_to_{child}_{axis}"
        assert str(row["feature_name"]) == expected_name
        assert axis in FEATURE_AXES
        links.add(link_stem(expected_name))

    n_links, n_features = EXPECTED[path.name]
    assert len(links) == n_links, path.name
    assert len(df) == n_features, path.name


@pytest.mark.parametrize("filename", sorted(EXPECTED))
def test_core_manifest_schema(filename):
    _validate_manifest(MANIFEST_DIR / filename)


def test_651_matches_671_link_set():
    m671 = project_io.load_feature_manifest(
        MANIFEST_DIR / "group4_core_14link_within_671_feature_manifest.csv"
    )
    m651 = project_io.load_feature_manifest(
        MANIFEST_DIR / "group4_core_14link_within_651_feature_manifest.csv"
    )
    links_671 = {link_stem(x) for x in project_io.feature_names_from_manifest(m671)}
    links_651 = {link_stem(x) for x in project_io.feature_names_from_manifest(m651)}
    assert links_671 == links_651


def test_790_includes_pelvis_roots():
    m790 = project_io.load_feature_manifest(
        MANIFEST_DIR / "group4_core_16link_within_790_feature_manifest.csv"
    )
    links = {link_stem(x) for x in project_io.feature_names_from_manifest(m790)}
    assert "790_to_LThigh" in links
    assert "790_to_RThigh" in links
    assert "671_to_LThigh" not in links
