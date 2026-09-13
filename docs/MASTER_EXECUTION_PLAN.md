# Master execution plan — committee case study, feature pilot, and publish path

**Status:** active plan (v4 — protocol window, 4 participants, skeleton mapping)  
**Purpose:** Complete step-by-step roadmap for jcvPCA case study (Gaga framing, trunk inclusion, NV strengthening, 4-participant within-N analysis, committee wrap, methods publication).  
**Not day-scheduled** — execute in order; each step lists prerequisites and decision gates.

**v4 decisions (locked):**
- **Primary window:** `ex09_13_contiguous` pooled — all four participants (671, 252, 651, 790).
- **Exercise language:** canonical `ex{NN}` only (`ex09`–`ex13` = Group4 curvilinear block). **No** Gaga `P1`–`P5` exercise aliases.
- **Task Part:** `P1` in session keys = **Task Part 1** (`{pid}_T{t}_P1_R{r}`), covering **ex01–ex17** per session. Never use `P1`–`P5` to mean exercises.
- **Old exploration winners** (`ex11_single`, `ex10_14_contiguous`, etc.) **dropped** from this plan.
- **Sensitivity** = defined framework (Step 4b), not alternate exercise windows.

**v5 decisions (validation-layer lean, locked):** the NV/robustness layer is restructured to remove conflation, redundancy, and significance-adjacent reporting. These supersede any conflicting v4 text below.
- **Two explicit, firewalled layers.** *Layer 1 — observed same-condition repetition variability* (across genuinely separate takes) is the **only** input to any "exceeds observed variability" logic. *Layer 2 — temporal-subsample sensitivity* (how the result moves under within-take block resampling) is **descriptive robustness only** and **never** feeds the floor.
- **Reference-subspace coverage is a validity gate**, read *before* both layers. If B is poorly represented in A's retained subspace, link-level JcvPCA interpretation is limited for that pair.
- **No frame-resampled "NV floor," no bootstrap CI as inference, no p90/p95 threshold.** Bootstrap is removed from the claim machinery; it survives only as an optional Layer-2 descriptive probe. Tiers B/C/D are removed; only **Tier A (descriptive Δ + matched single-rep ratio) + a robustness label** remain.
- **Matched footing:** the primary exceed-floor comparison is single-rep ÷ single-rep — `(T1_R1 vs T2_R1) / (T1_R1 vs T1_R2)`. Pooled longitudinal is the descriptive headline effect and is **not** divided by a mismatched single-rep floor. A pooled-rep NV reference is **not constructible** with 2 reps.
- **NV summaries** at n≈3–5 exercise units: individual per-exercise values + median + range (MAD caveated). No p90/p95.
- **Per-exercise NV across timepoints (Step 8h):** `ex09`–`ex13` singles at **T1, T2, and T3** (`R1↔R2` each) to characterize protocol-unit openness — descriptive only; **not** improvisation-skill or treatment claims.
- **Functional vs secondary PC labeling (Step 4b + 8h):** `p_functional_50` / `p_functional_60` from T1 cumulative EVR in `functional_pc_bands.csv`. Label PCs `p_functional_50+1 … selected_m` as **secondary** (not "null") in committee docs.
- **Effective information:** independent units = repetitions × exercises, **never frames**. Autocorrelation is measured once to justify block length; no formal multivariate effective-N estimator.
- **Vocabulary lock:** "reference range," "subsample spread," "coverage warning," "dominant PCs," "secondary PCs" — never "CI," "significance," "percentile threshold," "improvisation skill."

**v6 decisions (signed NV profile — supersedes abs-only exceed where noted, 2026-07-17):**
- **Per-link signed NV is primary.** jcvPCA link Δ is signed (`JRW_B − JRW_A`); NV profile and exceed logic use **signed** `nv_signed_t1` and `long_signed` on the **same link**. Never average \|Δ\| or signed Δ **across links** for committee NV conclusions.
- **Claim A2 (revised):** minimum evidence = **S2 — signed consistent exceed**: `|long_signed| > |nv_signed|` on the same link **and** `sign(long_signed)` robust to the arbitrary R1/R2 reference-take choice (**reference-direction stable**), not abs ratio > 1 alone. **S1** (magnitude exceed but direction not reference-stable) is reported separately — not counted as validated exceed. *(Sign-consistency = reference-direction stability, NOT "same sign as the R1→R2 rep difference"; the R1/R2 label has no physical order, so the NV sign is label-dependent. Phase-0 supervisor confirm.)*
- **Primary estimand lock:** pooled `ex09_13` block — `(T1_R1 vs T2/T3_R1) / (T1_R1 vs T1_R2)` on **single-rep, signed**, same window, same T1 basis. `long_signed_single` (`T1_R1 vs T{k}_R1`) is the A2 estimand — **not** the pooled longitudinal. Pooled longitudinal (Step 4) remains descriptive headline only and uses a **different basis** (pooled T1); report the single-rep signed effect next to it.
- **Signed per-link aggregation:** per-link signed value = **EVR-weighted signed sum** of `JcvPCA_link` across retained PCs (`Σ_pc weight_A_pc·(JRW_B − JRW_A)`, i.e. the existing `weighted_JcvPCA_link`); **never** `mean(|Δ|)` (discards sign), **never** naive signed mean across PCs (can cancel), **never** a cross-link average. Same aggregation for `long_signed` and `nv_signed`. Phase-0 lock (plain signed sum is the fallback).
- **Same-movement rule:** per-exercise NV strengthens a claim **only** with **per-exercise matched longitudinal** on that exercise (`long_ex_k / nv_ex_k`). ex11_13 aggregate, LOO, and cross-exercise ratios are **diagnostics or protocol-openness only** — they do **not** confirm the pooled-block A2 estimand (different movement / different estimand).
- **Paper mapping:** paper NV = random splits of **repeated discrete movements** → distribution. We cannot reproduce that with 2 improvised takes. Layer 1 = genuine R1↔R2; Layer 2 = **within-exercise-segment** contiguous block resampling (spread only, firewalled). **No** frame shuffle, pseudo-rep half-split, or imputation as NV floor.
- **New outputs:** `NV_PROFILE.csv`, `link_exercise_nv.csv`; `NV_EVIDENCE.csv` v2 schema; deprecate cross-link `mean_abs_nv` in `exercise_level_nv.csv`.
- **Implementation detail:** see [Step 8v6 — signed NV implementation roadmap](#step-8v6--signed-nv-implementation-roadmap). Working copy: `docs/SIGNED_NV_PROFILE_PLAN.md` (kept in sync with this section).

**Coverage note:** See [Appendix A — Chat coverage matrix](#appendix-a--chat-coverage-matrix) at end of this document for mapping from conversation topics → steps.

**Primary audiences:**
- Supervisors (written case study package)
- PhD committee (slides built from that package)
- Future journal submission (Methods/Application Note first)

---

## Mission (one paragraph)

Deliver a **rigorous, modest, evidence-backed case study** across **four participants** (671, 252, 651, 790) using the **protocol-complete Group4 window** (`ex09`–`ex13`, pooled) showing that reference-anchored jcvPCA on whole-body MoCap can quantify **redistribution of link contribution** to shared movement-variance structure before vs after the intervention period — framed as a **conservative proxy** for Gaga-inspired “broader access to underused degrees of freedom,” **without** claiming dormant motors, timing change, causality, or population effects. Close methodological gaps (skeleton/link harmonization, trunk under-selection, amplitude vs organization, observed-NV strength), run **all defensible descriptive NV computations** (coverage gate + Layer-1 observed variability + matched single-rep ratio; no bootstrap floor/CI), then let supervisors set claim wording before committee packaging.

---

## Global constraints (never violate)

| Rule | Rationale |
|---|---|
| Sacred jcvPCA core unchanged | `compute_jcvpca`, RSS aggregation, golden tests |
| T1 always reference A | Paper-faithful |
| Observed NV = same-condition repetition variability (Layer 1) | Estimated from genuinely separate takes: per-exercise `T1 R1 vs R2` (primary) + `ex09_13` reference row. Descriptive reference range, never a significance threshold. **Not** frame-resampled |
| Coverage gate before interpretation | Reference-subspace coverage read first; poor coverage → link-level JcvPCA interpreted cautiously for that pair (see Step 8h.0) |
| Layer 2 firewalled | Temporal-subsample / block-resampling stability is descriptive robustness only; it never enters the exceed-floor logic |
| No significance-adjacent NV reporting | No bootstrap NV floor, no bootstrap CI as inference, no p90/p95 threshold; only Tier A + robustness label |
| NV profile per link, signed | No cross-link mean/median \|Δ\| for exceed conclusions; per-link value = EVR-weighted signed sum (never mean-\|Δ\|); A2 = S2 = magnitude exceed + **reference-direction stable** sign (v6) |
| Same-movement stratum rule | Per-exercise NV confirms only per-exercise longitudinal; LOO/ex11_13 do not strengthen pooled A2 |
| Within-participant only | Four N-of-1 cases; no cohort inference |
| No JsvCRP / phase / RQA in this plan | Improv alignment risk; deferred |
| Claim language conservative | See Step 0; NV wording chosen with supervisors after Step 8 |
| Naming: `P1` = Task Part 1 only | Session scope ex01–ex17; exercises = `ex{NN}`; no Gaga exercise aliases |
| Inclusive QC | Include all feasible links per skeleton; exclude only clearly un-analyzable segments |

---

## Tiered execution — critical path first (v4)

The 14 steps below are the **full** spec. For the committee sprint, execute by tier. Do **not** run Tier 3 before Tier 1 is done.

### Tier 1 — Committee-critical (must do; nothing honest can be presented without these)
Ordered critical path:

```
0 Claims → 1 Baseline → 2 Link mapping → 3 Trunk+QC → 4 Primary (4 pids)
  → 4b Sensitivity → 5 Amplitude → 8 NV compute-all → 10 Synthesis → 11 Committee docs
```

- **Step 0** — claims/limits + naming lock (`P1` = task part; `ex{NN}` exercises)
- **Step 1** — baseline snapshot of `ex09_13` exploration runs (½ day)
- **Step 2** — two skeleton baselines + canonical link map + comparability flags (NEW)
- **Step 3** — trunk + all feasible links per marker setup; inclusive QC policy
- **Step 4** — primary runs: `ex09_13_contiguous` pooled, **all four participants**
- **Step 4b** — one merged robustness analysis (PC-count k-grid, repetition-mode, QC-drop) + link-pattern stability — **not** alternate windows
- **Step 5** — ROM/RMS covariate (answers "isn't this just bigger movement?")
- **Step 8** — Tier A descriptive ratio + **matched single-rep ratio** + **reference-subspace coverage gate**; **8h Layer-1 observed NV** (per-exercise); supervisor meeting sets claim wording
- **Step 10 / 11** — synthesis + brief/one-pager/narrative + avatars on `ex09_13`

### Tier 2 — Cheap, high-value (pure post-hoc on CSVs you already produce; add if Tier 1 done)
- **Step 6** — underused-at-T1 links (directly supports the hypothesis)
- **Step 7** — contribution distribution (entropy / top-1 share)
- **Step 9** — T2 vs T3 persistence
- **Step 8h Layer 2** — temporal-subsample / contiguous block-resampling stability (fixed `m`), **descriptive only, firewalled from the floor** — optional after Layer 1 is clean

### Tier 3 — Defer / optional (NOT before committee)
- **Step 2-FS** — BVH feature pilot (old Step 2) → **off critical path.** Rotvec is primary. Committee: one *future-direction* slide only.
- **Step 8i** — NV injection calibration → **deferred to methods note** (Step 12b); not committee-critical
- **Step 8h optional** — ex11_13 aggregate percentile characterization beyond median/range, principal-angles NV-basis, cohort-link subset, window-length/jitter/frame-removal, session-fraction curve
- **Step 12b** — methods-note validation tasks (synthetic, naive-PCA baseline) → parallel/after
- **Step 14** — JsvCRP / RQA / EMG → out of scope

**Efficiency rule:** if a step's likely output is "insufficient / inconclusive at current N," spend minutes documenting that honestly, not hours forcing it. Honesty about limits *is* the rigorous result.

---

## Post-step → `METRICS_DIGEST.md` (required after every step)

After **each step** completes (including sub-steps like 4b and 8h), run a short **metrics digest review** before starting the next step. This keeps conclusions auditable and prevents insights from living only in chat or scattered CSVs.

**Living document:** `results_committee_case/METRICS_DIGEST.md`  
**Formal end state (Step 10):** key columns migrate to `FINDINGS_SUMMARY.csv`; digest remains the narrative companion.

### Review procedure (agent or human)

1. **Code delta** — `git diff` / changed scripts, configs, tests, pipeline outputs. Note *what ran* and *what new columns/files exist*.
2. **Chat delta** — scan the session for interpretive conclusions, caveats, or metric readings not yet in a file. Do not invent metrics; only promote what is evidenced.
3. **Offer append block** — propose a concrete patch to `METRICS_DIGEST.md`:
   - new or updated **table** (numbers + source path)
   - **Conclusion** bullets (1–3 sentences, committee-safe)
   - **Update log** row (date, step id, one-line summary)
4. **User gate** — present the offered block; append only after confirmation (or explicit “add it” instruction).

### What belongs in the digest vs elsewhere

| Put in `METRICS_DIGEST.md` | Keep elsewhere |
|---|---|
| Cross-participant metric tables | Per-run `run_summary.md`, raw CSVs |
| “What we can conclude so far” | `CLAIMS.md`, `LIMITS.md` (rules) |
| Committee phrasing snippets | `ROBUSTNESS_FRAMEWORK.md` (method spec) |
| Status dashboard (steps done/pending) | This plan (execution order) |

### Per-step metrics to offer (checklist)

| Step | Metrics / conclusions to append |
|---|---|
| **0** | Claim tiers, forbidden language, primary window lock |
| **1** | Pre-trunk link counts, NV exceed counts (exploration), confound list |
| **2** | Skeleton classes, comparability flags, canonical link counts |
| **3** | Trunk links added, QC caution counts, convert readiness |
| **4** | `selected_m`, top links per pid×comparison, validation pass/fail |
| **4b** | `robustness_label`, rep overlaps (all + p50/p60), functional PC bands |
| **5** | organization vs amplitude counts per pid×comparison |
| **6** | underused-at-T1 links, secondary-PC band overlap |
| **7** | top-1 share, entropy, redistribution direction |
| **8 / 8h** | coverage bands, matched ratio exceed counts, per-exercise NV T1/T2/T3, ex13/ex09 ratios |
| **9** | T2 vs T3 sign agreement, persistence flags |
| **10** | migrate digest tables → `FINDINGS_SUMMARY.csv`; synthesis conclusions |
| **11** | final claim wording traceability (which digest rows support each slide) |

### Digest section template (copy when offering an append)

```markdown
## N. <Topic> (Step X)

| … metric table … |

**Source:** `<path/to/csv or md>`

### Conclusion
- …

---
<!-- update log -->
| Date | Step | What was added |
```

---

## Output folder layout

```
results_committee_case/
  step00_claim_framework/
  step01_baseline_audit/
  step02_link_mapping/           # skeleton baselines + canonical link table
  step02_feature_pilot/          # rotvec vs BVH (Tier 3 only)
  step03_trunk_extension/
  step04_primary_runs/
  step05_amplitude_vs_organization/
  step06_underused_at_t1/
  step07_contribution_distribution/
  step08_nv_and_stability/
  step09_persistence_t2_t3/
  step10_interpretation_package/
  RUN_OUTPUT_SPEC.md              # tiered per-participant outputs (scaling template)
  METRICS_DIGEST.md               # living rollup — updated after each step (see Post-step section)
  figures/
  FINDINGS_SUMMARY.csv

docs/
  COMMITTEE_BRIEF.md
  SUPERVISOR_ONE_PAGER.md
  MASTER_EXECUTION_PLAN.md       # this file
  METHODS_NOTE_OUTLINE.md        # Step 12
```

---

# STEP 0 — Claim framework and scope lock

### Scope
Define what the project **can** and **cannot** say — before any new analysis. Prevents overclaiming in committee and publication.

### Method
Write a fixed vocabulary table adopted by all downstream steps and documents.

**Allowed claims (operational):**
- Link/region **relative contribution** to shared variance structure changed T1 → T2/T3.
- Change **exceeds observed T1 R1–R2 variability** (descriptive; not significance).
- Pattern is **consistent with** broader participation of previously low-contributing links.
- **Contribution redistribution** occurred (some links ↑, some ↓) — if supported by data.

**Forbidden claims:**
- Dormant / remote motors activated or proven.
- Gaga or psilocybin **caused** the change.
- Improved timing, synchronization, or less segmentation (no dynamic metrics in scope).
- Richer adaptable repertoire vs noise (without structured variability evidence).
- Population-level effect.
- Anatomical joint-angle or muscle-use statements (features are **relative link rotvecs**, not ISB/Euler unless Step 2 promotes parallel stream and even then: contribution only).

**Measurement honesty (include in LIMITS.md):**
- jcvPCA measures **contribution to shared variance structure**, not “joint moved more” alone (Step 5 required).
- Improvisational movement → high within-condition variability; observed NV is a **descriptive reference range** built from 2 repetitions × ~3–5 exercises, **not** a significance threshold and **not** pure measurement noise (it necessarily contains genuine improv movement differences).
- Reference-subspace coverage limits: where B is poorly represented in A's retained subspace, link-level redistribution is interpreted cautiously (paper's "entirely different strategy" caveat).
- Effective information = repetitions × exercises, **never frame count**; more frames stabilize a point estimate but add zero independent repetitions.
- Blinded timepoint labels: report **contribution-structure differences across timepoints** without drug/causal language until unblinding protocol allows.

**Vocabulary lock (adopt in LIMITS.md and all outputs):** use "observed repetition variability / reference range," "subsample spread," "coverage warning," "robustness label." **Never** use "confidence interval / CI," "significant / significance," "p-value," or "percentile threshold" for any N-of-1 result. p90/p95 are not reported as thresholds.

**Gaga bridge phrase (use verbatim style):**
> *Gaga practice motivates the hypothesis of broader functional access to underused movement degrees of freedom. We operationalize this as change in the relative contribution of body links to whole-body movement-variance structure, measured by reference-anchored jcvPCA.*

### Deliverable
- `results_committee_case/step00_claim_framework/CLAIMS.md`
- `results_committee_case/step00_claim_framework/LIMITS.md`
- `results_committee_case/step00_claim_framework/EXPERIMENTAL_DESIGN.md` — what T1/T2/T3 and R1/R2 **mean in the study protocol**; **Task Part 1 (`P1`)** = full session block **ex01–ex17**; primary analysis window = **ex09–ex13** (Group4); explicit note that instruction vs lasting learning **cannot** be separated with current design (feeds committee Q&A)
- `results_committee_case/step00_claim_framework/NAMING.md` — vocabulary lock: `P1` = task part only; exercises = `ex{NN}`; remove/deprecate `gaga_group4_aliases` from config and UI

### Supporting
- Paper review (Dubois et al. 2025)
- `docs/MASTER_PLAN.md` §14 limitations
- Chat consensus on no JsvCRP

### Implementation logic
All later steps write results into tables that map to **claim tier** (simplified in v5):
- Tier A: descriptive fact (metric value) **and** matched single-rep ratio vs observed repetition variability
- Interpretive (consistent with hypothesis): requires Tier A + adequate reference-subspace coverage + robustness label (stable across k-grid / repetition-mode / QC-drop) + amplitude check (Step 5)
- (Removed: bootstrap "NV floor" / bootstrap-CI / combined tiers B/C/D — not supported at this N)

### Decision junction
**Proceed when:** supervisors agree claim scope is acceptable (or you accept proceeding with documented limits for committee).

**Stop if:** stakeholders require causal or timing claims — those need different methods (out of scope).

**Post-step:** offer `METRICS_DIGEST.md` append — claim tiers, vocabulary lock, primary window.

---

# STEP 1 — Baseline audit and protocol window lock

### Scope
Freeze **what exists today** for the **protocol primary window** (`ex09_13_contiguous`) before new runs. Establish the “before trunk / before 651–790 committee runs” state.

### Method
1. Copy exploration artifacts for **`ex09_13_contiguous` pooled** (671, 252) and spot-check 651/790 inventory readiness:
   - Pre-trunk exploration runs under `results_exploration_671_252/runs/{pid}/ex09_13_contiguous/pooled/`
2. Collect per participant: `link_level_results.csv`, `region_level_results.csv`, `functional/null_space_results.csv`, `natural_variability_results.csv`, `validation_results.csv`, `selected_m_by_comparison.csv`, `run_summary.md`, `reproducibility_manifest.json`.
3. Note pre-trunk link count and missing `trunk_spine` links.
4. Document known confounds: 671 T3 marker-set prefix; topology differences (671-style 51-bone vs 252-style 55-bone); participant-specific pelvis roots.
5. Write two paragraphs: **“What we can conclude from pre-trunk exploration”** / **“What we cannot yet.”**
6. **Do not** copy or cite old exploration winner windows — they are out of scope for v4.

### Deliverable
- `results_committee_case/step01_baseline_audit/` (exploration snapshot for `ex09_13` where available)
- `BASELINE_SUMMARY.md` (2 pages max)
- `KNOWN_CONFOUNDS.md`
- `PARTICIPANT_READINESS.md` — 671/252/651/790: segmentation present?, matrices converted?, topology class

### Supporting
- `results_exploration_671_252/runs/{671,252}/ex09_13_contiguous/...`
- `data/segmentation/{671,252,651,790}_ex_segmentatios_frames.xlsx`

### Implementation logic
No code changes. Pure inventory so every later delta is auditable (“trunk added → NV count went from X to Y”; “651 added → mapping flags applied”).

### Decision junction
**Proceed when:** baseline folders exist and **`ex09_13_contiguous` confirmed** as locked primary for all four participants.

**Post-step:** offer digest append — exploration NV exceed counts, confounds, participant readiness.

---

# STEP 2 — Canonical skeleton baselines & link mapping

### Scope
Define **two baseline skeleton/marker setups** (671-style 14-link core vs 252-style 16-link core), extend both with **trunk segments**, and produce **one canonical link mapping table** with cross-participant comparability flags. Required before trunk-inclusive manifests and 651/790 primary runs.

### Method
1. **Classify each participant** (671, 252, 651, 790) into a marker-setup baseline via DataDescriptions + sample skeleton CSV:
   - **Setup A (671-style):** 51 bones, no Spine2/Neck2, trunk chain `Root→Ab→Chest→…`
   - **Setup B (252-style):** 55 bones, Spine2 + Neck2 present, extended trunk chain
2. **Per setup**, enumerate **all feasible parent→child link pairs** (limbs + trunk + pelvis attachments present in that skeleton). Do not pre-drop trunk.
3. Build `configs/canonical_link_map.csv` (or `data/link_mapping/canonical_link_map.csv`):
   - `canonical_link_id` (participant-neutral anatomical name, e.g. `pelvis_to_LThigh`, `Ab_to_Chest`)
   - `region_id`, `anatomical_description`
   - `comparability` = `cohort` | `setup_specific` | `participant_only` | `topology_variant`
   - per-participant columns: raw bone parent/child, manifest `link_id`, rotvec column stem, `present_in_skeleton` (Y/N)
4. **Overlap matrix:** for each canonical link, flag which participants share an identical or mappable segment; flag where skeleton topology prevents cohort comparison (e.g. 252 `Spine2` intermediates vs 671 direct `Ab→Chest`).
5. **Marker-set audit** per participant × session (T1/T2/T3): prefix consistency; record in `MARKER_SET_AUDIT.md`.
6. Regenerate participant feature manifests from mapping table (not blind template clone).

### Deliverable
- `results_committee_case/step02_link_mapping/SKELETON_BASELINES.md` (two setups + participant assignment)
- `results_committee_case/step02_link_mapping/canonical_link_map.csv`
- `results_committee_case/step02_link_mapping/COMPARABILITY_MATRIX.md`
- `results_committee_case/step02_link_mapping/MARKER_SET_AUDIT.md`
- Updated `data/feature_manifests/*` per participant (draft → QC in Step 3)

### Supporting
- Step 1 inventory
- `data/descriptions/*_DataDescriptions.csv`
- `src/gaga_jcvpca/feature_manifest_gen.py` (topology assessment)

### Implementation logic
```
DataDescriptions hierarchy per participant
→ assign setup A or B (+ note variants)
→ enumerate feasible links including trunk
→ map to canonical_link_id + comparability flag
→ write manifests keyed to actual bone names
```

### Decision junction
| Outcome | Action |
|---|---|
| All 4 pids classified + mapping table complete | Step 3 trunk QC on full feasible set |
| Unknown topology (not A or B) | Document; assign `topology_variant` links as participant_only |
| Marker-set change within participant (e.g. 671 T3) | Flag sessions; restrict cross-timepoint to shared links per MASTER_PLAN |

**Do not proceed to Step 4 until:** canonical map exists and each participant has a manifest derived from it.

**Post-step:** offer digest append — skeleton classes, comparability matrix summary, link counts per setup.

---

# STEP 2-FS — Feature-stream pilot: rotvec (S0) vs BVH Euler (S1)

> **TIER 3 — moved OFF the committee critical path (v3).** Rotvec is the decided primary feature. For the committee, this is a *future-direction* slide only. Run the full pilot post-committee, or early only if Tier 1+2 are already done. Do not let BVH alignment work delay Steps 3–11.

### Scope
Decide whether **relative link rotvecs** remain the primary feature stream, or BVH Euler angles become a **parallel interpretability track**. BVH files are now available.

Optional later: S2 ISB-from-quaternion external pipeline — only if S1 fails QC or interpretability and S2 passes QC gate.

### Method
Follow `results_feature_pilot/PLAN.md` with these streams:

| ID | Input |
|---|---|
| S0_rotvec | Current pipeline matrices |
| S1_bvh_euler | User BVH exports |

**Fixed design (identical across streams):**
- Participants: 671, 252, 651, 790
- Window: **`ex09_13_contiguous` pooled** (protocol primary)
- T1 reference; T1 vs T2, T1 vs T3; NV = T1 R1 vs R2
- Pooled longitudinal + single sensitivity
- `variance_threshold=0.80`; sweep 0.70/0.80/0.90

**S1 intake (must complete before jcvPCA):**
1. Inventory BVH files: session coverage T1/T2/T3 × R1/R2 per participant.
2. Document Euler order, units (rad/deg), local vs global, joint naming map → canonical link names.
4. **Alignment test:** slice `ex09_13` window; compare frame count to rotvec matrix (±0 ideal; ≤2 documented).
4. Export tidy per-frame CSV: `frame, joint, axis, value` or wide channel columns.
5. Build feature matrix with same row index as segmentation windows.

**QC gate (per stream × session):**
- Finite values after slice
- Continuity (Euler wrap jumps flagged)
- Drop near-constant channels
- Shared channel set across timepoints
- ROM sanity spot-check on T1

**Scorecard metrics (per stream × participant × window):**
- `n_links_exceeding_nv`, `mean_effect_ratio`, `nv_magnitude`
- Rank stability: pooled vs single; threshold sweep top-5 overlap
- `selected_m` stability
- PCA stability flag
- QC fail rate
- Interpretability note (1–2 sentences)

**Win rule:** S0 stays default unless S1 wins on **QC + NV separability + rank stability** for both participants — not interpretability alone.

### Deliverable
- `results_committee_case/step02_feature_pilot/intake/` (BVH inventory, channel dictionary, alignment report)
- `results_committee_case/step02_feature_pilot/qc/{S0,S1}_qc.md`
- `results_committee_case/step02_feature_pilot/runs/...`
- `results_committee_case/step02_feature_pilot/scorecards/summary.csv` + `summary.md`
- `results_committee_case/step02_feature_pilot/decision_log.md` → one of: `keep_S0` | `add_parallel_S1` | `needs_fix_export`

### Supporting
- BVH files (user-provided; path recorded in `intake/BVH_PATHS.md`)
- Segmentation xlsx for frame windows
- Existing rotvec matrices / convert pipeline
- `results_feature_pilot/PLAN.md`

### Implementation logic
```
BVH → parse/extract Euler channels → align frames to segmentation slice
     → build A/B matrices (same as rotvec pipeline dimensions conceptually)
     → run_comparison() with same jcvPCA core
     → scorecard vs S0
```
Only the **feature construction layer** differs; orchestration and validation reuse `pipeline.run_analysis` pattern or a thin adapter script `scripts/run_feature_pilot.py`.

### Decision junction
| Outcome | Next step |
|---|---|
| S0 wins | Step 3 uses rotvecs only; BVH noted as “evaluated, not adopted” in brief |
| S1 wins parallel | Step 4 runs **both** streams for committee; primary claims still on S0 unless S1 clearly more stable |
| Alignment/QC fails | Fix export; do **not** block Steps 3–10 on S1 — proceed with S0 |
| S2 ISB available + S1 weak | Optional sub-pilot; same scorecard; low priority |

**Post-step (if run):** offer digest append — S0 vs S1 scorecard winner; one-line stream decision.

---

# STEP 3 — Full feasible link set + trunk (inclusive QC)

### Scope
Include **all feasible segments** per participant skeleton/marker setup (from Step 2 map), with **trunk links mandatory** where bones exist. Shift QC from “minimal core template” to **preserve data unless clearly un-analyzable**.

### Method
1. Start from `canonical_link_map.csv` — all links with `present_in_skeleton=Y`.
2. **Trunk links** (map to canonical IDs per setup):
   - Setup A: `Root→Ab`, `Ab→Chest` (+ existing `Chest→Neck`)
   - Setup B: pelvis root → `Ab`, `Ab→Spine2→…→Chest` chain mapped to canonical trunk segments where anatomically alignable; flag `topology_variant` where no 1:1 match to Setup A
3. **Inclusive QC policy** (per link × session × window `ex09_13`):
   - **Include (default):** finite rotvecs, variance > ε, jump rate below `jump_fail`
   - **include_with_caution:** elevated jumps or missing 5–20% frames in window — keep in primary run; test in Step 4b QC-drop axis
   - **Exclude (hard only):** non-finite, near-constant, >20% missing in window, or bone absent in that session's marker set
4. Re-run `run_convert.py` for any participant/session missing new link columns (651, 790 included).
5. Selection YAML: `{pid}_ex09_13_contiguous.yaml` with full feasible included link set.
6. Document every exclusion with reason in `LINK_INVENTORY.md` — target: **maximize included links**.

### Deliverable
- Updated `data/feature_manifests/*` (full feasible + trunk)
- `results_committee_case/step03_trunk_extension/TRUNK_QC.md`
- `results_committee_case/step03_trunk_extension/LINK_INVENTORY.md` (included / caution / excluded + reason)
- `results_committee_case/step03_trunk_extension/QC_POLICY.md` (inclusive rules)

### Supporting
- Step 2 canonical link map
- Raw skeleton + DataDescriptions (all four participants)
- `configs/body_regions.yaml`

### Implementation logic
```
canonical_link_map → participant manifest
→ convert all sessions (671,252,651,790)
→ QC per link with inclusive thresholds
→ write selection YAMLs for ex09_13_contiguous
```

### Decision junction
| Outcome | Action |
|---|---|
| Trunk + feasible links pass inclusive QC | Step 4 primary runs with full link set |
| Single link hard-fails | Exclude that link only; document; do not drop whole region |
| Session-level marker-set mismatch (671 T3) | Shared-link restriction for that comparison only |

**Do not proceed to Step 4 until:** convert verified for ≥1 T1 session **per participant** with trunk columns present.

**Post-step:** offer digest append — trunk links added, QC caution/exclude counts, convert status per pid.

---

# STEP 4 — Primary jcvPCA runs (protocol window, 4 participants)

### Scope
Produce the **authoritative** jcvPCA results for committee brief, avatars, and methods-note worked examples.

### Method
Re-run (fresh) for **all four participants** on the locked protocol window:

| Participant | Window | Mode (primary) | Comparisons |
|---|---|---|---|
| 671 | `ex09_13_contiguous` | **pooled** | T1 vs T2, T1 vs T3, NV |
| 252 | `ex09_13_contiguous` | **pooled** | same |
| 651 | `ex09_13_contiguous` | **pooled** | same |
| 790 | `ex09_13_contiguous` | **pooled** | same |

Parameters (locked):
- `exercise_ids: [9, 10, 11, 12, 13]`; `combine_exercises: true`
- `variance_threshold=0.80`
- `sensitivity_p=2` (functional/null labeling only)
- `--validate` enabled
- Filter: `10 Hz`, order 4 (same as exploration)

Run via `run_analysis.py` + Step 3 selection YAMLs; copy outputs to `step04_primary_runs/`.

### Deliverable
- `results_committee_case/step04_primary_runs/{671,252,651,790}/`
- Full run folders: CSVs, manifests, validation summaries
- `PRIMARY_RUN_INDEX.md` (run_ids, git hash, config snapshot, comparability flags per link)

### Supporting
- Steps 2 (link map), 3 (manifests + convert)
- `scripts/run_analysis.py`
- `results_exploration_671_252/selections/{pid}_ex09_13_contiguous.yaml` (update from Step 3)

### Implementation logic
Unchanged sacred pipeline:
```
load sliced ex09–ex13 matrices → restrict shared features per comparison
→ compute_jcvpca(A=T1,B=T2/T3) → rollups → NV (T1 R1 vs R2) → validation
```

### Decision junction
**Proceed to Step 4b when:** all four participants complete without ValidationError; `selected_m` logged; ≥1 longitudinal comparison produces link table per participant.

**Pause if:** no shared links between T1 and T3 for a participant — apply shared-link restriction; document excluded links.

**Post-step:** offer digest append — `selected_m`, link counts, headline top links per pid×comparison, validation summary.

---

# STEP 4b — Sensitivity & stability framework (not alternate windows)

### Scope
Define and execute **what “sensitivity” and “stability” mean** in this project now that exercise-window exploration winners are **out of scope**. Tests **robustness of the primary `ex09_13` pooled result** — not alternative exercise spans.

**Stability definition (adopted):** PCA stability does **not** mean identical PCA axes across improvised repetitions. It means the **link-contribution pattern stays qualitatively consistent** under reasonable analytical perturbations (PC count, repetition mode, QC drops, windowing).

### One merged robustness analysis (v5 — three axes, one table)

All robustness axes share the **same** stability metrics and write to **one** table. Do not build separate per-axis outputs.

| # | Axis | Primary | Perturbation | Question answered | Required? |
|---|---|---|---|---|---|
| 1 | **PC-count (`k`)** | `m` from 80% EVR (671→8, 252→10) | fixed `k` grid `[4…10]` on **fixed T1 pooled A** | Does the story depend on exactly `m`? | **Yes** (primary PC-count test) |
| 2 | **Repetition design** | pooled `T1(R1+R2)` vs `T2/T3(R1+R2)` | **single** `T1 R1` vs `T2/T3 R1` | Does effect depend on one take? | **Yes** |
| 2b | **Repetition diagnostics** (append to axis 2 rows) | same primary top-5 | pooled vs **R2-only**; **longitudinal R1 vs R2** top-5 overlap | Is instability symmetric across takes? | **Yes** (diagnostic columns) |
| 3 | **QC / link set** | Step 3 full feasible set | exclude `include_with_caution` links only | Survives dropping borderline QC links? | **Yes** |
| 4 | **Functional PC band** | `link_level` (all PCs) | re-label at `p_functional_50` / `p_functional_60` from T1 EVR | Does decomposition change interpretation? | **Yes** (reporting) |

**Removed / deferred (v5):**
- **EVR threshold sweep** — fully subsumed by the k-grid (primary `m` is on `[4…10]`). Optional only if `m` ever falls off-grid.
- **Naive PC-index cosine (`basis_similarity`)** — removed entirely; meaningless at `m=8–10` on improv. Not a gate, not reported.
- **Principal-angles NV-basis characterization** — deferred (descriptive, low actionable value; Tier 3 optional).
- **Cohort-link subset** — deferred until cross-participant comparison is on the table (N-of-1 now).
- **Bootstrap `mean_abs`/`mean_signed` CIs** — removed from the stability hierarchy.

### Link-pattern stability metrics (committee-facing heuristics — NOT p-values)

Report **two** things per axis, nothing more:

| Metric | Role | Pre-registered heuristic (not a validated cutoff) |
|---|---|---|
| **top-k overlap** (`k=5`) vs primary `m` | Quantitative — targets the scientifically relevant top contributors | ≥3/5 overlap |
| **functional-chain consistency** | Interpretive — dominant arm/trunk/leg chain retained in top contributors | qualitative retained/not |

Spearman ρ over the full ranking is **optional** supplementary only (dominated by noisy tail links at 14–16 links); do not lead with it.

### Config sketch (implementation backlog — not yet coded)

```yaml
pca:
  variance_threshold: 0.80
  k_sensitivity:
    enabled: true
    reference: T1_pooled          # A fixed; only k varies
    grid: [4, 5, 6, 7, 8, 9, 10]

validation:
  robustness:
    axes: [k_grid, repetition_mode, qc_drop]
    primary_metric: top_k_overlap
    top_k: 5
    top_k_overlap_threshold: 0.60   # heuristic label only
    functional_chain: true
    spearman: optional              # supplementary, not leading
```

### Method
1. Run **k-grid (#1)** on primary pooled runs: `compute_jcvpca(A=T1_pooled, B=T2/T3_pooled, selected_m=k)` for each `k`.
2. Run **single-rep mode (#2)** for all participants on `ex09_13_contiguous` (also supplies the matched single-rep ratio numerator/denominator — see Step 8).
3. Run **QC-drop (#3)** via `validation.sensitivity_analysis`.
4. Compile **one** `robustness.csv`: participant × comparison × axis × {top_5_overlap, functional_chain_retained, selected_m}.
5. **Append repetition diagnostics** on axis-2 rows: `pooled_vs_R2_overlap`, `longitudinal_R1_vs_R2_overlap` (top-5; descriptive only — does not change `robustness_label`).
6. Write **`functional_pc_bands.csv`**: per participant × comparison — `evr_pc1`, `evr_pc1_pc2`, `p_functional_50`, `p_functional_60`, `selected_m`; top-5 overlap `all` vs `p50` vs `p60`.
7. **Agreement rule (heuristic, not significance):** pattern labelled *stable* if k-grid median top-5 overlap ≥3/5 **and** pooled↔R1 single-rep overlap ≥3/5 **and** QC-drop passes; else *partial* / *unstable* — descriptive only. Repetition diagnostics (R2, R1↔R2) inform interpretation text only.

### Functional vs secondary PC bands (reporting rule)

| Band | Definition | Role |
|---|---|---|
| **Dominant reference (`p_functional_50`)** | minimum PCs with T1 cumulative EVR ≥ **50%** | Primary functional label for full block (~3–4 PCs) |
| **Broad core (`p_functional_60`)** | minimum PCs with T1 cumulative EVR ≥ **60%** | Sensitivity (~4–5 PCs) |
| **Secondary** | PCs `p_functional_50+1 … selected_m` | Subdominant redistribution (rename from "null" in docs) |
| **Combined** | all PCs to 80% EVR (`link_level_results.csv`) | **Primary ranking** for headlines |

`selected_m` (80% EVR) stays the computation dimensionality; `p_functional_*` are **labeling** choices only.

### Deliverable
- `results_committee_case/step04_primary_runs/ROBUSTNESS_FRAMEWORK.md` (definitions — this section)
- `results_committee_case/step04_primary_runs/robustness.csv` (axes 1–3 + repetition diagnostic columns on axis 2)
- `results_committee_case/step04_primary_runs/functional_pc_bands.csv` (EVR-based PC band metadata)
- Single-rep run folders: `{pid}/ex09_13_contiguous/single/`

### Supporting
- Step 4 pooled primary runs
- Step 2 comparability flags

### Decision junction
| Outcome | Action |
|---|---|
| k-grid + repetition-mode + QC-drop all stable | Primary brief uses pooled; robustness cited as "heuristic-supported" |
| Material disagreement or k-sensitive | Report as *partial/unstable*; no interpretive (hypothesis) claims without supervisor sign-off |

**Post-step:** offer digest append — `robustness_label`, rep overlaps (all + p50/p60), functional PC band table, cross-cutting robustness conclusions.

---

# STEP 5 — Amplitude vs organization (ROM/RMS covariate)

### Scope
Answer reviewer/committee question: *Is this just moving bigger, or did contribution **organization** change?*

### Method
For each primary run, per link and session side (T1/T2/T3, pooled or per-rep as appropriate):

1. Compute **ROM** = range(max − min) or **RMS** of rotvec magnitude (√(rx²+ry²+rz²)) over sliced window.
2. Join with `JRW_A`, `JRW_B`, `JcvPCA_link` from link tables.
3. Classify each link longitudinally:
   - **Organization signal:** \|JcvPCA\| exceeds NV AND ROM ratio T3/T1 (or T2/T1) ≈ 1 (e.g. 0.7–1.3 band — document threshold)
   - **Amplitude signal:** ROM increases strongly AND JcvPCA direction consistent with bigger motion
   - **Mixed / ambiguous:** both shift
4. Summarize counts per participant.

### Deliverable
- `results_committee_case/step05_amplitude_vs_organization/rom_rms_by_link.csv`
- `results_committee_case/step05_amplitude_vs_organization/classification_summary.md`
- Optional figure: scatter ROM ratio vs effect_ratio_vs_nv

### Supporting
- Step 4 primary runs
- Rotvec matrices (cached) for magnitude computation

### Implementation logic
Simple post-hoc script `scripts/compute_amplitude_covariate.py`:
```
for each link, each timepoint matrix slice:
  mag_t = sqrt(rx^2+ry^2+rz^2) per frame
  ROM_link = max(mag) - min(mag)  [or RMS]
join to jcvpca link_table + nv_table on link_id
```
No change to jcvPCA core.

### Decision junction
| Pattern | Claim adjustment |
|---|---|
| Many links: high JcvPCA/NV, flat ROM | Strengthen “organization / redistribution” language |
| ROM scales globally | Soften to “combined amplitude and contribution change” |
| ROM flat, JcvPCA flat | “Within variability” — no organization claim |

**Proceed to Step 6 regardless** — amplitude table always included in brief.

**Post-step:** offer digest append — organization vs amplitude counts per pid×comparison; participant headlines.

---

# STEP 6 — “Underused at T1” link analysis

### Scope
Operationalize Gaga “previously underused joints become more involved” **without** dormant-motor language.

### Method
1. At T1 (reference A), compute per-link **baseline contribution**: mean `JRW_A_link` across functional PCs (or all PCs — document choice).
2. Define **underused at T1**: bottom quartile (or bottom tertile — pick one, document) of JRW_A within participant.
3. For each underused link, test longitudinal:
   - `JcvPCA_link` sign (increase vs decrease)
   - `effect_ratio_vs_nv > 1` ?
4. Report: N underused links, N with increased contribution, N exceeding NV.

### Deliverable
- `results_committee_case/step06_underused_at_t1/underused_definition.md`
- `results_committee_case/step06_underused_at_t1/underused_link_results.csv`
- Summary bullet: “X of Y T1-underused links showed increased relative contribution beyond NV at T2/T3”

### Supporting
- Step 4 link tables (T1 reference side)
- Step 5 (cross-check: underused link ↑ with or without ROM ↑)

### Implementation logic
```
groupby link_id → JRW_A functional mean at T1
→ quantile cutoff → flag underused
→ merge longitudinal JcvPCA + NV ratio
→ count exceeds_nv & delta sign
```

### Decision junction
| Outcome | Committee phrasing |
|---|---|
| Several underused links ↑ beyond NV | “Consistent with broader participation hypothesis” (interpretive claim) |
| Only high-baseline links change | Do not claim underused activation |
| Mixed T2 vs T3 | Report each timepoint separately |

**Post-step:** offer digest append — underused-at-T1 link list, exceed-NV counts, secondary-PC band overlap.

---

# STEP 7 — Contribution distribution (dominance vs breadth)

### Scope
Test “less single-joint dominance / more distributed participation” — simple, no dynamics.

### Method
Per participant × timepoint × comparison, on link-level \|JcvPCA\| or JRW values:

1. **Top-1 share:** fraction of total \|contribution\| carried by highest link
2. **Gini** or **entropy** across links (document formula)
3. Compare T1 reference structure vs T2/T3 delta distribution
4. Optional: number of links exceeding NV (already in exploration)

### Deliverable
- `results_committee_case/step07_contribution_distribution/distribution_metrics.csv`
- `distribution_summary.md` (did top-1 share decrease? did entropy increase?)

### Supporting
- Step 4 link tables

### Implementation logic
Pure aggregation on existing CSV outputs — no pipeline rerun.

### Decision junction
- **Entropy ↑ + top-1 share ↓ + NV exceedance:** supports “more distributed participation” (careful wording)
- **Entropy ↓ or top-1 ↑:** do not claim broader participation; report redistribution toward specific links instead

**Post-step:** offer digest append — top-1 share, entropy, redistribution direction per pid×comparison.

---

# STEP 8 — NV evidence (coverage gate + signed NV profile + supervisor wording)

> **v6:** abs-only `matched_single_rep_ratio > 1` is **secondary**. Primary A2 gate = **S2 signed consistent exceed** on pooled `ex09_13` (see tiers below). MVP abs-only outputs in `step08_nv_and_stability/` remain valid until Step 8v6 re-run.

### Scope
Produce **defensible per-link NV evidence** for four N-of-1 cases. Paper-faithful structure: **T1 = reference A**; observed NV = **same-condition repetition variability** between genuine takes (Layer 1). No bootstrap floor, no p-values, no cross-link averaging.

### Paper ↔ committee mapping

| Paper idea | Committee implementation |
|---|---|
| Reference A (baseline) | T1 always side A in jcvPCA |
| NV from repeated same condition | T1 R1↔R2 on **same window** as longitudinal (Layer 1) |
| Effect vs NV distribution | **Single rep-pair reference per link** + optional Layer 2 **subsample spread** (not a distribution) |
| Poor subspace alignment caveat | **Coverage gate** (`coverage_rel`, warning band) |
| Analytical perturbations | Step 4b k-grid, rep-mode, QC-drop (**robustness label**, not NV floor) |
| Amplitude | Step 5 ROM/RMS (**extension**, not in paper NV) |

**Not reproducible here:** paper random splits across many discrete movement repeats → no honest imputation replaces that for committee claims.

### Evidence stack (read per link, in order)

| # | Pass | Same estimand as pooled A2? | Role |
|---|---|---|---|
| 1 | **Coverage** adequate/limited/severe | Yes (T1→T2/T3 pair) | Validity — interpret redistribution cautiously if limited |
| 2 | **S2 signed exceed** on `ex09_13` | Yes | **Primary A2** — `\|long\| > \|nv\|` and same sign |
| 3 | **S1 flag** (magnitude exceed, direction not reference-stable) | Yes | Report explicitly; **not** A2 |
| 4 | **Rep sensitivity** (R1→R2 vs R2→R1; Step 4b rep-mode) | Yes (same block) | Reference-direction / take choice |
| 5 | **Per-exercise matched pair** (`long_ex_k / nv_ex_k`) | Per exercise k only | Secondary read — **same movement k** |
| 6 | **Step 5 organization** (flat ROM) | Yes for that link | Mechanism qualifier |
| 7 | **Layer 2 subsample spread** (within-exercise blocks) | Estimation stability | Paper-**like** spread; **firewalled** from floor |
| — | ex11_13 aggregate, LOO, ex13/ex09 openness | **No** | Diagnostics / protocol texture only |

### Signed NV profile tiers (per link × comparison)

Signed per-link scalars, all anchored on a single T1 take (same retained subspace), each the **EVR-weighted signed sum** of `JcvPCA_link` over retained PCs (never mean-\|Δ\|, never cross-link):
- `long_signed` = `T1_R1 vs T{2,3}_R1` (A2 estimand)
- `nv_signed` = `T1_R1 vs T1_R2` (floor)
- `long_signed_rev` = `T1_R2 vs T{2,3}_R1` (anchor swapped — direction-stability probe only)

| Tier | Rule | Committee use |
|---|---|---|
| **S0** | `\|long_signed\| ≤ \|nv_signed\|` | within T1 repetition spread |
| **S1** | `\|long_signed\| > \|nv_signed\|` **but** `sign(long_signed) ≠ sign(long_signed_rev)` | magnitude exceed, **direction not reference-stable** — report, **not** A2 |
| **S2** | `\|long_signed\| > \|nv_signed\|` **and** `sign(long_signed) = sign(long_signed_rev)` | **A2 minimum** — reference-direction-stable exceed |
| **S3** | S2 + rep/coverage/Step 5 pass (+ optional stratum-K) | candidate interpretive (A3) with supervisor |

**Sign-consistency (v6.1):** defined as **reference-direction stability** — the longitudinal effect keeps its sign whether anchored on `T1_R1` or `T1_R2`. This replaces the earlier "same sign as T1 R1→R2," which was ill-posed (R1/R2 ordering is arbitrary → the NV sign is label-dependent). Phase-0 supervisor confirm.

**ε_sign:** links with `\|nv_signed\| < ε_sign` (default `1e-6`) → `nv_floor_unstable`; do not rely on ratio alone.

**Legacy:** `matched_abs_ratio = |long|/|nv|` and `exceeds_observed_variability` (= magnitude exceed only) retained one release as deprecated columns.

### Interpretation guardrails (v6.1)

- **Reference-basis asymmetry:** jcvPCA projects B into A's (=T1) retained subspace. A clean S2 therefore evidences **reweighting of links within T1's existing coordination subspace** — a *narrower* claim than "access to new degrees of freedom" (novel DOF outside T1's subspace surface as **low coverage**, not redistribution). Coverage-limited S2 is ambiguous; do not let the Gaga "broader access" framing attach to an S2 without this qualifier.
- **Headline vs validated effect use different bases.** The pooled longitudinal headline (basis = pooled T1) and the S2-validated effect (basis = `T1_R1` single-rep) can differ in magnitude or sign. Always report the **single-rep signed effect** next to the pooled headline — the number shown must be the one that passed S2.
- **A2 floor is n=1 rep-pair.** The pooled-block S2 gate rests on a single T1 R1↔R2 pair per link (no margin). "Effective units = reps × exercises" applies to the **descriptive** per-exercise/openness reads, **not** to the A2 gate. Rep-direction asymmetry (S1 vs S2) is the only robustness handle on this scalar floor.

### Method — compute evidence

**8h.0 Coverage gate (read FIRST)** — unchanged: `coverage_abs`, `coverage_rel`, warning band per comparison.

**Tier A — signed profile (primary)**
- Per link (EVR-weighted signed sum across PCs): `nv_signed_t1`, `nv_signed_t1_reverse`, `long_signed_single` (`T1_R1 vs T{k}_R1`, A2 estimand), `long_signed_single_rev` (`T1_R2 vs T{k}_R1`, direction-stability probe), `long_signed_pooled` (context only — **different basis**, see guardrails)
- Classify `nv_profile_tier` S0–S3 via `src/gaga_jcvpca/nv_profile.py` (S2 requires reference-direction stability)
- `exceeds_signed_consistent` = (tier ≥ S2); `sign_reference_stable` = (`sign(long_signed_single) == sign(long_signed_single_rev)`)

**Tier A secondary — magnitude only**
- `matched_abs_ratio`, `magnitude_exceed` (deprecated alias: `exceeds_observed_variability`)

**Supporting Layer 1 (8h)**
- R1↔R2 NV at T1/T2/T3: singles, `ex09_13` reference, ex11_13 aggregate, LOO — all emit **signed** Δ per link in `nv_observed.csv`
- **Per-exercise longitudinal** (new in v6): `T1_R1 vs T2/T3_R1` on each ex09…ex13 → `link_exercise_longitudinal.csv` for matched stratum ratios

**Layer 2 (optional, firewalled)**
- Contiguous block resampling **within each exercise segment** (same rep, same brief) → per-link subsample spread; never floor

### Deliverables

| File | Content |
|---|---|
| `coverage.csv` | Per comparison: coverage + band |
| `NV_EVIDENCE.csv` v2 | Per link × T1→T2/T3: signed fields, tiers, coverage |
| `NV_PROFILE.csv` | Full profile + stratum flags + evidence-stack booleans |
| `nv_observed.csv` | All Layer 1 runs, signed Δ per link (existing) |
| `link_exercise_nv.csv` | link × exercise × timepoint × direction — **no cross-link means** |
| `link_exercise_longitudinal.csv` | link × exercise × comparison — per-exercise long Δ (v6) |
| `nv_summary.csv` | Counts S0/S1/S2/S3 per participant; deprecated exceed counts |
| `EXERCISE_PROTOCOL_OPENNESS.md` | Per-link ranges / ranks; **not** cross-link mean ratios |
| `SUPERVISOR_NV_DECISION.md` | Adopt S2 vs legacy abs; S1 in brief? Layer 2 status |

Cross-ref: `robustness.csv` (Step 4b), Step 5 amplitude tables.

### Decision junction (v6)

| Outcome | Action |
|---|---|
| S2 + coverage adequate + Step 4b stable + Step 5 organization | Candidate A3; Step 11 waits on supervisor |
| S2 + coverage limited | Descriptive A2 OK; hedge interpretive language |
| S1 only | Report magnitude/opposite axis; **not** A2 |
| S0 | "Within observed repetition variability" |
| S2 but Layer 2 spread huge | Caution — estimation-sensitive (descriptive note) |

**Post-step:** offer `METRICS_DIGEST.md` append — S0/S1/S2/S3 counts, abs vs S2 diff, coverage bands.

---

# STEP 8h — Observed NV (Layer 1) + coverage gate + optional Layer 2

> **Status (v5):** restructured into a **validity gate** + **two firewalled layers**. Does **not** modify sacred `compute_jcvpca`. Reuses segmentation, exercise matching, PCA, JcvPCA, QC, aggregation, reporting.  
> **Scope:** **R1↔R2 same-condition variability** at each timepoint — not longitudinal T1 vs T2/T3 (that remains Step 4). Primary emphasis T1; **T2 and T3 required** for protocol-openness characterization.

### What this is NOT (non-duplication)

| Analysis | Step | Comparison |
|---|---|---|
| Longitudinal primary | **Step 4** | T1 pooled `ex09_13` vs T2/T3 pooled `ex09_13` |
| Observed NV reference row | **Step 4 / Step 8** | T1 R1 vs R2 on **full `ex09_13` contiguous** |
| **Step 8h Layer 1** | This step | R1↔R2 on **matched exercises** `ex09`–`ex13` at **T1, T2, T3** + ex11_13 secondary aggregate |

8h does **not** reintroduce alternate primary windows. Exercise units here are for **observed-NV estimation and protocol-structure description only**.

### Background (why two layers)

The JcvPCA paper estimates NV by randomly splitting a set of **repeated discrete movements** many times. Our data are long **improvised** recordings, **2 reps/timepoint**, autocorrelated frames — the paper's random-split NV is not reproducible here. Two distinct questions must be kept separate and **firewalled**:

- **Layer 1 — observed same-condition repetition variability:** how much the link-contribution result differs between *genuinely separate takes* (reps × exercises). This is the **only** input to any exceed-floor logic.
- **Layer 2 — temporal-subsample sensitivity:** how the result moves under within-take contiguous block resampling. **Descriptive robustness only; never enters the floor.**

Above both sits the **coverage gate**: whether B is even adequately represented in A's retained subspace.

---

### 8h.0 — Reference-subspace coverage gate (validity, read FIRST)

For **every** comparison (longitudinal and R1↔R2), quantify how well dataset B lives in A's retained `m`-dim subspace.

- `coverage_abs` = fraction of B's total variance retained after projection into A's retained `m` PCs (= 1 − normalized reconstruction error).
- `coverage_rel` = `coverage_abs` ÷ (variance B's **own** top-`m` PCA retains) — normalizes against B's ceiling (the most faithful "is A a good basis for B" measure).
- `coverage_m_sensitivity` = how `coverage_abs` moves across nearby `m` (descriptive).

**Graded warning bands (pre-registered heuristics, NOT hard cutoffs):**

| Band | Interpretation |
|---|---|
| Adequate | Descriptive note only |
| Limited | Caution: "part of B's structure lies outside retained A space — interpret link-level redistribution cautiously" |
| Severe | Withhold link-level redistribution claims for that pair |

Never a silent automatic rejection. Cross-reference with R1↔R2 direction asymmetry (large asymmetry is a co-signal that the reprojection assumption is shaky).

---

### 8h Layer 1 — observed same-condition repetition variability

**Primary units — matched exercise comparisons (exercise-specific NV), at each timepoint `T1`, `T2`, `T3`:**

- `T{k}_R1_ex09` vs `T{k}_R2_ex09` … through `ex13` (full Group4 block singles)
- `T{k}_R1_ex11` vs `T{k}_R2_ex11`, `ex12`, `ex13` (retain as primary NV floor units for matched ratio context)

Both directions (`R1→R2` and `R2→R1`; report both, **do not average** — asymmetry is a diagnostic).

**Protocol-openness summary (descriptive only — does NOT strengthen pooled A2):**

- Per **link** × timepoint × exercise: signed `delta_jcvpca` from R1↔R2 (from `link_exercise_nv.csv`)
- Summarize **ranges** of \|Δ\| or signed Δ across links per exercise (min–max, count exceeding link-local median) — **never mean \|Δ\| across links** as a primary metric
- `ex13_over_ex09_ratio` per **link** optional; committee table = participant-level **range** of link ratios
- Cross-participant: median/range of link-level values where needed

**Forbidden for A2 confirmation:** using ex13 NV to validate ex09_13 pooled longitudinal (different movements).

**Reference row:** full `ex09_13` contiguous R1 vs R2 at **T1, T2, T3** — **primary NV floor** for pooled A2.

**Secondary — ex11–ex13 aggregate (different estimand):**

- Sequence-level repetition variability; report signed Δ per link
- **Does not** confirm pooled `ex09_13` A2 unless longitudinal is computed on the **same aggregate**

**LOO — dominance diagnostic only:** flag if one exercise drives aggregate NV; **not** stratum confirmation for pooled A2.

**Per-exercise matched stratum (v6 — same movement):**

- For each ex09…ex13: `ratio_k = long_signed(T1_R1 vs T_k_R1) / nv_signed(T1_R1 vs T1_R2)` on exercise k only
- Stored in `NV_PROFILE.csv` columns `stratum_ex09` … `stratum_ex13`, `stratum_S2_count`
- **S3 optional:** S2 on pooled block **and** S2 on ≥ K exercises (supervisor sets K, default K=2)

**Matched exceed-floor (pooled A2):** signed S2 on `ex09_13` single-rep `(T1_R1 vs T2/T3_R1)` vs `(T1_R1 vs T1_R2)` — see Step 8 tiers.

---

### 8h Layer 2 — temporal-subsample sensitivity (OPTIONAL, firewalled)

> Descriptive robustness only. **Never** enters exceed-floor logic. Closest **mechanical** analogue to paper random splits — but measures **estimation stability within one take**, not between-take NV.

- **Fix `m`** at the exercise-segment value.
- **Resample within each exercise segment** of each rep (ex09…ex13 separately) using **contiguous blocks** with length ≥ ~2× autocorrelation time.
- Report per-link **spread** of signed Δ (min, max, median across subsamples), top-5 overlap, functional-chain consistency — label **"subsample spread"**, never "CI" or "NV distribution."
- Blocks are **not** independent repetitions.

**Forbidden as NV floor:** splitting one rep into two temporal halves as pseudo-R1/R2; frame shuffle bootstrap; pooling reps for NV denominator.

**Autocorrelation:** measure once; document block length and non-overlapping block count.

**Script:** `scripts/subsample_stability.py` (backlog).

---

### Critical safeguards

- **No p90/p95 threshold.** Summaries = individual values + median + range (+ caveated MAD).
- **Layer 2 firewalled** from the floor.
- **Coverage** limits interpretation of both layers.
- **Effective n** = repetitions × exercises — **never** frame count.
- **Not valid:** p-values, "CI," pure measurement noise, population NV, causal claims, significance.

### Minimum viable evaluation (MVP)

Per participant (671, 252 first; 651/790 only once Step 3 conversion verified):

| # | Component | Layer |
|---|---|---|
| 1 | Coverage gate for every comparison | Gate |
| 2 | Matched singles ex09–ex13 at T1, T2, T3 — both directions — signed Δ per link | Layer 1 |
| 3 | Reference row ex09_13 at T1, T2, T3 | Layer 1 |
| 4 | **Pooled A2:** S2 signed profile on ex09_13 (`NV_EVIDENCE` + `NV_PROFILE`) | Layer 1 → Step 8 |
| 5 | Per-exercise matched long/NV pairs (`link_exercise_longitudinal` + `link_exercise_nv`) | Layer 1 stratum |
| 6 | ex11_13 aggregate + LOO — dominance / diagnostics only | Layer 1 |
| 7 | Rep asymmetry + Step 4b cross-ref | Robustness |
| 8 | Protocol-openness from **link-level** tables (ranges, not cross-link means) | Descriptive |
| 9 | Functional PC bands per slice | Metadata |
| 10 | Layer 2 within-exercise block spread (optional) | Layer 2 |

**Deprecated MVP artifacts (replace on v6 re-run):** `exercise_level_nv.csv` cross-link means; abs-only exceed as primary gate.

### Required outputs (v6)

**`nv_observed.csv`** — unchanged row grain; **`delta_jcvpca_signed` primary**.

**`link_exercise_nv.csv`** (replaces `exercise_level_nv.csv`):  
`participant`, `timepoint`, `exercise_id`, `reference_direction`, `link_id`, `delta_jcvpca_signed`, `selected_m`, `coverage_rel`, `p_functional_50`, `p_functional_60`

**`link_exercise_longitudinal.csv` (v6):**  
`participant`, `comparison_id`, `exercise_id`, `link_id`, `long_signed_single`, `nv_signed_t1` (from same ex on T1), `stratum_tier`, `stratum_S2`

**`NV_EVIDENCE.csv` v2** — see Step 8 deliverables.

**`NV_PROFILE.csv`:**  
all signed fields (`nv_signed_t1`, `nv_signed_t1_reverse`, `long_signed_single`, `long_signed_single_rev`; EVR-weighted signed sum), `nv_profile_tier`, `sign_reference_stable`, `nv_floor_unstable`, evidence-stack flags (`coverage_ok`, `rep_pass`, `step5_organization`, `stratum_S2_count`, `layer2_spread_flag`)

**`nv_summary.csv`:** counts S0/S1/S2/S3; legacy abs exceed counts for diff

**`EXERCISE_PROTOCOL_OPENNESS.md`** — link-level ranges; protocol vs skill limits

**Removed / deprecated (v5–v6):** cross-link `mean_abs_nv`; abs-only as sole A2; `NV_EVIDENCE_TIERS.csv`; bootstrap NV floor; p90/p95 thresholds.

### Visualization (minimum)

1. Per-link observed NV **individual exercise values** vs the longitudinal effect (one panel per participant).  
2. Coverage warning summary (or table).  

(LOO-dominance and singles-vs-aggregate distribution plots → tables suffice; drop.)

### Integration

| Step | Relationship |
|---|---|
| Step 4 longitudinal | **Unchanged** |
| Step 8 Tier A | Signed S2 profile on pooled block; abs ratio secondary |
| Step 4b robustness | Rep-mode / k-grid — same block, not per-exercise NV |
| Layer 2 | Within-exercise subsample spread; firewalled |

### Implementation logic (v6)

```
# Shared module: src/gaga_jcvpca/nv_profile.py

for participant in [671, 252, 651, 790]:
  for timepoint in [T1, T2, T3]:
    for exercise in [ex09..ex13]:
      nv_signed[link] = JcvPCA(T{k}_R1 vs T{k}_R2 on exercise)   # both directions
    nv_ref[link] = JcvPCA(T{k}_R1 vs T{k}_R2 on ex09_13)

  for comparison in [T1_vs_T2, T1_vs_T3]:
    long_single[link]     = JcvPCA(T1_R1 vs T{k}_R1 on ex09_13)   # signed, single-rep — A2 estimand
    long_single_rev[link] = JcvPCA(T1_R2 vs T{k}_R1 on ex09_13)   # anchor swapped — direction-stability probe
    tier[link] = classify(S0..S3 from nv_ref, long_single, long_single_rev)  # S2 needs reference-direction stability
    for exercise in [ex09..ex13]:
      long_k[link] = JcvPCA(T1_R1 vs T{k}_R1 on exercise k)
      stratum_k[link] = classify using nv from exercise k at T1

  coverage gate on every comparison
  emit NV_EVIDENCE.csv, NV_PROFILE.csv, link_exercise_*.csv, nv_observed.csv

# Layer 2 optional (firewalled):
for each exercise segment in each rep:
  block-resample → subsample spread per link (signed)
```

**Scripts:** `scripts/observed_nv.py` (v6 refactor), `scripts/subsample_stability.py` (Layer 2), `src/gaga_jcvpca/nv_profile.py` (new), `src/gaga_jcvpca/validation.py` (signed baseline).

### Decision junction (8h)

| Outcome | Action |
|---|---|
| Pooled S2 + stratum S2 on ≥K exercises | Strongest descriptive profile for link |
| Pooled S2 only | A2 OK; note exercise heterogeneity if stratum mixed |
| Stratum S2 but pooled S0 | Report exercise-local only; do not lift to block claim |
| LOO dominance flag | Caveat aggregate NV reads only |

**Post-step:** offer digest append — S0/S1/S2/S3 counts, stratum table, link-level protocol openness (no cross-link means).

---

# Step 8v6 — Signed NV implementation roadmap

> **Status:** **implemented 2026-07-18** against **provisional Phase-0 defaults** (supervisor confirm pending). Phases 0–3 + Steps 6/7/9 done; Phase 4–5 downstream partial. Detail mirror: `docs/SIGNED_NV_PROFILE_PLAN.md`.

### Phase 0 — Spec lock (~1 h, supervisor) — **provisional defaults adopted**

- [x] Adopt **S2** as A2 gate (vs legacy abs > 1) — *provisional*
- [x] **Confirm A2 estimand = single-rep** `long_signed_single` (`T1_R1 vs T{k}_R1`), not pooled
- [x] **Lock sign-consistency = reference-direction stability** (`sign(long_signed_single) == sign(long_signed_single_rev)`)
- [x] **Lock signed per-link aggregation** = EVR-weighted signed sum across retained PCs (fallback: plain signed sum)
- [x] Decide: **S1** reported-not-counted; **S3** stratum K = 2 — *provisional*
- [x] Set `ε_sign` = `1e-6`; abs columns retained one release
- [x] Fill `SUPERVISOR_NV_DECISION.md` (provisional; sign-off pending)

### Phase 1 — Core module (~2 h) — **done**

- [x] Add `src/gaga_jcvpca/nv_profile.py` (`compute_link_nv_metrics`, `classify_nv_profile_tier`, `elevate_to_s3`)
- [x] Add `tests/test_nv_profile.py` (S0/S1/S2/S3, reference-direction stability, EVR-weighted signed aggregation preserves sign, ε_sign unstable floor)
- [x] Update `tests/test_validation.py` (signed tier emission)

### Phase 2 — Validation layer (~1 h) — **done**

- [x] Refactor `validation.natural_variability_baseline` → signed + tier (backward-compatible; `longitudinal_reverse` opt-in)
- [x] Extend metrics: `nv_profile_signed`/`nv_profile_tier` (kept `effect_ratio_vs_nv` as abs secondary)
- [ ] Re-run Step 4 validation for 4 participants if pipeline emits validation (optional parallel)

### Phase 3 — Step 8h script (~3 h) — **done**

- [x] Refactor `scripts/observed_nv.py`: signed evidence, per-exercise longitudinal, S3 evidence stack
- [x] Emit `NV_PROFILE.csv`, `link_exercise_nv.csv`, `link_exercise_longitudinal.csv` (+ re-run 4 pids)
- [~] `exercise_level_nv.csv` cross-link means retained (deprecated); `link_exercise_nv.csv` is the no-cross-link-mean replacement
- [ ] Regenerate `EXERCISE_PROTOCOL_OPENNESS.md` from link-level tables (still uses abs; unchanged)

```bash
PYTHONPATH=src .venv/bin/python scripts/observed_nv.py
```

### Phase 4 — Downstream (~2 h)

- [ ] `scripts/compute_amplitude_covariate.py` → join `exceeds_signed_consistent`
- [ ] `scripts/build_avatar_tables_671_252.py` (if committee path needs it)
- [ ] `ui/app.py` display signed columns (optional)

### Phase 5 — Framework docs (~2 h)

- [ ] `CLAIMS.md` — A2 = S2; S1 explicit
- [ ] `EXPERIMENTAL_DESIGN.md` — same-movement rule; no cross-link NV means
- [ ] `LIMITS.md` — paper mapping; forbidden imputation; Layer 2 scope
- [ ] `METRICS_DIGEST.md` — v6 diff table abs vs S2

### Phase 6 — Layer 2 optional (~3 h, after Phase 3)

- [ ] Implement `scripts/subsample_stability.py` (within-exercise blocks)
- [ ] Emit `subsample_spread.csv`; wire `layer2_spread_flag` in `NV_PROFILE.csv`

### Phase 7 — Step 8i methods note (deferred)

- [ ] `scripts/nv_injection_calibration.py` — calibrate **rule**, not participant inference

### Phase 8 — Committee downstream (after NV stable)

- [ ] Step 6 underused-at-T1 (use S2 links)
- [ ] Step 7 distribution metrics
- [ ] Step 9 T2/T3 persistence
- [ ] Step 10 `FINDINGS_SUMMARY.csv` + `INTERPRETATION.md`
- [ ] Step 11 committee brief + supervisor one-pager

### Acceptance criteria

1. Every A2 decision traceable to signed `nv_signed_t1` + `long_signed_single` on same link, same window, same T1 basis.
2. No committee NV metric averages across links; per-link signed value never uses mean-\|Δ\| (sign preserved via EVR-weighted signed sum).
3. S2 requires reference-direction stability (`sign(long_signed_single) == sign(long_signed_single_rev)`).
4. Per-exercise stratum uses matched long/NV on **same exercise only**.
5. LOO/ex11_13 never labeled as confirming pooled A2.
6. Committee text pairs each S2 with its coverage band (reweighting-within-subspace qualifier) and shows the single-rep signed effect, not only the pooled headline.
7. Tests green; four participants regenerated.

### Commands (post-implementation)

```bash
pytest tests/test_nv_profile.py tests/test_validation.py -q
PYTHONPATH=src .venv/bin/python scripts/observed_nv.py
PYTHONPATH=src .venv/bin/python scripts/compute_amplitude_covariate.py
# optional:
PYTHONPATH=src .venv/bin/python scripts/subsample_stability.py
```

---

# STEP 8i — NV injection calibration (DEFERRED to methods note — Tier 3)

> **Deferred (v5).** Not committee-critical and **not in the MVP**. Adds no committee-facing conclusion beyond the coverage gate + k-grid + Layer-2 robustness. Run **only** for the methods note (Step 12b), if at all. Validates the **NV rule**, not participant effects.  
> Complements Step 12b synthetic validation; focused on NV-rule behavior.

### Purpose

With only one real R1↔R2 pair per timepoint, injection tests whether the NV machinery is **calibrated** under known null and signal conditions — not whether real participants show statistical significance.

### Method (semi-synthetic)

**Base:** real `T1_R1` matrix sliced to `ex09_13` (preserves coordination structure).

**Synthetic R2 variants** (many draws, e.g. 500–1000):

| Variant | Construction | Tests |
|---|---|---|
| **Null** | R2 = R1 + block-correlated rotvec noise (sweep amplitude σ) | False-positive rate of exceed_nv |
| **Signal** | R2 = R1 + injected link-specific perturbation (known Δ) | Detection when signal > NV floor |

Repeat for aggregation levels: singles ex11–13, ex11_13 aggregate, full ex09_13.

Report:

- Null: distribution of \|ΔJcvPCA\| vs empirical real T1 R1↔R2 NV
- Signal: does Tier A flag exceed when injected Δ > empirical NV?
- Does ex11_13 aggregate NV behave more stably than singles under **same** injection?

### What it means / does not mean

**Valid:** “Under controlled null perturbations anchored to real T1 structure, empirical NV magnitudes are [consistent with / larger than] the injected null — supporting descriptive use of the NV floor.”

**Not valid:** “NV is statistically significant” for real participants; using injection p95 as committee threshold on real data.

### Deliverable

- `results_committee_case/step08_nv_and_stability/nv_injection_calibration.csv`
- `results_committee_case/step08_nv_and_stability/NV_INJECTION_CALIBRATION.md`

Script (backlog): `scripts/nv_injection_calibration.py` (or extend `tests_or_examples/synthetic_jcvpca_validation/`)

### Decision junction

Run after Step 8h MVP if methods-note or supervisor review needs calibration evidence. **Does not change** Tier A unless explicitly adopted in `SUPERVISOR_NV_DECISION.md`.

---

# STEP 9 — T2 vs T3 persistence check

### Scope
Descriptive retention: did contribution shift **persist** at later timepoint?

### Method
For each link/region in primary runs:
- Compare sign(direction) of JcvPCA at T1→T2 vs T1→T3
- Compare exceeds_nv at both
- Flag **consistent** vs **T2-only** vs **T3-only**

### Deliverable
- `results_committee_case/step09_persistence_t2_t3/consistency_table.csv`
- Summary: “consistent across timepoints: True/False” (per participant)

### Supporting
- Step 4 primary runs

### Implementation logic
Merge T1 vs T2 and T1 vs T3 link tables on link_id; boolean flags.

### Decision junction
- **Consistent:** stronger committee story
- **Inconsistent:** report both; avoid learning/retention language; note improvisation

**Post-step:** offer digest append — T2 vs T3 sign agreement, persistence flags per link.

---

# STEP 10 — Interpretation package and master findings table

### Scope
Synthesize Steps 1–9 into one auditable evidence table and narrative skeleton for supervisors.

### Method
1. Build `FINDINGS_SUMMARY.csv` — one row per participant × comparison (671, 252, 651, 790):
   - n_links, n_exceed_observed_variability (matched ratio > 1), coverage_band summary, robustness label (stable/partial/unstable), trunk_included, comparability_class breakdown
   - **NV / protocol:** `nv_ex09_t1`, `nv_ex13_t1`, `nv_ex13_over_ex09_t1`, same at T2/T3, `exercise_nv_rank_t1`, `dominant_exercise_flag`
   - **PC bands:** `p_functional_50`, `p_functional_60`, `evr_pc1_pc2`
   - **Rep diagnostics:** `pooled_vs_R1_overlap`, `pooled_vs_R2_overlap`, `longitudinal_R1_vs_R2_overlap`, `pooled_vs_R1_overlap_p50`, `pooled_vs_R1_overlap_p60`
2. **Migrate** validated tables from `METRICS_DIGEST.md` into `FINDINGS_SUMMARY.csv` (digest stays as narrative companion).
3. Write **`RUN_OUTPUT_SPEC.md`** — tier A/B/C outputs per participant run (scaling template; documents what is committee-critical vs diagnostic vs optional)
4. Write `INTERPRETATION.md`:
   - Tier findings per Step 0 — **pending supervisor NV decision** until `SUPERVISOR_NV_DECISION.md` filled
   - Explicit “not supported” list
5. Select **final figures** for brief (heatmaps per participant where available)
6. **Regenerate avatar communication layer** from Step 4 `ex09_13_contiguous` pooled runs:
   - Rebuild `avater_671_252/tables/` (extend to 651/790 when renders exist) from Step 4 outputs
   - Regenerate signed_nv heatmaps on **`ex09_13`** window (replace legacy `ex10_15` tables)
7. Final config summary (not exploration decision_log winners)

### Deliverable
- `results_committee_case/FINDINGS_SUMMARY.csv`
- `results_committee_case/RUN_OUTPUT_SPEC.md`
- `results_committee_case/step10_interpretation_package/INTERPRETATION.md`
- `results_committee_case/figures/` (final PNGs)
- `results_committee_case/step10_interpretation_package/FINAL_DECISION_SUMMARY.md`
- Updated avatar renders (if applicable) under `avater_671_252/renders/signed_nv/` or `results_committee_case/figures/`

### Supporting
- All prior steps

### Decision junction
**Ready for Step 11 when:** every interpretive claim traceable to a row in FINDINGS_SUMMARY with metric + coverage band + limit note.

**Post-step:** offer digest append — final cross-cutting conclusions; traceability map (digest section → FINDINGS_SUMMARY row).

---

# STEP 11 — Committee and supervisor deliverables

### Scope
Human-readable outputs for supervisors (first) and committee slides (second).

### Method
**11a. `docs/COMMITTEE_BRIEF.md`** (2–3 pages)
- Problem + Gaga hypothesis (Step 0 phrasing)
- Method summary (pipeline, jcvPCA, NV, feature stream choice)
- Results (**four participants**, within-N-of-1 framing) with observed-NV / coverage / robustness labels per supervisor decision
- Trunk + ROM + underused + distribution findings
- Limits + trajectory

**11b. `docs/SUPERVISOR_ONE_PAGER.md`**
- 5 bullets + 2 figures + 1 ask for feedback

**11c. Slide outline** (`docs/COMMITTEE_SLIDES_OUTLINE.md`) — 10–12 slides; build deck after supervisor feedback

**11d. Committee narrative drill-down** (`docs/COMMITTEE_NARRATIVE.md`) — structured story from chat:
- A. Problem → B. Scientific framing (modest) → C. What is done → D. What we conclude **now** → E. What we cannot conclude → F. Trajectory → G. One-sentence thesis

**11e. Backup slides list:** timing/JsvCRP deferred; trunk anatomy; 671 T3 confound; rotvec ≠ joint angle; instruction vs learning limit

### Deliverable
- Four docs above (+ narrative)
- Email-ready supervisor package linking to `results_committee_case/`

### Supporting
- Step 10 complete

### Decision junction
Send to supervisors → incorporate feedback → then build slides (Week 2 activity, not blocked on new science).

**Post-step:** offer digest append — approved claim wording snippets (if changed from draft).

---

# STEP 12 — Publication path (Methods / Application Note)

### Scope
Parallel track for journal — **not** required before committee, but outline now so trajectory is credible.

### Method
**12a. Outline** (`docs/METHODS_NOTE_OUTLINE.md`)
- Title (working): *Reference-anchored jcvPCA for whole-body optical MoCap with natural-variability reporting for improvisational movement*
- Sections: intro gap, pipeline, jcvPCA recap, rotvec features, observed NV + reference-subspace coverage gate (Step 8h), matched single-rep ratio, worked example (`ex09_13`, one participant), limits, code availability
- Target formats: Software/Application Note; Technical Note in movement science / biomechanics methods tracks

**12b. Executable before submission** (promote from checklist to tasks when committee package done):

| Task | Method | Deliverable |
|---|---|---|
| Synthetic validation | Reproduce paper-logic or controlled redistribution synthetic | `tests_or_examples/synthetic_jcvpca_validation/` + figure |
| Naive PCA baseline | Same data: direct PC loading comparison vs reference-anchored jcvPCA | `results_methods_note/naive_vs_jcvpca_comparison.md` |
| Worked example bundle | One command reruns primary case; manifest + config snapshot | `examples/committee_worked_example/` |
| Feature-stream appendix | Document Step 2 outcome (rotvec default; BVH evaluated) | subsection in methods note |
| Limitations box | No timing, no causality, NV descriptive, rotvec features | boxed text in manuscript |

**12c. Gaga findings paper** — defer until methods note accepted + more N + stronger NV

### Deliverable
- `docs/METHODS_NOTE_OUTLINE.md`
- Checklist in outline with completion status
- (Later) `results_methods_note/` folder when 12b tasks execute

### Supporting
- Step 4 worked run as example
- Step 8h empirical NV feasibility (if run)
- Step 2-FS feature pilot (document rotvec choice)
- Golden tests (existing)

### Decision junction
Submit methods note **before** empirical Gaga efficacy paper.

---

# STEP 13 — Deferred (merged into Step 4 in v4)

651 and 790 are **required** primary participants in Step 4, not a post-hoc spot-check. This step is retired; see Step 4 and Step 2 link mapping.

---

# STEP 14 — Deferred (explicitly out of this plan)

| Item | When | Why deferred |
|---|---|---|
| JsvCRP / phase | Later stage | Improv alignment; not needed for contribution claims |
| RQA | Later stage | User preference; more robust dynamics |
| S2 ISB pipeline pilot | If BVH fails | Second feature candidate |
| Weighted JcvPCA (EVR weighting) | Optional sensitivity | Paper optional step; config flag exists |
| Permutation tests | Deferred | Underpowered at current N |
| Subjective bodily access / effort scales | Future protocol | Not in current data |
| Smoothness / jerk metrics | Future | Amplitude-adjacent; not needed for v1 |
| Cross-participant inference | After N↑ | N-of-1 now |
| Full Euler production default | Only if Step 2 promotes S1 | Evidence-based |

---

# Execution order (dependency graph)

```
Step 0 (claims + naming)
  ↓
Step 1 (baseline ex09_13)
  ↓
Step 2 (skeleton baselines + canonical link map) ──┐
  ↓                                                │
Step 3 (trunk + inclusive QC + convert 4 pids)    │
  ↓                                                │
Step 4 (primary ex09_13 pooled, 4 participants) ←─┘
  ↓
Step 4b (one merged robustness table — PC count k-grid, repetition mode, QC drop)
  ↓
Steps 5,6,7,8,9 (parallelizable post-hoc)
  ↓
Step 8h.0 coverage gate → Layer 1 observed NV (signed; per-exercise matched strata)
  ↓
Step 8v6 signed NV profile (S0–S3) + NV_EVIDENCE v2 + NV_PROFILE.csv
  ↓
SUPERVISOR_NV_DECISION (wording gate)
  ↓
[optional] Step 8h Layer 2 (within-exercise subsample spread, firewalled) · Step 8i injection (methods note)
  ↓
Step 10 (synthesis + avatars ex09_13)
  ↓
Step 11 (supervisor + committee docs)
  ↓
Step 12 (methods note — parallel/longer horizon)
```

**Parallelizable after Step 4:** Steps 5, 6, 7, 8, 9 can run in any order or concurrently.

**Step 2-FS (BVH pilot)** can run in parallel with Steps 1–3 if needed — but Step 4 does not wait for BVH; rotvec is primary.

---

# Master checklist (definition of done)

- [ ] **`METRICS_DIGEST.md`** maintained — post-step review after each step (code + chat → offered append)
- [ ] Step 0: CLAIMS.md + LIMITS.md + NAMING.md (`P1` = task part; `ex{NN}` only)
- [ ] Step 1: baseline snapshot (`ex09_13` exploration + 4-pid readiness)
- [ ] Step 2: canonical link map + skeleton baselines + comparability matrix
- [ ] Step 2-FS: BVH pilot scorecard (Tier 3 / optional)
- [ ] Step 3: trunk + full feasible links + inclusive QC + convert all 4 pids
- [ ] Step 4: primary runs `ex09_13_contiguous` pooled (671, 252, 651, 790)
- [ ] Step 4b: robustness table + **repetition diagnostics (R2, R1↔R2, p50/p60 bands)** + **`functional_pc_bands.csv`**
- [ ] Step 5: ROM/RMS covariate
- [ ] Step 6: underused-at-T1 analysis (+ secondary-PC band check)
- [ ] Step 7: distribution metrics
- [ ] Step 8 MVP: coverage + abs-only Layer 1 (`step08_nv_and_stability/`) — **done**
- [ ] **Step 8v6:** signed NV profile (`nv_profile.py`, `NV_PROFILE.csv`, S2 A2 gate, link_exercise_* CSVs, framework doc updates, re-run 4 pids)
- [ ] Step 8h Layer 2: within-exercise subsample spread (optional; firewalled)
- [ ] Step 8i: NV injection calibration (**deferred to methods note / Tier 3**)
- [ ] Step 9: T2/T3 persistence
- [ ] Step 10: FINDINGS_SUMMARY.csv + **RUN_OUTPUT_SPEC.md** + INTERPRETATION.md + avatar regen (`ex09_13`)
- [ ] Step 11: COMMITTEE_BRIEF + SUPERVISOR_ONE_PAGER + COMMITTEE_NARRATIVE
- [ ] Step 12: METHODS_NOTE_OUTLINE (draft)
- [ ] Code/config: remove `gaga_group4_aliases` from `exercise_map.yaml`, `naming.py`, UI, tests

---

# Appendix A — Chat coverage matrix

| Conversation topic | Plan step(s) | Notes |
|---|---|---|
| Paper jcvPCA core + adaptations | 0, 4, 8 | Sacred core unchanged |
| NV mismatch (2 reps vs paper splits) | 8, 8h, 8v6 | Layer 1 genuine reps; Layer 2 within-exercise spread; no imputation floor |
| Signed NV profile / no cross-link means | 8v6 | S0–S3 tiers; A2 = S2; per-exercise stratum = same movement only |
| Same-movement / estimand lock | 8v6 | LOO/ex11_13 diagnostic only; pooled A2 on ex09_13 only |
| selected_m / functional-secondary / k-sensitivity | 4b, 8, 8h | k-grid primary; 80% EVR for `selected_m`; **p_functional_50/60** for labeling; legacy p=2 retained |
| PC-count & ranking stability | 4b | Heuristic labels (top-5 + functional-chain); **+ R2 / R1↔R2 diagnostics**; not p-values |
| Observed NV (per-exercise ex09–ex13 × T1/T2/T3 + ex11_13 secondary + LOO) | 8h | Layer 1; ex09_13 reference; matched single-rep ratio; **exercise protocol openness** |
| Per-exercise improvisation openness (ex13 vs ex09) | 8h, 10 | Descriptive NV ratios; **not** skill claims; ROM cross-check Step 5 |
| RUN_OUTPUT_SPEC / FINDINGS_SUMMARY scaling columns | 10 | Tiered outputs per participant |
| Living metrics rollup (`METRICS_DIGEST.md`) | all steps | Post-step review: code + chat → offered append; migrate to FINDINGS_SUMMARY at Step 10 |
| Reference-subspace coverage gate | 8, 8h.0 | Validity gate; absorbs former 8g reprojection sanity |
| Two-layer NV / firewall + no bootstrap floor | 8, 8h | Layer 2 descriptive only; Tiers B/C/D removed |
| NV injection calibration | 8i, 12b | **Deferred** to methods note; not participant significance |
| Rotvec vs joint angles | 2-FS, 0 LIMITS | BVH pilot Tier 3; default rotvec |
| JsvCRP deferred | 14 | Explicitly out |
| RQA later | 14 | Explicitly out |
| Amplitude vs organization | 5 | ROM/RMS covariate |
| Underused at T1 / dormant motors phrasing | 0, 6 | Careful interpretive claim only |
| Contribution distribution / dominance | 7 | Entropy, top-1 share |
| Trunk/pelvis missing from analysis | 2, 3 | Canonical map + inclusive QC |
| Gaga 7-question assessment | 0,5–9,11 | Timing/learning gaps documented |
| Publication as Methods Note | 12 | Findings paper deferred |
| Naive PCA baseline | 12b | Pre-submission task |
| Synthetic validation | 12b | Pre-submission task |
| BVH feature pilot | 2-FS | Tier 3 optional |
| ISB pipeline optional | 2-FS, 14 | S2 if BVH fails |
| 671 T3 marker-set confound | 1, 2, 8, 11e | Shared links + downgrade |
| Pooled vs single repetitions | 4, 4b | Pooled primary; single = sensitivity #1 |
| Avatar heatmaps | 10 | `ex09_13_contiguous` primary |
| Committee storytelling | 11, 11d | COMMITTEE_NARRATIVE.md |
| Instruction vs learning | 0 EXPERIMENTAL_DESIGN | Cannot separate — documented |
| Blinded / no causal drug language | 0 LIMITS | Explicit |
| Four participants 671/252/651/790 | 2, 3, 4 | Required in Step 4 |
| Sensitivity exclude flagged links (QC-drop) | 4b | Merged robustness table |
| Null-space exploratory | 8 | Soft claim only |
| Reprojection / radical strategy warning | 8, 8h.0 | Reference-subspace coverage gate |
| Protocol window ex09–ex13 | 1, 4, 10 | Primary; old winners dropped |
| Robustness framework (not alt windows) | 4b | k-grid, repetition-mode, QC-drop (one table) |
| Matched single-rep exceed-floor ratio | 8, 8h | Single-rep ÷ single-rep; pooled not divided |
| Autocorrelation / effective units | 8h L2 | Units = reps × exercises, never frames |
| Canonical link map + 2 skeleton setups | 2 | Comparability flags |
| Naming: P1 = task part; ex{NN} exercises | 0 | Remove gaga_group4_aliases |
| Improvisation / unrepeated movement | 0, 8, 8h | jcvPCA OK; NV = repetition variability not noise |

---

# Appendix B — Scripts / artifacts to create (implementation backlog)

| Artifact | Step | Purpose |
|---|---|---|
| `configs/canonical_link_map.csv` | 2 | Participant-neutral links + comparability flags |
| `scripts/audit_skeleton_baselines.py` (or extend feature_manifest_gen) | 2 | Two setup classification + overlap matrix |
| `scripts/run_feature_pilot.py` | 2-FS | BVH intake → matrices → scorecard |
| `scripts/compute_amplitude_covariate.py` | 5 | ROM/RMS join to link tables |
| `scripts/subspace_coverage.py` | 8 / 8h.0 | Reference-subspace coverage gate (abs + vs B's own ceiling) |
| `src/gaga_jcvpca/nv_profile.py` | 8v6 | Signed tiers S0–S3; direction consistency; shared validation + Step 8 |
| `scripts/observed_nv.py` | 8h / 8v6 | Layer 1 + coverage + signed NV_PROFILE + link_exercise CSVs |
| `scripts/run_step04b_robustness.py` | 4b | Extend: pooled vs R2, longitudinal R1↔R2, `functional_pc_bands.csv` |
| `scripts/subsample_stability.py` | 8h L2 | **Optional** fixed-`m` contiguous block resampling + autocorrelation read (firewalled) |
| `scripts/nv_injection_calibration.py` | 8i | **Deferred** (methods note) semi-synthetic NV-rule calibration |
| `scripts/robustness_table.py` (or extend pipeline) | 4b | Merged k-grid + repetition-mode + QC-drop → `robustness.csv` |
| ~~`scripts/bootstrap_nv_blocks.py`~~ | — | **Removed (v5):** bootstrap NV floor / CI dropped from claim machinery |
| ~~`scripts/empirical_nv_pilot.py`~~ / ~~`scripts/k_sensitivity.py`~~ | — | **Superseded** by `observed_nv.py` / `robustness_table.py` |
| BVH parser / Euler extractor | 2-FS | Feature matrix from BVH |
| Full feasible manifests (trunk included) | 3 | Per-participant from canonical map |
| Remove `gaga_group4_aliases` | 0 | `exercise_map.yaml`, `naming.py`, UI, tests |

---

# BVH intake — what to provide (Step 2-FS blocker list)

Place or document in `results_committee_case/step02_feature_pilot/intake/`:

1. `BVH_PATHS.md` — full paths, naming convention, which session each file maps to
2. `CHANNEL_DICTIONARY.csv` — BVH joint name → canonical link/DOF, Euler order, units
3. `ALIGNMENT_TEST.md` — one worked example: file frame count vs Motive frame slice for **`ex09_13`**
4. Optional: pre-exported tidy CSV per session (faster than parsing BVH in-pipeline)

Once intake is complete, Step 2-FS QC and scorecard can run.
