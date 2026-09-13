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

from gaga_jcvpca import jcvpca, marker_gap_policy, qc_markers, reporting, validation
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
    qc_gap_heatmaps: dict[str, pd.DataFrame] = field(default_factory=dict)

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
    qc_heatmaps: dict[str, pd.DataFrame] = {}
    parse_warnings: list[str] = []

    if any(r.has_marker_csv for r in inv.rows):
        qc_findings, qc_df, qc_heatmaps = qc_markers.run_marker_qc(cfg, inv, write_cache=True)
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
        qc_gap_heatmaps=qc_heatmaps,
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


def _segments_by_session(config: Config) -> dict[str, list]:
    """Map session_id -> its segmentation windows (built once per analysis)."""
    inv = build_inventory(config)
    out: dict[str, list] = {}
    for seg in inv.segments:
        out.setdefault(seg.session.as_str(), []).append(seg)
    return out


def slice_matrix_to_exercises(
    df: pd.DataFrame,
    segments: list,
    exercise_ids: list[int],
) -> pd.DataFrame:
    """Row-slice a full-session matrix to the selected exercise windows.

    Because conversion keeps matrix row index == Motive frame number (0-based,
    contiguous), each window is simply ``df.iloc[start:end]`` (half-open, matching
    the segmentation semantics). Windows are concatenated in frame order. Windows
    outside the matrix bounds are clamped/skipped; if nothing overlaps (e.g. a
    synthetic short matrix in tests), the full matrix is returned unchanged so the
    caller still has data to analyze.
    """
    if not exercise_ids:
        return df
    wanted = set(int(x) for x in exercise_ids)
    windows = sorted(
        (s for s in segments if int(s.exercise_id) in wanted),
        key=lambda s: int(s.start_frame),
    )
    n = len(df)
    parts = []
    for s in windows:
        start = max(0, int(s.start_frame))
        end = min(n, int(s.end_frame))
        if start < end:
            parts.append(df.iloc[start:end])
    if not parts:
        return df
    return pd.concat(parts, ignore_index=True)


def run_analysis(
    config: Config,
    selection: AnalysisSelection,
    timepoints: list[str],
    repetitions: Optional[list[str]] = None,
    reference_timepoint: str = "T1",
    repetition_mode: str = "single",
    run_threshold_sweep: bool = False,
    run_validation: bool = False,
    run_id: Optional[str] = None,
    matrices: Optional[dict[str, pd.DataFrame]] = None,
) -> Path:
    """Run the full participant-specific analysis and write a run folder.

    ``matrices`` optionally supplies session_id -> feature DataFrame (used by the
    smoke test and UI). When omitted, matrices are loaded from ``data.matrices``.

    ``repetition_mode``:
      * ``single`` (default/fallback): longitudinal sides use the first repetition
        only (``T1_R1 vs T2_R1`` / ``T1_R1 vs T3_R1``).
      * ``pooled`` (ideal): each timepoint side row-concatenates its repetitions
        (``T1(R1+R2) vs T2(R1+R2)`` / vs ``T3(R1+R2)``).
    In both modes, matrices are first sliced to ``selection.exercise_ids`` windows,
    and natural variability stays strictly within-timepoint ``T1_R1 vs T1_R2``
    (never pooled) so the noise floor is preserved. Returns the run folder path.
    """
    repetitions = repetitions or ["R1", "R2"]
    participant = selection.participant
    task_part = config.get("mode.task_part", "P1")
    features = selection.feature_columns()
    vt = float(config.get("pca.variance_threshold", 0.80))
    sensitivity_p = int(config.get("pc_focus.sensitivity_p", 2))
    region_fn = lambda stem: region_of_link(stem, config)
    exercise_ids = list(selection.exercise_ids or [])
    segments_by_session = _segments_by_session(config) if exercise_ids else {}
    gap_policy = marker_gap_policy.load_policy(config)

    def _sessions_for_side(timepoint: str) -> list[str]:
        return marker_gap_policy.sessions_for_side(
            participant,
            timepoint,
            repetition_mode=repetition_mode,
            repetitions=repetitions,
            task_part=task_part,
        )

    def _gap_pre_excluded(a_sessions: list[str], b_sessions: list[str]) -> dict[str, str]:
        return marker_gap_policy.pre_excluded_for_comparison(
            participant, a_sessions, b_sessions, gap_policy
        )

    def _run_comparison(
        comparison_id: str,
        kind: str,
        a_label: str,
        b_label: str,
        a_df: pd.DataFrame,
        b_df: pd.DataFrame,
        a_sessions: list[str],
        b_sessions: list[str],
    ) -> jcvpca.ComparisonResult:
        return jcvpca.run_comparison(
            comparison_id,
            kind,
            a_label,
            b_label,
            a_df,
            b_df,
            features,
            variance_threshold=vt,
            region_of_link=region_fn,
            sensitivity_p=sensitivity_p,
            pre_excluded_links=_gap_pre_excluded(a_sessions, b_sessions),
        )

    def _get(session_id: str) -> Optional[pd.DataFrame]:
        df = matrices.get(session_id) if matrices is not None else load_matrix(config, session_id)
        if df is None:
            return None
        if exercise_ids:
            df = slice_matrix_to_exercises(df, segments_by_session.get(session_id, []), exercise_ids)
        return df

    def _side_matrix(timepoint: str) -> Optional[pd.DataFrame]:
        """Build one timepoint's A/B matrix per the repetition mode (sliced)."""
        if repetition_mode == "pooled":
            frames = [_get(_timepoint_session(participant, timepoint, r, task_part)) for r in repetitions]
            frames = [f for f in frames if f is not None]
            if not frames:
                return None
            return pd.concat(frames, ignore_index=True)
        return _get(_timepoint_session(participant, timepoint, repetitions[0], task_part))

    comparisons: list[jcvpca.ComparisonResult] = []
    longitudinal_b: dict[str, pd.DataFrame] = {}

    a_df = _side_matrix(reference_timepoint)
    if a_df is None:
        raise FileNotFoundError(
            f"Reference matrix not found for {participant} {reference_timepoint} "
            f"(mode={repetition_mode}, reps={repetitions})."
        )
    ref_label = (
        f"{participant}_{reference_timepoint}_{'+'.join(repetitions)}"
        if repetition_mode == "pooled"
        else _timepoint_session(participant, reference_timepoint, repetitions[0], task_part)
    )

    # Longitudinal comparisons: reference vs each other timepoint.
    for tp in timepoints:
        if tp == reference_timepoint:
            continue
        b_df = _side_matrix(tp)
        if b_df is None:
            continue
        b_label = (
            f"{participant}_{tp}_{'+'.join(repetitions)}"
            if repetition_mode == "pooled"
            else _timepoint_session(participant, tp, repetitions[0], task_part)
        )
        comparison_id = f"{participant}_{reference_timepoint}_vs_{tp}"
        longitudinal_b[comparison_id] = b_df
        comparisons.append(
            _run_comparison(
                comparison_id,
                "longitudinal",
                ref_label,
                b_label,
                a_df,
                b_df,
                _sessions_for_side(reference_timepoint),
                _sessions_for_side(tp),
            )
        )

    # Natural variability: reference timepoint R1 vs R2 (never pooled, sliced).
    nv_comparison = None
    if len(repetitions) >= 2:
        r1_id = _timepoint_session(participant, reference_timepoint, repetitions[0], task_part)
        r2_id = _timepoint_session(participant, reference_timepoint, repetitions[1], task_part)
        r1_df, r2_df = _get(r1_id), _get(r2_id)
        if r1_df is not None and r2_df is not None:
            nv_comparison = _run_comparison(
                f"{participant}_{reference_timepoint}_R1_vs_R2",
                "natural_variability",
                r1_id,
                r2_id,
                r1_df,
                r2_df,
                [r1_id],
                [r2_id],
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
            sweep_df = jcvpca.threshold_sweep(
                a_df,
                longitudinal_b[first_long.comparison_id],
                features,
                candidates=[float(x) for x in config.get("pca.threshold_sweep.candidates", [0.7, 0.8, 0.9])],
            )

    # Optional validation.
    validation_df = None
    validation_md = None
    if run_validation:
        longitudinals = [c for c in comparisons if c.kind == "longitudinal"]
        if longitudinals and nv_comparison is not None:
            first_long = longitudinals[0]
            b_df = longitudinal_b[first_long.comparison_id]
            rep_matrices = {}
            for rep in repetitions:
                m = _get(_timepoint_session(participant, reference_timepoint, rep, task_part))
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
                additional_longitudinals=longitudinals[1:],
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
        input_files=[gap_policy.removals_path] if gap_policy.enabled else [],
        marker_set_notes=_marker_set_notes(config, participant, timepoints),
        marker_gap_policy_enabled=gap_policy.enabled,
        marker_gap_removals_path=str(gap_policy.removals_path) if gap_policy.enabled else "",
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
