# Amplitude vs organization — Step 5 classification summary

ROM flat band: **0.7–1.3** (follow-up / T1 pooled).
Exceeds observed NV: `effect_ratio_vs_nv` > **1.0** (descriptive).

## Classification rules

| Label | Rule |
|---|---|
| `organization` | exceeds NV **and** ROM ratio in flat band |
| `amplitude` | exceeds NV **and** ROM ratio outside band **with** consistent JcvPCA sign |
| `mixed` | exceeds NV **and** ROM shifts without consistent sign |
| `within_variability` | does not exceed NV **and** flat ROM |
| `amplitude_only` | does not exceed NV **but** ROM ratio outside flat band |

## Counts per participant × comparison

| participant | comparison_id | amplitude | amplitude_only | mixed | organization | within_variability |
| --- | --- | --- | --- | --- | --- | --- |
| 252 | 252_T1_vs_T2 | 0 | 1 | 0 | 4 | 15 |
| 252 | 252_T1_vs_T3 | 0 | 1 | 0 | 10 | 9 |
| 651 | 651_T1_vs_T2 | 0 | 0 | 1 | 8 | 1 |
| 651 | 651_T1_vs_T3 | 1 | 1 | 1 | 5 | 1 |
| 671 | 671_T1_vs_T2 | 0 | 0 | 1 | 6 | 11 |
| 671 | 671_T1_vs_T3 | 2 | 3 | 0 | 2 | 8 |
| 790 | 790_T1_vs_T2 | 1 | 2 | 1 | 9 | 7 |
| 790 | 790_T1_vs_T3 | 0 | 3 | 0 | 7 | 8 |

## Participant headlines

- **252 252_T1_vs_T2:** 4 links exceed NV; 4 organization / 0 amplitude / 0 mixed; 19 links with flat ROM ratio.
- **252 252_T1_vs_T3:** 10 links exceed NV; 10 organization / 0 amplitude / 0 mixed; 19 links with flat ROM ratio.
- **651 651_T1_vs_T2:** 9 links exceed NV; 8 organization / 0 amplitude / 1 mixed; 9 links with flat ROM ratio.
- **651 651_T1_vs_T3:** 7 links exceed NV; 5 organization / 1 amplitude / 1 mixed; 6 links with flat ROM ratio.
- **671 671_T1_vs_T2:** 7 links exceed NV; 6 organization / 0 amplitude / 1 mixed; 17 links with flat ROM ratio.
- **671 671_T1_vs_T3:** 4 links exceed NV; 2 organization / 2 amplitude / 0 mixed; 10 links with flat ROM ratio.
- **790 790_T1_vs_T2:** 11 links exceed NV; 9 organization / 1 amplitude / 1 mixed; 16 links with flat ROM ratio.
- **790 790_T1_vs_T3:** 7 links exceed NV; 7 organization / 0 amplitude / 0 mixed; 15 links with flat ROM ratio.

## Interpretation guide (committee)

- Many **organization** labels → redistribution language better supported.
- Dominant **amplitude** or **mixed** → soften to combined amplitude + organization change.
- Mostly **within_variability** → descriptive only; no organization headline.

See `rom_rms_by_link.csv` for link-level detail.
