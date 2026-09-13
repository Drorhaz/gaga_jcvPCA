# Run summary — 252_ex09_13_contiguous_single

- Participant: **252** (participant-specific, N-of-1)
- Selection: `252_ex09_13_contiguous` — 22 links included
- Exercises (authoritative exercise_id): [9, 10, 11, 12, 13]
- Variance threshold: 0.8; filter cutoff 10.0 Hz (order 4)
- Marker-gap policy: **on** (`/Users/drorhazan/Desktop/gaga_psilo/projects/gaga_jcvpca/results_committee_case/step03_trunk_extension/marker_gap_link_removals_ex09_13.csv`) — session-scoped exclusions listed per comparison when applicable.

## Comparisons
### 252_T1_vs_T2 — Longitudinal change
- 252_T1_P1_R1 (reference A) vs 252_T2_P1_R1 (B)
- selected_m = 10 at variance_threshold 0.8
- 22 links analyzed; 0 excluded.
- Largest contribution changes (mean |ΔJcvPCA|): RShoulder_to_RUArm (0.189), LShoulder_to_LUArm (0.127), LFArm_to_LHand (0.125), LUArm_to_LFArm (0.122), RUArm_to_RFArm (0.122)

### 252_T1_vs_T3 — Longitudinal change
- 252_T1_P1_R1 (reference A) vs 252_T3_P1_R1 (B)
- selected_m = 10 at variance_threshold 0.8
- 22 links analyzed; 0 excluded.
- Largest contribution changes (mean |ΔJcvPCA|): RThigh_to_RShin (0.202), RUArm_to_RFArm (0.201), LUArm_to_LFArm (0.189), RShoulder_to_RUArm (0.153), LThigh_to_LShin (0.134)

### 252_T1_R1_vs_R2 — Natural variability (R1 vs R2)
- 252_T1_P1_R1 (reference A) vs 252_T1_P1_R2 (B)
- selected_m = 9 at variance_threshold 0.8
- 20 links analyzed; 2 excluded.
- Note: 2 link(s) excluded by marker-gap policy before shared-link restriction.
- Largest contribution changes (mean |ΔJcvPCA|): RShoulder_to_RUArm (0.188), RUArm_to_RFArm (0.169), LUArm_to_LFArm (0.146), LFArm_to_LHand (0.120), LShoulder_to_LUArm (0.088)
- Excluded (marker-gap policy): LThigh_to_LShin — marker_gap_policy: T1_R2 — Supporting marker `252:LFAX` has 13.2% of ex09-13 window in large gaps (>0.5 s, 2 runs); Motive likely interpolated bone motion.; LShin_to_LFoot — marker_gap_policy: T1_R2 — Supporting marker `252:LFAX` has 13.2% of ex09-13 window in large gaps (>0.5 s, 2 runs); Motive likely interpolated bone motion.

## Statistical validation
Not run for this analysis (optional stage).

---
JcvPCA reports how each body link's contribution to the shared movement-variance structure differs between the two matched datasets. Values are descriptive; see the validation section for evidence strength.