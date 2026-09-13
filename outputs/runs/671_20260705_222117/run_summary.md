# Run summary — 671_20260705_222117

- Participant: **671** (participant-specific, N-of-1)
- Selection: `671_group4_default` — 14 links included
- Exercises (authoritative exercise_id): [9, 10, 11, 12, 13]
- Variance threshold: 0.8; filter cutoff 10.0 Hz (order 4)

## Comparability notes
- **671**: Marker-set prefix differs across timepoints (['671', 'T3']). Cross-timepoint comparisons restricted to shared valid links; interpret with care.

## Comparisons
### 671_T1_vs_T2 — Longitudinal change
- 671_T1_P1_R1 (reference A) vs 671_T2_P1_R1 (B)
- selected_m = 31 at variance_threshold 0.8
- 14 links analyzed; 0 excluded.
- Largest contribution changes (mean |ΔJcvPCA|): LThigh_to_LShin (0.134), Chest_to_RShoulder (0.131), Chest_to_LShoulder (0.124), RShin_to_RFoot (0.123), RFArm_to_RHand (0.123)

### 671_T1_vs_T3 — Longitudinal change
- 671_T1_P1_R1 (reference A) vs 671_T3_P1_R1 (B)
- selected_m = 31 at variance_threshold 0.8
- 14 links analyzed; 0 excluded.
- Largest contribution changes (mean |ΔJcvPCA|): RShin_to_RFoot (0.128), RFArm_to_RHand (0.121), Chest_to_Neck (0.120), Neck_to_Head (0.117), RThigh_to_RShin (0.116)

### 671_T1_R1_vs_R2 — Natural variability (R1 vs R2)
- 671_T1_P1_R1 (reference A) vs 671_T1_P1_R2 (B)
- selected_m = 31 at variance_threshold 0.8
- 14 links analyzed; 0 excluded.
- Largest contribution changes (mean |ΔJcvPCA|): RShoulder_to_RUArm (0.133), Chest_to_Neck (0.130), LShoulder_to_LUArm (0.126), LThigh_to_LShin (0.123), Chest_to_RShoulder (0.123)

## Variance-threshold sweep
Threshold robustness of selected_m and the top link:
- threshold 0.7: selected_m=26, top link LThigh_to_LShin
- threshold 0.8: selected_m=31, top link LThigh_to_LShin
- threshold 0.9: selected_m=36, top link RShin_to_RFoot

## Statistical validation
## Validation summary

### Natural-variability baseline
- Chest_to_LShoulder: longitudinal contribution change is 1.11x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- Chest_to_Neck: longitudinal contribution change is 0.58x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- Chest_to_RShoulder: longitudinal contribution change is 1.07x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- LFArm_to_LHand: longitudinal contribution change is 0.69x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- LShin_to_LFoot: longitudinal contribution change is 0.87x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- LShoulder_to_LUArm: longitudinal contribution change is 0.93x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- LThigh_to_LShin: longitudinal contribution change is 1.09x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- LUArm_to_LFArm: longitudinal contribution change is 0.95x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- Neck_to_Head: longitudinal contribution change is 0.85x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- RFArm_to_RHand: longitudinal contribution change is 1.09x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- RShin_to_RFoot: longitudinal contribution change is 1.30x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_
- RShoulder_to_RUArm: longitudinal contribution change is 0.92x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- RThigh_to_RShin: longitudinal contribution change is 0.93x the R1-vs-R2 natural variability (within repetition-level variability). _[descriptive only]_
- RUArm_to_RFArm: longitudinal contribution change is 1.07x the R1-vs-R2 natural variability (beyond repetition-level variability). _[descriptive only]_

### Sensitivity analysis
- Top-link ranking overlap after excluding flagged links = 100%; ranking is stable (sensitivity-supported). _[sensitivity-supported]_

### PCA-basis stability
- PCA basis similarity across repetitions = 0.14; movement space varies between repetitions (interpret with caution). _[descriptive only]_

### Bootstrap
- Bootstrap ran (14 links, 1000 resamples): 0 link(s) have a 95% CI that excludes zero. _[descriptive only]_


---
JcvPCA reports how each body link's contribution to the shared movement-variance structure differs between the two matched datasets. Values are descriptive; see the validation section for evidence strength.