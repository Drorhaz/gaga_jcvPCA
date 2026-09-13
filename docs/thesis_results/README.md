# Thesis results lock — cover sheet

**Date:** 2026-09-13  
**Repo:** `gaga_jcvpca`  
**Authoritative result tree:** `results_committee_case/marker_gap_policy_ex09_13/`  
**Production git hash (run manifests):** `728c871edf0423aa6ea526651023253c38ea118f`  
**Files now stored in commit:** `1101c4d` (commit added artifacts; it did **not** re-run the pipeline)

This folder (`docs/thesis_results/`) freezes what may enter the first thesis draft. It does **not** change analysis code or overwrite existing result trees.

## Verdict (independent)

**Category 2 — You can start writing the results chapter, but do not call the science fully locked.**

- The **numbers** for the four N-of-1 JcvPCA cases are internally consistent in the marker-gap tree and can be typed into the draft now.
- The **interpretive claim** (A3 / “broader underused-link participation”) is supported for **one cell only**: 671 T1→T2 (4 S3 links). Everything else is descriptive A1/A2 with coverage, QC, or robustness gates open.
- **No pipeline re-run is required** to start the draft. A one-comparison smoke re-run is desirable for provenance (results were generated from then-uncommitted code on `728c871`), not a scientific blocker.
- Do **not** use `results_committee_case/METRICS_DIGEST.md` as a number source. It is stale (see `RESULTS_AUDIT.md` §B).

## Package

| File | Role |
|---|---|
| `MASTER_RESULTS_TABLE.csv` / `.md` | One row per participant × T1→T2 / T1→T3 |
| `RUN_INVENTORY.csv` | Pooled + single Step-4 runs in the lock tree |
| `RESULTS_AUDIT.md` | Sample, T1→T2, T1→T3, NV, gaps, robustness, contradictions |
| `CENTRAL_CLAIM.md` | Three claim wordings + CLAIMS.md mapping |
| `THESIS_RESULTS_DECISION.md` | MUST / SHOULD / DO NOT INCLUDE |
| `OPEN_ITEMS_BEFORE_WRITING.md` | Blocking vs non-blocking actions |

## What is *not* in this lock

Shared-6D / Conv / RQA (`gaga_shared6d_poc`) and the 3Layers poster batch are complementary or historical. They are classified in `THESIS_RESULTS_DECISION.md`. They are not the A2 estimand.
