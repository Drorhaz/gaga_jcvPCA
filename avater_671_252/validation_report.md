# Validation report — avatar table build

_Generated 2026-07-07T19:48:36._

## Cross-checks performed

1. Every included selection link present in functional, null, and combined views
2. Combined `effect_ratio_vs_nv` matches `validation_results.csv` within ±0.01
3. Region ids populated (no unmapped `other` unless manifest gap)
4. Manifest warnings propagated

## Completeness matrix

| Participant | T1 vs T2 | T1 vs T3 | NV | Functional | Null | Combined |
|---|---|---|---|---|---|---|
| 671 | complete | complete | complete | complete | complete | complete |
| 252 | complete | complete | complete | complete | complete | complete |

**Overall build status:** PASS — all participant/comparison pairs complete

## Participant warnings

### 671
- Marker-set prefix differs across timepoints (['671', 'T3']). Cross-timepoint comparisons restricted to shared valid links; interpret with care.

### 252
- None beyond standard descriptive-only caveat.

## Bootstrap

- Per-link bootstrap CIs were **not** exported in source runs.
- Run-level bootstrap reported **0** links with CI excluding zero for all groups.
- Avatar tables set `bootstrap_supported_links = 0` in group summary.
