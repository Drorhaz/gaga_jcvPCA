# Open items before writing

No analysis code was changed for this lock. Items below are documentation, provenance, or supervisor process.

---

## A. Required before calling the *science* fully locked  
(does **not** block starting the first draft)

| # | Action | File / script | Re-run? | Risk if skipped | Blocks draft? |
|---|---|---|---|---|---|
| A1 | Treat `marker_gap_policy_ex09_13/` as the only number source; do not copy `METRICS_DIGEST.md` | Digest is stale (says Step 4 rerun pending; rerun already exists) | No | Wrong A2 counts (e.g. 252 T2 8 vs 3) | **No** if you ignore the digest |
| A2 | In every T1→T3 671 sentence that names thigh links, state A2 uses T3_R1 while pooled dropped T3_R2 99% `LThighFront` | `comparison_link_exclusions.csv` vs `NV_PROFILE.csv` | No | QC-inconsistent T3 thigh claim | No, but caption-critical |
| A3 | Label 671 T2 A3 as **candidate** until `SUPERVISOR_NV_DECISION.md` is signed | `step08_nv_and_stability/SUPERVISOR_NV_DECISION.md` (empty) | No | Over-claim if committee later rejects S3 | **No** for Version 2 wording |

---

## B. Desirable, not blocking

| # | Action | File / script | Re-run? | Risk if skipped | Blocks draft? |
|---|---|---|---|---|---|
| B1 | Smoke-reproduce **one** comparison (671 T2 pooled + NV profile) with current `src/` on commit `1101c4d` and diff against lock CSVs | `scripts/run_step04_primary.py`, `scripts/run_marker_gap_policy_stack.py`, `scripts/observed_nv.py` | Yes, **one PID** | Provenance: artifacts were generated on dirty `728c871`. Unlikely to change numbers; would embarrass a methods appendix if bit-identity fails | No |
| B2 | Write Step 10 `FINDINGS_SUMMARY.csv` + `INTERPRETATION.md` as a thin projection of this lock folder | currently empty `step10_interpretation_package/` | No (copy tables) | No single “official” findings file besides this lock | No |
| B3 | Supervisor decision: governing S3 (4 links) vs romflat sensitivity (7) | CLAIMS.md S3 footnote; `NV_PROFILE.nv_profile_tier_romflat` | No | 671 T2 S3 list might grow by `671_to_Ab`, `Ab_to_Chest`, `LUArm_to_LFArm` | No — use 4 in the draft |
| B4 | One-paragraph methods note that k-grid, not “rep_pass” as a name, is why 7/8 cells fail the strict AND | `tables_to_show/README.md`, `robustness.csv` | No | Reviewer asks why 651 T3 looks stable but `rep_pass=False` | No |
| B5 | Decide whether shared6d Conv profiles go in a **separate** Results subsection | `gaga_shared6d_poc` freeze; do not merge estimands | No | Confusing two “change” metrics | No |

---

## C. Defer until after the first draft

| # | Action | Why later |
|---|---|---|
| C1 | Full 4-PID batch re-run | Numbers already internally consistent; expensive; not needed to write |
| C2 | Fifth participant | Does not unlock population inference |
| C3 | G8 bootstrap / FDR | Explicitly out of V1; would change claim language |
| C4 | RQA Stage 3, shared-direction rerun, Transformer-primary, free-movement transfer | Already gated off |
| C5 | MRI / fNIRS / questionnaires | Out of core |
| C6 | COMMITTEE_BRIEF / slide polish | Writing the thesis draft is the brief |
| C7 | Fixing 651 trunk missingness | Data/template fact, not a code bug |

---

## Ranked blockers (if you asked “must I wait?”)

1. **None that stop typing Chapter Results** using Version 2 + Table 09 + 671 T2 S3 list.  
2. **Self-discipline:** never open `METRICS_DIGEST.md` as a source.  
3. **Caption discipline:** coverage and exclusions in the same table as A2.  
4. **Optional 2-hour job:** B1 smoke on 671 T2, then freeze a `PROVENANCE.md` line (pass/fail). Still not a writing blocker.

If B1 **fails** bit-identity, **then** it becomes blocking and you re-run the marker-gap stack into a new timestamped folder without touching `728c871` artifacts. There is no present evidence that it will fail; it is untested.
