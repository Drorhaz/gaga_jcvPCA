"""Snapshot read model used by the dashboard (Tabs 1 & 2)."""

from __future__ import annotations

from gaga_jcvpca.pipeline import build_snapshot


def test_snapshot_has_summary_and_next_action(config):
    snap = build_snapshot(config)
    assert snap.science_hash == config.science_hash
    s = snap.summary
    assert s["n_participants"] == 2
    assert s["n_sessions"] == 12
    assert snap.recommended_next_action  # non-empty guidance


def test_snapshot_dataframes_render(config):
    snap = build_snapshot(config)
    rows = snap.inventory.rows_dataframe()
    segs = snap.inventory.segments_dataframe()
    assert set(["session_id", "status", "n_exercises"]).issubset(rows.columns)
    assert set(["canonical_label", "gaga_alias", "group_id"]).issubset(segs.columns)
    assert len(rows) == 12
    assert len(segs) > 0


def test_next_action_reflects_ready_sessions(config):
    snap = build_snapshot(config)
    # Skeleton CSVs and segmentation sheets are present for all P1 sessions.
    assert snap.summary["n_ready_sessions"] == 12
    assert "review qc" in snap.recommended_next_action.lower()
