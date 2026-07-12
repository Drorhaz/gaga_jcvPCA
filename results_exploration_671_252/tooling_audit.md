# Tooling audit and scalability recommendations

This documents the core upgrades made for the ex09-15 contiguous jcvPCA sweep of
participants 671 and 252, what was verified, and how the tooling scales to
ex01-ex17 and additional participants. The golden jcvPCA math
(`compute_jcvpca`, `select_selected_m_from_A`, `aggregate_axis_to_link_rss`,
`build_axis_table`) was not touched; only the data fed into it changed.

## What changed in the core

1. Skeleton-hierarchy resolution with a raw-header fallback
   (`scripts/run_convert.py`, `src/gaga_jcvpca/project_io.py`,
   `src/gaga_jcvpca/rotations.py`).
   - Resolution order per session, each gated by how many manifest links it can
     actually convert on that session's take: exact per-session DataDescriptions
     sidecar, then same-participant sidecar (same timepoint first), then the
     session's own raw skeleton CSV header hierarchy.
   - The raw skeleton export already carries the full bone topology in its header
     (`Type`/`Name`/`Parent` rows), so the parent/child hierarchy is available
     from the session's own file without any sidecar and without inventing data.
   - This was necessary because the plan's stated sidecar inventory was wrong in
     practice: all three 252 DataDescriptions sidecars are 0-byte placeholders,
     and the 671-T3 sidecar is the marker-set-confounded one (`T3_671_*` bones),
     which yields link stems that do not match the feature manifest.

2. Exercise-window slicing (`src/gaga_jcvpca/pipeline.py`,
   `slice_matrix_to_exercises`). Because conversion keeps matrix row index equal
   to the Motive frame number (0-based, contiguous), each window is a plain
   `df.iloc[start:end]` (half-open, matching segmentation semantics), concatenated
   in frame order. Windows outside the matrix bounds are clamped/skipped, and if
   nothing overlaps the full matrix is returned so callers always have data.

3. Repetition mode (`src/gaga_jcvpca/pipeline.py`). `repetition_mode`:
   - `single` (fallback): `T1_R1 vs Tk_R1`.
   - `pooled` (ideal): `T1(R1+R2) vs Tk(R1+R2)`.
   Natural variability is always the within-timepoint `T1_R1 vs T1_R2` (never
   pooled), preserving the noise floor. T1 remains the reference PCA space and
   centering stays independent per side.

4. NV baseline for every longitudinal comparison
   (`src/gaga_jcvpca/validation.py`). `run_validation` now scores
   `effect_ratio_vs_nv` for both `T1-vs-T2` and `T1-vs-T3` (tagged in each
   conclusion's scope as `<link>@<comparison_id>`), removing the need for separate
   `--timepoints T1 T3` runs.

5. CLI/UI surface. `scripts/run_analysis.py` gained `--repetitions` and
   `--repetition-mode {single,pooled}`; Tab 5 in `ui/app.py` gained a repetition
   mode selector and surfaces the sliced exercise windows.

6. Robustness fix. `find_segmentation_workbooks` now skips Excel lock files
   (`~$*.xlsx`) and dotfiles, which previously crashed `build_inventory`.

## What was verified

- Full existing test suite: 102 passed, 4 skipped (pre-change baseline).
- New `tests/test_exploration_core.py` (10 tests): slicing selection/order/
  fallback, raw-header hierarchy resolving 16/16 (252) and 14/14 (671-T3) manifest
  links, empty-sidecar rejection, Excel-lock-file skipping, NV scored across both
  longitudinal comparisons, and a pooled end-to-end run with pooled side labels.
- Fresh conversion of all 12 P1 sessions (671 + 252) from raw; sources recorded in
  `outputs/cache/conversion_manifest.json` (671-T1/T2 via the T1 sidecar, 252 and
  671-T3 via the raw-header fallback).
- 112 analyses (2 participants x 28 contiguous spans x 2 repetition modes) with
  `--validate`; results copied under `runs/`, ranked in `summaries/ranking.csv`,
  and summarized in `decision_log.md`.

## Scalability recommendations (ex01-ex17, many participants)

- Slicing and pooling key off the authoritative `exercise_id` and any contiguous
  span; nothing is hardcoded to Group 4. `scripts/run_exploration_671_252.py`
  takes `--participants` and `--ex-range START END`, so ex01-ex17 and new
  participants work with no code change.
- The raw-header hierarchy fallback removes the per-take sidecar bottleneck as the
  cohort grows: any session with a valid raw skeleton CSV can be converted.
- Keep the batch driver argument-driven; it already generalizes to N participants
  x M contiguous groups and logs the chosen hierarchy source per session.
- Add a cross-participant SUMMARY aggregator that stacks per-participant results
  for reporting while keeping every statistic within-participant (descriptive,
  never pooled inference across people). `summaries/ranking.csv` is already in a
  shape that supports this.
- Bootstrap sufficiency: single exercises (~1-2k frames) clear the 4-window gate
  but produced no CI-excludes-zero links here; contiguous spans are more
  comfortable. The ranking down-weights single-exercise windows accordingly.
- Auditability: `reproducibility_manifest.json` records the repetition mode via the
  comparison labels (`T1_R1+R2`), selected_m per comparison, the selection
  (exercise_ids + links), and marker-set-difference notes;
  `outputs/cache/conversion_manifest.json` records the chosen skeleton hierarchy
  source and link coverage per session.

## Known limitations (carried from the plan)

- Only 2 repetitions, so the R1-vs-R2 NV is a descriptive floor, not significance;
  the paper builds NV from many within-condition random splits (documented
  mismatch).
- Gaga is improvisational, so within-timepoint variability is high and can mask
  signal.
- 671 uses a different marker-set prefix at T3 (`T3_671`) than at T1/T2 (`671`).
  Each session's hierarchy is taken from its own raw header, so stems are
  self-consistent; cross-timepoint comparisons still restrict to shared valid
  links, and 671 (14 links) vs 252 (16 links) are never merged.
