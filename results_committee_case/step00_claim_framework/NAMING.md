# Naming vocabulary lock (Step 0)

**Effective:** 2026-07-14  
**Rule:** Use only the terms below in committee docs, configs (new), UI, and new code. Legacy exploration artifacts may retain old config snapshots; do not cite them for naming.

---

## Two namespaces only

| Namespace | Symbol | Meaning | Example |
|---|---|---|---|
| **Task part** | `P1`, `P2`, … | Task Part in session key | `671_T1_P1_R1` → Task Part **1** |
| **Exercise** | `ex{NN}` | Canonical exercise from segmentation `exercise_id` | `ex09`, `ex13` |

**There is no third namespace.** Do not use P1–P5 to label exercises 9–13.

---

## Correct usage

| Context | Use | Do not use |
|---|---|---|
| Session / file | `671_T2_P1_R2` | “P3 session” for exercise 11 |
| Exercise reference | `ex09`, `ex10`–`ex13` | “P1 exercise” for ex09 |
| Combined window | `ex09_13_contiguous` | “P1–P5 block” |
| Movement grouping | `Group4` (ex09–ex13) | Gaga alias P1–P5 |
| Full session scope | “Task Part 1 covers ex01–ex17” | “P1 means ex09” |

---

## Movement groups (display only)

From `configs/exercise_map.yaml` — contiguous `exercise_id` ranges within Task Part 1:

| Group | exercise_ids | Name |
|---|---|---|
| Group1 | 1–2 | Trunk sagittal movement |
| Group2 | 3–5 | Upper-limb elevation and arm wave |
| Group3 | 6–8 | Axial rotation and reciprocal arm rotation |
| Group4 | 9–13 | Curvilinear exploration |
| Group5 | 14–15 | Single-leg balance with whole-body curves |
| Group6 | 16–17 | Whole-body shaking / dance |

**Primary analysis window:** Group4 = `ex09`–`ex13` combined.

---

## Removed from project (Step 0)

- Config key `gaga_group4_aliases` — **deleted** from `configs/exercise_map.yaml`
- Code field `gaga_alias` on `ExerciseSegment` — **removed**
- UI column `gaga_alias` — **removed**
- `NamingMap.gaga_alias_of()` — **removed**

Inventory and segmentation tables show: `exercise_id`, `canonical_label`, `group_id`, `exercise_name`.

---

## Code / config touchpoints updated

- `configs/exercise_map.yaml`
- `src/gaga_jcvpca/naming.py`
- `src/gaga_jcvpca/schemas.py`
- `src/gaga_jcvpca/project_io.py`
- `src/gaga_jcvpca/inventory.py`
- `ui/app.py`
- `tests/test_naming.py`, `tests/test_project_io.py`, `tests/test_pipeline_snapshot.py`

Historical `config_snapshot.yaml` files under `results_exploration_671_252/` are unchanged (frozen runs).
