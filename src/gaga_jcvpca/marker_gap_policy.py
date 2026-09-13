"""Session-scoped link exclusions from raw-marker large-gap QC (ex09-13).

Advisory layer: flags links where supporting markers spent material time in
contiguous missing runs (>0.5 s). Applied at comparison time (not in selection YAML).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from gaga_jcvpca.config import Config
from gaga_jcvpca.jcvpca import link_id_of

MARKER_GAP_PREFIX = "marker_gap_policy:"
DEFAULT_REMOVALS_REL = (
    "results_committee_case/step03_trunk_extension/marker_gap_link_removals_ex09_13.csv"
)


@dataclass(frozen=True)
class MarkerGapPolicy:
    enabled: bool
    removals_path: Path
    removals: pd.DataFrame


def timepoint_session(participant: str, timepoint: str, repetition: str, task_part: str = "P1") -> str:
    return f"{participant}_{timepoint}_{task_part}_{repetition}"


def sessions_for_side(
    participant: str,
    timepoint: str,
    *,
    repetition_mode: str,
    repetitions: list[str],
    task_part: str = "P1",
) -> list[str]:
    """Session ids on one comparison side (pooled => all reps for that timepoint)."""
    reps = repetitions if repetition_mode == "pooled" else [repetitions[0]]
    return [timepoint_session(participant, timepoint, rep, task_part) for rep in reps]


def load_marker_gap_removals(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if df.empty:
        return df
    tier = df.get("removal_tier", pd.Series(dtype=str))
    return df[tier == "remove_from_comparison"].copy()


def load_policy(config: Config) -> MarkerGapPolicy:
    enabled = bool(config.get("analysis.apply_marker_gap_removals", False))
    rel = config.get("analysis.marker_gap_removals_csv", DEFAULT_REMOVALS_REL)
    path = Path(rel)
    if not path.is_absolute():
        path = config.project_root / path
    removals = load_marker_gap_removals(path) if enabled else pd.DataFrame()
    return MarkerGapPolicy(enabled=enabled, removals_path=path, removals=removals)


def links_excluded_for_sessions(
    participant: str,
    session_ids: list[str],
    removals: pd.DataFrame,
) -> dict[str, str]:
    if removals.empty or not session_ids:
        return {}
    sub = removals[
        (removals["participant"].astype(str) == str(participant))
        & (removals["session_id"].isin(session_ids))
    ]
    out: dict[str, str] = {}
    for _, row in sub.iterrows():
        link = str(row["link_stem"])
        t_r = str(row.get("T_R", row.get("session_id", "")))
        detail = str(row.get("reason", "large marker gaps in ex09-13 window"))
        msg = f"{MARKER_GAP_PREFIX} {t_r} — {detail}"
        if link in out:
            out[link] = f"{out[link]}; also flagged on {t_r}"
        else:
            out[link] = msg
    return out


def pre_excluded_for_comparison(
    participant: str,
    a_session_ids: list[str],
    b_session_ids: list[str],
    policy: MarkerGapPolicy,
) -> dict[str, str]:
    if not policy.enabled or policy.removals.empty:
        return {}
    ex_a = links_excluded_for_sessions(participant, a_session_ids, policy.removals)
    ex_b = links_excluded_for_sessions(participant, b_session_ids, policy.removals)
    merged: dict[str, str] = {}
    for link in set(ex_a) | set(ex_b):
        parts = [ex_a[link]] if link in ex_a else []
        if link in ex_b and link not in ex_a:
            parts.append(ex_b[link])
        elif link in ex_b and link in ex_a:
            parts.append(f"B-side: {ex_b[link]}")
        merged[link] = " | ".join(parts)
    return merged


def filter_features(
    feature_names: list[str],
    excluded_stems: set[str],
) -> list[str]:
    return [f for f in feature_names if link_id_of(f) not in excluded_stems]


def is_marker_gap_exclusion(reason: str) -> bool:
    return str(reason).startswith(MARKER_GAP_PREFIX)


def partition_excluded_links(excluded: dict[str, str]) -> tuple[dict[str, str], dict[str, str]]:
    marker: dict[str, str] = {}
    other: dict[str, str] = {}
    for link, reason in excluded.items():
        if is_marker_gap_exclusion(reason):
            marker[link] = reason
        else:
            other[link] = reason
    return marker, other
