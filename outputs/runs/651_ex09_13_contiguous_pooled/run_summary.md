# Run summary — 651_ex09_13_contiguous_pooled

- Participant: **651** (participant-specific, N-of-1)
- Selection: `651_ex09_13_contiguous` — 18 links included
- Exercises (authoritative exercise_id): [9, 10, 11, 12, 13]
- Variance threshold: 0.8; filter cutoff 10.0 Hz (order 4)
- Marker-gap policy: **on** (`/Users/drorhazan/Desktop/gaga_psilo/projects/gaga_jcvpca/results_committee_case/step03_trunk_extension/marker_gap_link_removals_ex09_13.csv`) — session-scoped exclusions listed per comparison when applicable.

## Comparisons
### 651_T1_vs_T2 — Longitudinal change
- 651_T1_R1+R2 (reference A) vs 651_T2_R1+R2 (B)
- selected_m = 6 at variance_threshold 0.8
- 10 links analyzed; 8 excluded.
- Note: 3 link(s) excluded from this comparison; analysis restricted to the shared valid link intersection (10 links).
- Note: 5 link(s) excluded by marker-gap policy before shared-link restriction.
- Largest contribution changes (mean |ΔJcvPCA|): LFArm_to_LHand (0.249), RUArm_to_RFArm (0.210), LUArm_to_LFArm (0.171), RFArm_to_RHand (0.164), RThigh_to_RShin (0.127)
- Excluded (marker-gap policy): Chest_to_RShoulder — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.; Ab_to_Chest — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.; Chest_to_LShoulder — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.; Chest_to_Neck — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.; Neck_to_Head — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.
- Excluded (matrix / rotvec QC): 651_to_Ab — features missing in dataset B; 651_to_LThigh — features missing in dataset B; 651_to_RThigh — features missing in dataset B

### 651_T1_vs_T3 — Longitudinal change
- 651_T1_R1+R2 (reference A) vs 651_T3_R1+R2 (B)
- selected_m = 5 at variance_threshold 0.8
- 9 links analyzed; 9 excluded.
- Note: 2 link(s) excluded from this comparison; analysis restricted to the shared valid link intersection (9 links).
- Note: 7 link(s) excluded by marker-gap policy before shared-link restriction.
- Largest contribution changes (mean |ΔJcvPCA|): RUArm_to_RFArm (0.316), LUArm_to_LFArm (0.300), RFArm_to_RHand (0.193), LFArm_to_LHand (0.134), RThigh_to_RShin (0.111)
- Excluded (marker-gap policy): LThigh_to_LShin — marker_gap_policy: T3_R2 — Supporting marker `651_T3:WaistLBack` has 14.5% of ex09-13 window in large gaps (>0.5 s, 2 runs); Motive likely interpolated bone motion.; Chest_to_RShoulder — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.; 651_to_LThigh — marker_gap_policy: T3_R2 — Supporting marker `651_T3:WaistLBack` has 14.5% of ex09-13 window in large gaps (>0.5 s, 2 runs); Motive likely interpolated bone motion.; Ab_to_Chest — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.; Chest_to_LShoulder — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.; Chest_to_Neck — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.; Neck_to_Head — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.
- Excluded (matrix / rotvec QC): 651_to_Ab — features missing in dataset B; 651_to_RThigh — features missing in dataset B

### 651_T1_R1_vs_R2 — Natural variability (R1 vs R2)
- 651_T1_P1_R1 (reference A) vs 651_T1_P1_R2 (B)
- selected_m = 6 at variance_threshold 0.8
- 13 links analyzed; 5 excluded.
- Note: 5 link(s) excluded by marker-gap policy before shared-link restriction.
- Largest contribution changes (mean |ΔJcvPCA|): RUArm_to_RFArm (0.191), LFArm_to_LHand (0.154), LUArm_to_LFArm (0.135), LShoulder_to_LUArm (0.084), RThigh_to_RShin (0.076)
- Excluded (marker-gap policy): Chest_to_RShoulder — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.; Ab_to_Chest — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.; Chest_to_LShoulder — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.; Chest_to_Neck — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.; Neck_to_Head — marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 window in large gaps (>0.5 s, 4 runs); Motive likely interpolated bone motion.

## Statistical validation
## Validation summary

### Natural-variability baseline
- [651_T1_vs_T2] LFArm_to_LHand: longitudinal contribution change is 1.62x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [651_T1_vs_T2] LShin_to_LFoot: longitudinal contribution change is 2.04x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [651_T1_vs_T2] LShoulder_to_LUArm: longitudinal contribution change is 0.39x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [651_T1_vs_T2] LThigh_to_LShin: longitudinal contribution change is 1.30x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [651_T1_vs_T2] LUArm_to_LFArm: longitudinal contribution change is 1.27x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [651_T1_vs_T2] RFArm_to_RHand: longitudinal contribution change is 3.01x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [651_T1_vs_T2] RShin_to_RFoot: longitudinal contribution change is 1.91x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [651_T1_vs_T2] RShoulder_to_RUArm: longitudinal contribution change is 2.44x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [651_T1_vs_T2] RThigh_to_RShin: longitudinal contribution change is 1.68x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [651_T1_vs_T2] RUArm_to_RFArm: longitudinal contribution change is 1.10x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [651_T1_vs_T3] LFArm_to_LHand: longitudinal contribution change is 0.87x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [651_T1_vs_T3] LShin_to_LFoot: longitudinal contribution change is 1.91x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [651_T1_vs_T3] LShoulder_to_LUArm: longitudinal contribution change is 0.97x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [651_T1_vs_T3] LUArm_to_LFArm: longitudinal contribution change is 2.22x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [651_T1_vs_T3] RFArm_to_RHand: longitudinal contribution change is 3.53x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [651_T1_vs_T3] RShin_to_RFoot: longitudinal contribution change is 1.57x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [651_T1_vs_T3] RShoulder_to_RUArm: longitudinal contribution change is 2.01x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [651_T1_vs_T3] RThigh_to_RShin: longitudinal contribution change is 1.47x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [651_T1_vs_T3] RUArm_to_RFArm: longitudinal contribution change is 1.66x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_

### Sensitivity analysis
- Top-link ranking overlap after excluding flagged links = 100%; ranking is stable (sensitivity-supported). _[sensitivity-supported]_

### PCA-basis stability
- PCA basis similarity across repetitions = 0.70; movement space varies between repetitions (interpret with caution). _[descriptive only]_

### Bootstrap
- Bootstrap ran (14 links, 1000 resamples): 0 link(s) have a 95% CI that excludes zero. _[descriptive only]_


---
JcvPCA reports how each body link's contribution to the shared movement-variance structure differs between the two matched datasets. Values are descriptive; see the validation section for evidence strength.