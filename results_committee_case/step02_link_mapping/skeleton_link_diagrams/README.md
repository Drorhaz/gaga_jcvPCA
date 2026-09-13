# Skeleton link diagrams

Stick-figure reference pose (T1 R1 mean, ex10–15) with arrows labeled by jcvPCA **link stem** from each participant's feature manifest.

## Files

| PNG | Description |
|---|---|
| `{pid}_skeleton_link_map.png` | Per-participant diagram (correct `{pid}_to_*` pelvis labels) |
| `setup_a_671_reference_link_map.png` | Setup A (671-style) skeleton reference |
| `setup_b_252_reference_link_map.png` | Setup B (252-style) skeleton reference |

Gray dashed segments = bone hierarchy connectors (layout only). Colored arrows = analytic links used in jcvPCA.

Regenerate:
```bash
PYTHONPATH=src .venv/bin/python scripts/render_skeleton_link_diagrams.py
```