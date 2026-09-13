# Metrics digest — committee case study (living)

**Purpose:** Single human-readable rollup of meaningful metrics and conclusions discovered during execution. Updated as each step completes.

**Not a substitute for:** per-step CSVs, `FINDINGS_SUMMARY.csv` (Step 10), or framework docs (`CLAIMS.md`, `EXPERIMENTAL_DESIGN.md`, `ROBUSTNESS_FRAMEWORK.md`).

**Maintenance:** after each step, follow **Post-step → `METRICS_DIGEST.md`** in `docs/MASTER_EXECUTION_PLAN.md` — review code + chat deltas, offer append block, update log on confirmation.

**Last updated:** 2026-07-19 (marker-gap policy wired; Step 4 primary runs pending rerun)

---

## Status dashboard

| Step | Topic | Status | Primary source |
|---|---|---|---|
| 0 | Claims / design / limits | Locked | `step00_claim_framework/` |
| 1 | Baseline audit (pre-trunk) | Done (snapshot) | `step01_baseline_audit/BASELINE_SUMMARY.md` |
| 2 | Link mapping / comparability | Done | `step02_link_mapping/` |
| 3 | Trunk extension + QC | Done | `step03_trunk_extension/` |
| 4 | Primary pooled runs (4 participants) | Done | `step04_primary_runs/PRIMARY_RUN_INDEX.md` |
| 4b | Robustness + functional PC bands | Done | `step04_primary_runs/robustness.csv`, `functional_pc_bands.csv` |
| 5 | ROM/RMS amplitude vs organization | Done | `step05_amplitude_vs_organization/` |
| 6 | Underused-at-T1 links | Done | `step06_underused_at_t1/` |
| 7 | Contribution distribution | Done | `step07_contribution_distribution/` |
| 8 / 8h | Observed NV + per-exercise T1/T2/T3 (abs) | Done | `step08_nv_and_stability/` |
| 8v6 | Signed NV profile (S0–S3 tiers) | Done (provisional Phase-0) | `step08_nv_and_stability/NV_PROFILE.csv` |
| 9 | T2 vs T3 persistence | Done | `step09_persistence_t2_t3/` |
| 10 | `FINDINGS_SUMMARY.csv` + interpretation | Pending | — |

---

## Run parameters (committee primary)

| Field | Value |
|---|---|
| Window | `ex09_13_contiguous` (ex09–ex13, pooled) |
| Longitudinal | `T1(R1+R2)` vs `T2/T3(R1+R2)` |
| PCA | T1 reference, `variance_threshold=0.80` |
| Participants | 671 (18 links), 252 (22), 651 (18), 790 (22) |

---

## Step 0 — Claim framework (locked)

**Source:** `step00_claim_framework/CLAIMS.md`, `EXPERIMENTAL_DESIGN.md`, `LIMITS.md`

### Primary analysis lock

| Field | Value |
|---|---|
| Window | `ex09_13_contiguous` — ex09–ex13, **pooled** R1+R2 |
| Participants | 671, 252, 651, 790 (four separate N-of-1 cases) |
| Reference | T1 always side A |
| Features | Relative link rotvecs (not anatomical joint angles) |
| NV floor (authoritative) | Matched single-rep ratio — Step 8 (not pooled NV) |

### Allowed claims → evidence map

| ID | Claim (short) | Minimum evidence step |
|---|---|---|
| **A1** | Link/region contribution changed T1→T2/T3 | Step 4 |
| **A2** | Change exceeds observed T1 R1↔R2 variability | Step 8 matched ratio |
| **A3** | Consistent with broader underused-link participation | A2 + coverage + Step 5 + Step 4b + supervisor |
| **A4** | Contribution redistribution (↑ and ↓ links) | Step 4 + Step 7 |

### Claim tiers

| Tier | Use in committee |
|---|---|
| **A (descriptive)** | Metric values, ratios — always allowed when computed |
| **Interpretive** | “Consistent with hypothesis” — gated; needs evidence stack below |

### Evidence stack (read order)

1. Coverage gate (Step 8)  
2. Layer 1 observed NV — single-rep takes only  
3. Layer 2 subsample stability — optional, **never** feeds floor  
4. Robustness label (Step 4b)

### Forbidden (summary)

Causality, population inference, significance language, dormant-motor claims, timing/segmentation claims, anatomical angle claims.

### Supervisor status

| Item | Status |
|---|---|
| Claim scope accepted | **Pending** |
| NV wording (`SUPERVISOR_NV_DECISION.md`) | **Pending** (after Step 8) |

### Conclusion

Step 0 fixes vocabulary and gates — metrics in this digest map to **A1–A4** and tier rules for later presentation curation (Step 10).

---

## Step 1 — Baseline audit (pre-trunk exploration snapshot)

**Source:** `step01_baseline_audit/BASELINE_SUMMARY.md`, `PARTICIPANT_READINESS.md`, `KNOWN_CONFOUNDS.md`  
**Scope:** Historical snapshot before Steps 2–4; 671/252 only had committee-grade exploration runs.

### Readiness at audit date (2026-07-14)

| ID | Matrices | Topology | `ex09_13` exploration run | Blocker before Step 4 |
|---|---|---|---|---|
| 671 | 6/6 | Setup A | **Yes** | Trunk + committee rerun |
| 252 | 6/6 | Setup B | **Yes** | Trunk + committee rerun |
| 651 | **1/6** | Setup A | No | Convert 5 sessions + map |
| 790 | **1/6** | Setup B | No | Convert 5 sessions + map |

### Pre-trunk exploration signal (671, 252 only)

| Participant | Links | selected_m | Links > NV (T1–T2 + T1–T3) | Mean effect ratio | T2/T3 sign consistent |
|---|---:|---:|---:|---:|---|
| 671 | 14 | 8 | 12 | 1.03 | Yes |
| 252 | 16 | 10 | 20 | 1.36 | Yes |

**Pre-trunk limitation:** no `trunk_spine` region — limb-focused manifests only. Bootstrap-supported links: **0** (exploration-era).

### Pre-trunk → Step 4 delta (link inventory)

| Participant | Step 1 links | Step 4 links | Δ | Notes |
|---|---:|---:|---:|---|
| 671 | 14 | 18 | +4 | Trunk added |
| 252 | 16 | 22 | +6 | Trunk + extended spine |
| 651 | — | 18 | — | Onboarded in Step 3–4 |
| 790 | — | 22 | — | Onboarded in Step 3–4 |

### Conclusion

Step 1 locked **`ex09_13_contiguous` pooled** as the primary window and documented confounds. Exploration on 671/252 showed descriptive NV exceedance; **authoritative committee numbers are Step 4+** (trunk-inclusive, all four participants).

---

## Step 3b — Marker-gap session exclusions (wired 2026-07-19)

**Source:** `step03_trunk_extension/marker_gap_link_removals_ex09_13.csv`, `QC_POLICY.md`, `docs/MARKER_GAP_REMOVAL_WIRING.md`  
**Config:** `analysis.apply_marker_gap_removals: true` in `configs/analysis_defaults.yaml`

### Policy (session-scoped, not global)

Drop link from a comparison when that comparison uses a session/rep where supporting markers had **≥10%** of ex09–13 in large gaps (>0.5 s), or **≥2** markers **≥5%**. Pooled sides: any flagged rep on that side triggers drop.

### Removal inventory (`remove_from_comparison` tier)

| Participant | Session | Links affected (count) | Driver |
|---|---|---:|---|
| 252 | T1_R2 | 2 | `252:LFAX` 13% gaps → left knee/ankle |
| 651 | T1_R2 | 5 | `651:ChestTop` 20% → trunk/upper cluster |
| 651 | T3_R2 | 2 | `651_T3:WaistLBack` 14% → left hip |
| 671 | T3_R2 | 2 | `T3_671:LThighFront` 99% → left leg |
| 790 | T1_R2 | 2 | `790:RHLE` 99% → right elbow/hand |
| 790 | T3_R1 | 2 | `790:RIPS` 19% → spine |
| 790 | T3_R2 | 2 | `790:RIPS`/`790:LIPS` 58%/48% → spine |

**17 remove rows** (+ 16 watch-only at 5–10%). Recorded per comparison in `run_summary.md` as **Excluded (marker-gap policy)**.

### Conclusion

Marker gaps are **transparency on optical tracking**, not rotvec QC. Wiring is live in `pipeline.run_analysis` and `observed_nv.py`. **Step 4 primary CSVs still reflect pre-wiring runs until `run_step04_primary.py` is re-executed.**

---

## Step 4 — Primary pooled runs (headline metrics)

**Source:** `step04_primary_runs/PRIMARY_RUN_INDEX.md`, per-participant `run_summary.md`, `selected_m_by_comparison.csv`, `region_level_results.csv`, `validation_results.csv`  
**Git hash (runs):** `728c871edf0423aa6ea526651023253c38ea118f` · **validate=true**

### Run inventory

| Participant | Links in manifest | T1→T2 m | T1→T3 m | NV m | Links analyzed (long.) |
|---|---:|---:|---:|---:|---|
| 671 | 18 | 9 | 9 | 8 | 18 / **17** (T3: 1 excluded) |
| 252 | 22 | 10 | 10 | 10 | 22 / 22 |
| 651 | 18 | 6 | 6 | 6 | **14** / 14 (4 trunk links missing on T2/T3) |
| 790 | 22 | 9 | 9 | 8 | 22 / 22 |

### Largest \|ΔJcvPCA\| (pooled headline — mean across PCs)

| Participant | T1→T2 top links | T1→T3 top links |
|---|---|---|
| **252** | RThigh_to_RShin (0.217), RShoulder_to_RUArm (0.176), LUArm_to_LFArm (0.163) | **RUArm_to_RFArm (0.350)**, LUArm_to_LFArm (0.306), RShoulder_to_RUArm (0.215) |
| **671** | LFArm_to_LHand (0.222), LUArm_to_LFArm (0.166), RFArm_to_RHand (0.149) | RFArm_to_RHand (0.222), LFArm_to_LHand (0.221), LThigh_to_LShin (0.150) |
| **651** | LFArm_to_LHand (0.256), RUArm_to_RFArm (0.208), LUArm_to_LFArm (0.178) | RUArm_to_RFArm (0.311), LUArm_to_LFArm (0.306), RFArm_to_RHand (0.168) |
| **790** | LShoulder_to_LUArm (0.213), RFArm_to_RHand (0.164), LFArm_to_LHand (0.146) | LFArm_to_LHand (0.172), LUArm_to_LFArm (0.138), RUArm_to_RFArm (0.120) |

### Region rollup (mean JcvPCA_region across PCs)

| Participant | T1→T2 dominant regions | T1→T3 dominant regions |
|---|---|---|
| 671 | left_arm, right_arm | left_arm, head_neck |
| 252 | right_arm, left_leg | **right_leg**, left_arm |
| 651 | left_leg, left_arm (small \|Δ\|) | **right_arm**, right_leg |
| 790 | left_leg, trunk_spine | right_arm, right_leg, trunk_spine |

**Note:** region \|Δ\| magnitudes are modest; **link-level** tables drive headline claims (A1).

### NV exceed counts (pooled T1 R1↔R2 floor — descriptive until Step 8)

| Participant | T1→T2 exceed | T1→T3 exceed | Links evaluated |
|---|---:|---:|---:|
| 252 | 6 | **19** | 22 |
| 790 | 15 | 4 | 22 |
| 651 | 13 | 11 | 14 |
| 671 | 7 | 8 | 18 / 17 |

### Conclusion

- All **four participants** complete trunk-inclusive Step 4 pooled runs — committee-primary descriptive headline is locked.
- **252 T3** shows largest effect magnitudes and broadest NV exceedance (19 links) under current (pooled) floor.
- **651/671** shared-link restrictions reduce evaluated links on some comparisons — not pipeline failure.
- **Presentation candidates (Tier A headline):** link-level \|ΔJcvPCA\|, top-5 rankings (§5 below), NV exceed counts — **re-validate with Step 8 matched ratio** before interpretive tier.

---

## 1. Robustness labels (Step 4b)

Heuristic gate on k-grid median, pooled↔R1 overlap (all PCs), QC-drop. **Not p-values.**

| Participant | T1→T2 | T1→T3 | Notes |
|---|---|---|---|
| 671 | **stable** | **stable** | k-grid + QC pass; rep-mode borderline (0.6) |
| 252 | **partial** | **partial** | rep-mode fails at 0.4 (all PCs); k-grid + QC pass |
| 651 | **stable** | **stable** | strongest rep stability |
| 790 | **stable** | **partial** | T3: rep-mode 0.4 **and** k-grid median 0.4 |

**Source:** `step04_primary_runs/robustness.csv` (qc_drop row)

### Conclusion

- **3/4 participants stable** on at least one comparison; **252 partial on both**; **790 partial on T3**.
- `partial` does **not** block Tier A descriptive claims; it gates **interpretive** “consistent with hypothesis” language (see `CLAIMS.md` A3).

---

## 1b. k-grid, QC-drop, functional chain (Step 4b)

### k-grid median top-5 overlap (k ∈ [4…10])

| Participant | T1→T2 | T1→T3 |
|---|---:|---:|
| 671 | 0.6 | 0.8 |
| 252 | 0.6 | 0.6 |
| 651 | 0.6 | 0.8 |
| 790 | 0.8 | **0.4** |

### QC-drop overlap (drop `include_with_caution` links)

| Participant | T1→T2 | T1→T3 | Caution links dropped |
|---|---:|---:|---|
| 671 | 1.0 | 1.0 | 1 |
| 252 | 1.0 | 1.0 | 0 |
| 651 | 1.0 | 1.0 | 4 |
| 790 | 1.0 | 1.0 | 0 |

### `functional_chain_retained` (repetition_mode rows)

| Participant | T1→T2 | T1→T3 |
|---|---|---|
| 671 | not | not |
| 252 | **retained** | **retained** |
| 651 | retained | retained |
| 790 | retained | retained |

**Source:** `robustness.csv`

### Conclusion

- **252 `partial` is rep-driven**, not k-sensitive or QC-sensitive (k-median 0.6, QC 1.0).
- **790 T3 `partial`** is **rep + k-grid** (k-median 0.4 at k=4–7) — deeper caution than 252.
- **671** functional chain **not retained** on rep overlap despite stable label — sign/chain heuristic fails on overlapping links even when top-5 overlap passes.

---

## 2. Repetition diagnostics (Step 4b)

Top-5 overlap under rep perturbation. Threshold heuristic: ≥ 0.60 = stable axis.

### All PCs (→ 80% EVR)

| Participant | T1→T2 pooled↔R1 | pooled↔R2 | R1↔R2 long. | T1→T3 pooled↔R1 | pooled↔R2 | R1↔R2 long. |
|---|---:|---:|---:|---:|---:|---:|
| 671 | 0.6 | 0.4 | 0.6 | 0.6 | 0.4 | 0.4 |
| 252 | **0.4** | 0.2 | 0.6 | **0.4** | 0.8 | **0.2** |
| 651 | 0.6 | 0.6 | 0.6 | 0.8 | 0.8 | 0.6 |
| 790 | 0.6 | 0.8 | 0.4 | **0.4** | 0.4 | **0.2** |

### Dominant PC bands — pooled↔R1 (pooled T1 EVR cutoffs)

| Participant | T1→T2 p50 | p60 | T1→T3 p50 | p60 |
|---|---:|---:|---:|---:|
| 671 | **0.8** | 0.6 | **0.8** | 0.4 |
| 252 | 0.6 | 0.6 | **1.0** | **0.8** |
| 651 | 0.6 | 0.4 | 0.6 | 0.8 |
| 790 | 0.4 | 0.4 | **0.4** | 0.4 |

**Source:** `robustness.csv` (`repetition_mode` rows)

### Conclusion

- **Dominant-mode read (p50) is more rep-stable than full 80%-EVR ranking** in most cases (6/8 comparisons ≥ 0.6 at p50 vs 4/8 at all PCs).
- **252 T3:** full 0.4 → p50 **1.0** → instability is **fringe top-5 / secondary PCs**, not a flipped dominant coordination pattern.
- **790 T3:** **0.4 at all bands** → rep sensitivity affects dominant structure too; stronger caution than 252.
- **252 T3** R1↔R2 longitudinal = **0.2** (takes disagree) but pooled↔R2 = **0.8** → asymmetry; **R1 is the outlier take** for headline ranking.

---

## 2b. Repetition diagnostics — pooled↔R2 PC bands

| Participant | T1→T2 p50 | p60 | T1→T3 p50 | p60 |
|---|---:|---:|---:|---:|
| 671 | 0.6 | 0.8 | 0.2 | 0.8 |
| 252 | 0.6 | 0.6 | **1.0** | 0.8 |
| 651 | **1.0** | 0.6 | 0.6 | 0.8 |
| 790 | 0.8 | 0.8 | 0.6 | 0.4 |

**Source:** `robustness.csv` (`pooled_vs_r2_overlap_p50`, `pooled_vs_r2_overlap_p60`)

### Conclusion

- **252 T3 pooled↔R2 p50 = 1.0** — dominant story aligns with R2; **R1-only** longitudinal drives the 0.4 full-subspace fail.
- **671 T3 pooled↔R2 p50 = 0.2** — R2 take diverges more than R1 on dominant band (asymmetric take instability).

---

## 3. Functional PC structure (Step 4b)

Per comparison: PCs to 50% / 60% T1 EVR; overlap of top-5 rankings (same pooled fit).

| Participant | p50 | p60 | selected_m | evr_pc1+pc2 | all↔p50 | all↔p60 |
|---|---:|---:|---:|---:|---:|---:|
| 671 T2 | 4 | 5 | 9 | 0.35 | 0.6 | 0.4 |
| 671 T3 | 3 | 5 | 9 | 0.35 | 0.4 | 0.6 |
| 252 T2 | 4 | 5 | 10 | 0.33 | 0.4 | 0.6 |
| 252 T3 | 4 | 5 | 10 | 0.33 | 0.6 | 0.4 |
| 651 T2 | 3 | 4 | 6 | 0.44 | 0.6 | 0.6 |
| 651 T3 | 3 | 4 | 6 | 0.44 | 0.4 | 0.4 |
| 790 T2 | 4 | 5 | 9 | 0.32 | 0.6 | 0.8 |
| 790 T3 | 4 | 5 | 9 | 0.32 | 0.6 | 0.8 |

**Source:** `functional_pc_bands.csv`

### Conclusion

- Dominant structure is **low-dimensional** (3–5 PCs for 50–60% EVR); headline uses 6–10 PCs.
- Unweighted mean across all retained PCs lets **secondary modes** compete for top-5 slots — explains rep-mode gap between all-PC and p50 overlaps.
- **p50 vs p60** agree moderately (0.6–0.8) — bands are consistent, not arbitrary.

---

## 4. Amplitude vs organization (Step 5)

Links exceeding observed NV (ratio > 1) classified by ROM flat band (0.7–1.3).

| Participant | Comparison | Exceed NV | Organization | Amplitude | Mixed |
|---|---|---:|---:|---:|---:|
| 252 | T1→T3 | **19** | **19** | 0 | 0 |
| 252 | T1→T2 | 6 | 6 | 0 | 0 |
| 790 | T1→T2 | 15 | 12 | 0 | 3 |
| 651 | T1→T2 | 13 | 10 | 1 | 2 |
| 651 | T1→T3 | 11 | 7 | 2 | 2 |
| 671 | T1→T3 | 8 | 6 | 2 | 0 |
| 671 | T1→T2 | 7 | 6 | 0 | 1 |
| 790 | T1→T3 | 4 | 4 | 0 | 0 |

**Source:** `step05_amplitude_vs_organization/classification_summary.md`

### Conclusion

- **252 T3:** all 19 NV-exceeding links = **organization** (flat ROM) → supports **redistribution** wording, not amplitude-driven change.
- **671 / 651 / 790 T3:** some amplitude/mixed labels → soften interpretive language where applicable.
- Step 5 uses pooled-run NV floor; **Step 8 matched single-rep ratio** will be authoritative for exceed gates.

---

## 5. Headline top-5 links (pooled, all PCs)

| Participant | Comparison | Top-5 links |
|---|---|---|
| 252 | T1→T3 | LUArm_to_LFArm, RThigh_to_RShin, LFArm_to_LHand, **252_to_RThigh**, RFArm_to_RHand |
| 252 | T1→T2 | RUArm_to_RFArm, **252_to_LThigh**, LUArm_to_LFArm, **252_to_RThigh**, RThigh_to_RShin |
| 790 | T1→T3 | RShoulder_to_RUArm, RUArm_to_RFArm, RFArm_to_RHand, RThigh_to_RShin, LUArm_to_LFArm |
| 790 | T1→T2 | LShoulder_to_LUArm, **790_to_LThigh**, LThigh_to_LShin, LFArm_to_LHand, RUArm_to_RFArm |
| 671 | T1→T3 | LUArm_to_LFArm, RUArm_to_RFArm, LFArm_to_LHand, LShoulder_to_LUArm, Neck_to_Head |
| 671 | T1→T2 | LFArm_to_LHand, LUArm_to_LFArm, RShoulder_to_RUArm, RUArm_to_RFArm, **671_to_LThigh** |
| 651 | T1→T3 | RUArm_to_RFArm, LUArm_to_LFArm, RFArm_to_RHand, RThigh_to_RShin, LThigh_to_LShin |
| 651 | T1→T2 | RUArm_to_RFArm, LUArm_to_LFArm, LFArm_to_LHand, RShoulder_to_RUArm, RFArm_to_RHand |

**Source:** `functional_pc_bands.csv` (`top5_all_pcs`)

### Conclusion

- **Pelvis roots** (`252/790/671_to_*Thigh`) appear in headline top-5 but are **rep-sensitive fringe** (small effects, compete for slots 3–5) — not spine-driven (`partial` is not from trunk/spine links; spine ranks mid-tier, never top-5).
- **252 T3 dominant band (p50)** emphasizes RUArm, RThigh, LThigh chain — arm/leg coordination, not pelvis-only story.

---

## 6. Infrastructure summary (Steps 2–3)

| Item | Value |
|---|---|
| Skeleton setup A (671, 651) | 51 bones, 2 trunk links (`*_to_Ab`, `Ab_to_Chest`) |
| Skeleton setup B (252, 790) | 55 bones, 5 trunk links (extended spine chain) |
| Trunk QC (T1 R1) | **PASS** all 4 participants — all trunk links `include` |
| QC caution links | 671: **1**, 651: **4**, 252/790: **0** |
| Link manifest sizes | 671/651: 18 links, 252/790: 22 links |
| Comparability | Setup B pelvis roots (`*_to_LThigh/RThigh`) = within-participant only |

**Source:** `step02_link_mapping/`, `step03_trunk_extension/TRUNK_QC.md`, `step03_trunk_extension/selections/`

### Conclusion

- Trunk-inclusive primary runs are **methodologically complete** for all four participants.
- Dropping caution links does **not** change top-5 (QC overlap 1.0 everywhere) — robustness is not QC-artifact driven.

---

## 7. Known confounds (carry-forward)

| Confound | Affected | Impact |
|---|---|---|
| 671 T3 marker prefix | 671 T3 | Cross-timepoint caution |
| Setup B pelvis roots (`*_to_LThigh`) | 252, 790 | Rep-sensitive fringe; not cohort-comparable to 671 |
| 651/671 missing trunk on some T2/T3 matrices | 651, 671 | Shared-link restriction (651: 14 links evaluated) |
| 2 reps × 5 exercises | All | NV = descriptive reference range, not significance |

**Source:** `step01_baseline_audit/KNOWN_CONFOUNDS.md`, Step 3 QC

---

## 8. Observed NV + coverage gate (Step 8h)

**Source:** `step08_nv_and_stability/` — `NV_EVIDENCE.csv`, `coverage.csv`, `nv_summary.csv`, `EXERCISE_PROTOCOL_OPENNESS.md`

**Script:** `scripts/observed_nv.py` · **Module:** `src/gaga_jcvpca/subspace_coverage.py`

### Matched single-rep exceed-floor (authoritative Tier A)

Ratio = `(T1_R1 vs T2/T3_R1 |Δ|) / (T1_R1 vs T1_R2 |Δ|)` on **single-rep** footing (`ex09_13` matched). Exceed = ratio > 1 (descriptive).

| Participant | T1→T2 exceed | T1→T3 exceed | Longitudinal coverage |
|---|---:|---:|---|
| 671 | **12/18** | **9/18** | T2 adequate (0.81); T3 **limited** (0.70) |
| 252 | **10/22** | **10/22** | T2 adequate (0.81); T3 **limited** (0.60) |
| 651 | **3/18** | **5/18** | T2 adequate (0.84); T3 **limited** (0.71) |
| 790 | **5/22** | **7/22** | T2 adequate (0.87); T3 **adequate** (0.89) |

**Links exceeding both T2 and T3:** 671 **6**, 252 **7**, 651 **2**, 790 **3**.

### vs Step 4 pooled NV floor (not authoritative)

Pooled denominator inflates exceed counts; matched single-rep is stricter.

| Participant | T1→T2 pooled >1 | T1→T2 matched >1 | T1→T3 pooled >1 | T1→T3 matched >1 |
|---|---:|---:|---:|---:|
| 671 | 7/18 | 12/18 | 8/17 | 9/18 |
| 252 | 6/22 | 10/22 | **19/22** | 10/22 |
| 651 | 13/14 | 3/18 | 11/14 | 5/18 |
| 790 | 15/22 | 5/22 | 4/22 | 7/22 |

**252 T3** is the clearest case: pooled floor says 19/22 exceed; matched single-rep says **10/22** — roughly half.

### Reference-subspace coverage (longitudinal pairs)

| Participant | T1 NV floor (R1↔R2) | T1→T2 | T1→T3 |
|---|---|---|---|
| 671 | adequate (0.90) | adequate (0.81) | **limited** (0.70) |
| 252 | adequate (0.93) | adequate (0.81) | **limited** (0.60) |
| 651 | adequate (0.94) | adequate (0.84) | **limited** (0.71) |
| 790 | adequate (0.86) | adequate (0.87) | adequate (0.89) |

**T3 limited coverage** (671, 252, 651): interpret link-level redistribution claims with caution for those pairs. **790 T3** retains adequate coverage despite Step 4b `partial` rep sensitivity.

**Severe single-exercise coverage (T3):** 671 ex11 R2→R1 (0.44), 790 ex11 R1→R2 (0.50) — exercise-local, not protocol-reference rows.

### Per-exercise protocol openness (descriptive)

**ex13 / ex09 mean |Δ| ratio** (R1↔R2 single segment):

| Participant | T1 | T2 | T3 |
|---|---:|---:|---:|
| 671 | 2.25 | 1.63 | 0.91 |
| 252 | 0.79 | 1.20 | 1.77 |
| 651 | 1.77 | 1.74 | **3.31** |
| 790 | 0.82 | 2.06 | 0.67 |

**T1 rank (most → least open):** 671 ex13-led; 252 ex09-led; 651 ex12-led; 790 ex09-led. **No cross-participant consensus** on which exercise is most variable.

**671 dominant-exercise flag:** ex13 drives largest per-link NV at T1 (15/18 links). **252/651/790:** ex09 or ex12, not ex13.

### Conclusion

1. **Matched single-rep floor is operational** — `NV_EVIDENCE.csv` is the authoritative exceed table for claim A2.
2. **671 and 252** show the broadest matched exceedance; **651** is most conservative (3–5 links).
3. **T3 coverage limited** for 671/252/651 — pair with Step 4b rep caution before interpretive A3 language on T3.
4. **252 T3 headline (19/22 pooled)** does **not** survive matched footing at the same rate (10/22) — committee should cite Step 8 counts, not Step 4 pooled validation alone.
5. **Protocol-openness** is participant-specific; ex13/ex09 ratio is descriptive context only (supervisor wording pending in `SUPERVISOR_NV_DECISION.md`).

---

## 8v6. Signed NV profile — S0–S3 tiers (Step 8v6)

**Source:** `step08_nv_and_stability/NV_PROFILE.csv`, `nv_summary.csv` · **Module:** `src/gaga_jcvpca/nv_profile.py` · **Script:** `scripts/observed_nv.py`

**Status:** provisional Phase-0 defaults (see `SUPERVISOR_NV_DECISION.md`) — supervisor confirm pending.

Per-link signed value = **EVR-weighted signed sum** of `JcvPCA_link` over retained PCs (floor and effect share `A = T1_R1`, identical weights). **A2 = tier S2** = magnitude exceed **and** reference-direction stability (`sign(long) == sign(long_rev)`, `long_rev` anchored on `T1_R2`). **S3** = S2 + coverage adequate + rep pass (Step 4b k-grid ≥ 0.6) + Step-5 organization.

### A2 pass (S2 or S3) per link

| Participant | T1→T2 A2 pass | T1→T3 A2 pass | S3 candidates |
|---|---:|---:|---|
| 671 | **8/18** (S3=4) | **9/17** | T2: `671_to_LThigh`, `LFArm_to_LHand`, `LShin_to_LFoot`, `LThigh_to_LShin` |
| 252 | 8/22 | **13/22** | none (rep gate fails: k-grid 0.4; T3 coverage limited) |
| 651 | **8/14** (S3=5) | 7/14 | T2: `Chest_to_Neck`, `LFArm_to_LHand`, `LUArm_to_LFArm`, `Neck_to_Head`, `RThigh_to_RShin` |
| 790 | 5/22 | 5/22 | none (rep gate fails: k-grid 0.4) |

### Signed vs abs (why S2 is stricter than the old ratio)

- Signed S2 requires the effect direction to be **invariant to the arbitrary R1/R2 anchor**; several links that passed the abs ratio (>1) are demoted to **S1** (magnitude-only) because the sign flips when the anchor swaps.
- **252**: abs matched exceed was 10/22 at both T2/T3; signed A2 is 8/22 (T2) and 13/22 (T3). The T3 signed count is higher because the T3 effect is larger and directionally consistent even though coverage is limited (→ no S3 elevation).
- **S3 is gated by Step-4b rep stability:** 252 and 790 never reach S3 (their k-grid top-5 overlap bottoms at 0.4). 671 and 651 have S3 candidates only at **T2** (T3 coverage limited).

### Conclusion

1. **A2 (signed exceed) holds for a subset of links in every participant** — strongest, direction-stable evidence is at **T2** for 671/651 and at **T3** for 252.
2. **S3 (candidate-interpretive) exists only for 671 and 651 at T2** — arm-chain (`LFArm_to_LHand`, `LUArm_to_LFArm`) and leg-chain (`LThigh_to_LShin`, `RThigh_to_RShin`) links.
3. **790 is the most conservative** (5/22 A2, no S3) — consistent with its Step-4b caution.
4. Abs matched ratio retained as **deprecated-secondary** columns; committee A2 should cite signed tiers.

---

## 8v6b. Underused-at-T1 links (Step 6)

**Source:** `step06_underused_at_t1/underused_link_results.csv`, `underused_definition.md`

Underused = **bottom tertile** of mean `JRW_A_link` (T1 reference) within participant. Beyond-NV = signed A2 (S2/S3).

| Participant | Comparison | N underused | N increased | N beyond-NV (A2) |
|---|---|---:|---:|---:|
| 671 | T1→T2 | 6 | 6 | 3 |
| 671 | T1→T3 | 5 | 4 | 2 |
| 252 | T1→T2 | 8 | 8 | **7** |
| 252 | T1→T3 | 8 | 3 | 3 |
| 651 | T1→T2 | 5 | 1 | 2 |
| 651 | T1→T3 | 5 | 2 | 4 |
| 790 | T1→T2 | 8 | 1 | 0 |
| 790 | T1→T3 | 8 | 3 | 0 |

### Conclusion

- **252 T1→T2** is the clearest broader-participation signal: **7/8** T1-underused links exceed NV with increased contribution (interpretive, supervisor-gated).
- **671 T2** all 6 underused links increased (3 beyond NV).
- **790** shows underused links mostly **not** increasing/exceeding → do **not** claim underused activation for 790.

---

## 8v6c. Contribution distribution (Step 7)

**Source:** `step07_contribution_distribution/distribution_metrics.csv`, `distribution_summary.md`

Top-1 share and normalized Shannon entropy of link contribution to the shared subspace (`JRW_A` = T1, `JRW_B` = follow-up).

| Participant | top1 T1→fu (T2 / T3) | entropy T1→fu (T2 / T3) |
|---|---|---|
| 671 | 0.13→0.13 / 0.13→0.13 | 0.91→0.92 / 0.92→0.92 |
| 252 | 0.14→0.14 / 0.14→0.14 | 0.88→0.88 / 0.88→0.88 |
| 651 | 0.16→0.16 / 0.16→0.15 | 0.90→0.90 / 0.90→0.91 |
| 790 | 0.14→0.14 / 0.14→0.14 | 0.88→0.89 / 0.88→0.89 |

### Conclusion (important hedge)

- **No participant shows a meaningful shift in dominance or breadth**: top-1 share moves ≤ 0.01 and entropy moves ≤ 0.01 in every comparison.
- **Change is link-specific reweighting, not global broadening.** Do **not** claim "more distributed participation" at the whole-body level. The story is *which* links redistribute (A4), not that the overall distribution flattens.

---

## 8v6d. T2 vs T3 persistence (Step 9)

**Source:** `step09_persistence_t2_t3/persistence_results.csv`, `persistence_summary.md`

Persistence of the signed matched single-rep effect across T2 and T3 (`persistent` = A2 at both, same sign).

| Participant | persistent | emergent_T3 | transient_T2 | sign_flip | sign-agree (all links) |
|---|---:|---:|---:|---:|---:|
| 671 | **6** | 3 | 1 | 0 | 71% |
| 252 | 3 | **10** | 5 | 0 | 41% |
| 651 | 3 | 3 | 4 | 1 | 64% |
| 790 | 1 | 4 | 4 | 0 | 73% |

**Persistent A2 links:** 671 `671_to_Ab, 671_to_LThigh, 671_to_RThigh, LFArm_to_LHand, LShin_to_LFoot, LThigh_to_LShin`; 651 `Chest_to_Neck, Chest_to_RShoulder, Neck_to_Head`; 252 `Chest_to_Neck, Neck2_to_Head, Neck_to_Neck2`; 790 `RUArm_to_RFArm`.

### Conclusion

- **671 is the most temporally stable** (6 persistent links, 71% sign agreement) — its arm/leg-chain effects hold at both T2 and T3.
- **252 is dominated by `emergent_T3`** (10 links) with only 41% sign agreement — the T3 change is largely **new** relative to T2, not a continuation, and directions are less consistent. Consistent with T3 coverage-limited + rep-fringe caution.
- Persistence is **descriptive**; it cannot separate instruction-following from lasting change (design limit).

---

## 9. Cross-cutting conclusions (so far)

### Supported (descriptive / heuristic)

1. **Step 0** claim scope and evidence gates locked; interpretive tier needs supervisor sign-off (`SUPERVISOR_NV_DECISION.md`).
2. **Step 1** exploration validated `ex09_13` window; Step 4 trunk-inclusive runs supersede pre-trunk link counts.
3. All four participants complete **Step 4** pooled runs with longitudinal T1→T2/T3.
4. **252 T3** shows largest \|ΔJcvPCA\| (e.g. RUArm_to_RFArm 0.350); matched single-rep exceed **10/22** (pooled floor 19/22 overstates).
5. **Organization > amplitude** for 252 T3 exceed-NV links (19/19 organization, Step 5).
6. **Dominant PC band (50% EVR)** more rep-stable than full 80%-EVR top-5 in most cases (Step 4b).
7. **252 partial robustness** is rep-fringe instability; dominant mode stable at p50 (especially T3); not spine-driven.
8. **790 T3 partial** is stronger: rep + k-grid both fail at dominant bands.
9. QC-drop and k-grid do **not** explain 252 partial — rep-mode is the failing axis.

### Not yet supported / pending

1. **Supervisor sign-off** on Phase-0 v6 spec locks + interpretive tier (`SUPERVISOR_NV_DECISION.md`).
2. **Step 8h Layer 2** subsample stability (optional, firewalled).
3. **Step 10** `FINDINGS_SUMMARY.csv` migration.

### Forbidden (unchanged)

Population inference, causality, anatomical joint-angle claims, significance language — see `CLAIMS.md`.

---

## 10. Committee phrasing snippets (approved style)

> *Dominant-variance coordination (PCs to 50% T1 EVR) is more stable across repetitions than the full 80%-EVR link ranking.*

> *Where full-subspace ranking is rep-sensitive but p50 overlap is high (252 T3), borderline top-5 membership — not reversal of the dominant pattern — drives the partial label.*

> *252 T3 NV-exceeding links show flat ROM ratios, consistent with contribution redistribution rather than amplitude increase.*

> *790 T3 shows rep and k-grid sensitivity even at the dominant PC band — interpret with stronger caution than 252.*

> *Longitudinal change is compared to same-condition repetition variability on matched single-rep footing (Step 8), not pooled repetition spread.*

> *Where T3 reference-subspace coverage is limited (671, 252, 651), link-level redistribution claims carry a coverage caution even when the matched ratio exceeds 1.*

> *The A2 gate is a signed exceed: the longitudinal change must be larger than the T1 repetition spread **and** keep its direction regardless of which T1 take is used as the reference (S2). Magnitude-only exceedances (S1) are reported but not counted as validated.*

> *Overall contribution breadth (entropy, top-1 share) is essentially unchanged across timepoints — the effect is redistribution among specific links, not a global broadening of participation.*

> *671's arm- and leg-chain contribution changes persist across both T2 and T3; 252's T3 changes are largely emergent at T3 rather than a continuation of T2.*

---

## Update log

| Date | Step | What was added |
|---|---|---|
| 2026-07-14 | 4b | Robustness labels, rep diagnostics, functional PC bands |
| 2026-07-14 | 4b ext | p50/p60 rep-mode overlaps |
| 2026-07-14 | 5 | Amplitude vs organization classification |
| 2026-07-14 | gap-fill | §1b k-grid/QC/functional chain; §2b R2 bands; §5 top-5 links; §6 Steps 2–3; full amplitude table |
| 2026-07-17 | 0, 1, 4 | Step 0 claim map; Step 1 pre-trunk baseline; Step 4 headline runs (selected_m, regions, \|Δ\|) |
| 2026-07-17 | 8h | Matched single-rep exceed counts, coverage bands, per-exercise NV, ex13/ex09 ratios |
| 2026-07-18 | 8v6 | Signed NV profile S0–S3 tiers (`nv_profile.py`); A2 pass counts; S3 candidates |
| 2026-07-18 | 6, 7, 9 | Underused-at-T1; contribution distribution (entropy/top-1); T2 vs T3 persistence |

---

## Next updates (planned)
- **Step 8v6 confirm:** lock Phase-0 defaults with supervisor; re-run if any default changes
- **Step 10:** migrate key columns to `FINDINGS_SUMMARY.csv`; this digest becomes narrative companion
