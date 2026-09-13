"""Step 4b — merged robustness table (k-grid, repetition-mode, QC-drop).

Usage:
  PYTHONPATH=src .venv/bin/python scripts/run_step04b_robustness.py
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca import jcvpca, pipeline, validation
from gaga_jcvpca.config import load_config
from gaga_jcvpca.selection import load_selection, region_of_link

PARTICIPANTS = ("671", "252", "651", "790")
WINDOW = "ex09_13_contiguous"
K_GRID = [4, 5, 6, 7, 8, 9, 10]
TOP_K = 5
OVERLAP_THRESHOLD = 0.60  # heuristic: 3/5
EVR_FUNCTIONAL_50 = 0.50
EVR_FUNCTIONAL_60 = 0.60


def _top5_from_pc_band(
    link_table: pd.DataFrame, max_pc: int | None = None
) -> tuple[list[str], pd.Series]:
    sub = link_table if max_pc is None else link_table[link_table["pc"] <= max_pc]
    means = sub.groupby("link_id")["JcvPCA_link"].mean()
    ranked = means.abs().sort_values(ascending=False)
    return list(ranked.index[:TOP_K]), means


def _top5(link_table: pd.DataFrame) -> tuple[list[str], pd.Series]:
    return _top5_from_pc_band(link_table, max_pc=None)


def _pc_band_sizes(evr: np.ndarray, selected_m: int) -> dict[str, int | float]:
    evr = np.asarray(evr, dtype=float)[:selected_m]
    cum = np.cumsum(evr)

    def _p_at(th: float) -> int:
        return int(min(selected_m, np.searchsorted(cum, th) + 1))

    p50 = _p_at(EVR_FUNCTIONAL_50)
    p60 = _p_at(EVR_FUNCTIONAL_60)
    return {
        "evr_pc1": round(float(evr[0]), 4) if len(evr) else float("nan"),
        "evr_pc1_pc2": round(float(cum[1]), 4) if len(cum) > 1 else round(float(cum[0]), 4),
        "p_functional_50": p50,
        "p_functional_60": p60,
        "selected_m": int(selected_m),
    }


def _jcvpca_result(
    a_df: pd.DataFrame,
    b_df: pd.DataFrame,
    features: list[str],
    vt: float,
    selected_m: int | None,
) -> tuple[pd.DataFrame, dict]:
    kept, _, _ = jcvpca.restrict_to_shared_features(a_df, b_df, features)
    if not kept:
        raise jcvpca.ValidationError("no shared features")
    result = jcvpca.compute_jcvpca(
        a_df, b_df, kept, variance_threshold=vt, selected_m=selected_m
    )
    link_map = jcvpca.build_joint_link_map(kept)
    lt = jcvpca.aggregate_axis_to_link_rss(
        result["A_abs_loadings"],
        result["B_abs_loadings"],
        kept,
        link_map,
        pca_A_variance_ratio=result["pca_A_variance_ratio"],
    )
    meta = _pc_band_sizes(result["pca_A_variance_ratio"], int(result["selected_m"]))
    return lt, meta


def _overlap(primary_top: list[str], other_top: list[str]) -> float:
    if not primary_top:
        return 0.0
    return len(set(primary_top) & set(other_top)) / len(primary_top)


def _functional_chain_retained(
    primary_top: list[str],
    other_top: list[str],
    primary_means: pd.Series,
    other_means: pd.Series,
    config,
) -> str:
    if not primary_top or not other_top:
        return "not"
    overlap = set(primary_top) & set(other_top)
    if not overlap:
        return "not"
    same_sign = sum(
        1
        for link in overlap
        if np.sign(primary_means.get(link, 0)) == np.sign(other_means.get(link, 0))
    )
    primary_chains = {region_of_link(l, config) for l in primary_top}
    other_chains = {region_of_link(l, config) for l in other_top}
    chain_ok = len(primary_chains & other_chains) >= min(3, len(primary_chains))
    if same_sign >= max(1, len(overlap) // 2) and chain_ok:
        return "retained"
    return "not"


def _link_table(
    a_df: pd.DataFrame,
    b_df: pd.DataFrame,
    features: list[str],
    vt: float,
    selected_m: int | None,
) -> tuple[pd.DataFrame, int]:
    lt, meta = _jcvpca_result(a_df, b_df, features, vt, selected_m)
    return lt, int(meta["selected_m"])


def _side_matrices(
    config,
    selection,
    timepoint: str,
    repetition_mode: str,
    rep: str = "R1",
) -> pd.DataFrame | None:
    participant = selection.participant
    task_part = config.get("mode.task_part", "P1")
    reps = ["R1", "R2"]
    segments = pipeline._segments_by_session(config)

    def _get(session_id: str):
        df = pipeline.load_matrix(config, session_id)
        if df is None:
            return None
        return pipeline.slice_matrix_to_exercises(
            df, segments.get(session_id, []), selection.exercise_ids
        )

    if repetition_mode == "pooled":
        frames = [
            _get(pipeline._timepoint_session(participant, timepoint, r, task_part))
            for r in reps
        ]
        frames = [f for f in frames if f is not None]
        return pd.concat(frames, ignore_index=True) if frames else None
    return _get(
        pipeline._timepoint_session(participant, timepoint, rep, task_part)
    )


def _caution_links(selection_path: Path) -> list[str]:
    with open(selection_path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return [
        l["link"]
        for l in data.get("links", [])
        if l.get("qc_recommendation") == "include_with_caution" and l.get("included")
    ]


def _robustness_label(k_overlaps: list[float], rep_overlap: float, qc_overlap: float) -> str:
    k_median = float(np.median(k_overlaps)) if k_overlaps else 0.0
    scores = [
        k_median >= OVERLAP_THRESHOLD,
        rep_overlap >= OVERLAP_THRESHOLD,
        qc_overlap >= OVERLAP_THRESHOLD,
    ]
    if all(scores):
        return "stable"
    if any(scores):
        return "partial"
    return "unstable"


def run_single_rep(config, participant: str, out_root: Path) -> Path:
    sel_name = f"{participant}_{WINDOW}"
    selection = load_selection(config.resolve_path("outputs.root") / "selections" / f"{sel_name}.yaml")
    run_id = f"{participant}_{WINDOW}_single"
    run_dir = pipeline.run_analysis(
        config,
        selection,
        timepoints=["T1", "T2", "T3"],
        repetitions=["R1", "R2"],
        reference_timepoint="T1",
        repetition_mode="single",
        run_validation=False,
        run_id=run_id,
    )
    dst = out_root / participant / f"{WINDOW}_single"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(run_dir, dst)
    return dst


def _empty_rep_diagnostics() -> dict:
    return {
        "pooled_vs_r1_overlap": "",
        "pooled_vs_r2_overlap": "",
        "longitudinal_r1_vs_r2_overlap": "",
        "pooled_vs_r1_overlap_p50": "",
        "pooled_vs_r1_overlap_p60": "",
        "pooled_vs_r2_overlap_p50": "",
        "pooled_vs_r2_overlap_p60": "",
    }


def _rep_row_base(
    participant: str,
    comp_id: str,
    primary_m: int,
    rep_overlap: float,
    rep_overlap_r2: float,
    r1_vs_r2_overlap: float,
    functional_chain: str,
    *,
    rep_overlap_p50: float = 0.0,
    rep_overlap_p60: float = 0.0,
    rep_overlap_r2_p50: float = 0.0,
    rep_overlap_r2_p60: float = 0.0,
) -> dict:
    return {
        "participant": participant,
        "comparison_id": comp_id,
        "axis": "repetition_mode",
        "axis_detail": "pooled_vs_single",
        "primary_m": primary_m,
        "selected_m": primary_m,
        "top5_overlap": round(rep_overlap, 3),
        "pooled_vs_r1_overlap": round(rep_overlap, 3),
        "pooled_vs_r2_overlap": round(rep_overlap_r2, 3),
        "longitudinal_r1_vs_r2_overlap": round(r1_vs_r2_overlap, 3),
        "pooled_vs_r1_overlap_p50": round(rep_overlap_p50, 3),
        "pooled_vs_r1_overlap_p60": round(rep_overlap_p60, 3),
        "pooled_vs_r2_overlap_p50": round(rep_overlap_r2_p50, 3),
        "pooled_vs_r2_overlap_p60": round(rep_overlap_r2_p60, 3),
        "functional_chain_retained": functional_chain,
        "robustness_label": "",
    }


def build_functional_pc_bands(
    config,
    participant: str,
    pooled_dir: Path,
) -> list[dict]:
    sel_name = f"{participant}_{WINDOW}"
    selection = load_selection(
        config.resolve_path("outputs.root") / "selections" / f"{sel_name}.yaml"
    )
    features = selection.feature_columns()
    vt = float(config.get("pca.variance_threshold", 0.80))
    sm_df = pd.read_csv(pooled_dir / "selected_m_by_comparison.csv")
    link_lt = pd.read_csv(pooled_dir / "link_level_results.csv")
    long_ids = [
        cid
        for cid in sm_df["comparison_id"]
        if "_T1_vs_T" in cid and cid.endswith(("T2", "T3"))
    ]

    rows: list[dict] = []
    for comp_id in long_ids:
        tp = "T2" if comp_id.endswith("T2") else "T3"
        primary_m = int(sm_df.loc[sm_df["comparison_id"] == comp_id, "selected_m"].iloc[0])
        sub = link_lt[link_lt["comparison_id"] == comp_id]
        primary_top, primary_means = _top5(sub)

        a_pooled = _side_matrices(config, selection, "T1", "pooled")
        b_pooled = _side_matrices(config, selection, tp, "pooled")
        try:
            _, meta = _jcvpca_result(a_pooled, b_pooled, features, vt, primary_m)
        except jcvpca.ValidationError:
            continue

        p50 = int(meta["p_functional_50"])
        p60 = int(meta["p_functional_60"])
        top_p50, _ = _top5_from_pc_band(sub, p50)
        top_p60, _ = _top5_from_pc_band(sub, p60)

        rows.append(
            {
                "participant": participant,
                "comparison_id": comp_id,
                **meta,
                "top5_all_pcs": ",".join(primary_top),
                "top5_p_functional_50": ",".join(top_p50),
                "top5_p_functional_60": ",".join(top_p60),
                "overlap_all_vs_p50": round(_overlap(primary_top, top_p50), 3),
                "overlap_all_vs_p60": round(_overlap(primary_top, top_p60), 3),
                "overlap_p50_vs_p60": round(_overlap(top_p50, top_p60), 3),
            }
        )
    return rows


def build_robustness_for_participant(
    config,
    participant: str,
    pooled_dir: Path,
    single_dir: Path,
    step3_sel: Path,
) -> list[dict]:
    sel_name = f"{participant}_{WINDOW}"
    selection = load_selection(config.resolve_path("outputs.root") / "selections" / f"{sel_name}.yaml")
    features = selection.feature_columns()
    vt = float(config.get("pca.variance_threshold", 0.80))
    caution = _caution_links(step3_sel)

    rows: list[dict] = []
    sm_df = pd.read_csv(pooled_dir / "selected_m_by_comparison.csv")
    long_ids = [
        cid
        for cid in sm_df["comparison_id"]
        if "_T1_vs_T" in cid and cid.endswith(("T2", "T3"))
    ]

    for comp_id in long_ids:
        tp = "T2" if comp_id.endswith("T2") else "T3"
        primary_m = int(sm_df.loc[sm_df["comparison_id"] == comp_id, "selected_m"].iloc[0])

        primary_lt = pd.read_csv(pooled_dir / "link_level_results.csv")
        primary_lt = primary_lt[primary_lt["comparison_id"] == comp_id]
        primary_top, primary_means = _top5(primary_lt)

        a_pooled = _side_matrices(config, selection, "T1", "pooled")
        b_pooled = _side_matrices(config, selection, tp, "pooled")
        a_r1 = _side_matrices(config, selection, "T1", "single", rep="R1")
        b_r1 = _side_matrices(config, selection, tp, "single", rep="R1")
        a_r2 = _side_matrices(config, selection, "T1", "single", rep="R2")
        b_r2 = _side_matrices(config, selection, tp, "single", rep="R2")

        k_overlaps: list[float] = []

        # Axis 1: k-grid
        for k in K_GRID:
            try:
                lt_k, _ = _link_table(a_pooled, b_pooled, features, vt, selected_m=k)
                top_k, means_k = _top5(lt_k)
                ov = _overlap(primary_top, top_k)
                k_overlaps.append(ov)
                rows.append(
                    {
                        "participant": participant,
                        "comparison_id": comp_id,
                        "axis": "k_grid",
                        "axis_detail": k,
                        "primary_m": primary_m,
                        "selected_m": k,
                        "top5_overlap": round(ov, 3),
                        **_empty_rep_diagnostics(),
                        "functional_chain_retained": _functional_chain_retained(
                            primary_top, top_k, primary_means, means_k, config
                        ),
                        "robustness_label": "",
                    }
                )
            except jcvpca.ValidationError:
                rows.append(
                    {
                        "participant": participant,
                        "comparison_id": comp_id,
                        "axis": "k_grid",
                        "axis_detail": k,
                        "primary_m": primary_m,
                        "selected_m": k,
                        "top5_overlap": 0.0,
                        **_empty_rep_diagnostics(),
                        "functional_chain_retained": "not",
                        "robustness_label": "",
                    }
                )

        # Axis 2: repetition mode (pooled vs R1, plus diagnostics)
        rep_overlap = 0.0
        rep_overlap_r2 = 0.0
        r1_vs_r2_overlap = 0.0
        rep_overlap_p50 = 0.0
        rep_overlap_p60 = 0.0
        rep_overlap_r2_p50 = 0.0
        rep_overlap_r2_p60 = 0.0
        try:
            _, band_meta = _jcvpca_result(a_pooled, b_pooled, features, vt, primary_m)
            p50 = int(band_meta["p_functional_50"])
            p60 = int(band_meta["p_functional_60"])
            primary_top_p50, _ = _top5_from_pc_band(primary_lt, p50)
            primary_top_p60, _ = _top5_from_pc_band(primary_lt, p60)

            single_lt = pd.read_csv(single_dir / "link_level_results.csv")
            single_lt = single_lt[single_lt["comparison_id"] == comp_id]
            single_top, single_means = _top5(single_lt)
            rep_overlap = _overlap(primary_top, single_top)
            single_top_p50, _ = _top5_from_pc_band(single_lt, p50)
            single_top_p60, _ = _top5_from_pc_band(single_lt, p60)
            rep_overlap_p50 = _overlap(primary_top_p50, single_top_p50)
            rep_overlap_p60 = _overlap(primary_top_p60, single_top_p60)

            if a_r2 is not None and b_r2 is not None:
                lt_r2, _ = _link_table(a_r2, b_r2, features, vt, selected_m=primary_m)
                top_r2, means_r2 = _top5(lt_r2)
                rep_overlap_r2 = _overlap(primary_top, top_r2)
                top_r2_p50, _ = _top5_from_pc_band(lt_r2, p50)
                top_r2_p60, _ = _top5_from_pc_band(lt_r2, p60)
                rep_overlap_r2_p50 = _overlap(primary_top_p50, top_r2_p50)
                rep_overlap_r2_p60 = _overlap(primary_top_p60, top_r2_p60)
            else:
                top_r2, means_r2 = [], pd.Series(dtype=float)

            if a_r1 is not None and b_r1 is not None and a_r2 is not None and b_r2 is not None:
                lt_r1_run, _ = _link_table(a_r1, b_r1, features, vt, selected_m=primary_m)
                top_r1_run, _ = _top5(lt_r1_run)
                if top_r2:
                    r1_vs_r2_overlap = _overlap(top_r1_run, top_r2)

            rows.append(
                _rep_row_base(
                    participant,
                    comp_id,
                    primary_m,
                    rep_overlap,
                    rep_overlap_r2,
                    r1_vs_r2_overlap,
                    _functional_chain_retained(
                        primary_top, single_top, primary_means, single_means, config
                    ),
                    rep_overlap_p50=rep_overlap_p50,
                    rep_overlap_p60=rep_overlap_p60,
                    rep_overlap_r2_p50=rep_overlap_r2_p50,
                    rep_overlap_r2_p60=rep_overlap_r2_p60,
                )
            )
        except Exception:
            rows.append(
                {
                    **_rep_row_base(participant, comp_id, primary_m, 0.0, 0.0, 0.0, "not"),
                    "selected_m": "",
                    "top5_overlap": 0.0,
                    "pooled_vs_r1_overlap": 0.0,
                    "pooled_vs_r2_overlap": 0.0,
                    "longitudinal_r1_vs_r2_overlap": 0.0,
                    "pooled_vs_r1_overlap_p50": 0.0,
                    "pooled_vs_r1_overlap_p60": 0.0,
                    "pooled_vs_r2_overlap_p50": 0.0,
                    "pooled_vs_r2_overlap_p60": 0.0,
                }
            )

        # Axis 3: QC-drop (exclude caution links)
        qc_overlap = 0.0
        if caution:
            drop_feats = [f for f in features if jcvpca.link_id_of(f) not in caution]
            try:
                concs = validation.sensitivity_analysis(
                    a_pooled, b_pooled, drop_feats, vt, drop_links=caution, top_n=TOP_K
                )
                qc_overlap = float(concs[0].value) if concs else 0.0
                # re-run for functional chain
                lt_qc, _ = _link_table(a_pooled, b_pooled, drop_feats, vt, selected_m=None)
                top_qc, means_qc = _top5(lt_qc)
                rows.append(
                    {
                        "participant": participant,
                        "comparison_id": comp_id,
                        "axis": "qc_drop",
                        "axis_detail": f"drop_{len(caution)}_caution",
                        "primary_m": primary_m,
                        "selected_m": primary_m,
                        "top5_overlap": round(qc_overlap, 3),
                        **_empty_rep_diagnostics(),
                        "functional_chain_retained": _functional_chain_retained(
                            primary_top, top_qc, primary_means, means_qc, config
                        ),
                        "robustness_label": _robustness_label(k_overlaps, rep_overlap, qc_overlap),
                    }
                )
            except Exception:
                rows.append(
                    {
                        "participant": participant,
                        "comparison_id": comp_id,
                        "axis": "qc_drop",
                        "axis_detail": f"drop_{len(caution)}_caution",
                        "primary_m": primary_m,
                        "selected_m": primary_m,
                        "top5_overlap": 0.0,
                        **_empty_rep_diagnostics(),
                        "functional_chain_retained": "not",
                        "robustness_label": "unstable",
                    }
                )
        else:
            rows.append(
                {
                    "participant": participant,
                    "comparison_id": comp_id,
                    "axis": "qc_drop",
                    "axis_detail": "no_caution_links",
                    "primary_m": primary_m,
                    "selected_m": primary_m,
                    "top5_overlap": 1.0,
                    **_empty_rep_diagnostics(),
                    "functional_chain_retained": "retained",
                    "robustness_label": _robustness_label(k_overlaps, rep_overlap, 1.0),
                }
            )

    return rows


def write_framework_md(path: Path) -> None:
    path.write_text(
        """# Robustness framework — Step 4b (v5 + extensions)

Tests stability of the primary `ex09_13_contiguous` **pooled** result under perturbations — not alternate exercise windows.

## Axes (`robustness.csv`)

| Axis | Primary | Perturbation | Metric |
|---|---|---|---|
| **k_grid** | T1 pooled A; m from 80% EVR | Fixed k ∈ [4…10] | top-5 overlap vs primary at `primary_m` |
| **repetition_mode** | pooled T1 vs T2/T3 | single T1 R1 vs T2/T3 R1 | `top5_overlap` (= `pooled_vs_r1_overlap`) |
| **qc_drop** | full feasible link set | drop `include_with_caution` links only | top-5 overlap via sensitivity_analysis |

### Repetition diagnostics (on `repetition_mode` rows only)

| Column | Meaning |
|---|---|
| `pooled_vs_r1_overlap` | Same as `top5_overlap` — pooled vs R1-only longitudinal |
| `pooled_vs_r2_overlap` | pooled vs R2-only longitudinal top-5 overlap |
| `longitudinal_r1_vs_r2_overlap` | R1-only vs R2-only longitudinal top-5 overlap |
| `pooled_vs_r1_overlap_p50` / `_p60` | Same as above, top-5 from PCs 1…`p_functional_50` / `p_functional_60` (T1 EVR from pooled fit) |
| `pooled_vs_r2_overlap_p50` / `_p60` | R2-only band overlaps (same PC cutoffs) |

Diagnostics inform interpretation; they **do not** change `robustness_label`.

## Functional PC bands (`functional_pc_bands.csv`)

Separate table per participant × comparison:

| Field | Meaning |
|---|---|
| `p_functional_50` / `p_functional_60` | PCs needed for 50% / 60% T1 cumulative EVR |
| `overlap_all_vs_p50` / `overlap_all_vs_p60` | Top-5 stability: all PCs vs each EVR band |
| `overlap_p50_vs_p60` | Agreement between 50% and 60% band rankings |
| `top5_p_functional_50`, `top5_p_functional_60`, … | Ranked link lists per band |

Label PCs `p_functional_50+1 … selected_m` as **secondary** in committee docs (not "null").
Note: per-run `functional_space_results.csv` still uses config `sensitivity_p=2`; this table uses EVR bands only.

## Heuristic labels (not p-values)

- **top5_overlap** ≥ 0.60 (≥3/5 links) → stable axis
- **functional_chain_retained** — dominant arm/trunk/leg chains keep representation + sign agreement on overlap
- **robustness_label** (per comparison, on qc_drop row): `stable` if k-grid median, pooled↔R1, and qc-drop all pass; `partial` if some pass; `unstable` otherwise

## Removed (v5)

EVR threshold sweep (subsumed by k-grid), basis-similarity cosine, bootstrap CIs as stability gates.

See `docs/MASTER_EXECUTION_PLAN.md` Step 4b for full spec.
""",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-single-runs", action="store_true")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "results_committee_case" / "step04_primary_runs",
        help="Committee-case folder with pooled/single runs and robustness tables",
    )
    args = parser.parse_args()

    config = load_config()
    out_root = args.output_root.resolve()
    step3_sel_dir = ROOT / "results_committee_case" / "step03_trunk_extension" / "selections"

    all_rows: list[dict] = []
    band_rows: list[dict] = []
    for pid in PARTICIPANTS:
        print(f"\n=== {pid} ===")
        if not args.skip_single_runs:
            print("  single-rep run...")
            run_single_rep(config, pid, out_root)

        pooled_dir = out_root / pid / f"{WINDOW}_pooled"
        single_dir = out_root / pid / f"{WINDOW}_single"
        step3_sel = step3_sel_dir / f"{pid}_{WINDOW}.yaml"

        print("  robustness metrics...")
        rows = build_robustness_for_participant(
            config, pid, pooled_dir, single_dir, step3_sel
        )
        all_rows.extend(rows)
        print("  functional PC bands...")
        band_rows.extend(build_functional_pc_bands(config, pid, pooled_dir))

    df = pd.DataFrame(all_rows)
    csv_path = out_root / "robustness.csv"
    df.to_csv(csv_path, index=False)
    bands_path = out_root / "functional_pc_bands.csv"
    pd.DataFrame(band_rows).to_csv(bands_path, index=False)
    write_framework_md(out_root / "ROBUSTNESS_FRAMEWORK.md")

    # summary print
    summary = df[df["robustness_label"] != ""][["participant", "comparison_id", "robustness_label"]]
    rep = df[df["axis"] == "repetition_mode"][
        [
            "participant",
            "comparison_id",
            "pooled_vs_r1_overlap",
            "pooled_vs_r1_overlap_p50",
            "pooled_vs_r1_overlap_p60",
            "pooled_vs_r2_overlap",
            "pooled_vs_r2_overlap_p50",
            "pooled_vs_r2_overlap_p60",
            "longitudinal_r1_vs_r2_overlap",
        ]
    ]
    print(f"\nWrote {csv_path.relative_to(ROOT)} ({len(df)} rows)")
    print(f"Wrote {bands_path.relative_to(ROOT)} ({len(band_rows)} rows)")
    print(summary.to_string(index=False))
    print("\nRepetition diagnostics:")
    print(rep.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
