# Thesis results decision — what enters the first draft

Classification of **existing artifacts**, not of future analyses. Authoritative numbers: `marker_gap_policy_ex09_13/` @ `728c871`.

---

## 1. MUST INCLUDE (main Results)

These are required for an honest methods + feasibility chapter.

| Item | Where | Why |
|---|---|---|
| Four N-of-1 design, T1 reference, rotvec features, `ex09_13_contiguous` | CLAIMS.md, EXPERIMENTAL_DESIGN.md, LIMITS.md | Without this, every table is misread |
| A2 headline table (8 cells) | `tables_to_show/09_headline_a2_summary.csv` | The actual exceed-floor result |
| 671 T2 S3 link list (4 links) + coverage 0.81 + `rep_pass=True` | `NV_PROFILE.csv`, tables_to_show README | Only interpretive cell |
| Coverage table for all 8 cells | `06_coverage_gate_a2_estimand.csv` / `13_coverage_gate_vs_a2.csv` | Validity gate; 252 T3 = 0.60 |
| Marker-gap / shared-feature exclusions | `02_comparison_link_exclusions.csv`, `comparison_link_exclusions.md` | 651 trunk, 790 RHLE, 252 LFAX, 671 T3 thigh/prefix |
| A2 vs pooled footing sentence | `09_pooled_vs_single_headline.csv`, CLAIMS.md | Prevents dividing pooled Δ by single NV |
| Entropy / A4 (no broadening) | `distribution_summary.md` | Blocks “new DoF” language |
| Forbidden-claim box | LIMITS.md / CLAIMS.md | Committee and thesis both need it |
| Persistence of 671’s 6 links | `persistence_summary.md` | Strongest T2–T3 descriptive fact |

**First tables/figures to type into the draft**

1. Design lock (window, T1 reference, four IDs, rotvec).  
2. Table 09 (A2 / S3 / coverage / rep_pass).  
3. 671 T2 signed-Δ table (the 8 A2 links, S3 in bold).  
4. Exclusion table (one row per PID).  
5. Coverage bar or table (especially 252 T3 vs 790 T3).  
6. Optional: 671 avatar / link map for T1→T2 only, captioned as S3-gated.

---

## 2. SHOULD INCLUDE (Discussion or appendix)

| Item | Why not main-text primary |
|---|---|
| Step 5 ROM/organization counts | Different NV footing than A2; useful as amplitude control, not as the exceed test |
| Step 4b k-grid / repetition-mode matrices | Methods/appendix robustness; 671 T2 can be summarized in one sentence in Results |
| Policy delta (`14_policy_delta_summary.csv`, `DIFF_vs_pre_policy.md`) | Shows QC changed 252/651 A2 — Discussion, not a second results narrative |
| 671 T3 A2=9 with limited coverage | Descriptive; keep shorter than T2 |
| 790 / 651 / 252 T2 A2 link lists | Show heterogeneity; do not equal-weight with 671 T2 |
| Persistent `LFArm_to_LHand` in 790 | Interesting N-of-1 overlap with 671; not a group finding |
| Supervisor figures / slide45 / committee pack v2 | Presentation copies of the same numbers |
| Shared-6D Conv reliability-gated change (`gaga_shared6d_poc` freeze) | Different estimand (embedding Δ vs Drep). Complementary detection, **not** anatomical A2. If used: separate subsection, LIMITED GO, 651/790 strongest there — **do not reconcile by averaging with JcvPCA** |
| S3-romflat sensitivity (671 T2 7 vs 4) | One sentence + supervisor pending |

---

## 3. DO NOT INCLUDE IN MAIN THESIS

| Item | Reason |
|---|---|
| Pre-policy A2 counts (252 T2=8, 651 S3=5) | Superseded; would contradict the QC policy you are defending |
| `METRICS_DIGEST.md` numbers | Stale pointer to pre-policy Step 4 |
| `results_exploration_671_252/` windows (`ex11_single`, etc.) | Explicitly dropped in MASTER_EXECUTION_PLAN v4 |
| Step 5 “organization” as if it were A2 | Pooled mean-\|Δ\| footing |
| 252 T3 as the flagship result | Coverage 0.60; 0 persistent A2; 2 sign-flips |
| Cross-participant mean, t-test, “the group” | Forbidden |
| Shared-direction / S8 (shared6d) as a positive finding | Failed by design (`shared_direction_evidence=False`) |
| RQA Stage 2 as primary | `LIMITED_PASS_STOP`; 0 z-score novel cases |
| Transformer, clustering, P1–P5 cue stages | Negative or unsupported |
| 3Layers poster batch `193319` as the 4-person result | N=2, pre-rebuild, different packaging |
| MRI, fNIRS, questionnaires | Out of core by request |
| Causal Gaga / psilocybin / “improvement” / dormant motors | CLAIMS.md forbidden |
| Bootstrap CI / p-values / “significant links” | Removed in v5 |
| Version 3 central claim | Conditions not met |

---

## Consistency checklist (this package)

- IDs: 671, 252, 651, 790 — no others.  
- Window: `ex09–ex13` contiguous.  
- Pooled = headline; A2 = matched single-rep signed S2.  
- Features: relative link rotvecs.  
- T1 = PCA reference.  
- Language: descriptive N-of-1 except one guarded A3 sentence for 671 T2.

If a later draft violates any row, it is out of lock.
