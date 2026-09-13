# Limits — measurement honesty

**Step 0 deliverable.** Adopt in all committee and methods text.

---

## What jcvPCA measures

- **Contribution to shared movement-variance structure** (link/region relative weights in reference-anchored PCA space).
- It does **not** alone establish that a joint “moved more” — amplitude must be checked separately (Step 5 ROM/RMS).
- **Reference-basis asymmetry:** B (T2/T3) is projected into A's (T1) retained subspace. Results describe **redistribution/reweighting within T1's existing coordination subspace**, not access to *new* degrees of freedom outside it (those surface as **low coverage**, not redistribution). A clean signed exceed (**S2**) is therefore a *narrower* claim than "broader access to new DOF"; a coverage-limited S2 is ambiguous.

---

## Features

- Input = **parent→child relative rotation vectors** (`rx`, `ry`, `rz`) from Motive skeleton quaternions.
- These are **not** ISB/Euler anatomical joint angles; do not use flexion/extension language in primary claims.
- Optional BVH/Euler stream (Step 2-FS) may support interpretability only; primary claims stay on rotvecs unless supervisors adopt otherwise.

---

## Reference-subspace coverage (validity gate — read first)

- For every comparison, report how well dataset B is represented in A's retained `m`-dim subspace (`coverage_abs`, `coverage_rel`).
- Where B is poorly represented in A's retained subspace, link-level JcvPCA redistribution is interpreted **cautiously** for that pair (paper's "entirely different strategy" caveat).
- Graded **coverage warning** bands (adequate / limited / severe) are heuristic labels, not hard cutoffs.

---

## Natural variability — two firewalled layers (v5)

### Layer 1 — observed same-condition repetition variability (only floor input)

- Estimated from genuinely separate takes: per-exercise `T1 R1 vs R2` (primary) + full `ex09_13` reference row.
- Only **two repetitions** exist → NV is a **descriptive reference range**, not a significance threshold and **not** pure measurement noise (it necessarily contains genuine improv movement differences).
- **Matched single-rep footing** (primary exceed-floor comparison): `(T1_R1 vs T2/T3_R1)` vs `(T1_R1 vs T1_R2)` — numerator and denominator on identical single-rep footing, same T1 basis.
- **Signed exceed (v6, primary):** the exceed decision is tier **S2** — `|long_signed| > |nv_signed|` on the same link **and** direction robust to the arbitrary R1/R2 reference-take choice. Signed per-link value = **EVR-weighted signed sum** across retained PCs; **never** mean-\|Δ\| (discards sign) and **never** averaged across links. Abs matched ratio > 1 is a deprecated secondary.
- **A2 floor rests on one rep-pair** per link (n=1, no margin); the "reps × exercises" effective-information count applies to the descriptive per-exercise/openness reads, **not** to the A2 gate.
- NV summaries at n≈3–5 exercise units: individual per-exercise values + median + range (MAD caveated). **No p90/p95.**

### Layer 2 — temporal-subsample sensitivity (descriptive only, firewalled)

- Contiguous block-resampling stability under fixed `m`.
- Reports **subsample spread** — never feeds the exceed-floor logic.
- Optional after Layer 1 is clean (Step 8h Layer 2).

### Removed (v5)

- Frame-resampled "NV floor," bootstrap CI as inference, p90/p95 thresholds, combined tiers B/C/D.

**Supervisor meeting** (after Step 8) decides committee wording via `SUPERVISOR_NV_DECISION.md`. Honest default: "exceeds observed R1–R2 variability (descriptive only)."

---

## Effective information

- Independent units = **repetitions × exercises**, **never frames**.
- More frames stabilize a point estimate but add zero independent repetitions.
- The **A2 exceed gate is a single rep-pair** comparison per link; more exercises/reps enrich descriptive reads but add no margin to the pooled A2 floor.
- Autocorrelation is measured once to justify block length (Layer 2); no formal multivariate effective-N estimator.

---

## Vocabulary lock

Use in all outputs:

| Use | Never use (for N-of-1 results) |
|---|---|
| observed repetition variability / **reference range** | confidence interval / CI |
| **subsample spread** | significant / significance |
| **coverage warning** | p-value |
| **robustness label** | percentile threshold (p90, p95) |

---

## Design limits

- **Within-participant only** — four N-of-1 case studies; no cohort statistics.
- **Improvisational movement** — high within-condition variability; exercises are not identical across R1/R2 or timepoints.
- **Instruction vs lasting learning** cannot be separated with current T2/T3 design.
- **Blinded timepoints** — report contribution-structure differences across timepoints; avoid drug/causal language until unblinding protocol allows.

---

## Known data confounds (see Step 1 `KNOWN_CONFOUNDS.md`)

- Trunk links were excluded in pre-trunk exploration (Step 3 addresses).
- Participant 671: marker-set prefix differs at T3.
- Two skeleton setups (671-style vs 252-style); cross-participant link comparison requires Step 2 comparability flags.

---

## Out of scope (this plan)

- JsvCRP, phase, RQA, timing/synchronization metrics.
- Population inference, permutation p-values at current N.
- Dormant motor / muscle activation claims.
- Bootstrap NV floor / bootstrap CI as claim machinery.
