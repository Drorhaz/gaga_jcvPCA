# Master results table (thesis lock)

**Estimand lock:** A2 = matched single-repetition signed NV tier **S2** on `T1_R1 vs T{2,3}_R1` vs `T1_R1 vs T1_R2`, window `ex09_13_contiguous`. Pooled R1+R2 longitudinal is the **descriptive headline only** (different T1 basis; not the A2 floor).

**Source tree:** `results_committee_case/marker_gap_policy_ex09_13/`  
**Run git hash:** `728c871` (2026-07-19)  
**Machine table:** `MASTER_RESULTS_TABLE.csv`

Pre-policy Step 4 (`results_committee_case/step04_primary_runs/`, 2026-07-14) is **rejected** for thesis numbers. See `RESULTS_AUDIT.md` §B.

| PID | Comp. | A2 n / S3 | Coverage | rep_pass | k-grid min (k=4–7) | Status | One-line |
|---|---|---:|---|---|---:|---|---|
| **671** | T1→T2 | **8 / 4** | adequate 0.806 | **True** | 0.6 | **authoritative** | Only cell that clears S3 + coverage + rep_pass |
| 671 | T1→T3 | 9 / 0 | limited 0.697 | False | 0.4 | provisional | A2 exists; T3 marker-set + limited coverage block S3 |
| 252 | T1→T2 | 3 / 0 | adequate 0.811 | False | **0.0** | provisional | Small A2; one ratio = 1.01; ranking unstable |
| 252 | T1→T3 | 12 / 0 | **limited 0.601** | False | 0.4 | provisional | Largest A2 count; weakest coverage — do not headline |
| 651 | T1→T2 | 4 / 0 | adequate 0.837 | False | 0.4 | provisional | Trunk/chest stripped; pre-policy S3 gone |
| 651 | T1→T3 | 2 / 0 | limited 0.706 | False | 0.6 | provisional | Sparse; no persistent A2 |
| 790 | T1→T2 | 7 / 0 | adequate 0.867 | False | 0.2 | provisional | Count inflated by near-floor ratios (1.06–1.32) |
| 790 | T1→T3 | 3 / 0 | adequate 0.887 | False | 0.2 | provisional | Few A2; best T3 coverage; spine dropped |

## A2 links that may be quoted (signed `long_signed_single`)

### 671 T1→T2 — quote in main text (S3 in **bold**)

| Link | Signed Δ | NV signed | Ratio | Tier |
|---|---:|---:|---:|---|
| **LFArm_to_LHand** | +0.0740 | +0.0061 | 12.16 | **S3** |
| LUArm_to_LFArm | −0.0615 | +0.0002 | 256.32 | S2 (tiny NV floor) |
| **671_to_LThigh** | +0.0273 | +0.0055 | 4.98 | **S3** |
| **LThigh_to_LShin** | +0.0164 | +0.0077 | 2.13 | **S3** |
| **LShin_to_LFoot** | +0.0118 | −0.0060 | 1.96 | **S3** |
| 671_to_RThigh | +0.0138 | +0.0061 | 2.27 | S2 |
| 671_to_Ab | +0.0083 | +0.0023 | 3.59 | S2 |
| Ab_to_Chest | +0.0049 | +0.0002 | 30.39 | S2 |

S3-romflat sensitivity would add `671_to_Ab`, `Ab_to_Chest`, `LUArm_to_LFArm` (7 vs 4). **Governing S3 remains 4** until a supervisor decision (`CLAIMS.md` footing note).

### Persistent A2 (same sign at T2 and T3)

- **671:** `671_to_Ab`, `671_to_LThigh`, `671_to_RThigh`, `LFArm_to_LHand`, `LShin_to_LFoot`, `LThigh_to_LShin` (6)
- **790:** `LFArm_to_LHand` (1)
- **252, 651:** none

## How to read `status`

- **authoritative** — numbers + interpretive stack (A2 and candidate A3) may enter the main Results chapter.
- **provisional** — A2 **counts and link lists** may be shown as descriptive N-of-1 facts; do not promote to A3 / “organization of underused DoF” / shared pattern.
- **rejected** — pre-policy A2 (252 T2 was 8 not 3; 651 T2 S3 was 5 not 0).
