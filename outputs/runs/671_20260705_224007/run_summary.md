# Run summary — 671_20260705_224007

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
Not run for this analysis (optional stage).

---
JcvPCA reports how each body link's contribution to the shared movement-variance structure differs between the two matched datasets. Values are descriptive; see the validation section for evidence strength.