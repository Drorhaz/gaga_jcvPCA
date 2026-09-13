"""Naming unification.

Two namespaces only:
  * task_part  -> the P in a session key ({pid}_T{t}_P{part}_R{rep}); P1 = Task Part 1.
  * canonical  -> ex{NN}, derived from the authoritative segmentation `exercise_id`.

Exercise identity is ALWAYS taken from the segmentation workbook `exercise_id`
column. Nothing here hardcodes the exercise set.
"""

from __future__ import annotations

import re
from typing import Optional

from gaga_jcvpca.config import Config
from gaga_jcvpca.schemas import NamingIssue, SessionKey

# {participant}_T{t}_P{part}_R{rep}, tolerant of trailing "_Take ..." suffixes.
# No trailing \b: a following "_" is not a word boundary, so we anchor the
# repetition digits with a lookahead allowing end / underscore / dot / space.
SESSION_RE = re.compile(
    r"^(?P<participant>\w+?)_T(?P<timepoint>\d+)_P(?P<task_part>\d+)_R(?P<repetition>\d+)"
    r"(?=$|[_.\s])"
)
# "{participant} - T{t}P{p}R{r}" (segmentation sheet name).
SHEET_RE = re.compile(
    r"^(?P<participant>\w+?)\s*-\s*T(?P<timepoint>\d+)P(?P<task_part>\d+)R(?P<repetition>\d+)$"
)


def canonical_label(exercise_id: int) -> str:
    """Canonical exercise label derived from the authoritative exercise_id."""
    return f"ex{int(exercise_id):02d}"


def parse_session_id(text: str) -> Optional[SessionKey]:
    """Parse a session id / raw filename stem into a SessionKey (or None)."""
    m = SESSION_RE.match(text.strip())
    if not m:
        return None
    return SessionKey(
        participant=m.group("participant"),
        timepoint=f"T{int(m.group('timepoint'))}",
        task_part=f"P{int(m.group('task_part'))}",
        repetition=f"R{int(m.group('repetition'))}",
    )


def parse_sheet_name(text: str) -> Optional[SessionKey]:
    """Parse a segmentation sheet name into a SessionKey (or None)."""
    m = SHEET_RE.match(text.strip())
    if not m:
        return None
    return SessionKey(
        participant=m.group("participant"),
        timepoint=f"T{int(m.group('timepoint'))}",
        task_part=f"P{int(m.group('task_part'))}",
        repetition=f"R{int(m.group('repetition'))}",
    )


class NamingMap:
    """Config-driven mapping between canonical labels and movement groups."""

    def __init__(self, config: Config):
        self._groups: dict[str, dict] = config.get("movement_groups", {}) or {}
        # id -> group id (e.g. 9 -> "Group4")
        self._id_to_group: dict[int, str] = {}
        for gid, spec in self._groups.items():
            for ex_id in spec.get("exercise_ids", []) or []:
                self._id_to_group[int(ex_id)] = gid
        self.primary_group: str = config.get("primary_group", "Group4")

    def group_of(self, exercise_id: int) -> Optional[str]:
        return self._id_to_group.get(int(exercise_id))

    def group_exercise_ids(self, group_id: str) -> list[int]:
        spec = self._groups.get(group_id, {})
        return [int(x) for x in spec.get("exercise_ids", []) or []]

    def group_label(self, group_id: str) -> str:
        return self._groups.get(group_id, {}).get("name", group_id)

    def describe(self, exercise_id: int) -> str:
        """Human-readable one-liner with canonical label and movement group."""
        label = canonical_label(exercise_id)
        group = self.group_of(exercise_id)
        parts = [f"{label} (exercise_id={exercise_id})"]
        if group:
            parts.append(f"{self.group_label(group)} [{group}]")
        return " — ".join(parts)


def check_session_naming(
    raw_session_ids: list[str],
    sheet_names: list[str],
    task_part_scope: str = "P1",
) -> list[NamingIssue]:
    """Flag naming inconsistencies across discovered sessions and sheets.

    Detects: unparseable ids/sheets, duplicate session ids, task-part values
    outside the supported scope, and sheets without a matching raw session.
    """
    issues: list[NamingIssue] = []

    parsed_sessions: dict[str, int] = {}
    for sid in raw_session_ids:
        key = parse_session_id(sid)
        if key is None:
            issues.append(
                NamingIssue(
                    kind="unparseable_session",
                    subject=sid,
                    message=(
                        f"Raw file '{sid}' does not match the canonical session "
                        f"pattern {{pid}}_T#_P#_R#; it will not be linked automatically."
                    ),
                )
            )
            continue
        canon = key.as_str()
        parsed_sessions[canon] = parsed_sessions.get(canon, 0) + 1
        if key.task_part != task_part_scope:
            issues.append(
                NamingIssue(
                    kind="out_of_scope_task_part",
                    subject=canon,
                    message=(
                        f"Session '{canon}' is Task Part {key.task_part}, outside the "
                        f"V1 scope ({task_part_scope}). It is discovered but not analyzed."
                    ),
                )
            )

    for canon, count in parsed_sessions.items():
        if count > 1:
            issues.append(
                NamingIssue(
                    kind="duplicate_session",
                    subject=canon,
                    message=(
                        f"Session '{canon}' matches {count} raw files; a canonical "
                        f"take must be chosen to avoid ambiguous inputs."
                    ),
                )
            )

    sheet_keys = set()
    for name in sheet_names:
        key = parse_sheet_name(name)
        if key is None:
            issues.append(
                NamingIssue(
                    kind="unexpected_sheet_name",
                    subject=name,
                    message=(
                        f"Segmentation sheet '{name}' does not match the expected "
                        f"'{{pid}} - T#P#R#' pattern."
                    ),
                )
            )
            continue
        sheet_keys.add(key.as_str())

    for canon in parsed_sessions:
        key = parse_session_id(canon)
        if key and key.task_part == task_part_scope and canon not in sheet_keys:
            issues.append(
                NamingIssue(
                    kind="missing_segmentation_sheet",
                    subject=canon,
                    message=(
                        f"Session '{canon}' has raw data but no segmentation sheet; "
                        f"its exercises cannot be windowed until a sheet is added."
                    ),
                )
            )

    return issues
