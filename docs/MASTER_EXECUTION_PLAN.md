# Master execution plan — committee case study, feature pilot, and publish path

**Status:** active plan (v2 — gap patch after full chat review)  
**Purpose:** Complete step-by-step roadmap for everything agreed in project review (jcvPCA, Gaga framing, trunk gap, BVH pilot, NV, committee wrap, methods publication).  
**Not day-scheduled** — execute in order; each step lists prerequisites and decision gates.

**Coverage note:** See [Appendix A — Chat coverage matrix](#appendix-a--chat-coverage-matrix) at end of this document for mapping from conversation topics → steps.

**Primary audiences:**
- Supervisors (written case study package)
- PhD committee (slides built from that package)
- Future journal submission (Methods/Application Note first)

---

## Mission (one paragraph)

Deliver a **rigorous, modest, evidence-backed case study** showing that reference-anchored jcvPCA on whole-body MoCap can quantify **redistribution of link contribution** to shared movement-variance structure before vs after the intervention period — framed as a **conservative proxy** for Gaga-inspired “broader access to underused degrees of freedom,” **without** claiming dormant motors, timing change, causality, or population effects. Close methodological gaps (trunk under-selection, amplitude vs organization, weak NV, feature-stream choice with BVH now available), then package for supervisors and committee.

---

## Global constraints (never violate)

| Rule | Rationale |
|---|---|
| Sacred jcvPCA core unchanged | `compute_jcvpca`, RSS aggregation, golden tests |
| T1 always reference A | Paper-faithful |
| NV = T1 R1 vs R2 only | Descriptive floor; never pooled |
| Within-participant only | N-of-1; no cohort inference |
| No JsvCRP / phase / RQA in this plan | Improv alignment risk; deferred |
| Claim language conservative | See Step 0 |

---

## Tiered execution — critical path first (v3)

The 14 steps below are the **full** spec. For the committee sprint, execute by tier. Do **not** run Tier 3 before Tier 1 is done.

### Tier 1 — Committee-critical (must do; nothing honest can be presented without these)
Ordered critical path:

```
0 Claims → 1 Baseline → 3 Trunk → 4 Primary runs → 5 Amplitude-vs-organization
  → 8 (cheap parts: threshold sweep + PCA stability + NV honesty) → 10 Synthesis → 11 Committee docs
```

- **Step 0** — claims/limits (½ day)
- **Step 1** — baseline snapshot of existing winners (½ day)
- **Step 3** — trunk links `Root→Ab`, `Ab→Chest`, QC-gated (the real scientific gap)
- **Step 4** — primary runs on final link set (fold Step 4b re-ranking in here)
- **Step 5** — ROM/RMS covariate (answers "isn't this just bigger movement?")
- **Step 8 (cheap only)** — threshold sweep + PCA stability + honest NV language
- **Step 10 / 11** — synthesis + brief/one-pager/narrative

### Tier 2 — Cheap, high-value (pure post-hoc on CSVs you already produce; add if Tier 1 done)
- **Step 6** — underused-at-T1 links (directly supports the hypothesis)
- **Step 7** — contribution distribution (entropy / top-1 share)
- **Step 9** — T2 vs T3 persistence
- **Step 8a** — block bootstrap **only if** window length gives ≥4 blocks; otherwise write `INSUFFICIENT.md` and move on (do not over-invest)

### Tier 3 — Defer / optional (NOT before committee)
- **Step 2** — BVH feature pilot → **moved off critical path.** Rotvec is already the decided primary. For committee: one *future-direction* slide ("BVH/Euler interpretability track, protocol ready"). Run the full pilot only post-committee or if Tier 1+2 finish early.
- **Step 4b** — standalone window revalidation → fold into Step 4 unless trunk clearly changes the winner
- **Step 12b** — methods-note validation tasks (synthetic, naive-PCA baseline) → parallel/after
- **Step 13** — 651/790 scalability spot-check → optional
- **Step 14** — JsvCRP / RQA / EMG → out of scope

**Efficiency rule:** if a step's likely output is "insufficient / inconclusive at current N," spend minutes documenting that honestly, not hours forcing it. Honesty about limits *is* the rigorous result.

---

## Output folder layout

```
results_committee_case/
  step00_claim_framework/
  step01_baseline_audit/
  step02_feature_pilot/          # rotvec vs BVH
  step03_trunk_extension/
  step04_primary_runs/
  step05_amplitude_vs_organization/
  step06_underused_at_t1/
  step07_contribution_distribution/
  step08_nv_and_stability/
  step09_persistence_t2_t3/
  step10_interpretation_package/
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
- Improvisational movement → high within-condition variability; NV floor is **descriptive** with 2 repetitions.
- Blinded timepoint labels: report **contribution-structure differences across timepoints** without drug/causal language until unblinding protocol allows.

**Gaga bridge phrase (use verbatim style):**
> *Gaga practice motivates the hypothesis of broader functional access to underused movement degrees of freedom. We operationalize this as change in the relative contribution of body links to whole-body movement-variance structure, measured by reference-anchored jcvPCA.*

### Deliverable
- `results_committee_case/step00_claim_framework/CLAIMS.md`
- `results_committee_case/step00_claim_framework/LIMITS.md`
- `results_committee_case/step00_claim_framework/EXPERIMENTAL_DESIGN.md` — what T1/T2/T3 and R1/R2 **mean in the study protocol**; explicit note that instruction vs lasting learning **cannot** be separated with current design (feeds committee Q&A)

### Supporting
- Paper review (Dubois et al. 2025)
- `docs/MASTER_PLAN.md` §14 limitations
- Chat consensus on no JsvCRP

### Implementation logic
All later steps write results into tables that map to **claim tier**:
- Tier A: descriptive fact (metric value)
- Tier B: exceeds NV floor
- Tier C: interpretive (consistent with hypothesis) — requires Tier A + B + amplitude check

### Decision junction
**Proceed when:** supervisors agree claim scope is acceptable (or you accept proceeding with documented limits for committee).

**Stop if:** stakeholders require causal or timing claims — those need different methods (out of scope).

---

# STEP 1 — Baseline audit and case-study lock

### Scope
Freeze **what exists today** before any new runs. Establish the “before” state for trunk, BVH, and write-up comparisons.

### Method
1. Copy exploration winners and supporting artifacts:
   - 671: `ex11_single` pooled
   - 252: `ex10_14_contiguous` pooled
2. Collect per winner: `link_level_results.csv`, `region_level_results.csv`, `functional/null_space_results.csv`, `natural_variability_results.csv`, `validation_results.csv`, `selected_m_by_comparison.csv`, `run_summary.md`, `reproducibility_manifest.json`.
3. Copy avatar heatmaps from `avater_671_252/renders/signed_nv/`.
4. Document known confounds: 671 T3 marker-set prefix; 252-only hip roots; no trunk_spine in current selections.
5. Write two paragraphs: **“What we can conclude now”** / **“What we cannot yet.”**

### Deliverable
- `results_committee_case/step01_baseline_audit/` (full snapshot)
- `BASELINE_SUMMARY.md` (2 pages max)
- `KNOWN_CONFOUNDS.md`

### Supporting
- `results_exploration_671_252/decision_log.md`
- `results_exploration_671_252/runs/{671,252}/...`
- `avater_671_252/assumptions.md`

### Implementation logic
No code changes. Pure inventory so every later delta is auditable (“trunk added → NV count went from X to Y”).

### Decision junction
**Proceed when:** baseline folders exist and winner windows confirmed still best (or note if re-ranking needed after trunk).

**Re-evaluate winners if:** after Step 3–4 a different window clearly dominates — rare; document if it happens.

---

# STEP 2 — Feature-stream pilot: rotvec (S0) vs BVH Euler (S1)

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
- Participants: 671, 252
- Windows: primary winners (+ optional secondary from decision_log top-5)
- T1 reference; T1 vs T2, T1 vs T3; NV = T1 R1 vs R2
- Pooled longitudinal + single sensitivity
- `variance_threshold=0.80`; sweep 0.70/0.80/0.90

**S1 intake (must complete before jcvPCA):**
1. Inventory BVH files: session coverage T1/T2/T3 × R1/R2 per participant.
2. Document Euler order, units (rad/deg), local vs global, joint naming map → canonical link names.
3. **Alignment test:** slice one exercise window; compare frame count to rotvec matrix (±0 ideal; ≤2 documented).
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

---

# STEP 3 — Trunk link extension (Root→Ab, Ab→Chest)

### Scope
Fix the anatomical gap: raw skeleton **has** pelvis/abdomen/chest bones; current 14/16-link manifests **exclude** trunk intermediaries → `trunk_spine` region empty. Required for any center→periphery Gaga narrative.

### Method
1. **Confirm hierarchy** from DataDescriptions (already verified: `671` root → `Ab` → `Chest` → `Neck`/shoulders; thighs attach to root).
2. **Add links to manifests** (participant-specific naming):
   - 671: `671_to_Ab`, `Ab_to_Chest` (or canonical equivalents from raw column names)
   - 252: `252_to_Ab`, `Ab_to_Chest` (+ keep `252_to_LThigh/RThigh` as 252-only, non-cohort-comparable)
3. **QC each new link** on T1/T3: finite rotvecs, jump rate, variance > epsilon.
4. Update `configs/body_regions.yaml` `trunk_spine` matchers if needed (`Ab`, `Hip_to`, root→child patterns).
5. Create selection YAML variant: `{pid}_{window}_with_trunk.yaml`.

### Deliverable
- Updated `data/feature_manifests/group4_core_*_with_trunk.csv` (or extended manifests)
- `results_committee_case/step03_trunk_extension/TRUNK_QC.md`
- `results_committee_case/step03_trunk_extension/LINK_INVENTORY.md` (included/excluded + reason)

### Supporting
- Step 1 baseline (without trunk)
- Raw skeleton + DataDescriptions
- `configs/body_regions.yaml`
- Chosen feature stream from Step 2 (rotvec default)

### Implementation logic
```
DataDescriptions hierarchy → identify parent-child bone pairs
→ add *_rx/_ry/_rz to feature manifest
→ run_convert / matrix columns must exist or rotvec pipeline must compute them
→ QC flags per link → include or exclude with reason
```
If rotvec columns don't exist yet for new links, re-run `run_convert.py` for affected sessions before Step 4.

### Decision junction
| Outcome | Action |
|---|---|
| Trunk links pass QC | Step 4 runs **with_trunk** as primary case study config |
| Trunk links fail QC | Document failure; committee claims stay limb-focused; note as limitation |
| 671 T3 trunk unstable | Restrict T1–T3 trunk claims to shared stable links only |

**Do not proceed to Step 4 trunk-inclusive runs until:** manifest + convert verified for at least one T1 session per participant.

---

# STEP 4 — Primary jcvPCA case study runs (final config)

### Scope
Produce the **authoritative** jcvPCA results that feed committee brief, figures, and later methods note worked example.

### Method
Re-run (or confirm fresh) for both participants, winning windows, **final feature set** (post Step 2–3):

| Participant | Window | Mode | Comparisons |
|---|---|---|---|
| 671 | ex11_single | pooled (+ single sensitivity) | T1 vs T2, T1 vs T3, NV |
| 252 | ex10_14_contiguous | pooled (+ single sensitivity) | same |

Parameters (locked):
- `variance_threshold=0.80`
- `sensitivity_p=2` (labeling only)
- `--validate` enabled
- Same filter settings as exploration (`10 Hz`, order 4)

Run via existing `run_analysis.py` + selection YAMLs; copy outputs to `step04_primary_runs/`.

Also run **without trunk** variant if trunk added — for delta table in Step 10.

### Deliverable
- `results_committee_case/step04_primary_runs/{671,252}/{with_trunk,without_trunk}/`
- Full run folders: CSVs, manifests, validation summaries
- `PRIMARY_RUN_INDEX.md` (run_ids, git hash, config snapshot)

### Supporting
- Steps 2 (feature stream decision), 3 (trunk manifest)
- `scripts/run_analysis.py`
- Selection YAMLs under `results_exploration_671_252/selections/` (updated)

### Implementation logic
Unchanged sacred pipeline:
```
load sliced matrices → restrict shared features → compute_jcvpca(A=T1,B=T2/T3)
→ link/region/functional/null rollups → NV baseline → optional validation
```
Only inputs change (features, link set, windows).

### Decision junction
**Proceed to Steps 5–9 when:** primary runs complete without ValidationError; `selected_m` logged; at least one longitudinal comparison produces link table.

**Pause if:** no shared links between T1 and T3 for 671 — apply shared-link restriction per MASTER_PLAN decision 2; document excluded links.

---

# STEP 4b — Window re-validation (after trunk + feature stream)

> **TIER 3 — fold into Step 4 by default (v3).** Run as a standalone step only if trunk inclusion visibly changes which window wins. Otherwise a one-line confirmation in Step 4 is enough.

### Scope
Confirm exploration winners (671 ex11, 252 ex10–14) are still best **on the final feature set** — trunk links or BVH choice may change rankings.

### Method
1. Re-score primary windows + top-3 alternates from `decision_log.md` using Step 4 outputs.
2. Same scoring as exploration: `n_links_exceeding_nv`, mean effect ratio, T2/T3 consistency.
3. If a different window wins clearly → update case study focus and document why.

### Deliverable
- `results_committee_case/step04_primary_runs/WINDOW_REVALIDATION.md`

### Supporting
- Step 4 runs (with_trunk config)
- `results_exploration_671_252/decision_log.md`

### Implementation logic
Post-hoc ranking only — no new pipeline code unless window changes (then rerun Step 4 for new window).

### Decision junction
| Outcome | Action |
|---|---|
| Same winners | Proceed; cite original exploration + confirm on final config |
| New winner | Rerun Steps 5–9 for new window; update brief figures |
| Ambiguous | Report primary + alternate as sensitivity in brief |

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
| Several underused links ↑ beyond NV | “Consistent with broader participation hypothesis” (Tier C) |
| Only high-baseline links change | Do not claim underused activation |
| Mixed T2 vs T3 | Report each timepoint separately |

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

---

# STEP 8 — NV strengthening, threshold sweep, PCA stability

### Scope
Address biggest methodological weakness: single R1–R2 NV point. Give committee defensible variability language **without** JsvCRP.

### Method
**8a. Window/block bootstrap (within T1)**
- Split T1 sliced window into ≥4 contiguous blocks (if length allows; else document insufficient)
- Resample blocks; compute NV-like split comparisons or longitudinal Δ distribution
- Report: for each link, % bootstrap resamples where \|long\| > \|NV\|

**8b. Threshold sweep**
- Run `sweep_thresholds` at 0.70, 0.80, 0.90 on primary runs
- Record `selected_m`, top-5 link rank overlap

**8c. PCA stability**
- Compare T1 R1 vs R2 vs pooled loading similarity (existing `validation.pca_stability`)
- Flag comparisons as stable / warning / insufficient

**8d. Functional/null labeling**
- Keep `sensitivity_p=2` as **reporting partition only**
- Always report full `selected_m` and EVR table
- Do not over-interpret null space as “repertoire” without Step 6–7 support

**8e. Sensitivity analysis (QC-robustness)**
- Re-run jcvPCA excluding links flagged `include_with_caution` or high jump rate (existing `validation.sensitivity_analysis`)
- Report: does top-link ranking / region story survive?

**8f. Null-space exploratory read**
- Summarize links with largest \|JcvPCA\| in null space (PC > sensitivity_p)
- Label **exploratory only**: candidate redistribution in non-dominant variance modes — not “new repertoire” without Steps 6–7

**8g. Reprojection sanity (671 T3)**
- If PCA stability = warning for T1–T3: downgrade that comparison to exploratory per paper caution on radically different strategies

### Deliverable
- `results_committee_case/step08_nv_and_stability/bootstrap_summary.csv` (or INSUFFICIENT.md)
- `threshold_sensitivity.csv`
- `pca_stability_summary.md`
- `sensitivity_exclude_flagged_links.md`
- `null_space_exploratory_summary.md`
- Updated validation sentences with strength labels

### Supporting
- Step 4 runs with `--validate`
- `configs/analysis_defaults.yaml` bootstrap settings

### Implementation logic
Uses existing `validation.py` + optional new thin bootstrap-over-blocks helper if not already sufficient for single-exercise windows.

### Decision junction
| Bootstrap | Language |
|---|---|
| Sufficient + link exceeds 90% resamples | “bootstrap-supported (descriptive)” |
| Insufficient windows | “exceeds observed R1–R2 floor only” — mandatory honesty |
| PCA unstable for 671 T3 | Downgrade T1–T3 claims to exploratory for that participant |

**Committee brief must state which tier each finding uses.**

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

---

# STEP 10 — Interpretation package and master findings table

### Scope
Synthesize Steps 1–9 into one auditable evidence table and narrative skeleton for supervisors.

### Method
1. Build `FINDINGS_SUMMARY.csv` — one row per participant × config (with/without trunk) × feature stream:
   - n_links, n_exceed_nv, mean_effect_ratio, n_underused_increased, top1_share_delta, entropy_delta, bootstrap_supported_count, t2_t3_consistent, trunk_included, feature_stream, pca_stability_flag
2. Write `INTERPRETATION.md`:
   - Tier A/B/C findings per claim in Step 0
   - Explicit “not supported” list
3. Select **final figures** for brief (2 heatmaps + 1 distribution or ROM scatter)
4. **Regenerate avatar communication layer** from final primary runs:
   - Rebuild `avater_671_252/tables/` from Step 4 outputs (or copy run CSVs through existing table builder)
   - Regenerate signed_nv heatmaps + 2×2 summary if trunk/links changed
5. Update `decision_log`-style summary for committee case (final config, not exploration-only)

### Deliverable
- `results_committee_case/FINDINGS_SUMMARY.csv`
- `results_committee_case/step10_interpretation_package/INTERPRETATION.md`
- `results_committee_case/figures/` (final PNGs)
- `results_committee_case/step10_interpretation_package/FINAL_DECISION_SUMMARY.md`
- Updated avatar renders (if applicable) under `avater_671_252/renders/signed_nv/` or `results_committee_case/figures/`

### Supporting
- All prior steps

### Decision junction
**Ready for Step 11 when:** every Tier C claim traceable to a row in FINDINGS_SUMMARY with metric + limit note.

---

# STEP 11 — Committee and supervisor deliverables

### Scope
Human-readable outputs for supervisors (first) and committee slides (second).

### Method
**11a. `docs/COMMITTEE_BRIEF.md`** (2–3 pages)
- Problem + Gaga hypothesis (Step 0 phrasing)
- Method summary (pipeline, jcvPCA, NV, feature stream choice)
- Results (671, 252) with tier labels
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

---

# STEP 12 — Publication path (Methods / Application Note)

### Scope
Parallel track for journal — **not** required before committee, but outline now so trajectory is credible.

### Method
**12a. Outline** (`docs/METHODS_NOTE_OUTLINE.md`)
- Title (working): *Reference-anchored jcvPCA for whole-body optical MoCap with natural-variability reporting for improvisational movement*
- Sections: intro gap, pipeline, jcvPCA recap, rotvec features, NV, worked example (671 or 252), limits, code availability

**12b. Required before submission** (from review)
1. Synthetic / paper-logic validation (independent of golden tests)
2. Naive PCA comparison baseline on same example
3. Public or archived runnable worked example
4. Explicit “cannot claim timing” box

**12c. Gaga findings paper** — defer until methods note + more N + stronger NV

### Deliverable
- `docs/METHODS_NOTE_OUTLINE.md`
- Checklist in outline with completion status

### Supporting
- Step 4 worked run as example
- Step 2 feature pilot (document rotvec choice)
- Golden tests (existing)

### Decision junction
Submit methods note **before** empirical Gaga efficacy paper.

---

# STEP 12 — Publication path (Methods / Application Note)

### Scope
Parallel track for journal — **not** required before committee, but outline now so trajectory is credible.

### Method
**12a. Outline** (`docs/METHODS_NOTE_OUTLINE.md`)
- Title (working): *Reference-anchored jcvPCA for whole-body optical MoCap with natural-variability reporting for improvisational movement*
- Sections: intro gap, pipeline, jcvPCA recap, rotvec features, NV, worked example (671 or 252), limits, code availability
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
- Step 2 feature pilot (document rotvec choice)
- Golden tests (existing)

### Decision junction
Submit methods note **before** empirical Gaga efficacy paper.

---

# STEP 13 — Optional scalability spot-check (651 / 790)

### Scope
**Optional, not blocking committee.** Demonstrates pipeline generalizes beyond 671/252 without making population claims.

### Method
- Run Step 4 equivalent on one window for 651 or 790 if sessions exist and convert succeeds
- Report: pipeline completes, link count, one comparison table — no cross-participant statistics

### Deliverable
- `results_committee_case/step13_scalability_spotcheck/SPOTCHECK.md` (or SKIP.md with reason)

### Decision junction
Skip if time-constrained — note in committee trajectory as “in progress.”

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
Step 0 (claims)
  ↓
Step 1 (baseline) ────────────────────────────────┐
  ↓                                                │
Step 2 (BVH pilot) ──→ decision: S0/S1            │
  ↓                                                │
Step 3 (trunk) ──→ decision: include/exclude      │
  ↓                                                │
Step 4 (primary runs) ←───────────────────────────┘
  ↓
Step 4b (window re-validation)
  ↓
Steps 5,6,7,8,9 (parallelizable post-hoc analyses)
  ↓
Step 10 (synthesis)
  ↓
Step 11 (supervisor + committee docs)
  ↓
Step 12 (methods note — parallel/longer horizon)
```

**Parallelizable after Step 4:** Steps 5, 6, 7, 8, 9 can run in any order or concurrently.

**Step 2 can start immediately** (BVH available) in parallel with Step 1 if needed — but Step 4 must wait for Step 2 decision + Step 3 trunk QC.

---

# Master checklist (definition of done)

- [ ] Step 0: CLAIMS.md + LIMITS.md
- [ ] Step 1: baseline snapshot
- [ ] Step 2: BVH pilot scorecard + stream decision
- [ ] Step 3: trunk links QC + manifest
- [ ] Step 4: primary runs (with/without trunk)
- [ ] Step 4b: window re-validation on final config
- [ ] Step 5: ROM/RMS covariate
- [ ] Step 6: underused-at-T1 analysis
- [ ] Step 7: distribution metrics
- [ ] Step 8: bootstrap + threshold + PCA stability + sensitivity + null-space read
- [ ] Step 9: T2/T3 persistence
- [ ] Step 10: FINDINGS_SUMMARY.csv + INTERPRETATION.md + avatar regen
- [ ] Step 11: COMMITTEE_BRIEF + SUPERVISOR_ONE_PAGER + COMMITTEE_NARRATIVE
- [ ] Step 12: METHODS_NOTE_OUTLINE (draft)
- [ ] Step 13: scalability spot-check (optional)

---

# Appendix A — Chat coverage matrix

| Conversation topic | Plan step(s) | Notes |
|---|---|---|
| Paper jcvPCA core + adaptations | 0, 4, 8 | Sacred core unchanged |
| NV mismatch (2 reps vs paper splits) | 8a | Bootstrap; honest language |
| selected_m / functional-null | 8b, 8d | sensitivity_p=2 = label only |
| Rotvec vs joint angles | 2, 0 LIMITS | BVH pilot; default rotvec |
| JsvCRP deferred | 14 | Explicitly out |
| RQA later | 14 | Explicitly out |
| Amplitude vs organization | 5 | ROM/RMS covariate |
| Underused at T1 / dormant motors phrasing | 0, 6 | Careful Tier C only |
| Contribution distribution / dominance | 7 | Entropy, top-1 share |
| Trunk/pelvis missing from analysis | 3 | Root→Ab, Ab→Chest |
| Gaga 7-question assessment | 0,5–9,11 | Timing/learning gaps documented |
| Publication as Methods Note | 12 | Findings paper deferred |
| Naive PCA baseline | 12b | Pre-submission task |
| Synthetic validation | 12b | Pre-submission task |
| BVH feature pilot | 2 | Now unblocked |
| ISB pipeline optional | 2, 14 | S2 if BVH fails |
| 671 T3 marker-set confound | 1, 8g, 11e | Shared links + downgrade |
| Pooled vs single repetitions | 4 | Pooled primary; single sensitivity |
| Avatar heatmaps | 1, 10 | Regenerate after final runs |
| Committee storytelling | 11, 11d | COMMITTEE_NARRATIVE.md |
| Instruction vs learning | 0 EXPERIMENTAL_DESIGN | Cannot separate — documented |
| Blinded / no causal drug language | 0 LIMITS | Explicit |
| Scalability 651/790 | 13 | Optional |
| Sensitivity exclude flagged links | 8e | QC robustness |
| Null-space exploratory | 8f | Soft claim only |
| Reprojection / radical strategy warning | 8g | PCA stability gate |
| Window re-rank after trunk | 4b | New in v2 |
| Exploration winners 671 ex11, 252 ex10–14 | 1, 4, 4b | |
| Improvisation / unrepeated movement | 0, 8 | jcvPCA OK; dynamics deferred |

---

# Appendix B — Scripts / artifacts to create (implementation backlog)

| Artifact | Step | Purpose |
|---|---|---|
| `scripts/run_feature_pilot.py` | 2 | BVH intake → matrices → scorecard |
| `scripts/compute_amplitude_covariate.py` | 5 | ROM/RMS join to link tables |
| `scripts/bootstrap_nv_blocks.py` (if needed) | 8a | Within-T1 block bootstrap |
| `scripts/window_revalidation.py` (optional) | 4b | Re-rank windows on final config |
| BVH parser / Euler extractor | 2 | Feature matrix from BVH |
| Extended trunk manifests | 3 | `*_with_trunk.csv` |

---

# BVH intake — what to provide (Step 2 blocker list)

Place or document in `results_committee_case/step02_feature_pilot/intake/`:

1. `BVH_PATHS.md` — full paths, naming convention, which session each file maps to
2. `CHANNEL_DICTIONARY.csv` — BVH joint name → canonical link/DOF, Euler order, units
3. `ALIGNMENT_TEST.md` — one worked example: file frame count vs Motive frame slice for ex11 / ex10–14
4. Optional: pre-exported tidy CSV per session (faster than parsing BVH in-pipeline)

Once intake is complete, Step 2 QC and scorecard can run.
