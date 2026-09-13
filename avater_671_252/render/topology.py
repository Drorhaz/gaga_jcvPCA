"""Skeleton topology for the avatar: analytic edges + layout connectors.

Two layers, both derived from data already present (no hardcoded per-participant
edge lists), so this scales to any participant whose tables and reference pose
are available:

* **Analytic edges** come straight from the link-level table (``parent_joint``
  -> ``child_joint``, ``region_id``). These carry the JcvPCA ratios and get
  colored.
* **Layout connectors** come from the reference-pose bone hierarchy. Any
  parent->child bone pair that is *not* an analytic edge is drawn as a thin
  dashed "layout only" segment (E7) so the body reads as a connected skeleton.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

# Edge tags drive visual style downstream (renderer / E7).
TAG_ANALYTIC = "analytic"
TAG_PARTICIPANT_SPECIFIC = "participant_specific"
TAG_LAYOUT_ONLY = "layout_only"


@dataclass(frozen=True)
class Edge:
    parent_joint: str
    child_joint: str
    tag: str
    link_id: str | None = None
    canonical_link_name: str | None = None
    region_id: str | None = None
    region_label: str | None = None


def _is_participant_specific(link_id: str, participant: str) -> bool:
    """252 hip-root links (``252_to_LThigh``) exist only for that participant.

    Detected generically: a link whose parent token equals the participant id
    is a participant-rooted link not comparable across the cohort (E7).
    """
    return str(link_id).startswith(f"{participant}_to_")


def analytic_edges(links_all_spaces: pd.DataFrame, participant: str) -> list[Edge]:
    """One analytic edge per unique link_id (dominance/ratios joined later)."""
    cols = ["link_id", "parent_joint", "child_joint", "canonical_link_name",
            "region_id", "region_label"]
    dedup = links_all_spaces[cols].drop_duplicates(subset="link_id")
    edges: list[Edge] = []
    for _, row in dedup.iterrows():
        link_id = str(row["link_id"])
        tag = (
            TAG_PARTICIPANT_SPECIFIC
            if _is_participant_specific(link_id, participant)
            else TAG_ANALYTIC
        )
        edges.append(
            Edge(
                parent_joint=str(row["parent_joint"]),
                child_joint=str(row["child_joint"]),
                tag=tag,
                link_id=link_id,
                canonical_link_name=str(row["canonical_link_name"]),
                region_id=str(row["region_id"]),
                region_label=str(row["region_label"]),
            )
        )
    return edges


def layout_edges(hierarchy: dict[str, str], analytic: list[Edge]) -> list[Edge]:
    """Bone parent->child pairs not covered by analytic edges (E7 dashed).

    ``hierarchy`` maps a joint name to its parent joint (root maps to itself).
    Joint names here are the short segment tokens used in the reference pose
    (e.g. ``LUArm``), matching ``parent_joint``/``child_joint`` in the tables.
    """
    analytic_pairs = {(e.parent_joint, e.child_joint) for e in analytic}
    analytic_pairs |= {(e.child_joint, e.parent_joint) for e in analytic}
    out: list[Edge] = []
    for child, parent in hierarchy.items():
        if not parent or parent == child:
            continue
        if (parent, child) in analytic_pairs:
            continue
        out.append(Edge(parent_joint=parent, child_joint=child, tag=TAG_LAYOUT_ONLY))
    return out


def all_edges(
    links_all_spaces: pd.DataFrame,
    participant: str,
    hierarchy: dict[str, str],
) -> list[Edge]:
    analytic = analytic_edges(links_all_spaces, participant)
    return analytic + layout_edges(hierarchy, analytic)
