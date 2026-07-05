"""Golden regression — pins exact JcvPCA numeric outputs (ported verbatim).

Carried over from the validated pipeline's ``test_core_golden_regression.py`` so
the ported math is provably identical. If this fails, the numeric behaviour of
the core changed; do NOT update golden values without review.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from gaga_jcvpca.jcvpca import (
    aggregate_axis_to_link_rss,
    build_joint_link_map,
    compute_jcvpca,
    select_selected_m_from_A,
)

LINKS = ["J004_Neck_to_Head", "J028_Chest_to_Neck"]
AXES = ["rx", "ry", "rz"]
FEATURES = [f"{link}_{axis}" for link in LINKS for axis in AXES]

CANONICAL_VARIANCE_THRESHOLD = 0.80

_A_SEED = 20260701
_B_SEED = 20260703
_N_ROWS = 300
_TOL = 1e-8

GOLDEN_SELECTED_M = 5

GOLDEN_EVR = [
    0.199297307139,
    0.185762693947,
    0.179829862409,
    0.159644637667,
    0.152291009767,
    0.123174489071,
]

GOLDEN_CUMULATIVE = [
    0.199297307139,
    0.385060001086,
    0.564889863495,
    0.724534501162,
    0.876825510929,
    1.0,
]

GOLDEN_JCVPCA_AXIS = [
    [0.15666456771, -0.579428911411, 0.450827784518, -0.108238930411, 0.194199810707, -0.137579654933],
    [0.231570532893, -0.485788514099, -0.125685467249, 0.089524679147, -0.263425674807, 0.221969534014],
    [-0.217200437851, -0.180494989221, 0.552785343508, 0.059875907935, -0.090866846964, -0.30904350423],
    [-0.136170723925, 0.682160235898, -0.777832336837, 0.007605851062, 0.081431811668, 0.199144901444],
    [-0.170727636288, -0.083087398334, 0.351061390525, 0.064525189229, 0.1513608817, 0.089337594013],
]

GOLDEN_LINK_JCVPCA = {
    "J004_Neck_to_Head": [0.016786668197, -0.055449952147, 0.310369738852, -0.051870440741, -0.078690010928],
    "J028_Chest_to_Neck": [-0.013117358388, 0.076435194756, -0.172948016229, 0.144370056502, 0.119203136449],
}


def _make_fixture(seed: int, session_id: str) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    data = rng.standard_normal((_N_ROWS, len(FEATURES)))
    df = pd.DataFrame(data, columns=FEATURES)
    df.insert(0, "time_sec", np.arange(_N_ROWS) / 120.0)
    df.insert(0, "frame", np.arange(_N_ROWS))
    df.insert(0, "run_label", f"{session_id}_Take")
    df.insert(0, "session_id", session_id)
    return df


def _fixture_A() -> pd.DataFrame:
    return _make_fixture(_A_SEED, "671_T1_P1_R1")


def _fixture_B() -> pd.DataFrame:
    return _make_fixture(_B_SEED, "671_T3_P1_R1")


def test_golden_selected_m_and_explained_variance():
    selected_m, evr_table = select_selected_m_from_A(
        _fixture_A(), FEATURES, CANONICAL_VARIANCE_THRESHOLD
    )
    assert selected_m == GOLDEN_SELECTED_M
    np.testing.assert_allclose(
        evr_table["explained_variance_ratio"].to_numpy(), GOLDEN_EVR, atol=_TOL
    )
    np.testing.assert_allclose(
        evr_table["cumulative_explained_variance"].to_numpy(),
        GOLDEN_CUMULATIVE,
        atol=_TOL,
    )


def test_golden_jcvpca_axis_matrix():
    result = compute_jcvpca(
        _fixture_A(), _fixture_B(), FEATURES,
        variance_threshold=CANONICAL_VARIANCE_THRESHOLD,
    )
    assert result["selected_m"] == GOLDEN_SELECTED_M
    assert result["jcvpca_axis"].shape == (GOLDEN_SELECTED_M, len(FEATURES))
    np.testing.assert_allclose(
        result["jcvpca_axis"], np.array(GOLDEN_JCVPCA_AXIS), atol=_TOL
    )


def test_golden_link_level_rss_jcvpca():
    result = compute_jcvpca(
        _fixture_A(), _fixture_B(), FEATURES,
        variance_threshold=CANONICAL_VARIANCE_THRESHOLD,
    )
    link_map = build_joint_link_map(FEATURES)
    link_df = aggregate_axis_to_link_rss(
        result["A_abs_loadings"], result["B_abs_loadings"], FEATURES, link_map
    )
    for link, expected in GOLDEN_LINK_JCVPCA.items():
        got = link_df[link_df["link_id"] == link]["JcvPCA_link"].to_numpy()
        np.testing.assert_allclose(got, expected, atol=_TOL)


def test_golden_fixture_is_deterministic():
    a1 = _fixture_A()[FEATURES].to_numpy()
    a2 = _fixture_A()[FEATURES].to_numpy()
    np.testing.assert_array_equal(a1, a2)
    assert abs(float(a1[0, 0]) - 1.606939651113697) < 1e-12
