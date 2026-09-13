# Marker → link maps by session (ex09-13 window)

Per participant, all sessions `T1_R1` … `T3_R2`. Spatial bone assignment is computed **per session** on that session's ex09-13 slice. When a session CSV lacks bone Position channels (e.g. some T3 takes), mapping falls back to the participant reference session (`T1_R1` when present) — see `bone_source=reference_session`. DataDescriptions rows are merged when present.

## Files

| File | Use when |
|---|---|
| `{pid}_marker_to_link_by_session.csv` | Audit a specific marker across sessions; filter by `mapping_status` |
| `{pid}_link_to_markers_by_session.csv` | See which markers feed each jcvPCA link in each session |

## Column guide (marker-centric CSV)

- **`attached_bone_token`**: skeleton bone the marker is assigned to
- **`bone_source`**: `descriptions` | `spatial` | `reference_session` | `none`
- **`reference_session_for_fallback`**: session used when this row's bone came from reference fallback
- **`related_links`**: manifest link stem(s) touching that bone (or status text if unmapped)
- **`mapping_status`**: `manifest_link` | `bone_no_manifest_link` | `no_link_match` | `unlabeled`

## Recommended ways to show this

1. **Supervisor table (link-centric)** — open `{pid}_link_to_markers_by_session.csv`, pivot/filter on `link_stem` and scan `T_R` columns for marker coverage. Best for "which links are supported in T3 vs T1?"

2. **QC audit (marker-centric)** — open `{pid}_marker_to_link_by_session.csv`, sort by `mapping_status != manifest_link`. Best for explaining unmapped finger/toe markers.

3. **Slide figure (heatmap)** — rows = canonical link stems, columns = `T1_R1`…`T3_R2`, cell = `n_markers` from link-centric CSV (0 = gray, ≥1 = green). One panel per participant.

4. **Do not** use a full marker×session matrix in slides — too sparse; use link-centric summary instead.

## Participant summaries

### Participant 671

- Sessions: **6**
- Mean markers per session: **87**
- Rows with manifest link mapping: **270/524** (52%)
- Marker CSV: [`671_marker_to_link_by_session.csv`](671_marker_to_link_by_session.csv)
- Link CSV: [`671_link_to_markers_by_session.csv`](671_link_to_markers_by_session.csv)

| T_R | markers | manifest-mapped |
|---|---:|---:|
| T1_R1 | 102 | 45 |
| T1_R2 | 87 | 45 |
| T2_R1 | 69 | 45 |
| T2_R2 | 77 | 45 |
| T3_R1 | 74 | 45 |
| T3_R2 | 115 | 45 |

### Participant 252

- Sessions: **6**
- Mean markers per session: **56**
- Rows with manifest link mapping: **231/333** (69%)
- Marker CSV: [`252_marker_to_link_by_session.csv`](252_marker_to_link_by_session.csv)
- Link CSV: [`252_link_to_markers_by_session.csv`](252_link_to_markers_by_session.csv)

| T_R | markers | manifest-mapped |
|---|---:|---:|
| T1_R1 | 56 | 38 |
| T1_R2 | 60 | 40 |
| T2_R1 | 59 | 39 |
| T2_R2 | 61 | 39 |
| T3_R1 | 49 | 38 |
| T3_R2 | 48 | 37 |

### Participant 651

- Sessions: **6**
- Mean markers per session: **73**
- Rows with manifest link mapping: **241/436** (55%)
- Marker CSV: [`651_marker_to_link_by_session.csv`](651_marker_to_link_by_session.csv)
- Link CSV: [`651_link_to_markers_by_session.csv`](651_link_to_markers_by_session.csv)

| T_R | markers | manifest-mapped |
|---|---:|---:|
| T1_R1 | 66 | 42 |
| T1_R2 | 74 | 42 |
| T2_R1 | 75 | 40 |
| T2_R2 | 83 | 40 |
| T3_R1 | 67 | 39 |
| T3_R2 | 71 | 38 |

### Participant 790

- Sessions: **6**
- Mean markers per session: **58**
- Rows with manifest link mapping: **235/348** (68%)
- Marker CSV: [`790_marker_to_link_by_session.csv`](790_marker_to_link_by_session.csv)
- Link CSV: [`790_link_to_markers_by_session.csv`](790_link_to_markers_by_session.csv)

| T_R | markers | manifest-mapped |
|---|---:|---:|
| T1_R1 | 66 | 40 |
| T1_R2 | 63 | 39 |
| T2_R1 | 50 | 39 |
| T2_R2 | 51 | 39 |
| T3_R1 | 58 | 39 |
| T3_R2 | 60 | 39 |
