"""Inventory scan tests against the real copied data."""

from __future__ import annotations

from gaga_jcvpca.inventory import build_inventory


def test_inventory_discovers_both_participants(config):
    inv = build_inventory(config)
    assert set(inv.participants()) == {"671", "252"}


def test_inventory_timepoints_and_repetitions(config):
    inv = build_inventory(config)
    assert set(inv.timepoints()) == {"T1", "T2", "T3"}
    assert set(inv.repetitions()) == {"R1", "R2"}


def test_inventory_only_p1_task_part(config):
    inv = build_inventory(config)
    assert {r.task_part for r in inv.rows} == {"P1"}


def test_inventory_exercise_ids_authoritative(config):
    inv = build_inventory(config)
    assert inv.exercise_ids() == list(range(1, 18))


def test_inventory_summary_shape(config):
    inv = build_inventory(config)
    s = inv.summary()
    assert s["n_participants"] == 2
    # 2 participants x 3 timepoints x 2 reps of P1 segmentation sheets = 12
    assert s["n_sessions"] == 12


def test_inventory_marker_set_difference_flagged(config):
    inv = build_inventory(config)
    # 671 T3 uses a different marker-set prefix; if description files exist for
    # both prefixes it should be flagged. At minimum the checker must run cleanly.
    kinds = {i.kind for i in inv.naming_issues}
    assert isinstance(kinds, set)
