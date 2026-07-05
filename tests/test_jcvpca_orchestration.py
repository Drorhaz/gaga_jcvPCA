"""Comparison orchestration around the ported core."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from gaga_jcvpca import jcvpca
from gaga_jcvpca.selection import region_of_link


def _matrix(features, n=200, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame(rng.standard_normal((n, len(features))), columns=features)


FEATURES = [
    f"{stem}_{ax}"
    for stem in ["Chest_to_Neck", "Neck_to_Head", "LShoulder_to_LUArm", "RShoulder_to_RUArm"]
    for ax in ("rx", "ry", "rz")
]


def test_run_comparison_produces_all_tables(config):
    a = _matrix(FEATURES, seed=1)
    b = _matrix(FEATURES, seed=2)
    res = jcvpca.run_comparison(
        "671_T1_vs_T3",
        "longitudinal",
        "671_T1",
        "671_T3",
        a,
        b,
        FEATURES,
        variance_threshold=0.80,
        region_of_link=lambda stem: region_of_link(stem, config),
        sensitivity_p=2,
    )
    assert res.selected_m >= 1
    assert not res.axis_table.empty
    assert not res.link_table.empty
    assert not res.region_table.empty
    assert set(res.space_table["space"]) <= {"functional", "null"}
    assert len(res.included_links) == 4
    assert res.excluded_links == {}
    # link table has one row per (pc, link)
    assert len(res.link_table) == res.selected_m * 4


def test_shared_link_restriction_671_t3_case(config):
    """Marker-set difference: B lacks one link -> restrict, warn, record; no hard block."""
    a = _matrix(FEATURES, seed=3)
    b_features = [f for f in FEATURES if not f.startswith("Neck_to_Head")]
    b = _matrix(b_features, seed=4)
    res = jcvpca.run_comparison(
        "671_T1_vs_T3",
        "longitudinal",
        "671_T1",
        "671_T3",
        a,
        b,
        FEATURES,
        variance_threshold=0.80,
    )
    assert "Neck_to_Head" in res.excluded_links
    assert "missing in dataset B" in res.excluded_links["Neck_to_Head"]
    assert res.warnings and "shared valid link intersection" in res.warnings[0]
    assert len(res.included_links) == 3


def test_no_shared_links_raises_validation_error():
    a = _matrix(FEATURES[:3], seed=5)  # only Chest_to_Neck triplet
    b = _matrix(FEATURES[3:6], seed=6)  # only Neck_to_Head triplet
    with pytest.raises(jcvpca.ValidationError):
        jcvpca.run_comparison(
            "x", "longitudinal", "a", "b", a, b, FEATURES[:6], variance_threshold=0.80
        )


def test_nonfinite_link_excluded():
    a = _matrix(FEATURES, seed=7)
    b = _matrix(FEATURES, seed=8)
    b.loc[5, "LShoulder_to_LUArm_ry"] = np.nan
    res = jcvpca.run_comparison(
        "c", "natural_variability", "R1", "R2", a, b, FEATURES, variance_threshold=0.80
    )
    assert "LShoulder_to_LUArm" in res.excluded_links
    assert "non-finite" in res.excluded_links["LShoulder_to_LUArm"]


def test_threshold_sweep_diagnostic():
    a = _matrix(FEATURES, seed=9)
    b = _matrix(FEATURES, seed=10)
    sweep = jcvpca.threshold_sweep(a, b, FEATURES, candidates=[0.70, 0.80, 0.90])
    assert list(sweep["variance_threshold"]) == [0.70, 0.80, 0.90]
    # selected_m must be non-decreasing with threshold
    ms = sweep["selected_m"].tolist()
    assert ms == sorted(ms)
    assert sweep["top1_link"].notna().all()


def test_functional_null_split_uses_sensitivity_p():
    a = _matrix(FEATURES, seed=11)
    b = _matrix(FEATURES, seed=12)
    res = jcvpca.run_comparison(
        "c", "longitudinal", "a", "b", a, b, FEATURES, variance_threshold=0.90, sensitivity_p=2
    )
    functional = res.space_table[res.space_table["space"] == "functional"]
    assert (functional["n_pcs"] <= 2).all()


def test_min_rows_gate():
    a = _matrix(FEATURES, n=5, seed=13)
    b = _matrix(FEATURES, n=5, seed=14)
    with pytest.raises(jcvpca.ValidationError):
        jcvpca.run_comparison(
            "c", "longitudinal", "a", "b", a, b, FEATURES, variance_threshold=0.80
        )
