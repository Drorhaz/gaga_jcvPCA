---
name: jcvpca exploration 671 252
overview: Implement exercise-window slicing, pooled-repetition longitudinal comparisons, and a DataDescriptions sidecar fallback in the gaga_jcvpca core (golden jcvPCA math untouched), reconvert all 12 P1 sessions fresh, then screen ex09-ex15 and every contiguous group for participants 671 and 252 to find the strongest longitudinal jcvPCA signal against the R1-vs-R2 NV floor plus bootstrap.
todos:
  - id: sidecar-fallback
    content: Add per-participant/marker-set DataDescriptions fallback in project_io/run_convert so all P1 sessions convert without a per-take sidecar
    status: pending
  - id: slicing-core
    content: Implement segmentation-window slicing (by exercise_ids + combine_exercises) at matrix load in pipeline.run_analysis; row index == Motive frame
    status: pending
  - id: pooling-core
    content: Add repetition_mode (single|pooled) so longitudinal builds T1(R1+R2) vs T2/T3(R1+R2); keep NV as within-timepoint R1 vs R2
    status: pending
  - id: nv-all-longitudinal
    content: Extend validation.natural_variability_baseline to score every longitudinal comparison (T1-vs-T2 and T1-vs-T3), not just the first
    status: pending
  - id: cli-ui
    content: Add --repetitions/--repetition-mode CLI flags and Tab 5 UI controls for repetition mode and per-exercise vs combined
    status: pending
  - id: batch-driver
    content: Add a batch driver script that enumerates singles + contiguous spans per participant and runs analyses
    status: pending
  - id: convert-fresh
    content: Delete synthetic matrices; reconvert all 12 P1 sessions (671 + 252) from raw with one identical config
    status: pending
  - id: selections
    content: Author corrected participant-specific selections (671 14-link, 252 16-link) for singles and contiguous spans under results_exploration_671_252/selections/
    status: pending
  - id: run-all
    content: Run pooled (ideal) + single (fallback) longitudinal with --validate for both participants; copy runs into results dir
    status: pending
  - id: rank-decide
    content: Build ranking summaries and decision_log.md; pick winning contiguous group per participant with caveats
    status: pending
  - id: scalability-docs
    content: Write tooling_audit.md + scalability recommendations (ex01-ex17, many participants, cross-participant summaries)
    status: pending
isProject: false
---

# jcvPCA Exploration + Core Upgrade — Contiguous ex09–ex15 Signal for 671 & 252

## 1. Mission summary
Upgrade the gaga_jcvpca core so exercise-window slicing and pooled-repetition longitudinal comparisons are driven by selection/config YAML, unblock conversion with a DataDescriptions sidecar fallback, then reconvert all 12 P1 sessions fresh and run an identical-parameter jcvPCA sweep for participants 671 and 252. Screen ex09–ex15 individually (Phase 1) and over every contiguous group (Phase 2), compare longitudinal change (ideal pooled `T1(R1+R2) vs T2/T3(R1+R2)` and fallback single-rep) against the T1 R1-vs-R2 NV floor plus `--validate` bootstrap, and rank contiguous groups by links exceeding NV. The golden jcvPCA math stays byte-for-byte; only the DATA fed to it changes.

## 2. Authorized scope
- Core library edits allowed (`src/gaga_jcvpca/`), UI edits allowed (`ui/`), CLI/script edits allowed (`scripts/`).
- SACRED, UNTOUCHED: `compute_jcvpca`, `select_selected_m_from_A`, `aggregate_axis_to_link_rss`, `build_axis_table` in [src/gaga_jcvpca/jcvpca.py](src/gaga_jcvpca/jcvpca.py) (lines 89-254). Slicing/pooling only change which rows enter A and B; centering stays independent per side and T1 remains the reference PCA space — paper-faithful per [refernces/JcvPCA and JsvCRP.pdf](refernces/JcvPCA%20and%20JsvCRP.pdf).
- Everything fresh: discard synthetic 671 matrices; do not rely on any past run.

## 3. Data confirmation
All six P1 sessions exist as raw skeleton CSVs for BOTH participants: 671 and 252 each have T1/T2/T3 × R1/R2 under `data/raw_skeleton/{pid}/`, including `252_T3_P1_R2`.
- Blocker: only three DataDescriptions sidecars exist (671 T1_R1, 671 T3_R1, 252 T3_R2); the other nine P1 sessions have none, so `run_convert.py` currently skips them (fixed in Step 4a).
- Favorable: Motive frames are 0-based and contiguous (Frame col = 0,1,2,…; 671 T1 ≈ 30,604 frames) and segmentation `start_frame`/`end_frame` are in that same absolute space, so after conversion **matrix row index == Motive frame number** → slicing is `matrix.iloc[start:end]` with no alignment logic.

## 4. Core implementation steps (golden math untouched)

### 4a. DataDescriptions sidecar fallback — [src/gaga_jcvpca/project_io.py](src/gaga_jcvpca/project_io.py), [scripts/run_convert.py](scripts/run_convert.py)
`_description_for_session` requires an exact per-session sidecar. Add a fallback that resolves, in order: exact session sidecar → same participant+timepoint → same participant (any P1 take), gated by a marker-set-prefix match (`project_io.marker_set_prefix`, already exists) so we never mix skeleton assets. Log which sidecar was used per session in the run manifest. Unblocks all 12 sessions without fabricating data.

### 4b. Exercise-window slicing — [src/gaga_jcvpca/pipeline.py](src/gaga_jcvpca/pipeline.py)
Today `run_analysis` loads full-session matrices and filters only columns; `exercise_ids`/`combine_exercises` are inert. Add a slicing step in `load_matrix` (or a new `_sliced_matrix`) that, given the session's segmentation windows (`build_inventory(cfg).segments` filtered to the selection's `exercise_ids`), returns the row-concatenation of `matrix.iloc[start:end]` per window. `combine_exercises: true` → one matrix over all contiguous windows; `false` → per-exercise matrices. This makes Phase 1 (singles) and Phase 2 (contiguous groups) real and YAML-driven.

### 4c. Pooled-repetition longitudinal — [src/gaga_jcvpca/pipeline.py](src/gaga_jcvpca/pipeline.py)
Add `repetition_mode: single | pooled` (config default + selection field). In `pooled`, build each timepoint side by row-concatenating sliced R1+R2 into one matrix, then run `T1(R1+R2) vs T2(R1+R2)` and `T1(R1+R2) vs T3(R1+R2)`. In `single`, keep the current `T1_R1 vs T2_R1` / `T1_R1 vs T3_R1` fallback. NV stays strictly within-timepoint `T1_R1 vs T1_R2` (never pooled) so the noise floor is preserved. Both modes runnable so the ideal vs fallback can be compared directly.

### 4d. NV baseline for every longitudinal — [src/gaga_jcvpca/validation.py](src/gaga_jcvpca/validation.py)
`natural_variability_baseline` currently scores only the first longitudinal comparison. Loop it over all longitudinal comparisons so both T1-vs-T2 and T1-vs-T3 get per-link `effect_ratio_vs_nv` in `validation_results.csv`, removing the need for duplicate `--timepoints T1 T3` runs.

### 4e. CLI + UI — [scripts/run_analysis.py](scripts/run_analysis.py), [ui/app.py](ui/app.py)
Add `--repetition-mode {single,pooled}` (and optional `--repetitions`) to the CLI. In Tab 5 setup (`_render_setup`, ui/app.py line 434) add a repetition-mode selector and a per-exercise vs combined toggle, surfacing exactly what will run. No other UI redesign.

### 4f. Batch driver — new [scripts/run_exploration_671_252.py](scripts/run_exploration_671_252.py)
Thin loop that, per participant, enumerates ex09–ex15 singles + all contiguous spans, ensures a selection YAML exists, and runs `run_analysis` in both pooled and single modes with `--validate`, then copies each `outputs/runs/<run_id>/` into `results_exploration_671_252/runs/`. Generic over exercise_id and participant so it scales later.

## 5. Execution sequence
1. Implement 4a–4f (core + CLI/UI + driver).
2. Delete synthetic `outputs/cache/matrices/671_*.parquet`; `python scripts/run_convert.py` to convert all 12 P1 sessions with one identical config.
3. Author selections under `results_exploration_671_252/selections/`: `{pid}_ex{NN}_single.yaml` (7 each) and `{pid}_ex{start}_{end}_contiguous.yaml` (all spans), 671 with 14 links, 252 with 16 links.
4. Run the batch driver (pooled + single, `--validate`) for both participants.
5. Build ranking summaries and the decision log.

## 6. Run matrix
- Contiguous subsets of ex09..ex15 = 28 (7 singles + 21 multi-exercise spans).
- Per group, one run yields T1-vs-T2, T1-vs-T3, and NV (T1 R1-vs-R2) together; run once pooled + once single = 2 runs/group.
- Per participant ≈ 28 × 2 = 56 runs; ≈ 112 total. Driven by the batch script, not by hand.

## 7. Scoring & ranking
Per contiguous group G and participant P, per included link:
- `per_link_score = |longitudinal_JcvPCA_link| / (|NV_JcvPCA_link| + eps)` (matches `validation.natural_variability_baseline`).
- `exceeds_nv = per_link_score > 1.0`.
Rank groups by: (1) count of links with `exceeds_nv`; (2) mean `per_link_score`; (3) bootstrap-supported links (CI excludes zero); (4) consistency across T1-vs-T2 and T1-vs-T3. Report pooled vs single side-by-side and use whichever design is better supported, stating which. Flag groups with a large NV baseline as low-confidence.

## 8. Same-parameters guarantee (both participants)
Identical jcvPCA parameters for 671 and 252: variance_threshold 0.80, Butterworth 10 Hz order 4, sensitivity_p 2, min_rows_for_pca 10, bootstrap 1000 / min 4 windows, seed 12345 (all from [configs/analysis_defaults.yaml](configs/analysis_defaults.yaml)). Note the one unavoidable difference: link SETS stay participant-specific (671=14, 252=16) because manifests differ and cross-participant merging is forbidden; results are compared structurally (each participant vs its own NV), never link-for-link across people.

## 9. Scalability recommendations (for ex01–ex17 and many future participants)
- Slicing and pooling are keyed off the authoritative `exercise_id` and any contiguous span — nothing hardcoded to Group 4, so ex01–ex17 and future groups work with no code change.
- Sidecar fallback removes the per-take sidecar bottleneck as the cohort grows.
- Batch driver generalizes to N participants × M groups; keep it config/argument-driven.
- Add a cross-participant SUMMARY aggregator that stacks per-participant results for reporting while keeping every statistic within-participant (descriptive, never pooled inference).
- Record `repetition_mode`, the exact sliced frame windows, chosen sidecar, and per-comparison `selected_m` in `reproducibility_manifest.json` so large batches stay auditable.
- Bootstrap sufficiency: single exercises (~960–1,920 frames) are borderline (~4 blocks); contiguous groups are comfortable — the ranking should down-weight `insufficient data` singles.

## 10. Risks & limitations
- Only 2 repetitions → R1-vs-R2 NV is a descriptive floor, not significance; the paper builds NV from many within-condition random splits (documented mismatch).
- Gaga is improvisational → high within-timepoint variability can mask signal.
- Pooled design increases frames/robustness but blends two takes; report both pooled and single so the choice is evidenced.
- 671-T3 marker-set prefix confound and 14-vs-16 link manifests keep analyses within-participant.
- Sidecar fallback must verify marker-set identity before reusing a description.

## 11. Directory layout (`results_exploration_671_252/`)
- `PLAN.md`, `tooling_audit.md`, `decision_log.md`
- `selections/` — `{pid}_ex{NN}_single.yaml`, `{pid}_ex{start}_{end}_contiguous.yaml`
- `runs/{pid}/{ex_or_group}/{mode}/{comparison}/` — copied run folders
- `summaries/` — ranking tables (n_links_exceeding_NV, mean effect ratio, bootstrap-supported links, pooled-vs-single)

## 12. Decision criteria
Pick the contiguous ex09–ex15 group with the most links whose longitudinal change exceeds its own NV, then highest mean effect ratio, then most bootstrap-supported links, preferring groups strong in both T1-vs-T2 and T1-vs-T3. Record per participant: the winning group, whether pooled (ideal) or single (fallback) was used and why, and all confidence caveats in `decision_log.md`.
