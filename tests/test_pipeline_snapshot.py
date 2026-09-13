"""Snapshot read model used by the dashboard (Tabs 1 & 2)."""

from __future__ import annotations

from gaga_jcvpca.pipeline import build_snapshot


def test_snapshot_has_summary_and_next_action(config):
    snap = build_snapshot(config)
    assert snap.science_hash == config.science_hash
    s = snap.summary
    assert s["n_participants"] >= 2
    assert s["n_sessions"] >= 12
    assert snap.recommended_next_action  # non-empty guidance
    assert "n_findings" in snap.qc_summary
    assert isinstance(snap.qc_summary_df, type(snap.qc_summary_df))


def test_snapshot_qc_when_markers_present(config):
    snap = build_snapshot(config)
    n_marker = sum(1 for r in snap.inventory.rows if r.has_marker_csv)
    if n_marker == 0:
        assert snap.qc_summary["n_findings"] == 0
        return
    assert snap.qc_summary["n_sessions_with_markers"] == n_marker
    assert set(["n_soft_warnings", "n_large_gaps", "by_severity"]).issubset(
        snap.qc_summary.keys()
    )
    assert isinstance(snap.qc_gap_heatmaps, dict)


def test_snapshot_dataframes_render(config):
    snap = build_snapshot(config)
    rows = snap.inventory.rows_dataframe()
    segs = snap.inventory.segments_dataframe()
    assert set(["session_id", "status", "n_exercises"]).issubset(rows.columns)
    assert set(["canonical_label", "group_id"]).issubset(segs.columns)
    assert len(rows) >= 12
    assert len(segs) > 0


def test_snapshot_qc_covers_skeleton_only_sessions(config):
    from gaga_jcvpca import qc_markers
    from gaga_jcvpca.inventory import build_inventory

    inv = build_inventory(config)
    skeleton_dir = config.resolve_path("data.raw_skeleton")
    for pid in ("651", "790"):
        if not (skeleton_dir / pid).is_dir():
            continue
        expected = {
            r.session_id for r in inv.rows if r.participant == pid and r.has_marker_csv
        }
        assert expected
        findings, _, _ = qc_markers.run_marker_qc(config, inv, write_cache=False)
        qc_sessions = {f.scope.split("::", 1)[0] for f in findings}
        assert expected.intersection(qc_sessions)


def test_next_action_reflects_ready_sessions(config):
    snap = build_snapshot(config)
    assert snap.summary["n_ready_sessions"] > 0
    assert snap.summary["n_ready_sessions"] == snap.inventory.summary()["n_ready_sessions"]
    assert "review qc" in snap.recommended_next_action.lower()
