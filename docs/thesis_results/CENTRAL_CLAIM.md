# Central claim — three wordings

**Question this claim answers:**  
Can within-participant changes in **link contribution** to shared movement-variance structure be detected across T1→T2 and T1→T3, in the Group4 window `ex09–ex13`, **beyond observed T1 R1↔R2 repetition variability**?

**Measurement:** reference-anchored jcvPCA on **parent–child relative rotation vectors**. T1 is always side A. A2 = signed NV tier **S2** (matched single-rep). Not joint angles, EMG, timing, “improvement,” or a treatment effect.

**Evidence files (all versions):**  
`results_committee_case/marker_gap_policy_ex09_13/step08_nv_and_stability/NV_PROFILE.csv`  
`tables_to_show/09_headline_a2_summary.csv`  
`tables_to_show/06_coverage_gate_a2_estimand.csv`  
`step00_claim_framework/CLAIMS.md` and `LIMITS.md`  
`step09_persistence_t2_t3/persistence_summary.md`  
`step07_contribution_distribution/distribution_summary.md`

---

## Version 1 — very conservative (always allowed)

**Wording**

> In four separate N-of-1 OptiTrack case studies, reference-anchored jcvPCA on relative link rotation vectors was applied to the concatenated Group4 window (ex09–ex13). For each person, some links changed their relative contribution to T1’s retained movement-variance subspace between T1 and T2 and/or T1 and T3. Using a matched single-repetition signed comparison against that person’s own T1 R1↔R2 take, a subset of those links exceeded the observed repetition range with a direction that did not reverse when the T1 reference take was swapped (tier S2). Counts, coverage, and QC exclusions differ by person. No group effect is estimated.

| Field | Value |
|---|---|
| CLAIMS.md | **A1** (all four) + **A2** as a count statement, not a mechanism |
| Descriptive vs interpretive | Descriptive |
| Must sit next to it | N=4 N-of-1; NV is one rep-pair; features are rotvecs; T1 reference; marker-gap drops; 252 T3 coverage 0.60 |
| Allowed now? | **Yes** — no supervisor signature required |

---

## Version 2 — recommended for the first draft

**Wording**

> The method can detect within-person, link-level contribution change in this protocol window that is not identical to T1 take-to-take repetition. The pattern is **participant-specific**, not a shared coordination strategy.  
>  
> Only **671 T1→T2** currently satisfies the pre-registered interpretive stack for a stronger reading: 8 of 18 links meet signed S2, 4 of those also meet S3 (`LFArm_to_LHand`, `671_to_LThigh`, `LThigh_to_LShin`, `LShin_to_LFoot`), reference-subspace coverage is adequate (0.81), and repetition-mode/QC ranking is stable. Six of 671’s S2 links keep the same sign at T3, but T3 coverage is limited (0.70), so T3 is reported as descriptive persistence, not as a second S3 cell.  
>  
> For 252, 651, and 790, S2 links exist but S3 is zero: either coverage is limited (especially 252 T3), marker-gap/template stripping removes trunk or limb chains (651, 790 right arm, 252 left leg), k-grid ranking is unstable, or several S2 ratios sit near 1. Contribution entropy is essentially unchanged in every longitudinal comparison, so the data show **reweighting among links**, not global broadening of degrees of freedom.  
>  
> These differences are **consistent with** individual reorganization of contribution structure during the intervention period. They do not identify Gaga or psilocybin as the cause, and they do not show a common group direction.

| Field | Value |
|---|---|
| CLAIMS.md | A1 + A2 (all, descriptive) + **candidate A3 for 671 T2 only** (S2 + coverage + Step 5 organization + Step 4b). A4 (redistribution) yes; “broader whole-body participation” **no** |
| Descriptive vs interpretive | Mixed: A1/A2 descriptive; one guarded A3 sentence for 671 T2 |
| Must sit next to it | S3 footing note (governing 4 vs romflat 7); unsigned `SUPERVISOR_NV_DECISION.md`; LUArm T2 ratio is NV-degenerate; 252 T3 must not be the hero figure |
| Allowed now? | **Yes for a draft**, if A3 is labeled *candidate / pending supervisor*. If supervisors later reject A3, drop that paragraph and keep Version 1 + the 671 T2 S2 list |

This is the version to paste into the Results opening and the Discussion’s first paragraph.

---

## Version 3 — slightly broader (only if extra conditions hold)

**Wording**

> Across four N-of-1 cases, signed S2 exceedances of T1 repetition variability were observed in every T1→T2 and T1→T3 comparison, with 671 additionally showing S3-gated, ROM-flat reorganization concentrated on the left distal arm and left leg, and the only multi-link T2–T3 persistent set. This is consistent with **person-specific redistribution of contribution inside T1’s retained subspace** during the intervention period, more often in the organization (flat-ROM) direction than in a simple amplitude scaling.

**Do not use Version 3 in the first draft.** Extra conditions that are **not** all true today:

1. Supervisor sign-off on S3 / A3 language (`SUPERVISOR_NV_DECISION.md` empty).
2. Decision that Step 5’s pooled organization gate is accepted (or replacement by romflat-7 for 671 T2).
3. A reader-safe way to mention “every comparison has S2” without implying equal strength (790 T2 ratios 1.06–1.08; 252 T2 ratio 1.01; 252 T3 coverage 0.60).
4. Explicit rejection of any leftover “underused DoF / dormant motors” gloss — CLAIMS.md A3 is already narrower than that (*reweighting inside T1’s subspace*).

| Field | Value |
|---|---|
| CLAIMS.md | Pushes A2 toward a **uniform** reading the evidence stack does not support; A3 still only 671 T2 |
| Descriptive vs interpretive | Interpretive — **not allowed** as a main-text claim until (1)–(3) |
| Allowed now? | **No** |

---

## Forbidden sentences (all versions)

Do not write, even in Discussion, as findings of this lock:

- Gaga caused the change / activated remote motors.
- Psilocybin caused the change / placebo comparison.
- The participant improved, learned, or acquired new degrees of freedom.
- Muscles or dormant regions were recruited.
- A group effect or statistical significance was found.
- Joint angles, muscle activation, or temporal synchrony were measured.
- 252 T3 is the strongest evidence of reorganization (it is the weakest *coverage*).
- Entropy increase proves broader DoF access (entropy is flat).

---

## Mapping to the thesis question

| Question piece | Lock answer |
|---|---|
| Detect individual link-contribution change? | **Yes** (A1), all four, rotvec jcvPCA |
| Beyond T1 repetition variability? | **Yes, unevenly** (A2/S2). Strongest: 671 T2. Weakest as a *claim*: 252 T2 (n=3, ratio 1.01) and 252 T3 (coverage) |
| Shared pattern across people? | **No** |
| Cause = Gaga or psilocybin? | **Not asked, not answered** |
