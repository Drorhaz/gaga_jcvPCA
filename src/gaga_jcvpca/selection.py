"""Segment & link selection: combine QC information into one decision surface.

The user (or a default policy) chooses which exercises/segments and which links
enter the analysis. The result is a saved, named ``analysis_selection.yaml`` that
JcvPCA runs consume, so every run records exactly what was analyzed and why.

QC recommendations are advisory: the user can override any include/exclude, and
overrides are recorded with the persisted selection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import yaml

from gaga_jcvpca.config import Config
from gaga_jcvpca.schemas import QCFinding, Recommendation

AXIS_SUFFIXES = ("_rx", "_ry", "_rz")


def link_stem(feature_name: str) -> str:
    """Feature column -> link stem: 'Chest_to_Neck_rx' -> 'Chest_to_Neck'."""
    for suffix in AXIS_SUFFIXES:
        if feature_name.endswith(suffix):
            return feature_name[: -len(suffix)]
    return feature_name


def region_of_link(stem: str, config: Config) -> str:
    """Map a link stem to a configured body region (token matching)."""
    regions: dict = config.get("regions", {}) or {}
    for region_id, spec in regions.items():
        for token in spec.get("match_any", []) or []:
            if token in stem:
                return region_id
    return "other"


def is_excluded_distal(stem: str, config: Config) -> bool:
    tokens = config.get("exclude_tokens", []) or []
    return any(tok in stem for tok in tokens)


@dataclass
class LinkChoice:
    link: str                  # canonical stem
    region: str
    included: bool
    reason: str                # research-language why
    qc_recommendation: str = Recommendation.INCLUDE.value
    user_override: bool = False


@dataclass
class AnalysisSelection:
    """A named, persistable selection of segments + links."""

    name: str
    participant: str
    exercise_ids: list[int]                    # authoritative ids (e.g. [9,10,11,12,13])
    combine_exercises: bool                    # analyze the group as one unit vs per-exercise
    links: list[LinkChoice] = field(default_factory=list)
    notes: str = ""
    created_at: str = ""

    def included_links(self) -> list[str]:
        return [c.link for c in self.links if c.included]

    def excluded_links(self) -> list[LinkChoice]:
        return [c for c in self.links if not c.included]

    def feature_columns(self) -> list[str]:
        return [f"{stem}{ax}" for stem in self.included_links() for ax in AXIS_SUFFIXES]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "participant": self.participant,
            "exercise_ids": [int(x) for x in self.exercise_ids],
            "combine_exercises": bool(self.combine_exercises),
            "links": [
                {
                    "link": c.link,
                    "region": c.region,
                    "included": bool(c.included),
                    "reason": c.reason,
                    "qc_recommendation": c.qc_recommendation,
                    "user_override": bool(c.user_override),
                }
                for c in self.links
            ],
            "notes": self.notes,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AnalysisSelection":
        return cls(
            name=data["name"],
            participant=str(data["participant"]),
            exercise_ids=[int(x) for x in data["exercise_ids"]],
            combine_exercises=bool(data["combine_exercises"]),
            links=[
                LinkChoice(
                    link=l["link"],
                    region=l["region"],
                    included=bool(l["included"]),
                    reason=l.get("reason", ""),
                    qc_recommendation=l.get("qc_recommendation", Recommendation.INCLUDE.value),
                    user_override=bool(l.get("user_override", False)),
                )
                for l in data.get("links", [])
            ],
            notes=data.get("notes", ""),
            created_at=data.get("created_at", ""),
        )


def default_selection(
    name: str,
    participant: str,
    manifest: pd.DataFrame,
    config: Config,
    exercise_ids: Optional[list[int]] = None,
    combine_exercises: bool = True,
    qc_findings: Optional[list[QCFinding]] = None,
) -> AnalysisSelection:
    """Build a default selection from a feature manifest + QC recommendations.

    Included by default: every manifest link that is not distal-excluded and whose
    region has no EXCLUDE-level QC recommendation.
    """
    qc_findings = qc_findings or []
    region_recs: dict[str, str] = {}
    region_messages: dict[str, str] = {}
    order = {
        Recommendation.INCLUDE.value: 0,
        Recommendation.INCLUDE_WITH_CAUTION.value: 1,
        Recommendation.EXCLUDE.value: 2,
    }
    for f in qc_findings:
        # link/region-resolution findings carry scope suffix '::<region>'
        if f.resolution == "link" and "::" in f.scope:
            region = f.scope.rsplit("::", 1)[-1]
            prev = region_recs.get(region)
            if prev is None or order.get(f.recommendation.value, 0) > order.get(prev, 0):
                region_recs[region] = f.recommendation.value
                region_messages[region] = f.message

    stems = sorted({link_stem(f) for f in manifest["feature_name"].astype(str)})
    choices: list[LinkChoice] = []
    for stem in stems:
        region = region_of_link(stem, config)
        if is_excluded_distal(stem, config):
            choices.append(
                LinkChoice(
                    link=stem,
                    region=region,
                    included=False,
                    reason="Distal link excluded by policy (noisy fingers/toes).",
                    qc_recommendation=Recommendation.EXCLUDE.value,
                )
            )
            continue
        rec = region_recs.get(region, Recommendation.INCLUDE.value)
        included = rec != Recommendation.EXCLUDE.value
        if rec == Recommendation.INCLUDE.value:
            reason = "Clean QC; included by default."
        else:
            reason = region_messages.get(
                region,
                {
                    Recommendation.INCLUDE_WITH_CAUTION.value: (
                        "QC soft-warning in this body region; included but flagged for careful interpretation."
                    ),
                    Recommendation.EXCLUDE.value: (
                        "QC recommends exclusion for this body region (excess marker gaps)."
                    ),
                }.get(rec, "QC advisory for this body region."),
            )
        choices.append(
            LinkChoice(link=stem, region=region, included=included, reason=reason, qc_recommendation=rec)
        )

    if exercise_ids is None:
        primary = config.get("primary_group", "Group4")
        exercise_ids = [
            int(x)
            for x in (config.get(f"movement_groups.{primary}.exercise_ids", []) or [])
        ]

    return AnalysisSelection(
        name=name,
        participant=participant,
        exercise_ids=exercise_ids,
        combine_exercises=combine_exercises,
        links=choices,
        created_at=datetime.now().isoformat(timespec="seconds"),
    )


def shared_link_intersection(a: AnalysisSelection, b: AnalysisSelection) -> list[str]:
    """Shared included links between two selections (cross-timepoint / cross-participant)."""
    return sorted(set(a.included_links()) & set(b.included_links()))


def save_selection(selection: AnalysisSelection, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{selection.name}.yaml"
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(selection.to_dict(), fh, sort_keys=False, allow_unicode=True)
    return path


def load_selection(path: Path) -> AnalysisSelection:
    with open(path, "r", encoding="utf-8") as fh:
        return AnalysisSelection.from_dict(yaml.safe_load(fh))


def list_selections(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(directory.glob("*.yaml"))
