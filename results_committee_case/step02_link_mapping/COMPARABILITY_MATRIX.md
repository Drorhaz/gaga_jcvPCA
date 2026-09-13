# Comparability matrix — Step 2

Flags indicate whether a canonical link supports cross-participant comparison.

| Comparability | Meaning |
|---|---|
| `cohort` | Identical segment topology in all participants that carry the link |
| `setup_specific` | Present in Setup B only (extended spine/neck chain) |
| `topology_variant` | Anatomically related but different bone path between setups |
| `participant_only` | Pelvis-root attachment; participant-prefixed stem |

## Cohort-comparable links (all four participants)

- `Chest_to_Neck` — Chest to neck base
- `Chest_to_LShoulder` — Chest to left shoulder
- `LShoulder_to_LUArm` — Left shoulder to upper arm
- `LUArm_to_LFArm` — Left elbow
- `LFArm_to_LHand` — Left wrist / hand
- `Chest_to_RShoulder` — Chest to right shoulder
- `RShoulder_to_RUArm` — Right shoulder to upper arm
- `RUArm_to_RFArm` — Right elbow
- `RFArm_to_RHand` — Right wrist / hand
- `LThigh_to_LShin` — Left knee
- `LShin_to_LFoot` — Left ankle / foot
- `RThigh_to_RShin` — Right knee
- `RShin_to_RFoot` — Right ankle / foot

## Setup-specific (252-style only)

- `Ab_to_Spine2` — present: 252, 790
- `Spine2_to_Spine3` — present: 252, 790
- `Spine3_to_Spine4` — present: 252, 790
- `Spine4_to_Chest` — present: 252, 790
- `Neck_to_Neck2` — present: 252, 790

## Topology variants (cross-setup mapping)

- `Ab_to_Chest` — 671=Ab_to_Chest, 651=Ab_to_Chest
- `neck_to_head` — 671=Neck_to_Head, 252=Neck2_to_Head, 651=Neck_to_Head, 790=Neck2_to_Head

## Participant-only (pelvis roots)

- `pelvis_to_Ab` — stems: `671_to_Ab` pattern
- `pelvis_to_LThigh` — stems: `671_to_LThigh` pattern
- `pelvis_to_RThigh` — stems: `671_to_RThigh` pattern

## Cross-participant analysis guidance

- **Within-participant** longitudinal claims: use all feasible links per participant.
- **Side-by-side illustration** across participants: prefer `cohort` links only.
- **Trunk redistribution:** compare `Ab_to_Chest` (671/651) vs `Spine4_to_Chest` + intermediate Setup B segments separately — do not merge as one cohort trunk link.
- **Head/neck:** Setup A `Neck_to_Head` maps to Setup B `Neck2_to_Head` (alias-aware in pipeline).
