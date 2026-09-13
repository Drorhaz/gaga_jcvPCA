"""Reference-subspace coverage gate (Step 8h.0).

Quantifies how well dataset B is represented in A's retained m-dimensional PCA subspace.
"""

from __future__ import annotations

import numpy as np
from sklearn.decomposition import PCA

from gaga_jcvpca import jcvpca

# Heuristic warning bands (pre-registered in LIMITS.md; not hard cutoffs).
COVERAGE_ADEQUATE_REL = 0.75
COVERAGE_LIMITED_REL = 0.50


def compute_subspace_coverage(
    a_df,
    b_df,
    feature_names: list[str],
    variance_threshold: float = 0.80,
    selected_m: int | None = None,
) -> dict[str, float | int | str]:
    """Return coverage_abs, coverage_rel, selected_m, and warning_band."""
    kept, _, _ = jcvpca.restrict_to_shared_features(a_df, b_df, feature_names)
    if not kept:
        return {
            "selected_m": 0,
            "coverage_abs": float("nan"),
            "coverage_rel": float("nan"),
            "coverage_band": "severe",
            "b_top_m_evr": float("nan"),
        }

    if selected_m is None:
        selected_m, _ = jcvpca.select_selected_m_from_A(
            a_df, kept, variance_threshold
        )
    selected_m = int(selected_m)

    a_centered = a_df[kept] - a_df[kept].mean()
    b_centered = b_df[kept] - b_df[kept].mean()
    m = min(selected_m, a_centered.shape[0], a_centered.shape[1], b_centered.shape[0])

    if m < 1:
        return {
            "selected_m": selected_m,
            "coverage_abs": float("nan"),
            "coverage_rel": float("nan"),
            "coverage_band": "severe",
            "b_top_m_evr": float("nan"),
        }

    pca_a = PCA(n_components=m)
    pca_a.fit(a_centered)
    frame = pca_a.components_

    x = b_centered.to_numpy(dtype=float)
    total_ss = float(np.sum(x**2))
    if total_ss <= 0:
        coverage_abs = float("nan")
    else:
        x_proj = x @ frame.T
        x_recon = x_proj @ frame
        residual_ss = float(np.sum((x - x_recon) ** 2))
        coverage_abs = max(0.0, min(1.0, 1.0 - residual_ss / total_ss))

    pca_b = PCA(n_components=m)
    pca_b.fit(b_centered)
    b_cum = float(np.cumsum(pca_b.explained_variance_ratio_)[m - 1])
    coverage_rel = (
        coverage_abs / b_cum if np.isfinite(coverage_abs) and b_cum > 0 else float("nan")
    )

    return {
        "selected_m": selected_m,
        "coverage_abs": round(coverage_abs, 4) if np.isfinite(coverage_abs) else float("nan"),
        "coverage_rel": round(coverage_rel, 4) if np.isfinite(coverage_rel) else float("nan"),
        "coverage_band": coverage_warning_band(coverage_rel),
        "b_top_m_evr": round(b_cum, 4),
    }


def coverage_warning_band(coverage_rel: float) -> str:
    if not np.isfinite(coverage_rel):
        return "severe"
    if coverage_rel >= COVERAGE_ADEQUATE_REL:
        return "adequate"
    if coverage_rel >= COVERAGE_LIMITED_REL:
        return "limited"
    return "severe"
