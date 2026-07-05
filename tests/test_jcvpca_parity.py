"""Direct numeric parity: ported jcvpca core vs the original Layer 3 core.

Runs both implementations on identical random inputs and asserts the selected_m,
axis-level JcvPCA matrix, and RSS link deltas match to machine precision. This is
the numeric-parity acceptance check from the master plan (Section 17).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gaga_jcvpca import jcvpca

_ORIG_SRC = Path(
    "/Users/drorhazan/Desktop/gaga_psilo/projects/3Layers_project/Layer3_JcvPCA/src"
)

LINKS = ["J004_Neck_to_Head", "J028_Chest_to_Neck", "J046_Hip_to_Chest"]
FEATURES = [f"{link}_{ax}" for link in LINKS for ax in ("rx", "ry", "rz")]


def _fixture(seed: int, n: int = 250) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    return pd.DataFrame(rng.standard_normal((n, len(FEATURES))), columns=FEATURES)


@pytest.mark.skipif(not _ORIG_SRC.exists(), reason="original Layer 3 source not present")
@pytest.mark.parametrize("threshold", [0.70, 0.80, 0.90])
def test_ported_core_matches_original_layer3(threshold):
    import sys

    if str(_ORIG_SRC) not in sys.path:
        sys.path.insert(0, str(_ORIG_SRC))
    from layer3_jcvpca.core import compute_jcvpca as orig_compute
    from layer3_jcvpca.core import select_selected_m_from_A as orig_select
    from layer3_jcvpca.aggregation import aggregate_axis_to_link_rss as orig_rss
    from layer3_jcvpca.io import build_joint_link_map as orig_map

    a = _fixture(101)
    b = _fixture(202)

    # selected_m + EVR
    m_new, evr_new = jcvpca.select_selected_m_from_A(a, FEATURES, threshold)
    m_old, evr_old = orig_select(a, FEATURES, threshold)
    assert m_new == m_old
    np.testing.assert_allclose(
        evr_new["explained_variance_ratio"].to_numpy(),
        evr_old["explained_variance_ratio"].to_numpy(),
        atol=1e-12,
    )

    # axis-level jcvpca
    res_new = jcvpca.compute_jcvpca(a, b, FEATURES, variance_threshold=threshold)
    res_old = orig_compute(a, b, FEATURES, variance_threshold=threshold)
    assert res_new["selected_m"] == res_old["selected_m"]
    np.testing.assert_allclose(res_new["jcvpca_axis"], res_old["jcvpca_axis"], atol=1e-12)

    # RSS link deltas
    lm_new = jcvpca.build_joint_link_map(FEATURES)
    lm_old = orig_map(FEATURES)
    link_new = jcvpca.aggregate_axis_to_link_rss(
        res_new["A_abs_loadings"], res_new["B_abs_loadings"], FEATURES, lm_new
    )
    link_old = orig_rss(
        res_old["A_abs_loadings"], res_old["B_abs_loadings"], FEATURES, lm_old
    )
    np.testing.assert_allclose(
        link_new["JcvPCA_link"].to_numpy(),
        link_old["JcvPCA_link"].to_numpy(),
        atol=1e-12,
    )
