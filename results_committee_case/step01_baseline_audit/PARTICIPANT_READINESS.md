# Participant readiness — Step 1

**Audit date:** 2026-07-14  
**Target:** four participants on `ex09_13_contiguous` pooled (v4 primary window)

---

## Summary table

| ID | Segmentation xlsx | P1 sheets | Raw skeleton CSVs | Rotvec matrices | Manifest | Topology | `ex09_13` pooled run | Ready for Step 4? |
|---|---|---:|---:|---:|---|---|---|---|
| **671** | Yes | 6/6 | 6/6 | **6/6** | 14-link 671-style | Setup A | **Yes** (exploration) | After Step 2–3 (trunk) |
| **252** | Yes | 6/6 | 6/6 | **6/6** | 16-link 252-style | Setup B | **Yes** (exploration) | After Step 2–3 (trunk) |
| **651** | Yes | 6/6 | 6/6 | **1/6** | 14-link (template) | Setup A (expected) | **No** | **No** — convert + map first |
| **790** | Yes | 6/6 | 6/6 | **1/6** | 16-link (template) | Setup B (expected) | **No** | **No** — convert + map first |

**Ready for Step 4** = all six sessions converted, trunk-inclusive manifest from Step 2–3, fresh committee run — not met by any participant yet.

---

## Per participant

### 671

- **Segmentation:** `data/segmentation/671_ex_segmentatios_frames.xlsx` — sheets `671 - T1P1R1` … `T3P1R2`; ex09–ex13 present on all sheets (verified 2026-07-14).
- **Matrices:** `671_T1_P1_R1` … `671_T3_P1_R2` in `outputs/cache/matrices/`.
- **Baseline snapshot:** `step01_baseline_audit/671/ex09_13_contiguous_pooled/`.
- **Gaps:** trunk links; committee rerun after Step 3.

### 252

- **Segmentation:** `data/segmentation/252_ex_segmentatios_frames.xlsx` — 6 sheets; ex09–ex13 complete.
- **Matrices:** 6/6 sessions cached.
- **Extra links:** `252_to_LThigh`, `252_to_RThigh` (non-comparable to 671).
- **Baseline snapshot:** `step01_baseline_audit/252/ex09_13_contiguous_pooled/`.
- **Gaps:** trunk links; committee rerun after Step 3.

### 651

- **Segmentation:** `data/segmentation/651_ex_segmentatios_frames.xlsx` — 6 sheets (`651- T…` naming).
- **Matrices:** only `651_T1_P1_R1.parquet` — **missing T1_R2, T2×2, T3×2**.
- **Manifest:** `group4_core_14link_within_651_feature_manifest.csv` (template-derived; not yet mapped from hierarchy audit).
- **DataDescriptions:** 6 files under `data/descriptions/`.
- **Actions before Step 4:** Step 2 topology confirm → Step 3 `run_convert.py` for 5 missing sessions → `651_ex09_13_contiguous.yaml` → primary run.

### 790

- **Segmentation:** `data/segmentation/790_ex_segmentatios_frames.xlsx` — 6 sheets (`790- T…` naming).
- **Matrices:** only `790_T1_P1_R1.parquet` — **5 sessions missing**.
- **Manifest:** `group4_core_16link_within_790_feature_manifest.csv` (template-derived).
- **DataDescriptions:** 6 files.
- **Actions:** same as 651 (Setup B expected).

---

## Protocol window artifacts on disk

| Artifact | 671 | 252 | 651 | 790 |
|---|---|---|---|---|
| Selection YAML `*_ex09_13_contiguous.yaml` | `results_exploration_671_252/selections/` | Yes | No | No |
| Exploration run folder | Yes | Yes | No | No |
| Step 1 snapshot copy | Yes | Yes | — | — |

---

## Blocking items before Step 4 (all participants)

1. **Step 2:** `canonical_link_map.csv` + skeleton baseline assignment  
2. **Step 3:** trunk-inclusive manifests, inclusive QC, full convert (651/790 priority)  
3. **Step 0** (if not done): claim/naming docs in `step00_claim_framework/`

---

## File paths (quick reference)

```
data/segmentation/{671,252,651,790}_ex_segmentatios_frames.xlsx
data/raw_skeleton/{pid}/*.csv
data/feature_manifests/group4_core_*_{pid}_feature_manifest.csv
outputs/cache/matrices/{pid}_T{t}_P1_R{r}.parquet
results_exploration_671_252/runs/{671,252}/ex09_13_contiguous/pooled/
results_committee_case/step01_baseline_audit/{671,252}/ex09_13_contiguous_pooled/
```
