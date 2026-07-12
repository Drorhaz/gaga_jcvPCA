"""Auto-discover the render manifest from the tables directory.

Everything that varies per cohort (participants, comparisons, link counts,
which spaces exist) is read from ``tables/`` and ``provenance_manifest.json``.
Dropping a new participant's link_level + region_space CSVs into the tables tree
makes it renderable with no code change.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

# link_level file names look like ``671_T1_vs_T2_links.csv``.
_LINK_RE = re.compile(r"^(?P<participant>\w+?)_(?P<comparison>T\d+_vs_T\d+)_links\.csv$")
_SPACES = ("functional", "null", "combined")


@dataclass(frozen=True)
class ViewSpec:
    """One render target: a participant x comparison x space."""

    participant: str
    comparison: str          # e.g. "T1_vs_T2"
    space: str               # functional | null | combined
    comparison_id: str       # e.g. "671_T1_vs_T2"

    @property
    def view_id(self) -> str:
        return f"{self.comparison_id}_{self.space}"

    @property
    def reference_timepoint(self) -> str:
        return self.comparison.split("_vs_")[0]

    @property
    def target_timepoint(self) -> str:
        return self.comparison.split("_vs_")[1]


@dataclass(frozen=True)
class TableSet:
    """Resolved table paths for one participant x comparison."""

    participant: str
    comparison: str
    comparison_id: str
    link_level_csv: Path
    region_space_csv: Path


@dataclass(frozen=True)
class RenderManifest:
    tables_dir: Path
    provenance: dict
    table_sets: list[TableSet]

    @property
    def participants(self) -> list[str]:
        seen: list[str] = []
        for ts in self.table_sets:
            if ts.participant not in seen:
                seen.append(ts.participant)
        return seen

    def views(self, spaces: tuple[str, ...] = _SPACES) -> list[ViewSpec]:
        out: list[ViewSpec] = []
        for ts in self.table_sets:
            for space in spaces:
                out.append(
                    ViewSpec(
                        participant=ts.participant,
                        comparison=ts.comparison,
                        space=space,
                        comparison_id=ts.comparison_id,
                    )
                )
        return out

    def table_set(self, participant: str, comparison: str) -> TableSet:
        for ts in self.table_sets:
            if ts.participant == participant and ts.comparison == comparison:
                return ts
        raise KeyError(f"No table set for {participant} {comparison}")


def discover_manifest(avatar_dir: Path) -> RenderManifest:
    """Scan ``{avatar_dir}/tables`` for renderable participant x comparison pairs."""
    tables_dir = avatar_dir / "tables"
    link_dir = tables_dir / "link_level"
    region_space_dir = tables_dir / "region_space"

    prov_path = avatar_dir / "provenance_manifest.json"
    provenance: dict = {}
    if prov_path.exists():
        with open(prov_path, "r", encoding="utf-8") as fh:
            provenance = json.load(fh)

    table_sets: list[TableSet] = []
    for link_csv in sorted(link_dir.glob("*_links.csv")):
        m = _LINK_RE.match(link_csv.name)
        if not m:
            continue
        participant = m.group("participant")
        comparison = m.group("comparison")
        comparison_id = f"{participant}_{comparison}"
        region_csv = region_space_dir / f"{comparison_id}_region_space.csv"
        if not region_csv.exists():
            # Without the region rollup we cannot compute E5 region stats; skip.
            continue
        table_sets.append(
            TableSet(
                participant=participant,
                comparison=comparison,
                comparison_id=comparison_id,
                link_level_csv=link_csv,
                region_space_csv=region_csv,
            )
        )

    return RenderManifest(
        tables_dir=tables_dir, provenance=provenance, table_sets=table_sets
    )
