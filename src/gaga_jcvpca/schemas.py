"""Shared data contracts (single source of field/column definitions).

These are lightweight dataclasses used across the pipeline so every module agrees
on field names and severity vocabulary. No heavy dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# --- severity + recommendation vocabulary (fixed categories) ---

class Severity(str, Enum):
    """Fixed QC severity categories (thresholds are configurable, categories are not)."""

    HARD_FAILURE = "hard_failure"      # cannot compute -> block this unit
    SOFT_WARNING = "soft_warning"      # compute, but interpret carefully
    INFO = "info"                      # neutral note


class Recommendation(str, Enum):
    INCLUDE = "include"
    EXCLUDE = "exclude"
    INCLUDE_WITH_CAUTION = "include_with_caution"


class ValidationStrength(str, Enum):
    DESCRIPTIVE_ONLY = "descriptive only"
    BOOTSTRAP_SUPPORTED = "bootstrap-supported"
    PERMUTATION_SUPPORTED = "permutation-supported"
    SENSITIVITY_SUPPORTED = "sensitivity-supported"
    INSUFFICIENT_DATA = "insufficient data"


# --- session identity ---

@dataclass(frozen=True)
class SessionKey:
    """Canonical capture identity: {participant}_T{timepoint}_P{task_part}_R{repetition}."""

    participant: str
    timepoint: str        # "T1" / "T2" / "T3"
    task_part: str        # "P1" (Task Part 1). V1 supports P1 only.
    repetition: str       # "R1" / "R2"

    def as_str(self) -> str:
        return f"{self.participant}_{self.timepoint}_{self.task_part}_{self.repetition}"

    def as_sheet(self) -> str:
        return f"{self.participant} - {self.timepoint}{self.task_part}{self.repetition}"


@dataclass(frozen=True)
class ExerciseSegment:
    """One segmentation-workbook row (exercise_id is authoritative)."""

    session: SessionKey
    exercise_id: int
    canonical_label: str          # ex{exercise_id:02d}
    exercise_name: str
    start_frame: int
    end_frame: int
    group_id: Optional[str] = None      # Group1..Group6 if the id falls in a group range
    gaga_alias: Optional[str] = None    # P1..P5 for exercise_id 9..13, else None

    @property
    def n_frames(self) -> int:
        return int(self.end_frame) - int(self.start_frame)


# --- discovery / inventory ---

@dataclass
class InventoryRow:
    """One row of the Project Inventory."""

    participant: str
    timepoint: str
    task_part: str
    repetition: str
    session_id: str
    has_marker_csv: bool = False
    has_skeleton_csv: bool = False
    has_description: bool = False
    has_segmentation_sheet: bool = False
    n_exercises: int = 0
    status: str = "unknown"       # ready / partial / missing / legacy
    notes: list[str] = field(default_factory=list)


@dataclass
class NamingIssue:
    """A detected naming/consistency problem."""

    kind: str                     # e.g. "duplicate_session", "unexpected_sheet_name"
    subject: str                  # what it is about (file / sheet / session id)
    message: str                  # research-language explanation


# --- QC finding (used from Phase 3 on) ---

@dataclass
class QCFinding:
    resolution: str               # dataset / participant / timepoint / segment / link / frame
    scope: str                    # which unit (e.g. "671_T1_P1_R1::ex09" or "left_arm")
    metric: str                   # what was measured
    value: float
    severity: Severity
    recommendation: Recommendation
    message: str                  # research-language sentence
    affects_levels: list[str] = field(default_factory=list)  # link/region/functional/null
