# Pilot protocol — feature-stream comparison for jcvPCA

**Status:** ready to run when feature streams arrive  
**Goal:** Decide whether relative rotvecs (current default), BVH/Euler channels, and/or an existing ISB-from-quaternion pipeline are preferable as the **input features** to the same paper-faithful jcvPCA core.  
**Non-goal:** Do not change `compute_jcvpca` / RSS aggregation / golden math. Only the feature matrices fed to A/B change.

---

## 0. Decision in one sentence

Prefer the stream that, on the same sessions/windows/design, gives **clearer longitudinal change above the T1 R1–R2 NV floor**, with **stable rankings**, **acceptable continuity QC**, and **honest physiological interpretability** — without inventing significance from 2 repetitions.

---

## 1. Streams under test

| ID | Stream | Source | Notes |
|---|---|---|---|
| `S0_rotvec` | Relative rotation vectors (`*_rx/_ry/_rz`) | Current `gaga_jcvpca` pipeline | Baseline / control |
| `S1_bvh_euler` | BVH / Euler joint channels | User-supplied export | Requires frame + name alignment |
| `S2_isb_quat` | ISB-style angles from quaternions | Existing external pipeline (validity uncertain) | Fast candidate; must pass QC gate |

Add more rows only if a third export appears; keep IDs stable.

**Sacred rule:** all streams use the same jcvPCA operator, variance threshold, NV design, and windows.

---

## 2. Fixed analysis design (identical across streams)

Copied from exploration defaults so streams are comparable:

| Parameter | Value |
|---|---|
| Participants | `671`, `252` |
| Pilot windows (primary) | 671: `ex11_single` pooled; 252: `ex10_14_contiguous` pooled |
| Secondary check (optional) | each participant’s next-best group from `decision_log.md` |
| Reference | T1 always = A |
| Longitudinal | T1 vs T2, T1 vs T3 |
| NV | within-T1 `R1 vs R2` only (never pooled) |
| Repetition mode | pooled for longitudinal; single as sensitivity |
| `variance_threshold` | `0.80` (+ sweep `0.70/0.80/0.90`) |
| `sensitivity_p` | `2` (functional/null labeling only) |
| Filter (rotvec only) | Butterworth 10 Hz, order 4 |
| Validation | NV baseline + PCA stability + threshold sweep; bootstrap if windows allow |
| Inference | within-participant only; descriptive language |

Output root:

```
results_feature_pilot/
  PLAN.md          # this protocol (symlink or copy)
  intake/
  qc/
  runs/{stream}/{pid}/{window}/{mode}/
  scorecards/
  decision_log.md
```

---

## 3. Intake checklist (blockers before any jcvPCA)

For **each** non-rotvec stream, require:

1. **Session coverage:** T1/T2/T3 × R1/R2 for 671 and 252 (P1), or explicit missing list.
2. **Time base:** Motive-compatible frame index **or** documented mapping to segmentation `start_frame`/`end_frame`.
3. **Channel dictionary:** joint/DOF name, units (rad/deg), Euler order / ISB convention, parent–child definition.
4. **Alignment test:** on one take, length or frame span matches rotvec matrix after the same exercise slice (±0 frames preferred; ≤2 frame offset documented).
5. **Shared feature set:** list of channels present in all compared timepoints (671-T3 marker-set caveat applies).

If (2) or (4) fails → stop; fix export before scoring.

### Stream-specific intake

**`S1_bvh_euler`**
- BVH or tidy CSV of per-frame Euler channels
- Document rotation order (e.g. ZXY) and whether channels are local or global
- Prefer pre-extracted channels over parsing hierarchy mid-pilot

**`S2_isb_quat`**
- Path to pipeline + exact commit/config used
- Short validity note from owner (known issues OK if listed)
- Must pass §4 QC gate before entering the scorecard as a contender

**`S0_rotvec`**
- Reuse existing converted matrices / exploration selections; do not re-derive unless cache is stale

---

## 4. QC gate (must pass to be scorecard-eligible)

Per stream × session (at least T1_R1 and T3_R1):

| Check | Pass rule |
|---|---|
| Finite values | no NaN/Inf in selected channels after slice |
| Continuity | jump rate below agreed threshold (document; flag near ±π wraps for Euler) |
| Constant channels | drop or exclude DOFs with near-zero variance on T1 |
| Cross-timepoint overlap | ≥ agreed shared DOF count; log dropped channels |
| ROM sanity (spot) | angles on a simple window look physiologically plausible |

**`S2_isb_quat` rule:** if continuity or ROM sanity fails → label `exploratory_only`; do not let it beat `S0` on interpretability alone.

---

## 5. Run matrix

For each stream that passes intake + QC:

```
for pid in {671, 252}:
  for window in {primary_winner[, secondary]}:
    for mode in {pooled, single}:  # longitudinal uses mode; NV always single-rep R1vsR2
      run jcvPCA + NV + threshold sweep (+ validate if enabled)
```

Minimum viable pilot (fast path):

- Streams: `S0`, plus whichever of `S1`/`S2` arrives first  
- Windows: primary winners only  
- Modes: pooled longitudinal + NV  
- Participants: both  

Full pilot adds secondary windows + single-rep longitudinal + bootstrap when sufficient.

---

## 6. Scorecard — how we decide “better”

Per stream × participant × window, compute:

| Metric | Definition | Prefer |
|---|---|---|
| `n_links_exceeding_nv` | count of links with `effect_ratio > 1` on T1–T2 and T1–T3 | higher, if NV not inflated |
| `mean_effect_ratio` | mean \|long\| / (\|NV\|+eps) | higher |
| `nv_magnitude` | mean \|NV Δ\| across links | lower (less noisy floor) |
| `rank_stability_pooled_vs_single` | overlap of top-5 links | higher |
| `rank_stability_threshold` | top-5 overlap across 0.70/0.80/0.90 | higher |
| `selected_m_stability` | range of `selected_m` across modes/thresholds | tighter |
| `pca_stability` | loading similarity T1_R1 vs T1_R2 (existing validation) | higher / “stable” |
| `qc_fail_rate` | fraction of channels/sessions failing §4 | lower |
| `story_agreement` | same body regions exceed NV as `S0`? (Jaccard on regions) | report; not a sole winner rule |
| `interpretability` | can state a clear DOF-level sentence? (0–2 rubrics) | higher only if QC passed |

Write one row per stream into `scorecards/summary.csv` and a short `scorecards/summary.md`.

### Decision rules

1. **Keep `S0` as default** unless another stream wins on **NV separability + rank stability + QC**, not interpretability alone.
2. **Promote a stream to parallel track** if it wins those three for both participants (or wins one clearly and ties the other).
3. **Reject / exploratory_only** if QC fails, frame alignment fails, or rankings flip under tiny threshold changes while `S0` does not.
4. **Do not switch production default** from a single participant win.
5. If streams **disagree on region story** and both pass QC → no switch; investigate feature definition (Euler order / ISB axes / link set) before choosing.

### What “better” does *not* mean

- Larger raw JcvPCA numbers  
- Closer numeric match to the paper’s 2-DoF example  
- Prettier avatar colors  
- Any causal / drug language

---

## 7. Execution phases

| Phase | Action | Exit criterion |
|---|---|---|
| A | Lock this protocol; create `results_feature_pilot/` | folder exists |
| B | Intake `S1` and/or `S2` files + dictionaries | checklist green or blockers listed |
| C | QC gate report | pass/fail per stream |
| D | Re-run `S0` on pilot windows (reference snapshot) | rotvec scorecard rows exist |
| E | Run jcvPCA for passed alt streams | run folders complete |
| F | Build scorecard + `decision_log.md` | verdict written |
| G | Optional: wire winning alt stream as optional feature backend | only if promoted |

**Blocked until:** user drops BVH/Euler and/or ISB exports (or paths) into the project / points to them.

---

## 8. Deliverables

- `results_feature_pilot/qc/{stream}_qc.md`
- `results_feature_pilot/runs/...` (mirrors exploration layout)
- `results_feature_pilot/scorecards/summary.csv` + `summary.md`
- `results_feature_pilot/decision_log.md` with one of:
  - `keep_S0_rotvec`
  - `add_parallel_S1_or_S2`
  - `needs_fix_export`
  - `inconclusive_investigate_features`

---

## 9. Owner inputs still needed

1. BVH/Euler files (or path) for pilot sessions + Euler order note  
2. ISB pipeline path + how to export per-frame angles for the same sessions  
3. Confirm primary windows above, or nominate different ones  
4. Optional: continuity jump threshold preference (else use rotvec-analogous defaults)

When those arrive, start at Phase B — no sacred-core changes required for the pilot.
