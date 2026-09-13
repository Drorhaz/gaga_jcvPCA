# Supervisor meeting — elaboration companion (2026-07-18)

**Use with:** [`SUPERVISOR_MEETING_DECK_2026-07-18.md`](SUPERVISOR_MEETING_DECK_2026-07-18.md) (slides)  
**Short thesis brief:** [`SUPERVISOR_MEETING_2026-07-18.md`](SUPERVISOR_MEETING_2026-07-18.md)  
**Figures (by deck block):** [`supervisor_meeting_figures_2026-07-18/`](supervisor_meeting_figures_2026-07-18/README.md) — regenerate: `PYTHONPATH=src .venv/bin/python scripts/supervisor_meeting_figures.py`

Every number below traces to a file under `results_committee_case/` or to pipeline code. Nothing invented.

**Scope balance:** Primary = functional / full retained subspace + NV/robustness sensitivity. Secondary = null/redundant-space trunk–neck insight.

---

## How to use this doc tomorrow

1. Present from the **deck** (one idea per slide).
2. When the supervisor asks “how?” or “why that parameter?”, open the matching section here.
3. End on the **Decisions** checklist — leave blanks for what they decide.

---

# Part A — Question and scope

### Plain claim
We ask whether, **within each dancer**, the relative contribution of body links to shared movement-variance structure changes from T1 to T2/T3 beyond that dancer’s own improvisation variability.

### What we did
Four independent N-of-1 analyses (671, 252, 651, 790) on window `ex09_13` (Group4 curvilinear block). Never pooled across people.

### Exact numbers / design lock
| Field | Value | Source |
|---|---|---|
| Window | `ex09_13_contiguous` | Step 0 / selections |
| Participants | 671, 252, 651, 790 | Step 4 |
| Reference | T1 always side A | jcvPCA paper + code |

### Why it matters
Keeps the project in a defensible descriptive frame for committee.

### Hedge
No causality, no population inference, no timing/anatomical claims.

### If supervisor asks…
**“Is this a Gaga effect?”** → We cannot say. Design is blinded / no control. We report within-person redistribution vs own NV only.

---

# Part B — Feature pipeline: quaternion → parent/child → rotvec

### Plain claim
Analysis features are **relative link rotation vectors**, built from Motive bone quaternions via parent→child composition — not anatomical joint angles.

### What we did / how
Pipeline in [`src/gaga_jcvpca/rotations.py`](../src/gaga_jcvpca/rotations.py) and Motive I/O in [`project_io.py`](../src/gaga_jcvpca/project_io.py):

1. Parse Motive solved-skeleton CSV → per-bone quaternions `(n_frames, n_bones, 4)` SciPy order `[x,y,z,w]`.
2. For each feasible skeleton edge (parent bone → child bone):  
   `q_rel = inv(q_parent) * q_child` (`compute_relative_quaternions`).
3. Apply **sign continuity** along time (quaternion double-cover).
4. Convert to **rotation vector** via SO(3) log-map (`Rotation.as_rotvec()`).
5. Zero-phase Butterworth low-pass in tangent space (default 10 Hz, order 4, 120 Hz capture).
6. Emit features `link_id_rx`, `link_id_ry`, `link_id_rz` for jcvPCA.

### Why chosen
- Paper-faithful S0 stream for jcvPCA.
- Relative parent→child isolates segmental motion from global orientation.
- Avoids claiming ISB flexion/abduction from Euler angles we did not validate as primary.

### Hedge
Features are **not** anatomical joint angles. Do not say “knee flexion increased.”

### If supervisor asks…
**“Why not BVH / Euler?”** → Rotvec is default (S0). BVH/Euler is an optional pilot only if S0 fails QC or interpretability; primary claims stay on rotvecs unless supervisors adopt otherwise (`LIMITS.md`).

**“What is a link?”** → A parent→child bone pair in the Motive skeleton graph (e.g. `LUArm_to_LFArm`, `Ab_to_Chest`).

---

# Part C — QC insights

### Plain claim
We used an **inclusive QC** policy: keep all feasible links including trunk; exclude only clearly un-analyzable segments. Trunk QC passed for all four at T1 R1.

### What we did
- Step 2: map all feasible parent→child pairs per setup (A vs B).
- Step 3: trunk extension + QC (`step03_trunk_extension/TRUNK_QC.md`).
- Flag `include_with_caution` links; Step 4b QC-drop tests whether they drive top-5.

### Exact numbers
| Item | Value | Source |
|---|---|---|
| Trunk QC T1 R1 | PASS × 4 | `TRUNK_QC.md` |
| Caution links | 671: 1; 651: 4; 252/790: 0 | Step 3 / digest §6 |
| QC-drop top-5 overlap | 1.0 all comparisons | `robustness.csv` |
| Setup A | 671, 651 — 18 links, 2 trunk | Step 2 |
| Setup B | 252, 790 — 22 links, 5 trunk/spine | Step 2 |
| Shared-link drops | 651: 14 links evaluated on long.; 671 T3 marker-prefix | digest §4, KNOWN_CONFOUNDS |

### Why it matters
Shows we did not cherry-pick a limb-only template. Partial robustness is **not** a QC artifact.

### Hedge
651 cannot support a trunk-involvement claim when trunk links are missing on follow-up matrices.

### If supervisor asks…
**“Did bad markers drive the story?”** → No. Dropping caution links leaves top-5 unchanged (overlap 1.0).

---

# Part D — Parameter decision log (what / why / how)

| Decision | Chosen | Why | How | Status |
|---|---|---|---|---|
| Feature stream | Relative link rotvecs (S0) | Paper-faithful; not anatomical claims | Motive quats → parent/child → rotvec | **Locked** |
| Analysis window | `ex09_13_contiguous` | Group4 curvilinear block; Step 0/1 lock | Selection YAMLs + pipeline slice | **Locked** |
| Longitudinal headline | Pooled R1+R2 | Descriptive committee headline | Step 4 pooled runs | **Locked** |
| A2 estimand | Single-rep `T1_R1 vs T{k}_R1` | Matched footing with NV floor | Step 8v6 `observed_nv.py` | **Provisional** |
| Reference | T1 = A | jcvPCA definition | `compute_jcvpca` | **Locked** |
| PCA VT | 0.80 | Project default | `pca.variance_threshold` | **Locked** (sensitivity via k-grid) |
| Link set | Full feasible + trunk | Inclusive | Step 2–3 | **Locked** |
| NV floor | Observed R1↔R2 matched | Improvisation; no many-split NV | `observed_nv.py` | **Locked** concept |
| A2 gate | Signed **S2** | Direction-stable exceed | `nv_profile.py` | **Provisional** |
| Signed aggregation | EVR-weighted signed sum | Preserves sign; PC importance | `weighted_JcvPCA_link` sum | **Provisional** |
| ε_sign | 1e-6 | Flag tiny-floor inflation | `nv_floor_unstable` | **Provisional** |
| S1 handling | Report, not A2 | Mag-only is weaker | Tier classifier | **Provisional** |
| Functional split | PC1…p vs p+1…m | Paper dual objective | `functional_null_split` (p≈2) + p50/p60 bands | **Locked** diagnostic |
| Robustness axes | k-grid, rep-mode, QC-drop | Sensitivity without alternate windows | Step 4b | **Locked** |

**Provisional** items need supervisor confirm in `step08_nv_and_stability/SUPERVISOR_NV_DECISION.md`.

### If supervisor asks…
**“Why 0.80 not 0.90?”** → Project default; we do not treat m as sacred — Step 4b k-grid checks whether top-5 survives m changes.

**“Why single-rep for A2 if headline is pooled?”** → Pooled and single-rep use **different T1 bases**. A2 must share footing with the R1↔R2 floor (both A = T1_R1). Always show single-rep signed effect next to pooled headline.

---

# Part E — Sensitivity checks (broad)

## E1. NV / exceedance sensitivity

### Plain claim
Exceedance counts are **sensitive to floor definition**. Matched single-rep + signed S2 is stricter and more honest than pooled abs ratio.

### Exact numbers
| Check | Example | Source |
|---|---|---|
| Pooled → matched abs | 252 T3: 19/22 → **10/22** | digest §8 |
| Abs → signed A2 | 252 T2: abs 10/22 → A2 **8/22**; T3 A2 **13/22** | `NV_PROFILE.csv` |
| Coverage T3 limited | 671 0.70; 252 0.60; 651 0.71; 790 **adequate** 0.89 | `coverage.csv` |
| Floor-unstable | Extreme ratios (e.g. ~133×) flagged | `nv_floor_unstable` |

### Hedge
A large ratio alone is not a large effect if NV≈0.

### If supervisor asks…
**“Which number do we cite?”** → Signed A2 (S2/S3) from `NV_PROFILE.csv`. Abs matched ratio is deprecated-secondary.

---

## E2. Ranking robustness (Step 4b)

### Plain claim
We stress-tested top-link rankings under PC count, take choice, and QC drops — **not** p-values.

### Exact numbers (digest §1–2)
| Pid | T2 label | T3 label | Notes |
|---|---|---|---|
| 671 | stable | stable | rep chain-heuristic can fail |
| 252 | partial | partial | rep-driven; k/QC OK |
| 651 | stable | stable | strongest |
| 790 | stable | partial | T3 weak at dominant band too |

QC-drop overlap = 1.0 everywhere → not QC-driven.

### If supervisor asks…
**“Does partial kill the finding?”** → No for Tier A descriptive. It gates interpretive A3. For 252, dominant p50 can still be stable while full ranking wobbles.

---

## E3. Functional band (primary stability read)

### Plain claim
Dominant coordination (PCs to ~50% T1 EVR) is often more rep-stable than the full 80% EVR top-5.

### Exact numbers
- p50 typically 3–5 PCs; selected_m typically 6–10.
- 252 T3: full pooled↔R1 ≈ 0.4; **p50 ≈ 1.0**.
- 790 T3: ≈ 0.4 even at p50 → stronger caution.

### Source
`functional_pc_bands.csv`, `robustness.csv` (p50/p60 columns).

---

# Part F — Signed NV gate (method heart)

### Plain claim
A2 = per-link **signed exceed** that is **reference-direction stable**, on matched single-rep footing.

### What we did
Module [`src/gaga_jcvpca/nv_profile.py`](../src/gaga_jcvpca/nv_profile.py); script `scripts/observed_nv.py`:

- Floor: `T1_R1 vs T1_R2` on `ex09_13`
- Effect: `T1_R1 vs T{k}_R1`
- Probe: `T1_R2 vs T{k}_R1` (anchor swap)
- Per-link scalar = **EVR-weighted signed sum** of `JcvPCA_link`
- S2 if `|long| > |nv|` and `sign(long) == sign(long_rev)`
- S3 if S2 + coverage adequate + rep pass + Step-5 organization

### Why within-link (not cross-link magnitude)
Arms are more articulated/accessible than trunk. Cross-link |Δ| ranking is not commensurate. The fair test is **each link vs its own NV**. A trunk S2 with small |Δ| can still be a real within-link exceedance.

### Hedge
A2 rests on **n=1 rep-pair** per link (no margin). S1 vs S2 is the robustness handle on that scalar floor.

### If supervisor asks…
**“Is sign-consistency ‘same as R1→R2’?”** → No. That would be label-dependent. We use **stability under R1/R2 anchor swap**.

---

# Part G — Headline table (signed A2)

| Pid | Links | A2 T2 | A2 T3 | S3 | Cov T2/T3 | Robust T2/T3 |
|---|---:|---:|---:|---|---|---|
| 671 | 18 | 8/18 | 9/17 | 4 (T2) | adequate / limited | stable / stable |
| 252 | 22 | 8/22 | 13/22 | none | adequate / limited | partial / partial |
| 651 | 14 eval | 8/14 | 7/14 | 5 (T2) | adequate / limited | stable / stable |
| 790 | 22 | 5/22 | 5/22 | none | adequate / adequate | stable / partial |

Source: `step08_nv_and_stability/NV_PROFILE.csv`, `robustness.csv`, `coverage.csv`.

---

# Part H — Per-participant deep dive

## H1. Participant 671

### Results
- A2: **8/18** (T2), **9/17** (T3)
- **S3 T2:** `671_to_LThigh`, `LFArm_to_LHand`, `LShin_to_LFoot`, `LThigh_to_LShin`
- Persistence: **6** persistent A2 links (incl. trunk roots `671_to_Ab`, thighs, LFArm→LHand, LShin→LFoot, LThigh→LShin); 71% sign agreement
- Trunk: `671_to_Ab`, `Ab_to_Chest` reach **S2** under within-link rule (small absolute Δ)
- selected_m ≈ 9 (long.), 8 (NV)

### Say this
“671 is our most temporally stable case: arm and leg-chain contribution changes exceed own NV in a direction-stable way and largely persist T2→T3. Some trunk links also clear S2 when judged against their own floor.”

### Don’t say
“Trunk dominates.” Regionally trunk ranks last by |Δ|; S2 is within-link, not region dominance.

### Hedges
T3 coverage limited; functional-chain heuristic not retained under rep; watch floor-unstable trunk ratios.

### Role in story
Primary persistent + has S3 candidates.

---

## H2. Participant 252

### Results
- A2: 8/22 (T2), **13/22** (T3)
- **No S3** (rep_pass false; T3 coverage limited)
- Underused-at-T1 (bottom tertile JRW_A): **7/8** increased + beyond NV at T2
- Step 5: T3 NV-exceed (pooled-era classif.) **19/19 organization**
- Persistence: only 3 persistent; **10 emergent_T3**; sign-agree 41%
- Null-space (secondary): neck \|Δ\|_null ≈ 0.045 vs fun ≈ 0.013 at T3

### Say this
“252 shows the broadest T3 signed redistribution and the clearest underused-at-T1 signal at T2, with organization-type amplitude. We still withhold S3 because take-stability and T3 coverage don’t clear the interpretive bar.”

### Don’t say
“Validated broader participation for 252” without supervisor — no S3.

### Role
Strongest redistribution narrative; keep gated.

---

## H3. Participant 651

### Results
- A2: **8/14** (T2), 7/14 (T3)
- **S3 T2:** `Chest_to_Neck`, `LFArm_to_LHand`, `LUArm_to_LFArm`, `Neck_to_Head`, `RThigh_to_RShin`
- Strongest robustness (stable both)
- True trunk (`*_to_Ab`, `Ab_to_Chest`) **absent** on some follow-up comparisons
- Neck often **functional-dominant** (counterexample to null-trunk story)
- Persistence: 3 persistent (neck/chest)

### Say this
“651 is the honest conservative case with the strongest robustness — and still produces S3 candidates at T2 in neck and arm chain. We cannot claim trunk involvement here because trunk links drop out of shared T2/T3 matrices.”

### Role
Counterweight / not-overfitting + S3 yes.

---

## H4. Participant 790

### Results
- A2: **5/22** both timepoints
- No S3; underused beyond-NV ≈ 0
- T3 coverage adequate but T3 robustness partial at dominant band
- Persistence: only `RUArm_to_RFArm`
- Extreme floor-unstable ratio exists — do not headline

### Say this
“790 is where the method self-limits: few direction-stable exceeds, no S3, underused links don’t clear NV. Useful as the caution case.”

### Role
Limits demonstration.

---

# Part I — Cross-cutting results (Steps 5–7, 9)

| Step | Finding | Source |
|---|---|---|
| 5 Amplitude vs org | 252 T3: organization dominates among exceed links | `classification_summary.md` |
| 6 Underused@T1 | 252 T2 7/8; 671 T2 6/6 increased (3 beyond NV); 790 ≈ 0 | `underused_link_results.csv` |
| 7 Distribution | Entropy & top-1 share move ≤ 0.01 — **not global broadening** | `distribution_metrics.csv` |
| 9 Persistence | 671 most persistent; 252 T3 emergent | `persistence_results.csv` |

### Why Step 7 matters
Supports “link-specific reweighting” and blocks “the whole body opened up.”

---

# Part J — Functional vs null (secondary insight)

### Plain claim
Paper: first p PCs = functionally used joints; last (m−p) = redundant / null. For an arm-led task, arms should load functional; subtle trunk/neck may appear more in secondary PCs.

### Exact numbers (T1→T3 mean |Δ|)
| Pid | Band | Functional | Null | Pattern |
|---|---|---:|---:|---|
| 252 | arm | 0.20 | 0.15 | more functional |
| 252 | neck | 0.013 | **0.045** | null-dominant |
| 252 | trunk_core | 0.009 | 0.015 | null-dominant |
| 651 | neck | 0.028 | 0.019 | **functional** (counterexample) |

Sources: `functional_space_results.csv`, `null_space_results.csv` (pooled primary).

### Say this
“In 252 T3, arm changes sit mainly in task-relevant PCs while neck changes sit more in secondary/redundant PCs — consistent with the paper’s dual objective. This is a secondary, case-dependent insight, not the primary A2 claim for all four.”

### Don’t say
“Gaga activates null-space trunk in everyone.” 651 disagrees; not causal.

### Future
Optional next: **null-only signed NV profile** (S2 logic on PC(p+1)…m only) — ask supervisor if worth building.

---

# Part K — Claims ladder

| ID | Claim | Status from data |
|---|---|---|
| A1 | Contribution changed T1→later | **Supported** all 4 |
| A2 | Exceeds own NV, direction-stable (S2) | **Supported** subset of links all 4 |
| A3 | Broader / underused interpretive | **Only** 671 & 651 T2 S3 candidates, supervisor-gated |
| A4 | Redistribution among specific links | **Supported**; not global entropy shift |

### Forbidden list (keep on a slide)
Causality · population · p-values · global opening · new DOF · timing/segmentation · muscle/anatomical angles · trunk as main effector

---

# Part L — Future questions & decisions (consultation)

Fill in during the meeting:

| # | Question | Decision / notes |
|---|---|---|
| 1 | Confirm Phase-0 (S2=A2, ε_sign=1e-6, EVR-weighted, S1 not A2)? | |
| 2 | Interpretive A3 only for S3 candidates? | |
| 3 | Elevate null-space trunk/neck — show only / deepen with null-only NV / hold? | |
| 4 | Adopt within-link NV wording (vs cross-link magnitude) for committee? | |
| 5 | Stay on rotvecs S0 — reopen BVH pilot? | |
| 6 | Run Layer 2 subsample stability before committee? | |
| 7 | Feature: 671+252 primary, 651 counterweight, 790 limits? | |
| 8 | Next: Step 10 `FINDINGS_SUMMARY` vs thesis methods note? | |

---

# Part M — Anticipated challenges (quick answers)

**“Isn’t improvisation noise?”**  
NV already includes real take differences → exceeding it is a high bar, not a weak one.

**“Arms always win by magnitude.”**  
We don’t compare across links by |Δ|. We compare each link to its own NV. Trunk can S2 with small |Δ|.

**“Why no statistics?”**  
By design at this N: descriptive ratios, signed tiers, robustness labels — not significance.

**“Did you overfit the method to find a story?”**  
790 fails S3; 651 trunk missing; coverage/rep gates block 252 S3; Step 7 blocks global-broadening language. The gates refuse over-claim.

**“Is null-space the main finding?”**  
No. Primary = full/functional A2. Null is a secondary paper-aligned insight, strongest in 252.

---

# Part N — File index

| Need | Path |
|---|---|
| Deck | `docs/SUPERVISOR_MEETING_DECK_2026-07-18.md` |
| This elaboration | `docs/SUPERVISOR_MEETING_ELABORATION_2026-07-18.md` |
| Short brief | `docs/SUPERVISOR_MEETING_2026-07-18.md` |
| Digest | `results_committee_case/METRICS_DIGEST.md` |
| Signed NV | `results_committee_case/step08_nv_and_stability/NV_PROFILE.csv` |
| Phase-0 | `results_committee_case/step08_nv_and_stability/SUPERVISOR_NV_DECISION.md` |
| Robustness | `results_committee_case/step04_primary_runs/robustness.csv` |
| Functional/null | `…/step04_primary_runs/{pid}/ex09_13_contiguous_pooled/{functional,null}_space_results.csv` |
| Rotvec code | `src/gaga_jcvpca/rotations.py` |
| NV code | `src/gaga_jcvpca/nv_profile.py` |
