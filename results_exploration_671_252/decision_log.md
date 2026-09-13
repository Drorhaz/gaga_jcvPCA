# Decision log — contiguous ex09-15 jcvPCA signal (671 & 252)

_Generated 2026-07-07T19:28:19._

Scoring per plan section 7: per link, `effect_ratio = |longitudinal ΔJcvPCA| / (|NV ΔJcvPCA| + eps)`; a link `exceeds NV` when ratio > 1. Groups are ranked by (1) total links exceeding NV across T1-vs-T2 and T1-vs-T3, (2) mean effect ratio, (3) bootstrap-supported links, preferring groups strong in both longitudinal comparisons. Statistics are strictly within-participant.

## Participant 671

- **Winning group:** `ex11_single` using **pooled** design.
- **Why this design:** pooled (ideal: T1(R1+R2) vs T2/T3(R1+R2)) — more frames and cross-take robustness.
- **Support:** 26 link-comparisons exceed NV; mean effect ratio 3.22; 0 bootstrap-supported link(s); consistent across timepoints: True.
- **Caveats:** only 2 repetitions -> NV is a descriptive floor, not significance; single-exercise windows are borderline for bootstrap (down-weighted); Gaga is improvisational so within-timepoint variability is high. 671 carries a T3 marker-set prefix confound (skeleton hierarchy taken from the session's own raw header).

Top 5 groups (this participant):

| group | mode | total_links_exceeding_nv | mean_effect_ratio | n_bootstrap_supported | consistent_across_timepoints |
| --- | --- | --- | --- | --- | --- |
| ex11_single | pooled | 26 | 3.22 | 0 | True |
| ex12_15_contiguous | single | 26 | 2.312 | 0 | True |
| ex11_12_contiguous | single | 26 | 1.574 | 0 | True |
| ex11_single | single | 24 | 2.493 | 0 | True |
| ex12_15_contiguous | pooled | 24 | 2.243 | 0 | True |

## Participant 252

- **Winning group:** `ex10_14_contiguous` using **pooled** design.
- **Why this design:** pooled (ideal: T1(R1+R2) vs T2/T3(R1+R2)) — more frames and cross-take robustness.
- **Support:** 26 link-comparisons exceed NV; mean effect ratio 1.726; 0 bootstrap-supported link(s); consistent across timepoints: True.
- **Caveats:** only 2 repetitions -> NV is a descriptive floor, not significance; single-exercise windows are borderline for bootstrap (down-weighted); Gaga is improvisational so within-timepoint variability is high. 671 carries a T3 marker-set prefix confound (skeleton hierarchy taken from the session's own raw header).

Top 5 groups (this participant):

| group | mode | total_links_exceeding_nv | mean_effect_ratio | n_bootstrap_supported | consistent_across_timepoints |
| --- | --- | --- | --- | --- | --- |
| ex11_single | single | 29 | 1.742 | 0 | True |
| ex10_15_contiguous | single | 27 | 1.452 | 0 | True |
| ex09_10_contiguous | single | 26 | 1.841 | 0 | True |
| ex10_14_contiguous | pooled | 26 | 1.726 | 0 | True |
| ex10_13_contiguous | single | 26 | 1.293 | 0 | True |
