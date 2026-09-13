"""Step 3 — trunk-inclusive convert, inclusive link QC, selection YAMLs.

Produces:
  - results_committee_case/step03_trunk_extension/QC_POLICY.md
  - results_committee_case/step03_trunk_extension/TRUNK_QC.md
  - results_committee_case/step03_trunk_extension/LINK_INVENTORY.md
  - results_committee_case/step03_trunk_extension/link_qc_results.csv
  - results_committee_case/step03_trunk_extension/selections/{pid}_ex09_13_contiguous.yaml
  - outputs/selections/{pid}_ex09_13_contiguous.yaml  (for run_analysis.py)

Usage:
  PYTHONPATH=src .venv/bin/python scripts/run_step03_trunk_qc.py
  PYTHONPATH=src .venv/bin/python scripts/run_step03_trunk_qc.py --skip-convert
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca.config import load_config
from gaga_jcvpca.feature_manifest_gen import (
    TopologyKind,
    resolve_manifest_path,
    _sample_skeleton_for_participant,
    parse_skeleton_hierarchy,
    assess_topology,
    load_reference_hierarchies,
)
from gaga_jcvpca.inventory import build_inventory
from gaga_jcvpca import project_io
from gaga_jcvpca.pipeline import slice_matrix_to_exercises, _segments_by_session
from gaga_jcvpca.rotations import frame_to_frame_rotvec_jumps
from gaga_jcvpca.schemas import Recommendation
from gaga_jcvpca.selection import (
    AnalysisSelection,
    LinkChoice,
    link_stem,
    region_of_link,
    save_selection,
)

PARTICIPANTS = ("671", "252", "651", "790")
EXERCISE_IDS = [9, 10, 11, 12, 13]
VAR_EPS = 1e-10

TRUNK_STEMS_A = ("{pid}_to_Ab", "Ab_to_Chest")
TRUNK_STEMS_B = (
    "{pid}_to_Ab",
    "Ab_to_Spine2",
    "Spine2_to_Spine3",
    "Spine3_to_Spine4",
    "Spine4_to_Chest",
)


@dataclass(frozen=True)
class LinkQCResult:
    participant: str
    session_id: str
    link: str
    region: str
    is_trunk: bool
    n_frames: int
    non_finite_frac: float
    variance: float
    jump_frac: float
    status: str  # include | include_with_caution | exclude
    reason: str


def _trunk_stems_for(pid: str, kind: TopologyKind) -> set[str]:
    if kind == TopologyKind.STYLE_671_14LINK:
        return {s.format(pid=pid) for s in TRUNK_STEMS_A}
    return {s.format(pid=pid) for s in TRUNK_STEMS_B}


def _classify_link_slice(
    rotvec: np.ndarray,
    *,
    jump_warning: float,
    jump_fail: float,
    columns_present: bool,
) -> tuple[str, str]:
    if not columns_present:
        return "exclude", "bone/link columns absent in matrix"
    n = rotvec.shape[0]
    if n == 0:
        return "exclude", "zero frames in ex09_13 window"

    finite = np.isfinite(rotvec).all(axis=1)
    non_finite_frac = float(1.0 - finite.mean())
    if non_finite_frac > 0.20:
        return "exclude", f">{non_finite_frac:.0%} non-finite frames in window"

    rv = rotvec[finite]
    if rv.size == 0:
        return "exclude", "all frames non-finite in window"

    variance = float(np.nanvar(rv))
    if variance < VAR_EPS:
        return "exclude", "near-constant rotvec (variance below epsilon)"

    jumps = frame_to_frame_rotvec_jumps(rv)
    jump_frac = float((jumps > jump_fail).mean()) if jumps.size else 0.0
    jump_warn_frac = float((jumps > jump_warning).mean()) if jumps.size else 0.0

    if jump_frac > 0.05:
        return "include_with_caution", f"elevated jump rate ({jump_frac:.1%} frames > jump_fail)"
    if non_finite_frac > 0.05:
        return "include_with_caution", f"partial missing data ({non_finite_frac:.1%} non-finite)"
    if jump_warn_frac > 0.10:
        return "include_with_caution", f"moderate jumps ({jump_warn_frac:.1%} > jump_warning)"
    return "include", "finite, sufficient variance, acceptable jumps"


def _aggregate_status(results: list[LinkQCResult]) -> tuple[str, str]:
    """Participant-level status: T1 (reference) gates inclusion; later timepoints → caution."""
    order = {"exclude": 2, "include_with_caution": 1, "include": 0}
    t1 = [r for r in results if "_T1_" in r.session_id]
    if not t1:
        worst = max(results, key=lambda r: order[r.status])
        return worst.status, worst.reason

    t1_worst = max(t1, key=lambda r: order[r.status])
    if t1_worst.status == "exclude":
        return "exclude", f"hard-fail on T1 ({t1_worst.reason})"

    non_t1 = [r for r in results if "_T1_" not in r.session_id]
    if not non_t1:
        return "include", "passes inclusive QC on T1"

    non_t1_worst = max(non_t1, key=lambda r: order[r.status])
    if non_t1_worst.status == "exclude":
        n = sum(1 for r in non_t1 if r.status == "exclude")
        return (
            "include_with_caution",
            f"absent or hard-fail on {n}/{len(non_t1)} non-T1 session(s); "
            f"T1 OK — shared-link restriction applies at comparison time",
        )
    if non_t1_worst.status == "include_with_caution" or t1_worst.status == "include_with_caution":
        return "include_with_caution", f"caution on follow-up timepoint(s): {non_t1_worst.reason}"
    return "include", "passes inclusive QC on all sessions"


def qc_session_links(
    config,
    participant: str,
    session_id: str,
    link_stems: list[str],
    trunk_stems: set[str],
) -> list[LinkQCResult]:
    matrix_path = config.resolve_path("data.matrices") / f"{session_id}.parquet"
    if not matrix_path.exists():
        return [
            LinkQCResult(
                participant=participant,
                session_id=session_id,
                link=stem,
                region=region_of_link(stem, config),
                is_trunk=stem in trunk_stems,
                n_frames=0,
                non_finite_frac=1.0,
                variance=0.0,
                jump_frac=0.0,
                status="exclude",
                reason="matrix not converted",
            )
            for stem in link_stems
        ]

    df = pd.read_parquet(matrix_path)
    segments = _segments_by_session(config).get(session_id, [])
    sliced = slice_matrix_to_exercises(df, segments, EXERCISE_IDS)

    rot_cfg = config.get("rotvec", {}) or {}
    jump_warning = float(rot_cfg.get("jump_warning_rad", 0.5))
    jump_fail = float(rot_cfg.get("jump_fail_rad", 1.0))

    out: list[LinkQCResult] = []
    for stem in link_stems:
        cols = [f"{stem}_rx", f"{stem}_ry", f"{stem}_rz"]
        present = all(c in sliced.columns for c in cols)
        if present:
            rotvec = sliced[cols].to_numpy(dtype=float)
            n_frames = int(len(rotvec))
            finite = np.isfinite(rotvec).all(axis=1)
            non_finite_frac = float(1.0 - finite.mean()) if n_frames else 1.0
            rv = rotvec[finite] if finite.any() else rotvec
            variance = float(np.nanvar(rv)) if rv.size else 0.0
            jumps = frame_to_frame_rotvec_jumps(rv) if rv.size else np.array([])
            jump_frac = float((jumps > jump_fail).mean()) if jumps.size else 0.0
            status, reason = _classify_link_slice(
                rotvec,
                jump_warning=jump_warning,
                jump_fail=jump_fail,
                columns_present=True,
            )
        else:
            n_frames = 0
            non_finite_frac = 1.0
            variance = 0.0
            jump_frac = 0.0
            status, reason = "exclude", "bone/link columns absent in matrix"

        out.append(
            LinkQCResult(
                participant=participant,
                session_id=session_id,
                link=stem,
                region=region_of_link(stem, config),
                is_trunk=stem in trunk_stems,
                n_frames=n_frames,
                non_finite_frac=non_finite_frac,
                variance=variance,
                jump_frac=jump_frac,
                status=status,
                reason=reason,
            )
        )
    return out


def build_selection(
    config,
    participant: str,
    link_stems: list[str],
    aggregated: dict[str, tuple[str, str]],
) -> AnalysisSelection:
    choices: list[LinkChoice] = []
    for stem in sorted(link_stems):
        status, reason = aggregated[stem]
        region = region_of_link(stem, config)
        included = status != "exclude"
        if status == "include":
            qc_rec = Recommendation.INCLUDE.value
            msg = f"Inclusive QC pass on ex09_13 ({reason})."
        elif status == "include_with_caution":
            qc_rec = Recommendation.INCLUDE_WITH_CAUTION.value
            msg = f"Inclusive QC caution on ex09_13 ({reason})."
        else:
            qc_rec = Recommendation.EXCLUDE.value
            msg = f"Hard exclusion on ex09_13 ({reason})."
        choices.append(
            LinkChoice(
                link=stem,
                region=region,
                included=included,
                reason=msg,
                qc_recommendation=qc_rec,
            )
        )
    return AnalysisSelection(
        name=f"{participant}_ex09_13_contiguous",
        participant=participant,
        exercise_ids=EXERCISE_IDS,
        combine_exercises=True,
        links=choices,
        notes=(
            "Step 3 committee selection: full feasible link set (trunk-inclusive) "
            f"on ex09_13_contiguous. Policy: maximize inclusion; caution links retained "
            f"for Step 4b QC-drop axis."
        ),
        created_at=datetime.now().isoformat(timespec="seconds"),
    )


def write_qc_policy_md(path: Path) -> None:
    path.write_text(
        """# QC policy — Step 3 (inclusive)

**Effective:** Step 3 trunk extension  
**Window:** `ex09_13_contiguous` (exercise_ids 9–13)  
**Goal:** Maximize included links; exclude only clearly un-analyzable segments.

---

## Decision tiers (per link × session × window)

| Tier | Criteria | Selection YAML |
|---|---|---|
| **Include** (default) | Columns present; ≤5% non-finite; variance > ε; jump rate acceptable | `included: true`, `qc_recommendation: include` |
| **Include with caution** | 5–20% non-finite **or** elevated jumps (moderate `jump_warning` / `jump_fail` rate) | `included: true`, `qc_recommendation: include_with_caution` |
| **Exclude** (hard only) | Columns absent; >20% non-finite; near-constant (var < 1e-10); matrix missing | `included: false`, `qc_recommendation: exclude` |

---

## Thresholds (from `configs/qc_thresholds.yaml`)

| Parameter | Value | Role |
|---|---:|---|
| `rotvec.jump_warning_rad` | 0.5 | Caution signal |
| `rotvec.jump_fail_rad` | 1.0 | Large jump / branch-cut flag |
| Non-finite caution | >5% | `include_with_caution` |
| Non-finite exclude | >20% | hard exclude |
| Variance floor ε | 1e-10 | near-constant exclude |

---

## Trunk links (mandatory where bones exist)

**Setup A (671, 651):** `{pid}_to_Ab`, `Ab_to_Chest`  
**Setup B (252, 790):** `{pid}_to_Ab`, `Ab_to_Spine2`, `Spine2_to_Spine3`, `Spine3_to_Spine4`, `Spine4_to_Chest`

Trunk links are **not** exempt from QC — they follow the same tiers. A trunk hard-fail is documented and excluded link-only (never whole-region drop).

---

## Aggregation rule (participant selection YAML)

Per link, QC is run on **every session** in the `ex09_13` window. Participant-level status:

1. If **T1** hard-fails → exclude link from selection.
2. Else if non-T1 sessions hard-fail (e.g. missing columns) → `include_with_caution` (retained; pipeline shared-link restriction at comparison time).
3. Else if any session is caution → `include_with_caution`.
4. Else → include.

---

## Distal exclusion (unchanged)

Finger/toe links are not in manifests (filtered at Step 2 feasible enumeration).

---

## Session confounds

- **671 T3** marker-set prefix differs — link may pass T1 but caution/fail T3; cross-timepoint comparisons use shared valid links automatically in pipeline.
- Missing DataDescriptions sidecars: conversion uses raw skeleton header hierarchy (verified in Step 2).
""",
        encoding="utf-8",
    )


def write_trunk_qc_md(path: Path, all_results: list[LinkQCResult], participants_meta: dict) -> None:
    lines = [
        "# Trunk QC summary — Step 3",
        "",
        f"**Generated:** {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Per participant (T1 R1 trunk links)",
        "",
        "| Participant | Setup | Trunk link | Status | n_frames | Notes |",
        "|---|---|---|---|---:|---|",
    ]
    for pid in PARTICIPANTS:
        setup = participants_meta[pid]["setup"]
        t1r1 = f"{pid}_T1_P1_R1"
        trunk = participants_meta[pid]["trunk_stems"]
        for r in all_results:
            if r.participant == pid and r.session_id == t1r1 and r.link in trunk:
                lines.append(
                    f"| {pid} | {setup} | `{r.link}` | {r.status} | {r.n_frames} | {r.reason} |"
                )

    lines.extend(["", "## Gate check (Step 3 → Step 4)", ""])
    for pid in PARTICIPANTS:
        t1r1 = f"{pid}_T1_P1_R1"
        trunk = participants_meta[pid]["trunk_stems"]
        trunk_rows = [
            r for r in all_results if r.participant == pid and r.session_id == t1r1 and r.link in trunk
        ]
        n_ok = sum(1 for r in trunk_rows if r.status != "exclude")
        gate = "PASS" if n_ok == len(trunk) else "PARTIAL"
        lines.append(
            f"- **{pid}:** {n_ok}/{len(trunk)} trunk links present on T1 R1 — **{gate}**"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_link_inventory_md(path: Path, aggregated: dict[str, dict[str, tuple[str, str]]]) -> None:
    lines = [
        "# Link inventory — Step 3",
        "",
        "Participant-level selection status after inclusive QC on `ex09_13`.",
        "",
    ]
    for pid in PARTICIPANTS:
        lines.append(f"## {pid}")
        lines.append("")
        lines.append("| Link | Region | Included | QC status | Reason |")
        lines.append("|---|---|---|---|---|")
        for stem, (status, reason) in sorted(aggregated[pid].items()):
            region = region_of_link(stem, load_config())
            included = "yes" if status != "exclude" else "no"
            lines.append(f"| `{stem}` | {region} | {included} | {status} | {reason} |")
        n_in = sum(1 for s, _ in aggregated[pid].items() if aggregated[pid][s][0] != "exclude")
        n_caution = sum(
            1 for s, _ in aggregated[pid].items() if aggregated[pid][s][0] == "include_with_caution"
        )
        lines.append("")
        lines.append(
            f"**Summary:** {n_in}/{len(aggregated[pid])} links included "
            f"({n_caution} with caution)."
        )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def run_convert_all(config, participants: list[str]) -> list[dict]:
    import importlib.util

    convert_path = ROOT / "scripts" / "run_convert.py"
    spec = importlib.util.spec_from_file_location("run_convert_mod", convert_path)
    run_convert_mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(run_convert_mod)
    convert_one_session = run_convert_mod.convert_one_session

    inv = build_inventory(config)
    ready = [r for r in inv.rows if r.status == "ready" and r.participant in participants]
    log: list[dict] = []
    for row in ready:
        skel = project_io.resolve_session_skeleton(config, row.session_id)
        if skel is None:
            log.append({"session_id": row.session_id, "status": "skipped", "reason": "no skeleton"})
            continue
        convert_one_session(config, row.session_id, skel, log)
    log_path = config.resolve_path("outputs.cache") / "conversion_manifest.json"
    log_path.write_text(json.dumps(log, indent=2), encoding="utf-8")
    return log


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-convert", action="store_true")
    parser.add_argument(
        "--participants", nargs="*", default=list(PARTICIPANTS),
    )
    args = parser.parse_args()

    config = load_config()
    out_dir = ROOT / "results_committee_case" / "step03_trunk_extension"
    sel_out = out_dir / "selections"
    outputs_sel = config.resolve_path("outputs.root") / "selections"
    manifest_dir = config.resolve_path("data.feature_manifests")

    refs = load_reference_hierarchies(config)
    participants_meta: dict[str, dict] = {}

    if not args.skip_convert:
        print("Converting all ready sessions...")
        log = run_convert_all(config, args.participants)
        converted = sum(1 for x in log if x.get("status") == "converted")
        print(f"Converted {converted}/{len(log)} sessions")

    inv = build_inventory(config)
    all_results: list[LinkQCResult] = []
    aggregated: dict[str, dict[str, tuple[str, str]]] = {}

    for pid in args.participants:
        sample = _sample_skeleton_for_participant(config.resolve_path("data.raw_skeleton"), pid)
        kind = assess_topology(parse_skeleton_hierarchy(sample), refs).kind
        setup = "A" if kind == TopologyKind.STYLE_671_14LINK else "B"
        trunk_stems = _trunk_stems_for(pid, kind)
        participants_meta[pid] = {"setup": setup, "trunk_stems": trunk_stems}

        manifest_path = resolve_manifest_path(pid, manifest_dir)
        manifest = project_io.load_feature_manifest(manifest_path)
        stems = sorted({link_stem(f) for f in project_io.feature_names_from_manifest(manifest)})

        by_link: dict[str, list[LinkQCResult]] = defaultdict(list)
        sessions = [r.session_id for r in inv.rows if r.participant == pid and r.status == "ready"]
        for sid in sessions:
            rows = qc_session_links(config, pid, sid, stems, trunk_stems)
            all_results.extend(rows)
            for r in rows:
                by_link[r.link].append(r)

        aggregated[pid] = {stem: _aggregate_status(by_link[stem]) for stem in stems}
        selection = build_selection(config, pid, stems, aggregated[pid])
        p1 = save_selection(selection, sel_out)
        p2 = save_selection(selection, outputs_sel)
        n_in = len(selection.included_links())
        print(f"{pid}: selection {n_in}/{len(stems)} links → {p1.relative_to(ROOT)}")

    # CSV inventory
    csv_path = out_dir / "link_qc_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "participant", "session_id", "link", "region", "is_trunk",
                "n_frames", "non_finite_frac", "variance", "jump_frac",
                "status", "reason",
            ],
        )
        writer.writeheader()
        for r in all_results:
            writer.writerow(
                {
                    "participant": r.participant,
                    "session_id": r.session_id,
                    "link": r.link,
                    "region": r.region,
                    "is_trunk": r.is_trunk,
                    "n_frames": r.n_frames,
                    "non_finite_frac": f"{r.non_finite_frac:.4f}",
                    "variance": f"{r.variance:.6g}",
                    "jump_frac": f"{r.jump_frac:.4f}",
                    "status": r.status,
                    "reason": r.reason,
                }
            )

    write_qc_policy_md(out_dir / "QC_POLICY.md")
    write_trunk_qc_md(out_dir / "TRUNK_QC.md", all_results, participants_meta)
    write_link_inventory_md(out_dir / "LINK_INVENTORY.md", aggregated)

    print(f"Wrote {out_dir.relative_to(ROOT)}/ (QC docs + selections + link_qc_results.csv)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
