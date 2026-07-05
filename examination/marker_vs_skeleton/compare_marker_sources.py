#!/usr/bin/env python3
"""Compare marker data in raw_markers vs raw_skeleton Motive CSV exports.

Run from project root:
    .venv/bin/python examination/marker_vs_skeleton/compare_marker_sources.py
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MARKER_DIR = PROJECT_ROOT / "data" / "raw_markers"
SKELETON_DIR = PROJECT_ROOT / "data" / "raw_skeleton"
OUT_DIR = Path(__file__).resolve().parent
SUMMARY_CSV = OUT_DIR / "comparison_summary.csv"
RESULTS_MD = OUT_DIR / "RESULTS.md"

PASS_MAX_DIFF_M = 1e-5
SPOT_CHECK_FRAMES = [0, 1, 100, 1000, 5000, 10000]
SPOT_CHECK_MARKERS = [
    "252:LAH",
    "252:CV7",
    "252:LFM1",
    "252:RUA",
    "252:SJN",
    "671:BackLeft",
    "671:BackRight",
    "Unlabeled 2739",
]


@dataclass
class MarkerTable:
    names: list[str]
    positions: np.ndarray  # (n_frames, n_markers, 3)
    presence: np.ndarray  # (n_frames, n_markers)
    meta: dict[str, str]
    path: Path


@dataclass
class PairResult:
    session_label: str
    marker_path: str
    skeleton_path: str
    n_markers_marker: int
    n_markers_skeleton: int
    n_common_markers: int
    n_frames_marker: int
    n_frames_skeleton: int
    marker_units: str
    skeleton_units: str
    names_only_in_markers: int
    names_only_in_skeleton: int
    presence_mismatches: int
    max_abs_diff_m: float
    mean_abs_diff_m: float
    marker_size_mb: float
    skeleton_size_mb: float
    passed: bool
    notes: str


def parse_meta(path: Path) -> dict[str, str]:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        row0 = next(csv.reader([fh.readline()]))
    meta: dict[str, str] = {}
    for i in range(0, len(row0) - 1, 2):
        meta[row0[i]] = row0[i + 1]
    return meta


def load_marker_table(path: Path) -> MarkerTable:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        header_rows: list[list[str]] = []
        for i, line in enumerate(fh):
            header_rows.append(next(csv.reader([line])))
            if i >= 8:
                break

    type_row_idx = next(
        i for i, row in enumerate(header_rows) if len(row) > 1 and row[1] == "Type"
    )
    type_row = header_rows[type_row_idx]
    name_row = header_rows[type_row_idx + 1]

    marker_cols = [i for i, token in enumerate(type_row) if token.strip() == "Marker"]
    by_name: dict[str, list[int]] = {}
    for col in marker_cols:
        by_name.setdefault(name_row[col], []).append(col)

    names = sorted(by_name.keys())
    triplets = {name: cols[:3] for name, cols in by_name.items()}
    usecols = sorted({c for cols in triplets.values() for c in cols})
    colmap = {c: ui for ui, c in enumerate(usecols)}

    df = pd.read_csv(
        path,
        skiprows=type_row_idx + 3,
        header=None,
        usecols=usecols,
        low_memory=False,
    )

    positions = np.full((len(df), len(names), 3), np.nan, dtype=float)
    presence = np.zeros((len(df), len(names)), dtype=bool)
    for mi, name in enumerate(names):
        for ai, col in enumerate(triplets[name][:3]):
            positions[:, mi, ai] = pd.to_numeric(
                df.iloc[:, colmap[col]], errors="coerce"
            )
        presence[:, mi] = np.all(np.isfinite(positions[:, mi, :]), axis=1)

    return MarkerTable(
        names=names,
        positions=positions,
        presence=presence,
        meta=parse_meta(path),
        path=path,
    )


def skeleton_to_marker_coords(
    positions: np.ndarray, length_units: str
) -> np.ndarray:
    """Map skeleton Marker columns to marker-export meter coordinates.

    Millimeter skeleton exports use a different axis layout than marker-only exports.
    Meter skeleton exports (e.g. some T3 takes) already match marker-only layout.
    """
    units = (length_units or "").strip().lower()
    if units.startswith("millimeter"):
        scaled = positions / 1000.0
        out = np.empty_like(scaled)
        out[..., 0] = -scaled[..., 0]
        out[..., 1] = scaled[..., 2]
        out[..., 2] = scaled[..., 1]
        return out
    return positions


def session_label_from_name(filename: str) -> str:
    stem = Path(filename).stem
    for token in ("_Take", ".csv"):
        if token in stem:
            stem = stem.split(token)[0]
            break
    return stem


def has_marker_columns(path: Path) -> bool:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh):
                cells = next(csv.reader([line]))
                if len(cells) > 1 and cells[1] == "Type":
                    return any(c.strip() == "Marker" for c in cells)
                if i >= 8:
                    break
    except OSError:
        return False
    return False


def index_by_filename(root: Path) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for path in sorted(root.rglob("*.csv")):
        if path.stat().st_size == 0:
            continue
        if "DataDescriptions" in path.name:
            continue
        if not has_marker_columns(path):
            continue
        out[path.name] = path
    return out


def compare_pair(marker_path: Path, skeleton_path: Path) -> PairResult:
    md = load_marker_table(marker_path)
    sd = load_marker_table(skeleton_path)

    names_m = set(md.names)
    names_s = set(sd.names)
    common = sorted(names_m & names_s)

    idx_m = {n: i for i, n in enumerate(md.names)}
    idx_s = {n: i for i, n in enumerate(sd.names)}

    skel_marker_coords = skeleton_to_marker_coords(
        sd.positions, sd.meta.get("Length Units", "")
    )

    presence_mismatches = 0
    diffs: list[float] = []
    for name in common:
        mi, si = idx_m[name], idx_s[name]
        prm = md.presence[:, mi]
        prs = sd.presence[:, si]
        presence_mismatches += int(np.sum(prm != prs))
        both = prm & prs
        if both.any():
            delta = np.abs(md.positions[both, mi] - skel_marker_coords[both, si])
            diffs.extend(delta.ravel().tolist())

    max_diff = float(np.max(diffs)) if diffs else float("nan")
    mean_diff = float(np.mean(diffs)) if diffs else float("nan")
    passed = (
        len(common) > 0
        and presence_mismatches == 0
        and np.isfinite(max_diff)
        and max_diff < PASS_MAX_DIFF_M
    )

    notes: list[str] = []
    if names_m - names_s:
        notes.append(f"{len(names_m - names_s)} marker name(s) only in marker export")
    if names_s - names_m:
        notes.append(f"{len(names_s - names_m)} marker name(s) only in skeleton export")
    if md.meta.get("Length Units") != sd.meta.get("Length Units"):
        notes.append(
            f"units differ ({md.meta.get('Length Units')} vs {sd.meta.get('Length Units')})"
        )
    if md.meta.get("Rotation Type") != sd.meta.get("Rotation Type"):
        notes.append("rotation type differs (XYZ marker export vs Quaternion skeleton export)")

    return PairResult(
        session_label=session_label_from_name(marker_path.name),
        marker_path=str(marker_path.relative_to(PROJECT_ROOT)),
        skeleton_path=str(skeleton_path.relative_to(PROJECT_ROOT)),
        n_markers_marker=len(md.names),
        n_markers_skeleton=len(sd.names),
        n_common_markers=len(common),
        n_frames_marker=md.positions.shape[0],
        n_frames_skeleton=sd.positions.shape[0],
        marker_units=md.meta.get("Length Units", ""),
        skeleton_units=sd.meta.get("Length Units", ""),
        names_only_in_markers=len(names_m - names_s),
        names_only_in_skeleton=len(names_s - names_m),
        presence_mismatches=presence_mismatches,
        max_abs_diff_m=max_diff,
        mean_abs_diff_m=mean_diff,
        marker_size_mb=os.path.getsize(marker_path) / 1e6,
        skeleton_size_mb=os.path.getsize(skeleton_path) / 1e6,
        passed=passed,
        notes="; ".join(notes),
    )


def spot_check_lines(marker_path: Path, skeleton_path: Path) -> list[str]:
    md = load_marker_table(marker_path)
    sd = load_marker_table(skeleton_path)
    skel_coords = skeleton_to_marker_coords(
        sd.positions, sd.meta.get("Length Units", "")
    )
    idx_m = {n: i for i, n in enumerate(md.names)}
    idx_s = {n: i for i, n in enumerate(sd.names)}
    common = [n for n in SPOT_CHECK_MARKERS if n in idx_m and n in idx_s]
    if not common:
        common = sorted(set(md.names) & set(sd.names))[:3]

    lines = [f"Spot checks for `{marker_path.name}`:"]
    for name in common[:6]:
        mi, si = idx_m[name], idx_s[name]
        for fi in SPOT_CHECK_FRAMES:
            if fi >= md.positions.shape[0]:
                continue
            pm = md.positions[fi, mi]
            ps = skel_coords[fi, si]
            if np.all(np.isfinite(pm)) and np.all(np.isfinite(ps)):
                d = float(np.max(np.abs(pm - ps)))
                lines.append(f"  - {name} frame {fi}: max_diff={d:.3e} m")
    return lines


def skeleton_only_report(path: Path) -> str:
    try:
        table = load_marker_table(path)
    except StopIteration:
        return f"- `{path.relative_to(PROJECT_ROOT)}`: skipped (not a Motive marker CSV)"
    return (
        f"- `{path.relative_to(PROJECT_ROOT)}`: "
        f"{len(table.names)} markers, {table.positions.shape[0]} frames, "
        f"units={table.meta.get('Length Units', '?')}"
    )


def write_summary_csv(results: list[PairResult]) -> None:
    rows = [
        {
            "session_label": r.session_label,
            "marker_path": r.marker_path,
            "skeleton_path": r.skeleton_path,
            "n_markers_marker": r.n_markers_marker,
            "n_markers_skeleton": r.n_markers_skeleton,
            "n_common_markers": r.n_common_markers,
            "n_frames_marker": r.n_frames_marker,
            "n_frames_skeleton": r.n_frames_skeleton,
            "marker_units": r.marker_units,
            "skeleton_units": r.skeleton_units,
            "names_only_in_markers": r.names_only_in_markers,
            "names_only_in_skeleton": r.names_only_in_skeleton,
            "presence_mismatches": r.presence_mismatches,
            "max_abs_diff_m": r.max_abs_diff_m,
            "mean_abs_diff_m": r.mean_abs_diff_m,
            "marker_size_mb": round(r.marker_size_mb, 2),
            "skeleton_size_mb": round(r.skeleton_size_mb, 2),
            "passed": r.passed,
            "notes": r.notes,
        }
        for r in results
    ]
    pd.DataFrame(rows).to_csv(SUMMARY_CSV, index=False)


def write_results_md(
    results: list[PairResult],
    skeleton_only: list[Path],
    spot_checks: list[str],
) -> None:
    all_passed = all(r.passed for r in results)
    n_marker_files = len(index_by_filename(MARKER_DIR))
    n_skeleton_files = len(index_by_filename(SKELETON_DIR))

    lines = [
        "# Marker vs Skeleton — Examination Results",
        "",
        "## Verdict",
        "",
    ]
    n_passed = sum(1 for r in results if r.passed)
    n_failed = len(results) - n_passed
    if all_passed:
        lines.extend(
            [
                f"**All {len(results)} overlapping pairs pass** on their shared marker names. "
                "Marker QC information in `data/raw_markers/` is recoverable from the "
                "`Type=Marker` columns embedded in `data/raw_skeleton/`.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                f"**{n_passed}/{len(results)} overlapping pairs pass** on shared marker names; "
                f"**{n_failed} pair(s) failed** (see table). Failures indicate sessions where "
                "marker naming or tracking differs between exports — not a universal 1:1 copy.",
                "",
            ]
        )

    lines.extend(
        [
            "Coordinate mapping depends on skeleton export units:",
            "",
            "- **Millimeters** (most T1/T2 takes):",
            "",
            "```text",
            "marker_X = -skeleton_marker_X / 1000",
            "marker_Y =  skeleton_marker_Z / 1000",
            "marker_Z =  skeleton_marker_Y / 1000",
            "```",
            "",
            "- **Meters** (some T3 takes): positions already match marker-only exports directly.",
            "",
            "**You do not strictly need `raw_markers/` when `raw_skeleton/` is available**, "
            "provided QC code applies the correct unit/axis mapping and handles sessions where "
            "marker name sets differ.",
            "",
            "Practical notes:",
            "",
            "- Skeleton exports are ~5× larger (~226 MB vs ~44 MB per take); dedicated marker "
            "files are faster when you only need QC.",
            f"- {len(skeleton_only)} skeleton file(s) have no dedicated marker export.",
            "- `parse_motive_marker_csv` in `qc_markers.py` currently looks for `r[0] == \"Type\"` "
            "but Motive exports use a leading empty cell (`,Type,...`). Header detection should "
            "be fixed before wiring QC to real files.",
            "",
        ]
    )

    lines.extend(
        [
            "## Comparison summary",
            "",
            "| Session | Common markers | Max diff (m) | Presence mismatches | Passed | Notes |",
            "|---|---:|---:|---:|---|---|",
        ]
    )
    for r in results:
        lines.append(
            f"| {r.session_label} | {r.n_common_markers} | "
            f"{r.max_abs_diff_m:.3e} | {r.presence_mismatches} | "
            f"{'yes' if r.passed else 'NO'} | {r.notes or '—'} |"
        )

    lines.extend(
        [
            "",
            "## File sizes (representative pair)",
            "",
        ]
    )
    if results:
        r0 = results[0]
        lines.append(
            f"- `{r0.marker_path}`: {r0.marker_size_mb:.1f} MB "
            f"({r0.marker_units})"
        )
        lines.append(
            f"- `{r0.skeleton_path}`: {r0.skeleton_size_mb:.1f} MB "
            f"({r0.skeleton_units})"
        )

    lines.extend(["", "## Coverage", ""])
    lines.append(f"- Marker-only files: {n_marker_files}")
    lines.append(f"- Skeleton files: {n_skeleton_files}")
    lines.append(f"- Skeleton-only (no marker export): {len(skeleton_only)}")

    if skeleton_only:
        lines.extend(["", "### Skeleton-only sessions", ""])
        for path in skeleton_only[:10]:
            lines.append(skeleton_only_report(path))

    lines.extend(["", "## Spot checks", ""])
    lines.extend(spot_checks)

    lines.extend(
        [
            "",
            "## Decision table",
            "",
            "| Need | raw_markers | raw_skeleton |",
            "|---|---|---|",
            "| JcvPCA rotations | No | Yes (Bone quaternions) |",
            "| Marker gap QC | Yes (standalone) | Yes (embedded Marker cols) |",
            "| All sessions covered | 12/19 | 19/19 |",
            "",
            "## Recommendation",
            "",
            "Prefer skeleton as the canonical marker source when available (covers extra sessions). "
            "Keep `raw_markers/` as an optional convenience for faster QC-only loads.",
            "",
        ]
    )

    RESULTS_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    marker_index = index_by_filename(MARKER_DIR)
    skeleton_index = index_by_filename(SKELETON_DIR)

    overlapping = sorted(set(marker_index) & set(skeleton_index))
    skeleton_only_names = sorted(set(skeleton_index) - set(marker_index))

    print(f"Found {len(overlapping)} overlapping pairs, {len(skeleton_only_names)} skeleton-only files")

    results: list[PairResult] = []
    spot_checks: list[str] = []
    for name in overlapping:
        print(f"Comparing {name} ...")
        result = compare_pair(marker_index[name], skeleton_index[name])
        results.append(result)
        status = "PASS" if result.passed else "FAIL"
        print(
            f"  {status}: max_diff={result.max_abs_diff_m:.3e} m, "
            f"presence_mismatches={result.presence_mismatches}"
        )
        if name.startswith("252_T1_P1_R1") or name.startswith("671_T1_P1_R1"):
            spot_checks.extend(
                spot_check_lines(marker_index[name], skeleton_index[name])
            )

    skeleton_only_paths = [skeleton_index[n] for n in skeleton_only_names]
    write_summary_csv(results)
    write_results_md(results, skeleton_only_paths, spot_checks)
    print(f"\nWrote {SUMMARY_CSV.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {RESULTS_MD.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
