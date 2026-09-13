# Marker gap tables — ex09-13 window

Per participant: all markers × sessions `T1_R1` … `T3_R2`.

**Window:** contiguous ex09–ex13 (same slice as primary jcvPCA).

**`n_gaps_gt_0p5s`:** contiguous missing-marker runs longer than 0.5 s.

**`pct_frames_in_large_gaps_of_session`:** % of **full session** frames inside large gaps (gaps detected within the ex09-13 slice only).

**`n_velocity_artifacts` / `pct_velocity_artifacts_of_window`:** frame intervals where this marker's speed exceeds the window's shared 99.97th-percentile threshold (same rule as segment QC; attributed per marker). Denominator = ex09-13 window intervals (n_frames − 1).

**`related_links`:** jcvPCA link stems from marker→bone mapping (DataDescriptions when present; else nearest bone Position in skeleton CSV). Audit maps: `data/link_mapping/marker_bone_map_{pid}.csv`.

Full CSVs: one file per participant in this folder.

## Participant 671

- Markers per session: **288**
- Sessions: **6**
- Rows with manifest link mapping: **246/524** (47%)
- CSV: [`671_ex09_13_marker_gaps.csv`](671_ex09_13_marker_gaps.csv)

Markers with largest large-gap footprint (top 12 by max % window):

| marker | max % window in large gaps | total large gaps (all sessions) | related links |
|---|---:|---:|---|
| `Unlabeled 3415` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1925` | 100.0 | 3 | unlabeled (other) |
| `Unlabeled 1901` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1902` | 100.0 | 3 | unlabeled (other) |
| `Unlabeled 1903` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1904` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1907` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1908` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1910` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1923` | 100.0 | 3 | unlabeled (other) |
| `Unlabeled 1924` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1927` | 100.0 | 3 | unlabeled (other) |

## Participant 252

- Markers per session: **85**
- Sessions: **6**
- Rows with manifest link mapping: **227/333** (68%)
- CSV: [`252_ex09_13_marker_gaps.csv`](252_ex09_13_marker_gaps.csv)

Markers with largest large-gap footprint (top 12 by max % window):

| marker | max % window in large gaps | total large gaps (all sessions) | related links |
|---|---:|---:|---|
| `252:RHME` | 100.0 | 4 | no link match |
| `252:LTAM` | 100.0 | 1 | no link match |
| `252:RTAM` | 100.0 | 2 | no link match |
| `Unlabeled 1673` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 2012` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 2014` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 2015` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 2018` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 2741` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 2742` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 2750` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 2763` | 100.0 | 1 | unlabeled (other) |

## Participant 651

- Markers per session: **265**
- Sessions: **6**
- Rows with manifest link mapping: **252/436** (58%)
- CSV: [`651_ex09_13_marker_gaps.csv`](651_ex09_13_marker_gaps.csv)

Markers with largest large-gap footprint (top 12 by max % window):

| marker | max % window in large gaps | total large gaps (all sessions) | related links |
|---|---:|---:|---|
| `Unlabeled 2014` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1609` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1611` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1612` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1620` | 100.0 | 3 | unlabeled (other) |
| `Unlabeled 1621` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1622` | 100.0 | 3 | unlabeled (other) |
| `Unlabeled 1623` | 100.0 | 3 | unlabeled (other) |
| `Unlabeled 1627` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1629` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1648` | 100.0 | 3 | unlabeled (other) |
| `Unlabeled 1651` | 100.0 | 1 | unlabeled (other) |

## Participant 790

- Markers per session: **102**
- Sessions: **6**
- Rows with manifest link mapping: **238/348** (68%)
- CSV: [`790_ex09_13_marker_gaps.csv`](790_ex09_13_marker_gaps.csv)

Markers with largest large-gap footprint (top 12 by max % window):

| marker | max % window in large gaps | total large gaps (all sessions) | related links |
|---|---:|---:|---|
| `790:LFM2` | 100.0 | 1 | no link match |
| `Unlabeled 1491` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1489` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1832` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1490` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1834` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1450` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1676` | 100.0 | 1 | unlabeled (other) |
| `Unlabeled 1492` | 100.0 | 1 | unlabeled (other) |
| `790:RFME` | 100.0 | 1 | no link match |
| `Unlabeled 1493` | 100.0 | 1 | unlabeled (other) |
| `790:LFME` | 100.0 | 2 | no link match |
