"""Tests for the signed NV profile module (v6)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from gaga_jcvpca import nv_profile


def _link_table(deltas: dict[str, list[float]], weights: list[float] | None = None) -> pd.DataFrame:
    """Build a per-PC link table. ``deltas`` maps link_id -> per-PC signed JcvPCA."""
    rows = []
    n_pc = len(next(iter(deltas.values())))
    for pc in range(n_pc):
        for link_id, vals in deltas.items():
            row = {"pc": pc + 1, "link_id": link_id, "JcvPCA_link": vals[pc]}
            if weights is not None:
                row["weighted_JcvPCA_link"] = vals[pc] * weights[pc]
            rows.append(row)
    return pd.DataFrame(rows)


# --- link_signed_value ---

def test_link_signed_value_preserves_sign_plain_sum():
    lt = _link_table({"A": [0.3, -0.1, -0.05]})  # sum = 0.15
    s = nv_profile.link_signed_value(lt, weighted=True)  # no weighted col -> plain
    assert s["A"] == pytest.approx(0.15)


def test_link_signed_value_does_not_cancel_to_abs():
    # A link up on PC1, down on PC2 must NOT be turned into mean-|Δ|.
    lt = _link_table({"A": [0.4, -0.4]})
    s = nv_profile.link_signed_value(lt, weighted=False)
    assert s["A"] == pytest.approx(0.0)  # signed sum cancels; abs-mean would be 0.4


def test_link_signed_value_evr_weighted():
    lt = _link_table({"A": [1.0, 1.0]}, weights=[0.8, 0.2])
    s = nv_profile.link_signed_value(lt, weighted=True)
    assert s["A"] == pytest.approx(1.0)  # 1*0.8 + 1*0.2
    s_plain = nv_profile.link_signed_value(lt, weighted=False)
    assert s_plain["A"] == pytest.approx(2.0)


def test_link_signed_value_empty():
    assert nv_profile.link_signed_value(None).empty
    assert nv_profile.link_signed_value(pd.DataFrame()).empty


# --- classify_nv_profile_tier ---

def test_tier_s0_within_floor():
    r = nv_profile.classify_nv_profile_tier(long_signed=0.05, nv_signed=0.10, long_signed_rev=0.05)
    assert r["nv_profile_tier"] == "S0"
    assert not r["magnitude_exceed"]
    assert not r["exceeds_signed_consistent"]


def test_tier_s2_exceed_and_direction_stable():
    r = nv_profile.classify_nv_profile_tier(long_signed=0.30, nv_signed=0.10, long_signed_rev=0.25)
    assert r["nv_profile_tier"] == "S2"
    assert r["magnitude_exceed"] and r["sign_reference_stable"]
    assert r["exceeds_signed_consistent"]


def test_tier_s1_exceed_but_direction_flips():
    r = nv_profile.classify_nv_profile_tier(long_signed=0.30, nv_signed=0.10, long_signed_rev=-0.25)
    assert r["nv_profile_tier"] == "S1"
    assert r["magnitude_exceed"] and not r["sign_reference_stable"]
    assert not r["exceeds_signed_consistent"]


def test_tier_s1_when_reverse_missing():
    r = nv_profile.classify_nv_profile_tier(long_signed=0.30, nv_signed=0.10, long_signed_rev=np.nan)
    assert r["nv_profile_tier"] == "S1"  # cannot confirm stability -> not S2


def test_floor_unstable_flag():
    r = nv_profile.classify_nv_profile_tier(long_signed=0.01, nv_signed=1e-9, long_signed_rev=0.01)
    assert r["nv_floor_unstable"]
    assert r["nv_profile_tier"] == "S2"  # still exceeds; flag warns ratio is unreliable


# --- elevate_to_s3 ---

def test_elevate_to_s3_all_pass():
    assert nv_profile.elevate_to_s3("S2", True, True, True) == "S3"


def test_no_elevation_when_evidence_missing():
    assert nv_profile.elevate_to_s3("S2", True, False, True) == "S2"
    assert nv_profile.elevate_to_s3("S1", True, True, True) == "S1"


# --- compute_link_nv_metrics integration ---

def test_compute_link_nv_metrics_end_to_end():
    nv = _link_table({"A": [0.10], "B": [0.20]}, weights=[1.0])
    lon = _link_table({"A": [0.30], "B": [0.05]}, weights=[1.0])       # A exceeds, B does not
    rev = _link_table({"A": [0.28], "B": [0.05]}, weights=[1.0])       # A same sign
    out = nv_profile.compute_link_nv_metrics(nv, lon, rev, weighted=True)
    a = out[out["link_id"] == "A"].iloc[0]
    b = out[out["link_id"] == "B"].iloc[0]
    assert a["nv_profile_tier"] == "S2"
    assert b["nv_profile_tier"] == "S0"
    assert a["long_signed_single"] == pytest.approx(0.30)
    assert a["matched_abs_ratio"] > 1.0
