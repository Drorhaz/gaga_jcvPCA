# One-week execution plan — committee case study + publish path

> **Superseded for step detail by:** [`MASTER_EXECUTION_PLAN.md`](MASTER_EXECUTION_PLAN.md) — full scope/method/deliverable/decision gates for all 13 steps (including BVH pilot).  
> This file remains a **time-boxed summary** (Week 1 supervisors / Week 2 slides).

**Created:** 2026-07-11  
**Horizon:** Week 1 = implement + supervisor share | Week 2 = committee slides  
**Audience:** PhD supervisors (end Week 1), committee (Week 2)

---

## Mission (what this week is for)

You are **not** trying to prove Gaga “activates dormant motors” or to publish a treatment-effect paper this week.

You **are** trying to deliver a **rigorous, modest, evidence-backed case study** that shows:

1. You built a **reproducible pipeline** that applies reference-anchored jcvPCA to whole-body improvisational MoCap.
2. You can **quantify contribution-structure change** (who carries the movement-variance pattern) before vs after the intervention period, against an honest NV floor.
3. You know **exactly what you can and cannot claim**, and have closed the biggest methodological gaps we identified (trunk under-selection, amplitude vs organization, weak NV).
4. The Gaga “remote motors / broader DoF access” idea is framed as a **motivating hypothesis** with a **conservative operational proxy** — not as proven mechanism.

**End of Week 1 deliverable to supervisors:** a short written brief + figures + one-page results summary they can read in 15 minutes.

**Week 2 deliverable:** committee slide deck built from that package (story + methods + limits + trajectory).

**Publication path (later):** Methods/Application Note first; findings paper only after method note + stronger NV + more N.

---

## Scope lock (do not expand this week)

| In scope | Out of scope |
|---|---|
| jcvPCA on relative link rotvecs | JsvCRP / phase / RQA |
| Trunk links re-inclusion (QC-gated) | Full Euler/BVH pilot (unless files arrive Day 1) |
| ROM/RMS amplitude covariate | EMG, subjective scales (note as future) |
| NV descriptive + simple window bootstrap | Population inference, cross-participant pooling |
| 671 + 252 case study, winning windows | New participants beyond quick 651/790 spot-check |
| Careful claim language + committee brief | Full journal submission draft |

---

## Week 1 — day-by-day plan

### Day 1 (Mon) — Lock story + audit baseline

**Goal:** Know exactly what you have before changing anything.

- [ ] **1.1** Read and adopt claim language from this chat (contribution redistribution; no dormant motors; no timing; descriptive NV).
- [ ] **1.2** Export baseline snapshot for supervisors (no reruns yet):
  - Winning windows: 671 `ex11_single` pooled; 252 `ex10_14_contiguous` pooled
  - Pull: link tables, region heatmaps, `decision_log.md`, `validation_summary.md` per winner
- [ ] **1.3** Write **one paragraph “current conclusion”** (what we can say today) and **one paragraph “cannot say yet”**.
- [ ] **1.4** Inventory trunk gap: confirm raw bones `Root→Ab`, `Ab→Chest` exist; list why excluded from manifests.

**Deliverable:** `docs/COMMITTEE_BRIEF_DRAFT.md` §1–2 (problem + current state).

---

### Day 2 (Tue) — Trunk links + re-run winners

**Goal:** Fix the biggest anatomical gap for Gaga center→periphery story.

- [ ] **2.1** Extend feature manifests (671 + 252) with QC-gated trunk links:
  - `Root→Ab` (or participant-root → Ab)
  - `Ab→Chest`
  - Keep participant-specific pelvis roots (252 only) labeled non-comparable
- [ ] **2.2** Update `body_regions.yaml` matching if needed so `trunk_spine` populates.
- [ ] **2.3** Create/update selection YAMLs for winning windows with trunk links included.
- [ ] **2.4** Re-run jcvPCA (pooled + NV) for both winners with `--validate`.
- [ ] **2.5** Compare **with vs without trunk**: link count exceeding NV, region story, top links.

**Deliverable:** `results_committee_case/` folder with before/after trunk comparison table.

**Stop rule:** If trunk links fail QC (>X% invalid/jumps), document exclusion reason; do not force them into claims.

---

### Day 3 (Wed) — Amplitude vs organization + “underused at T1”

**Goal:** Separate “moved bigger” from “contribution reorganized.”

- [ ] **3.1** Add per-link **ROM/RMS** (or mean abs rotvec magnitude) per session/window — simple table, no new dynamics.
- [ ] **3.2** For each winner run, join ROM with JcvPCA link table.
- [ ] **3.3** Define **T1-underused links**: e.g. bottom quartile of `JRW_A_link` (functional space mean) at T1.
- [ ] **3.4** Test: did underused links show **relative contribution increase** at T2/T3 beyond NV?
- [ ] **3.5** Add **contribution distribution** metrics: top-1 link share, Gini or entropy across links (T1 vs T2 vs T3).

**Deliverable:** `results_committee_case/amplitude_vs_organization.md` + CSV tables.

**Interpretation rule:**
- Redistribution + flat/uniform ROM scaling → stronger “organization” language
- ROM scales everywhere + JcvPCA shifts → report both; soften organization claim

---

### Day 4 (Thu) — Strengthen NV + stability (still no JsvCRP)

**Goal:** Make the NV floor less embarrassing for committee questions.

- [ ] **4.1** Run **window/block bootstrap** within T1 for winning windows (if ≥4 blocks; else document insufficient).
- [ ] **4.2** Report: % of bootstrap resamples where longitudinal Δ exceeds NV Δ per link.
- [ ] **4.3** Run **threshold sweep** 0.70/0.80/0.90 on winners; record `selected_m` + top-5 link stability.
- [ ] **4.4** Run **PCA stability** check (T1 R1 vs R2 vs pooled) — flag unstable comparisons.
- [ ] **4.5** T2 vs T3 **persistence check**: same links/regions exceed NV at both timepoints?

**Deliverable:** `results_committee_case/nv_and_stability_summary.md`

**Language upgrade:** replace “significant” with “bootstrap-supported (descriptive)” or “exceeds observed R1–R2 floor.”

---

### Day 5 (Fri) — Case study wrap + supervisor package

**Goal:** Ship the supervisor shareable package.

- [ ] **5.1** Regenerate avatar/heatmap figures for final winner configs (with trunk if included).
- [ ] **5.2** Write **`docs/COMMITTEE_BRIEF.md`** (2–3 pages max):
  - Problem & Gaga hypothesis (careful framing)
  - Method (jcvPCA, rotvecs, T1 reference, NV)
  - What was done this week (trunk, ROM, bootstrap, stability)
  - Results (671 + 252, bullet findings)
  - Limits (N, 2 reps, no timing, no causality)
  - Trajectory (methods note → findings later)
- [ ] **5.3** Write **`docs/SUPERVISOR_ONE_PAGER.md`** — 1 page, 5 bullets + 2 figures.
- [ ] **5.4** Create **`results_committee_case/FINDINGS_SUMMARY.csv`**: participant, window, n_links_exceed_nv, mean_effect_ratio, n_underused_increased, trunk_included, bootstrap_supported_count, consistent_T2_T3.
- [ ] **5.5** Send to supervisors with explicit ask: “feedback on claim scope before committee slides.”

**Deliverable:** Email-ready package in `results_committee_case/` + `docs/COMMITTEE_BRIEF.md`.

---

## Week 2 — committee slide build (start after supervisor feedback)

### Slide deck structure (10–12 slides)

| # | Slide | Content source |
|---|---|---|
| 1 | Title + one-line thesis | COMMITTEE_BRIEF §thesis sentence |
| 2 | Gaga hypothesis (modest) | remote motors as motivation, not claim |
| 3 | Scientific question | contribution redistribution / DoF access proxy |
| 4 | Data & design | T1/T2/T3, R1/R2, Group 4 curvilinear, N=2 case |
| 5 | Pipeline diagram | README flow, 1 figure |
| 6 | jcvPCA in plain language | reference A, project B, link RSS |
| 7 | What we can measure / cannot | limits box |
| 8 | Results 671 | heatmap + 3 bullets |
| 9 | Results 252 | heatmap + 3 bullets |
| 10 | Trunk + ROM findings | before/after table |
| 11 | NV & stability | bootstrap/threshold sweep |
| 12 | Trajectory + ask | methods note, expand N, optional RQA later |

- [ ] **6.1** Draft slides from COMMITTEE_BRIEF (don't design before supervisor feedback).
- [ ] **6.2** Prepare **backup slide**: “what if committee asks about timing?” → JsvCRP deferred, why.
- [ ] **6.3** Prepare **backup slide**: trunk/pelvis anatomy in Motive skeleton.
- [ ] **6.4** Rehearse 10-min + 20-min versions.

---

## Publication track (parallel, not blocking Week 1)

| Phase | When | Output |
|---|---|---|
| P1 Methods note outline | Week 2–3 | 1-page outline + target journal list |
| P2 Synthetic validation | Week 2–3 | reproduce paper-logic example |
| P3 Worked example + repo hygiene | Week 3–4 | public/minimal runnable example |
| P4 Draft Application Note | Month 2 | submit methods note |
| P5 Findings paper | After more N + NV | separate empirical paper |

**Methods note title (working):** *Reference-anchored jcvPCA for whole-body optical MoCap: a reproducible pipeline with natural-variability reporting for improvisational movement.*

**Findings paper (later):** Gaga case study as illustration, not headline.

---

## Checklist — “done” for supervisor share (end Week 1)

- [ ] Trunk links evaluated and included or explicitly excluded with reason
- [ ] ROM/RMS covariate table exists
- [ ] T1-underused link analysis exists
- [ ] Contribution distribution metrics (entropy/Gini or top-1 share) exist
- [ ] Bootstrap + threshold sweep + PCA stability reported
- [ ] T2 vs T3 consistency noted
- [ ] COMMITTEE_BRIEF.md + SUPERVISOR_ONE_PAGER.md written
- [ ] Claim language reviewed (no dormant motors, no timing, no causality)
- [ ] Figures regenerated for final config

---

## Risk register (know these going in)

| Risk | Mitigation |
|---|---|
| Trunk links noisy | QC gate; report with/without trunk |
| Bootstrap insufficient (single ex) | Say so; lean on R1–R2 + threshold stability |
| 671 T3 marker-set confound | Restrict shared links; caveat in every 671 T3 slide |
| Supervisors want “Gaga effect” language | COMMITTEE_BRIEF limits section pre-written |
| Euler/BVH arrives mid-week | Only run if Day 1–2 complete; else defer to Week 3 |

---

## File / folder layout

```
docs/
  COMMITTEE_BRIEF.md              ← main narrative (Week 1 Fri)
  SUPERVISOR_ONE_PAGER.md         ← email attachment
  WEEK_PLAN_COMMITTEE_AND_PUBLISH.md  ← this file
results_committee_case/
  baseline/                       ← Day 1 snapshot (pre-trunk)
  with_trunk/                     ← Day 2 reruns
  amplitude_vs_organization/      ← Day 3
  nv_and_stability/               ← Day 4
  figures/                        ← final heatmaps
  FINDINGS_SUMMARY.csv            ← Day 5 master table
```

---

## Daily time budget (realistic)

| Day | Focus | ~Hours |
|---|---|---|
| Mon | Audit + draft brief | 3–4 |
| Tue | Trunk + rerun | 4–6 |
| Wed | ROM + underused analysis | 4–5 |
| Thu | NV bootstrap + stability | 4–5 |
| Fri | Write-up + supervisor send | 3–4 |

**Total:** ~20–24 h focused work. If blocked on compute, prioritize Days 3–5 write-up with baseline results rather than perfect bootstrap.

---

## First command to run Monday morning

```bash
mkdir -p results_committee_case/{baseline,with_trunk,amplitude_vs_organization,nv_and_stability,figures}
cp results_exploration_671_252/decision_log.md results_committee_case/baseline/
# Then snapshot winner run folders (671 ex11 pooled, 252 ex10_14 pooled)
```

---

## Success criteria

**Supervisors (end Week 1):** They can answer: What did you build? What changed? What can you claim? What's next?

**Committee (Week 2):** You can present in 15 minutes without overstating, with figures that trace claim → metric → limit.

**Publication (later):** Methods note has synthetic validation + worked example; Gaga case is appendix/use-case, not the method's proof.
