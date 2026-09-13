# Experimental design — vocabulary for analysis

**Step 0 deliverable.** Defines session structure and primary analysis window for v4/v5/v6.

---

## Session identity

Canonical session key:

```
{participant}_T{timepoint}_P{task_part}_R{repetition}
```

Example: `671_T1_P1_R1` = participant 671, timepoint T1, **Task Part 1**, repetition 1.

Segmentation workbook sheet (equivalent):

```
{participant} - T{timepoint}P{task_part}R{repetition}
```

---

## Task Part 1 (`P1`) — critical definition

| Term | Meaning |
|---|---|
| **`P1` in session key** | **Task Part 1** — the first (and only) analyzed task part in V1 |
| **Scope of P1** | Full Gaga movement battery: **exercise_id 1–17** (canonical `ex01`–`ex17`) per session |
| **Not P1** | Any label using P1–P5 to mean individual exercises within Group4 — **removed from project vocabulary** |

V1 analyzes **Task Part 1 only** (`mode.task_part: P1`). Other task parts may exist in raw files but are out of scope.

---

## Timepoints and repetitions

| Token | Role in jcvPCA |
|---|---|
| **T1** | Reference timepoint (always side A) |
| **T2, T3** | Longitudinal comparison timepoints (side B) |
| **R1, R2** | Within-timepoint repetitions (two takes of the same session content) |

**Longitudinal (primary):** pooled `T1(R1+R2)` vs `T2(R1+R2)` and vs `T3(R1+R2)` — descriptive headline effect.

**Observed NV (Layer 1):** `T{k} R1` vs `T{k} R2` (single-rep, never pooled) at **T1, T2, and T3**, stratified by exercise `ex09`–`ex13` (Step 8h). Matched exceed-floor compares **single-rep** longitudinal `(T1_R1 vs T2/T3_R1)` against single-rep **T1** NV `(T1_R1 vs T1_R2)` on the same T1 basis. **v6:** the exceed decision is signed tier **S2** (magnitude exceed + reference-direction stability), not abs ratio alone — see `CLAIMS.md`.

**Protocol-openness read (descriptive):** compare per-exercise NV (e.g. `ex13` vs `ex09` between-rep variability). Allowed: “consistent with a more open curvilinear brief.” Forbidden: improvisation skill, learning, or treatment claims.

**Same-movement / estimand lock (v6):** per-exercise NV strengthens a claim **only** via per-exercise matched longitudinal on that same exercise (`long_ex_k / nv_ex_k`). ex11_13 aggregate, LOO, and `ex13/ex09` openness are **diagnostics / protocol-texture only** — they do **not** confirm the pooled `ex09_13` A2 estimand (different movement → different estimand).

---

## Exercises

- **Authoritative ID:** `exercise_id` column in `{pid}_ex_segmentatios_frames.xlsx` (1-indexed, 1–17 in current data).
- **Canonical label:** `ex{exercise_id:02d}` (e.g. exercise_id 9 → `ex09`).
- **Movement groups** (display / combined windows only): Group1–Group6 per `configs/exercise_map.yaml`.

---

## Primary analysis window (v4 lock)

| Field | Value |
|---|---|
| Selection name | `{pid}_ex09_13_contiguous` |
| exercise_ids | [9, 10, 11, 12, 13] |
| combine_exercises | true (concatenated in frame order per session) |
| Group | Group4 — “Curvilinear exploration” |
| Repetition mode (primary) | **pooled** |
| Participants | 671, 252, 651, 790 (each run separately) |

This is the **protocol-complete Group4 block** for the committee case study. Alternate exercise spans from early exploration are **not** part of v4.

---

## Group4 internal structure (Step 8h NV stratification)

Within Group4 (`ex09`–`ex13`), the protocol nests two analytical layers:

| Exercises | Movement logic (analytical label) | Primary use |
|---|---|---|
| ex09, ex10 | Entry / initial curvilinear exploration | Longitudinal primary (`ex09_13`); **Step 8h NV singles at T1/T2/T3** |
| **ex11, ex12, ex13** | Progressive linked curvilinear sequence | **Step 8h Layer 1:** matched R1↔R2 singles (all timepoints) + **ex11_13 aggregate** |

The **ex11_13 aggregate** (`T{k}_R1: ex11+ex12+ex13` vs `T{k}_R2: …`, per-exercise centered before concatenation) is a **planned NV validation unit**, not a post hoc subgroup and **not** a replacement for the longitudinal `ex09_13` primary window.

**Step 8h deliverables (v6):** `link_exercise_nv.csv`, `link_exercise_longitudinal.csv`, `NV_PROFILE.csv`, `EXERCISE_PROTOCOL_OPENNESS.md` — **link-level ranges/ranks only; no cross-link mean \|Δ\|**. (Deprecates `exercise_level_nv.csv` cross-link means; `ex13/ex09` reported as participant-level **range of per-link ratios**, not a cross-link mean.)

---

## Robustness / sensitivity (not alternate windows)

Robustness of the primary `ex09_13` pooled result is tested in **Step 4b** as one merged analysis — **not** alternate exercise windows.

| Axis | Perturbation | Question |
|---|---|---|
| **PC-count (`k`)** | Fixed T1 pooled A; `k` grid [4…10] | Does the story depend on exactly `m`? |
| **Repetition design** | pooled vs **single** `T1 R1` vs `T2/T3 R1` | Does effect depend on one take? (also supplies matched ratio numerator/denominator) |
| **Repetition diagnostics** | pooled vs **R2**; longitudinal **R1 vs R2** top-5; **p50/p60 band** overlaps (pooled vs R1/R2) | Is take instability symmetric? Dominant-mode vs full-subspace? (interpretation only) |
| **QC / link set** | exclude `include_with_caution` links only | Survives dropping borderline QC links? |
| **Functional PC band** | `p_functional_50` / `p_functional_60` from T1 EVR | Does dominant vs secondary decomposition change the story? |

Outputs: `robustness.csv`, `functional_pc_bands.csv`, **top-k overlap** (k=5), **functional-chain consistency** — heuristic **robustness label** only (stable / partial / unstable), not p-values.

### Functional vs secondary PCs (labeling)

| Band | Rule |
|---|---|
| **Dominant reference** | PCs 1…`p_functional_50` (T1 cumulative EVR ≥ 50%) |
| **Broad core (sensitivity)** | PCs 1…`p_functional_60` (T1 cumulative EVR ≥ 60%) |
| **Secondary** | PCs after `p_functional_50` through `selected_m` (80% EVR) |
| **Combined (headline)** | All PCs in `link_level_results.csv` |

`selected_m` (80% EVR) remains the computation; `p_functional_*` are reporting labels in `functional_pc_bands.csv`. Per-run `functional_space_results.csv` still uses config `sensitivity_p=2` for UI/avatar compatibility.

**Removed from Step 4b (v5):** EVR threshold sweep (subsumed by k-grid), naive basis-similarity cosine, bootstrap CIs.

See `MASTER_EXECUTION_PLAN.md` Step 4b.

---

## What the design cannot separate

- **Instruction effect vs lasting learning** at T2/T3 (no passive retention-only condition).
- **Drug effect vs practice effect** while labels are blinded — report timepoint differences descriptively only.

---

## Participants

671, 252, 651, 790 — four independent case studies. Results may be shown side-by-side for illustration; **no pooled cohort inference**.
