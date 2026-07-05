"""gaga_jcvpca dashboard — slim, decision-focused, single-app 7-tab shell.

Tabs 1 (Overview) and 2 (Inventory) are functional. Later phases fill in
QC Review, Selection, Analysis Setup, Results, and Run History.
"""

from __future__ import annotations

import _bootstrap  # noqa: F401  (adds src/ to sys.path)
import streamlit as st

from components.widgets import metric_row, next_action_banner, sidebar_navigator, status_badge
from gaga_jcvpca.pipeline import build_snapshot

st.set_page_config(page_title="gaga_jcvpca", layout="wide")


@st.cache_data(show_spinner=False)
def _load_snapshot_cached(science_token: str):
    # science_token only participates in cache invalidation.
    return build_snapshot()


def _snapshot():
    from gaga_jcvpca.config import load_config

    cfg = load_config()
    return _load_snapshot_cached(cfg.science_hash)


def main() -> None:
    st.title("gaga_jcvpca")
    st.caption("JcvPCA: how body links contribute to shared movement-variance patterns across matched datasets.")

    snapshot = _snapshot()
    nav = sidebar_navigator(snapshot)

    tabs = st.tabs(
        [
            "1 · Overview",
            "2 · Data Inventory",
            "3 · QC Review",
            "4 · Segment & Link Selection",
            "5 · Analysis Setup",
            "6 · Results",
            "7 · Run History",
        ]
    )

    with tabs[0]:
        _render_overview(snapshot)
    with tabs[1]:
        _render_inventory(snapshot, nav)
    with tabs[2]:
        _render_qc(snapshot)
    with tabs[3]:
        _render_selection(snapshot)
    with tabs[4]:
        _render_setup(snapshot)
    with tabs[5]:
        _render_results(snapshot)
    with tabs[6]:
        _render_history(snapshot)


def _render_overview(snapshot) -> None:
    s = snapshot.summary
    st.subheader("Project overview")
    metric_row(
        [
            ("Participants", s["n_participants"]),
            ("Timepoints", len(s["timepoints"])),
            ("Exercises", s["n_exercises"]),
            ("Repetitions", len(snapshot.inventory.repetitions())),
            ("Sessions", s["n_sessions"]),
            ("Analysis-ready", s["n_ready_sessions"]),
        ]
    )
    next_action_banner(snapshot.recommended_next_action)

    issues = snapshot.inventory.naming_issues
    if issues:
        st.subheader(f"Naming / comparability notes ({len(issues)})")
        for issue in issues:
            st.warning(f"**{issue.kind}** — {issue.subject}: {issue.message}")
    else:
        st.success("No naming or comparability issues detected.")


def _render_inventory(snapshot, nav) -> None:
    st.subheader("Data inventory")
    df = snapshot.inventory.rows_dataframe()
    if nav["participants"]:
        df = df[df["participant"].isin(nav["participants"])]
    if nav["timepoints"]:
        df = df[df["timepoint"].isin(nav["timepoints"])]
    if nav["repetitions"]:
        df = df[df["repetition"].isin(nav["repetitions"])]

    df = df.copy()
    df["status"] = df["status"].map(status_badge)
    show_cols = [
        "session_id",
        "has_skeleton_csv",
        "has_description",
        "has_segmentation_sheet",
        "n_exercises",
        "status",
    ]
    st.dataframe(df[show_cols], width="stretch", hide_index=True)

    with st.expander("Exercise segments (canonical mapping)"):
        seg = snapshot.inventory.segments_dataframe()
        if nav["participants"]:
            seg = seg[seg["participant"].isin(nav["participants"])]
        st.dataframe(
            seg[
                [
                    "session_id",
                    "exercise_id",
                    "canonical_label",
                    "gaga_alias",
                    "group_id",
                    "exercise_name",
                    "start_frame",
                    "end_frame",
                    "n_frames",
                ]
            ],
            width="stretch",
            hide_index=True,
        )

    with st.expander("Marker-set prefixes by session"):
        st.json(snapshot.inventory.marker_set_by_session)


def _render_qc(snapshot) -> None:
    st.subheader("QC Review")
    st.markdown(
        "Raw-marker QC translates technical measures into research consequences at "
        "six resolutions. Findings are advisory: they inform link/region inclusion "
        "in Tab 4 but do not silently drop data."
    )
    issues = [i for i in snapshot.inventory.naming_issues if i.kind == "marker_set_difference"]
    if issues:
        for i in issues:
            st.warning(f"**Comparability** — {i.subject}: {i.message}")
    st.info(
        "Per-segment marker QC runs against the embedded marker columns in each "
        "raw skeleton CSV (`configs/paths.yaml` → `data.raw_skeleton`). When skeleton "
        "files are linked, per-region gap/artifact findings appear here with include / "
        "exclude / caution recommendations."
    )
    with st.expander("QC thresholds in effect"):
        st.json(
            {
                "marker_missing_percent": snapshot.config.get("marker_missing_percent"),
                "gaps": snapshot.config.get("gaps"),
                "rotvec": snapshot.config.get("rotvec"),
            }
        )


def _render_setup(snapshot) -> None:
    from gaga_jcvpca import pipeline, selection as sel_mod

    st.subheader("Analysis Setup")
    cfg = snapshot.config
    sel_dir = cfg.resolve_path("outputs.root") / "selections"
    selections = sel_mod.list_selections(sel_dir)
    if not selections:
        st.info("No saved selections. Build one in Tab 4 first.")
        return

    chosen = st.selectbox("Selection", [p.stem for p in selections], key="setup_selection")
    selection = sel_mod.load_selection(sel_dir / f"{chosen}.yaml")

    st.write(f"Participant **{selection.participant}** — {len(selection.included_links())} links included.")
    timepoints = st.multiselect(
        "Timepoints to compare", snapshot.inventory.timepoints(),
        default=snapshot.inventory.timepoints(), key="setup_tps"
    )
    reference = st.selectbox("Reference timepoint (defines PCA space)", timepoints or ["T1"], key="setup_ref")
    col1, col2, col3 = st.columns(3)
    vt = col1.number_input(
        "variance_threshold", min_value=0.5, max_value=0.99,
        value=float(cfg.get("pca.variance_threshold", 0.80)), step=0.05, key="setup_vt"
    )
    run_sweep = col2.checkbox("Run threshold sweep", key="setup_sweep")
    run_val = col3.checkbox("Run statistical validation", key="setup_val")

    st.caption(
        f"Will run: reference {reference} vs "
        f"{[t for t in timepoints if t != reference]} (longitudinal) + "
        f"{reference} R1-vs-R2 (natural variability). Participant-specific (N-of-1)."
    )

    if st.button("Run analysis", type="primary", key="setup_run"):
        run_cfg = _config_with_threshold(cfg, vt)
        try:
            run_dir = pipeline.run_analysis(
                run_cfg,
                selection,
                timepoints=timepoints,
                reference_timepoint=reference,
                run_threshold_sweep=run_sweep,
                run_validation=run_val,
            )
            st.success(f"Run complete: `{run_dir.name}`. See Tab 6 (Results).")
        except FileNotFoundError as exc:
            st.error(
                f"{exc}\n\nGenerate feature matrices first (see "
                "`scripts/generate_smoke_matrices.py`) or link raw data in `configs/paths.yaml`."
            )


def _config_with_threshold(cfg, vt):
    import copy

    from gaga_jcvpca.config import Config

    data = copy.deepcopy(cfg.data)
    data.setdefault("pca", {})["variance_threshold"] = float(vt)
    return Config(data=data, project_root=cfg.project_root)


def _render_history(snapshot) -> None:
    from gaga_jcvpca import reporting

    st.subheader("Run History & Reproducibility")
    runs = reporting.list_runs(snapshot.config)
    if not runs:
        st.info("No runs yet.")
        return
    rows = []
    for run_dir in runs:
        try:
            m = reporting.load_manifest(run_dir)
        except (OSError, ValueError):
            continue
        rows.append(
            {
                "run_id": m.get("run_id"),
                "datetime": m.get("datetime"),
                "participant": m.get("participant"),
                "variance_threshold": m.get("variance_threshold"),
                "git_hash": (m.get("git_hash") or "")[:8],
                "science_hash": m.get("science_hash"),
                "n_comparisons": len(m.get("comparisons", [])),
            }
        )
    import pandas as pd

    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    chosen = st.selectbox("Inspect run", [r["run_id"] for r in rows], key="hist_run")
    run_dir = next(p for p in runs if p.name == chosen)
    with st.expander("Full reproducibility manifest"):
        st.json(reporting.load_manifest(run_dir))


def _render_selection(snapshot) -> None:
    import pandas as pd

    from gaga_jcvpca import project_io, selection as sel_mod

    st.subheader("Segment & link selection")
    cfg = snapshot.config

    participants = snapshot.inventory.participants()
    if not participants:
        st.warning("No participants discovered yet.")
        return
    participant = st.selectbox("Participant", participants, key="sel_participant")

    manifest_dir = cfg.resolve_path("data.feature_manifests")
    manifests = {p.name: p for p in sorted(manifest_dir.glob("*.csv"))}
    matching = [n for n in manifests if participant in n] or list(manifests)
    manifest_name = st.selectbox("Feature manifest", matching, key="sel_manifest")
    manifest = project_io.load_feature_manifest(manifests[manifest_name])

    # exercise scope
    seg = snapshot.inventory.segments_dataframe()
    seg_p = seg[seg["participant"] == participant]
    available_ids = sorted(seg_p["exercise_id"].unique().tolist())
    primary_group = cfg.get("primary_group", "Group4")
    group_ids = [
        int(x) for x in (cfg.get(f"movement_groups.{primary_group}.exercise_ids", []) or [])
    ]
    default_ids = [i for i in group_ids if i in available_ids] or available_ids
    exercise_ids = st.multiselect(
        "Exercises (authoritative exercise_id)",
        available_ids,
        default=default_ids,
        format_func=lambda i: f"ex{i:02d}",
        key="sel_exercises",
    )
    combine = st.checkbox(
        "Combine selected exercises into one analysis unit", value=True, key="sel_combine"
    )

    default_sel = sel_mod.default_selection(
        "draft", participant, manifest, cfg, exercise_ids=exercise_ids, combine_exercises=combine
    )
    st.markdown("**Links** — QC recommendations are advisory; you can override any row.")
    link_df = pd.DataFrame(
        [
            {
                "include": c.included,
                "link": c.link,
                "region": c.region,
                "qc_recommendation": c.qc_recommendation,
                "reason": c.reason,
            }
            for c in default_sel.links
        ]
    )
    edited = st.data_editor(
        link_df,
        column_config={"include": st.column_config.CheckboxColumn("include")},
        disabled=["link", "region", "qc_recommendation", "reason"],
        hide_index=True,
        width="stretch",
        key="sel_editor",
    )

    name = st.text_input("Selection name", value=f"{participant}_group4_default", key="sel_name")
    notes = st.text_area("Notes (why this selection)", key="sel_notes")
    if st.button("Save selection", type="primary", key="sel_save"):
        for c, (_, row) in zip(default_sel.links, edited.iterrows()):
            new_included = bool(row["include"])
            if new_included != c.included:
                c.user_override = True
                c.reason += " (user override)"
            c.included = new_included
        default_sel.name = name
        default_sel.notes = notes
        out_dir = cfg.resolve_path("outputs.root") / "selections"
        path = sel_mod.save_selection(default_sel, out_dir)
        st.success(
            f"Saved `{path.name}` with {len(default_sel.included_links())} included links "
            f"and {len(default_sel.excluded_links())} excluded."
        )

    existing = sel_mod.list_selections(cfg.resolve_path("outputs.root") / "selections")
    if existing:
        with st.expander(f"Saved selections ({len(existing)})"):
            for p in existing:
                st.code(p.name)


def _render_results(snapshot) -> None:
    import pandas as pd

    from gaga_jcvpca import reporting

    st.subheader("Results")
    runs = reporting.list_runs(snapshot.config)
    if not runs:
        st.info("No analysis runs yet. Build a selection (Tab 4) and run an analysis.")
        return
    run_names = [p.name for p in runs]
    chosen = st.selectbox("Run", run_names, key="results_run")
    run_dir = next(p for p in runs if p.name == chosen)

    summary_path = run_dir / "run_summary.md"
    if summary_path.exists():
        st.markdown(summary_path.read_text())

    def _show(label: str, filename: str) -> None:
        path = run_dir / filename
        if path.exists():
            with st.expander(label):
                st.dataframe(pd.read_csv(path), width="stretch", hide_index=True)

    _show("Link-level results", "link_level_results.csv")
    _show("Region-level results", "region_level_results.csv")
    _show("Functional space", "functional_space_results.csv")
    _show("Null space", "null_space_results.csv")
    _show("Natural variability (R1 vs R2)", "natural_variability_results.csv")
    _show("selected_m by comparison", "selected_m_by_comparison.csv")
    _show("Variance-threshold sweep", "threshold_sensitivity.csv")

    with st.expander("Reproducibility manifest"):
        st.json(reporting.load_manifest(run_dir))


if __name__ == "__main__":
    main()
