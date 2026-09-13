# Avatar-ready tables — ex10_15_contiguous | pooled (671 & 252)

Tabular foundation for a future 3D body-avatar visualization module. Built from
existing JcvPCA run outputs only; no new analyses and no avatar images.

## Configuration

- Participants: **671** (14 links), **252** (16 links)
- Exercise window: **ex10–ex15 contiguous**, combined
- Repetition mode: **pooled**
- Comparisons: **T1 vs T2**, **T1 vs T3**
- NV floor: **T1 R1 vs R2** (within-timepoint, never pooled)

## Source runs

- `results_exploration_671_252/runs/671/ex10_15_contiguous/pooled/`
- `results_exploration_671_252/runs/252/ex10_15_contiguous/pooled/`

## Builder

```bash
python scripts/build_avatar_tables_671_252.py
```

## Outputs

See `provenance_manifest.json` for the full file index. Key tables:

- `tables/link_level/` — per-link × space (functional / null / combined)
- `tables/region_level/` — combined-space region summary
- `tables/region_space/` — functional / null / combined region views
- `tables/group_summary.csv` — cross-participant descriptive summary

## Documentation

- `inventory_report.md` — what exists / what is missing
- `assumptions.md` — coloring rules, rollups, caveats
- `validation_report.md` — cross-checks and warnings
