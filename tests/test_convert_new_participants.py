"""Smoke conversion for newly added participants 651 and 790."""

from __future__ import annotations

from pathlib import Path

import pytest

from gaga_jcvpca import project_io
from gaga_jcvpca.config import load_config
from gaga_jcvpca.rotations import FilterSettings, build_link_map_from_bones, convert_session_take
from gaga_jcvpca.selection import link_stem

ROOT = Path(__file__).resolve().parents[1]

SMOKE_SESSIONS = {
    "651": (
        ROOT / "data/raw_skeleton/651/651_T1_P1_R1_Take 2026-01-15 04.35.25 PM_002.csv",
        ROOT
        / "data/descriptions/651_T1_P1_R1_Take 2026-01-15 04.35.25 PM_002_DataDescriptions.csv",
        "group4_core_14link_within_651_feature_manifest.csv",
        42,
    ),
    "790": (
        ROOT / "data/raw_skeleton/790/790_T1_P1_R1_Take 2026-04-26 06.09.29 PM_000.csv",
        ROOT
        / "data/descriptions/790_T1_P1_R1_Take 2026-04-26 06.09.29 PM_000_DataDescriptions.csv",
        "group4_core_16link_within_790_feature_manifest.csv",
        48,
    ),
}


@pytest.mark.parametrize("participant", sorted(SMOKE_SESSIONS))
def test_convert_session_matches_manifest(participant, tmp_path, monkeypatch):
    skeleton_path, desc_path, manifest_name, n_features = SMOKE_SESSIONS[participant]
    if not skeleton_path.exists() or not desc_path.exists():
        pytest.skip("skeleton or description file missing")

    cfg = load_config()
    manifest = project_io.load_feature_manifest(
        cfg.resolve_path("data.feature_manifests") / manifest_name
    )
    feature_names = project_io.feature_names_from_manifest(manifest)
    link_ids = sorted({link_stem(f) for f in feature_names})

    take = project_io.parse_motive_take(skeleton_path, max_frames=200)
    bones = project_io.load_skeleton_bones(desc_path)
    link_map = build_link_map_from_bones(bones)
    settings = FilterSettings.from_config(cfg)

    links = convert_session_take(
        take,
        link_map,
        settings,
        qc_thresholds=cfg.get("rotvec", {}) or {},
        link_ids=link_ids,
    )
    assert set(links.keys()) == set(link_ids)

    parts = [links[stem].to_feature_frame() for stem in link_ids if stem in links]
    matrix = __import__("pandas").concat(parts, axis=1)
    assert set(matrix.columns) == set(feature_names)
    assert matrix.shape == (200, n_features)
