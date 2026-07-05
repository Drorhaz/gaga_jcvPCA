"""project_io tests against the real copied data."""

from __future__ import annotations

from gaga_jcvpca import project_io
from gaga_jcvpca.naming import NamingMap


def test_find_segmentation_workbooks(config):
    wbs = project_io.find_segmentation_workbooks(config.resolve_path("data.segmentation"))
    assert set(wbs.keys()) == {"671", "252"}


def test_load_segments_exercise_id_authoritative(config):
    nm = NamingMap(config)
    wbs = project_io.find_segmentation_workbooks(config.resolve_path("data.segmentation"))
    segs = project_io.load_segments_for_workbook(wbs["252"], nm, task_part_scope="P1")
    assert segs, "expected segments for 252 P1"
    # exercise_id 1..17 present, 1-indexed, canonical labels derived
    ex_ids = sorted({s.exercise_id for s in segs})
    assert ex_ids == list(range(1, 18))
    ex09 = next(s for s in segs if s.exercise_id == 9)
    assert ex09.canonical_label == "ex09"
    assert ex09.group_id == "Group4"
    assert ex09.gaga_alias == "P1"
    assert ex09.n_frames > 0


def test_only_p1_sheets_returned(config):
    nm = NamingMap(config)
    wbs = project_io.find_segmentation_workbooks(config.resolve_path("data.segmentation"))
    segs = project_io.load_segments_for_workbook(wbs["252"], nm, task_part_scope="P1")
    assert {s.session.task_part for s in segs} == {"P1"}


def test_load_skeleton_bones_and_prefix(config):
    files = project_io.find_description_files(config.resolve_path("data.descriptions"))
    assert files
    # find a 671 T1 description
    t1 = next(f for f in files if f.name.startswith("671_T1"))
    bones = project_io.load_skeleton_bones(t1)
    assert any(b.name.endswith("_Chest") for b in bones)
    prefix = project_io.marker_set_prefix(t1)
    assert prefix == "671"


def test_feature_manifest_loads(config):
    md = config.resolve_path("data.feature_manifests")
    df = project_io.load_feature_manifest(md / "group4_core_14link_within_671_feature_manifest.csv")
    feats = project_io.feature_names_from_manifest(df)
    assert len(feats) == 42  # 14 links x 3 axes
    assert all(f.endswith(("_rx", "_ry", "_rz")) for f in feats)
