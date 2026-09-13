# Inventory report — avatar table sources

_Generated 2026-07-07T19:48:36._

## Target configuration

- Exercise window: **ex10_15_contiguous** (exercise_ids 10–15, combined)
- Repetition mode: **pooled** (`T1(R1+R2) vs T2/T3(R1+R2)`)
- NV floor: **T1 R1 vs R2** (within-timepoint, never pooled)
- Participants: **671** (14 links), **252** (16 links)

## Source run folders

### Participant 671
- Run: `results_exploration_671_252/runs/671/ex10_15_contiguous/pooled`
- Run id: `671_ex10_15_contiguous_pooled`
- Links included: 14
- `link_level_results.csv`: present
- `functional_space_results.csv`: present
- `null_space_results.csv`: present
- `natural_variability_results.csv`: present
- `validation_results.csv`: present
- `region_level_results.csv`: present
- `analysis_selection.yaml`: present
- `reproducibility_manifest.json`: present
- `selected_m_by_comparison.csv`: present
- Comparisons in manifest: 671_T1_vs_T2, 671_T1_vs_T3, 671_T1_R1_vs_R2

### Participant 252
- Run: `results_exploration_671_252/runs/252/ex10_15_contiguous/pooled`
- Run id: `252_ex10_15_contiguous_pooled`
- Links included: 16
- `link_level_results.csv`: present
- `functional_space_results.csv`: present
- `null_space_results.csv`: present
- `natural_variability_results.csv`: present
- `validation_results.csv`: present
- `region_level_results.csv`: present
- `analysis_selection.yaml`: present
- `reproducibility_manifest.json`: present
- `selected_m_by_comparison.csv`: present
- Comparisons in manifest: 252_T1_vs_T2, 252_T1_vs_T3, 252_T1_R1_vs_R2

## Sufficiency verdict

**Existing results are sufficient** to build avatar-ready tables for both participants across T1→T2 and T1→T3 without recomputing JcvPCA.

### Not required for tables (future renderer)

- 3D skeleton mesh / joint coordinates
- Avatar image assets

### Documented limitations (warnings only)

- 671 T3 marker-set prefix confound (cross-timepoint interpret with care)
- No trunk_spine links in these selections
- 252-only pelvis-root links: `252_to_LThigh`, `252_to_RThigh`
- Bootstrap: 0 per-link CI-supported links in these runs
- Validation strength: descriptive only (2 repetitions)
