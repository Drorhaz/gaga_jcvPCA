# Minimal BVH compatibility test

**Goal:** In **≤ half a day**, answer three yes/no questions — not pick a permanent feature stream.

1. Can BVH Euler channels be **aligned** to the same Motive exercise windows?
2. Can they be fed to the **same** `compute_jcvpca` operator without pipeline surgery?
3. Do they tell a **qualitatively similar** contribution story to rotvec on one test case?

**Non-goals:** Full scorecard, all participants, all windows, production adapter, ISB pipeline, changing the sacred core.

---

## Scope lock

| In | Out |
|---|---|
| 1 participant (671) | 252, 651, 790 |
| 1 window (ex11 single — current 671 winner) | All contiguous spans |
| 6 sessions: T1/T2/T3 × R1/R2 | P2, other task parts |
| 8–12 Euler channels (trunk + shoulders + elbows) | Full skeleton |
| 1 jcvPCA run: T1 vs T2, T1 vs T3, NV | Threshold sweep, bootstrap |
| Qualitative compare vs existing rotvec run | Full Step 2 scorecard |

**Time box:** stop after **4 hours** of alignment/debug. If not aligned by then → record `INCOMPATIBLE` and keep rotvec.

---

## Phase A — Intake (30–60 min)

**Deliverable:** `results_feature_pilot/intake/BVH_MINIMAL_INTAKE.md`

Record:

1. **BVH root path** and naming pattern (how file maps to `671_T1_P1_R1`, etc.)
2. **Frame rate** and total frames per file
3. **Joint/channel list** from one BVH (copy MOTION section or export header)
4. **Euler convention:** order (e.g. ZXY), units (deg/rad), local vs global
5. **Session coverage table:**

| session_id | BVH path | exists? | n_frames |
|---|---|---|---|
| 671_T1_P1_R1 | … | | |
| … (6 rows) | | | |

**Decision gate A:** ≥ 6 sessions present for 671 P1. If missing >2 sessions → stop; note gap only.

---

## Phase B — Channel pick list (15 min)

**Deliverable:** `results_feature_pilot/intake/BVH_CHANNEL_PICKLIST.csv`

Pick **8–12 channels max** that support the Gaga center→periphery story:

| bvh_joint | bvh_channel | canonical_label | rationale |
|---|---|---|---|
| e.g. Spine / Chest | rotX | trunk_sagittal | center |
| … | | L_shoulder_flex | left arm |
| … | | R_shoulder_flex | right arm |

Rules:
- Same channel **names** must exist in all 6 BVH files (or document drops).
- Prefer channels that already exist in your ISB export if names match.
- No fingers, toes, or redundant DoFs.

**Decision gate B:** ≥ 8 channels shared across all 6 files. If < 8 → reduce story scope or stop.

---

## Phase C — Frame alignment (60–90 min, hard stop 4 h total)

**Deliverable:** `results_feature_pilot/intake/BVH_ALIGNMENT_TEST.md`

For **one** session (671 T1 R1) and window **ex11**:

1. Load segmentation row: `start_frame`, `end_frame` from `{671}_ex_segmentatios_frames.xlsx`
2. Load rotvec matrix row count for same session (from `outputs/cache/matrices/671_T1_P1_R1.parquet` or equivalent)
3. Load BVH frame count
4. Apply same slice to BVH: rows `[start:end]`

Report:

| check | rotvec | BVH | pass? |
|---|---|---|---|
| full session frames | | | |
| ex11 slice length | | | |
| frame offset needed | 0 / ±N | | |

**Pass rules:**
- Slice lengths match **exactly**, or
- Documented constant offset ≤ 2 frames applied consistently to all sessions

**Decision gate C:** alignment pass → Phase D. Fail → `INCOMPATIBLE_ALIGNMENT`, stop, keep rotvec.

---

## Phase D — Build minimal feature matrix (60 min)

**Deliverable:** `results_feature_pilot/bvh_minimal/matrices/` (6 CSV or parquet files)

Per session, one wide matrix:

```
frame_index, ch1, ch2, ... chN   # only sliced ex11 rows; frame_index = Motive index
```

Requirements:
- Column names stable across sessions
- No NaN after slice (or drop bad channels with log)
- Same row count for pooled build: T1 = concat R1+R2 rows

**Optional quick QC** (5 min per session):
- max \|Δθ\| per channel — flag Euler wraps / spikes
- variance > ε on T1

**Decision gate D:** finite matrix, ≥ 8 columns, ≥ `min_rows_for_pca` (10) rows after pooled slice.

---

## Phase E — One jcvPCA run (30 min)

**Deliverable:** `results_feature_pilot/bvh_minimal/run/`

Use **existing sacred core only** — a one-off script is fine, e.g. `scripts/bvh_minimal_jcvpca.py`:

```text
A = T1 pooled (R1+R2 sliced ex11)
B = T2 pooled, T3 pooled
NV = T1 R1 vs R2 (not pooled)
features = BVH_CHANNEL_PICKLIST columns
variance_threshold = 0.80
→ compute_jcvpca → link-level table (treat each channel as one "link" OR group channels per joint — pick one, document)
```

**Aggregation choice (pick one, document):**
- **Option 1 (simplest):** each Euler channel = one feature column → jcvPCA axis-level; no RSS triplet.
- **Option 2:** group 3 Euler channels per joint with RSS → closer to link-level rotvec readout.

For minimal test, **Option 1 is enough**.

Outputs:
- `bvh_jcvpca_link_or_channel_results.csv`
- `selected_m`, comparison ids, n_rows

**Decision gate E:** run completes without ValidationError.

---

## Phase F — Compare to rotvec (30 min)

**Deliverable:** `results_feature_pilot/bvh_minimal/BVH_vs_ROTVEC_SANITY.md`

Load existing rotvec run: `results_exploration_671_252/runs/671/ex11_single/pooled/`

Compare **qualitatively** (no need for numeric identity):

| question | rotvec | BVH | agree? |
|---|---|---|---|
| Top 3 contributors changing T1→T2 | | | |
| Top 3 contributors changing T1→T3 | | | |
| Trunk/center in top ranks? | | | |
| NV: any channel/link exceeds R1–R2 floor? | | | |
| Direction: redistribution vs one global scale-up | | | |

**Verdict (pick one):**

| Verdict | Meaning | Next action |
|---|---|---|
| **COMPATIBLE_SAME_STORY** | Same regions/joints lead | Rotvec primary; BVH = 1 committee validation slide |
| **COMPATIBLE_DIFFERENT_STORY** | Both run; rankings diverge | Do not switch before mapping review; investigate naming/convention |
| **INCOMPATIBLE** | Alignment/QC/run failed | Rotvec only; document BVH blocker in brief |

---

## Minimal file checklist

```
results_feature_pilot/
  intake/
    BVH_MINIMAL_INTAKE.md
    BVH_CHANNEL_PICKLIST.csv
    BVH_ALIGNMENT_TEST.md
  bvh_minimal/
    matrices/           # 6 session matrices (ex11 slice)
    run/                # one jcvPCA output
    BVH_vs_ROTVEC_SANITY.md   # final verdict
```

---

## What you need to provide to start

1. Directory path to BVH files  
2. One example filename for `671_T1_P1_R1`  
3. Euler order / units (or sample BVH header)  
4. Confirm ex11 frame range still valid in segmentation xlsx  

---

## Success criteria (minimal)

Test **passes** if: alignment OK + jcvPCA runs + verdict is COMPATIBLE_SAME_STORY or COMPATIBLE_DIFFERENT_STORY (both are informative).

Test **does not block committee** if: INCOMPATIBLE — rotvec path unchanged.

**Do not promote BVH to primary** from this test alone; full Step 2 scorecard only if COMPATIBLE_SAME_STORY and you want angles in the methods note.
