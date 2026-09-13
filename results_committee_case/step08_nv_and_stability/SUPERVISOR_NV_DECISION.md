# Supervisor NV decision — Step 8 (v6 spec lock = Step 8v6 Phase 0)

**Status:** PROVISIONAL DEFAULTS adopted for implementation (2026-07-18) — **pending supervisor confirmation** at the meeting. Each default is cheap to change (config/constant), so code was built against these so results exist to react to.

## Phase 0 spec locks (v6)

| Field | Provisional decision | Change cost if overridden |
|---|---|---|
| A2 gate | **S2** signed tier (magnitude exceed + reference-direction stable) | low — flag |
| A2 estimand | **single-rep** `long_signed_single` (`T1_R1 vs T{k}_R1`) | low |
| Sign-consistency | **reference-direction stability** (`sign(long_signed_single) == sign(long_signed_single_rev)`) | low |
| Signed per-link aggregation | **EVR-weighted signed sum** across retained PCs (fallback: plain signed sum) | low — `weighted` flag in `nv_profile.py` |
| `ε_sign` | **`1e-6`** (`nv_floor_unstable` below this) | trivial constant |
| S1 in committee brief? | **report separately, not counted as A2** | doc-only |
| S3 stratum K | **K = 2** exercises | trivial constant |
| Backward-compat columns | keep deprecated `matched_abs_ratio` / `exceeds_observed_variability` one release | already kept |

## Adopted wording for committee brief

| Field | Decision |
|---|---|
| NV reference label | observed repetition variability / reference range (descriptive) |
| Exceed-floor rule | signed tier **S2** primary; abs matched ratio > 1 = deprecated secondary |
| Basis / coverage qualifier | pair each S2 with coverage band; state "reweighting within T1 subspace"; show single-rep signed effect next to pooled headline |
| Coverage-limited pairs | T3 for 671 / 252 / 651 (see `coverage.csv`) |
| Protocol-openness language | descriptive only; participant-specific, no consensus (soften) |
| Interpretive claims approved | _pending supervisor — candidate S3 links listed in `NV_PROFILE.csv`_ |

## Sign-off

| Name | Date | Notes |
|---|---|---|
| | | |
