# Assumptions — avatar-ready tables

## Scientific interpretation

- Tables show **above-natural-variability descriptive change**, not treatment effect.
- Data are **blinded/timepoint-based** unless otherwise stated.
- NV floor is **T1 R1 vs R2** at the reference timepoint, identical for T1-vs-T2 and T1-vs-T3.

## Space definitions

- **functional**: PC1–PC2 (`sensitivity_p=2` from analysis defaults)
- **null**: PC3..selected_m
- **combined**: mean across all selected PCs from `link_level_results.csv`
- Combined is **not** functional + null summed (disjoint PC subsets).

## Exceeds-NV rule

- Link: `effect_ratio_vs_nv = long_abs_mean / (nv_abs_mean + 1e-9) > 1.0`
- NV magnitude per space comes from the matching space file's natural_variability rows.

## Region coloring rule (conservative)

- A body **region is marked for coloring** if **any** link in that region exceeds NV for the active space view.
- Region aggregate metrics are **means** of link-level abs means (descriptive rollup).
- **Top contributing link** = link with highest `effect_ratio_vs_nv` in the region.

## Avatar color categories (per link)

| Category | Condition |
|---|---|
| `neutral` | exceeds in none of functional / null / combined |
| `functional_only` | functional exceeds, null does not |
| `null_only` | null exceeds, functional does not |
| `functional_and_null` | both exceed |
| `combined_only` | combined exceeds but neither sub-space alone |

## Region mapping

- Primary: `region_id` from `analysis_selection.yaml` (persisted at analysis time)
- Labels: human names from `configs/body_regions.yaml`
- Joint names: `parent_canonical` / `child_canonical` from participant feature manifest

## Known data caveats

- Participant 671: marker-set prefix differs at T3; comparisons restricted to shared valid links.
- Participant 252: two extra hip-root links not comparable to 671.
- No `trunk_spine` region links in this exercise window selection.
