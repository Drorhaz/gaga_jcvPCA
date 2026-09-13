# Functional / null bands — pooled vs NV (8 figures)

**Source:** `marker_gap_policy_ex09_13` · `ex09_13_contiguous_pooled`

## Layout

**8 figures** = 4 participants × 2 band types.

Each figure has **2 panels** (side by side):
- **Left (1A / 2A):** T1 vs T3 pooled overlapped with NV (T1_R1 vs T1_R2)
- **Right (1B / 2B):** T1 vs T2 pooled overlapped with NV

| Figure | Band |
|--------|------|
| `{pid}_functional_60pct_T2_T3_vs_NV.png` | PC1…`p_functional_60` (60% T1 EVR) |
| `{pid}_null_40pct_T2_T3_vs_NV.png` | PC(`p60`+1)…`selected_m` (~40% tail) |

- **Values:** EVR-weighted signed sum of `JcvPCA_link` across PCs in band
- **Blue:** pooled longitudinal · **Red:** NV floor (semi-transparent overlap)
- **★ top:** same-sign exceed (`|long|>|nv|` same sign), sorted first
- **Grey hatch:** QC / marker-gap excluded

## Files

- `671_functional_60pct_T2_T3_vs_NV.png`
- `671_null_40pct_T2_T3_vs_NV.png`
- `252_functional_60pct_T2_T3_vs_NV.png`
- `252_null_40pct_T2_T3_vs_NV.png`
- `651_functional_60pct_T2_T3_vs_NV.png`
- `651_null_40pct_T2_T3_vs_NV.png`
- `790_functional_60pct_T2_T3_vs_NV.png`
- `790_null_40pct_T2_T3_vs_NV.png`
