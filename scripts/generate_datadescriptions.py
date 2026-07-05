"""Generate Motive DataDescriptions sidecars from skeleton CSV header hierarchy.

Reads the Bone Name/Parent rows in a Motive skeleton export and writes a minimal
``*_DataDescriptions.csv`` file with bone hierarchy (enough for rotation conversion).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca.project_io import DESCRIPTION_SUFFIX, _find_frame_row, _find_type_row, _read_motive_header_rows


def _canon_bone_name(name: str) -> str:
    """Map skeleton export names (671:Chest) to DataDescriptions form (671_Chest)."""
    if ":" in name:
        return name.replace(":", "_", 1)
    return name


def generate_datadescriptions(skeleton_path: Path, out_path: Path) -> None:
    rows = _read_motive_header_rows(skeleton_path, max_rows=12)
    type_row_idx = _find_type_row(rows)
    type_row = rows[type_row_idx]
    name_row = rows[type_row_idx + 1]
    parent_row = rows[type_row_idx + 3]

    bones_ordered: list[str] = []
    parent_of: dict[str, str] = {}
    for i, kind in enumerate(type_row):
        if kind.strip() != "Bone":
            continue
        if i >= len(name_row):
            break
        name = name_row[i].strip()
        if not name or name in parent_of:
            continue
        parent = parent_row[i].strip() if i < len(parent_row) else ""
        bones_ordered.append(name)
        parent_of[name] = parent

    if not bones_ordered:
        raise ValueError(f"No Bone columns found in {skeleton_path}")

    index_of = {_canon_bone_name(name): idx + 1 for idx, name in enumerate(bones_ordered)}
    root_name = _canon_bone_name(bones_ordered[0])
    participant = root_name.split("_", 1)[0]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(f"Skeleton,{participant},0,\n")
        for name in bones_ordered:
            bone_name = _canon_bone_name(name)
            parent_raw = parent_of.get(name, "")
            if parent_raw in {"", "Root"}:
                parent_idx = 0
            else:
                parent_idx = index_of.get(_canon_bone_name(parent_raw), 0)
            fh.write(
                f"Bone,{bone_name},{index_of[bone_name]},{parent_idx},0,0,0,{participant}\n"
            )
        fh.write(f"Marker set,{participant},\n")


def main() -> None:
    desc_dir = ROOT / "data" / "descriptions"
    for participant in ("651", "790"):
        skel_dir = ROOT / "data" / "raw_skeleton" / participant
        for skeleton_path in sorted(skel_dir.glob("*.csv")):
            if "DataDescriptions" in skeleton_path.name:
                continue
            out_path = desc_dir / f"{skeleton_path.stem}{DESCRIPTION_SUFFIX}"
            generate_datadescriptions(skeleton_path, out_path)
            print(f"wrote {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
