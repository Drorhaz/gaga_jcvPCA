"""Naming unification tests."""

from __future__ import annotations

from gaga_jcvpca.naming import (
    NamingMap,
    canonical_label,
    check_session_naming,
    parse_session_id,
    parse_sheet_name,
)


def test_canonical_label_is_zero_padded():
    assert canonical_label(1) == "ex01"
    assert canonical_label(9) == "ex09"
    assert canonical_label(17) == "ex17"


def test_parse_session_id_basic():
    key = parse_session_id("671_T1_P1_R1")
    assert key is not None
    assert (key.participant, key.timepoint, key.task_part, key.repetition) == (
        "671",
        "T1",
        "P1",
        "R1",
    )


def test_parse_session_id_with_take_suffix():
    key = parse_session_id("671_T1_P1_R1_Take 2026-01-06 03.57.12 PM_001.csv")
    assert key is not None
    assert key.as_str() == "671_T1_P1_R1"


def test_parse_sheet_name():
    key = parse_sheet_name("252 - T3P1R2")
    assert key is not None
    assert key.as_str() == "252_T3_P1_R2"


def test_three_namespaces_disambiguated(config):
    nm = NamingMap(config)
    # exercise_id 9 is canonical ex09, group 4, and Gaga alias P1
    assert nm.group_of(9) == "Group4"
    assert nm.gaga_alias_of(9) == "P1"
    assert nm.gaga_alias_of(13) == "P5"
    assert nm.gaga_alias_of(1) is None  # ex01 has no gaga alias
    assert nm.group_of(1) == "Group1"
    assert nm.group_exercise_ids("Group4") == [9, 10, 11, 12, 13]


def test_check_naming_flags_task_part_and_missing_sheet():
    issues = check_session_naming(
        raw_session_ids=["671_T1_P1_R1", "671_T1_P2_R1", "252_T1_P1_R1"],
        sheet_names=["671 - T1P1R1"],  # 252 sheet missing
        task_part_scope="P1",
    )
    kinds = {i.kind for i in issues}
    assert "out_of_scope_task_part" in kinds  # the P2 session
    assert "missing_segmentation_sheet" in kinds  # 252_T1_P1_R1 has no sheet


def test_check_naming_flags_duplicates():
    issues = check_session_naming(
        raw_session_ids=["671_T1_P1_R1_takeA.csv", "671_T1_P1_R1_takeB.csv"],
        sheet_names=["671 - T1P1R1"],
        task_part_scope="P1",
    )
    assert any(i.kind == "duplicate_session" for i in issues)
