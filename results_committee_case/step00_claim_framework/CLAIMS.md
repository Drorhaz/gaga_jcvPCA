# Claims framework — committee case study (v6)

**Status:** locked for execution (Step 0); A2 machinery updated to signed NV profile (v6)  
**Effective:** 2026-07-17  
**Scope:** Four within-participant case studies (671, 252, 651, 790); primary window `ex09_13_contiguous` pooled.

---

## Gaga bridge phrase (use this style)

> *Gaga practice motivates the hypothesis of broader functional access to underused movement degrees of freedom. We operationalize this as change in the relative contribution of body links to whole-body movement-variance structure, measured by reference-anchored jcvPCA.*

---

## Allowed claims (operational)

| ID | Claim | Minimum evidence |
|---|---|---|
| A1 | A link or region's **relative contribution** to shared movement-variance structure changed between T1 (reference) and T2 or T3 | Step 4 link/region tables |
| A2 | That change **exceeds observed T1 R1–R2 variability** for the same link, **consistently in direction** — signed tier **S2** (not abs ratio alone, not significance) | Step 8 Tier A: `\|long_signed\| > \|nv_signed\|` on `T1_R1 vs T{2,3}_R1` vs `T1_R1 vs T1_R2`, sign robust to R1/R2 anchor |
| A3 | Pattern is **consistent with** broader participation of previously low-contributing links (**reweighting within T1's retained subspace**) | S2 + adequate coverage + Step 5 amplitude check + Step 4b robustness label + supervisor sign-off (tier S3) |
| A4 | **Contribution redistribution** occurred (some links ↑, some ↓ relative contribution) | Step 4 + Step 7 distribution metrics |

---

## Forbidden claims

- Dormant or remote motors were activated or proven.
- Gaga practice or psilocybin **caused** the observed change.
- Improved timing, synchronization, or reduced movement segmentation (no dynamic metrics in scope).
- Richer adaptable repertoire vs noise without structured variability evidence.
- **Population-level** or cross-participant treatment effect (four separate N-of-1 cases only).
- Anatomical joint-angle statements (flexion/abduction) or muscle-use statements — features are **relative link rotvecs**, not ISB/Euler angles.
- Statistical significance, p-values, confidence intervals, percentile thresholds, or causal drug language while timepoints remain blinded.

---

## Signed NV profile tiers (v6 — A2 machinery)

Per link × comparison, anchored on a single T1 take. Each signed scalar = **EVR-weighted signed sum** of `JcvPCA_link` across retained PCs (never mean-\|Δ\|, never cross-link):
- `long_signed` = `T1_R1 vs T{2,3}_R1` (A2 estimand) · `nv_signed` = `T1_R1 vs T1_R2` (floor) · `long_signed_rev` = `T1_R2 vs T{2,3}_R1` (direction-stability probe)

| Tier | Rule | Committee use |
|---|---|---|
| **S0** | `\|long_signed\| ≤ \|nv_signed\|` | within observed T1 repetition spread |
| **S1** | `\|long_signed\| > \|nv_signed\|`, direction **not** reference-stable | magnitude exceed only — reported, **not** A2 |
| **S2** | `\|long_signed\| > \|nv_signed\|` **and** `sign(long_signed) = sign(long_signed_rev)` | **A2 minimum** — reference-direction-stable exceed |
| **S3** | S2 + coverage adequate + Step 5 organization + Step 4b robustness | candidate A3 (interpretive) with supervisor |

- **Sign-consistency = reference-direction stability** (sign invariant to the arbitrary R1/R2 anchor), **not** "same sign as the R1→R2 rep difference."
- `ε_sign` (default `1e-6`): `\|nv_signed\| < ε_sign` → `nv_floor_unstable`; do not rely on ratio alone.
- **Legacy (deprecated one release):** `matched_abs_ratio > 1` / `exceeds_observed_variability` — magnitude-only, secondary.

### Known footing asymmetry in the S3 organization gate (documented, not changed)

S2 uses the **matched single-rep signed** floor. The Step-5 `organization` label that gates S3
uses Step 5's own `exceeds_nv`, which is the **pooled** longitudinal effect over the single-rep
floor on a mean-\|Δ\| metric. A link can therefore be flat-ROM and S2 yet be labelled
`within_variability` by Step 5 and so be denied S3.

The governing S3 definition is **unchanged** pending supervisor decision. Both variants are
emitted per link in `NV_PROFILE.csv`:

| Column | Gate | Status |
|---|---|---|
| `step5_organization` → `nv_profile_tier` | Step-5 `classification == "organization"` (flat ROM **and** pooled NV exceed) | **governing** |
| `step5_rom_flat` → `nv_profile_tier_romflat` | flat ROM alone; pooled NV test dropped as redundant with S2 | sensitivity only |

---

## Claim tiers (v6 — map to outputs)

| Tier | Label | Meaning | Who sets |
|---|---|---|---|
| **A** | Descriptive fact | Metric value recorded (e.g. `JcvPCA_link`, longitudinal signed Δ, observed NV signed Δ, **signed NV tier S0–S3**) | Pipeline (Steps 4, 8) |
| **Interpretive** | Consistent with hypothesis | Broader participation / redistribution language | Requires **S2** + adequate **reference-subspace coverage** + **robustness label** (Step 4b) + amplitude check (Step 5) + supervisor approval |

**Removed (v5):** bootstrap NV floor, bootstrap CI, combined tiers B/C/D — not supported at this N.  
**Updated (v6):** A2 = signed tier S2 (was abs matched ratio > 1); abs ratio is deprecated secondary.

---

## Interpretation guardrails (v6)

- **Reference-basis asymmetry:** jcvPCA projects B into T1's retained subspace, so S2 evidences **reweighting within T1's existing coordination subspace** — narrower than "access to new degrees of freedom." Novel DOF outside T1's subspace appear as **low coverage**, not redistribution; coverage-limited S2 is ambiguous. Every S2 in committee text is paired with its coverage band.
- **Headline vs validated effect:** report the **single-rep signed** S2 effect next to the pooled longitudinal headline (different bases; the number shown must be the one that passed S2).
- **A2 floor is a single rep-pair** (n=1, no margin); "effective units = reps × exercises" applies to descriptive per-exercise/openness reads, **not** the A2 gate.

Pooled longitudinal effect is the **descriptive headline** only; it is **not** divided by a mismatched single-rep floor (a pooled-rep NV reference is not constructible with 2 reps).

Step 11 committee language **must not** use interpretive claims unless traceable in `FINDINGS_SUMMARY.csv` and `SUPERVISOR_NV_DECISION.md`.

---

## Evidence stack (read in order)

1. **Coverage gate** — reference-subspace coverage read first; poor coverage → link-level redistribution interpreted cautiously for that pair.
2. **Layer 1 — observed repetition variability** — T1 R1↔R2 across genuinely separate takes; the **only** input to exceed-floor logic.
3. **Layer 2 — temporal-subsample sensitivity** — descriptive robustness only; **firewalled** from the floor (optional, Step 8h Layer 2).
4. **Robustness label** — k-grid, repetition-mode, QC-drop stability (Step 4b).

---

## Primary analysis lock

- **Window:** `ex09_13_contiguous` — exercise_ids 9, 10, 11, 12, 13 combined; **pooled** repetitions for longitudinal comparisons.
- **Participants:** 671, 252, 651, 790 (each analyzed separately).
- **Reference:** T1 always side A.
- **Observed NV:** T1 R1 vs T1 R2 (single-rep footing); never pooled across repetitions for the floor.
- **Feature stream:** Relative link rotation vectors (primary); BVH/Euler is optional parallel track only (Step 2-FS, Tier 3).

---

## Supervisor sign-off

| Field | Value |
|---|---|
| Claim scope accepted? | _Pending supervisor meeting_ |
| NV wording adopted for committee | _Pending `SUPERVISOR_NV_DECISION.md` (after Step 8)_ |
| Date / notes | |

Proceeding to Step 2+ with **documented limits** is acceptable if supervisors have not yet met; committee slides must reflect the adopted tier table above.
