# Skeleton baselines — Step 2

Two marker-setup classes cover all four committee participants.

## Setup A — 671-style (51 bones)

- **Participants:** 671, 651
- **Bones:** 51; no `Spine2` / `Neck2`
- **Trunk chain:** `{pid}_to_Ab` → `Ab_to_Chest` → `Chest_to_Neck` → `Neck_to_Head`
- **Pelvis legs:** `{pid}_to_LThigh`, `{pid}_to_RThigh`
- **Feasible non-distal links:** 18

## Setup B — 252-style (55 bones)

- **Participants:** 252, 790
- **Bones:** 55; `Spine2` + `Neck2` present
- **Trunk chain:** `{pid}_to_Ab` → `Ab_to_Spine2` → `Spine3` → `Spine4` → `Chest`
- **Neck chain:** `Chest_to_Neck` → `Neck_to_Neck2` → `Neck2_to_Head`
- **Pelvis legs:** `{pid}_to_LThigh`, `{pid}_to_RThigh`
- **Feasible non-distal links:** 22

## Participant assignment

| Participant | Setup | Bones | Spine2 | Neck2 | Bone names match reference | Sample skeleton |
|---|---|---:|---|---|---|---|
| 671 | A | 51 | N | N | Yes | `671_T1_P1_R1_Take 2026-01-06 03.57.12 PM_001.csv` |
| 252 | B | 55 | Y | Y | Yes | `252_T1_P1_R1_Take 2026-04-28 04.15.00 PM_000.csv` |
| 651 | A | 51 | N | N | Yes | `651_T1_P1_R1_Take 2026-01-15 04.35.25 PM_002.csv` |
| 790 | B | 55 | Y | Y | Yes | `790_T1_P1_R1_Take 2026-04-26 06.09.29 PM_000.csv` |

## Notes

- Feasible links exclude finger/toe distal segments (`configs/body_regions.yaml` `exclude_tokens`).
- Pre-trunk `group4_core` manifests (14/16 links) omitted pelvis roots and trunk; Step 2 manifests restore the full feasible set.
- Step 3 applies inclusive QC before primary runs.
