"""Discover missing per-participant feature manifests and generate them from known templates."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from gaga_jcvpca import project_io
from gaga_jcvpca.config import Config
from gaga_jcvpca.naming import parse_session_id
from gaga_jcvpca.project_io import _find_type_row, _read_motive_header_rows
from gaga_jcvpca.rotations import build_link_map_from_bones, resolve_link_pair
from gaga_jcvpca.selection import link_stem

MANIFEST_SUFFIX = "_feature_manifest.csv"

# Explicit overrides; convention-based lookup fills gaps (see resolve_manifest_path).
DEFAULT_MANIFEST_BY_PARTICIPANT: dict[str, str] = {
    "671": "group4_core_14link_within_671_feature_manifest.csv",
    "252": "group4_core_16link_within_252_feature_manifest.csv",
    "651": "group4_core_14link_within_651_feature_manifest.csv",
    "790": "group4_core_16link_within_790_feature_manifest.csv",
}

TEMPLATE_671 = "671_style_14link"
TEMPLATE_252 = "252_style_16link"


class TopologyKind(str, Enum):
    STYLE_671_14LINK = "671_style_14link"
    STYLE_252_16LINK = "252_style_16link"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class SkeletonHierarchy:
    participant: str
    bones_ordered: tuple[str, ...]
    bone_short_names: frozenset[str]
    bone_count: int
    has_spine2: bool
    has_neck2: bool
    sample_skeleton: Path


@dataclass(frozen=True)
class TopologyAssessment:
    kind: TopologyKind
    reference_participant: str
    bone_names_match_reference: bool
    trunk_label: str
    notes: tuple[str, ...]


@dataclass(frozen=True)
class MissingManifestReport:
    participant: str
    sample_skeleton: Path
    hierarchy: SkeletonHierarchy
    assessment: TopologyAssessment
    proposed_filename: str
    template_manifest: Path
    existing_manifest: Optional[Path]


def _canon_bone_name(name: str) -> str:
    if ":" in name:
        return name.replace(":", "_", 1)
    return name


def _bone_short_name(name: str) -> str:
    if ":" in name:
        return name.split(":", 1)[1]
    if "_" in name:
        return name.split("_", 1)[1]
    return name


def parse_skeleton_hierarchy(skeleton_path: Path) -> SkeletonHierarchy:
    """Parse unique Motive Bone columns (name + parent rows) from a skeleton CSV header."""
    rows = _read_motive_header_rows(skeleton_path, max_rows=12)
    type_row_idx = _find_type_row(rows)
    type_row = rows[type_row_idx]
    name_row = rows[type_row_idx + 1]
    parent_row = rows[type_row_idx + 3]

    bones_ordered: list[str] = []
    seen: set[str] = set()
    for i, kind in enumerate(type_row):
        if kind.strip() != "Bone":
            continue
        if i >= len(name_row):
            break
        name = name_row[i].strip()
        if not name or name in seen:
            continue
        seen.add(name)
        bones_ordered.append(name)

    if not bones_ordered:
        raise ValueError(f"No Bone columns found in {skeleton_path}")

    root = _canon_bone_name(bones_ordered[0])
    participant = root.split("_", 1)[0]
    shorts = frozenset(_bone_short_name(b) for b in bones_ordered)

    return SkeletonHierarchy(
        participant=participant,
        bones_ordered=tuple(bones_ordered),
        bone_short_names=shorts,
        bone_count=len(bones_ordered),
        has_spine2="Spine2" in shorts,
        has_neck2="Neck2" in shorts,
        sample_skeleton=skeleton_path,
    )


def _hierarchy_to_bones(hierarchy: SkeletonHierarchy) -> list[project_io.SkeletonBone]:
    rows = _read_motive_header_rows(hierarchy.sample_skeleton, max_rows=12)
    type_row_idx = _find_type_row(rows)
    type_row = rows[type_row_idx]
    name_row = rows[type_row_idx + 1]
    parent_row = rows[type_row_idx + 3]

    index_of = {_canon_bone_name(n): i + 1 for i, n in enumerate(hierarchy.bones_ordered)}
    bones: list[project_io.SkeletonBone] = []
    for name in hierarchy.bones_ordered:
        idx = index_of[_canon_bone_name(name)]
        parent_raw = ""
        for i, kind in enumerate(type_row):
            if kind.strip() != "Bone":
                continue
            if i < len(name_row) and name_row[i].strip() == name:
                parent_raw = parent_row[i].strip() if i < len(parent_row) else ""
                break
        if parent_raw in {"", "Root"}:
            parent_idx = 0
        else:
            parent_idx = index_of.get(_canon_bone_name(parent_raw), 0)
        bones.append(
            project_io.SkeletonBone(
                name=_canon_bone_name(name),
                index=idx,
                parent_index=parent_idx,
            )
        )
    return bones


def _template_manifest_path(manifest_dir: Path, kind: TopologyKind) -> Path:
    if kind == TopologyKind.STYLE_671_14LINK:
        return manifest_dir / "group4_core_14link_within_671_feature_manifest.csv"
    if kind == TopologyKind.STYLE_252_16LINK:
        return manifest_dir / "group4_core_16link_within_252_feature_manifest.csv"
    raise ValueError(f"No template manifest for topology {kind}")


def _proposed_filename(participant: str, kind: TopologyKind) -> str:
    if kind == TopologyKind.STYLE_671_14LINK:
        return f"group4_core_14link_within_{participant}{MANIFEST_SUFFIX}"
    if kind == TopologyKind.STYLE_252_16LINK:
        return f"group4_core_16link_within_{participant}{MANIFEST_SUFFIX}"
    raise ValueError(f"Cannot propose filename for unknown topology")


def _normalized_bone_short_names(hierarchy: SkeletonHierarchy) -> frozenset[str]:
    """Compare topology without the participant-specific pelvis root token (671, 252, …)."""
    pid = hierarchy.participant
    out: set[str] = set()
    for short in hierarchy.bone_short_names:
        if short == pid:
            out.add("ROOT")
        else:
            out.add(short)
    return frozenset(out)


def assess_topology(
    hierarchy: SkeletonHierarchy,
    reference_hierarchies: dict[str, SkeletonHierarchy],
) -> TopologyAssessment:
    notes: list[str] = []
    ref_671 = reference_hierarchies.get("671")
    ref_252 = reference_hierarchies.get("252")

    if hierarchy.bone_count == 51 and not hierarchy.has_spine2 and not hierarchy.has_neck2:
        kind = TopologyKind.STYLE_671_14LINK
        ref_pid = "671"
        trunk = "Ab→Chest→Neck (51 bones, no Spine2/Neck2)"
    elif hierarchy.bone_count == 55 and hierarchy.has_spine2 and hierarchy.has_neck2:
        kind = TopologyKind.STYLE_252_16LINK
        ref_pid = "252"
        trunk = "Ab→Spine2→…→Neck2→Head (55 bones, Spine2 + Neck2 present)"
    else:
        notes.append(
            f"Unrecognized layout: {hierarchy.bone_count} bones, "
            f"Spine2={hierarchy.has_spine2}, Neck2={hierarchy.has_neck2}"
        )
        return TopologyAssessment(
            kind=TopologyKind.UNKNOWN,
            reference_participant="",
            bone_names_match_reference=False,
            trunk_label="unknown",
            notes=tuple(notes),
        )

    ref = reference_hierarchies.get(ref_pid)
    names_match = (
        ref is not None
        and _normalized_bone_short_names(hierarchy) == _normalized_bone_short_names(ref)
    )
    if ref and not names_match:
        only_new = sorted(
            _normalized_bone_short_names(hierarchy) - _normalized_bone_short_names(ref)
        )
        only_ref = sorted(
            _normalized_bone_short_names(ref) - _normalized_bone_short_names(hierarchy)
        )
        if only_new:
            notes.append(f"Bones not in {ref_pid} reference: {', '.join(only_new[:8])}")
        if only_ref:
            notes.append(f"Bones missing vs {ref_pid} reference: {', '.join(only_ref[:8])}")
    elif names_match:
        notes.append(f"Bone segment names match participant {ref_pid}")

    return TopologyAssessment(
        kind=kind,
        reference_participant=ref_pid,
        bone_names_match_reference=names_match,
        trunk_label=trunk,
        notes=tuple(notes),
    )


def resolve_manifest_path(
    participant: str,
    manifest_dir: Path,
    explicit_map: Optional[dict[str, str]] = None,
) -> Optional[Path]:
    """Return an existing feature manifest CSV for a participant, if present."""
    mapping = explicit_map if explicit_map is not None else DEFAULT_MANIFEST_BY_PARTICIPANT
    named = mapping.get(participant)
    if named:
        path = manifest_dir / named
        if path.is_file():
            return path
    matches = sorted(manifest_dir.glob(f"*within_{participant}{MANIFEST_SUFFIX}"))
    if len(matches) == 1:
        return matches[0]
    return None


def _sample_skeleton_for_participant(skeleton_dir: Path, participant: str) -> Optional[Path]:
    folder = skeleton_dir / participant
    candidates: list[Path] = []
    if folder.is_dir():
        candidates.extend(
            p
            for p in sorted(folder.glob("*.csv"))
            if "DataDescriptions" not in p.name and p.stat().st_size > 0
        )
    if not candidates:
        candidates.extend(
            p
            for p in sorted(skeleton_dir.rglob("*.csv"))
            if "DataDescriptions" not in p.name
            and p.stat().st_size > 0
            and parse_session_id(p.name) is not None
            and parse_session_id(p.name).participant == participant
        )
    return candidates[0] if candidates else None


def participants_with_skeleton(config: Config) -> set[str]:
    try:
        skeleton_dir = config.resolve_path("data.raw_skeleton")
    except KeyError:
        return set()
    if not skeleton_dir.exists():
        return set()
    out: set[str] = set()
    for path in skeleton_dir.rglob("*.csv"):
        if "DataDescriptions" in path.name or path.stat().st_size == 0:
            continue
        key = parse_session_id(path.name)
        if key is not None:
            out.add(key.participant)
            continue
        if path.parent.name.isdigit():
            out.add(path.parent.name)
    return out


def load_reference_hierarchies(config: Config) -> dict[str, SkeletonHierarchy]:
    skeleton_dir = config.resolve_path("data.raw_skeleton")
    refs: dict[str, SkeletonHierarchy] = {}
    for pid in ("671", "252"):
        sample = _sample_skeleton_for_participant(skeleton_dir, pid)
        if sample is not None:
            refs[pid] = parse_skeleton_hierarchy(sample)
    return refs


def discover_missing_manifests(
    config: Config,
    explicit_map: Optional[dict[str, str]] = None,
) -> list[MissingManifestReport]:
    manifest_dir = config.resolve_path("data.feature_manifests")
    skeleton_dir = config.resolve_path("data.raw_skeleton")
    refs = load_reference_hierarchies(config)
    reports: list[MissingManifestReport] = []

    for participant in sorted(participants_with_skeleton(config)):
        existing = resolve_manifest_path(participant, manifest_dir, explicit_map)
        if existing is not None:
            continue
        sample = _sample_skeleton_for_participant(skeleton_dir, participant)
        if sample is None:
            continue
        hierarchy = parse_skeleton_hierarchy(sample)
        assessment = assess_topology(hierarchy, refs)
        if assessment.kind == TopologyKind.UNKNOWN:
            proposed = f"group4_core_UNKNOWN_within_{participant}{MANIFEST_SUFFIX}"
            template = Path()
        else:
            proposed = _proposed_filename(participant, assessment.kind)
            template = _template_manifest_path(manifest_dir, assessment.kind)
        reports.append(
            MissingManifestReport(
                participant=participant,
                sample_skeleton=sample,
                hierarchy=hierarchy,
                assessment=assessment,
                proposed_filename=proposed,
                template_manifest=template,
                existing_manifest=existing,
            )
        )
    return reports


def _link_stems_from_manifest(path: Path) -> set[str]:
    df = project_io.load_feature_manifest(path)
    return {link_stem(x) for x in project_io.feature_names_from_manifest(df)}


def verify_manifest_links(
    hierarchy: SkeletonHierarchy,
    manifest_path: Path,
) -> tuple[bool, list[str]]:
    """Check skeleton hierarchy can supply every manifest link (incl. aliases)."""
    link_map = build_link_map_from_bones(_hierarchy_to_bones(hierarchy))
    missing: list[str] = []
    for stem in sorted(_link_stems_from_manifest(manifest_path)):
        if resolve_link_pair(stem, link_map) is None:
            missing.append(stem)
    return not missing, missing


def generate_manifest_csv(
    participant: str,
    template_path: Path,
    out_path: Path,
    reference_participant: str,
) -> Path:
    """Clone a reference manifest and rewrite participant-specific tokens."""
    text = template_path.read_text(encoding="utf-8")
    ref = reference_participant
    replacements = [
        (f"Within-{ref}", f"Within-{participant}"),
        (f"{ref}->LThigh", f"{participant}->LThigh"),
        (f"{ref}->RThigh", f"{participant}->RThigh"),
        (f"{ref}_to_LThigh", f"{participant}_to_LThigh"),
        (f"{ref}_to_RThigh", f"{participant}_to_RThigh"),
        (f"{ref}->LThigh", f"{participant}->LThigh"),
        (f"parent_canonical,{ref},", f"parent_canonical,{participant},"),
    ]
    if ref != participant:
        # Pelvis feature rows: 252_to_LThigh -> {pid}_to_LThigh
        replacements.extend(
            [
                (f"{ref}_to_LThigh_", f"{participant}_to_LThigh_"),
                (f"{ref}_to_RThigh_", f"{participant}_to_RThigh_"),
                (f"{ref}->{ref}", f"{participant}->{participant}"),
            ]
        )
    for old, new in replacements:
        text = text.replace(old, new)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    return out_path


def format_report(report: MissingManifestReport) -> str:
    lines = [
        f"Participant {report.participant} — feature manifest MISSING",
        f"  Sample skeleton: {report.sample_skeleton}",
        f"  Topology: {report.assessment.trunk_label}",
    ]
    if report.assessment.kind == TopologyKind.UNKNOWN:
        lines.append("  Equivalent to known data: NO — manual manifest authoring required")
    else:
        equiv = "YES" if report.assessment.bone_names_match_reference else "PARTIAL"
        lines.append(
            f"  Equivalent to {report.assessment.reference_participant} "
            f"({report.assessment.kind.value}): {equiv}"
        )
        lines.append(f"  Proposed file: {report.proposed_filename}")
    for note in report.assessment.notes:
        lines.append(f"  Note: {note}")
    return "\n".join(lines)
