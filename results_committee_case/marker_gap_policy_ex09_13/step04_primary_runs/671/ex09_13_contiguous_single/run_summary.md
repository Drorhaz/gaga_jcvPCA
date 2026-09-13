# Run summary — 671_ex09_13_contiguous_single

- Participant: **671** (participant-specific, N-of-1)
- Selection: `671_ex09_13_contiguous` — 18 links included
- Exercises (authoritative exercise_id): [9, 10, 11, 12, 13]
- Variance threshold: 0.8; filter cutoff 10.0 Hz (order 4)
- Marker-gap policy: **on** (`/Users/drorhazan/Desktop/gaga_psilo/projects/gaga_jcvpca/results_committee_case/step03_trunk_extension/marker_gap_link_removals_ex09_13.csv`) — session-scoped exclusions listed per comparison when applicable.

## Comparability notes
- **671**: Marker-set prefix differs across timepoints (['671', 'T3']). Cross-timepoint comparisons restricted to shared valid links; interpret with care.

## Comparisons
### 671_T1_vs_T2 — Longitudinal change
- 671_T1_P1_R1 (reference A) vs 671_T2_P1_R1 (B)
- selected_m = 8 at variance_threshold 0.8
- 18 links analyzed; 0 excluded.
- Largest contribution changes (mean |ΔJcvPCA|): LUArm_to_LFArm (0.286), RUArm_to_RFArm (0.242), LFArm_to_LHand (0.230), LThigh_to_LShin (0.163), RFArm_to_RHand (0.154)

### 671_T1_vs_T3 — Longitudinal change
- 671_T1_P1_R1 (reference A) vs 671_T3_P1_R1 (B)
- selected_m = 8 at variance_threshold 0.8
- 17 links analyzed; 1 excluded.
- Note: 1 link(s) excluded from this comparison; analysis restricted to the shared valid link intersection (17 links).
- Largest contribution changes (mean |ΔJcvPCA|): RFArm_to_RHand (0.272), RUArm_to_RFArm (0.261), LFArm_to_LHand (0.186), LUArm_to_LFArm (0.175), 671_to_LThigh (0.124)
- Excluded (matrix / rotvec QC): Ab_to_Chest — features missing in dataset B

### 671_T1_R1_vs_R2 — Natural variability (R1 vs R2)
- 671_T1_P1_R1 (reference A) vs 671_T1_P1_R2 (B)
- selected_m = 8 at variance_threshold 0.8
- 18 links analyzed; 0 excluded.
- Largest contribution changes (mean |ΔJcvPCA|): LUArm_to_LFArm (0.254), RFArm_to_RHand (0.204), RUArm_to_RFArm (0.179), RShoulder_to_RUArm (0.127), LShoulder_to_LUArm (0.106)

## Statistical validation
Not run for this analysis (optional stage).

---
JcvPCA reports how each body link's contribution to the shared movement-variance structure differs between the two matched datasets. Values are descriptive; see the validation section for evidence strength.