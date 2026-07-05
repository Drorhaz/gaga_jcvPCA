# Marker vs Skeleton — Examination Results

## Verdict

**11/12 overlapping pairs pass** on shared marker names; **1 pair(s) failed** (see table). Failures indicate sessions where marker naming or tracking differs between exports — not a universal 1:1 copy.

Coordinate mapping depends on skeleton export units:

- **Millimeters** (most T1/T2 takes):

```text
marker_X = -skeleton_marker_X / 1000
marker_Y =  skeleton_marker_Z / 1000
marker_Z =  skeleton_marker_Y / 1000
```

- **Meters** (some T3 takes): positions already match marker-only exports directly.

**You do not strictly need `raw_markers/` when `raw_skeleton/` is available**, provided QC code applies the correct unit/axis mapping and handles sessions where marker name sets differ.

Practical notes:

- Skeleton exports are ~5× larger (~226 MB vs ~44 MB per take); dedicated marker files are faster when you only need QC.
- 7 skeleton file(s) have no dedicated marker export.
- `parse_motive_marker_csv` in `qc_markers.py` currently looks for `r[0] == "Type"` but Motive exports use a leading empty cell (`,Type,...`). Header detection should be fixed before wiring QC to real files.

## Comparison summary

| Session | Common markers | Max diff (m) | Presence mismatches | Passed | Notes |
|---|---:|---:|---:|---|---|
| 252_T1_P1_R1 | 56 | 6.170e-07 | 0 | yes | units differ (Meters vs Millimeters); rotation type differs (XYZ marker export vs Quaternion skeleton export) |
| 252_T1_P1_R2 | 60 | 6.070e-07 | 0 | yes | units differ (Meters vs Millimeters); rotation type differs (XYZ marker export vs Quaternion skeleton export) |
| 252_T2_P1_R1 | 59 | 6.150e-07 | 0 | yes | units differ (Meters vs Millimeters); rotation type differs (XYZ marker export vs Quaternion skeleton export) |
| 252_T2_P1_R2 | 61 | 6.110e-07 | 0 | yes | units differ (Meters vs Millimeters); rotation type differs (XYZ marker export vs Quaternion skeleton export) |
| 252_T3_P1_R1 | 49 | 0.000e+00 | 0 | yes | 27 marker name(s) only in marker export; rotation type differs (XYZ marker export vs Quaternion skeleton export) |
| 252_T3_P1_R2 | 48 | 0.000e+00 | 0 | yes | 39 marker name(s) only in marker export; rotation type differs (XYZ marker export vs Quaternion skeleton export) |
| 671_T1_P1_R1 | 102 | 6.170e-07 | 0 | yes | units differ (Meters vs Millimeters); rotation type differs (XYZ marker export vs Quaternion skeleton export) |
| 671_T1_P1_R2 | 87 | 6.130e-07 | 0 | yes | units differ (Meters vs Millimeters); rotation type differs (XYZ marker export vs Quaternion skeleton export) |
| 671_T2_P1_R1 | 69 | 6.210e-07 | 0 | yes | units differ (Meters vs Millimeters); rotation type differs (XYZ marker export vs Quaternion skeleton export) |
| 671_T2_P1_R2 | 77 | 5.610e-07 | 1641666 | NO | 54 marker name(s) only in marker export; units differ (Meters vs Millimeters); rotation type differs (XYZ marker export vs Quaternion skeleton export) |
| 671_T3_P1_R1 | 74 | 6.210e-07 | 0 | yes | units differ (Meters vs Millimeters); rotation type differs (XYZ marker export vs Quaternion skeleton export) |
| 671_T3_P1_R2 | 115 | 6.170e-07 | 0 | yes | units differ (Meters vs Millimeters); rotation type differs (XYZ marker export vs Quaternion skeleton export) |

### Failed pair detail: `671_T2_P1_R2`

The marker-only export contains **duplicate naming** for the same physical markers: empty `671:*` columns alongside populated `FKA-671_*` columns (54 extra names). The skeleton export only includes the `671:*` names with full tracking data. Positions match when both are present (`max_diff ≈ 6×10⁻⁷` m), but presence on shared `671:*` names differs because the marker export stores data under `FKA-671_*` instead. **Use skeleton as source for this session**, or map `FKA-671_*` ↔ `671:*` before comparing.

## File sizes (representative pair)

- `data/raw_markers/252/252_T1_P1_R1_Take 2026-04-28 04.15.00 PM_000.csv`: 44.2 MB (Meters)
- `data/raw_skeleton/252/T1/252_T1_P1_R1_Take 2026-04-28 04.15.00 PM_000.csv`: 225.5 MB (Millimeters)

## Coverage

- Marker-only files: 12
- Skeleton files: 19
- Skeleton-only (no marker export): 7

### Skeleton-only sessions

- `data/raw_skeleton/252/T1/252_T1_P2_R1_Take 2026-04-28 04.15.00 PM_001.csv`: 74 markers, 23226 frames, units=Millimeters
- `data/raw_skeleton/252/T1/252_T1_P2_R2_Take 2026-04-28 04.15.00 PM_004.csv`: 87 markers, 23293 frames, units=Millimeters
- `data/raw_skeleton/252/T2/252_T2_P2_R1_Take 2026-04-26 06.09.29 PM_002.csv`: 111 markers, 23264 frames, units=Millimeters
- `data/raw_skeleton/252/T2/252_T2_P2_R1_Take 2026-04-26 06.09.29 PM_003.csv`: 49 markers, 10 frames, units=Millimeters
- `data/raw_skeleton/252/T2/252_T2_P2_R2_Take 2026-04-26 06.09.29 PM_005.csv`: 80 markers, 23667 frames, units=Millimeters
- `data/raw_skeleton/252/T3/252_T3_P2_R1_Take 2026-06-09 05.04.14 PM_000.csv`: 49 markers, 23505 frames, units=Meters
- `data/raw_skeleton/252/T3/252_T3_P2_R2_Take 2026-06-09 05.04.14 PM_002.csv`: 49 markers, 23549 frames, units=Meters

## Spot checks

Spot checks for `252_T1_P1_R1_Take 2026-04-28 04.15.00 PM_000.csv`:
  - 252:LAH frame 100: max_diff=3.460e-07 m
  - 252:LAH frame 1000: max_diff=3.970e-07 m
  - 252:LAH frame 5000: max_diff=4.180e-07 m
  - 252:LAH frame 10000: max_diff=4.910e-07 m
  - 252:CV7 frame 100: max_diff=4.410e-07 m
  - 252:CV7 frame 1000: max_diff=4.470e-07 m
  - 252:CV7 frame 5000: max_diff=4.980e-07 m
  - 252:CV7 frame 10000: max_diff=4.570e-07 m
  - 252:LFM1 frame 100: max_diff=4.860e-07 m
  - 252:LFM1 frame 1000: max_diff=3.030e-07 m
  - 252:LFM1 frame 5000: max_diff=3.170e-07 m
  - 252:LFM1 frame 10000: max_diff=2.680e-07 m
  - 252:RUA frame 100: max_diff=4.620e-07 m
  - 252:RUA frame 1000: max_diff=4.500e-07 m
  - 252:RUA frame 5000: max_diff=4.380e-07 m
  - 252:RUA frame 10000: max_diff=4.820e-07 m
  - 252:SJN frame 100: max_diff=3.250e-07 m
  - 252:SJN frame 1000: max_diff=4.480e-07 m
  - 252:SJN frame 5000: max_diff=4.690e-07 m
  - 252:SJN frame 10000: max_diff=2.230e-07 m
  - Unlabeled 2739 frame 100: max_diff=3.430e-07 m
  - Unlabeled 2739 frame 1000: max_diff=2.580e-07 m
  - Unlabeled 2739 frame 5000: max_diff=3.760e-07 m
  - Unlabeled 2739 frame 10000: max_diff=3.110e-07 m
Spot checks for `671_T1_P1_R1_Take 2026-01-06 03.57.12 PM_001.csv`:
  - 671:BackLeft frame 100: max_diff=4.380e-07 m
  - 671:BackLeft frame 1000: max_diff=4.470e-07 m
  - 671:BackLeft frame 5000: max_diff=4.780e-07 m
  - 671:BackLeft frame 10000: max_diff=4.870e-07 m
  - 671:BackRight frame 100: max_diff=4.700e-07 m
  - 671:BackRight frame 1000: max_diff=3.720e-07 m
  - 671:BackRight frame 5000: max_diff=3.110e-07 m
  - 671:BackRight frame 10000: max_diff=2.320e-07 m

## Decision table

| Need | raw_markers | raw_skeleton |
|---|---|---|
| JcvPCA rotations | No | Yes (Bone quaternions) |
| Marker gap QC | Yes (standalone) | Yes (embedded Marker cols) |
| All sessions covered | 12/19 | 19/19 |

## Recommendation

Prefer skeleton as the canonical marker source when available (covers extra sessions). Keep `raw_markers/` as an optional convenience for faster QC-only loads.
