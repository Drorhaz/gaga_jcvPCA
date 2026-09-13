# Run summary — 651_ex09_13_contiguous_single

- Participant: **651** (participant-specific, N-of-1)
- Selection: `651_ex09_13_contiguous` — 18 links included
- Exercises (authoritative exercise_id): [9, 10, 11, 12, 13]
- Variance threshold: 0.8; filter cutoff 10.0 Hz (order 4)
- Marker-gap policy: **on** (`/Users/drorhazan/Desktop/gaga_psilo/projects/gaga_jcvpca/results_committee_case/step03_trunk_extension/marker_gap_link_removals_ex09_13.csv`) — session-scoped exclusions listed per comparison when applicable.

## Comparisons
### 651_T1_vs_T2 — Longitudinal change
- 651_T1_P1_R1 (reference A) vs 651_T2_P1_R1 (B)
- selected_m = 6 at variance_threshold 0.8
- 14 links analyzed; 4 excluded.
- Note: 4 link(s) excluded from this comparison; analysis restricted to the shared valid link intersection (14 links).
- Largest contribution changes (mean |ΔJcvPCA|): RUArm_to_RFArm (0.253), LUArm_to_LFArm (0.217), LFArm_to_LHand (0.184), RFArm_to_RHand (0.169), RShoulder_to_RUArm (0.146)
- Excluded (matrix / rotvec QC): 651_to_Ab — features missing in dataset B; 651_to_LThigh — features missing in dataset B; 651_to_RThigh — features missing in dataset B; Ab_to_Chest — features missing in dataset B

### 651_T1_vs_T3 — Longitudinal change
- 651_T1_P1_R1 (reference A) vs 651_T3_P1_R1 (B)
- selected_m = 6 at variance_threshold 0.8
- 14 links analyzed; 4 excluded.
- Note: 4 link(s) excluded from this comparison; analysis restricted to the shared valid link intersection (14 links).
- Largest contribution changes (mean |ΔJcvPCA|): RUArm_to_RFArm (0.242), LUArm_to_LFArm (0.185), RFArm_to_RHand (0.163), LFArm_to_LHand (0.158), RShoulder_to_RUArm (0.100)
- Excluded (matrix / rotvec QC): 651_to_Ab — features missing in dataset B; 651_to_LThigh — features missing in dataset B; 651_to_RThigh — features missing in dataset B; Ab_to_Chest — features missing in dataset B

### 651_T1_R1_vs_R2 — Natural variability (R1 vs R2)
- 651_T1_P1_R1 (reference A) vs 651_T1_P1_R2 (B)
- selected_m = 6 at variance_threshold 0.8
- 13 links analyzed; 5 excluded.
- Note: 5 link(s) excluded by marker-gap policy before shared-link restriction.
- Largest contribution changes (mean |ΔJcvPCA|): RUArm_to_RFArm (0.191), LFArm_to_LHand (0.154), LUArm_to_LFArm (0.135), LShoulder_to_LUArm (0.084), RThigh_to_RShin (0.076)
- Excluded (marker-gap policy): Ab_to_Chest — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.; Chest_to_LShoulder — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.; Neck_to_Head — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.; Chest_to_Neck — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.; Chest_to_RShoulder — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.

## Statistical validation
Not run for this analysis (optional stage).

---
JcvPCA reports how each body link's contribution to the shared movement-variance structure differs between the two matched datasets. Values are descriptive; see the validation section for evidence strength.