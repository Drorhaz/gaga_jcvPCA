"""Step 2 — skeleton baseline audit, canonical link map, and manifest regeneration.

Produces:
  - results_committee_case/step02_link_mapping/SKELETON_BASELINES.md
  - results_committee_case/step02_link_mapping/canonical_link_map.csv
  - results_committee_case/step02_link_mapping/COMPARABILITY_MATRIX.md
  - results_committee_case/step02_link_mapping/MARKER_SET_AUDIT.md
  - data/link_mapping/canonical_link_map.csv  (source copy)
  - Updated data/feature_manifests/*_feature_manifest.csv (trunk-inclusive feasible set)

Usage:
  PYTHONPATH=src .venv/bin/python scripts/audit_skeleton_baselines.py
  PYTHONPATH=src .venv/bin/python scripts/audit_skeleton_baselines.py --write-manifests
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca.config import load_config
from gaga_jcvpca.feature_manifest_gen import (
    TopologyKind,
    _hierarchy_to_bones,
    _sample_skeleton_for_participant,
    assess_topology,
    load_reference_hierarchies,
    parse_skeleton_hierarchy,
    verify_manifest_links,
)
from gaga_jcvpca.inventory import build_inventory
from gaga_jcvpca.project_io import marker_set_prefix
from gaga_jcvpca.rotations import build_link_map_from_bones, resolve_link_pair
from gaga_jcvpca.selection import is_excluded_distal

PARTICIPANTS = ("671", "252", "651", "790")
SETUP_A = TopologyKind.STYLE_671_14LINK
SETUP_B = TopologyKind.STYLE_252_16LINK

# Canonical IDs that group topology variants across setups.
CANONICAL_SPECS: list[dict] = [
    # pelvis / trunk
    {"canonical_link_id": "pelvis_to_Ab", "region_id": "trunk_spine", "anatomical_description": "Pelvis root to abdomen", "comparability": "participant_only", "match_stems": ("{pid}_to_Ab",)},
    {"canonical_link_id": "pelvis_to_LThigh", "region_id": "left_leg", "anatomical_description": "Pelvis root to left thigh", "comparability": "participant_only", "match_stems": ("{pid}_to_LThigh",)},
    {"canonical_link_id": "pelvis_to_RThigh", "region_id": "right_leg", "anatomical_description": "Pelvis root to right thigh", "comparability": "participant_only", "match_stems": ("{pid}_to_RThigh",)},
    {"canonical_link_id": "Ab_to_Chest", "region_id": "trunk_spine", "anatomical_description": "Abdomen to chest (direct)", "comparability": "topology_variant", "match_stems": ("Ab_to_Chest",)},
    {"canonical_link_id": "Ab_to_Spine2", "region_id": "trunk_spine", "anatomical_description": "Abdomen to upper lumbar (Spine2)", "comparability": "setup_specific", "match_stems": ("Ab_to_Spine2",)},
    {"canonical_link_id": "Spine2_to_Spine3", "region_id": "trunk_spine", "anatomical_description": "Lumbar spine segment", "comparability": "setup_specific", "match_stems": ("Spine2_to_Spine3",)},
    {"canonical_link_id": "Spine3_to_Spine4", "region_id": "trunk_spine", "anatomical_description": "Thoracic spine segment", "comparability": "setup_specific", "match_stems": ("Spine3_to_Spine4",)},
    {"canonical_link_id": "Spine4_to_Chest", "region_id": "trunk_spine", "anatomical_description": "Upper trunk to chest", "comparability": "setup_specific", "match_stems": ("Spine4_to_Chest",)},
    {"canonical_link_id": "Chest_to_Neck", "region_id": "head_neck", "anatomical_description": "Chest to neck base", "comparability": "cohort", "match_stems": ("Chest_to_Neck",)},
    {"canonical_link_id": "Neck_to_Neck2", "region_id": "head_neck", "anatomical_description": "Neck to upper neck (Neck2)", "comparability": "setup_specific", "match_stems": ("Neck_to_Neck2",)},
    {"canonical_link_id": "neck_to_head", "region_id": "head_neck", "anatomical_description": "Neck to head (terminal)", "comparability": "topology_variant", "match_stems": ("Neck_to_Head", "Neck2_to_Head")},
    # left arm
    {"canonical_link_id": "Chest_to_LShoulder", "region_id": "left_arm", "anatomical_description": "Chest to left shoulder", "comparability": "cohort", "match_stems": ("Chest_to_LShoulder",)},
    {"canonical_link_id": "LShoulder_to_LUArm", "region_id": "left_arm", "anatomical_description": "Left shoulder to upper arm", "comparability": "cohort", "match_stems": ("LShoulder_to_LUArm",)},
    {"canonical_link_id": "LUArm_to_LFArm", "region_id": "left_arm", "anatomical_description": "Left elbow", "comparability": "cohort", "match_stems": ("LUArm_to_LFArm",)},
    {"canonical_link_id": "LFArm_to_LHand", "region_id": "left_arm", "anatomical_description": "Left wrist / hand", "comparability": "cohort", "match_stems": ("LFArm_to_LHand",)},
    # right arm
    {"canonical_link_id": "Chest_to_RShoulder", "region_id": "right_arm", "anatomical_description": "Chest to right shoulder", "comparability": "cohort", "match_stems": ("Chest_to_RShoulder",)},
    {"canonical_link_id": "RShoulder_to_RUArm", "region_id": "right_arm", "anatomical_description": "Right shoulder to upper arm", "comparability": "cohort", "match_stems": ("RShoulder_to_RUArm",)},
    {"canonical_link_id": "RUArm_to_RFArm", "region_id": "right_arm", "anatomical_description": "Right elbow", "comparability": "cohort", "match_stems": ("RUArm_to_RFArm",)},
    {"canonical_link_id": "RFArm_to_RHand", "region_id": "right_arm", "anatomical_description": "Right wrist / hand", "comparability": "cohort", "match_stems": ("RFArm_to_RHand",)},
    # legs (distal chain — pelvis roots listed above)
    {"canonical_link_id": "LThigh_to_LShin", "region_id": "left_leg", "anatomical_description": "Left knee", "comparability": "cohort", "match_stems": ("LThigh_to_LShin",)},
    {"canonical_link_id": "LShin_to_LFoot", "region_id": "left_leg", "anatomical_description": "Left ankle / foot", "comparability": "cohort", "match_stems": ("LShin_to_LFoot",)},
    {"canonical_link_id": "RThigh_to_RShin", "region_id": "right_leg", "anatomical_description": "Right knee", "comparability": "cohort", "match_stems": ("RThigh_to_RShin",)},
    {"canonical_link_id": "RShin_to_RFoot", "region_id": "right_leg", "anatomical_description": "Right ankle / foot", "comparability": "cohort", "match_stems": ("RShin_to_RFoot",)},
]

FEATURE_AXES = ("rx", "ry", "rz")
MANIFEST_COLUMNS = [
    "feature_name",
    "canonical_link_name",
    "parent_canonical",
    "child_canonical",
    "axis",
    "source_layer2_column",
    "include_in_pilot",
    "feature_scope",
    "notes",
]


@dataclass(frozen=True)
class ParticipantSkeleton:
    participant: str
    hierarchy: object
    assessment: object
    feasible_links: tuple[str, ...]
    link_map: dict[str, tuple[str, str]]


def _feasible_link_stems(link_map: dict[str, tuple[str, str]], config) -> list[str]:
    stems = sorted(link_map.keys())
    return [s for s in stems if not is_excluded_distal(s, config)]


def _match_canonical(stem: str, pid: str, spec: dict) -> bool:
    for pattern in spec["match_stems"]:
        candidate = pattern.format(pid=pid)
        if stem == candidate:
            return True
    return False


def _parent_child_tokens(stem: str) -> tuple[str, str]:
    parent, child = stem.split("_to_", 1)
    return parent, child


def _collect_participants(config) -> dict[str, ParticipantSkeleton]:
    skeleton_dir = config.resolve_path("data.raw_skeleton")
    refs = load_reference_hierarchies(config)
    out: dict[str, ParticipantSkeleton] = {}
    for pid in PARTICIPANTS:
        sample = _sample_skeleton_for_participant(skeleton_dir, pid)
        if sample is None:
            raise FileNotFoundError(f"No skeleton CSV for participant {pid}")
        hierarchy = parse_skeleton_hierarchy(sample)
        assessment = assess_topology(hierarchy, refs)
        bones = _hierarchy_to_bones(hierarchy)
        link_map = build_link_map_from_bones(bones)
        feasible = tuple(_feasible_link_stems(link_map, config))
        out[pid] = ParticipantSkeleton(
            participant=pid,
            hierarchy=hierarchy,
            assessment=assessment,
            feasible_links=feasible,
            link_map=link_map,
        )
    return out


def _assign_stems_to_canonical(participants: dict[str, ParticipantSkeleton]) -> dict[str, dict[str, str]]:
    """canonical_link_id -> {participant: skeleton_link_stem}."""
    assigned: dict[str, dict[str, str]] = {spec["canonical_link_id"]: {} for spec in CANONICAL_SPECS}
    for pid, skel in participants.items():
        for stem in skel.feasible_links:
            for spec in CANONICAL_SPECS:
                if _match_canonical(stem, pid, spec):
                    assigned[spec["canonical_link_id"]][pid] = stem
                    break
    return assigned


def _unmapped_stems(participants: dict[str, ParticipantSkeleton], assigned: dict[str, dict[str, str]]) -> dict[str, list[str]]:
    mapped = {stem for stems in assigned.values() for stem in stems.values()}
    out: dict[str, list[str]] = {}
    for pid, skel in participants.items():
        extra = [s for s in skel.feasible_links if s not in mapped]
        if extra:
            out[pid] = extra
    return out


def build_canonical_rows(
    participants: dict[str, ParticipantSkeleton],
    assigned: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for spec in CANONICAL_SPECS:
        cid = spec["canonical_link_id"]
        row = {
            "canonical_link_id": cid,
            "region_id": spec["region_id"],
            "anatomical_description": spec["anatomical_description"],
            "comparability": spec["comparability"],
        }
        present_count = 0
        for pid in PARTICIPANTS:
            stem = assigned[cid].get(pid, "")
            skel = participants[pid]
            present = "Y" if stem else "N"
            if present == "Y":
                present_count += 1
                parent_bone, child_bone = skel.link_map[stem]
                parent_tok, child_tok = _parent_child_tokens(stem)
            else:
                parent_bone = child_bone = parent_tok = child_tok = ""
            row[f"{pid}_present"] = present
            row[f"{pid}_link_stem"] = stem
            row[f"{pid}_parent_bone"] = parent_bone
            row[f"{pid}_child_bone"] = child_bone
            row[f"{pid}_parent_token"] = parent_tok
            row[f"{pid}_child_token"] = child_tok
        row["n_participants_present"] = str(present_count)
        rows.append(row)
    return rows


def write_canonical_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "canonical_link_id",
        "region_id",
        "anatomical_description",
        "comparability",
        "n_participants_present",
    ]
    for pid in PARTICIPANTS:
        fieldnames.extend(
            [
                f"{pid}_present",
                f"{pid}_link_stem",
                f"{pid}_parent_bone",
                f"{pid}_child_bone",
                f"{pid}_parent_token",
                f"{pid}_child_token",
            ]
        )
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _manifest_filename(pid: str, kind: TopologyKind) -> str:
    if kind == SETUP_A:
        return f"group4_core_14link_within_{pid}_feature_manifest.csv"
    if kind == SETUP_B:
        return f"group4_core_16link_within_{pid}_feature_manifest.csv"
    raise ValueError(f"Unknown topology for {pid}")


def write_manifest_for_participant(
    pid: str,
    skel: ParticipantSkeleton,
    manifest_path: Path,
) -> None:
    rows: list[dict[str, str]] = []
    setup = "Setup A (671-style)" if skel.assessment.kind == SETUP_A else "Setup B (252-style)"
    for stem in skel.feasible_links:
        parent_tok, child_tok = _parent_child_tokens(stem)
        canonical_name = f"{parent_tok}->{child_tok}"
        for axis in FEATURE_AXES:
            rows.append(
                {
                    "feature_name": f"{parent_tok}_to_{child_tok}_{axis}",
                    "canonical_link_name": canonical_name,
                    "parent_canonical": parent_tok,
                    "child_canonical": child_tok,
                    "axis": axis,
                    "source_layer2_column": f"{axis}_filtered_analysis",
                    "include_in_pilot": "true",
                    "feature_scope": "feasible_full",
                    "notes": (
                        f"Step 2 full feasible set ({setup}); "
                        f"trunk-inclusive; QC in Step 3"
                    ),
                }
            )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _marker_audit_rows(config) -> list[dict[str, str]]:
    inv = build_inventory(config)
    desc_dir = config.resolve_path("data.descriptions")
    skeleton_dir = config.resolve_path("data.raw_skeleton")
    rows: list[dict[str, str]] = []
    for row in inv.rows:
        sid = row.session_id
        desc_files = sorted(desc_dir.glob(f"{sid}*DataDescriptions.csv"))
        prefix = inv.marker_set_by_session.get(sid, "")
        if not prefix and desc_files:
            prefix = marker_set_prefix(desc_files[0]) or ""
        skel_files = sorted((skeleton_dir / row.participant).glob(f"{sid}*.csv"))
        rows.append(
            {
                "participant": row.participant,
                "session_id": sid,
                "timepoint": sid.split("_")[1],
                "repetition": sid.split("_")[3],
                "marker_set_prefix": prefix or "unknown",
                "has_datadescriptions": "Y" if desc_files else "N",
                "has_skeleton_csv": "Y" if skel_files else "N",
                "session_status": row.status,
            }
        )
    return rows


def write_marker_audit_md(path: Path, rows: list[dict[str, str]]) -> None:
    by_pid: dict[str, list[dict[str, str]]] = {}
    for r in rows:
        by_pid.setdefault(r["participant"], []).append(r)

    lines = [
        "# Marker-set audit — Step 2",
        "",
        "**Audit date:** generated by `scripts/audit_skeleton_baselines.py`",
        "",
        "Prefixes inferred from DataDescriptions sidecars where present; "
        "raw skeleton headers used for sessions without sidecars.",
        "",
    ]
    for pid in PARTICIPANTS:
        sessions = by_pid.get(pid, [])
        prefixes = sorted({r["marker_set_prefix"] for r in sessions if r["marker_set_prefix"] != "unknown"})
        lines.append(f"## Participant {pid}")
        lines.append("")
        if len(prefixes) > 1:
            lines.append(
                f"- **Flag:** multiple marker-set prefixes across timepoints: `{prefixes}`"
            )
        elif prefixes:
            lines.append(f"- Marker-set prefix: `{prefixes[0]}` (consistent)")
        else:
            lines.append("- **Flag:** no DataDescriptions sidecars found — prefix unknown")
        lines.append("")
        lines.append("| Session | Prefix | DataDescriptions | Skeleton CSV | Status |")
        lines.append("|---|---|---|---|---|")
        for r in sessions:
            lines.append(
                f"| {r['session_id']} | {r['marker_set_prefix']} | "
                f"{r['has_datadescriptions']} | {r['has_skeleton_csv']} | {r['session_status']} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Cross-timepoint implications",
            "",
            "- **671 T3** uses prefix `T3` (not `671`) — shared-link restriction applies for T1↔T3 comparisons.",
            "- **252** has no DataDescriptions sidecars in `data/descriptions/`; skeleton CSV headers supply hierarchy.",
            "- Marker-set differences do not block within-participant analysis but require caution in cross-timepoint PCA stability.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_skeleton_baselines_md(path: Path, participants: dict[str, ParticipantSkeleton]) -> None:
    lines = [
        "# Skeleton baselines — Step 2",
        "",
        "Two marker-setup classes cover all four committee participants.",
        "",
        "## Setup A — 671-style (51 bones)",
        "",
        "- **Participants:** 671, 651",
        "- **Bones:** 51; no `Spine2` / `Neck2`",
        "- **Trunk chain:** `{pid}_to_Ab` → `Ab_to_Chest` → `Chest_to_Neck` → `Neck_to_Head`",
        "- **Pelvis legs:** `{pid}_to_LThigh`, `{pid}_to_RThigh`",
        f"- **Feasible non-distal links:** {len(participants['671'].feasible_links)}",
        "",
        "## Setup B — 252-style (55 bones)",
        "",
        "- **Participants:** 252, 790",
        "- **Bones:** 55; `Spine2` + `Neck2` present",
        "- **Trunk chain:** `{pid}_to_Ab` → `Ab_to_Spine2` → `Spine3` → `Spine4` → `Chest`",
        "- **Neck chain:** `Chest_to_Neck` → `Neck_to_Neck2` → `Neck2_to_Head`",
        "- **Pelvis legs:** `{pid}_to_LThigh`, `{pid}_to_RThigh`",
        f"- **Feasible non-distal links:** {len(participants['252'].feasible_links)}",
        "",
        "## Participant assignment",
        "",
        "| Participant | Setup | Bones | Spine2 | Neck2 | Bone names match reference | Sample skeleton |",
        "|---|---|---:|---|---|---|---|",
    ]
    for pid in PARTICIPANTS:
        skel = participants[pid]
        h = skel.hierarchy
        a = skel.assessment
        setup = "A" if a.kind == SETUP_A else "B"
        match = "Yes" if a.bone_names_match_reference else "Partial"
        lines.append(
            f"| {pid} | {setup} | {h.bone_count} | "
            f"{'Y' if h.has_spine2 else 'N'} | {'Y' if h.has_neck2 else 'N'} | "
            f"{match} | `{h.sample_skeleton.name}` |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Feasible links exclude finger/toe distal segments (`configs/body_regions.yaml` `exclude_tokens`).",
            "- Pre-trunk `group4_core` manifests (14/16 links) omitted pelvis roots and trunk; Step 2 manifests restore the full feasible set.",
            "- Step 3 applies inclusive QC before primary runs.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_comparability_matrix_md(
    path: Path,
    rows: list[dict[str, str]],
) -> None:
    lines = [
        "# Comparability matrix — Step 2",
        "",
        "Flags indicate whether a canonical link supports cross-participant comparison.",
        "",
        "| Comparability | Meaning |",
        "|---|---|",
        "| `cohort` | Identical segment topology in all participants that carry the link |",
        "| `setup_specific` | Present in Setup B only (extended spine/neck chain) |",
        "| `topology_variant` | Anatomically related but different bone path between setups |",
        "| `participant_only` | Pelvis-root attachment; participant-prefixed stem |",
        "",
        "## Cohort-comparable links (all four participants)",
        "",
    ]
    cohort = [r for r in rows if r["comparability"] == "cohort" and r["n_participants_present"] == "4"]
    for r in cohort:
        lines.append(f"- `{r['canonical_link_id']}` — {r['anatomical_description']}")

    lines.extend(["", "## Setup-specific (252-style only)", ""])
    for r in rows:
        if r["comparability"] == "setup_specific":
            pids = [pid for pid in PARTICIPANTS if r[f"{pid}_present"] == "Y"]
            lines.append(f"- `{r['canonical_link_id']}` — present: {', '.join(pids)}")

    lines.extend(["", "## Topology variants (cross-setup mapping)", ""])
    for r in rows:
        if r["comparability"] == "topology_variant":
            mapping = ", ".join(
                f"{pid}={r[f'{pid}_link_stem']}" for pid in PARTICIPANTS if r[f"{pid}_present"] == "Y"
            )
            lines.append(f"- `{r['canonical_link_id']}` — {mapping}")

    lines.extend(["", "## Participant-only (pelvis roots)", ""])
    for r in rows:
        if r["comparability"] == "participant_only":
            lines.append(f"- `{r['canonical_link_id']}` — stems: `{r['671_link_stem'] or '{pid}_to_*'}` pattern")

    lines.extend(
        [
            "",
            "## Cross-participant analysis guidance",
            "",
            "- **Within-participant** longitudinal claims: use all feasible links per participant.",
            "- **Side-by-side illustration** across participants: prefer `cohort` links only.",
            "- **Trunk redistribution:** compare `Ab_to_Chest` (671/651) vs `Spine4_to_Chest` + intermediate Setup B segments separately — do not merge as one cohort trunk link.",
            "- **Head/neck:** Setup A `Neck_to_Head` maps to Setup B `Neck2_to_Head` (alias-aware in pipeline).",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-manifests",
        action="store_true",
        help="Regenerate per-participant feature manifests from feasible link sets",
    )
    args = parser.parse_args()

    config = load_config()
    out_dir = ROOT / "results_committee_case" / "step02_link_mapping"
    map_dir = ROOT / "data" / "link_mapping"
    manifest_dir = config.resolve_path("data.feature_manifests")

    participants = _collect_participants(config)
    assigned = _assign_stems_to_canonical(participants)
    unmapped = _unmapped_stems(participants, assigned)
    if unmapped:
        print("WARNING: unmapped feasible stems:", unmapped)

    rows = build_canonical_rows(participants, assigned)
    csv_path = out_dir / "canonical_link_map.csv"
    write_canonical_csv(csv_path, rows)
    write_canonical_csv(map_dir / "canonical_link_map.csv", rows)

    write_skeleton_baselines_md(out_dir / "SKELETON_BASELINES.md", participants)
    write_comparability_matrix_md(out_dir / "COMPARABILITY_MATRIX.md", rows)
    marker_rows = _marker_audit_rows(config)
    write_marker_audit_md(out_dir / "MARKER_SET_AUDIT.md", marker_rows)

    print(f"Wrote {csv_path.relative_to(ROOT)} ({len(rows)} canonical links)")
    print(f"Wrote {out_dir.relative_to(ROOT)}/SKELETON_BASELINES.md")
    print(f"Wrote {out_dir.relative_to(ROOT)}/COMPARABILITY_MATRIX.md")
    print(f"Wrote {out_dir.relative_to(ROOT)}/MARKER_SET_AUDIT.md")

    if args.write_manifests:
        for pid, skel in participants.items():
            fname = _manifest_filename(pid, skel.assessment.kind)
            path = manifest_dir / fname
            write_manifest_for_participant(pid, skel, path)
            ok, missing = verify_manifest_links(skel.hierarchy, path)
            if not ok:
                print(f"ERROR {pid}: manifest missing skeleton links: {missing}")
                return 1
            n_links = len(skel.feasible_links)
            print(f"Wrote {path.relative_to(ROOT)} ({n_links} links, {n_links * 3} features)")
    else:
        print("Manifests not written (pass --write-manifests to regenerate).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
