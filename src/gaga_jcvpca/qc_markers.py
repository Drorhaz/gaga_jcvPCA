"""Raw-marker QC that translates technical measures into research consequences.

QC is computed at six resolutions (dataset, participant, timepoint, segment,
link/body-region, frame). Every finding is both a structured record and a
plain-language sentence, and carries a fixed severity plus an include / exclude /
include_with_caution recommendation. Thresholds come from qc_thresholds.yaml;
severity CATEGORIES are fixed (decision 5).

The heavy raw-marker matrices are parsed elsewhere; this module operates on a
compact ``MarkerData`` object so the logic is fully testable with synthetic data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from gaga_jcvpca.schemas import QCFinding, Recommendation, Severity

# --- marker -> body-region mapping (raw marker names, not link stems) ---
# Ordered so more specific tokens win.
_REGION_TOKENS: list[tuple[str, list[str]]] = [
    ("head_neck", ["Head", "Neck"]),
    ("left_arm", ["LShoulder", "LUArm", "LElbow", "LWrist", "LFArm", "LHand", "LArm"]),
    ("right_arm", ["RShoulder", "RUArm", "RElbow", "RWrist", "RFArm", "RHand", "RArm"]),
    ("left_leg", ["LThigh", "LKnee", "LShin", "LAnkle", "LFoot", "LToe", "LHeel", "LLeg"]),
    ("right_leg", ["RThigh", "RKnee", "RShin", "RAnkle", "RFoot", "RToe", "RHeel", "RLeg"]),
    ("trunk_spine", ["Chest", "Back", "Waist", "Hip", "Ab", "Spine", "Sternum"]),
]


def region_of_marker(marker_name: str) -> str:
    for region, tokens in _REGION_TOKENS:
        for tok in tokens:
            if tok in marker_name:
                return region
    return "other"


@dataclass
class MarkerData:
    """Compact raw-marker representation.

    ``presence`` is a boolean array (n_frames x n_markers): True when the marker
    is tracked in that frame. ``positions`` (optional) is (n_frames x n_markers x 3)
    used for artifact (velocity) detection. ``frame_rate_hz`` converts frames->seconds.
    """

    marker_names: list[str]
    presence: np.ndarray
    frame_rate_hz: float
    positions: Optional[np.ndarray] = None
    session_id: str = ""

    @property
    def n_frames(self) -> int:
        return int(self.presence.shape[0])

    @property
    def n_markers(self) -> int:
        return int(self.presence.shape[1])


# --- gap detection ---

@dataclass
class Gap:
    marker: str
    start_frame: int
    end_frame: int      # inclusive

    @property
    def length_frames(self) -> int:
        return self.end_frame - self.start_frame + 1

    def length_seconds(self, frame_rate_hz: float) -> float:
        return self.length_frames / frame_rate_hz


def detect_gaps(
    presence: np.ndarray,
    marker_names: list[str],
    frame_start: int = 0,
) -> list[Gap]:
    """Find contiguous runs of missing frames per marker.

    ``frame_start`` offsets reported frame indices (for segment-relative windows).
    """
    gaps: list[Gap] = []
    n_frames, n_markers = presence.shape
    for m in range(n_markers):
        col = presence[:, m]
        f = 0
        while f < n_frames:
            if not col[f]:
                start = f
                while f < n_frames and not col[f]:
                    f += 1
                gaps.append(
                    Gap(
                        marker=marker_names[m],
                        start_frame=frame_start + start,
                        end_frame=frame_start + f - 1,
                    )
                )
            else:
                f += 1
    return gaps


def _cluster_flags(
    gaps: list[Gap],
    frame_rate_hz: float,
    cfg: dict,
) -> tuple[list[Gap], dict[str, int]]:
    """Split gaps into large (critical) and count short-gap clusters per marker."""
    large_gap_s = float(cfg["gaps"]["large_gap_seconds"])
    cluster_window_s = float(cfg["gaps"]["cluster_window_seconds"])
    cluster_min = int(cfg["gaps"]["cluster_min_count"])

    large = [g for g in gaps if g.length_seconds(frame_rate_hz) > large_gap_s]

    # cluster short gaps per marker within a sliding time window
    window_frames = cluster_window_s * frame_rate_hz
    by_marker: dict[str, list[Gap]] = {}
    for g in gaps:
        if g.length_seconds(frame_rate_hz) <= large_gap_s:
            by_marker.setdefault(g.marker, []).append(g)
    clustered: dict[str, int] = {}
    for marker, mgaps in by_marker.items():
        mgaps.sort(key=lambda x: x.start_frame)
        for i in range(len(mgaps)):
            window = [mgaps[i]]
            for j in range(i + 1, len(mgaps)):
                if mgaps[j].start_frame - mgaps[i].start_frame <= window_frames:
                    window.append(mgaps[j])
            if len(window) >= cluster_min:
                clustered[marker] = max(clustered.get(marker, 0), len(window))
    return large, clustered


# --- artifact (velocity spike) detection ---

def detect_velocity_artifacts(md: MarkerData, cfg: dict) -> int:
    """Count frames with implausible marker velocity spikes (percentile-based)."""
    if md.positions is None:
        return 0
    pct = float(cfg["artifacts"]["velocity_percentile_threshold"])
    pos = md.positions
    # per-marker speed magnitude between consecutive frames
    diffs = np.diff(pos, axis=0)  # (n-1, m, 3)
    speed = np.linalg.norm(diffs, axis=2)  # (n-1, m)
    finite = speed[np.isfinite(speed)]
    if finite.size == 0:
        return 0
    threshold = np.percentile(finite, pct)
    spike_frames = np.any(speed > threshold, axis=1)
    return int(np.sum(spike_frames))


# --- resolution rollups + findings ---

def _missing_percent(presence: np.ndarray) -> float:
    total = presence.size
    if total == 0:
        return 0.0
    return 100.0 * float(np.sum(~presence)) / total


def _tier_and_recommendation(missing_pct: float, cfg: dict) -> tuple[Severity, Recommendation]:
    tiers = cfg["marker_missing_percent"]
    if missing_pct <= tiers["warn_max"]:
        return Severity.INFO, Recommendation.INCLUDE
    if missing_pct <= tiers["caution_max"]:
        return Severity.SOFT_WARNING, Recommendation.INCLUDE_WITH_CAUTION
    return Severity.SOFT_WARNING, Recommendation.EXCLUDE


def _gap_span_text(gaps: list[Gap]) -> str:
    if not gaps:
        return ""
    first, last = min(g.start_frame for g in gaps), max(g.end_frame for g in gaps)
    return f"frames {first:,}-{last:,}"


# --- marker -> manifest link stem mapping ---

LinkSpec = tuple[str, str, str]  # (stem, parent_canonical, child_canonical)


def link_specs_from_manifest(manifest: pd.DataFrame) -> list[LinkSpec]:
    """Build unique link specs from a feature manifest."""
    from gaga_jcvpca.selection import link_stem

    specs: list[LinkSpec] = []
    seen: set[str] = set()
    for _, row in manifest.iterrows():
        stem = link_stem(str(row["feature_name"]))
        if stem in seen:
            continue
        seen.add(stem)
        parent = str(row.get("parent_canonical", "") or "")
        child = str(row.get("child_canonical", "") or "")
        if parent and child:
            specs.append((stem, parent, child))
    return specs


def _marker_short_name(marker_name: str) -> str:
    return marker_name.split(":")[-1]


def links_for_marker(marker_name: str, link_specs: list[LinkSpec]) -> list[str]:
    """Return manifest link stems whose parent/child tokens appear in the marker name."""
    short = _marker_short_name(marker_name)
    return [stem for stem, parent, child in link_specs if parent in short or child in short]


def links_for_gaps(gaps: list[Gap], link_specs: list[LinkSpec]) -> list[str]:
    """Unique link stems affected by the given marker gaps."""
    stems: set[str] = set()
    for g in gaps:
        stems.update(links_for_marker(g.marker, link_specs))
    return sorted(stems)


def load_link_specs_for_participant(config, participant: str) -> list[LinkSpec]:
    """Load link specs from the participant feature manifest, if available."""
    from gaga_jcvpca import project_io
    from gaga_jcvpca.feature_manifest_gen import resolve_manifest_path

    try:
        manifest_dir = config.resolve_path("data.feature_manifests")
    except KeyError:
        return []
    path = resolve_manifest_path(participant, manifest_dir)
    if path is None:
        return []
    return link_specs_from_manifest(project_io.load_feature_manifest(path))


def build_large_gap_heatmap(
    md: MarkerData,
    cfg: dict,
    link_specs: list[LinkSpec],
) -> pd.DataFrame:
    """Binary matrix: rows = link stems, columns = frame index, 1 = critical gap frame."""
    if not link_specs or md.n_frames == 0:
        return pd.DataFrame()

    large_gap_s = float(cfg["gaps"]["large_gap_seconds"])
    frame_rate = md.frame_rate_hz
    stems = [s[0] for s in link_specs]
    stem_idx = {s: i for i, s in enumerate(stems)}
    matrix = np.zeros((len(stems), md.n_frames), dtype=np.uint8)

    marker_link_map = [links_for_marker(n, link_specs) for n in md.marker_names]
    gaps = detect_gaps(md.presence, md.marker_names)
    for g in gaps:
        if g.length_seconds(frame_rate) <= large_gap_s:
            continue
        mi = md.marker_names.index(g.marker)
        start = max(0, g.start_frame)
        end = min(md.n_frames - 1, g.end_frame)
        for stem in marker_link_map[mi]:
            row = stem_idx.get(stem)
            if row is not None:
                matrix[row, start : end + 1] = 1

    return pd.DataFrame(matrix, index=stems, columns=list(range(md.n_frames)))


def bin_heatmap_for_display(heatmap: pd.DataFrame, max_cols: int = 500) -> tuple[pd.DataFrame, bool]:
    """Bin frame columns for UI display when captures are very long."""
    if heatmap.empty or heatmap.shape[1] <= max_cols:
        return heatmap, False
    n_frames = heatmap.shape[1]
    bin_size = int(np.ceil(n_frames / max_cols))
    cols: list[str] = []
    data: list[np.ndarray] = []
    for b in range(max_cols):
        start = b * bin_size
        end = min(n_frames, (b + 1) * bin_size)
        if start >= n_frames:
            break
        chunk = heatmap.iloc[:, start:end]
        data.append((chunk.max(axis=1) > 0).astype(np.uint8).values)
        cols.append(f"{start}-{end - 1}")
    return pd.DataFrame(np.column_stack(data), index=heatmap.index, columns=cols), True


def qc_segment(
    md: MarkerData,
    cfg: dict,
    scope_label: str,
    region_filter: Optional[str] = None,
    link_specs: Optional[list[LinkSpec]] = None,
) -> list[QCFinding]:
    """Produce QC findings for one segment window across all resolutions below dataset.

    ``scope_label`` is like '671_T1_P1_R1::ex09'. If ``region_filter`` is given,
    only that region's markers are considered (link/region resolution).
    """
    findings: list[QCFinding] = []
    frame_rate = md.frame_rate_hz

    # select marker columns for the region if requested
    if region_filter:
        idx = [i for i, m in enumerate(md.marker_names) if region_of_marker(m) == region_filter]
        if not idx:
            return findings
        presence = md.presence[:, idx]
        names = [md.marker_names[i] for i in idx]
        res = "link"
        scope = f"{scope_label}::{region_filter}"
    else:
        presence = md.presence
        names = md.marker_names
        res = "segment"
        scope = scope_label

    missing_pct = _missing_percent(presence)
    gaps = detect_gaps(presence, names)
    large, clustered = _cluster_flags(gaps, frame_rate, cfg)
    severity, recommendation = _tier_and_recommendation(missing_pct, cfg)

    # escalate on critical large gaps
    if large:
        severity = Severity.SOFT_WARNING
        if recommendation == Recommendation.INCLUDE:
            recommendation = Recommendation.INCLUDE_WITH_CAUTION

    # build the research-language sentence
    where = f"the {region_filter.replace('_', ' ')} region" if region_filter else "this segment"
    span = _gap_span_text(large or gaps)
    n_gaps = len(gaps)
    largest_s = max((g.length_seconds(frame_rate) for g in gaps), default=0.0)
    clustered_note = (
        f" Short gaps cluster in markers {sorted(clustered)[:3]}." if clustered else ""
    )
    analyzable = recommendation != Recommendation.EXCLUDE
    affects = _affected_levels(region_filter)

    parts = [
        f"{scope}: {missing_pct:.1f}% marker gaps in {where}"
        + (f" (mainly {span})" if span else "")
        + f"; {n_gaps} gap(s), largest {largest_s:.2f}s.{clustered_note}"
    ]
    if large:
        parts.append(
            f"{len(large)} gap(s) exceed {cfg['gaps']['large_gap_seconds']}s and are flagged critical for review."
        )
    parts.append(
        "Analyzable, but interpret with care." if analyzable and severity != Severity.INFO
        else ("Good coverage." if severity == Severity.INFO else "Recommend excluding this unit.")
    )
    if recommendation == Recommendation.INCLUDE_WITH_CAUTION and region_filter:
        parts.append(f"Consider excluding {region_filter.replace('_', ' ')} links from JcvPCA.")

    specs = link_specs or []
    affected = links_for_gaps(large, specs) if large and specs else []
    if affected:
        parts.append(
            f"Affected links for exclusion review: {', '.join(affected)}."
        )
    message = " ".join(parts)

    findings.append(
        QCFinding(
            resolution=res,
            scope=scope,
            metric="marker_missing_percent",
            value=round(missing_pct, 3),
            severity=severity,
            recommendation=recommendation,
            message=message,
            affects_levels=affects,
            affected_links=affected,
        )
    )
    return findings


def _affected_levels(region_filter: Optional[str]) -> list[str]:
    if region_filter:
        return ["link-level", "region-level", "functional-space", "null-space"]
    return ["region-level", "functional-space", "null-space"]


def qc_segment_all_regions(
    md: MarkerData,
    cfg: dict,
    scope_label: str,
    link_specs: Optional[list[LinkSpec]] = None,
) -> list[QCFinding]:
    """Segment-level finding plus one per body region present in the segment."""
    specs = link_specs or []
    findings = qc_segment(md, cfg, scope_label, link_specs=specs)
    regions = sorted({region_of_marker(m) for m in md.marker_names} - {"other"})
    for region in regions:
        findings.extend(
            qc_segment(md, cfg, scope_label, region_filter=region, link_specs=specs)
        )
    # artifact note
    n_artifact = detect_velocity_artifacts(md, cfg)
    if n_artifact:
        findings.append(
            QCFinding(
                resolution="segment",
                scope=scope_label,
                metric="velocity_artifact_frames",
                value=float(n_artifact),
                severity=Severity.SOFT_WARNING,
                recommendation=Recommendation.INCLUDE_WITH_CAUTION,
                message=(
                    f"{scope_label}: {n_artifact} frame(s) show implausible marker "
                    f"velocity spikes (>{cfg['artifacts']['velocity_percentile_threshold']} "
                    f"percentile). These frames may distort rotation-vector estimates."
                ),
                affects_levels=["link-level", "functional-space", "null-space"],
            )
        )
    return findings


def marker_set_finding(
    participant: str,
    prefixes_by_session: dict[str, str],
) -> Optional[QCFinding]:
    """Comparability finding when a participant's marker-set prefix differs across sessions."""
    prefixes = sorted(set(prefixes_by_session.values()))
    if len(prefixes) <= 1:
        return None
    return QCFinding(
        resolution="participant",
        scope=participant,
        metric="marker_set_prefixes",
        value=float(len(prefixes)),
        severity=Severity.SOFT_WARNING,
        recommendation=Recommendation.INCLUDE_WITH_CAUTION,
        message=(
            f"Participant {participant} uses different marker-set prefixes across "
            f"timepoints ({prefixes}). Cross-timepoint comparisons are allowed but "
            f"must be interpreted with this context; analysis is restricted to the "
            f"shared valid link intersection and the difference is recorded in the run manifest."
        ),
        affects_levels=["link-level", "region-level"],
    )


def findings_to_dataframe(findings: list[QCFinding]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "resolution": f.resolution,
                "scope": f.scope,
                "metric": f.metric,
                "value": f.value,
                "severity": f.severity.value,
                "recommendation": f.recommendation.value,
                "affects_levels": ";".join(f.affects_levels),
                "affected_links": ";".join(f.affected_links),
                "message": f.message,
            }
            for f in findings
        ]
    )


# --- Motive marker CSV parsing (skeleton CSV is the canonical source) ---

def marker_data_from_take(take, frame_rate_hz: Optional[float] = None) -> MarkerData:
    """Build MarkerData from an already-parsed MotiveTake (avoids re-reading the CSV)."""
    from gaga_jcvpca.project_io import MotiveTake

    if not isinstance(take, MotiveTake):
        raise TypeError("take must be a MotiveTake instance")
    rate = float(frame_rate_hz) if frame_rate_hz is not None else take.frame_rate_hz
    return MarkerData(
        marker_names=take.marker_names,
        presence=take.marker_presence,
        frame_rate_hz=rate,
        positions=take.marker_positions_m,
        session_id=take.path.stem,
    )


def parse_motive_marker_csv(path: str | Path, frame_rate_hz: float) -> MarkerData:
    """Parse marker channels from a Motive skeleton CSV into MarkerData (meters)."""
    from gaga_jcvpca import project_io

    take = project_io.parse_motive_take(path)
    md = marker_data_from_take(take, frame_rate_hz=frame_rate_hz)
    md.session_id = Path(path).stem
    return md


def _slice_marker_data(md: MarkerData, start: int, end: int) -> Optional[MarkerData]:
    """Return a segment window of marker data (half-open frame interval)."""
    end = min(int(end), md.n_frames)
    start = int(start)
    if start >= end:
        return None
    return MarkerData(
        marker_names=md.marker_names,
        presence=md.presence[start:end],
        frame_rate_hz=md.frame_rate_hz,
        positions=md.positions[start:end] if md.positions is not None else None,
        session_id=md.session_id,
    )


def _comparability_findings(inventory) -> list[QCFinding]:
    """Convert inventory naming issues and marker-set checks into QC findings."""
    findings: list[QCFinding] = []
    for issue in inventory.naming_issues:
        if issue.kind != "marker_set_difference":
            continue
        findings.append(
            QCFinding(
                resolution="participant",
                scope=issue.subject,
                metric="marker_set_prefixes",
                value=1.0,
                severity=Severity.SOFT_WARNING,
                recommendation=Recommendation.INCLUDE_WITH_CAUTION,
                message=issue.message,
                affects_levels=["link-level", "region-level"],
            )
        )

    by_participant: dict[str, dict[str, str]] = {}
    for sid, prefix in inventory.marker_set_by_session.items():
        pid = sid.split("_", 1)[0]
        by_participant.setdefault(pid, {})[sid] = prefix
    for pid, mapping in by_participant.items():
        f = marker_set_finding(pid, mapping)
        if f is not None and not any(
            x.scope == pid and x.metric == "marker_set_prefixes" for x in findings
        ):
            findings.append(f)
    return findings


def _qc_one_session(
    config,
    inventory,
    session_id: str,
    thresholds: dict,
) -> tuple[list[QCFinding], Optional[pd.DataFrame]]:
    """Run session-level and per-segment QC for one capture."""
    from gaga_jcvpca import project_io

    path = project_io.resolve_session_marker_csv(config, session_id)
    if path is None:
        return [], None

    participant = session_id.split("_", 1)[0]
    link_specs = load_link_specs_for_participant(config, participant)
    frame_rate = float(thresholds.get("capture", {}).get("frame_rate_hz", 120.0))
    try:
        md = parse_motive_marker_csv(path, frame_rate_hz=frame_rate)
        md.session_id = session_id
    except Exception as exc:
        return [
            QCFinding(
                resolution="session",
                scope=session_id,
                metric="parse_error",
                value=0.0,
                severity=Severity.SOFT_WARNING,
                recommendation=Recommendation.INCLUDE_WITH_CAUTION,
                message=(
                    f"Could not parse marker CSV for {session_id} at {path}: {exc}. "
                    f"Marker QC for this session is unavailable; review the file manually."
                ),
                affects_levels=["region-level", "functional-space", "null-space"],
            )
        ], None

    heatmap = build_large_gap_heatmap(md, thresholds, link_specs)

    findings: list[QCFinding] = []
    findings.extend(
        qc_segment_all_regions(
            md, thresholds, scope_label=f"{session_id}::session", link_specs=link_specs
        )
    )

    segments = [s for s in inventory.segments if s.session.as_str() == session_id]
    for seg in segments:
        seg_md = _slice_marker_data(md, seg.start_frame, seg.end_frame)
        if seg_md is None:
            continue
        label = f"{session_id}::{seg.canonical_label}"
        findings.extend(
            qc_segment_all_regions(seg_md, thresholds, label, link_specs=link_specs)
        )
    return findings, heatmap if not heatmap.empty else None


def run_marker_qc(
    config,
    inventory,
    *,
    session_ids: Optional[list[str]] = None,
    write_cache: bool = True,
) -> tuple[list[QCFinding], pd.DataFrame, dict[str, pd.DataFrame]]:
    """Run raw-marker QC across inventory sessions and optionally persist qc_summary.csv."""
    thresholds = config.data
    if session_ids is None:
        session_ids = sorted(
            r.session_id for r in inventory.rows if r.has_marker_csv
        )

    all_findings: list[QCFinding] = []
    heatmaps: dict[str, pd.DataFrame] = {}
    for sid in session_ids:
        findings, heatmap = _qc_one_session(config, inventory, sid, thresholds)
        all_findings.extend(findings)
        if heatmap is not None:
            heatmaps[sid] = heatmap

    if session_ids is None or len(session_ids) > 1:
        all_findings.extend(_comparability_findings(inventory))

    df = findings_to_dataframe(all_findings)
    if write_cache and not df.empty:
        qc_dir = config.resolve_path("outputs.cache") / "qc"
        qc_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(qc_dir / "qc_summary.csv", index=False)
    return all_findings, df, heatmaps


def marker_source_cache_key(config, inventory) -> str:
    """Hash marker input paths + mtimes for Streamlit cache invalidation."""
    import hashlib

    from gaga_jcvpca import project_io

    parts: list[str] = []
    for row in sorted(inventory.rows, key=lambda r: r.session_id):
        if not row.has_marker_csv:
            continue
        path = project_io.resolve_session_marker_csv(config, row.session_id)
        if path is None:
            continue
        try:
            mtime = path.stat().st_mtime
        except OSError:
            mtime = 0
        parts.append(f"{row.session_id}:{path}:{mtime}")
    blob = "|".join(parts)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def summarize_qc_findings(findings: list[QCFinding], inventory) -> dict:
    """Roll up QC metrics for the dashboard overview."""
    n_sessions = sum(1 for r in inventory.rows if r.has_marker_csv)
    if not findings:
        return {
            "n_findings": 0,
            "n_sessions_with_markers": n_sessions,
            "n_soft_warnings": 0,
            "n_large_gaps": 0,
            "n_velocity_artifact_findings": 0,
            "by_severity": {},
            "by_recommendation": {},
        }

    by_severity: dict[str, int] = {}
    by_recommendation: dict[str, int] = {}
    n_large_gaps = 0
    n_velocity = 0
    for f in findings:
        by_severity[f.severity.value] = by_severity.get(f.severity.value, 0) + 1
        by_recommendation[f.recommendation.value] = (
            by_recommendation.get(f.recommendation.value, 0) + 1
        )
        if f.metric == "velocity_artifact_frames":
            n_velocity += 1
        if f.metric == "marker_missing_percent" and "critical" in f.message.lower():
            n_large_gaps += 1

    return {
        "n_findings": len(findings),
        "n_sessions_with_markers": n_sessions,
        "n_soft_warnings": by_severity.get(Severity.SOFT_WARNING.value, 0),
        "n_large_gaps": n_large_gaps,
        "n_velocity_artifact_findings": n_velocity,
        "by_severity": by_severity,
        "by_recommendation": by_recommendation,
    }
