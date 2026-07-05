"""Small shared Streamlit widgets used across tabs."""

from __future__ import annotations

import streamlit as st

_STATUS_ICON = {
    "ready": "🟢",
    "partial": "🟡",
    "missing": "🔴",
    "legacy": "⚪",
    "unknown": "⚪",
}


def status_badge(status: str) -> str:
    return f"{_STATUS_ICON.get(status, '⚪')} {status}"


def metric_row(metrics: list[tuple[str, object]]) -> None:
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics):
        col.metric(label, value)


def next_action_banner(text: str) -> None:
    st.info(f"**Recommended next action:** {text}")


def sidebar_navigator(snapshot) -> dict:
    """Shared cohort navigator; returns the current filter selection."""
    st.sidebar.header("Navigator")
    inv = snapshot.inventory
    participants = inv.participants()
    timepoints = inv.timepoints()
    repetitions = inv.repetitions()

    sel_participants = st.sidebar.multiselect(
        "Participants", participants, default=participants
    )
    sel_timepoints = st.sidebar.multiselect(
        "Timepoints", timepoints, default=timepoints
    )
    sel_reps = st.sidebar.multiselect("Repetitions", repetitions, default=repetitions)
    st.sidebar.caption(f"science_hash: `{snapshot.science_hash}`")
    return {
        "participants": sel_participants,
        "timepoints": sel_timepoints,
        "repetitions": sel_reps,
    }
