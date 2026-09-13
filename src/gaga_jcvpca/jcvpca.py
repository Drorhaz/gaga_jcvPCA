"""JcvPCA analysis: ported paper-faithful core + comparison orchestration.

PORTED BYTE-FAITHFUL from the validated Layer 3 pipeline (do not modify the math):
  * ``select_selected_m_from_A``  — smallest m with cumulative EVR of A >= threshold
  * ``compute_jcvpca``            — center A -> PCA(A) -> center B -> manual projection
                                     -> PCA(B_proj) -> reproject -> |B| - |A|
  * ``aggregate_axis_to_link_rss``— RSS link magnitudes, JcvPCA_link = JRW_B - JRW_A
  * ``build_axis_table``          — long-format axis-level table

Forbidden (and intentionally not used): PCA_A.transform(B_raw); z-scoring;
variance scaling; any alternative PCA-space comparison.

Added around the core (rewritten clean): region rollups, functional/null-space
split, comparison orchestration (T1 vs T2/T3, R1 vs R2 natural variability),
and the optional variance-threshold sweep diagnostic (decision 1).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

AXIS_SUFFIXES = ("_rx", "_ry", "_rz")
REQUIRED_AXES: tuple[str, str, str] = ("rx", "ry", "rz")


class ValidationError(Exception):
    """Raised when a JcvPCA validation gate fails (fail-fast, non-destructive)."""

    def __init__(self, message: str, report: dict | None = None):
        super().__init__(message)
        self.report = report or {}


# --- io helpers (ported) ---

def infer_feature_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c.endswith(AXIS_SUFFIXES)]


def axis_of(feature: str) -> str:
    if not feature.endswith(AXIS_SUFFIXES):
        raise ValueError(f"Not a rotation-vector feature column: {feature}")
    return feature[-2:]


def link_id_of(feature: str) -> str:
    if not feature.endswith(AXIS_SUFFIXES):
        raise ValueError(f"Not a rotation-vector feature column: {feature}")
    return feature[:-3]


def build_joint_link_map(feature_names: list[str]) -> dict[str, dict[str, str]]:
    link_map: dict[str, dict[str, str]] = {}
    for feat in feature_names:
        link_map.setdefault(link_id_of(feat), {})[axis_of(feat)] = feat
    return link_map


# --- validation gate (ported) ---

def validate_selected_m(
    selected_m: int,
    n_features_A: int,
    n_rows_A: int,
    n_rows_B: int,
    min_rows_for_pca: int = 10,
) -> None:
    if not isinstance(selected_m, (int, np.integer)) or selected_m < 1:
        raise ValidationError(f"selected_m must be a positive integer, got {selected_m!r}.")
    if selected_m > n_features_A:
        raise ValidationError(f"selected_m={selected_m} exceeds number of features={n_features_A}.")
    if selected_m > n_rows_A:
        raise ValidationError(f"selected_m={selected_m} exceeds number of A rows={n_rows_A}.")
    if selected_m > n_rows_B:
        raise ValidationError(
            f"selected_m={selected_m} exceeds number of B rows={n_rows_B} "
            f"(B is projected into the selected_m-dimensional A space)."
        )
    if n_rows_A < min_rows_for_pca or n_rows_B < min_rows_for_pca:
        raise ValidationError(
            f"Too few rows for PCA: A={n_rows_A}, B={n_rows_B}, min_rows_for_pca={min_rows_for_pca}."
        )


# --- SACRED CORE (ported byte-faithful; numbers must not change) ---

def select_selected_m_from_A(
    A_data: pd.DataFrame,
    feature_names: list[str],
    variance_threshold: float = 0.90,
) -> tuple[int, pd.DataFrame]:
    """Choose ``selected_m`` from A only (smallest m reaching the cumulative EVR)."""
    A_centered = A_data[feature_names] - A_data[feature_names].mean()
    max_components = min(A_centered.shape[0], A_centered.shape[1])
    pca_full = PCA(n_components=max_components)
    pca_full.fit(A_centered)

    evr = pca_full.explained_variance_ratio_
    cumulative = np.cumsum(evr)
    selected_m = int(np.searchsorted(cumulative, variance_threshold) + 1)
    selected_m = min(selected_m, max_components)

    evr_table = pd.DataFrame(
        {
            "pc": np.arange(1, len(evr) + 1),
            "explained_variance_ratio": evr,
            "cumulative_explained_variance": cumulative,
        }
    )
    return selected_m, evr_table


def compute_jcvpca(
    A_data: pd.DataFrame,
    B_data: pd.DataFrame,
    feature_names: list[str],
    variance_threshold: float = 0.90,
    selected_m: int | None = None,
    min_rows_for_pca: int = 10,
) -> dict:
    """Compute axis-level JcvPCA comparing B against reference A (paper sequence)."""
    if selected_m is None:
        selected_m, evr_table_full = select_selected_m_from_A(
            A_data, feature_names, variance_threshold
        )
    else:
        _, evr_table_full = select_selected_m_from_A(
            A_data, feature_names, variance_threshold
        )

    validate_selected_m(
        selected_m=selected_m,
        n_features_A=len(feature_names),
        n_rows_A=len(A_data),
        n_rows_B=len(B_data),
        min_rows_for_pca=min_rows_for_pca,
    )

    # Step 1: center A independently.
    A_centered = A_data[feature_names] - A_data[feature_names].mean()

    # Step 2: fit PCA on A.
    pca_A = PCA(n_components=selected_m)
    pca_A.fit(A_centered)
    pca_A_frame = pca_A.components_
    pca_A_variance_ratio = pca_A.explained_variance_ratio_

    # Step 3: center B independently (NOT with A's mean).
    B_centered = B_data[feature_names] - B_data[feature_names].mean()

    # Step 4: manually project B into A's PCA space.
    B_projected = np.matmul(B_centered.to_numpy(), pca_A_frame.transpose())

    # Step 5: fit PCA on the projected B.
    pca_B = PCA(n_components=selected_m)
    pca_B.fit(B_projected)
    pca_B_frame = pca_B.components_
    pca_B_variance_ratio = pca_B.explained_variance_ratio_

    # Step 6: re-express B loadings in the original feature space.
    B_reprojected_loadings = np.matmul(pca_B_frame, pca_A_frame)

    A_abs_loadings = np.abs(pca_A_frame)
    B_abs_loadings = np.abs(B_reprojected_loadings)

    # Step 7: axis-level JcvPCA.
    jcvpca_axis = B_abs_loadings - A_abs_loadings

    return {
        "feature_names": list(feature_names),
        "selected_m": int(selected_m),
        "variance_threshold": float(variance_threshold),
        "pca_A_frame": pca_A_frame,
        "pca_A_variance_ratio": pca_A_variance_ratio,
        "pca_B_variance_ratio": pca_B_variance_ratio,
        "A_abs_loadings": A_abs_loadings,
        "B_abs_loadings": B_abs_loadings,
        "jcvpca_axis": jcvpca_axis,
        "explained_variance_table_A": evr_table_full,
    }


def aggregate_axis_to_link_rss(
    A_abs_loadings: np.ndarray,
    B_abs_loadings: np.ndarray,
    feature_names: list[str],
    joint_link_map: dict[str, dict[str, str]],
    pca_A_variance_ratio: np.ndarray | None = None,
    export_weighted: bool = False,
) -> pd.DataFrame:
    """RSS link magnitudes per PC: JcvPCA_link = JRW_B_link - JRW_A_link."""
    feature_index = {feat: i for i, feat in enumerate(feature_names)}
    selected_m = A_abs_loadings.shape[0]

    rows: list[dict] = []
    for pc in range(selected_m):
        for link_id, axes in joint_link_map.items():
            axis_indices = [feature_index[axes[a]] for a in ("rx", "ry", "rz")]
            jrw_a = float(np.sqrt(np.sum(A_abs_loadings[pc, axis_indices] ** 2)))
            jrw_b = float(np.sqrt(np.sum(B_abs_loadings[pc, axis_indices] ** 2)))
            row = {
                "pc": pc + 1,
                "link_id": link_id,
                "JRW_A_link": jrw_a,
                "JRW_B_link": jrw_b,
                "JcvPCA_link": jrw_b - jrw_a,
            }
            if export_weighted:
                if pca_A_variance_ratio is None:
                    raise ValueError("export_weighted=True requires pca_A_variance_ratio.")
                weight = float(pca_A_variance_ratio[pc])
                row["weight_A_variance_ratio"] = weight
                row["weighted_JcvPCA_link"] = (jrw_b - jrw_a) * weight
            rows.append(row)

    return pd.DataFrame(rows)


def build_axis_table(
    A_abs_loadings: np.ndarray,
    B_abs_loadings: np.ndarray,
    jcvpca_axis: np.ndarray,
    feature_names: list[str],
    pca_A_variance_ratio: np.ndarray,
    pca_B_variance_ratio: np.ndarray,
    export_weighted: bool = False,
) -> pd.DataFrame:
    """Long-format axis-level table for one comparison."""
    selected_m = A_abs_loadings.shape[0]
    rows: list[dict] = []
    for pc in range(selected_m):
        for j, feat in enumerate(feature_names):
            row = {
                "pc": pc + 1,
                "feature": feat,
                "link_id": link_id_of(feat),
                "axis": axis_of(feat),
                "loading_A_abs": float(A_abs_loadings[pc, j]),
                "loading_B_reprojected_abs": float(B_abs_loadings[pc, j]),
                "jcvpca_axis": float(jcvpca_axis[pc, j]),
                "explained_variance_A": float(pca_A_variance_ratio[pc]),
                "explained_variance_B_projected": float(pca_B_variance_ratio[pc]),
            }
            if export_weighted:
                row["weighted_jcvpca_axis"] = float(jcvpca_axis[pc, j] * pca_A_variance_ratio[pc])
            rows.append(row)
    return pd.DataFrame(rows)


# --- END SACRED CORE ---


# --- clean rewritten orchestration on top of the core ---

@dataclass
class ComparisonResult:
    """One JcvPCA comparison (B against reference A) with all rollups."""

    comparison_id: str            # e.g. "671_T1_vs_T3_group4"
    kind: str                     # "longitudinal" | "natural_variability" | "exploratory"
    a_label: str
    b_label: str
    selected_m: int
    variance_threshold: float
    feature_names: list[str] = field(default_factory=list)
    axis_table: pd.DataFrame = field(default_factory=pd.DataFrame)
    link_table: pd.DataFrame = field(default_factory=pd.DataFrame)
    region_table: pd.DataFrame = field(default_factory=pd.DataFrame)
    space_table: pd.DataFrame = field(default_factory=pd.DataFrame)
    evr_table: pd.DataFrame = field(default_factory=pd.DataFrame)
    included_links: list[str] = field(default_factory=list)
    excluded_links: dict[str, str] = field(default_factory=dict)  # link -> reason
    warnings: list[str] = field(default_factory=list)


def region_rollup(link_table: pd.DataFrame, region_of_link) -> pd.DataFrame:
    """Aggregate link-level JcvPCA to body regions (mean of link deltas per PC)."""
    df = link_table.copy()
    df["region"] = df["link_id"].map(region_of_link)
    return (
        df.groupby(["pc", "region"], as_index=False)
        .agg(
            JRW_A_region=("JRW_A_link", "mean"),
            JRW_B_region=("JRW_B_link", "mean"),
            JcvPCA_region=("JcvPCA_link", "mean"),
            n_links=("link_id", "count"),
        )
        .sort_values(["pc", "region"])
        .reset_index(drop=True)
    )


def functional_null_split(link_table: pd.DataFrame, sensitivity_p: int) -> pd.DataFrame:
    """Split link deltas into functional (PC1..p) vs null space (PC(p+1)..m)."""
    df = link_table.copy()
    df["space"] = np.where(df["pc"] <= sensitivity_p, "functional", "null")
    return (
        df.groupby(["space", "link_id"], as_index=False)
        .agg(
            JcvPCA_mean=("JcvPCA_link", "mean"),
            JcvPCA_abs_mean=("JcvPCA_link", lambda s: float(np.mean(np.abs(s)))),
            n_pcs=("pc", "count"),
        )
        .sort_values(["space", "link_id"])
        .reset_index(drop=True)
    )


def restrict_to_shared_features(
    a_df: pd.DataFrame,
    b_df: pd.DataFrame,
    requested_features: list[str],
) -> tuple[list[str], dict[str, str], list[str]]:
    """Restrict features to those with complete rx/ry/rz triplets in BOTH matrices.

    Returns (kept_features, excluded_links_with_reason, warnings).
    Used for the 671 T1-vs-T3 marker-set case (decision 2): never hard-block,
    restrict to the shared valid link intersection and record what was dropped.
    """
    warnings: list[str] = []
    excluded: dict[str, str] = {}
    link_map = build_joint_link_map(requested_features)
    kept: list[str] = []
    for link, axes in link_map.items():
        missing_axes = [ax for ax in REQUIRED_AXES if ax not in axes]
        if missing_axes:
            excluded[link] = f"incomplete axis triplet (missing {missing_axes})"
            continue
        cols = [axes[ax] for ax in REQUIRED_AXES]
        in_a = all(c in a_df.columns for c in cols)
        in_b = all(c in b_df.columns for c in cols)
        if not (in_a and in_b):
            where = "A" if not in_a else "B"
            excluded[link] = f"features missing in dataset {where}"
            continue
        a_ok = np.isfinite(a_df[cols].to_numpy(dtype=float)).all()
        b_ok = np.isfinite(b_df[cols].to_numpy(dtype=float)).all()
        if not (a_ok and b_ok):
            excluded[link] = "non-finite values in feature columns"
            continue
        kept.extend(cols)
    if excluded:
        warnings.append(
            f"{len(excluded)} link(s) excluded from this comparison; analysis restricted "
            f"to the shared valid link intersection ({len(kept) // 3} links)."
        )
    return kept, excluded, warnings


def run_comparison(
    comparison_id: str,
    kind: str,
    a_label: str,
    b_label: str,
    a_df: pd.DataFrame,
    b_df: pd.DataFrame,
    feature_names: list[str],
    variance_threshold: float,
    region_of_link=None,
    sensitivity_p: int = 2,
    min_rows_for_pca: int = 10,
    export_weighted: bool = False,
    pre_excluded_links: dict[str, str] | None = None,
) -> ComparisonResult:
    """Run one full comparison: core -> axis/link tables -> region + space rollups."""
    pre_excluded_links = dict(pre_excluded_links or {})
    drop_stems = set(pre_excluded_links)
    filtered_features = [
        f for f in feature_names if link_id_of(f) not in drop_stems
    ]
    kept, excluded, warnings = restrict_to_shared_features(a_df, b_df, filtered_features)
    merged_excluded = dict(pre_excluded_links)
    for link, reason in excluded.items():
        merged_excluded.setdefault(link, reason)
    if pre_excluded_links:
        warnings = list(warnings)
        warnings.append(
            f"{len(pre_excluded_links)} link(s) excluded by marker-gap policy "
            f"before shared-link restriction."
        )
    if not kept:
        raise ValidationError(
            f"{comparison_id}: no shared valid links between {a_label} and {b_label}.",
            report={"excluded_links": merged_excluded},
        )

    result = compute_jcvpca(
        a_df,
        b_df,
        kept,
        variance_threshold=variance_threshold,
        min_rows_for_pca=min_rows_for_pca,
    )
    link_map = build_joint_link_map(kept)
    link_table = aggregate_axis_to_link_rss(
        result["A_abs_loadings"],
        result["B_abs_loadings"],
        kept,
        link_map,
        pca_A_variance_ratio=result["pca_A_variance_ratio"] if export_weighted else None,
        export_weighted=export_weighted,
    )
    axis_table = build_axis_table(
        result["A_abs_loadings"],
        result["B_abs_loadings"],
        result["jcvpca_axis"],
        kept,
        result["pca_A_variance_ratio"],
        result["pca_B_variance_ratio"],
        export_weighted=export_weighted,
    )
    region_table = (
        region_rollup(link_table, region_of_link) if region_of_link else pd.DataFrame()
    )
    space_table = functional_null_split(link_table, sensitivity_p)

    return ComparisonResult(
        comparison_id=comparison_id,
        kind=kind,
        a_label=a_label,
        b_label=b_label,
        selected_m=result["selected_m"],
        variance_threshold=result["variance_threshold"],
        feature_names=kept,
        axis_table=axis_table,
        link_table=link_table,
        region_table=region_table,
        space_table=space_table,
        evr_table=result["explained_variance_table_A"],
        included_links=list(link_map.keys()),
        excluded_links=merged_excluded,
        warnings=warnings,
    )


def threshold_sweep(
    a_df: pd.DataFrame,
    b_df: pd.DataFrame,
    feature_names: list[str],
    candidates: list[float],
    min_rows_for_pca: int = 10,
) -> pd.DataFrame:
    """Diagnostic: how selected_m and top-link ranking shift across thresholds.

    Returns one row per candidate threshold with selected_m and the top-3 links by
    mean |JcvPCA_link| so threshold robustness can be judged (decision 1).
    """
    kept, _, _ = restrict_to_shared_features(a_df, b_df, feature_names)
    link_map = build_joint_link_map(kept)
    rows = []
    for threshold in candidates:
        result = compute_jcvpca(
            a_df, b_df, kept, variance_threshold=threshold, min_rows_for_pca=min_rows_for_pca
        )
        link_table = aggregate_axis_to_link_rss(
            result["A_abs_loadings"], result["B_abs_loadings"], kept, link_map
        )
        ranking = (
            link_table.assign(absd=link_table["JcvPCA_link"].abs())
            .groupby("link_id")["absd"]
            .mean()
            .sort_values(ascending=False)
        )
        rows.append(
            {
                "variance_threshold": float(threshold),
                "selected_m": int(result["selected_m"]),
                "top1_link": ranking.index[0] if len(ranking) > 0 else "",
                "top2_link": ranking.index[1] if len(ranking) > 1 else "",
                "top3_link": ranking.index[2] if len(ranking) > 2 else "",
                "top1_mean_abs_delta": float(ranking.iloc[0]) if len(ranking) else np.nan,
            }
        )
    return pd.DataFrame(rows)
