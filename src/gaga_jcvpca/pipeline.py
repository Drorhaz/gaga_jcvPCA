"""Pipeline orchestration + the single read model the UI consumes.

Later phases extend this with QC, rotation-vector conversion, selection, JcvPCA,
validation, and reporting. For now it exposes a project snapshot built from the
Inventory so the dashboard has one source of truth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pandas as pd

from gaga_jcvpca import jcvpca, qc_markers, reporting, validation
from gaga_jcvpca.config import Config, load_config
from gaga_jcvpca.inventory import Inventory, build_inventory
from gaga_jcvpca.schemas import QCFinding
from gaga_jcvpca.selection import AnalysisSelection, region_of_link


@dataclass
class ProjectSnapshot:
    """Everything the dashboard needs about current project state (read-only)."""

    config: Config
    inventory: Inventory
    science_hash: str = ""
    recommended_next_action: str = ""
    qc_findings: list[QCFinding] = field(default_factory=list)
    qc_summary_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    qc_summary: dict = field(default_factory=dict)
    qc_parse_warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> dict:
        base = self.inventory.summary()
        base.update(self.qc_summary)
        return base


def _recommend_next_action(inv: Inventory, qc_summary: dict) -> str:
    n_marker_sessions = sum(1 for r in inv.rows if r.has_marker_csv)
    if not inv.rows:
        return "No sessions discovered. Add segmentation workbooks and raw captures to data/."
    if n_marker_sessions == 0:
        return (
            "No marker CSV files found. Set data.raw_markers or data.raw_skeleton in "
            "configs/paths.yaml (expected layout: data/raw_markers/{participant}/), "
            "then open Tab 3 for QC review."
        )
    ready = [r for r in inv.rows if r.status == "ready"]
    if not ready:
        return (
            "Marker files are present but sessions are not analysis-ready "
            "(need segmentation sheet + skeleton CSV). Review Tab 2 inventory."
        )
    if qc_summary.get("n_findings", 0) == 0:
        return "Review QC in Tab 3, then build an analysis selection and run JcvPCA."
    return "Review QC in Tab 3, then build an analysis selection and run JcvPCA."


def build_snapshot(config: Optional[Config] = None) -> ProjectSnapshot:
    cfg = config or load_config()
    inv = build_inventory(cfg)
    qc_findings: list[QCFinding] = []
    qc_df = pd.DataFrame()
    parse_warnings: list[str] = []

    if any(r.has_marker_csv for r in inv.rows):
        qc_findings, qc_df = qc_markers.run_marker_qc(cfg, inv, write_cache=True)
        parse_warnings = [
            f.message for f in qc_findings if f.metric == "parse_error"
        ]

    qc_summary = qc_markers.summarize_qc_findings(qc_findings, inv)
    return ProjectSnapshot(
        config=cfg,
        inventory=inv,
        science_hash=cfg.science_hash,
        recommended_next_action=_recommend_next_action(inv, qc_summary),
        qc_findings=qc_findings,
        qc_summary_df=qc_df,
        qc_summary=qc_summary,
        qc_parse_warnings=parse_warnings,
    )


# --- analysis run orchestration (selection -> matrices -> comparisons -> report) ---

def load_matrix(config: Config, session_id: str) -> Optional[pd.DataFrame]:
    """Load a windowed rotation-vector feature matrix for a session, if present."""
    try:
        matrices_dir = config.resolve_path("data.matrices")
    except KeyError:
        return None
    path = matrices_dir / f"{session_id}.parquet"
    if path.exists():
        return pd.read_parquet(path)
    return None


def _timepoint_session(participant: str, timepoint: str, repetition: str, task_part: str = "P1") -> str:
    return f"{participant}_{timepoint}_{task_part}_{repetition}"


def run_analysis(
    config: Config,
    selection: AnalysisSelection,
    timepoints: list[str],
    repetitions: Optional[list[str]] = None,
    reference_timepoint: str = "T1",
    run_threshold_sweep: bool = False,
    run_validation: bool = False,
    run_id: Optional[str] = None,
    matrices: Optional[dict[str, pd.DataFrame]] = None,
) -> Path:
    """Run the full participant-specific analysis and write a run folder.

    ``matrices`` optionally supplies session_id -> feature DataFrame (used by the
    smoke test and UI). When omitted, matrices are loaded from ``data.matrices``.
    Returns the path to the written run folder.
    """
    repetitions = repetitions or ["R1", "R2"]
    participant = selection.participant
    task_part = config.get("mode.task_part", "P1")
    features = selection.feature_columns()
    vt = float(config.get("pca.variance_threshold", 0.80))
    sensitivity_p = int(config.get("pc_focus.sensitivity_p", 2))
    region_fn = lambda stem: region_of_link(stem, config)

    def _get(session_id: str) -> Optional[pd.DataFrame]:
        if matrices is not None:
            return matrices.get(session_id)
        return load_matrix(config, session_id)

    # Reference A = reference timepoint, R1 (fallback to first available rep).
    comparisons: list[jcvpca.ComparisonResult] = []
    input_sessions: list[str] = []

    ref_rep = repetitions[0]
    ref_id = _timepoint_session(participant, reference_timepoint, ref_rep, task_part)
    a_df = _get(ref_id)
    if a_df is None:
        raise FileNotFoundError(f"Reference matrix not found for {ref_id}.")
    input_sessions.append(ref_id)

    # Longitudinal comparisons: reference vs each other timepoint (same rep).
    for tp in timepoints:
        if tp == reference_timepoint:
            continue
        b_id = _timepoint_session(participant, tp, ref_rep, task_part)
        b_df = _get(b_id)
        if b_df is None:
            continue
        input_sessions.append(b_id)
        comparisons.append(
            jcvpca.run_comparison(
                f"{participant}_{reference_timepoint}_vs_{tp}",
                "longitudinal",
                ref_id,
                b_id,
                a_df,
                b_df,
                features,
                variance_threshold=vt,
                region_of_link=region_fn,
                sensitivity_p=sensitivity_p,
            )
        )

    # Natural variability: reference timepoint R1 vs R2.
    nv_comparison = None
    if len(repetitions) >= 2:
        r1_id = _timepoint_session(participant, reference_timepoint, repetitions[0], task_part)
        r2_id = _timepoint_session(participant, reference_timepoint, repetitions[1], task_part)
        r1_df, r2_df = _get(r1_id), _get(r2_id)
        if r1_df is not None and r2_df is not None:
            nv_comparison = jcvpca.run_comparison(
                f"{participant}_{reference_timepoint}_R1_vs_R2",
                "natural_variability",
                r1_id,
                r2_id,
                r1_df,
                r2_df,
                features,
                variance_threshold=vt,
                region_of_link=region_fn,
                sensitivity_p=sensitivity_p,
            )
            comparisons.append(nv_comparison)

    if not comparisons:
        raise FileNotFoundError(
            f"No comparison could be built for {participant}; check available matrices."
        )

    # Optional threshold sweep on the first longitudinal comparison.
    sweep_df = None
    if run_threshold_sweep:
        first_long = next((c for c in comparisons if c.kind == "longitudinal"), None)
        if first_long is not None:
            b_id = first_long.b_label
            sweep_df = jcvpca.threshold_sweep(
                a_df,
                _get(b_id),
                features,
                candidates=[float(x) for x in config.get("pca.threshold_sweep.candidates", [0.7, 0.8, 0.9])],
            )

    # Optional validation.
    validation_df = None
    validation_md = None
    if run_validation:
        first_long = next((c for c in comparisons if c.kind == "longitudinal"), None)
        if first_long is not None and nv_comparison is not None:
            b_df = _get(first_long.b_label)
            rep_matrices = {}
            for rep in repetitions:
                sid = _timepoint_session(participant, reference_timepoint, rep, task_part)
                m = _get(sid)
                if m is not None:
                    rep_matrices[rep] = m
            report = validation.run_validation(
                config,
                first_long,
                nv_comparison,
                a_df,
                b_df,
                features,
                flagged_links=[c.link for c in selection.excluded_links()],
                repetition_matrices=rep_matrices,
            )
            validation_df = report.to_dataframe()
            validation_md = report.summary_md()

    from gaga_jcvpca.rotations import FilterSettings

    ctx = reporting.RunContext(
        run_id=run_id or reporting.new_run_id(participant),
        participant=participant,
        config=config,
        selection=selection,
        filter_settings=FilterSettings.from_config(config).__dict__,
        comparisons=comparisons,
        threshold_sweep=sweep_df,
        validation_results=validation_df,
        validation_summary_md=validation_md,
        marker_set_notes=_marker_set_notes(config, participant, timepoints),
    )
    return reporting.write_run(ctx)


def _marker_set_notes(config: Config, participant: str, timepoints: list[str]) -> dict:
    inv = build_inventory(config)
    prefixes = {
        sid: pref
        for sid, pref in inv.marker_set_by_session.items()
        if sid.startswith(participant)
    }
    if len(set(prefixes.values())) > 1:
        return {
            participant: (
                f"Marker-set prefix differs across timepoints ({sorted(set(prefixes.values()))}). "
                f"Cross-timepoint comparisons restricted to shared valid links; interpret with care."
            )
        }
    return {}
