"""Tests for marker-gap session-scoped link exclusions."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from gaga_jcvpca import jcvpca, marker_gap_policy


@pytest.fixture
def sample_removals(tmp_path):
    rows = [
        {
            "participant": "790",
            "session_id": "790_T1_P1_R2",
            "T_R": "T1_R2",
            "link_stem": "RUArm_to_RFArm",
            "removal_tier": "remove_from_comparison",
            "reason": "RHLE 99% large gaps",
        },
        {
            "participant": "790",
            "session_id": "790_T1_P1_R1",
            "T_R": "T1_R1",
            "link_stem": "Chest_to_Neck",
            "removal_tier": "watch",
            "reason": "minor",
        },
    ]
    path = tmp_path / "removals.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_pre_excluded_only_remove_tier(sample_removals):
    policy = marker_gap_policy.MarkerGapPolicy(
        enabled=True,
        removals_path=sample_removals,
        removals=marker_gap_policy.load_marker_gap_removals(sample_removals),
    )
    excl = marker_gap_policy.pre_excluded_for_comparison(
        "790",
        ["790_T1_P1_R1", "790_T1_P1_R2"],
        ["790_T2_P1_R1"],
        policy,
    )
    assert list(excl) == ["RUArm_to_RFArm"]
    assert excl["RUArm_to_RFArm"].startswith(marker_gap_policy.MARKER_GAP_PREFIX)


def test_pooled_side_includes_both_reps():
    sessions = marker_gap_policy.sessions_for_side(
        "651", "T1", repetition_mode="pooled", repetitions=["R1", "R2"]
    )
    assert sessions == ["651_T1_P1_R1", "651_T1_P1_R2"]


def test_run_comparison_applies_pre_excluded(config):
    import numpy as np

    features = [f"{s}_{ax}" for s in ("Chest_to_Neck", "RUArm_to_RFArm") for ax in ("rx", "ry", "rz")]
    rng = np.random.default_rng(0)
    a = pd.DataFrame(rng.standard_normal((50, len(features))), columns=features)
    b = pd.DataFrame(rng.standard_normal((50, len(features))), columns=features)
    pre = {
        "RUArm_to_RFArm": "marker_gap_policy: T1_R2 — test reason",
    }
    res = jcvpca.run_comparison(
        "790_T1_vs_T2",
        "longitudinal",
        "790_T1",
        "790_T2",
        a,
        b,
        features,
        variance_threshold=0.80,
        pre_excluded_links=pre,
    )
    assert "RUArm_to_RFArm" in res.excluded_links
    assert "RUArm_to_RFArm" not in res.included_links
    assert any("marker-gap policy" in w for w in res.warnings)
