# Supervisor meeting — scientific story & findings (2026-07-18)

**Prep doc for tomorrow.** Four within-participant (N-of-1) case studies: 671, 252, 651, 790.
Window `ex09_13` (Group4 curvilinear block, pooled). All numbers below trace to
`results_committee_case/METRICS_DIGEST.md`, `step08_nv_and_stability/`, `step05_amplitude_vs_organization/`,
`step04_primary_runs/robustness.csv`. **Nothing here is invented — every figure has a source file.**

**Meeting pack (use these tomorrow):**
- **Slides (show):** [`SUPERVISOR_MEETING_DECK_2026-07-18.md`](SUPERVISOR_MEETING_DECK_2026-07-18.md) — Marp deck (~30 slides)
- **Speak notes (explain):** [`SUPERVISOR_MEETING_ELABORATION_2026-07-18.md`](SUPERVISOR_MEETING_ELABORATION_2026-07-18.md) — pipeline, QC, parameter decisions, sensitivity, per-pid, null-space, Q&A
- **Figures (by deck block):** [`supervisor_meeting_figures_2026-07-18/`](supervisor_meeting_figures_2026-07-18/README.md) — 22 PNGs; regenerate with `scripts/supervisor_meeting_figures.py`

> **Update (2026-07-18, pre-meeting):** the **signed NV profile (Step 8v6)** and **Steps 6, 7, 9** are now
> **implemented and run** (provisional Phase-0 defaults — see `SUPERVISOR_NV_DECISION.md`). This doc now
> reports the **signed S0–S3 tiers** (A2 = S2) alongside the older abs matched ratio. New source files:
> `step08_nv_and_stability/NV_PROFILE.csv`, `step06_underused_at_t1/`, `step07_contribution_distribution/`,
> `step09_persistence_t2_t3/`.

---

## 0. One-sentence thesis

> In each of four dancers, reference-anchored jcvPCA on whole-body MoCap shows that the **relative
> contribution of specific body links to shared movement-variance structure changes from T1 to later
> timepoints**, and for a subset of links this change **exceeds that person's own take-to-take
> improvisation variability** — a conservative, descriptive proxy for "broader access to underused
> degrees of freedom," with **no** causal, timing, or population claim.

---

## 1. What we actually did (method in one breath)

- **Feature:** relative link rotation vectors (not anatomical joint angles).
- **jcvPCA:** T1 is always the reference basis A; T2/T3 (B) are projected into T1's retained subspace;
  per link we get a signed contribution change `JcvPCA_link = JRW_B − JRW_A`.
- **4 separate N-of-1 analyses** — never pooled across people.
- **Natural variability (NV) floor** = same-condition **R1↔R2** variability, on **matched single-rep
  footing**, same window, same T1 basis: `(T1_R1 vs T{2,3}_R1)` compared to `(T1_R1 vs T1_R2)`.
- **Coverage gate** read first: is T2/T3 even well-represented in T1's subspace?

Key framing to say out loud: **jcvPCA measures reweighting *within* T1's existing coordination
subspace.** Genuinely new degrees of freedom would show up as *low coverage*, not as redistribution.
So our positive result is deliberately the *narrower, safer* claim.

---

## 2. What we found — the four participants

### Headline table (matched single-rep exceed = authoritative Tier A)

| Participant | Links | Exceed NV T1→T2 | T1→T3 | Exceed **both** | Coverage T2 / T3 | Robustness (T2/T3) |
|---|---:|---:|---:|---:|---|---|
| **671** | 18 | **12/18** | 9/18 | **6** | adequate / **limited** (0.70) | stable / stable* |
| **252** | 22 | 10/22 | 10/22 | **7** | adequate / **limited** (0.60) | partial / partial |
| **651** | 18 (14 eval) | 3/18 | 5/18 | 2 | adequate / **limited** (0.71) | **stable / stable** |
| **790** | 22 | 5/22 | 7/22 | 3 | adequate / **adequate** (0.89) | stable / **partial** |

\*671 top-5 overlap is stable but the functional-chain heuristic is *not* retained under rep
perturbation — flag it.
Source: `METRICS_DIGEST.md` §8, §1; `step08_nv_and_stability/coverage.csv`.

### Signed A2 (S2/S3) — the firmer number to present

Signed exceed = larger than the T1 rep spread **and** direction-stable to the arbitrary R1/R2 anchor
(S2). S3 = S2 + coverage adequate + rep-stable (Step 4b) + Step-5 organization.

| Participant | A2 pass T1→T2 | A2 pass T1→T3 | S3 candidates (T2) |
|---|---:|---:|---|
| **671** | **8/18** (4 = S3) | 9/17 | `671_to_LThigh`, `LFArm_to_LHand`, `LShin_to_LFoot`, `LThigh_to_LShin` |
| **252** | 8/22 | **13/22** | none — rep gate (k-grid 0.4) + T3 coverage limited |
| **651** | **8/14** (5 = S3) | 7/14 | `Chest_to_Neck`, `LFArm_to_LHand`, `LUArm_to_LFArm`, `Neck_to_Head`, `RThigh_to_RShin` |
| **790** | 5/22 | 5/22 | none — rep gate (k-grid 0.4) |

Source: `step08_nv_and_stability/NV_PROFILE.csv`, `METRICS_DIGEST.md` §8v6.

> Say it: "Only **671 and 651 at T2** produce S3 candidate-interpretive links; everyone else stays at
> S2 (statistical exceed) because rep-stability or coverage doesn't clear the interpretive bar. That's
> the machinery doing its job."

### The convergent signal (the real story)

Across **all four** dancers, independently, the **distal arm chain** dominates the redistribution:
`UpperArm→Forearm`, `Forearm→Hand`, `Shoulder→UpperArm` appear in the top-5 changed links for every
participant; legs (`Thigh→Shin`) are a secondary theme. Trunk/spine links rank mid-tier.
Source: `METRICS_DIGEST.md` §4–5, `functional_pc_bands.csv` (`top5_all_pcs`).

> Say it carefully: "Four independent N-of-1 cases each show arm-chain links among the largest
> contribution shifts." That is a *convergence observation*, **not** cohort inference.

### Cleanest single case: 252 T1→T3

- Largest effect magnitudes (`RUArm_to_RFArm` |Δ|=0.35).
- **19/19** NV-exceeding links classified **organization** (flat ROM) → redistribution, not "just
  bigger movement." Source: `step05.../classification_summary.md`.
- But pooled floor said 19/22 exceed; **matched single-rep says 10/22** — we cite the stricter number.

---

## 3. How we quantified NV / the improvisation problem (the methodological heart)

This is what makes the project defensible; spend time here.

1. **The paper's NV (random splits of many repeated discrete movements) is not reproducible** — we
   have 2 long *improvised* takes per timepoint. So we redefined NV honestly as **observed
   same-condition repetition variability** (R1↔R2).
2. **Improvisation means R1 ≠ R2 genuinely** — the floor already *contains real movement differences*,
   not just measurement noise. So "exceeds NV" is a **conservative, high bar** (effect beats
   take-to-take improv spread). This is a strength, not a weakness — frame it that way.
3. **The T1 floor is trustworthy:** coverage of the T1 R1↔R2 floor is adequate for all four
   (0.86–0.94). Source: `coverage.csv`.
4. **Pooled floor overstates exceedance** — we switched to matched single-rep (252 T3: 19→10). Report
   matched only.
5. **Ratio inflation on low-variability links** (known limitation, honestly flagged): e.g. 790
   `LUArm_to_LFArm` matched ratio ≈ **133×**, 671 trunk links ≈ 10–13×, 252 spine links ≈ 9×. These are
   **small-denominator artifacts** (a near-zero NV inflates the ratio), *not* 133× real effects. The
   v6 `ε_sign` flag (**now implemented**, default `1e-6`) marks these `nv_floor_unstable` in
   `NV_PROFILE.csv`, and the **signed S2 gate does not rely on the ratio at all** — it uses signed
   magnitude + direction stability. Source: `nv_summary.csv`, `NV_PROFILE.csv`.
6. **Protocol openness (ex13/ex09 variability ratio) is participant-specific with no consensus**
   (671 2.25→0.91 across T1→T3; 651 T3=3.31; 252 rises 0.79→1.77; 790 T2 spike 2.06). Descriptive
   context only — **not** improvisation skill or learning. Source: `EXERCISE_PROTOCOL_OPENNESS.md`.

---

## 4. What we CAN conclude (descriptive / Tier A)

- **A1:** link/region relative contribution to shared variance structure **changed** T1→T2/T3 (all four).
- **A2 (signed, direction-stable):** for a **subset of links per person**, the change **exceeds that
  person's observed T1 repetition variability AND keeps its direction under R1/R2 anchor swap** (S2).
  Counts in §2 signed table (671 8/18, 252 13/22 at T3, 651 8/14, 790 5/22).
- **Redistribution is organization-type, not amplitude** where ROM is flat (strongest: 252 T3, 19/19).
- **A4 (redistribution among specific links), NOT global broadening:** contribution **breadth is
  essentially unchanged** — entropy and top-1 share move ≤ 0.01 at every timepoint (Step 7). The story
  is *which* links redistribute, not that the whole-body distribution flattens.
- **Underused-at-T1 links do increase in a couple of cases** (Step 6): **252 T1→T2 = 7/8** underused
  links exceed NV with increased contribution (strongest broader-participation signal); 671 T2 6/6
  increased (3 beyond NV). 790 shows essentially none → do not claim underused activation there.
- **671's effects persist across T2 and T3** (Step 9: 6 persistent links, 71% sign agreement); 252's
  T3 change is largely **emergent at T3** (10 emergent links, 41% sign agreement), not a continuation.
- **Dominant low-dimensional coordination (3–5 PCs) is more repetition-stable** than the fine-grained
  full ranking — so the *big-picture* pattern is more trustworthy than any single link's rank.

## 5. What we CANNOT say (keep these on a slide)

- Gaga/psilocybin **caused** anything (blinded, no control condition).
- Improved **timing / synchronization / less segmentation** (no dynamic metrics in scope).
- **Dormant motors activated**, or any **anatomical joint-angle / muscle** statement (features are
  relative rotvecs).
- **Population / cross-participant** effect (four separate N-of-1).
- Statistical **significance / p-values / CIs** (by design at this N).
- Access to **genuinely new DOF** — method only sees reweighting within T1's subspace.

## 6. How we hedge (defensive moves, per finding)

- **T3 caution:** 3/4 have *limited* T3 coverage (671, 252, 651) → interpretive language on T3 is
  hedged; 790 T3 keeps coverage but is rep+k unstable (opposite trade-off).
- **Matched, not pooled** floor everywhere.
- **`ε_sign` / floor-unstable flag** on inflated-ratio links (don't headline a 133× link).
- **Organization vs amplitude** (Step 5) gate before "redistribution" wording.
- **Dominant-mode (p50) reporting** when the full ranking is rep-sensitive (252 T3 p50 overlap = 1.0
  even though full = 0.4 → the *dominant story* is stable, only fringe links wobble).
- **N-of-1 side-by-side**, never averaged.
- **Blinded language:** "T1 vs later timepoint," not drug/practice.

---

## 7. Next steps

### Done since last plan (ready to show)
- ✅ **Step 8v6 signed NV** implemented (`nv_profile.py`, tested) + re-run all 4 pids → `NV_PROFILE.csv`
  with S0–S3 tiers, ε_sign flag, S3 evidence stack. Signed A2 replaces the ratio for the gate.
- ✅ **Steps 6, 7, 9** run: underused-at-T1, contribution distribution (entropy/top-1), T2↔T3 persistence.

### For the committee (short path)
1. **Phase 0 supervisor lock** (this meeting): confirm the **provisional defaults** already coded
   (signed **S2** = A2 gate; ε_sign=1e-6; stratum K=2; S1 reported-not-counted; EVR-weighted signed
   sum) → sign off `SUPERVISOR_NV_DECISION.md`. Any change is a cheap re-run.
2. **Step 10** `FINDINGS_SUMMARY.csv` + interpretation; **Step 11** committee brief + one-pager.
3. *(Optional)* Step 8h **Layer 2** subsample spread (firewalled) if a spread visual is wanted.

### For the thesis / methods note
- The **NV-for-improvisation** redefinition + **coverage gate** + **ε_sign floor-stability** is itself
  a methods contribution — package as an Application Note.
- **Naive-PCA baseline** and **synthetic validation** (Step 12b) to show jcvPCA adds value.
- Feature-stream appendix (rotvec default; BVH evaluated).

---

## 8. Decisions I need from you tomorrow

1. **Confirm the coded Phase-0 defaults** (signed S2 = A2, ε_sign=1e-6, K=2, EVR-weighted signed sum,
   S1 reported-not-counted) — or override any (cheap re-run).
2. **Claim tier:** comfortable presenting **A2 as signed S2 (descriptive)** now, and **A3 interpretive
   "broader participation"** only for the **S3 candidate links** (671/651 T2), supervisor-gated?
3. **NV wording** for committee (adopt "exceeds observed repetition variability, direction-stable, descriptive").
4. **Which case to feature:** 671 (persistent, has S3 candidates) & 252 (broad T3 signal, 7/8 underused
   exceed at T2) as primary, 651 (conservative, strongest robustness, has S3) as counterweight, 790
   (caution, no S3) as the limits example?

---

### Appendix — per-participant one-liners

- **671:** broadest T2 signal (signed A2 8/18, **4 S3 candidates**: LThigh, LFArm→LHand, LShin→LFoot,
  LThigh→LShin); **most persistent** (6 links hold T2→T3, 71% sign agree); arm-led; rep chain-heuristic
  fails; T3 coverage limited. Trunk ratios inflated (floor-unstable).
- **252:** broadest **T3** signed A2 (**13/22**) and cleanest organization (T3 19/19 flat ROM); **7/8
  underused links exceed at T2**; but **no S3** (k-grid rep gate 0.4 + T3 coverage limited) and T3 is
  largely **emergent** (10 emergent, 41% sign agreement) → present as "strong but not yet interpretive."
- **651:** conservative (signed A2 8/14) but **strongest robustness** and has **5 S3 candidates at T2**
  (arm chain + Neck) — use as the "we're not overfitting, and it still clears the interpretive bar" case.
- **790:** adequate T3 coverage (the exception) but **weakest** signal (signed A2 5/22, **no S3**,
  underused links don't increase); one extreme floor-unstable link (133×). Use to demonstrate the
  caution machinery — the method correctly refuses to over-claim here.
