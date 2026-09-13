"""Core upgrades for the 671/252 exploration: slicing, pooling, sidecar fallback,
and NV baseline over every longitudinal comparison."""

from __future__ import annotations

import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gaga_jcvpca import jcvpca, pipeline, project_io, validation
from gaga_jcvpca.config import load_config
from gaga_jcvpca.rotations import (
    build_link_map_from_hierarchy,
    convert_session_take,
    FilterSettings,
)
from gaga_jcvpca.schemas import ExerciseSegment, SessionKey
from gaga_jcvpca.selection import default_selection, link_stem

ROOT = Path(__file__).resolve().parents[1]

FEATURES = [
    f"{stem}_{ax}"
    for stem in ["Chest_to_Neck", "Neck_to_Head", "LShoulder_to_LUArm", "RShoulder_to_RUArm"]
    for ax in ("rx", "ry", "rz")
]


def _seg(pid, ex, start, end):
    key = SessionKey(participant=pid, timepoint="T1", task_part="P1", repetition="R1")
    return ExerciseSegment(
        session=key, exercise_id=ex, canonical_label=f"ex{ex:02d}",
        exercise_name="", start_frame=start, end_frame=end,
    )


# --- 4b. slicing ---

def test_slice_selects_and_concats_windows():
    df = pd.DataFrame({"a": range(100)})
    segs = [_seg("671", 9, 10, 20), _seg("671", 10, 30, 35)]
    out = pipeline.slice_matrix_to_exercises(df, segs, [9, 10])
    assert len(out) == (20 - 10) + (35 - 30)  # 15 rows, half-open
    assert list(out["a"])[:3] == [10, 11, 12]


def test_slice_orders_by_frame_and_skips_unselected():
    df = pd.DataFrame({"a": range(100)})
    segs = [_seg("671", 10, 50, 60), _seg("671", 9, 10, 15), _seg("671", 11, 80, 90)]
    out = pipeline.slice_matrix_to_exercises(df, segs, [9, 10])
    # ex9 (10..15) comes before ex10 (50..60); ex11 excluded
    assert list(out["a"])[:5] == [10, 11, 12, 13, 14]
    assert 80 not in list(out["a"])


def test_slice_falls_back_to_full_when_no_overlap():
    df = pd.DataFrame({"a": range(50)})
    segs = [_seg("671", 9, 9000, 9100)]  # beyond matrix bounds
    out = pipeline.slice_matrix_to_exercises(df, segs, [9])
    assert len(out) == 50  # unchanged


def test_slice_noop_when_no_exercise_ids():
    df = pd.DataFrame({"a": range(50)})
    out = pipeline.slice_matrix_to_exercises(df, [], [])
    assert out is df


# --- 4a. sidecar fallback / raw-header hierarchy ---

@pytest.mark.parametrize(
    "pid,manifest,pattern",
    [
        ("252", "group4_core_16link_within_252_feature_manifest.csv", "data/raw_skeleton/252/252_T1_P1_R1*"),
        ("671", "group4_core_14link_within_671_feature_manifest.csv", "data/raw_skeleton/671/671_T3_P1_R1*"),
    ],
)
def test_raw_header_hierarchy_resolves_manifest_links(pid, manifest, pattern):
    """252 (no sidecar) and 671-T3 (confounded sidecar) both convert from the
    session's own raw-skeleton header hierarchy."""
    matches = glob.glob(str(ROOT / pattern))
    if not matches:
        pytest.skip("raw skeleton csv missing")
    cfg = load_config()
    man = project_io.load_feature_manifest(cfg.resolve_path("data.feature_manifests") / manifest)
    stems = sorted({link_stem(f) for f in project_io.feature_names_from_manifest(man)})

    take = project_io.parse_motive_take(matches[0], max_frames=150)
    hierarchy = project_io.read_skeleton_hierarchy_from_take(Path(matches[0]))
    link_map = build_link_map_from_hierarchy(hierarchy)
    links = convert_session_take(
        take, link_map, FilterSettings.from_config(cfg),
        qc_thresholds=cfg.get("rotvec", {}) or {}, link_ids=stems,
    )
    assert set(links.keys()) == set(stems)


def test_sidecar_has_bones_rejects_empty(tmp_path):
    empty = tmp_path / "empty_DataDescriptions.csv"
    empty.write_text("")
    assert project_io.sidecar_has_bones(empty) is False
    assert project_io.sidecar_has_bones(None) is False


def test_workbook_discovery_skips_excel_lock_files(tmp_path):
    (tmp_path / "252_ex_segmentatios_frames.xlsx").write_text("x")
    (tmp_path / "~$252_ex_segmentatios_frames.xlsx").write_text("lock")
    found = project_io.find_segmentation_workbooks(tmp_path)
    assert set(found) == {"252"}


# --- 4d. NV baseline over every longitudinal comparison ---

def _matrix(n=400, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame(rng.standard_normal((n, len(FEATURES))), columns=FEATURES)


def test_nv_baseline_scores_all_longitudinals(config):
    a = _matrix(seed=1)
    b2 = _matrix(seed=2)
    b3 = _matrix(seed=3)
    r2 = _matrix(seed=4)
    lon12 = jcvpca.run_comparison("671_T1_vs_T2", "longitudinal", "a", "b2", a, b2, FEATURES, 0.80)
    lon13 = jcvpca.run_comparison("671_T1_vs_T3", "longitudinal", "a", "b3", a, b3, FEATURES, 0.80)
    nv = jcvpca.run_comparison("671_T1_R1_vs_R2", "natural_variability", "a", "r2", a, r2, FEATURES, 0.80)

    report = validation.run_validation(
        config, lon12, nv, a, b2, FEATURES,
        repetition_matrices={"R1": a, "R2": r2},
        additional_longitudinals=[lon13],
    )
    df = report.to_dataframe()
    nv_rows = df[df["method"] == "natural_variability"]
    scopes = set(nv_rows["scope"])
    # both comparisons are represented, tagged by comparison id
    assert any("@671_T1_vs_T2" in s for s in scopes)
    assert any("@671_T1_vs_T3" in s for s in scopes)


# --- 4c. pooled repetition mode (end to end, synthetic) ---

def _pooled_matrices(cfg, participant="671"):
    md = cfg.resolve_path("data.feature_manifests")
    manifest = project_io.load_feature_manifest(md / "group4_core_14link_within_671_feature_manifest.csv")
    features = project_io.feature_names_from_manifest(manifest)
    stems = sorted({link_stem(f) for f in features})
    columns = [f"{s}_{ax}" for s in stems for ax in ("rx", "ry", "rz")]
    rng = np.random.default_rng(11)
    matrices = {}
    for tp in ("T1", "T2", "T3"):
        for rep in ("R1", "R2"):
            drift = {"T1": 0.0, "T2": 0.2, "T3": 0.4}[tp]
            arr = rng.standard_normal((300, len(columns)))
            arr[:, : len(columns) // 2] += drift
            matrices[f"{participant}_{tp}_P1_{rep}"] = pd.DataFrame(arr, columns=columns)
    return manifest, matrices


def test_pooled_mode_runs_and_labels_pooled_sides(config, tmp_path):
    import copy
    from gaga_jcvpca.config import Config

    data = copy.deepcopy(config.data)
    data["outputs"] = {
        "root": str(tmp_path / "outputs"),
        "runs": str(tmp_path / "outputs" / "runs"),
        "cache": str(tmp_path / "outputs" / "cache"),
    }
    cfg = Config(data=data, project_root=config.project_root)
    manifest, matrices = _pooled_matrices(cfg)
    # empty exercise_ids -> full-session (synthetic matrices have no real windows)
    selection = default_selection("671_pooled", "671", manifest, cfg, exercise_ids=[])

    run_dir = pipeline.run_analysis(
        cfg, selection, timepoints=["T1", "T2", "T3"], repetitions=["R1", "R2"],
        reference_timepoint="T1", repetition_mode="pooled",
        run_validation=True, run_id="pooled_run", matrices=matrices,
    )
    manifest_json = json.loads((run_dir / "reproducibility_manifest.json").read_text())
    by_id = {c["comparison_id"]: c for c in manifest_json["comparisons"]}
    assert "671_T1_vs_T2" in by_id and "671_T1_vs_T3" in by_id
    # pooled sides carry the R1+R2 label
    assert by_id["671_T1_vs_T2"]["a_label"] == "671_T1_R1+R2"
    assert by_id["671_T1_vs_T2"]["b_label"] == "671_T2_R1+R2"
    # NV stays single-rep within reference timepoint
    assert by_id["671_T1_R1_vs_R2"]["kind"] == "natural_variability"
