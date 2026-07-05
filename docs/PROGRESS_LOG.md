# Progress log

Short per-phase log. A phase is complete only when implemented, tested, verified,
and shown to match `MASTER_PLAN.md`.

---

## Phase 0 — Scaffold + master plan + configs + data copy

- Implemented:
  - Standalone `gaga_jcvpca/` tree (docs, configs, src, ui, tests, scripts, outputs, data).
  - `docs/MASTER_PLAN.md` (authoritative spec, both corrections folded in), `README.md`, this log.
  - Configs: `default.yaml`, `paths.yaml`, `exercise_map.yaml`, `body_regions.yaml`,
    `qc_thresholds.yaml`, `analysis_defaults.yaml` (variance_threshold=0.80,
    filter controls, participant-specific mode, optional validation).
  - Data copy: both segmentation workbooks, `*_DataDescriptions.csv` sidecars,
    671 (14-link) + 252 (16-link) feature manifests. Confirmed `exercise_id` is
    1..17, 1-indexed, in the xlsx (authoritative).
  - Project `.venv` with numpy/pandas/scipy/scikit-learn/pyarrow/openpyxl/pyyaml/pytest.
- Tests run: none yet (scaffolding phase).
- Failed: none.
- Fixed: n/a.
- Status: COMPLETE.

---

## Phase 1 — Discovery + naming unification

- Implemented:
  - `config.py` (compose configs + `science_hash`), `schemas.py` (SessionKey,
    ExerciseSegment, InventoryRow, NamingIssue, QCFinding, severity/recommendation
    vocab), `naming.py` (canonical `ex{NN}` from authoritative exercise_id; session/
    sheet parsers; three-namespace disambiguation; consistency checks incl. marker-set),
    `project_io.py` (segmentation xlsx, DataDescriptions bones + marker-set prefix,
    feature manifests, raw CSV type sniff), `inventory.py` (Project Inventory scan).
- Tests run: `pytest` — 22 tests (config, naming, project_io, inventory).
- Failed then fixed:
  1. `end_frame` NaN in 671 workbook -> skip rows with NaN start/end.
  2. Session regex `\b` failed before `_Take` suffix -> replaced with lookahead `(?=$|[_.\s])`.
  3. 671 workbook uses `end_frame_exclusive` (not `end_frame`) + duplicated blocks ->
     tolerant column resolution.
  4. Some cells contain literal `'blank'` -> `_as_int` numeric coercion, skip non-numeric.
- Verified by inspection: 2 participants (671, 252); T1/T2/T3; R1/R2; exercise_id 1..17;
  all 12 P1 sessions carry segmentation sheets; 671 marker-set difference (671 vs T3)
  correctly flagged. Sessions show `partial` because 200MB+ raw skeleton CSVs are
  referenced via `configs/paths.yaml`, not copied into the standalone tree (expected).
- Status: COMPLETE.

---

## Phase 2 — Data inventory UI (Tabs 1 & 2)

- Implemented:
  - `pipeline.py` `build_snapshot()` — single read model (inventory + summary +
    science_hash + recommended next action).
  - `ui/app.py` — slim single-app 7-tab shell with a shared sidebar navigator;
    Tab 1 Overview (metrics, next-action banner, naming/comparability notes) and
    Tab 2 Data Inventory (session table + canonical segment mapping + marker-set
    prefixes) functional; Tabs 3-7 placeholder for later phases.
  - `ui/components/widgets.py`, `ui/_bootstrap.py`.
- Tests run: `pytest` — 25 tests incl. `test_pipeline_snapshot.py`; plus a headless
  `streamlit.testing.v1.AppTest` smoke asserting no exceptions, 7 tabs, live metrics
  (Participants 2 / Timepoints 3 / Exercises 17 / Sessions 12 / ready 0).
- Failed then fixed: `use_container_width` deprecation -> `width="stretch"`.
- Status: COMPLETE.

---

## Phase 3 — Raw-marker QC

- Implemented `qc_markers.py`: compact `MarkerData`, gap detection, large-gap
  (>0.5s) critical flag + short-gap clustering, velocity-artifact detection,
  six-resolution findings (dataset/participant/timepoint/segment/link-region/frame),
  fixed severity categories + include/exclude/caution recommendations, research-language
  sentences, marker-set comparability finding, and a pragmatic Motive marker-CSV parser.
- Tests run: `pytest tests/test_qc_markers.py` (9) then full suite (34 total).
- Failed: none.
- Verified by inspection: a synthetic left-arm gap produced
  "671_T1_P1_R1::ex09::left_arm: 6.9% marker gaps in the left arm region (mainly
  frames 2,430-2,869) ... flagged critical ... Consider excluding left arm links
  from JcvPCA." — matches the plan's target style.
- Status: COMPLETE.

---

## Phase 4 — Quaternion -> rotation-vector conversion (ported)

- Implemented `rotations.py`: ported `quat_rows_to_rotvec` (SciPy log-map),
  `compute_relative_quaternions` (inv(parent)*child), `apply_sign_continuity`,
  Butterworth low-pass in tangent space (segment-wise sosfiltfilt, never fed NaNs),
  `convert_link` with per-frame flags (missing marker / invalid quaternion / rotation
  jump / near-pi branch cut) and link-level low-confidence flag, `FilterSettings`
  with a cache key that changes when any filter parameter changes (decision 5),
  and `build_link_map_from_bones` for canonical link stems.
- Tests run: `pytest tests/test_rotations.py` (9) incl. a NUMERIC PARITY test
  importing the original `layer2_motive` modules and asserting identical output
  (atol 1e-12) for rotvec conversion, relative quaternions, and sign continuity.
  Full suite: 43 passed.
- Failed then fixed: min-filtfilt-length guard underestimated scipy's padlen
  (10 vs 16 for order-4 sos) -> mirror scipy's exact ntaps-based formula.
- Status: COMPLETE.

---

## Phase 5 — Segment & link selection + Tab 4

- Implemented `selection.py`: link-stem/region mapping from `body_regions.yaml`,
  distal exclusion policy, `default_selection` combining a feature manifest with
  QC recommendations (worst-per-region), user-override tracking, shared-link
  intersection helper (cross-timepoint / cross-participant), and YAML persistence
  (`outputs/selections/<name>.yaml`). Tab 4 UI: participant + manifest + exercise
  multiselect (authoritative `exercise_id`, canonical `exNN` labels), editable
  link table with advisory QC recommendations, named save with notes.
- Tests run: `pytest tests/test_selection.py` (6); full suite 49 passed; headless
  AppTest confirms Tab 4 renders (selectboxes, exercise multiselect, save button).
- Failed: none.
- Status: COMPLETE.

---

## Phase 6 — JcvPCA analysis (ported core + orchestration)

- Implemented `jcvpca.py`: ported byte-faithful `select_selected_m_from_A`,
  `compute_jcvpca` (center A -> PCA(A) -> center B -> manual projection ->
  PCA(B_proj) -> reproject -> |B|-|A|), `aggregate_axis_to_link_rss`,
  `build_axis_table`, `validate_selected_m`, io helpers. Clean orchestration:
  `run_comparison` (longitudinal T1-vs-T2/T3 + natural-variability R1-vs-R2),
  `region_rollup`, `functional_null_split` (sensitivity_p), `restrict_to_shared_features`
  (671 T3 marker-set case: warn + record excluded links, never hard-block),
  `threshold_sweep` diagnostic (decision 1).
- Tests run: `pytest` golden + orchestration (11). GOLDEN REGRESSION carried over
  verbatim from the validated pipeline (selected_m=5, EVR, jcvpca_axis matrix, RSS
  link deltas) passes at atol 1e-8 -> ported math is numerically identical.
  Orchestration tests cover shared-link restriction, no-shared-links error,
  non-finite exclusion, threshold-sweep monotonic selected_m, functional/null split,
  min-rows gate.
- Failed: none.
- Status: COMPLETE.

---

## Phase 7 — Results + reporting + Tab 6

- Implemented `reporting.py`: `RunContext`, `write_run` producing a self-contained
  `outputs/runs/<run_id>/` with `run_summary.md` (interpretation), `config_snapshot.yaml`,
  `analysis_selection.yaml`, `jcvpca_results.csv`, `link/region/functional/null_space`
  results, `natural_variability_results.csv`, `selected_m_by_comparison.csv`,
  `threshold_sensitivity.csv`, and `reproducibility_manifest.json` (run_id, datetime,
  git hash, science_hash, variance_threshold, filter settings, per-comparison
  included/excluded links, marker-set-difference notes, input file checksums, overrides).
  Tab 6 UI: run browser showing summary + all result tables + manifest.
- Tests run: `pytest tests/test_reporting.py` (5, outputs redirected to tmp); full
  suite 65 passed; headless AppTest confirms 7 tabs render with Tab 6.
- Failed: none.
- Status: COMPLETE.

---

## Phase 8 — Optional statistical validation

- Implemented `validation.py`: strength-labeled, data-gated methods —
  natural-variability baseline (effect ratio vs R1-vs-R2, descriptive), sensitivity
  analysis (top-link ranking overlap after dropping flagged links -> sensitivity-supported
  or descriptive), PCA-basis stability (subspace cosine similarity across repetition
  matrices), and bootstrap (block resampling CIs; runs ONLY when >= min_windows clean
  windows exist, else `insufficient data`). `ValidationReport` -> `validation_results.csv`
  + `validation_summary.md`; every conclusion carries a `ValidationStrength` label.
- Tests run: `pytest tests/test_validation.py` (8); full suite 73 passed.
- Failed then fixed: end-to-end test expected `bootstrap` method present even when no
  link CI excluded zero -> added a run-level bootstrap summary conclusion.
- Status: COMPLETE.

---

## Phase 9 — Full dashboard integration + run orchestration

- Implemented `pipeline.run_analysis` tying selection -> matrices -> longitudinal
  (reference vs each timepoint) + natural-variability (R1 vs R2) comparisons ->
  optional threshold sweep + validation -> run folder, with marker-set-difference
  notes injected. Added `configs/paths.yaml` `data.matrices`, `scripts/run_analysis.py`
  (CLI), `scripts/generate_smoke_matrices.py`. Completed all 7 UI tabs: Tab 3 QC
  Review (comparability + thresholds), Tab 5 Analysis Setup (selection + timepoints +
  variance_threshold + sweep/validation toggles + Run button), Tab 7 Run History &
  Reproducibility (manifest table + inspector).
- Tests run: full suite 74 passed (incl. end-to-end smoke). Also verified the real
  CLI path: generated 6 smoke matrices, saved a default selection, ran
  `run_analysis.py --sweep --validate` -> complete run folder with coherent
  `run_summary.md` (longitudinal T1-vs-T2/T3, NV R1-vs-R2, threshold sweep, strength-
  labeled validation, marker-set caveat). Headless AppTest: 7 tabs, no exceptions.
- Failed: none.
- Status: COMPLETE.

---

## Phase 10 — Tests, smoke, docs, numeric parity

- Added `test_jcvpca_parity.py`: direct numeric parity of the ported core against
  the ORIGINAL `layer3_jcvpca.core`/`aggregation` on identical random inputs at
  thresholds 0.70/0.80/0.90 (selected_m, EVR, axis matrix, RSS link deltas all
  match to atol 1e-12). Combined with the rotvec parity test (Phase 4) and the
  golden regression (Phase 6), the sacred math is provably identical to the
  validated pipeline.
- Lint: `ReadLints` over src/ui/scripts/tests -> no errors.
- Final suite: `pytest` -> 77 passed.
- Module inventory matches MASTER_PLAN Section 13 (12 modules: config, schemas,
  project_io, naming, inventory, qc_markers, rotations, selection, jcvpca,
  validation, reporting, pipeline) plus 7-tab `ui/app.py` and 2 scripts.
- Status: COMPLETE.

---

## Skeleton-only raw input migration

- Implemented `project_io.parse_motive_take()`: single Motive skeleton CSV read for
  embedded `Type=Marker` (meters, with mm axis transform) and `Type=Bone` quaternions.
- Refactored `qc_markers.parse_motive_marker_csv` / `marker_data_from_take` to use it.
- Added `rotations.convert_session_take()` and `scripts/run_convert.py` (one parse per
  session → matrices + QC cache).
- Removed `data.raw_markers` from `paths.yaml`, inventory, schemas, and UI.
- Tests: `tests/test_motive_io.py`, integration on real 252 T1 skeleton; full suite run.
- Status: COMPLETE.

---

## Raw-marker QC dashboard wiring

- Restored `data.raw_markers` in `configs/paths.yaml` with skeleton fallback via
  `project_io.resolve_session_marker_csv()`. Inventory rows expose `has_marker_csv`.
- Added `qc_markers.run_marker_qc()` orchestration: session-level + per-segment QC,
  comparability findings, soft parse-error handling, `qc_summary.csv` cache under
  `outputs/cache/qc/`.
- Extended `pipeline.ProjectSnapshot` with `qc_findings`, `qc_summary_df`, and rollup
  metrics for Tab 1 overview.
- Tab 3 QC Review: filterable findings table (gaps, artifacts, comparability tabs),
  summary metrics, navigator-aligned filters, reference-threshold expander.
- Tab 4 passes filtered QC findings into `default_selection`; link reasons use QC
  messages; override reason required when including QC-excluded links.
- CLI: `python scripts/run_qc.py` writes offline QC cache.
- Deferred: `qc_flags.parquet` frame-level export (planned for a later phase).
- **How to use Tab 3:** link marker CSVs in `configs/paths.yaml` (`data/raw_markers/{pid}/`
  or `data/raw_skeleton/`), optionally run `python scripts/run_qc.py`, then open the
  dashboard Tab 3 and filter by participant/timepoint/severity/recommendation.
- Status: COMPLETE.

---

## Project status: COMPLETE

All ten phases implemented, tested, and verified end-to-end. The standalone
`gaga_jcvpca/` project runs discovery -> QC -> rotation-vector conversion ->
selection -> JcvPCA -> optional validation -> self-contained run folder, with a
slim 7-tab decision dashboard. The scientific core (JcvPCA math + quaternion->
rotation-vector conversion) is byte-faithful to the validated pipeline (parity +
golden tests). 77 tests pass. Raw 200MB+ skeleton CSVs are referenced via
`configs/paths.yaml` (not copied); a smoke-matrix generator lets the full pipeline
run without them.
