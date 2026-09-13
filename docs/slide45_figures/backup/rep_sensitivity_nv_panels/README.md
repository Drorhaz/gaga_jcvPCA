# Repetition sensitivity — NV exceedance (2×2 per participant)

**Source:** `marker_gap_policy_ex09_13` · `ex09_13_contiguous`

## Layout (4 figures)

One PNG per participant; **2×2 panels**:

| | R1-matched | R2-matched |
|---|---|---|
| **T2** | T1_R1 vs T2_R1 | T1_R2 vs T2_R2 |
| **T3** | T1_R1 vs T3_R1 | T1_R2 vs T3_R2 |

**NV floor (all panels):** `T1_R1 vs T1_R2` — red bar

**Values:** EVR-weighted signed sum across retained PCs (`NV_EVIDENCE` + on-the-fly R2–R2 comps)

- **★** same-sign exceed (`|long|>|nv|`, same sign)
- **†** magnitude exceed only
- Links sorted with ★ first in each panel

Companion CSV: `{pid}_rep_sensitivity_nv_flags.csv`
