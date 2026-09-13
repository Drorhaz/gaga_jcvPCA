# Run summary — 651_ex09_13_contiguous_single

- Participant: **651** (participant-specific, N-of-1)
- Selection: `651_ex09_13_contiguous` — 18 links included
- Exercises (authoritative exercise_id): [9, 10, 11, 12, 13]
- Variance threshold: 0.8; filter cutoff 10.0 Hz (order 4)

## Comparisons
### 651_T1_vs_T2 — Longitudinal change
- 651_T1_P1_R1 (reference A) vs 651_T2_P1_R1 (B)
- selected_m = 6 at variance_threshold 0.8
- 14 links analyzed; 4 excluded.
- Note: 4 link(s) excluded from this comparison; analysis restricted to the shared valid link intersection (14 links).
- Largest contribution changes (mean |ΔJcvPCA|): RUArm_to_RFArm (0.253), LUArm_to_LFArm (0.217), LFArm_to_LHand (0.184), RFArm_to_RHand (0.169), RShoulder_to_RUArm (0.146)
- Excluded links: 651_to_Ab — features missing in dataset B; 651_to_LThigh — features missing in dataset B; 651_to_RThigh — features missing in dataset B; Ab_to_Chest — features missing in dataset B

### 651_T1_vs_T3 — Longitudinal change
- 651_T1_P1_R1 (reference A) vs 651_T3_P1_R1 (B)
- selected_m = 6 at variance_threshold 0.8
- 14 links analyzed; 4 excluded.
- Note: 4 link(s) excluded from this comparison; analysis restricted to the shared valid link intersection (14 links).
- Largest contribution changes (mean |ΔJcvPCA|): RUArm_to_RFArm (0.242), LUArm_to_LFArm (0.185), RFArm_to_RHand (0.163), LFArm_to_LHand (0.158), RShoulder_to_RUArm (0.100)
- Excluded links: 651_to_Ab — features missing in dataset B; 651_to_LThigh — features missing in dataset B; 651_to_RThigh — features missing in dataset B; Ab_to_Chest — features missing in dataset B

### 651_T1_R1_vs_R2 — Natural variability (R1 vs R2)
- 651_T1_P1_R1 (reference A) vs 651_T1_P1_R2 (B)
- selected_m = 6 at variance_threshold 0.8
- 18 links analyzed; 0 excluded.
- Largest contribution changes (mean |ΔJcvPCA|): RUArm_to_RFArm (0.171), LFArm_to_LHand (0.149), LUArm_to_LFArm (0.120), LShoulder_to_LUArm (0.076), RThigh_to_RShin (0.065)

## Statistical validation
Not run for this analysis (optional stage).

---
JcvPCA reports how each body link's contribution to the shared movement-variance structure differs between the two matched datasets. Values are descriptive; see the validation section for evidence strength.