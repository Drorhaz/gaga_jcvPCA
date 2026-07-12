# Plan — render all 12 avatar views (671 & 252)

Produce **12 static or interactive body-avatar views** plus **one investor 2×2
summary panel** from existing `avater_671_252/tables/` — without re-running
JcvPCA.

**Visual decisions are now locked** (see section 2). Implementation can proceed.

---

## 1. Mission clarity (in plain language)

### What is clear

| Dimension | Fixed choice |
|---|---|
| Participants | **671** (14 links) and **252** (16 links) — separate avatars, never merged |
| Exercise window | **ex10–ex15 contiguous**, pooled repetitions |
| Comparisons | **T1→T2** and **T1→T3** (longitudinal only; NV is not an avatar) |
| Space views | **functional** (PC1–2), **null** (PC3+), **combined** (all selected PCs) |
| NV floor | T1 R1 vs R2, within-timepoint, never pooled |
| Interpretation | Descriptive above-NV change only — **not** a treatment effect; blinded timepoints |
| Data inputs | Fully built and validated under `avater_671_252/tables/` |
| Pose | **One canonical T1 reference pose per participant** — identical across all 6 views for that participant; only colors/annotations change |

That gives **2 × 2 × 3 = 12 views**, plus **1 slide-ready 2×2 summary** (combined
space only).

### Remaining minor choices (defaults assumed)

| Item | Locked default |
|---|---|
| Body representation | Stick skeleton + shaded region capsules |
| Reference pose session | T1 R1 mean pose over ex10–ex15 frames |
| Direction encoding | Magnitude only at region level (ratio vs NV) |
| Output | 12 PNGs + 2×2 summary PNG + per-view metadata JSON + Streamlit tab |
| 671 T3 confound | Footer warning on all 671 views |

---

## 2. Locked visual design (user-approved enhancements)

### E1 — Intensity above NV (not binary) — **priority**

Only links/regions with `effect_ratio_vs_nv > 1.0` receive warm colors.
Thresholds (configurable in `render_config.yaml`):

| Ratio vs NV | Fill color | Meaning |
|---|---|---|
| ≤ 1.0 | `#B0B0B0` gray | Within natural variability |
| 1.0 – 1.5 | `#FFD700` yellow | Slightly above NV |
| 1.5 – 3.0 | `#FF8C00` orange | Moderate above NV |
| > 3.0 | `#DC143C` red | Strong above NV |

Intensity is driven by **link-level** `effect_ratio_vs_nv` for the active space.
Region capsule fill uses the **max ratio among exceeding links** in that region.

### E2 — Combined view: functional vs null dominance — **priority**

In `space=combined` renders only, each region/link uses **dual encoding** derived
from per-link functional and null `exceeds_nv` flags (join from `link_level` tables):

| Dominance | Visual |
|---|---|
| **functional-only** (`functional_only`) | Filled capsule/heatmap color (intensity per E1) |
| **null-only** (`null_only`) | Outline / glow / ring only (no fill above gray base) |
| **functional + null** (`functional_and_null`) | Filled color **+** outline ring |
| **combined-only** (`combined_only`) | Filled color (combined exceeds; neither sub-space alone) |
| **neutral** | Solid gray fill, no outline |

Outline color: `#4A90D9` blue ring (distinct from warm fill scale).

Functional/null views use **fill only** (no dual encoding) — simpler, space-pure.

### E3 — Dominant-link callouts — **priority**

Every render includes a **right side panel** listing top 3 above-NV links for the
active space, sorted by `effect_ratio_vs_nv` descending:

```text
Top above-NV links:
1. LShoulder → LUArm, ratio 36.9× NV
2. RFArm → RHand, ratio 19.4× NV
3. LShin → LFoot, ratio 2.9× NV
```

Labels use human-readable joint names from `canonical_link_name` or
`parent_joint → child_joint`. Only links with `exceeds_nv == True` are eligible.

### E4 — Mini legend on every image

Embedded legend block (bottom-left), fixed text template:

```text
Gray     = within natural variability (≤ NV)
Yellow   = slightly above NV
Orange   = moderate above NV
Red      = strong above NV
Outline  = null-space contribution (combined view)
Dashed   = unavailable / not measured
```

Plus one-line NV source: `NV floor: T1 R1 vs R2 repetition variability`.

### E5 — Self-explanatory stats (top corner)

```text
Regions above NV: 4/5
Links above NV:   10/14
Max ratio:        36.9× NV
```

- **Regions**: analytic regions from `region_space` (`head_neck`, arms, legs).
- **Links**: participant link count (14 for 671, 16 for 252).
- **Max ratio**: global max `effect_ratio_vs_nv` among exceeding links in this view.

### E6 — Investor 2×2 summary panel — **priority**

Additional deliverable: `avater_671_252/renders/summary_2x2_combined.png`

```text
┌─────────────────┬─────────────────┐
│ 671  T1 → T2    │ 671  T1 → T3    │
│  (combined)     │  (combined)     │
├─────────────────┼─────────────────┤
│ 252  T1 → T2    │ 252  T1 → T3    │
│  (combined)     │  (combined)     │
└─────────────────┴─────────────────┘
```

Each quadrant is a compact avatar (dual encoding per E2) with mini stats (E5) and
shared legend (E4). Slide-ready; no cross-participant merging of statistics.

### E7 — Missing / not measured visual state

Segments with no analytic mapping must **not** use solid gray (confusable with
within-NV):

| State | Visual | Examples |
|---|---|---|
| **within NV** | Solid gray fill | Measured, `exceeds_nv == False` |
| **above NV** | Warm intensity fill (+ outline per E2) | Measured, `exceeds_nv == True` |
| **unavailable** | Dashed gray line + `†` marker | Trunk connector (non-analytic), 671 hip-root absence |
| **participant-specific** | Dashed + footnote | `252_to_LThigh`, `252_to_RThigh` on 252 only |

Footnote on figure: `† not in analysis scope — layout only`.

### E8 — Render metadata JSON (traceability)

Per view, write `avater_671_252/renders/{view_id}.meta.json`:

```json
{
  "view_id": "671_T1_vs_T2_combined",
  "participant": "671",
  "comparison_id": "671_T1_vs_T2",
  "space": "combined",
  "regions": [
    {
      "region_id": "left_arm",
      "exceeds_nv_region": true,
      "dominance": "functional_and_null",
      "fill_color": "#DC143C",
      "outline": true,
      "effect_ratio_vs_nv_region": 4.29,
      "strongest_link": {
        "link_id": "LShoulder_to_LUArm",
        "canonical_link_name": "LShoulder->LUArm",
        "effect_ratio_vs_nv": 36.93,
        "nv_source": "T1 within-timepoint R1 vs R2 (never pooled)",
        "nv_comparison_id": "671_T1_R1_vs_R2"
      }
    }
  ],
  "top_links": [ "... top 3 ..." ],
  "stats": { "regions_above_nv": 4, "regions_total": 5, "max_ratio": 36.93 },
  "source_tables": [
    "avater_671_252/tables/region_space/671_T1_vs_T2_region_space.csv",
    "avater_671_252/tables/link_level/671_T1_vs_T2_links.csv"
  ]
}
```

Enables audit: image → region → link → ratio → NV source.

### E9 — Null-space side strip (optional, recommended)

For views where `space == null`, add a left side strip:

```text
Null-space dominant links
─────────────────────────
• LUArm → LFArm  (2.57× NV)
• Chest → Neck   (2.11× NV)
• ...
```

Lists all null-exceeding links (not just top 3), sorted by ratio. Explains highlights
that may not align with intuitive functional movement.

### E10 — Canonical pose (reinforced)

- Extract **once** per participant → `geometry/{participant}_reference_pose.json`.
- Reuse for all 12 views + 2×2 summary.
- Makes T1→T2 vs T1→T3 directly comparable within participant.

---

## 3. The 12 views + summary (render manifest)

| view_id | participant | comparison | space | expected regions above NV |
|---|---|---|---|---|
| `671_T1_vs_T2_functional` | 671 | T1→T2 | functional | 4 / 5 |
| `671_T1_vs_T2_null` | 671 | T1→T2 | null | 5 / 5 |
| `671_T1_vs_T2_combined` | 671 | T1→T2 | combined | 5 / 5 |
| `671_T1_vs_T3_functional` | 671 | T1→T3 | functional | 5 / 5 |
| `671_T1_vs_T3_null` | 671 | T1→T3 | null | 5 / 5 |
| `671_T1_vs_T3_combined` | 671 | T1→T3 | combined | 5 / 5 |
| `252_T1_vs_T2_functional` | 252 | T1→T2 | functional | 3 / 5 |
| `252_T1_vs_T2_null` | 252 | T1→T2 | null | 4 / 5 |
| `252_T1_vs_T2_combined` | 252 | T1→T2 | combined | 4 / 5 |
| `252_T1_vs_T3_functional` | 252 | T1→T3 | functional | 5 / 5 |
| `252_T1_vs_T3_null` | 252 | T1→T3 | null | 5 / 5 |
| `252_T1_vs_T3_combined` | 252 | T1→T3 | combined | 5 / 5 |

**Extra:** `summary_2x2_combined` — quadrants use `*_combined` views only.

**Analytic regions (5):** `head_neck`, `left_arm`, `right_arm`, `left_leg`, `right_leg`.

---

## 4. Required references

### A. Coloring & science

| File | Use |
|---|---|
| `avater_671_252/assumptions.md` | Space definitions, `avatar_color_category` rules |
| `avater_671_252/validation_report.md` | Table↔source ratio validation |
| `avater_671_252/provenance_manifest.json` | Source runs, comparison IDs |
| `avater_671_252/tables/group_summary.csv` | Expected region counts per view |

### B. Per-view inputs

```
tables/region_space/{671,252}_T1_vs_{T2,T3}_region_space.csv   # region rollups
tables/link_level/{671,252}_T1_vs_{T2,T3}_links.csv            # link ratios, dominance, top-3
```

**Combined-view dominance** requires joining link rows where `space` is
`functional`, `null`, and `combined` on `link_id`.

### C. Topology & geometry

| File | Use |
|---|---|
| `configs/body_regions.yaml` | Region labels |
| `data/feature_manifests/group4_core_*_feature_manifest.csv` | Link/joint topology |
| `data/raw_skeleton/{671,252}/` | T1 R1 bone positions |
| `data/segmentation/{pid}_ex_segmentatios_frames.xlsx` | ex10–ex15 frame window |
| `src/gaga_jcvpca/project_io.py` | Motive CSV parsing |

---

## 5. Implementation phases

### Phase 0 — Render config

**Deliverable:** `avater_671_252/render_config.yaml`

Locks: intensity thresholds, palette hex codes, outline color, panel layout
dimensions, font sizes, 2×2 summary layout.

### Phase 1 — Skeleton topology

**Deliverable:** `src/gaga_jcvpca/avatar_topology.py`

- Participant edge list (14 vs 16 links).
- Tag each edge: `analytic` | `layout_only` | `participant_specific`.
- Map edges → `region_id`.

### Phase 2 — Canonical reference pose

**Deliverable:** `scripts/extract_avatar_reference_pose.py`

- One pose per participant (T1 R1, ex10–ex15 mean).
- Output: `geometry/{671,252}_reference_pose.json`.

### Phase 3 — Region geometry mapper

**Deliverable:** `src/gaga_jcvpca/avatar_regions.py`

- Capsule meshes per region from joint segments.
- Dashed segments for unavailable/layout-only edges (E7).

### Phase 4 — Color & dominance mapper

**Deliverable:** `src/gaga_jcvpca/avatar_colors.py`

Functions:

- `intensity_color(ratio)` → gray/yellow/orange/red (E1)
- `dominance_style(link_id, space)` → fill/outline/both (E2)
- `top_links(df, space, n=3)` → callout list (E3)
- `null_dominant_links(df)` → side-strip list (E9)

### Phase 5 — Annotated renderer

**Deliverable:** `src/gaga_jcvpca/avatar_render.py` + `scripts/render_avatars_671_252.py`

Layout per PNG (matplotlib composite or Plotly + Pillow post-process):

```
┌──────────────────────────────────────────────────────────┐
│ Regions above NV: 4/5          Max ratio: 36.9× NV      │  ← E5
├────────────────────────────┬─────────────────────────────┤
│ Null-space dominant links  │                             │
│ (null views only, E9)      │      3D avatar              │
│                            │                             │
├────────────────────────────┤                             │
│                            │  Top above-NV links (E3)    │
│                            │  1. ...                     │
│                            │  2. ...                     │
│                            │  3. ...                     │
├────────────────────────────┴─────────────────────────────┤
│ Legend (E4)  |  Disclaimer  |  671 T3 warning (if 671)   │
└──────────────────────────────────────────────────────────┘
```

Exports per view:

- `renders/{view_id}.png`
- `renders/{view_id}.meta.json` (E8)
- `renders/{view_id}.html` (interactive, optional)

Batch:

```bash
python scripts/render_avatars_671_252.py --all
python scripts/render_avatars_671_252.py --summary-2x2
```

### Phase 6 — 2×2 summary composer

**Deliverable:** `src/gaga_jcvpca/avatar_summary.py`

Stitches four `*_combined` renders into `summary_2x2_combined.png` (E6).
Shared title: `JcvPCA body change vs natural variability | ex10–15 pooled`.

### Phase 7 — Streamlit tab

**Deliverable:** section in `ui/app.py` or `ui/pages/avatar_views.py`

- Toggles: participant / comparison / space.
- Live figure with same encoding rules.
- Download PNG + metadata JSON.

### Phase 8 — Validation

**Deliverable:** `avater_671_252/render_validation.md`

| Check | Method |
|---|---|
| 12 PNGs + 1 summary exist | file manifest |
| Region above-NV counts match `group_summary.csv` | automated |
| Max ratio in metadata matches link table | automated |
| Top-3 callouts match sorted link table | automated |
| Combined dominance matches `avatar_color_category` | per-link join |
| Dashed segments ≠ within-NV gray | visual metadata flag |
| `671_T1_vs_T2_functional`: head_neck neutral | spot check |
| Metadata traceability: every colored region has `strongest_link` | JSON schema |

---

## 6. Output tree

```text
avater_671_252/
  tables/                          # existing
  geometry/
    671_reference_pose.json
    252_reference_pose.json
  renders/
    671_T1_vs_T2_functional.png
    671_T1_vs_T2_functional.meta.json
    ...                            # 12 views × (png + meta.json)
    summary_2x2_combined.png
    summary_2x2_combined.meta.json
  render_config.yaml
  render_manifest.json             # master index of all outputs
  render_validation.md
```

---

## 7. Dependencies

- `plotly` — 3D skeleton
- `matplotlib` — 2D annotation panels, 2×2 stitch
- `pillow` — PNG compositing (if needed)
- `kaleido` — Plotly static export

---

## 8. Out of scope

- Re-running JcvPCA
- Cross-participant merged statistics
- Bootstrap significance glyphs (0 supported links)
- Anatomical mesh / animation
- Treatment-effect language

---

## 9. Acceptance criteria

1. **12 view PNGs** with E1–E5 annotations on every image.
2. **Combined views** use dual functional/null encoding per E2.
3. **Top-3 link callouts** present and numerically correct (E3).
4. **Legend + stats** on every image (E4, E5).
5. **`summary_2x2_combined.png`** exists (E6).
6. **Dashed unavailable** segments distinct from within-NV gray (E7).
7. **12 + 1 metadata JSON** files with full traceability (E8).
8. **Null views** include side strip when ≥1 null-exceeding link (E9).
9. **Same pose** per participant across all views (E10).
10. `render_validation.md` = PASS.

---

## 10. Effort estimate (revised)

| Phase | Estimate |
|---|---|
| 0 Config | 1 h |
| 1 Topology | 2–3 h |
| 2 Pose | 3–4 h |
| 3 Geometry | 2–3 h |
| 4 Color/dominance mapper | 3–4 h |
| 5 Annotated renderer | 6–8 h |
| 6 2×2 summary | 2 h |
| 7 Streamlit | 2–3 h |
| 8 Validation | 2 h |
| **Total** | **~3–4 days** |

---

## 11. Implementation priority order

Build in this sequence (matches user priority):

1. **E1** intensity scale + **E10** canonical pose
2. **E2** combined-view dual encoding
3. **E3** top-3 callouts + **E5** corner stats
4. **E4** legend
5. **E6** 2×2 summary panel
6. **E7** dashed unavailable state
7. **E8** metadata JSON
8. **E9** null-space side strip
