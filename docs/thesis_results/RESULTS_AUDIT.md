# Results audit — thesis lock

**Audit date:** 2026-09-13  
**Method:** Read-only. Numbers below are taken from CSVs/JSON, not from secondary rollups unless the rollup is a documented projection of those CSVs.

**Authoritative tree:** `results_committee_case/marker_gap_policy_ex09_13/`  
**Rejected as number source:** `results_committee_case/METRICS_DIGEST.md` (stale); `results_committee_case/step04_primary_runs/` (pre-marker-gap, 2026-07-14); `results_exploration_671_252/` (superseded windows).

Production hash in every marker-gap `reproducibility_manifest.json`: **`728c871edf0423aa6ea526651023253c38ea118f`**. Science hash: **`5f58540b49016b41`**. Variance threshold: **0.80**. Window: **`ex09_13_contiguous`**. Validate: **true**. Datetime: **2026-07-19T21:04–21:05**.

---

## B. Which version is final? (including the METRICS_DIGEST contradiction)

### What exists

| Tree | When | Marker-gap | Role |
|---|---|---|---|
| `results_committee_case/step04_primary_runs/` | 2026-07-14 | **OFF** | Pre-policy baseline |
| `results_committee_case/step08_nv_and_stability/` (repo root, not under marker_gap) | with pre-policy Step 4 | OFF | Pre-policy NV |
| `marker_gap_policy_ex09_13/step04` + `step08` + `step05–09` + `tables_to_show/` | **2026-07-19T21:04** | **ON** | **Thesis lock** |
| Commit `1101c4d` (2026-09-13) | n/a | n/a | Stored the lock tree on GitHub; **did not re-run** |

### The contradiction — still present in the digest, resolved in the files

`METRICS_DIGEST.md` header (line 9):

> Last updated: 2026-07-19 (marker-gap policy wired; **Step 4 primary runs pending rerun**)

The same file’s status table then marks Step 4 **Done** and points at `step04_primary_runs/PRIMARY_RUN_INDEX.md` — the **pre-policy** folder. Its “Run parameters” table still says 671=18, 252=22, 651=18, 790=22 links as if nothing was dropped.

**That is not true of the 21:04 rerun.** Same calendar day, later that evening, `marker_gap_policy_ex09_13/tables_to_show/01_primary_run_index.md` was generated (`2026-07-19T21:05:10`, git `728c871`) with the policy ON. `DIFF_vs_pre_policy.md` records the deltas.

**Lock rule:** ignore `METRICS_DIGEST.md` for any number that will appear in the thesis. Use `marker_gap_policy_ex09_13/tables_to_show/09_headline_a2_summary.csv` and `step08_nv_and_stability/NV_PROFILE.csv`.

A second, smaller contradiction inside the lock tree is **already documented and resolved**:

- `DIFF_vs_pre_policy.md` §3 lists 671 T1→T2 new S2/S3 as **8/0**.
- `09_headline_a2_summary.csv` and live `NV_PROFILE.csv` have **S2=4, S3=4** (A2=8).

Cause: `tables_to_show/README.md` — an early snapshot of table 05 was taken before Step 5 wrote `step5_organization`, so every row looked like S3=0. **Authoritative: S3=4 on 671 T2.** Do not quote DIFF §3 S3 column.

### Pooled vs single

| Layer | Footing | Thesis use |
|---|---|---|
| Step 4 pooled | T1(R1+R2) vs T2/T3(R1+R2), T1 PCA | Descriptive headline (A1, heatmaps, avatars) |
| Step 8 A2 | `T1_R1 vs T{k}_R1` / `T1_R1 vs T1_R2`, signed S2 | **Only** “exceeds observed repetition variability” statement |
| Step 5 `exceeds_nv` | pooled mean-\|Δ\| over single-rep floor | **Not** A2. Used only as S3 organization gate (footing mismatch; see CLAIMS.md) |

`09_pooled_vs_single_headline.csv`: 790 T1→T2 has **12 sign-flips** between pooled and single (20 links). Never divide pooled Δ by the single-rep NV floor.

### Signed vs absolute NV

v6 lock: A2 = **S2**, not `matched_abs_ratio > 1`. Absolute ratio remains in `NV_PROFILE.csv` as a secondary column. Several 790 T2 A2 links pass S2 with ratios 1.06–1.32; that is magnitude-near-floor, not a strong exceed.

### Is a re-run required?

**No** for draft numbers. The lock tree is complete (Steps 4–9) and internally consistent. A re-run would only re-prove bit identity of code now committed in `1101c4d` against artifacts produced from a dirty `728c871` tree. Optional, not blocking (`OPEN_ITEMS_BEFORE_WRITING.md`).

What **is** missing and stays missing: Step 10 `FINDINGS_SUMMARY.csv`, `COMMITTEE_BRIEF.md`, signed `SUPERVISOR_NV_DECISION.md`. Those are packaging, not new science.

---

## 1. Sample

All four IDs have **Task Part 1 only**, T1/T2/T3 × R1/R2 (6 Motive sessions each) under `data/raw_skeleton/{pid}/`. Segmentation workbooks exist for all four.

| PID | Skeleton setup | Manifest links | Usable A2 links T2 / T3 | Timepoints usable |
|---|---|---:|---|---|
| 671 | A (14-core + trunk → 18) | 18 | 18 / 17 | T1, T2, T3. T3 marker-prefix; `Ab_to_Chest` missing in T3 B |
| 252 | B (16-core + trunk → 22) | 22 | 20 / 20 | All six sessions |
| 651 | A, **template change T1→T2** | 18 | 10 / 10 | All six; trunk/pelvis columns missing on T2/T3 B; ChestTop gaps on T1_R2 |
| 790 | B | 22 | 20 / 18 | All six; RHLE ~99% gapped on T1_R2; RIPS on T3 |

**Comparisons that can actually be run:** for each PID, T1→T2, T1→T3, and T1 R1↔R2 NV. Cross-participant pooling is forbidden by design and by non-identical link inventories (Setup A vs B; 651 missing trunk).

No MRI / fNIRS / questionnaires in this lock.

---

## 2. T1→T2 (A2 numbers from `NV_PROFILE.csv`)

### 671 — only fully gated cell

- Links in A2 universe: **18**. selected_m pooled **9**, single **8**.
- Tiers: S0=7, S1=3, S2-only=4, **S3=4**, A2=8.
- Coverage: adequate, `coverage_rel=0.8056`. `rep_pass=True`. qc_drop **stable**. k-grid min k=4–7 = **0.6**.
- Leading signed Δ: `LFArm_to_LHand +0.074` (S3), `LUArm_to_LFArm −0.0615` (S2; NV≈0 → ratio 256, treat as unstable floor), left-leg chain S3.
- Dominant pooled |Δ| regions: left_leg, left_arm, right_leg.
- Step 5: 6 organization / 11 within_variability / 1 mixed (pooled footing).
- Entropy 0.91→0.92 (no global broadening).
- **Limits:** LUArm S2 should not be sold as a huge effect; the NV denominator is ~2e-4.

### 252

- A2 universe **20** (left-leg dropped for NV matching). m=10.
- A2=**3**, S3=0. S1=9 (magnitude without direction-stable sign).
- Coverage adequate 0.811 but `rep_pass=False`, k-grid min **0.0**.
- A2 links: `LFArm_to_LHand −0.0292` (ratio 1.70); `RFArm_to_RHand +0.0077` (**ratio 1.01**); `Chest_to_LShoulder −0.0029` (ratio 2.08).
- **Limits:** three A2 links, one of them is a rounding-level exceed. Do not describe 252 T2 as a clear longitudinal reorganization.

### 651

- A2 universe **10**. m=6. Eight links gone (ChestTop + missing B pelvis/trunk).
- A2=**4**, S3=0 (pre-policy A2=8 and S3=5 — **policy changed the story**).
- Coverage adequate 0.837; `rep_pass=False`; k-grid min 0.4.
- A2: `LFArm_to_LHand +0.0625`, `RShoulder_to_RUArm −0.0361`, `LUArm_to_LFArm +0.0355`, `RThigh_to_RShin −0.0199`.
- **Limits:** no trunk remaining. Cannot test a Gaga “center→periphery” reading on this person.

### 790

- A2 universe **20**. Right distal arm dropped (RHLE 99.4%).
- A2=**7**, S3=0. Coverage adequate 0.867; k-grid min **0.2**.
- Several A2 ratios: 1.32, **1.08**, **1.06**, 1.24, 1.57, 1.31, and one huge ratio on `LFArm_to_LHand` because NV≈0.
- **Limits:** A2=7 overstates how far the person moved past repetition. Quote the ratios, not only the count.

---

## 3. T1→T3

### 671

- A2 universe **17** (`Ab_to_Chest` shared-feature miss). A2=**9**, S3=0.
- Coverage **limited 0.697**. `rep_pass=False`. k-grid min 0.4. Functional chain **not** retained.
- Leading: `RFArm_to_RHand −0.0742`, `LFArm_to_LHand +0.0722` (same left-hand sign as T2).
- **Pooled vs A2 mismatch:** pooled T3 drops `671_to_LThigh` and `LThigh_to_LShin` (T3_R2 99% `LThighFront` gaps). **A2 keeps them** because A2 uses T3_R1. Thesis text must say this explicitly if those links are named for T3.
- Persistence: 6 of the T2 A2 links persist with the same sign (see master table). `LUArm_to_LFArm` is T2-only (sign flip / transient).

### 252

- A2=**12** / 20. Coverage **limited 0.6005** (worst). All 12 A2 are coverage-blocked for S3 (`13_coverage_gate_vs_a2.csv`: `n_s2_blocked_by_coverage=12`).
- Persistence: **0** persistent A2; **2 sign-flips**.
- **Limits:** this is the cell most likely to be misread as “biggest effect.” Under CLAIMS.md it is the cell that most looks like *B poorly represented in T1’s subspace* — i.e. possibly a different strategy, not redistribution. Report A2 counts with the coverage number in the same sentence.

### 651

- A2=**2**. Coverage limited 0.706. No persistent A2. T2 A2 links are mostly `transient_T2`.

### 790

- A2=**3**. Coverage **adequate 0.887** (best T3). Persistent A2: only `LFArm_to_LHand`. Spine links dropped (RIPS).

---

## 4. Natural variability

**Definition (v6, CLAIMS.md + LIMITS.md):** Layer 1 observed same-condition repetition, **one pair of takes**: `T1_R1 vs T1_R2`. Signed per-link value = EVR-weighted signed sum across retained PCs. A2 = `|long_signed| > |nv_signed|` **and** sign(`long_signed`) = sign(`long_signed_rev`) using `T1_R2 vs T{k}_R1` as the reverse anchor.

- **Not** pooled NV. A pooled-rep floor is not constructible with 2 reps.
- **Not** a significance test. n=1 rep-pair, no margin.
- **Not** pure measurement noise — improvisation differs between takes.
- S0 = within floor; S1 = magnitude only; **S2 = A2**; S3 = S2 + coverage + Step 5 organization + Step 4b robustness.

S2 exists in **all eight** comparisons (48 A2-positive link-cells across 133 NV_PROFILE rows). That does **not** mean all eight comparisons are equally interpretable. S3 exists in **one** comparison (671 T2, 4 links).

`SUPERVISOR_NV_DECISION.md` is **unsigned**. Default wording until signed: “exceeds observed T1 R1–R2 variability (descriptive).”

---

## 5. Marker gaps — did they change the conclusions?

Yes. `14_policy_delta_summary.csv` / `DIFF_vs_pre_policy.md`:

| PID | T2 A2 old→new | T3 A2 old→new | What was dropped |
|---|---|---|---|
| 671 | 8→8 | 9→9 | T3_R2 left thigh (pooled only); `Ab_to_Chest` on T3 |
| 252 | **8→3** | 13→12 | Left-leg via LFAX on T1_R2 |
| 651 | **8→4** (S3 **5→0**) | **7→2** | ChestTop cluster + missing trunk on B |
| 790 | 5→7 | 5→3 | RHLE right arm; T3 RIPS spine |

**Central conclusions that survive policy:** 671 T2 remains the only S3 cell; 671 T3 A2 count unchanged; no cross-participant shared pattern; entropy still flat.

**Conclusions that do *not* survive:** 252 T2 as a broad A2 case; 651 S3; any trunk-inclusive story for 651.

Pre-policy A2 counts are **rejected**.

---

## 6. Robustness and coverage

Stable enough to discuss ranking (qc_drop overlap 1.0 and k-grid not collapsing): **671 T2** (and, more weakly, 651 T3 k-grid).

Partial / ranking-fragile: **252 T2** (k-grid min 0), **790 both** (k-grid min 0.2), **651 T2**.

Coverage-limited (interpret A2 as “reweighting inside T1 subspace” only with a warning, or not at all): **671 T3, 252 T3, 651 T3**. 252 T3 is the severe end (`coverage_rel=0.60`).

`rep_pass` is a **strict** AND across k-grid (k=4..10), qc_drop, and repetition_mode with threshold 0.6. It is True only for 671 T2. The name understates k-grid’s role (`tables_to_show/README.md`).

Step 7 entropy: all longitudinal changes are **≤0.02** on a 0–1 scale. There is **no evidence of global DoF unfreezing**. A4 (redistribution: some links ↑ some ↓) is allowed; “broader participation of the whole body” is not.

---

## Independent scientific reading (not just file summary)

1. **The data support individual, not shared, change.** Persistent same-sign A2 sets are 6 / 0 / 0 / 1 links. 252 even sign-flips on two A2 links. A group Gaga or psilocybin sentence is not hiding in the tables.
2. **Exceeding repetition variability is real but uneven.** S2 is not rare, but most S2 cells fail at least one of: coverage, k-grid, near-floor ratio, or QC stripping. The honest core is: *in this protocol window, one participant (671) has a T1→T2 pattern that clears the pre-registered interpretive stack; the other seven cells are descriptive.*
3. **A result that is under-claimed in the existing docs:** 671’s **persistence** of six left-hand/left-leg/pelvis links T2→T3, with `LFArm_to_LHand` also persistent in 790. That is still N-of-1 and not a group finding, but it is stronger than “A2 counts exist.”
4. **A result that is over-claimable if one only reads A2 counts:** 252 T3 (12 S2, coverage 0.60, zero persistence).
5. **Methodological risk to the Results chapter:** (a) mixing pooled headlines with single-rep A2 in one table without labels; (b) quoting METRICS_DIGEST; (c) treating Step 5 “organization” counts as A2; (d) LUArm/LFArm huge ratios driven by ~0 NV.
6. **Pipeline completeness vs scientific strength are different.** The code path from QC → rotvec → JcvPCA → signed NV is technically complete for these four people. The **inferential** stack for A3 is complete for one cell. That is enough for a methods + feasibility thesis. It is not enough for a findings paper.

---

## Short lock summary

- **Can we lock numbers now?** Yes — from `marker_gap_policy_ex09_13`, hash `728c871`.
- **Is another full batch required?** No.
- **Recommended central claim:** version 2 in `CENTRAL_CLAIM.md`.
- **First writing step:** copy Table 09 + 671 T2 S3 list + coverage row + exclusion list into the Results skeleton; write Methods from CLAIMS.md / LIMITS.md.
- **Still open:** supervisor NV wording, Step 10 narrative file, S3 footing (4 vs 7 on 671 T2), provenance smoke test.
