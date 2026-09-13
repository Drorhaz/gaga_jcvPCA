# Robustness framework — Step 4b (v5 + extensions)

Tests stability of the primary `ex09_13_contiguous` **pooled** result under perturbations — not alternate exercise windows.

## Axes (`robustness.csv`)

| Axis | Primary | Perturbation | Metric |
|---|---|---|---|
| **k_grid** | T1 pooled A; m from 80% EVR | Fixed k ∈ [4…10] | top-5 overlap vs primary at `primary_m` |
| **repetition_mode** | pooled T1 vs T2/T3 | single T1 R1 vs T2/T3 R1 | `top5_overlap` (= `pooled_vs_r1_overlap`) |
| **qc_drop** | full feasible link set | drop `include_with_caution` links only | top-5 overlap via sensitivity_analysis |

### Repetition diagnostics (on `repetition_mode` rows only)

| Column | Meaning |
|---|---|
| `pooled_vs_r1_overlap` | Same as `top5_overlap` — pooled vs R1-only longitudinal |
| `pooled_vs_r2_overlap` | pooled vs R2-only longitudinal top-5 overlap |
| `longitudinal_r1_vs_r2_overlap` | R1-only vs R2-only longitudinal top-5 overlap |
| `pooled_vs_r1_overlap_p50` / `_p60` | Same as above, top-5 from PCs 1…`p_functional_50` / `p_functional_60` (T1 EVR from pooled fit) |
| `pooled_vs_r2_overlap_p50` / `_p60` | R2-only band overlaps (same PC cutoffs) |

Diagnostics inform interpretation; they **do not** change `robustness_label`.

## Functional PC bands (`functional_pc_bands.csv`)

Separate table per participant × comparison:

| Field | Meaning |
|---|---|
| `p_functional_50` / `p_functional_60` | PCs needed for 50% / 60% T1 cumulative EVR |
| `overlap_all_vs_p50` / `overlap_all_vs_p60` | Top-5 stability: all PCs vs each EVR band |
| `overlap_p50_vs_p60` | Agreement between 50% and 60% band rankings |
| `top5_p_functional_50`, `top5_p_functional_60`, … | Ranked link lists per band |

Label PCs `p_functional_50+1 … selected_m` as **secondary** in committee docs (not "null").
Note: per-run `functional_space_results.csv` still uses config `sensitivity_p=2`; this table uses EVR bands only.

## Heuristic labels (not p-values)

- **top5_overlap** ≥ 0.60 (≥3/5 links) → stable axis
- **functional_chain_retained** — dominant arm/trunk/leg chains keep representation + sign agreement on overlap
- **robustness_label** (per comparison, on qc_drop row): `stable` if k-grid median, pooled↔R1, and qc-drop all pass; `partial` if some pass; `unstable` otherwise

## Removed (v5)

EVR threshold sweep (subsumed by k-grid), basis-similarity cosine, bootstrap CIs as stability gates.

See `docs/MASTER_EXECUTION_PLAN.md` Step 4b for full spec.
