# Diff — marker-gap policy run vs pre-policy baseline

**New run root:** `results_committee_case/marker_gap_policy_ex09_13`
**Old Step 4:** `results_committee_case/step04_primary_runs`
**Old Step 8:** `results_committee_case/step08_nv_and_stability`

Policy change: session-scoped marker-gap link exclusions wired into `run_analysis`.

## 1. New marker-gap exclusions (pooled comparisons)

| participant | comparison | link | reason (truncated) |
|---|---|---|---|
| 252 | 252_T1_R1_vs_R2 | LShin_to_LFoot | marker_gap_policy: T1_R2 — Supporting marker `252:LFAX` has 13.2% of ex09-13 win |
| 252 | 252_T1_R1_vs_R2 | LThigh_to_LShin | marker_gap_policy: T1_R2 — Supporting marker `252:LFAX` has 13.2% of ex09-13 win |
| 252 | 252_T1_vs_T2 | LShin_to_LFoot | marker_gap_policy: T1_R2 — Supporting marker `252:LFAX` has 13.2% of ex09-13 win |
| 252 | 252_T1_vs_T2 | LThigh_to_LShin | marker_gap_policy: T1_R2 — Supporting marker `252:LFAX` has 13.2% of ex09-13 win |
| 252 | 252_T1_vs_T3 | LShin_to_LFoot | marker_gap_policy: T1_R2 — Supporting marker `252:LFAX` has 13.2% of ex09-13 win |
| 252 | 252_T1_vs_T3 | LThigh_to_LShin | marker_gap_policy: T1_R2 — Supporting marker `252:LFAX` has 13.2% of ex09-13 win |
| 651 | 651_T1_R1_vs_R2 | Ab_to_Chest | marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 |
| 651 | 651_T1_R1_vs_R2 | Chest_to_LShoulder | marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 |
| 651 | 651_T1_R1_vs_R2 | Chest_to_Neck | marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 |
| 651 | 651_T1_R1_vs_R2 | Chest_to_RShoulder | marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 |
| 651 | 651_T1_R1_vs_R2 | Neck_to_Head | marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 |
| 651 | 651_T1_vs_T2 | Ab_to_Chest | marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 |
| 651 | 651_T1_vs_T2 | Chest_to_LShoulder | marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 |
| 651 | 651_T1_vs_T2 | Chest_to_Neck | marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 |
| 651 | 651_T1_vs_T2 | Chest_to_RShoulder | marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 |
| 651 | 651_T1_vs_T2 | Neck_to_Head | marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 |
| 651 | 651_T1_vs_T3 | 651_to_LThigh | marker_gap_policy: T3_R2 — Supporting marker `651_T3:WaistLBack` has 14.5% of ex |
| 651 | 651_T1_vs_T3 | Ab_to_Chest | marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 |
| 651 | 651_T1_vs_T3 | Chest_to_LShoulder | marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 |
| 651 | 651_T1_vs_T3 | Chest_to_Neck | marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 |
| 651 | 651_T1_vs_T3 | Chest_to_RShoulder | marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 |
| 651 | 651_T1_vs_T3 | LThigh_to_LShin | marker_gap_policy: T3_R2 — Supporting marker `651_T3:WaistLBack` has 14.5% of ex |
| 651 | 651_T1_vs_T3 | Neck_to_Head | marker_gap_policy: T1_R2 — Supporting marker `651:ChestTop` has 20.5% of ex09-13 |
| 671 | 671_T1_vs_T3 | 671_to_LThigh | marker_gap_policy: T3_R2 — Supporting marker `T3_671:LThighFront` has 99.0% of e |
| 671 | 671_T1_vs_T3 | LThigh_to_LShin | marker_gap_policy: T3_R2 — Supporting marker `T3_671:LThighFront` has 99.0% of e |
| 790 | 790_T1_R1_vs_R2 | RFArm_to_RHand | marker_gap_policy: T1_R2 — Supporting marker `790:RHLE` has 99.4% of ex09-13 win |
| 790 | 790_T1_R1_vs_R2 | RUArm_to_RFArm | marker_gap_policy: T1_R2 — Supporting marker `790:RHLE` has 99.4% of ex09-13 win |
| 790 | 790_T1_vs_T2 | RFArm_to_RHand | marker_gap_policy: T1_R2 — Supporting marker `790:RHLE` has 99.4% of ex09-13 win |
| 790 | 790_T1_vs_T2 | RUArm_to_RFArm | marker_gap_policy: T1_R2 — Supporting marker `790:RHLE` has 99.4% of ex09-13 win |
| 790 | 790_T1_vs_T3 | Ab_to_Spine2 | marker_gap_policy: T3_R1 — Supporting marker `790:RIPS` has 19.2% of ex09-13 win |
| 790 | 790_T1_vs_T3 | RFArm_to_RHand | marker_gap_policy: T1_R2 — Supporting marker `790:RHLE` has 99.4% of ex09-13 win |
| 790 | 790_T1_vs_T3 | RUArm_to_RFArm | marker_gap_policy: T1_R2 — Supporting marker `790:RHLE` has 99.4% of ex09-13 win |
| 790 | 790_T1_vs_T3 | Spine2_to_Spine3 | marker_gap_policy: T3_R1 — Supporting marker `790:RIPS` has 19.2% of ex09-13 win |

## 2. Selected m and link counts (pooled Step 4)

| participant | comparison | old m | new m | old links | new links | old excl | new excl |
|---|---|---:|---:|---:|---:|---:|---:|
| 252 | 252_T1_R1_vs_R2 | 10 | 9 | 22 | 20 | 0 | 2 |
| 252 | 252_T1_vs_T2 | 10 | 10 | 22 | 20 | 0 | 2 |
| 252 | 252_T1_vs_T3 | 10 | 10 | 22 | 20 | 0 | 2 |
| 651 | 651_T1_R1_vs_R2 | 6 | 6 | 18 | 13 | 0 | 5 |
| 651 | 651_T1_vs_T2 | 6 | 6 | 14 | 10 | 4 | 8 |
| 651 | 651_T1_vs_T3 | 6 | 5 | 14 | 9 | 4 | 9 |
| 671 | 671_T1_R1_vs_R2 | 8 | 8 | 18 | 18 | 0 | 0 |
| 671 | 671_T1_vs_T2 | 9 | 9 | 18 | 18 | 0 | 0 |
| 671 | 671_T1_vs_T3 | 9 | 8 | 17 | 15 | 1 | 3 |
| 790 | 790_T1_R1_vs_R2 | 8 | 7 | 22 | 20 | 0 | 2 |
| 790 | 790_T1_vs_T2 | 9 | 8 | 22 | 20 | 0 | 2 |
| 790 | 790_T1_vs_T3 | 9 | 8 | 22 | 18 | 0 | 4 |

## 3. Signed NV profile (A2 / tiers)

| participant | comparison | old A2 | new A2 | Δ A2 | old S2/S3 | new S2/S3 | old n | new n |
|---|---|---:|---:|---:|---|---:|---:|---:|
| 252 | T1_vs_T2 | 8 | 3 | -5 | 8/0 | 3/0 | 22 | 20 |
| 252 | T1_vs_T3 | 13 | 12 | -1 | 13/0 | 12/0 | 22 | 20 |
| 651 | T1_vs_T2 | 8 | 4 | -4 | 3/5 | 4/0 | 14 | 10 |
| 651 | T1_vs_T3 | 7 | 2 | -5 | 7/0 | 2/0 | 14 | 10 |
| 671 | T1_vs_T2 | 8 | 8 | +0 | 4/4 | 8/0 | 18 | 18 |
| 671 | T1_vs_T3 | 9 | 9 | +0 | 9/0 | 9/0 | 17 | 17 |
| 790 | T1_vs_T2 | 5 | 7 | +2 | 5/0 | 7/0 | 22 | 20 |
| 790 | T1_vs_T3 | 5 | 3 | -2 | 5/0 | 3/0 | 22 | 18 |

## 4. Top-5 link ranking (pooled |JcvPCA|, longitudinal only)

| participant | comparison | overlap | old top-5 | new top-5 |
|---|---|---:|---|---|
| 671 | T1_vs_T2 | 1.0 | LFArm_to_LHand, LUArm_to_LFArm, RShoulder_to_RUArm, RUArm_to_RFArm, 671_to_LThigh | LFArm_to_LHand, LUArm_to_LFArm, RShoulder_to_RUArm, RUArm_to_RFArm, 671_to_LThigh |
| 671 | T1_vs_T3 | 0.4 | LUArm_to_LFArm, RUArm_to_RFArm, LFArm_to_LHand, LShoulder_to_LUArm, Neck_to_Head | RFArm_to_RHand, LFArm_to_LHand, Chest_to_LShoulder, LUArm_to_LFArm, 671_to_Ab |
| 252 | T1_vs_T2 | 0.6 | RUArm_to_RFArm, 252_to_LThigh, LUArm_to_LFArm, 252_to_RThigh, RThigh_to_RShin | RFArm_to_RHand, LUArm_to_LFArm, 252_to_RThigh, 252_to_LThigh, LFArm_to_LHand |
| 252 | T1_vs_T3 | 0.8 | LUArm_to_LFArm, RThigh_to_RShin, LFArm_to_LHand, 252_to_RThigh, RFArm_to_RHand | LUArm_to_LFArm, RThigh_to_RShin, LFArm_to_LHand, RFArm_to_RHand, RUArm_to_RFArm |
| 651 | T1_vs_T2 | 0.8 | RUArm_to_RFArm, LUArm_to_LFArm, LFArm_to_LHand, RShoulder_to_RUArm, RFArm_to_RHand | RUArm_to_RFArm, RShoulder_to_RUArm, LUArm_to_LFArm, RFArm_to_RHand, LShoulder_to_LUArm |
| 651 | T1_vs_T3 | 0.6 | RUArm_to_RFArm, LUArm_to_LFArm, RFArm_to_RHand, RThigh_to_RShin, LThigh_to_LShin | LUArm_to_LFArm, RUArm_to_RFArm, RThigh_to_RShin, LFArm_to_LHand, LShoulder_to_LUArm |
| 790 | T1_vs_T2 | 0.4 | LShoulder_to_LUArm, 790_to_LThigh, LThigh_to_LShin, LFArm_to_LHand, RUArm_to_RFArm | LShoulder_to_LUArm, LUArm_to_LFArm, LFArm_to_LHand, RThigh_to_RShin, RShoulder_to_RUArm |
| 790 | T1_vs_T3 | 0.4 | RShoulder_to_RUArm, RUArm_to_RFArm, RFArm_to_RHand, RThigh_to_RShin, LUArm_to_LFArm | 790_to_LThigh, RThigh_to_RShin, LThigh_to_LShin, RShoulder_to_RUArm, Chest_to_LShoulder |

## 5. Step 4b robustness labels

| participant | comparison | old | new |
|---|---|---|---|
| 252 | 252_T1_vs_T2 | nan | nan |
| 252 | 252_T1_vs_T2 | nan | partial |
| 252 | 252_T1_vs_T2 | partial | nan |
| 252 | 252_T1_vs_T2 | partial | partial |
| 252 | 252_T1_vs_T3 | nan | nan |
| 252 | 252_T1_vs_T3 | nan | stable |
| 252 | 252_T1_vs_T3 | partial | nan |
| 252 | 252_T1_vs_T3 | partial | stable |
| 651 | 651_T1_vs_T2 | nan | nan |
| 651 | 651_T1_vs_T2 | nan | partial |
| 651 | 651_T1_vs_T2 | stable | nan |
| 651 | 651_T1_vs_T2 | stable | partial |
| 651 | 651_T1_vs_T3 | nan | nan |
| 651 | 651_T1_vs_T3 | nan | stable |
| 651 | 651_T1_vs_T3 | stable | nan |
| 651 | 651_T1_vs_T3 | stable | stable |
| 671 | 671_T1_vs_T2 | nan | nan |
| 671 | 671_T1_vs_T2 | nan | stable |
| 671 | 671_T1_vs_T2 | stable | nan |
| 671 | 671_T1_vs_T2 | stable | stable |
| 671 | 671_T1_vs_T3 | nan | nan |
| 671 | 671_T1_vs_T3 | nan | stable |
| 671 | 671_T1_vs_T3 | stable | nan |
| 671 | 671_T1_vs_T3 | stable | stable |
| 790 | 790_T1_vs_T2 | nan | nan |
| 790 | 790_T1_vs_T2 | nan | partial |
| 790 | 790_T1_vs_T2 | stable | nan |
| 790 | 790_T1_vs_T2 | stable | partial |
| 790 | 790_T1_vs_T3 | nan | nan |
| 790 | 790_T1_vs_T3 | nan | partial |
| 790 | 790_T1_vs_T3 | partial | nan |
| 790 | 790_T1_vs_T3 | partial | partial |

## 6. Step 5 org/amp mix

- **671_T1_vs_T2** org old=6 new=6
- **671_T1_vs_T3** org old=6 new=2
- **252_T1_vs_T2** org old=6 new=4
- **252_T1_vs_T3** org old=19 new=10
- **651_T1_vs_T2** org old=10 new=8
- **651_T1_vs_T3** org old=7 new=5
- **790_T1_vs_T2** org old=12 new=9
- **790_T1_vs_T3** org old=4 new=7

## 6. Step 9 persistence flags

- **671** old persistent=6 → new 6
- **252** old persistent=3 → new 0
- **651** old persistent=3 → new 0
- **790** old persistent=1 → new 1

## Summary interpretation

- **Link count changes** reflect marker-gap drops (and any shared-feature intersection shifts).
- **A2 / tier changes** can come from fewer links, different subspaces, or shifted signed effects.
- **Top-5 overlap < 1.0** flags comparisons worth checking in run summaries; Step 4b k-grid remains the formal sensitivity check.
- Pre-policy Step 5–9 used old Step 4/8 inputs; new Step 5–9 in this run tree are internally consistent with marker-gap Step 4/8.
