# QC policy — Step 3 (inclusive)

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

---

## Marker-gap advisory layer (wired in pipeline)

**Source table:** `marker_gap_link_removals_ex09_13.csv` (17 `remove_from_comparison` rows + 16 `watch`).  
**Regenerate:** `scripts/build_marker_gap_link_removals.py`

Session-scoped exclusions applied at **comparison time** when `analysis.apply_marker_gap_removals: true` (default in `analysis_defaults.yaml`). Does **not** change selection YAML.

| Tier | Rule | Pipeline effect |
|---|---|---|
| **remove_from_comparison** | max supporting-marker gap ≥10% **or** ≥2 markers ≥5% | Link dropped from comparisons using that session/rep |
| **watch** | gap 5–10% | Document only; not auto-dropped |

Recorded in `ComparisonResult.excluded_links` with prefix `marker_gap_policy:` and in `run_summary.md` / `marker_gap_excluded_links.json`.

See `docs/MARKER_GAP_REMOVAL_WIRING.md` for full wiring notes.
