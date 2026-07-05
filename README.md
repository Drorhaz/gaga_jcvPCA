# gaga_jcvpca

A slim, standalone, scientifically faithful rebuild of the Gaga / psilocybin
motion-capture JcvPCA pipeline.

JcvPCA compares **how body links contribute to shared movement-variance patterns
across matched datasets**. One dataset (the T1 reference) defines the PCA movement
space; the matched dataset (T2, T3, or the other repetition) is projected into that
same space so the change in per-link contribution can be read out.

## What it does

```
data/ (raw skeleton quaternions + markers + segmentation xlsx)
  -> inventory   (what exists, canonical naming, missing/duplicate/legacy)
  -> qc_markers  (raw-marker QC in research language, 6 resolutions)
  -> rotations   (quaternion -> rotation-vector, ported, + flags)
  -> selection   (pick segments/links -> analysis_selection.yaml)
  -> jcvpca       (T1 vs T2/T3, R1 vs R2, combined; link/region/functional/null)
  -> validation  (OPTIONAL: NV baseline, sensitivity, stability, bootstrap-if-sufficient)
  -> reporting   (one self-contained run folder + reproducibility manifest)
  -> ui           (7-tab decision dashboard)
```

## Scope (V1)

- Task Part 1 only (`P1` in the session key). Extensible to more task parts later.
- Participant-specific analysis by default; cross-participant is optional/exploratory only.
- Default `variance_threshold = 0.80` (configurable + swept diagnostically).
- Exercise identity comes from the segmentation workbook `exercise_id` column
  (canonical label `ex{NN}`), never hardcoded.

## Layout

- `docs/` — `MASTER_PLAN.md` (authoritative spec), `PRD.md`, `specs/`, progress log.
- `configs/` — `default.yaml` composing `paths/exercise_map/body_regions/qc_thresholds/analysis_defaults`.
- `src/gaga_jcvpca/` — the ~11 source modules.
- `ui/` — Streamlit app + 7 tabs.
- `tests/` — one module per src module + golden regression + smoke.
- `scripts/` — thin CLI entrypoints.
- `data/` — standalone inputs (segmentation, descriptions, feature manifests; large raw CSVs referenced via `configs/paths.yaml`).
- `outputs/runs/<run_id>/` — one self-contained folder per run.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -e .           # or: pip install numpy pandas scipy scikit-learn pyarrow openpyxl pyyaml pytest
.venv/bin/pytest                      # run tests
.venv/bin/streamlit run ui/app.py     # launch dashboard
```

## Faithful core

The JcvPCA math (`compute_jcvpca`, `select_selected_m_from_A`, RSS link aggregation)
and the quaternion->rotation-vector conversion are ported byte-faithfully from the
validated pipeline and guarded by golden-regression tests. All orchestration, QC
presentation, selection, validation, reporting, and UI are rewritten clean.
