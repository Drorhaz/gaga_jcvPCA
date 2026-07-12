# Render validation — 671 / 252 avatar views

**Overall: PASS**

| Check | Result | Detail |
|---|---|---|
| signed_nv_files_exist | PASS | 12 views expected; missing: none |
| signed_nv_region_counts_match_group_summary | PASS | all region/link counts match |
| signed_nv_max_ratio_matches_table | PASS | all max ratios match |
| signed_nv_top_links_match_table | PASS | all top-3 callouts match |
| signed_nv_region_traceability | PASS | every above-NV region has a strongest_link |
| signed_nv_mixed_sign_documented | PASS | all mixed-sign regions documented |
| signed_nv_mixed_sign_inventory | PASS | 23 mixed-sign region(s): 252_T1_vs_T2_functional/right_leg, 252_T1_vs_T2_null/left_leg, 252_T1_vs_T2_combined/left_arm, 252_T1_vs_T2_combined/left_leg, 252_T1_vs_T2_combined/right_leg, 252_T1_vs_T3_functional/left_arm, 252_T1_vs_T3_null/left_arm, 252_T1_vs_T3_combined/left_arm, 252_T1_vs_T3_combined/right_arm, 252_T1_vs_T3_combined/left_leg, 252_T1_vs_T3_combined/right_leg, 671_T1_vs_T2_functional/left_arm, 671_T1_vs_T2_functional/right_arm, 671_T1_vs_T2_null/left_arm, 671_T1_vs_T2_null/right_arm, 671_T1_vs_T2_combined/left_arm, 671_T1_vs_T2_combined/right_arm, 671_T1_vs_T3_functional/left_arm, 671_T1_vs_T3_functional/right_arm, 671_T1_vs_T3_null/left_arm, 671_T1_vs_T3_null/right_arm, 671_T1_vs_T3_combined/left_arm, 671_T1_vs_T3_combined/right_arm |
| signed_nv_tables_exist | PASS | missing: none |
| signed_nv_tables_row_counts_match_base | PASS | all row counts match base tables |
| signed_nv_tables_fill_color_spotcheck | PASS | sample signed_fill_color values match link_style |
| signed_nv_tables_mixed_sign_matches_meta | PASS | mixed-sign inventory matches signed region_space CSVs |

## Signed-NV render mode

1. **Added as optional render mode** — default `magnitude_nv` is unchanged.
2. **How to activate:** `python avater_671_252/render_avatars.py --all --render-mode signed_nv` or `--render-mode both`.
3. **Color rules:** sign from `long_jcvpca_mean`; strength from `effect_ratio_vs_nv` with moderate (1.0–3.0× NV) vs strong (>3.0× NV). Dark/light blue = decreased contribution vs T1; yellow/red = increased; gray = within NV.
4. **Output location:** `renders/signed_nv/{view_id}.png` + `.meta.json`, plus `summary_2x2_combined.png` in the same folder. Signed table exports live under `tables/signed_nv/`.
5. **Mixed-sign regions:** 23 mixed-sign region(s): 252_T1_vs_T2_functional/right_leg, 252_T1_vs_T2_null/left_leg, 252_T1_vs_T2_combined/left_arm, 252_T1_vs_T2_combined/left_leg, 252_T1_vs_T2_combined/right_leg, 252_T1_vs_T3_functional/left_arm, 252_T1_vs_T3_null/left_arm, 252_T1_vs_T3_combined/left_arm, 252_T1_vs_T3_combined/right_arm, 252_T1_vs_T3_combined/left_leg, 252_T1_vs_T3_combined/right_leg, 671_T1_vs_T2_functional/left_arm, 671_T1_vs_T2_functional/right_arm, 671_T1_vs_T2_null/left_arm, 671_T1_vs_T2_null/right_arm, 671_T1_vs_T2_combined/left_arm, 671_T1_vs_T2_combined/right_arm, 671_T1_vs_T3_functional/left_arm, 671_T1_vs_T3_functional/right_arm, 671_T1_vs_T3_null/left_arm, 671_T1_vs_T3_null/right_arm, 671_T1_vs_T3_combined/left_arm, 671_T1_vs_T3_combined/right_arm.
6. **Default mode unchanged:** magnitude outputs remain in `renders/` with the original E1 intensity legend.
