# Run summary — 790_ex09_13_contiguous_single

- Participant: **790** (participant-specific, N-of-1)
- Selection: `790_ex09_13_contiguous` — 22 links included
- Exercises (authoritative exercise_id): [9, 10, 11, 12, 13]
- Variance threshold: 0.8; filter cutoff 10.0 Hz (order 4)
- Marker-gap policy: **on** (`/Users/drorhazan/Desktop/gaga_psilo/projects/gaga_jcvpca/results_committee_case/step03_trunk_extension/marker_gap_link_removals_ex09_13.csv`) — session-scoped exclusions listed per comparison when applicable.

## Comparisons
### 790_T1_vs_T2 — Longitudinal change
- 790_T1_P1_R1 (reference A) vs 790_T2_P1_R1 (B)
- selected_m = 8 at variance_threshold 0.8
- 22 links analyzed; 0 excluded.
- Largest contribution changes (mean |ΔJcvPCA|): RShoulder_to_RUArm (0.209), LThigh_to_LShin (0.155), LFArm_to_LHand (0.154), LUArm_to_LFArm (0.151), 790_to_LThigh (0.122)

### 790_T1_vs_T3 — Longitudinal change
- 790_T1_P1_R1 (reference A) vs 790_T3_P1_R1 (B)
- selected_m = 8 at variance_threshold 0.8
- 20 links analyzed; 2 excluded.
- Note: 2 link(s) excluded by marker-gap policy before shared-link restriction.
- Largest contribution changes (mean |ΔJcvPCA|): RUArm_to_RFArm (0.180), LShoulder_to_LUArm (0.166), LUArm_to_LFArm (0.135), LFArm_to_LHand (0.128), LThigh_to_LShin (0.109)
- Excluded (marker-gap policy): Spine2_to_Spine3 — marker_gap_policy: T3_R1 — Supporting marker `790:RIPS` has 19.2% of ex09-13 window in large gaps (>0.5 s, 2 runs); Motive likely interpolated bone motion.; Ab_to_Spine2 — marker_gap_policy: T3_R1 — Supporting marker `790:RIPS` has 19.2% of ex09-13 window in large gaps (>0.5 s, 2 runs); Motive likely interpolated bone motion.

### 790_T1_R1_vs_R2 — Natural variability (R1 vs R2)
- 790_T1_P1_R1 (reference A) vs 790_T1_P1_R2 (B)
- selected_m = 7 at variance_threshold 0.8
- 20 links analyzed; 2 excluded.
- Note: 2 link(s) excluded by marker-gap policy before shared-link restriction.
- Largest contribution changes (mean |ΔJcvPCA|): LShoulder_to_LUArm (0.238), RShoulder_to_RUArm (0.165), LUArm_to_LFArm (0.158), LFArm_to_LHand (0.151), LThigh_to_LShin (0.147)
- Excluded (marker-gap policy): RUArm_to_RFArm — marker_gap_policy: T1_R2 — Supporting marker `790:RHLE` has 99.4% of ex09-13 window in large gaps (>0.5 s, 3 runs); Motive likely interpolated bone motion.; RFArm_to_RHand — marker_gap_policy: T1_R2 — Supporting marker `790:RHLE` has 99.4% of ex09-13 window in large gaps (>0.5 s, 3 runs); Motive likely interpolated bone motion.

## Statistical validation
Not run for this analysis (optional stage).

---
JcvPCA reports how each body link's contribution to the shared movement-variance structure differs between the two matched datasets. Values are descriptive; see the validation section for evidence strength.