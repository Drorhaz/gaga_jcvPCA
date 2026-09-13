# Functional / null space — pooled T1 vs T3 + NV T1_R1 vs T1_R2 (by link)

**Run:** `marker_gap_policy_ex09_13` · **mode:** `ex09_13_contiguous_pooled` · **participants:** 671, 252, 651, 790

## Files

| File | Contents |
|------|----------|
| `{pid}_functional_T3_and_NV.csv` | PC1–2 (functional) per link |
| `{pid}_null_T3_and_NV.csv` | PC3–m (null) per link |
| `ALL_participants_fun_null_T3_NV.csv` | All 4 × 2 spaces stacked |

## Columns

- **T1_vs_T3_*** — longitudinal pooled **T1 vs T3** (functional/null from Step 4 pooled run)
- **NV_*** — natural variability **T1_R1 vs T1_R2** (same space decomposition)
- **`*_status`:** `included` \| `excluded` \| `missing`
- **`*_QC_exclusion`:** reason when excluded (`marker_gap_policy`, `shared_features_or_qc`, rotvec QC, etc.) — from `comparison_link_exclusions.csv`

Empty JcvPCA cells = link excluded or not in that comparison’s analysis set.

## Exclusion counts (functional space; null identical)

| Participant | Links | T1 vs T3 excluded | NV T1_R1 vs R2 excluded |
|-------------|------:|------------------:|------------------------:|
| 671 | 18 | 3 | 0 |
| 252 | 22 | 2 | 2 |
| 651 | 18 | 9 | 5 |
| 790 | 22 | 4 | 2 |

Full audit: `../../comparison_link_exclusions.csv`

## Suggested graphs

| Pack | Count | Description |
|------|------:|-------------|
| **Minimal (recommended)** | **8** | One grouped bar chart per participant × space (4×2): x = link, bars = T1 vs T3 (pooled) vs NV; hatched / grey = QC-excluded links |
| **Split comparisons** | **16** | Separate figure for T3-only and NV-only (4 participants × 2 spaces × 2 comparisons) |
| **Single slide per person** | **4** | 2×2 panel: functional T3, functional NV, null T3, null NV |
| **Cross-participant heatmap** | **2** | One heatmap functional + one null (links on y, columns = participant×comparison); poor if link sets differ |

Use **signed** `JcvPCA_mean` for direction; `JcvPCA_abs_mean` for magnitude-only view.
