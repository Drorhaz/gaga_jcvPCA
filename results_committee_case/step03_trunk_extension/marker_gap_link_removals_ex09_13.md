# Marker-gap link removals (ex09-13)

Advisory table: links to **withhold from comparisons** that use the listed session/rep.
Does not remove links globally from the participant selection YAML.

## Policy

- **remove_from_comparison:** max supporting-marker gap >= 10% OR >= 2 markers each >= 5% (large gap = contiguous missing > 0.5 s)
- **watch:** max gap 5–10% — document only

**Rows:** 33 total (17 remove, 16 watch)

## Regenerate

```bash
PYTHONPATH=src .venv/bin/python scripts/build_marker_gap_link_removals.py
```

## Wire to pipeline

See `docs/MARKER_GAP_REMOVAL_WIRING.md`.
