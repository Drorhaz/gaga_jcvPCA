# Marker-gap link removals — wired in pipeline

**Status:** implemented (2026-07-19)  
**Table:** `results_committee_case/step03_trunk_extension/marker_gap_link_removals_ex09_13.csv`  
**Regenerate table:** `PYTHONPATH=src .venv/bin/python scripts/build_marker_gap_link_removals.py`

---

## Config (`configs/analysis_defaults.yaml`)

```yaml
analysis:
  apply_marker_gap_removals: true
  marker_gap_removals_csv: results_committee_case/step03_trunk_extension/marker_gap_link_removals_ex09_13.csv
```

Set `apply_marker_gap_removals: false` to disable (e.g. Step 4b sensitivity vs on).

---

## Code path

| Module | Role |
|---|---|
| `src/gaga_jcvpca/marker_gap_policy.py` | Load CSV; resolve session-scoped link drops |
| `src/gaga_jcvpca/pipeline.py` → `run_analysis()` | Applies before each `run_comparison()` |
| `src/gaga_jcvpca/jcvpca.py` → `run_comparison()` | `pre_excluded_links` merged into `excluded_links` |
| `scripts/observed_nv.py` | Same policy on NV / matched single-rep comparisons |
| `src/gaga_jcvpca/reporting.py` | Splits exclusions in `run_summary.md`; writes audit JSON |

---

## Policy

Remove link for **participant × session × rep** when any supporting manifest-mapped marker has:

- **≥10%** of ex09–13 window in large gaps (>0.5 s), **or**
- **≥2** supporting markers each **≥5%** in large gaps

**Pooled mode:** if any rep on a comparison side is flagged, drop the link for that side.  
**Does not** change selection YAML or drop symmetric links.

---

## Run outputs

Each analysis run may include:

- `run_summary.md` — per comparison: **Excluded (marker-gap policy)** vs **Excluded (matrix / rotvec QC)**
- `marker_gap_excluded_links.json` — `{comparison_id: {link: reason}}`
- `reproducibility_manifest.json` — `marker_gap_policy.enabled`, CSV path

---

## Re-run committee primary results

After enabling, regenerate Step 4 primary runs so authoritative CSVs reflect new link sets:

```bash
PYTHONPATH=src .venv/bin/python scripts/run_step04_primary.py
```

Optional: Step 8 NV (`scripts/observed_nv.py`) if signed profile must match.

---

## What not to do

- Do not global-exclude links in selection YAML from marker gaps alone.
- Do not auto-drop symmetric (left/right) links.
- Do not use artifact % as a removal driver (not discriminative in ex09–13).
