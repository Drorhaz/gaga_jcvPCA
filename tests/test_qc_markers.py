"""Raw-marker QC logic (synthetic data so behaviour is deterministic)."""

from __future__ import annotations

import numpy as np
import pytest
from pathlib import Path

from gaga_jcvpca import qc_markers as qc
from gaga_jcvpca.schemas import Recommendation, Severity


@pytest.fixture()
def thresholds(config):
    return config.data


def _md(presence, names, fr=120.0, positions=None):
    return qc.MarkerData(marker_names=names, presence=presence, frame_rate_hz=fr, positions=positions)


def test_region_of_marker():
    assert qc.region_of_marker("LElbowOut") == "left_arm"
    assert qc.region_of_marker("RThighFront") == "right_leg"
    assert qc.region_of_marker("ChestTop") == "trunk_spine"
    assert qc.region_of_marker("HeadTop") == "head_neck"


def test_detect_gaps_contiguous():
    # 1 marker, missing frames 2..4 (inclusive)
    presence = np.array([[True], [True], [False], [False], [False], [True]])
    gaps = qc.detect_gaps(presence, ["M"])
    assert len(gaps) == 1
    assert gaps[0].start_frame == 2 and gaps[0].end_frame == 4
    assert gaps[0].length_frames == 3


def test_clean_segment_is_include_info(thresholds):
    presence = np.ones((600, 5), dtype=bool)
    names = ["HeadTop", "ChestTop", "LElbowOut", "RElbowOut", "WaistLFront"]
    findings = qc.qc_segment(_md(presence, names), thresholds, "S::ex09")
    seg = findings[0]
    assert seg.severity == Severity.INFO
    assert seg.recommendation == Recommendation.INCLUDE
    assert "0.0% marker gaps" in seg.message or "0.0%" in seg.message


def test_high_missing_region_recommends_exclude(thresholds):
    # left-arm markers missing 30% -> caution_max (10%) exceeded -> exclude
    n = 1000
    presence = np.ones((n, 4), dtype=bool)
    names = ["LElbowOut", "LWristOut", "ChestTop", "HeadTop"]
    presence[:300, 0] = False  # LElbowOut missing 30%
    findings = qc.qc_segment(_md(presence, names), thresholds, "S::ex09", region_filter="left_arm")
    la = findings[0]
    assert la.resolution == "link"
    assert la.recommendation == Recommendation.EXCLUDE
    assert "left arm" in la.message
    assert "link-level" in la.affects_levels


def test_large_gap_flagged_critical(thresholds):
    # one marker with a 1s gap at 120Hz = 120 frames > 0.5s critical
    n = 1200
    presence = np.ones((n, 2), dtype=bool)
    names = ["LElbowOut", "ChestTop"]
    presence[100:230, 0] = False  # 130-frame gap ~1.08s
    findings = qc.qc_segment(_md(presence, names), thresholds, "S::ex09", region_filter="left_arm")
    msg = findings[0].message
    assert "critical" in msg.lower()
    assert findings[0].severity == Severity.SOFT_WARNING


def test_all_regions_emits_per_region_findings(thresholds):
    presence = np.ones((300, 4), dtype=bool)
    names = ["HeadTop", "ChestTop", "LElbowOut", "RElbowOut"]
    findings = qc.qc_segment_all_regions(_md(presence, names), thresholds, "S::ex09")
    resolutions = {f.resolution for f in findings}
    scopes = {f.scope for f in findings}
    assert "segment" in resolutions and "link" in resolutions
    assert any("left_arm" in s for s in scopes)
    assert any("right_arm" in s for s in scopes)


def test_velocity_artifact_detection(thresholds):
    rng = np.random.default_rng(0)
    n, m = 500, 3
    positions = rng.normal(0, 0.001, size=(n, m, 3))
    positions[250, 0, :] += 100.0  # a huge spike
    presence = np.ones((n, m), dtype=bool)
    names = ["LElbowOut", "ChestTop", "HeadTop"]
    findings = qc.qc_segment_all_regions(_md(presence, names, positions=positions), thresholds, "S::ex09")
    assert any(f.metric == "velocity_artifact_frames" and f.value >= 1 for f in findings)


def test_marker_set_finding():
    f = qc.marker_set_finding("671", {"671_T1_P1_R1": "671", "671_T3_P1_R1": "T3"})
    assert f is not None
    assert f.recommendation == Recommendation.INCLUDE_WITH_CAUTION
    assert "shared valid link intersection" in f.message
    assert qc.marker_set_finding("252", {"a": "252", "b": "252"}) is None


def test_findings_to_dataframe(thresholds):
    presence = np.ones((300, 2), dtype=bool)
    findings = qc.qc_segment_all_regions(_md(presence, ["ChestTop", "HeadTop"]), thresholds, "S::ex09")
    df = qc.findings_to_dataframe(findings)
    assert set(["resolution", "severity", "recommendation", "message"]).issubset(df.columns)


@pytest.mark.slow
def test_parse_motive_marker_csv_from_skeleton(project_root):
    skel = (
        project_root
        / "data/raw_skeleton/252/T1/252_T1_P1_R1_Take 2026-04-28 04.15.00 PM_000.csv"
    )
    if not skel.exists():
        pytest.skip("skeleton CSV not present")
    md = qc.parse_motive_marker_csv(skel, frame_rate_hz=120.0)
    assert "252:LAH" in md.marker_names
    mi = md.marker_names.index("252:LAH")
    assert md.positions is not None
    assert md.positions[100:, mi].shape[0] > 0
    assert np.isfinite(md.positions[100, mi]).all()


def test_run_marker_qc_synthetic(config, monkeypatch):
    from gaga_jcvpca.inventory import Inventory
    from gaga_jcvpca.schemas import ExerciseSegment, InventoryRow, SessionKey

    session = SessionKey("671", "T1", "P1", "R1")
    inv = Inventory(
        rows=[
            InventoryRow(
                participant="671",
                timepoint="T1",
                task_part="P1",
                repetition="R1",
                session_id=session.as_str(),
                has_marker_csv=True,
            )
        ],
        segments=[
            ExerciseSegment(
                session=session,
                exercise_id=9,
                canonical_label="ex09",
                exercise_name="test",
                start_frame=0,
                end_frame=300,
            )
        ],
        naming_issues=[],
    )
    presence = np.ones((600, 3), dtype=bool)
    names = ["LElbowOut", "ChestTop", "HeadTop"]
    md = qc.MarkerData(marker_names=names, presence=presence, frame_rate_hz=120.0)

    monkeypatch.setattr(
        "gaga_jcvpca.qc_markers.parse_motive_marker_csv",
        lambda path, frame_rate_hz: md,
    )
    monkeypatch.setattr(
        "gaga_jcvpca.project_io.resolve_session_marker_csv",
        lambda cfg, sid: Path("/fake/marker.csv"),
    )

    findings, df = qc.run_marker_qc(config, inv, write_cache=False)
    assert findings
    assert not df.empty
    assert set(["resolution", "severity", "recommendation", "message"]).issubset(df.columns)
    assert any("::session" in f.scope for f in findings)
    assert any("::ex09" in f.scope for f in findings)


def test_run_marker_qc_parse_failure_soft_warning(config, monkeypatch):
    from gaga_jcvpca.inventory import Inventory
    from gaga_jcvpca.schemas import InventoryRow

    inv = Inventory(
        rows=[
            InventoryRow(
                participant="671",
                timepoint="T1",
                task_part="P1",
                repetition="R1",
                session_id="671_T1_P1_R1",
                has_marker_csv=True,
            )
        ],
        segments=[],
        naming_issues=[],
    )

    def _boom(path, frame_rate_hz):
        raise ValueError("bad csv")

    monkeypatch.setattr("gaga_jcvpca.qc_markers.parse_motive_marker_csv", _boom)
    monkeypatch.setattr(
        "gaga_jcvpca.project_io.resolve_session_marker_csv",
        lambda cfg, sid: Path("/fake/bad.csv"),
    )

    findings, df = qc.run_marker_qc(config, inv, write_cache=False)
    assert len(findings) == 1
    assert findings[0].metric == "parse_error"
    assert "bad csv" in findings[0].message
