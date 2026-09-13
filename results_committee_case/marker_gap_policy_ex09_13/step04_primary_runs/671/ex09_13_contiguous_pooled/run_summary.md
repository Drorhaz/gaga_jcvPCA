# Run summary — 671_ex09_13_contiguous_pooled

- Participant: **671** (participant-specific, N-of-1)
- Selection: `671_ex09_13_contiguous` — 18 links included
- Exercises (authoritative exercise_id): [9, 10, 11, 12, 13]
- Variance threshold: 0.8; filter cutoff 10.0 Hz (order 4)
- Marker-gap policy: **on** (`/Users/drorhazan/Desktop/gaga_psilo/projects/gaga_jcvpca/results_committee_case/step03_trunk_extension/marker_gap_link_removals_ex09_13.csv`) — session-scoped exclusions listed per comparison when applicable.

## Comparability notes
- **671**: Marker-set prefix differs across timepoints (['671', 'T3']). Cross-timepoint comparisons restricted to shared valid links; interpret with care.

## Comparisons
### 671_T1_vs_T2 — Longitudinal change
- 671_T1_R1+R2 (reference A) vs 671_T2_R1+R2 (B)
- selected_m = 9 at variance_threshold 0.8
- 18 links analyzed; 0 excluded.
- Largest contribution changes (mean |ΔJcvPCA|): LFArm_to_LHand (0.222), LUArm_to_LFArm (0.166), RFArm_to_RHand (0.149), RUArm_to_RFArm (0.132), LThigh_to_LShin (0.126)

### 671_T1_vs_T3 — Longitudinal change
- 671_T1_R1+R2 (reference A) vs 671_T3_R1+R2 (B)
- selected_m = 8 at variance_threshold 0.8
- 15 links analyzed; 3 excluded.
- Note: 1 link(s) excluded from this comparison; analysis restricted to the shared valid link intersection (15 links).
- Note: 2 link(s) excluded by marker-gap policy before shared-link restriction.
- Largest contribution changes (mean |ΔJcvPCA|): LFArm_to_LHand (0.238), RFArm_to_RHand (0.236), LUArm_to_LFArm (0.148), RUArm_to_RFArm (0.131), RShoulder_to_RUArm (0.087)
- Excluded (marker-gap policy): LThigh_to_LShin — marker_gap_policy: T3_R2 — Supporting marker `T3_671:LThighFront` has 99.0% of ex09-13 window in large gaps (>0.5 s, 6 runs); Motive likely interpolated bone motion.; 671_to_LThigh — marker_gap_policy: T3_R2 — Supporting marker `T3_671:LThighFront` has 99.0% of ex09-13 window in large gaps (>0.5 s, 6 runs); Motive likely interpolated bone motion.
- Excluded (matrix / rotvec QC): Ab_to_Chest — features missing in dataset B

### 671_T1_R1_vs_R2 — Natural variability (R1 vs R2)
- 671_T1_P1_R1 (reference A) vs 671_T1_P1_R2 (B)
- selected_m = 8 at variance_threshold 0.8
- 18 links analyzed; 0 excluded.
- Largest contribution changes (mean |ΔJcvPCA|): LUArm_to_LFArm (0.254), RFArm_to_RHand (0.204), RUArm_to_RFArm (0.179), RShoulder_to_RUArm (0.127), LShoulder_to_LUArm (0.106)

## Statistical validation
## Validation summary

### Natural-variability baseline
- [671_T1_vs_T2] 671_to_Ab: longitudinal contribution change is 0.93x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T2] 671_to_LThigh: longitudinal contribution change is 1.42x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [671_T1_vs_T2] 671_to_RThigh: longitudinal contribution change is 1.67x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [671_T1_vs_T2] Ab_to_Chest: longitudinal contribution change is 0.91x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T2] Chest_to_LShoulder: longitudinal contribution change is 0.64x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T2] Chest_to_Neck: longitudinal contribution change is 0.77x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T2] Chest_to_RShoulder: longitudinal contribution change is 0.65x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T2] LFArm_to_LHand: longitudinal contribution change is 3.18x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [671_T1_vs_T2] LShin_to_LFoot: longitudinal contribution change is 1.07x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [671_T1_vs_T2] LShoulder_to_LUArm: longitudinal contribution change is 1.09x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [671_T1_vs_T2] LThigh_to_LShin: longitudinal contribution change is 1.93x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [671_T1_vs_T2] LUArm_to_LFArm: longitudinal contribution change is 0.65x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T2] Neck_to_Head: longitudinal contribution change is 0.77x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T2] RFArm_to_RHand: longitudinal contribution change is 0.73x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T2] RShin_to_RFoot: longitudinal contribution change is 1.23x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [671_T1_vs_T2] RShoulder_to_RUArm: longitudinal contribution change is 0.96x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T2] RThigh_to_RShin: longitudinal contribution change is 0.89x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T2] RUArm_to_RFArm: longitudinal contribution change is 0.73x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T3] 671_to_Ab: longitudinal contribution change is 1.11x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [671_T1_vs_T3] 671_to_RThigh: longitudinal contribution change is 1.87x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [671_T1_vs_T3] Chest_to_LShoulder: longitudinal contribution change is 0.84x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T3] Chest_to_Neck: longitudinal contribution change is 0.63x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T3] Chest_to_RShoulder: longitudinal contribution change is 0.61x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T3] LFArm_to_LHand: longitudinal contribution change is 3.41x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [671_T1_vs_T3] LShin_to_LFoot: longitudinal contribution change is 0.65x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T3] LShoulder_to_LUArm: longitudinal contribution change is 0.46x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T3] LUArm_to_LFArm: longitudinal contribution change is 0.58x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T3] Neck_to_Head: longitudinal contribution change is 0.63x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T3] RFArm_to_RHand: longitudinal contribution change is 1.16x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [671_T1_vs_T3] RShin_to_RFoot: longitudinal contribution change is 0.96x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T3] RShoulder_to_RUArm: longitudinal contribution change is 0.68x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T3] RThigh_to_RShin: longitudinal contribution change is 0.64x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [671_T1_vs_T3] RUArm_to_RFArm: longitudinal contribution change is 0.73x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_

### Sensitivity analysis
- Top-link ranking overlap after excluding flagged links = 100%; ranking is stable (sensitivity-supported). _[sensitivity-supported]_

### PCA-basis stability
- PCA basis similarity across repetitions = 0.36; movement space varies between repetitions (interpret with caution). _[descriptive only]_

### Bootstrap
- Bootstrap ran (18 links, 1000 resamples): 0 link(s) have a 95% CI that excludes zero. _[descriptive only]_


---
JcvPCA reports how each body link's contribution to the shared movement-variance structure differs between the two matched datasets. Values are descriptive; see the validation section for evidence strength.