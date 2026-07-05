"""Convert raw skeleton CSVs to rotation-vector matrices (one parse per session).

Reads marker QC data and bone quaternions from the same Motive skeleton export,
writes feature parquets under data.matrices and optional QC CSVs under
outputs/cache/qc/.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca import project_io, qc_markers  # noqa: E402
from gaga_jcvpca.config import load_config  # noqa: E402
from gaga_jcvpca.inventory import build_inventory  # noqa: E402
from gaga_jcvpca.feature_manifest_gen import (  # noqa: E402
    DEFAULT_MANIFEST_BY_PARTICIPANT,
    resolve_manifest_path,
)
from gaga_jcvpca.rotations import FilterSettings, build_link_map_from_bones, convert_session_take  # noqa: E402
from gaga_jcvpca.selection import link_stem  # noqa: E402

MANIFEST_BY_PARTICIPANT = DEFAULT_MANIFEST_BY_PARTICIPANT


def _description_for_session(config, session_id: str) -> Path | None:
    desc_dir = config.resolve_path("data.descriptions")
    if not desc_dir.exists():
        return None
    for path in project_io.find_description_files(desc_dir):
        from gaga_jcvpca.naming import parse_session_id

        key = parse_session_id(path.name)
        if key is not None and key.as_str() == session_id:
            return path
    return None


def convert_one_session(config, session_id: str, skeleton_path: Path) -> None:
    participant = session_id.split("_", 1)[0]
    manifest_dir = config.resolve_path("data.feature_manifests")
    manifest_path = resolve_manifest_path(participant, manifest_dir, MANIFEST_BY_PARTICIPANT)
    if manifest_path is None:
        print(f"skip {session_id}: no feature manifest for participant {participant}")
        return

    features = project_io.feature_names_from_manifest(
        project_io.load_feature_manifest(manifest_path)
    )
    link_ids = sorted({link_stem(f) for f in features})

    desc_path = _description_for_session(config, session_id)
    if desc_path is None:
        print(f"skip {session_id}: no DataDescriptions sidecar")
        return

    take = project_io.parse_motive_take(skeleton_path)
    bones = project_io.load_skeleton_bones(desc_path)
    link_map = build_link_map_from_bones(bones)
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
        print(f"skip {session_id}: no link columns produced")
        return

    matrix = pd.concat(parts, axis=1)
    out_dir = config.resolve_path("data.matrices")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{session_id}.parquet"
    matrix.to_parquet(out_path)
    print(f"wrote {out_path} ({matrix.shape})")

    inv = build_inventory(config)
    findings, _ = qc_markers.run_marker_qc(
        config, inv, session_ids=[session_id], write_cache=False
    )
    if findings:
        qc_dir = config.resolve_path("outputs.cache") / "qc"
        qc_dir.mkdir(parents=True, exist_ok=True)
        qc_path = qc_dir / f"{session_id}.csv"
        qc_markers.findings_to_dataframe(findings).to_csv(qc_path, index=False)
        print(f"wrote {qc_path} ({len(findings)} findings)")


def main() -> None:
    cfg = load_config()
    inv = build_inventory(cfg)
    ready = [r for r in inv.rows if r.status == "ready"]
    if not ready:
        print("No ready sessions (need segmentation sheet + skeleton CSV).")
        return

    for row in ready:
        skel = project_io.resolve_session_skeleton(cfg, row.session_id)
        if skel is None:
            print(f"skip {row.session_id}: skeleton path not found")
            continue
        convert_one_session(cfg, row.session_id, skel)


if __name__ == "__main__":
    main()
