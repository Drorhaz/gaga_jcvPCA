# Baseline summary — Step 1 (protocol window lock)

**Snapshot date:** 2026-07-14  
**Primary window (v4):** `ex09_13_contiguous` pooled — exercise_ids [9, 10, 11, 12, 13]  
**Snapshot scope:** Pre-trunk, pre–651/790 committee runs. Exploration artifacts only for 671 and 252.

---

## What is frozen in this folder

| Participant | Source run | Links | selected_m | Location |
|---|---|---:|---:|---|
| 671 | `671_ex09_13_contiguous_pooled` (2026-07-07) | 14 | 8 | `671/ex09_13_contiguous_pooled/` |
| 252 | `252_ex09_13_contiguous_pooled` (2026-07-07) | 16 | 10 | `252/ex09_13_contiguous_pooled/` |

Each folder contains: `link_level_results.csv`, `region_level_results.csv`, `functional_space_results.csv`, `null_space_results.csv`, `natural_variability_results.csv`, `validation_results.csv`, `selected_m_by_comparison.csv`, `run_summary.md`, `reproducibility_manifest.json`, `analysis_selection.yaml`, `config_snapshot.yaml`, `jcvpca_results.csv`, `validation_summary.md`, `selection_source.yaml`.

**Parameters (exploration):** `variance_threshold=0.80`, filter 10 Hz order 4, pooled longitudinal (`T1(R1+R2)` vs `T2/T3(R1+R2)`), NV = `T1 R1` vs `T1 R2` only.

---

## Exploration signal summary (`ex09_13` pooled, pre-trunk)

From `results_exploration_671_252/summaries/ranking.csv`:

| Participant | Links > NV (T1–T2 + T1–T3) | Mean effect ratio | T2/T3 sign consistent | Bootstrap-supported links |
|---|---:|---:|---|---:|
| 671 | 12 | 1.03 | Yes | 0 |
| 252 | 20 | 1.36 | Yes | 0 |

**671 notable links (validation_summary, descriptive ratio > 1):** e.g. `LFArm_to_LHand`, `LShin_to_LFoot`, `RUArm_to_RFArm` at T1–T2; similar pattern at T1–T3 with `RFArm_to_RHand` prominent.

**252:** broader NV exceedance across limbs and hips at T1–T3 (e.g. `LUArm_to_LFArm`, `LThigh_to_LShin`, `252_to_RThigh`).

**Regions represented:** `head_neck`, `left_arm`, `right_arm`, `left_leg`, `right_leg` only — **`trunk_spine` absent** (no pelvis/abdomen trunk links in manifest).

---

## What we can conclude from pre-trunk exploration

For participants **671** and **252**, the protocol-complete Group4 window (`ex09`–`ex13`, pooled) produces complete jcvPCA runs with longitudinal T1–T2 and T1–T3 comparisons plus T1 R1–R2 NV baselines. Descriptive link-level contribution changes are present; several links show longitudinal |ΔJcvPCA| above the observed R1–R2 floor (ratio > 1) in both participants, with **consistent direction across T2 and T3** in the exploration ranking. The pipeline, segmentation slicing, and validation layer execute without link exclusion on this window. This supports **ex09_13_contiguous pooled** as the locked primary window for the committee case study, pending trunk extension and 651/790 onboarding.

---

## What we cannot yet conclude

These exploration runs use **limb-focused manifests without trunk intermediaries** (`Root→Ab`, `Ab→Chest`), so center→periphery claims involving trunk are not supported. **651 and 790** have no `ex09_13` runs and incomplete rotvec matrices (1/6 sessions converted). NV evidence is a **single R1–R2 point** per link — bootstrap supported **zero** links. Features are **relative link rotvecs**, not anatomical joint angles. All inference remains **within-participant, descriptive, N-of-1**; no population or causal claims. **671 T3** carries a marker-set prefix confound. Committee-authoritative results require **Steps 2–4** (link map, trunk-inclusive QC, fresh runs on all four participants).

---

## Next step (per MASTER_EXECUTION_PLAN v4)

**Step 2** — canonical skeleton baselines and link mapping, then **Step 3** trunk + convert 651/790 before **Step 4** primary runs.
