"""Optional statistical validation (runs after per-participant JcvPCA results).

Validation never manufactures confidence. Each conclusion carries an explicit
strength label, and methods only run when the data supports them (decision 6):

  1. Natural-variability baseline (primary, always available)
  2. Sensitivity analysis (primary, always available)
  3. PCA-basis stability (primary)
  4. Bootstrap over frames/windows (secondary, only when enough windows exist)
  5. Permutation tests (secondary/exploratory, sufficiency-gated)

When data is insufficient it reports `insufficient data` / `descriptive only`
rather than emitting misleading statistics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from gaga_jcvpca import jcvpca
from gaga_jcvpca.schemas import ValidationStrength


@dataclass
class ValidationConclusion:
    method: str                 # natural_variability / sensitivity / pca_stability / bootstrap / permutation
    scope: str                  # link or region id, or "run"
    metric: str
    value: float
    strength: str               # ValidationStrength value
    message: str                # researcher-facing sentence


def conclusions_to_dataframe(conclusions: list[ValidationConclusion]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "method": c.method,
                "scope": c.scope,
                "metric": c.metric,
                "value": c.value,
                "strength": c.strength,
                "message": c.message,
            }
            for c in conclusions
        ]
    )


# --- 1. natural-variability baseline ---

def natural_variability_baseline(
    longitudinal: jcvpca.ComparisonResult,
    natural_variability: jcvpca.ComparisonResult,
) -> list[ValidationConclusion]:
    """Compare each longitudinal link delta to the R1-vs-R2 (NV) delta magnitude.

    Effect ratio = |longitudinal Δ| / (|NV Δ| + eps). Ratio > 1 means the
    longitudinal change is larger than the observed repetition-level variability.
    """
    eps = 1e-9
    long_link = (
        longitudinal.link_table.groupby("link_id")["JcvPCA_link"]
        .apply(lambda s: float(np.mean(np.abs(s))))
    )
    nv_link = (
        natural_variability.link_table.groupby("link_id")["JcvPCA_link"]
        .apply(lambda s: float(np.mean(np.abs(s))))
    )
    conclusions: list[ValidationConclusion] = []
    for link, long_val in long_link.items():
        nv_val = float(nv_link.get(link, np.nan))
        if not np.isfinite(nv_val):
            continue
        ratio = long_val / (nv_val + eps)
        beyond = ratio > 1.0
        conclusions.append(
            ValidationConclusion(
                method="natural_variability",
                scope=link,
                metric="effect_ratio_vs_nv",
                value=round(ratio, 4),
                strength=ValidationStrength.DESCRIPTIVE_ONLY.value,
                message=(
                    f"{link}: longitudinal contribution change is "
                    f"{ratio:.2f}x the R1-vs-R2 natural variability "
                    f"({'beyond' if beyond else 'within'} repetition-level variability)."
                ),
            )
        )
    return conclusions


# --- 2. sensitivity analysis ---

def sensitivity_analysis(
    a_df: pd.DataFrame,
    b_df: pd.DataFrame,
    feature_names: list[str],
    variance_threshold: float,
    drop_links: list[str],
    top_n: int = 5,
) -> list[ValidationConclusion]:
    """Re-run without flagged links; check whether the top-link ranking survives."""
    def _ranking(features):
        res = jcvpca.run_comparison(
            "sens", "longitudinal", "a", "b", a_df, b_df, features, variance_threshold
        )
        lt = res.link_table
        return (
            lt.assign(absd=lt["JcvPCA_link"].abs())
            .groupby("link_id")["absd"].mean()
            .sort_values(ascending=False)
        )

    base = _ranking(feature_names)
    kept_features = [
        f for f in feature_names if jcvpca.link_id_of(f) not in set(drop_links)
    ]
    if len({jcvpca.link_id_of(f) for f in kept_features}) < 2:
        return [
            ValidationConclusion(
                method="sensitivity",
                scope="run",
                metric="top_link_overlap",
                value=0.0,
                strength=ValidationStrength.INSUFFICIENT_DATA.value,
                message="Sensitivity analysis skipped: too few links remain after exclusions.",
            )
        ]
    reduced = _ranking(kept_features)

    base_top = [l for l in base.index[:top_n] if l not in set(drop_links)]
    reduced_top = list(reduced.index[:top_n])
    overlap = len(set(base_top) & set(reduced_top)) / max(1, len(base_top))
    stable = overlap >= 0.6
    return [
        ValidationConclusion(
            method="sensitivity",
            scope="run",
            metric="top_link_overlap",
            value=round(overlap, 3),
            strength=(
                ValidationStrength.SENSITIVITY_SUPPORTED.value
                if stable
                else ValidationStrength.DESCRIPTIVE_ONLY.value
            ),
            message=(
                f"Top-link ranking overlap after excluding flagged links = {overlap:.0%}; "
                f"{'ranking is stable (sensitivity-supported)' if stable else 'ranking is not stable (interpret with caution)'}."
            ),
        )
    ]


# --- 3. PCA-basis stability ---

def _subspace_similarity(frame_a: np.ndarray, frame_b: np.ndarray) -> float:
    """Mean absolute cosine similarity between matched principal-component rows."""
    m = min(frame_a.shape[0], frame_b.shape[0])
    sims = []
    for i in range(m):
        va, vb = frame_a[i], frame_b[i]
        denom = np.linalg.norm(va) * np.linalg.norm(vb)
        if denom > 0:
            sims.append(abs(float(np.dot(va, vb)) / denom))
    return float(np.mean(sims)) if sims else 0.0


def pca_stability(
    matrices: dict[str, pd.DataFrame],
    feature_names: list[str],
    variance_threshold: float,
) -> list[ValidationConclusion]:
    """Loading similarity of the A-basis across repetitions (e.g. R1, R2, R1+R2)."""
    from sklearn.decomposition import PCA

    labels = list(matrices)
    if len(labels) < 2:
        return [
            ValidationConclusion(
                method="pca_stability",
                scope="run",
                metric="basis_similarity",
                value=0.0,
                strength=ValidationStrength.INSUFFICIENT_DATA.value,
                message="PCA stability skipped: need at least two repetition matrices.",
            )
        ]
    frames = {}
    for label, df in matrices.items():
        selected_m, _ = jcvpca.select_selected_m_from_A(df, feature_names, variance_threshold)
        centered = df[feature_names] - df[feature_names].mean()
        pca = PCA(n_components=selected_m)
        pca.fit(centered)
        frames[label] = pca.components_

    sims = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            sims.append(_subspace_similarity(frames[labels[i]], frames[labels[j]]))
    mean_sim = float(np.mean(sims))
    stable = mean_sim >= 0.8
    return [
        ValidationConclusion(
            method="pca_stability",
            scope="run",
            metric="basis_similarity",
            value=round(mean_sim, 3),
            strength=(
                ValidationStrength.SENSITIVITY_SUPPORTED.value
                if stable
                else ValidationStrength.DESCRIPTIVE_ONLY.value
            ),
            message=(
                f"PCA basis similarity across repetitions = {mean_sim:.2f}; "
                f"{'dominant movement space is stable' if stable else 'movement space varies between repetitions (interpret with caution)'}."
            ),
        )
    ]


# --- 4. bootstrap (only when sufficient) ---

def bootstrap_link_deltas(
    a_df: pd.DataFrame,
    b_df: pd.DataFrame,
    feature_names: list[str],
    variance_threshold: float,
    n_resamples: int,
    min_windows_for_bootstrap: int,
    window_size: Optional[int] = None,
    random_seed: int = 12345,
) -> tuple[list[ValidationConclusion], pd.DataFrame]:
    """Bootstrap CIs on link deltas by resampling frame blocks.

    Runs ONLY when both matrices provide at least ``min_windows_for_bootstrap``
    resampling blocks. Otherwise returns an insufficient-data conclusion and an
    empty detail table (never fabricates statistics).
    """
    rng = np.random.default_rng(random_seed)
    n_a, n_b = len(a_df), len(b_df)
    win = window_size or max(10, min(n_a, n_b) // min_windows_for_bootstrap)
    n_blocks_a = n_a // win
    n_blocks_b = n_b // win

    if n_blocks_a < min_windows_for_bootstrap or n_blocks_b < min_windows_for_bootstrap:
        return (
            [
                ValidationConclusion(
                    method="bootstrap",
                    scope="run",
                    metric="n_windows",
                    value=float(min(n_blocks_a, n_blocks_b)),
                    strength=ValidationStrength.INSUFFICIENT_DATA.value,
                    message=(
                        f"Bootstrap not run: only {min(n_blocks_a, n_blocks_b)} clean windows "
                        f"available (need {min_windows_for_bootstrap}). Reporting descriptive only."
                    ),
                )
            ],
            pd.DataFrame(),
        )

    kept, _, _ = jcvpca.restrict_to_shared_features(a_df, b_df, feature_names)
    link_map = jcvpca.build_joint_link_map(kept)
    a_arr = a_df[kept].to_numpy()
    b_arr = b_df[kept].to_numpy()

    samples: dict[str, list[float]] = {link: [] for link in link_map}
    for _ in range(n_resamples):
        idx_a = _block_resample(n_a, win, n_blocks_a, rng)
        idx_b = _block_resample(n_b, win, n_blocks_b, rng)
        a_s = pd.DataFrame(a_arr[idx_a], columns=kept)
        b_s = pd.DataFrame(b_arr[idx_b], columns=kept)
        try:
            res = jcvpca.compute_jcvpca(a_s, b_s, kept, variance_threshold=variance_threshold)
        except jcvpca.ValidationError:
            continue
        lt = jcvpca.aggregate_axis_to_link_rss(
            res["A_abs_loadings"], res["B_abs_loadings"], kept, link_map
        )
        per_link = lt.groupby("link_id")["JcvPCA_link"].apply(lambda s: float(np.mean(s)))
        for link, val in per_link.items():
            samples[link].append(val)

    rows = []
    conclusions = []
    n_significant = 0
    for link, vals in samples.items():
        if not vals:
            continue
        arr = np.array(vals)
        lo, hi = np.percentile(arr, [2.5, 97.5])
        mean = float(np.mean(arr))
        excludes_zero = lo > 0 or hi < 0
        rows.append(
            {
                "link_id": link,
                "mean_delta": mean,
                "ci_low": float(lo),
                "ci_high": float(hi),
                "n_samples": len(vals),
                "ci_excludes_zero": bool(excludes_zero),
            }
        )
        if excludes_zero:
            n_significant += 1
            conclusions.append(
                ValidationConclusion(
                    method="bootstrap",
                    scope=link,
                    metric="ci95_delta",
                    value=round(mean, 4),
                    strength=ValidationStrength.BOOTSTRAP_SUPPORTED.value,
                    message=(
                        f"{link}: bootstrap 95% CI [{lo:.3f}, {hi:.3f}] excludes zero "
                        f"(bootstrap-supported change)."
                    ),
                )
            )
    # Always emit a run-level summary so the method is represented when it runs.
    conclusions.insert(
        0,
        ValidationConclusion(
            method="bootstrap",
            scope="run",
            metric="n_links_ci_excludes_zero",
            value=float(n_significant),
            strength=(
                ValidationStrength.BOOTSTRAP_SUPPORTED.value
                if n_significant > 0
                else ValidationStrength.DESCRIPTIVE_ONLY.value
            ),
            message=(
                f"Bootstrap ran ({len(rows)} links, {n_resamples} resamples): "
                f"{n_significant} link(s) have a 95% CI that excludes zero."
            ),
        ),
    )
    return conclusions, pd.DataFrame(rows)


def _block_resample(n: int, win: int, n_blocks: int, rng) -> np.ndarray:
    starts = rng.integers(0, n - win + 1, size=n_blocks)
    return np.concatenate([np.arange(s, s + win) for s in starts])


# --- top-level runner ---

@dataclass
class ValidationReport:
    conclusions: list[ValidationConclusion] = field(default_factory=list)
    bootstrap_detail: pd.DataFrame = field(default_factory=pd.DataFrame)

    def to_dataframe(self) -> pd.DataFrame:
        return conclusions_to_dataframe(self.conclusions)

    def summary_md(self) -> str:
        if not self.conclusions:
            return "No validation was run for this analysis."
        by_method: dict[str, list[ValidationConclusion]] = {}
        for c in self.conclusions:
            by_method.setdefault(c.method, []).append(c)
        lines = ["## Validation summary", ""]
        titles = {
            "natural_variability": "Natural-variability baseline",
            "sensitivity": "Sensitivity analysis",
            "pca_stability": "PCA-basis stability",
            "bootstrap": "Bootstrap",
            "permutation": "Permutation",
        }
        for method, items in by_method.items():
            lines.append(f"### {titles.get(method, method)}")
            for c in items:
                lines.append(f"- {c.message} _[{c.strength}]_")
            lines.append("")
        return "\n".join(lines)


def run_validation(
    config,
    longitudinal: jcvpca.ComparisonResult,
    natural_variability: jcvpca.ComparisonResult,
    a_df: pd.DataFrame,
    b_df: pd.DataFrame,
    feature_names: list[str],
    flagged_links: Optional[list[str]] = None,
    repetition_matrices: Optional[dict[str, pd.DataFrame]] = None,
) -> ValidationReport:
    """Run the enabled validation methods; each is strength-labeled and data-gated."""
    vt = float(config.get("pca.variance_threshold", 0.80))
    methods = config.get("validation.methods", {}) or {}
    conclusions: list[ValidationConclusion] = []
    bootstrap_detail = pd.DataFrame()

    if methods.get("natural_variability_baseline", True):
        conclusions += natural_variability_baseline(longitudinal, natural_variability)

    if methods.get("sensitivity_analysis", True):
        conclusions += sensitivity_analysis(
            a_df, b_df, feature_names, vt, drop_links=flagged_links or []
        )

    if methods.get("pca_stability", True) and repetition_matrices:
        conclusions += pca_stability(repetition_matrices, feature_names, vt)

    if methods.get("bootstrap", True):
        bs_conf = config.get("validation.bootstrap", {}) or {}
        bs_conclusions, bootstrap_detail = bootstrap_link_deltas(
            a_df,
            b_df,
            feature_names,
            vt,
            n_resamples=int(bs_conf.get("n_resamples", 1000)),
            min_windows_for_bootstrap=int(bs_conf.get("min_windows_for_bootstrap", 4)),
            random_seed=int(config.get("validation.random_seed", 12345)),
        )
        conclusions += bs_conclusions

    return ValidationReport(conclusions=conclusions, bootstrap_detail=bootstrap_detail)
