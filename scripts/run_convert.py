"""Convert raw skeleton CSVs to rotation-vector matrices (one parse per session).

Reads marker QC data and bone quaternions from the same Motive skeleton export,
writes feature parquets under data.matrices and optional QC CSVs under
outputs/cache/qc/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca import project_io, qc_markers  # noqa: E402
from gaga_jcvpca.config import load_config  # noqa: E402
from gaga_jcvpca.inventory import build_inventory  # noqa: E402
from gaga_jcvpca.naming import parse_session_id  # noqa: E402
from gaga_jcvpca.feature_manifest_gen import (  # noqa: E402
    DEFAULT_MANIFEST_BY_PARTICIPANT,
    resolve_manifest_path,
)
from gaga_jcvpca.rotations import (  # noqa: E402
    FilterSettings,
    build_link_map_from_bones,
    build_link_map_from_hierarchy,
    convert_session_take,
    resolve_link_pair,
)
from gaga_jcvpca.selection import link_stem  # noqa: E402

MANIFEST_BY_PARTICIPANT = DEFAULT_MANIFEST_BY_PARTICIPANT


def _bone_index_keys(take) -> set[str]:
    """Every name convert_session_take will accept for a bone (colon/underscore variants)."""
    keys: set[str] = set()
    for name in take.bone_names:
        keys.add(name)
        if ":" in name:
            keys.add(name.replace(":", "_", 1))
        elif "_" in name:
            keys.add(name.replace("_", ":", 1))
    return keys


def _count_resolvable(link_map, link_ids, take) -> int:
    """How many manifest link stems a candidate link_map can convert on this take."""
    keys = _bone_index_keys(take)
    n = 0
    for stem in link_ids:
        pair = resolve_link_pair(stem, link_map)
        if pair and pair[0] in keys and pair[1] in keys:
            n += 1
    return n


def _description_for_session(config, session_id: str) -> Path | None:
    """Exact per-session DataDescriptions sidecar, if it exists and has bones."""
    desc_dir = config.resolve_path("data.descriptions")
    if not desc_dir.exists():
        return None
    for path in project_io.find_description_files(desc_dir):
        key = parse_session_id(path.name)
        if key is not None and key.as_str() == session_id and project_io.sidecar_has_bones(path):
            return path
    return None


def _participant_sidecars(config, participant: str, timepoint: str) -> list[Path]:
    """Non-empty same-participant sidecars, same-timepoint first (prefix fallback)."""
    desc_dir = config.resolve_path("data.descriptions")
    if not desc_dir.exists():
        return []
    same_tp: list[Path] = []
    other_tp: list[Path] = []
    for path in project_io.find_description_files(desc_dir):
        key = parse_session_id(path.name)
        if key is None or key.participant != participant:
            continue
        if not project_io.sidecar_has_bones(path):
            continue
        (same_tp if key.timepoint == timepoint else other_tp).append(path)
    return same_tp + other_tp


def resolve_link_map(config, session_id: str, take, link_ids: list[str]) -> tuple[dict, str]:
    """Resolve the best skeleton link_map for a session and label its source.

    Order (each gated on how many manifest links it can actually convert on this
    take, so the 671-T3 marker-set confound and cross-participant mismatches are
    rejected automatically):
      1. exact per-session sidecar,
      2. same-participant sidecar (same timepoint first, then any),
      3. the session's own raw-skeleton header hierarchy (always available).
    """
    key = parse_session_id(session_id)
    participant = key.participant if key else session_id.split("_", 1)[0]
    timepoint = key.timepoint if key else ""
    n_target = len(link_ids)

    candidates: list[tuple[str, dict]] = []
    exact = _description_for_session(config, session_id)
    if exact is not None:
        candidates.append(
            (f"exact_sidecar:{exact.name}", build_link_map_from_bones(project_io.load_skeleton_bones(exact)))
        )
    for path in _participant_sidecars(config, participant, timepoint):
        if exact is not None and path == exact:
            continue
        candidates.append(
            (f"participant_sidecar:{path.name}", build_link_map_from_bones(project_io.load_skeleton_bones(path)))
        )
    raw_lm = build_link_map_from_hierarchy(
        project_io.read_skeleton_hierarchy_from_take(take.path)
    )
    candidates.append(("raw_skeleton_header", raw_lm))

    best_lm: dict = {}
    best_source = "none"
    best_n = -1
    for idx, (source, lm) in enumerate(candidates):
        n = _count_resolvable(lm, link_ids, take)
        # Prefer higher coverage; among ties keep the earlier (more authoritative)
        # candidate. Take a full-coverage candidate immediately.
        if n > best_n:
            best_n, best_lm, best_source = n, lm, source
        if best_n == n_target:
            break
    return best_lm, f"{best_source} ({best_n}/{n_target} links)"


def convert_one_session(config, session_id: str, skeleton_path: Path, log: list[dict]) -> None:
    participant = session_id.split("_", 1)[0]
    manifest_dir = config.resolve_path("data.feature_manifests")
    manifest_path = resolve_manifest_path(participant, manifest_dir, MANIFEST_BY_PARTICIPANT)
    if manifest_path is None:
        print(f"skip {session_id}: no feature manifest for participant {participant}")
        log.append({"session_id": session_id, "status": "skipped", "reason": "no feature manifest"})
        return

    features = project_io.feature_names_from_manifest(
        project_io.load_feature_manifest(manifest_path)
    )
    link_ids = sorted({link_stem(f) for f in features})

    take = project_io.parse_motive_take(skeleton_path)
    link_map, source = resolve_link_map(config, session_id, take, link_ids)
    if not link_map:
        print(f"skip {session_id}: no skeleton hierarchy could be resolved")
        log.append({"session_id": session_id, "status": "skipped", "reason": "no hierarchy"})
        return

    settings = FilterSettings.from_config(config)
    qc_thresholds = config.get("rotvec", {}) or {}

    links = convert_session_take(
        take,
        link_map,
        settings,
        qc_thresholds=qc_thresholds,
        link_ids=link_ids,
    )

    parts = [links[stem].to_feature_frame() for stem in link_ids if stem in links]
    if not parts:
        print(f"skip {session_id}: no link columns produced (source={source})")
        log.append({"session_id": session_id, "status": "skipped", "reason": "no link columns", "hierarchy_source": source})
        return

    matrix = pd.concat(parts, axis=1)
    out_dir = config.resolve_path("data.matrices")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{session_id}.parquet"
    matrix.to_parquet(out_path)
    print(f"wrote {out_path} ({matrix.shape}) via {source}")
    log.append(
        {
            "session_id": session_id,
            "status": "converted",
            "hierarchy_source": source,
            "n_links": len(parts),
            "n_manifest_links": len(link_ids),
            "n_frames": int(matrix.shape[0]),
            "skeleton_csv": skeleton_path.name,
        }
    )

    inv = build_inventory(config)
    findings, _, _ = qc_markers.run_marker_qc(
        config, inv, session_ids=[session_id], write_cache=False
    )
    if findings:
        qc_dir = config.resolve_path("outputs.cache") / "qc"
        qc_dir.mkdir(parents=True, exist_ok=True)
        qc_path = qc_dir / f"{session_id}.csv"
        qc_markers.findings_to_dataframe(findings).to_csv(qc_path, index=False)
        print(f"wrote {qc_path} ({len(findings)} findings)")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Convert raw skeleton CSVs to feature matrices.")
    parser.add_argument(
        "--participants", nargs="*", default=None,
        help="Restrict conversion to these participant ids (default: all ready).",
    )
    args = parser.parse_args()

    cfg = load_config()
    inv = build_inventory(cfg)
    ready = [r for r in inv.rows if r.status == "ready"]
    if args.participants:
        keep = set(args.participants)
        ready = [r for r in ready if r.participant in keep]
    if not ready:
        print("No ready sessions (need segmentation sheet + skeleton CSV).")
        return

    log: list[dict] = []
    for row in ready:
        skel = project_io.resolve_session_skeleton(cfg, row.session_id)
        if skel is None:
            print(f"skip {row.session_id}: skeleton path not found")
            log.append({"session_id": row.session_id, "status": "skipped", "reason": "skeleton path not found"})
            continue
        convert_one_session(cfg, row.session_id, skel, log)

    log_dir = cfg.resolve_path("outputs.cache")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "conversion_manifest.json"
    with open(log_path, "w", encoding="utf-8") as fh:
        json.dump(log, fh, indent=2)
    print(f"wrote conversion manifest: {log_path} ({len(log)} sessions)")


if __name__ == "__main__":
    main()
