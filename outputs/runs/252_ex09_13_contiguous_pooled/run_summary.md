# Run summary — 252_ex09_13_contiguous_pooled

- Participant: **252** (participant-specific, N-of-1)
- Selection: `252_ex09_13_contiguous` — 22 links included
- Exercises (authoritative exercise_id): [9, 10, 11, 12, 13]
- Variance threshold: 0.8; filter cutoff 10.0 Hz (order 4)
- Marker-gap policy: **on** (`/Users/drorhazan/Desktop/gaga_psilo/projects/gaga_jcvpca/results_committee_case/step03_trunk_extension/marker_gap_link_removals_ex09_13.csv`) — session-scoped exclusions listed per comparison when applicable.

## Comparisons
### 252_T1_vs_T2 — Longitudinal change
- 252_T1_R1+R2 (reference A) vs 252_T2_R1+R2 (B)
- selected_m = 10 at variance_threshold 0.8
- 20 links analyzed; 2 excluded.
- Note: 2 link(s) excluded by marker-gap policy before shared-link restriction.
- Largest contribution changes (mean |ΔJcvPCA|): RFArm_to_RHand (0.185), RUArm_to_RFArm (0.155), RShoulder_to_RUArm (0.137), RThigh_to_RShin (0.104), LShoulder_to_LUArm (0.088)
- Excluded (marker-gap policy): LThigh_to_LShin — marker_gap_policy: T1_R2 — Supporting marker `252:LFAX` has 13.2% of ex09-13 window in large gaps (>0.5 s, 2 runs); Motive likely interpolated bone motion.; LShin_to_LFoot — marker_gap_policy: T1_R2 — Supporting marker `252:LFAX` has 13.2% of ex09-13 window in large gaps (>0.5 s, 2 runs); Motive likely interpolated bone motion.

### 252_T1_vs_T3 — Longitudinal change
- 252_T1_R1+R2 (reference A) vs 252_T3_R1+R2 (B)
- selected_m = 10 at variance_threshold 0.8
- 20 links analyzed; 2 excluded.
- Note: 2 link(s) excluded by marker-gap policy before shared-link restriction.
- Largest contribution changes (mean |ΔJcvPCA|): RUArm_to_RFArm (0.289), LUArm_to_LFArm (0.274), RShoulder_to_RUArm (0.211), LShoulder_to_LUArm (0.171), RThigh_to_RShin (0.171)
- Excluded (marker-gap policy): LThigh_to_LShin — marker_gap_policy: T1_R2 — Supporting marker `252:LFAX` has 13.2% of ex09-13 window in large gaps (>0.5 s, 2 runs); Motive likely interpolated bone motion.; LShin_to_LFoot — marker_gap_policy: T1_R2 — Supporting marker `252:LFAX` has 13.2% of ex09-13 window in large gaps (>0.5 s, 2 runs); Motive likely interpolated bone motion.

### 252_T1_R1_vs_R2 — Natural variability (R1 vs R2)
- 252_T1_P1_R1 (reference A) vs 252_T1_P1_R2 (B)
- selected_m = 9 at variance_threshold 0.8
- 20 links analyzed; 2 excluded.
- Note: 2 link(s) excluded by marker-gap policy before shared-link restriction.
- Largest contribution changes (mean |ΔJcvPCA|): RShoulder_to_RUArm (0.188), RUArm_to_RFArm (0.169), LUArm_to_LFArm (0.146), LFArm_to_LHand (0.120), LShoulder_to_LUArm (0.088)
- Excluded (marker-gap policy): LThigh_to_LShin — marker_gap_policy: T1_R2 — Supporting marker `252:LFAX` has 13.2% of ex09-13 window in large gaps (>0.5 s, 2 runs); Motive likely interpolated bone motion.; LShin_to_LFoot — marker_gap_policy: T1_R2 — Supporting marker `252:LFAX` has 13.2% of ex09-13 window in large gaps (>0.5 s, 2 runs); Motive likely interpolated bone motion.

## Statistical validation
## Validation summary

### Natural-variability baseline
- [252_T1_vs_T2] 252_to_Ab: longitudinal contribution change is 0.80x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] 252_to_LThigh: longitudinal contribution change is 0.84x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] 252_to_RThigh: longitudinal contribution change is 0.83x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] Ab_to_Spine2: longitudinal contribution change is 0.69x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] Chest_to_LShoulder: longitudinal contribution change is 1.51x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] Chest_to_Neck: longitudinal contribution change is 1.00x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] Chest_to_RShoulder: longitudinal contribution change is 0.77x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] LFArm_to_LHand: longitudinal contribution change is 0.52x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] LShoulder_to_LUArm: longitudinal contribution change is 1.01x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] LUArm_to_LFArm: longitudinal contribution change is 0.44x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] Neck2_to_Head: longitudinal contribution change is 0.99x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] Neck_to_Neck2: longitudinal contribution change is 1.00x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] RFArm_to_RHand: longitudinal contribution change is 2.55x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] RShin_to_RFoot: longitudinal contribution change is 0.75x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] RShoulder_to_RUArm: longitudinal contribution change is 0.73x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] RThigh_to_RShin: longitudinal contribution change is 1.31x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] RUArm_to_RFArm: longitudinal contribution change is 0.92x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] Spine2_to_Spine3: longitudinal contribution change is 0.69x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] Spine3_to_Spine4: longitudinal contribution change is 0.69x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T2] Spine4_to_Chest: longitudinal contribution change is 0.69x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] 252_to_Ab: longitudinal contribution change is 0.76x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] 252_to_LThigh: longitudinal contribution change is 0.70x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] 252_to_RThigh: longitudinal contribution change is 2.20x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] Ab_to_Spine2: longitudinal contribution change is 0.73x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] Chest_to_LShoulder: longitudinal contribution change is 1.66x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] Chest_to_Neck: longitudinal contribution change is 0.91x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] Chest_to_RShoulder: longitudinal contribution change is 1.01x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] LFArm_to_LHand: longitudinal contribution change is 0.55x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] LShoulder_to_LUArm: longitudinal contribution change is 1.95x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] LUArm_to_LFArm: longitudinal contribution change is 1.87x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] Neck2_to_Head: longitudinal contribution change is 0.91x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] Neck_to_Neck2: longitudinal contribution change is 0.91x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] RFArm_to_RHand: longitudinal contribution change is 1.39x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] RShin_to_RFoot: longitudinal contribution change is 1.70x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] RShoulder_to_RUArm: longitudinal contribution change is 1.12x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] RThigh_to_RShin: longitudinal contribution change is 2.15x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] RUArm_to_RFArm: longitudinal contribution change is 1.71x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] Spine2_to_Spine3: longitudinal contribution change is 0.73x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] Spine3_to_Spine4: longitudinal contribution change is 0.73x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [252_T1_vs_T3] Spine4_to_Chest: longitudinal contribution change is 0.73x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_

### Sensitivity analysis
- Top-link ranking overlap after excluding flagged links = 100%; ranking is stable (sensitivity-supported). _[sensitivity-supported]_

### PCA-basis stability
- PCA basis similarity across repetitions = 0.45; movement space varies between repetitions (interpret with caution). _[descriptive only]_

### Bootstrap
- Bootstrap ran (22 links, 1000 resamples): 0 link(s) have a 95% CI that excludes zero. _[descriptive only]_


---
JcvPCA reports how each body link's contribution to the shared movement-variance structure differs between the two matched datasets. Values are descriptive; see the validation section for evidence strength.