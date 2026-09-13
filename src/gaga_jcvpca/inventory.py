"""Project Inventory: discover what exists before any analysis.

Scans the standalone data/ folder and builds a clear picture of which
participants / timepoints / exercises / repetitions exist, which files are
present or missing, naming inconsistencies, and the canonical<->alias mapping.

Raw marker/skeleton/description captures are listed even when no segmentation
workbook exists (status ``partial``) so session-level QC can run before exercise
windows are authored.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

import pandas as pd

from gaga_jcvpca import project_io
from gaga_jcvpca.config import Config
from gaga_jcvpca.naming import NamingMap, check_session_naming, parse_session_id
from gaga_jcvpca.schemas import ExerciseSegment, InventoryRow, NamingIssue


@dataclass
class Inventory:
    rows: list[InventoryRow]
    segments: list[ExerciseSegment]
    naming_issues: list[NamingIssue]
    marker_set_by_session: dict[str, str] = field(default_factory=dict)

    # --- summaries for the UI overview ---
    def participants(self) -> list[str]:
        return sorted({r.participant for r in self.rows})

    def timepoints(self) -> list[str]:
        return sorted({r.timepoint for r in self.rows})

    def repetitions(self) -> list[str]:
        return sorted({r.repetition for r in self.rows})

    def exercise_ids(self) -> list[int]:
        return sorted({s.exercise_id for s in self.segments})

    def rows_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([asdict(r) for r in self.rows])

    def segments_dataframe(self) -> pd.DataFrame:
        recs = []
        for s in self.segments:
            recs.append(
                {
                    "session_id": s.session.as_str(),
                    "participant": s.session.participant,
                    "timepoint": s.session.timepoint,
                    "task_part": s.session.task_part,
                    "repetition": s.session.repetition,
                    "exercise_id": s.exercise_id,
                    "canonical_label": s.canonical_label,
                    "exercise_name": s.exercise_name,
                    "group_id": s.group_id,
                    "start_frame": s.start_frame,
                    "end_frame": s.end_frame,
                    "n_frames": s.n_frames,
                }
            )
        return pd.DataFrame(recs)

    def summary(self) -> dict:
        return {
            "n_participants": len(self.participants()),
            "participants": self.participants(),
            "timepoints": self.timepoints(),
            "repetitions": self.repetitions(),
            "n_exercises": len(self.exercise_ids()),
            "exercise_ids": self.exercise_ids(),
            "n_sessions": len(self.rows),
            "n_ready_sessions": sum(1 for r in self.rows if r.status == "ready"),
            "n_naming_issues": len(self.naming_issues),
        }


def _index_raw_files(dir_path: Path, expected_type: str | None) -> dict[str, Path]:
    """Map canonical session id -> raw CSV path for a raw data directory."""
    out: dict[str, Path] = {}
    if not dir_path or not dir_path.exists():
        return out
    for path in dir_path.rglob("*.csv"):
        key = parse_session_id(path.name)
        if key is None:
            continue
        out.setdefault(key.as_str(), path)
    return out


def _index_descriptions(dir_path: Path) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for path in project_io.find_description_files(dir_path):
        key = parse_session_id(path.name)
        if key is not None:
            out.setdefault(key.as_str(), path)
    return out


def build_inventory(config: Config) -> Inventory:
    """Scan data/ and assemble the Project Inventory."""
    naming = NamingMap(config)
    task_part_scope = config.get("mode.task_part", "P1")

    seg_dir = config.resolve_path("data.segmentation")
    desc_dir = config.resolve_path("data.descriptions")

    # Raw dirs may not physically exist in a standalone checkout; that's fine.
    try:
        marker_dir = config.resolve_path("data.raw_markers")
    except KeyError:
        marker_dir = Path()
    try:
        skeleton_dir = config.resolve_path("data.raw_skeleton")
    except KeyError:
        skeleton_dir = Path()

    marker_files = _index_raw_files(marker_dir, "Marker")
    skeleton_files = _index_raw_files(skeleton_dir, "Bone")
    description_files = _index_descriptions(desc_dir)

    workbooks = project_io.find_segmentation_workbooks(seg_dir)

    # Collect segments + build per-session segment counts.
    segments: list[ExerciseSegment] = []
    sheet_names: list[str] = []
    sessions_with_sheet: set[str] = set()
    seg_count_by_session: dict[str, int] = {}
    for pid, wb_path in workbooks.items():
        sheet_names.extend(project_io.segmentation_sheet_names(wb_path))
        wb_segments = project_io.load_segments_for_workbook(
            wb_path, naming, task_part_scope=task_part_scope
        )
        for s in wb_segments:
            sid = s.session.as_str()
            sessions_with_sheet.add(sid)
            seg_count_by_session[sid] = seg_count_by_session.get(sid, 0) + 1
        segments.extend(wb_segments)

    # Union of all discovered session ids (in-scope task part only for rows).
    # Segmentation workbooks define exercise windows; raw marker/skeleton/description
    # files are included even without a workbook so session-level QC can run.
    all_session_ids = set(sessions_with_sheet)
    for sid in list(marker_files) + list(skeleton_files) + list(description_files):
        key = parse_session_id(sid)
        if key and key.task_part == task_part_scope:
            all_session_ids.add(sid)

    rows: list[InventoryRow] = []
    marker_set_by_session: dict[str, str] = {}
    for sid in sorted(all_session_ids):
        key = parse_session_id(sid)
        if key is None:
            continue
        has_marker = sid in marker_files or sid in skeleton_files
        has_skel = sid in skeleton_files
        has_desc = sid in description_files
        has_sheet = sid in sessions_with_sheet
        n_ex = seg_count_by_session.get(sid, 0)

        if has_desc:
            prefix = project_io.marker_set_prefix(description_files[sid])
            if prefix:
                marker_set_by_session[sid] = prefix

        notes: list[str] = []
        if has_sheet and has_skel:
            status = "ready"
        elif has_sheet or has_skel or has_desc:
            status = "partial"
            if not has_sheet:
                notes.append("no segmentation sheet")
            if not has_skel:
                notes.append("no raw skeleton csv")
            if not has_marker:
                notes.append("no marker csv")
        else:
            status = "missing"

        rows.append(
            InventoryRow(
                participant=key.participant,
                timepoint=key.timepoint,
                task_part=key.task_part,
                repetition=key.repetition,
                session_id=sid,
                has_marker_csv=has_marker,
                has_skeleton_csv=has_skel,
                has_description=has_desc,
                has_segmentation_sheet=has_sheet,
                n_exercises=n_ex,
                status=status,
                notes=notes,
            )
        )

    raw_ids = sorted(set(skeleton_files))
    naming_issues = check_session_naming(
        raw_session_ids=raw_ids,
        sheet_names=sheet_names,
        task_part_scope=task_part_scope,
    )
    naming_issues.extend(_marker_set_issues(marker_set_by_session))

    return Inventory(
        rows=rows,
        segments=segments,
        naming_issues=naming_issues,
        marker_set_by_session=marker_set_by_session,
    )


def _marker_set_issues(marker_set_by_session: dict[str, str]) -> list[NamingIssue]:
    """Flag participants whose marker-set prefix differs across timepoints."""
    issues: list[NamingIssue] = []
    by_participant: dict[str, dict[str, str]] = {}
    for sid, prefix in marker_set_by_session.items():
        key = parse_session_id(sid)
        if key is None:
            continue
        by_participant.setdefault(key.participant, {})[sid] = prefix

    for pid, mapping in by_participant.items():
        prefixes = set(mapping.values())
        if len(prefixes) > 1:
            issues.append(
                NamingIssue(
                    kind="marker_set_difference",
                    subject=pid,
                    message=(
                        f"Participant {pid} uses more than one marker-set prefix "
                        f"across timepoints ({sorted(prefixes)}). Cross-timepoint "
                        f"comparisons are allowed but must be interpreted with this "
                        f"context; features are restricted to shared valid links."
                    ),
                )
            )
    return issues
