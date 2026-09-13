# Known confounds — baseline audit (Step 1)

Documented limitations that apply to **pre-trunk** `ex09_13` exploration and carry forward until Steps 2–4 resolve them.

---

## 1. Trunk links excluded from manifests

- Current selections use **group4_core** manifests: 671/651 = **14 links**, 252/790 = **16 links**.
- **Missing:** `Root→Ab`, `Ab→Chest` (and 252 extended spine chain segments).
- `Chest_to_Neck` is present but **`trunk_spine` region is empty** in region rollups.
- **Impact:** Cannot claim pelvis/abdomen/chest contribution redistribution until Step 3.

---

## 2. Participant 671 — T3 marker-set prefix

- T1/T2 sessions use marker prefix `671:`; T3 uses `T3_671:` (or equivalent) per DataDescriptions / pipeline warnings.
- Cross-timepoint comparisons use **shared valid links**; comparability note appears in run summaries and manifests.
- **Impact:** T1–T3 for 671 should be interpreted with caution; PCA stability may flag T1–T3.

---

## 3. Skeleton topology — two marker setups

| Setup | Participants (expected) | Bones | Extra links vs 671-style |
|---|---|---:|---|
| **A (671-style)** | 671, 651 | 51 | — |
| **B (252-style)** | 252, 790 | 55 | `252_to_LThigh`, `252_to_RThigh` (participant-prefixed pelvis roots) |

- **Impact:** Cross-participant link comparison requires canonical mapping and comparability flags (Step 2). 252/790 hip-root links are **within-participant only**, not cohort-comparable to 671 pelvis attachment.

---

## 4. Feature representation

- Features = **parent→child relative rotation vectors** (`rx`, `ry`, `rz`), not ISB/Euler anatomical joint angles.
- **Impact:** Claim **contribution to shared variance structure**, not “flexion increased” or muscle use.

---

## 5. Natural variability floor (2 repetitions)

- NV = single **T1 R1 vs T2** comparison per participant; never pooled across reps.
- Bootstrap (exploration): **0** links with 95% CI excluding zero on `ex09_13` pooled for 671 and 252.
- **Impact:** “Exceeds NV” is **descriptive ratio > 1**, not significance. Step 8 tiered NV still required.

---

## 6. Improvisational movement

- Gaga Task Part 1 exercises are **not repeated identically** across R1/R2 or timepoints.
- High within-condition variability inflates NV floor and weakens single-point NV interpretation.

---

## 7. Segmentation sheet naming (651, 790)

- Workbooks use sheet names `651- T1P1R1` / `790- T1P1R1` (hyphen spacing differs from `671 - T1P1R1`).
- Parser may accept via tolerant regex; **verify** during Step 2 inventory that all 24 sheets parse to valid session keys.

---

## 8. Avatar / communication layer mismatch (not in this snapshot)

- `avater_671_252/` tables were built from **`ex10_15_contiguous`**, not `ex09_13`.
- **Impact:** Do not use current avatar heatmaps as Step 1 baseline; regenerate in Step 10.

---

## 9. Out of scope for v4 baseline

- Old exploration **winner windows** (e.g. single-exercise spans) — not copied or cited here.
- BVH/Euler feature stream — not evaluated in this snapshot.
- Population/cohort statistics across the four participants.
