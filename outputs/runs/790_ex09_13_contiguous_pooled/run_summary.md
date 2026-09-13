# Run summary — 790_ex09_13_contiguous_pooled

- Participant: **790** (participant-specific, N-of-1)
- Selection: `790_ex09_13_contiguous` — 22 links included
- Exercises (authoritative exercise_id): [9, 10, 11, 12, 13]
- Variance threshold: 0.8; filter cutoff 10.0 Hz (order 4)
- Marker-gap policy: **on** (`/Users/drorhazan/Desktop/gaga_psilo/projects/gaga_jcvpca/results_committee_case/step03_trunk_extension/marker_gap_link_removals_ex09_13.csv`) — session-scoped exclusions listed per comparison when applicable.

## Comparisons
### 790_T1_vs_T2 — Longitudinal change
- 790_T1_R1+R2 (reference A) vs 790_T2_R1+R2 (B)
- selected_m = 8 at variance_threshold 0.8
- 20 links analyzed; 2 excluded.
- Note: 2 link(s) excluded by marker-gap policy before shared-link restriction.
- Largest contribution changes (mean |ΔJcvPCA|): LUArm_to_LFArm (0.260), LShoulder_to_LUArm (0.248), RShoulder_to_RUArm (0.164), LFArm_to_LHand (0.099), RThigh_to_RShin (0.098)
- Excluded (marker-gap policy): RFArm_to_RHand — marker_gap_policy: T1_R2 — Supporting marker `790:RHLE` has 99.4% of ex09-13 window in large gaps (>0.5 s, 3 runs); Motive likely interpolated bone motion.; RUArm_to_RFArm — marker_gap_policy: T1_R2 — Supporting marker `790:RHLE` has 99.4% of ex09-13 window in large gaps (>0.5 s, 3 runs); Motive likely interpolated bone motion.

### 790_T1_vs_T3 — Longitudinal change
- 790_T1_R1+R2 (reference A) vs 790_T3_R1+R2 (B)
- selected_m = 8 at variance_threshold 0.8
- 18 links analyzed; 4 excluded.
- Note: 4 link(s) excluded by marker-gap policy before shared-link restriction.
- Largest contribution changes (mean |ΔJcvPCA|): LUArm_to_LFArm (0.192), LShoulder_to_LUArm (0.121), LFArm_to_LHand (0.112), RShoulder_to_RUArm (0.100), RThigh_to_RShin (0.075)
- Excluded (marker-gap policy): Spine2_to_Spine3 — marker_gap_policy: T3_R1 — Supporting marker `790:RIPS` has 19.2% of ex09-13 window in large gaps (>0.5 s, 2 runs); Motive likely interpolated bone motion.; also flagged on T3_R2; Ab_to_Spine2 — marker_gap_policy: T3_R1 — Supporting marker `790:RIPS` has 19.2% of ex09-13 window in large gaps (>0.5 s, 2 runs); Motive likely interpolated bone motion.; also flagged on T3_R2; RFArm_to_RHand — marker_gap_policy: T1_R2 — Supporting marker `790:RHLE` has 99.4% of ex09-13 window in large gaps (>0.5 s, 3 runs); Motive likely interpolated bone motion.; RUArm_to_RFArm — marker_gap_policy: T1_R2 — Supporting marker `790:RHLE` has 99.4% of ex09-13 window in large gaps (>0.5 s, 3 runs); Motive likely interpolated bone motion.

### 790_T1_R1_vs_R2 — Natural variability (R1 vs R2)
- 790_T1_P1_R1 (reference A) vs 790_T1_P1_R2 (B)
- selected_m = 7 at variance_threshold 0.8
- 20 links analyzed; 2 excluded.
- Note: 2 link(s) excluded by marker-gap policy before shared-link restriction.
- Largest contribution changes (mean |ΔJcvPCA|): LShoulder_to_LUArm (0.238), RShoulder_to_RUArm (0.165), LUArm_to_LFArm (0.158), LFArm_to_LHand (0.151), LThigh_to_LShin (0.147)
- Excluded (marker-gap policy): RFArm_to_RHand — marker_gap_policy: T1_R2 — Supporting marker `790:RHLE` has 99.4% of ex09-13 window in large gaps (>0.5 s, 3 runs); Motive likely interpolated bone motion.; RUArm_to_RFArm — marker_gap_policy: T1_R2 — Supporting marker `790:RHLE` has 99.4% of ex09-13 window in large gaps (>0.5 s, 3 runs); Motive likely interpolated bone motion.

## Statistical validation
## Validation summary

### Natural-variability baseline
- [790_T1_vs_T2] 790_to_Ab: longitudinal contribution change is 0.96x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] 790_to_LThigh: longitudinal contribution change is 0.68x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] 790_to_RThigh: longitudinal contribution change is 0.44x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] Ab_to_Spine2: longitudinal contribution change is 1.07x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] Chest_to_LShoulder: longitudinal contribution change is 0.87x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] Chest_to_Neck: longitudinal contribution change is 1.04x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] Chest_to_RShoulder: longitudinal contribution change is 1.25x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] LFArm_to_LHand: longitudinal contribution change is 0.66x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] LShin_to_LFoot: longitudinal contribution change is 2.42x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] LShoulder_to_LUArm: longitudinal contribution change is 1.04x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] LThigh_to_LShin: longitudinal contribution change is 0.51x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] LUArm_to_LFArm: longitudinal contribution change is 1.65x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] Neck2_to_Head: longitudinal contribution change is 1.04x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] Neck_to_Neck2: longitudinal contribution change is 1.04x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] RShin_to_RFoot: longitudinal contribution change is 0.42x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] RShoulder_to_RUArm: longitudinal contribution change is 1.00x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] RThigh_to_RShin: longitudinal contribution change is 0.82x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] Spine2_to_Spine3: longitudinal contribution change is 1.07x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] Spine3_to_Spine4: longitudinal contribution change is 1.07x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [790_T1_vs_T2] Spine4_to_Chest: longitudinal contribution change is 1.07x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] 790_to_Ab: longitudinal contribution change is 0.99x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] 790_to_LThigh: longitudinal contribution change is 0.43x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] 790_to_RThigh: longitudinal contribution change is 0.36x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] Chest_to_LShoulder: longitudinal contribution change is 0.79x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] Chest_to_Neck: longitudinal contribution change is 1.72x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] Chest_to_RShoulder: longitudinal contribution change is 0.90x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] LFArm_to_LHand: longitudinal contribution change is 0.75x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] LShin_to_LFoot: longitudinal contribution change is 1.95x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] LShoulder_to_LUArm: longitudinal contribution change is 0.51x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] LThigh_to_LShin: longitudinal contribution change is 0.41x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] LUArm_to_LFArm: longitudinal contribution change is 1.22x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] Neck2_to_Head: longitudinal contribution change is 1.72x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] Neck_to_Neck2: longitudinal contribution change is 1.72x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] RShin_to_RFoot: longitudinal contribution change is 0.61x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] RShoulder_to_RUArm: longitudinal contribution change is 0.61x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] RThigh_to_RShin: longitudinal contribution change is 0.63x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] Spine3_to_Spine4: longitudinal contribution change is 1.27x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- [790_T1_vs_T3] Spine4_to_Chest: longitudinal contribution change is 1.28x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_

### Sensitivity analysis
- Top-link ranking overlap after excluding flagged links = 100%; ranking is stable (sensitivity-supported). _[sensitivity-supported]_

### PCA-basis stability
- PCA basis similarity across repetitions = 0.33; movement space varies between repetitions (interpret with caution). _[descriptive only]_

### Bootstrap
- Bootstrap ran (22 links, 1000 resamples): 0 link(s) have a 95% CI that excludes zero. _[descriptive only]_


---
JcvPCA reports how each body link's contribution to the shared movement-variance structure differs between the two matched datasets. Values are descriptive; see the validation section for evidence strength.