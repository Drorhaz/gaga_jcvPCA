# Signed NV profile — implementation spec

**Status:** planned (v6)  
**Canonical plan:** [`docs/MASTER_EXECUTION_PLAN.md`](MASTER_EXECUTION_PLAN.md) — **v6 decisions**, **Step 8**, **Step 8h**, **Step 8v6 roadmap**  
**MVP status:** abs-only Step 8h outputs exist in `results_committee_case/step08_nv_and_stability/` (pre-v6).

This file is a **working spec** kept in sync with the master plan. When they diverge, the master plan wins.

---

## Summary of v6 changes

1. **Signed per-link NV** — direction matters; per-link value = **EVR-weighted signed sum** of `JcvPCA_link` across retained PCs (never mean-\|Δ\|, never cross-link averaging).
2. **A2 gate = S2** — magnitude exceed (`|long_signed| > |nv_signed|`) **plus reference-direction stability** (`sign(long_signed)` invariant to the arbitrary R1/R2 anchor), not abs ratio > 1 alone.
3. **S1** = magnitude exceed but direction **not** reference-stable — report, do not count as A2.
4. **Same-movement rule** — per-exercise stratum only with per-exercise longitudinal on that exercise.
5. **LOO / ex11_13 / ex13/ex09 openness** — diagnostics only; do not confirm pooled `ex09_13` A2.
6. **Paper mapping** — Layer 1 = genuine R1↔R2; Layer 2 = within-exercise block spread (firewalled); no imputation as floor.
7. **New outputs:** `NV_PROFILE.csv`, `link_exercise_nv.csv`, `link_exercise_longitudinal.csv`; `NV_EVIDENCE.csv` v2.
8. **Basis caveat** — A2 estimand = single-rep `T1_R1 vs T{k}_R1` (basis = `T1_R1`); the pooled longitudinal headline uses a different basis (pooled T1). S2 evidences **reweighting within T1's retained subspace** (narrower than "new DOF" — novel DOF appear as low coverage). Report the single-rep signed effect next to the pooled headline; pair every S2 with its coverage band.

---

## Implementation phases (see master plan for full checklist)

| Phase | Focus | Est. effort |
|---|---|---|
| 0 | Supervisor spec lock | ~1 h |
| 1 | `nv_profile.py` + tests | ~2 h |
| 2 | `validation.py` | ~1 h |
| 3 | `observed_nv.py` + re-run | ~3 h |
| 4 | Step 5 / avatar downstream | ~2 h |
| 5 | CLAIMS, LIMITS, EXPERIMENTAL_DESIGN, digest | ~2 h |
| 6 | Layer 2 `subsample_stability.py` (optional) | ~3 h |
| 7 | Step 8i injection (methods note, deferred) | later |
| 8 | Steps 6–11 committee package | after NV stable |

**Total implementation (Phases 0–5):** ~1 focused day, not calendar days.

---

## NV_EVIDENCE.csv v2 schema

See master plan Step 8 deliverables. Key columns:

- `nv_signed_t1`, `nv_signed_t1_reverse`, `long_signed_single`, `long_signed_single_rev` (EVR-weighted signed sum across PCs)
- `nv_profile_tier` (S0–S3), `exceeds_signed_consistent`, `sign_reference_stable`, `nv_floor_unstable`
- `matched_abs_ratio`, `magnitude_exceed` (legacy secondary)
- `coverage_*` (unchanged)

---

## Evidence stack (per link)

1. Coverage  
2. S2 signed exceed on single-rep `ex09_13` (magnitude + reference-direction stable) → **A2**  
3. S1 if magnitude exceed but direction not reference-stable  
4. Rep sensitivity (Step 4b)  
5. Per-exercise matched stratum (same movement k)  
6. Step 5 organization  
7. Layer 2 subsample spread (optional, firewalled)

---

## Commands (post-implementation)

```bash
pytest tests/test_nv_profile.py tests/test_validation.py -q
PYTHONPATH=src .venv/bin/python scripts/observed_nv.py
PYTHONPATH=src .venv/bin/python scripts/compute_amplitude_covariate.py
```
