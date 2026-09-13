# Tables to show — supervisor meeting

**Run:** `marker_gap_policy_ex09_13` (marker-gap policy ON)  
**Window:** `ex09_13_contiguous` · **Participants:** 671, 252, 651, 790

Ten curated tables (01–10) plus addendum (11–14). Read in this order for the narrative.

| # | File | Show when discussing… |
|---|---|---|
| 01 | `01_primary_run_index.md` | **Design lock** — links, selected_m per comparison |
| 02 | `02_comparison_link_exclusions.csv` | **QC transparency** — marker-gap drops per comparison |
| 03 | `03_robustness_stability.csv` | **Ranking stability** — rep-mode + QC-drop (Step 4b) |
| 04 | `04_functional_pc_bands.csv` | **PC sensitivity** — dominant (p50/p60) vs full 80% top-5 |
| 05 | `05_nv_profile_signed_tiers.csv` | **Primary evidence** — per-link S0–S3, A2, signed NV |
| 06 | `06_coverage_gate_a2_estimand.csv` | **Validity gate** — coverage before interpreting A2 |
| 07 | `07_persistence_t2_t3.csv` | **Temporal stability** — which A2 links persist T2→T3 |
| 08 | `08_amplitude_vs_organization_summary.md` | **Mechanism** — organization vs amplitude (Step 5) |
| 09 | `09_headline_a2_summary.csv` | **One-slide headline** — A2 counts + tiers per participant |
| 10 | `10_diff_vs_pre_policy.md` | **Policy impact** — what changed vs pre-marker-gap run |
| 11 | `11_r1_r2_same_sign_exceed_agreement.csv` | **Rep sensitivity** — R1 vs R2 same-sign exceed |
| 12 | `12_fun_null_same_sign_exceed_flags.csv` | **Band exceed** — fun/null × T2/T3 per link |
| 13 | `13_coverage_gate_vs_a2.csv` | **Coverage vs A2** — S2 blocked under limited coverage |
| 14 | `14_policy_delta_summary.csv` | **Policy delta** — Δ A2, exclusions, tier flips |
| 09 | `09_pooled_vs_single_headline.csv` | **Basis caveat** — pooled vs single-rep (Tier 3) |
| 10 | `10_per_exercise_nv_layer2.csv` | **Layer 2** — per-exercise NV (firewalled) |
| 11 | `11_exclusion_by_region.csv` | **QC map** — exclusions by body region |

## Regenerating 05 / 06 / 09

These three are pure projections of `step08_nv_and_stability/`. Rebuild them with:

```bash
PYTHONPATH=src .venv/bin/python scripts/build_tables_to_show.py \
    --results-root results_committee_case/marker_gap_policy_ex09_13
```

Do **not** hand-copy them. An earlier hand-made snapshot of `05` was taken seconds before
Step 5 finished writing, so it carried `step5_organization=False` on every row and showed
`S3 = 0`; the authoritative `NV_PROFILE.csv` had `S3 = 4` the whole time.

## Headline numbers (from 09)

| Participant | T1→T2 A2 | T1→T3 A2 | S3 | Coverage T3 | rep_pass T2 / T3 |
|---|---:|---:|---:|---|---|
| 671 | 8 | 9 | **4 (T2)** | limited | **True** / False |
| 252 | 3 | 12 | 0 | limited | False / False |
| 651 | 4 | 2 | 0 | limited | False / False |
| 790 | 7 | 3 | 0 | adequate | False / False |

`671_T1_vs_T2` is the only comparison where both S3 gates outside Step 5 are open
(coverage adequate 0.806 **and** `rep_pass` True). Its four S3 links are `671_to_LThigh`,
`LFArm_to_LHand`, `LShin_to_LFoot`, `LThigh_to_LShin`. Every other comparison is blocked by
`rep_pass=False` and/or limited T3 coverage, so no Step-5 outcome could produce S3 there.

`rep_pass` = min `top5_overlap` ≥ 0.6 across **all** Step-4b axes (`k_grid`, `qc_drop`,
`repetition_mode`), and `k_grid` is the binding constraint in 7 of 8 comparisons — the name
understates its strictness.

### Footing caveat on the S3 organization gate

`step5_organization` comes from Step 5, whose `exceeds_nv` test uses the **pooled** longitudinal
effect over the single-rep NV floor and a mean-|Δ| metric. S2 uses the **matched single-rep**
signed floor. The two are not on the same footing, so `classification == "organization"` bundles
an NV test that S2 already supersedes more strictly.

The governing definition is unchanged. `05` also carries a clearly-named sensitivity pair —
`step5_rom_flat` and `nv_profile_tier_romflat` — which applies ROM flatness alone and drops the
redundant pooled test. Under that variant 671 T1→T2 has **7** S3 links instead of 4 (adding
`671_to_Ab`, `Ab_to_Chest`, `LUArm_to_LFArm`, all flat-ROM but labelled `within_variability` by
Step 5's pooled read); all other comparisons remain 0. Choosing between them is a supervisor
decision, not a pipeline one.

## Figures (companion)

- Main deck: `docs/supervisor_meeting_figures_marker_gap_policy_ex09_13/`
- Addendum: `docs/supervisor_addendum/` (items 12–14)
- Tier 2 methods: `docs/supervisor_addendum/tier2/` (items 5–8)
- Tier 3 appendix: `docs/supervisor_addendum/tier3/` (items 9–11)
- Band overlap: `docs/fun_null_t3_nv_by_link/`
- Rep 2×2: `docs/rep_sensitivity_nv_panels/`
