"""Optional statistical validation: strength labels + data-sufficiency gating."""

from __future__ import annotations

import numpy as np
import pandas as pd

from gaga_jcvpca import jcvpca, validation
from gaga_jcvpca.schemas import ValidationStrength

FEATURES = [
    f"{stem}_{ax}"
    for stem in ["Chest_to_Neck", "Neck_to_Head", "LShoulder_to_LUArm", "RShoulder_to_RUArm"]
    for ax in ("rx", "ry", "rz")
]


def _matrix(features, n=300, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame(rng.standard_normal((n, len(features))), columns=features)


def _comparison(kind, a, b, seed_offset=0):
    return jcvpca.run_comparison(
        f"c_{kind}", kind, "a", "b", a, b, FEATURES, variance_threshold=0.80
    )


def test_natural_variability_baseline_labels_descriptive():
    a = _matrix(FEATURES, seed=1)
    b = _matrix(FEATURES, seed=2)
    r1 = _matrix(FEATURES, seed=3)
    r2 = _matrix(FEATURES, seed=4)
    lon = _comparison("longitudinal", a, b)
    nv = _comparison("natural_variability", r1, r2)
    concs = validation.natural_variability_baseline(lon, nv)
    assert concs
    assert all(c.strength == ValidationStrength.DESCRIPTIVE_ONLY.value for c in concs)
    assert all("natural variability" in c.message for c in concs)


def test_sensitivity_analysis_runs():
    a = _matrix(FEATURES, seed=5)
    b = _matrix(FEATURES, seed=6)
    concs = validation.sensitivity_analysis(a, b, FEATURES, 0.80, drop_links=["Neck_to_Head"])
    assert len(concs) == 1
    assert concs[0].strength in {
        ValidationStrength.SENSITIVITY_SUPPORTED.value,
        ValidationStrength.DESCRIPTIVE_ONLY.value,
    }


def test_sensitivity_insufficient_when_too_few_links():
    a = _matrix(FEATURES, seed=7)
    b = _matrix(FEATURES, seed=8)
    drop = ["Chest_to_Neck", "Neck_to_Head", "LShoulder_to_LUArm"]  # leaves 1 link
    concs = validation.sensitivity_analysis(a, b, FEATURES, 0.80, drop_links=drop)
    assert concs[0].strength == ValidationStrength.INSUFFICIENT_DATA.value


def test_pca_stability_needs_two_matrices():
    a = _matrix(FEATURES, seed=9)
    concs = validation.pca_stability({"R1": a}, FEATURES, 0.80)
    assert concs[0].strength == ValidationStrength.INSUFFICIENT_DATA.value


def test_pca_stability_reports_similarity():
    r1 = _matrix(FEATURES, seed=10)
    r2 = _matrix(FEATURES, seed=11)
    concs = validation.pca_stability({"R1": r1, "R2": r2}, FEATURES, 0.80)
    assert concs[0].metric == "basis_similarity"
    assert 0.0 <= concs[0].value <= 1.0


def test_bootstrap_insufficient_data():
    a = _matrix(FEATURES, n=30, seed=12)
    b = _matrix(FEATURES, n=30, seed=13)
    concs, detail = validation.bootstrap_link_deltas(
        a, b, FEATURES, 0.80, n_resamples=50, min_windows_for_bootstrap=10, window_size=20
    )
    assert concs[0].strength == ValidationStrength.INSUFFICIENT_DATA.value
    assert detail.empty


def test_bootstrap_runs_when_sufficient():
    a = _matrix(FEATURES, n=800, seed=14)
    b = _matrix(FEATURES, n=800, seed=15)
    concs, detail = validation.bootstrap_link_deltas(
        a, b, FEATURES, 0.80, n_resamples=100, min_windows_for_bootstrap=4, window_size=50
    )
    assert not detail.empty
    assert {"link_id", "ci_low", "ci_high", "ci_excludes_zero"}.issubset(detail.columns)


def test_run_validation_end_to_end(config):
    a = _matrix(FEATURES, n=600, seed=16)
    b = _matrix(FEATURES, n=600, seed=17)
    r1 = _matrix(FEATURES, n=600, seed=18)
    r2 = _matrix(FEATURES, n=600, seed=19)
    lon = _comparison("longitudinal", a, b)
    nv = _comparison("natural_variability", r1, r2)
    report = validation.run_validation(
        config, lon, nv, a, b, FEATURES,
        flagged_links=["Neck_to_Head"],
        repetition_matrices={"R1": r1, "R2": r2},
    )
    df = report.to_dataframe()
    assert not df.empty
    assert set(df["method"]) >= {"natural_variability", "sensitivity", "pca_stability", "bootstrap"}
    md = report.summary_md()
    assert "Validation summary" in md
    # every conclusion carries an explicit strength label
    valid_strengths = {s.value for s in ValidationStrength}
    assert set(df["strength"]).issubset(valid_strengths)
