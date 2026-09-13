"""gaga_jcvpca dashboard — slim, decision-focused, single-app 7-tab shell.

Tabs 1 (Overview) and 2 (Inventory) are functional. Later phases fill in
QC Review, Selection, Analysis Setup, Results, and Run History.
"""

from __future__ import annotations

import re

import _bootstrap  # noqa: F401  (adds src/ to sys.path)
import pandas as pd
import streamlit as st

from components.widgets import metric_row, next_action_banner, sidebar_navigator, status_badge
from gaga_jcvpca import qc_markers
from gaga_jcvpca.pipeline import build_snapshot

st.set_page_config(page_title="gaga_jcvpca", layout="wide")

_SCOPE_SESSION_RE = re.compile(r"^([^:]+)_([^_]+)_([^_]+)_([^:]+)")


@st.cache_data(show_spinner="Running marker QC…")
def _load_snapshot_cached(science_token: str, marker_key: str):
    # science_token and marker_key participate in cache invalidation only.
    return build_snapshot()


def _snapshot():
    from gaga_jcvpca.config import load_config
    from gaga_jcvpca.inventory import build_inventory

    cfg = load_config()
    inv = build_inventory(cfg)
    marker_key = qc_markers.marker_source_cache_key(cfg, inv)
    return _load_snapshot_cached(cfg.science_hash, marker_key)


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
            "8 · Avatar Views",
        ]
    )

    with tabs[0]:
        _render_overview(snapshot)
    with tabs[1]:
        _render_inventory(snapshot, nav)
    with tabs[2]:
        _render_qc(snapshot, nav)
    with tabs[3]:
        _render_selection(snapshot)
    with tabs[4]:
        _render_setup(snapshot)
    with tabs[5]:
        _render_results(snapshot)
    with tabs[6]:
        _render_history(snapshot)
    with tabs[7]:
        _render_avatars(snapshot)


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
            ("QC soft warnings", s.get("n_soft_warnings", 0)),
            ("Critical gap flags", s.get("n_large_gaps", 0)),
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
        "has_marker_csv",
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

    with st.expander("Feature manifests (missing / topology check)"):
        from gaga_jcvpca.feature_manifest_gen import discover_missing_manifests, format_report

        missing = discover_missing_manifests(snapshot.config)
        if not missing:
            st.success("Every participant with skeleton data has a feature manifest CSV.")
        else:
            st.warning(f"{len(missing)} participant(s) have skeleton data but no manifest.")
            for report in missing:
                st.code(format_report(report), language=None)
            st.caption(
                "Generate from the project root: "
                "`.venv/bin/python scripts/generate_feature_manifest.py --apply`"
            )


def _parse_scope_session(scope: str) -> dict:
    """Extract participant/timepoint/repetition from a QC scope string."""
    head = scope.split("::", 1)[0]
    m = _SCOPE_SESSION_RE.match(head)
    if not m:
        return {}
    return {
        "participant": m.group(1),
        "timepoint": m.group(2),
        "repetition": m.group(4),
        "session_id": head,
    }


def _filter_qc_df(
    df: pd.DataFrame,
    nav: dict,
    *,
    resolutions: list[str] | None = None,
    severities: list[str] | None = None,
    recommendations: list[str] | None = None,
    search: str = "",
) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    parsed = out["scope"].map(_parse_scope_session)
    out["_participant"] = parsed.map(lambda x: x.get("participant", ""))
    out["_timepoint"] = parsed.map(lambda x: x.get("timepoint", ""))
    out["_repetition"] = parsed.map(lambda x: x.get("repetition", ""))

    if nav.get("participants"):
        out = out[
            (out["_participant"].isin(nav["participants"]))
            | (out["resolution"] == "participant")
        ]
    if nav.get("timepoints"):
        out = out[
            (out["_timepoint"].isin(nav["timepoints"]))
            | (out["resolution"] == "participant")
            | (out["_timepoint"] == "")
        ]
    if nav.get("repetitions"):
        out = out[
            (out["_repetition"].isin(nav["repetitions"]))
            | (out["resolution"] == "participant")
            | (out["_repetition"] == "")
        ]
    if resolutions:
        out = out[out["resolution"].isin(resolutions)]
    if severities:
        out = out[out["severity"].isin(severities)]
    if recommendations:
        out = out[out["recommendation"].isin(recommendations)]
    if search.strip():
        needle = search.strip().lower()
        out = out[out["message"].str.lower().str.contains(needle, na=False)]
    return out.drop(columns=["_participant", "_timepoint", "_repetition"], errors="ignore")


def _filter_qc_findings_for_selection(findings, participant: str, exercise_ids: list[int]):
    """Keep participant-scoped findings relevant to selected exercises."""
    allowed_ex = {f"ex{int(i):02d}" for i in exercise_ids}

    def _keep(f) -> bool:
        if f.resolution == "participant" and f.scope == participant:
            return True
        if not f.scope.startswith(f"{participant}_"):
            return False
        parts = f.scope.split("::")
        if len(parts) < 2:
            return True
        label = parts[1]
        if label == "session":
            return True
        if label.startswith("ex") and label not in allowed_ex:
            return False
        return True

    return [f for f in findings if _keep(f)]


def _sessions_for_nav(snapshot, nav) -> list[str]:
    sessions = []
    for row in snapshot.inventory.rows:
        if not row.has_marker_csv:
            continue
        if nav.get("participants") and row.participant not in nav["participants"]:
            continue
        if nav.get("timepoints") and row.timepoint not in nav["timepoints"]:
            continue
        if nav.get("repetitions") and row.repetition not in nav["repetitions"]:
            continue
        sessions.append(row.session_id)
    return sorted(sessions)


def _render_qc_gap_heatmaps(snapshot, nav) -> None:
    from gaga_jcvpca import qc_markers

    heatmaps = snapshot.qc_gap_heatmaps
    sessions = _sessions_for_nav(snapshot, nav)
    available = [s for s in sessions if s in heatmaps]
    st.subheader("Critical gap heatmap (>= 0.5 s)")
    if not available:
        st.info("No session heatmaps available (need marker CSV + feature manifest).")
        return

    session_id = st.selectbox("Session", available, key="qc_heatmap_session")
    raw = heatmaps[session_id]
    display, binned = qc_markers.bin_heatmap_for_display(raw)
    if binned:
        st.caption("Frames binned for display; cell = any critical gap in that frame range.")

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        st.warning('Install UI extras (`pip install -e ".[ui]"`) to render heatmaps.')
        st.dataframe(display, width="stretch")
        return

    fig, ax = plt.subplots(figsize=(12, max(3, len(display) * 0.35)))
    ax.imshow(display.values, aspect="auto", interpolation="nearest", cmap="Reds")
    ax.set_yticks(range(len(display.index)))
    ax.set_yticklabels(display.index)
    ax.set_xlabel("Frame" if not binned else "Frame range (binned)")
    ax.set_ylabel("Link")
    ax.set_title(f"Critical gaps — {session_id}")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def _render_qc(snapshot, nav) -> None:
    st.subheader("QC Review")
    st.markdown(
        "Raw-marker QC translates technical measures into research consequences at "
        "segment and body-region resolution. Findings are advisory: they inform "
        "link/region inclusion in Tab 4 but do not silently drop data."
    )

    n_marker_sessions = sum(1 for r in snapshot.inventory.rows if r.has_marker_csv)
    if n_marker_sessions == 0:
        st.warning(
            "No marker CSV files were found. Configure `data.raw_markers` or "
            "`data.raw_skeleton` in `configs/paths.yaml` (expected layout: "
            "`data/raw_markers/{participant}/` or linked skeleton exports), then reload."
        )
        return

    for msg in snapshot.qc_parse_warnings:
        st.warning(msg)

    issues = [i for i in snapshot.inventory.naming_issues if i.kind == "marker_set_difference"]
    if issues:
        for i in issues:
            st.warning(f"**Comparability** — {i.subject}: {i.message}")

    df = snapshot.qc_summary_df
    if df.empty:
        st.info("Marker files are present but QC produced no findings.")
        return
    if "affected_links" not in df.columns:
        df = df.copy()
        df["affected_links"] = ""

    col1, col2, col3, col4, col5 = st.columns(5)
    filtered_for_metrics = _filter_qc_df(df, nav)
    col1.metric("Total findings", len(filtered_for_metrics))
    col2.metric(
        "Soft warnings",
        int((filtered_for_metrics["severity"] == "soft_warning").sum()),
    )
    col3.metric(
        "Exclude recommendations",
        int((filtered_for_metrics["recommendation"] == "exclude").sum()),
    )
    col4.metric(
        "Critical gap flags",
        int(
            filtered_for_metrics["message"]
            .str.contains("critical", case=False, na=False)
            .sum()
        ),
    )
    col5.metric(
        "Velocity artifact findings",
        int((filtered_for_metrics["metric"] == "velocity_artifact_frames").sum()),
    )

    fcol1, fcol2, fcol3 = st.columns(3)
    all_res = sorted(df["resolution"].unique())
    all_sev = sorted(df["severity"].unique())
    all_rec = sorted(df["recommendation"].unique())
    sel_res = fcol1.multiselect("Resolution", all_res, default=all_res, key="qc_res")
    sel_sev = fcol2.multiselect("Severity", all_sev, default=all_sev, key="qc_sev")
    sel_rec = fcol3.multiselect("Recommendation", all_rec, default=all_rec, key="qc_rec")
    search = st.text_input("Search message text", key="qc_search")

    filtered = _filter_qc_df(
        df,
        nav,
        resolutions=sel_res,
        severities=sel_sev,
        recommendations=sel_rec,
        search=search,
    )
    show_cols = [
        "resolution",
        "scope",
        "metric",
        "value",
        "severity",
        "recommendation",
        "affected_links",
        "affects_levels",
        "message",
    ]
    col_config = {
        "affected_links": st.column_config.TextColumn(
            "Links with gaps (exclude if needed)",
            width="medium",
        ),
    }

    tab_all, tab_gaps, tab_art, tab_cmp = st.tabs(
        ["All", "Gaps", "Artifacts", "Comparability"]
    )
    with tab_all:
        st.dataframe(
            filtered[show_cols],
            column_config=col_config,
            width="stretch",
            hide_index=True,
        )
    with tab_gaps:
        gaps = filtered[filtered["metric"] == "marker_missing_percent"]
        st.dataframe(
            gaps[show_cols],
            column_config=col_config,
            width="stretch",
            hide_index=True,
        )
    with tab_art:
        art = filtered[filtered["metric"] == "velocity_artifact_frames"]
        st.dataframe(art[show_cols], width="stretch", hide_index=True)
    with tab_cmp:
        cmp_df = filtered[
            (filtered["metric"] == "marker_set_prefixes")
            | (filtered["resolution"] == "participant")
        ]
        st.dataframe(cmp_df[show_cols], width="stretch", hide_index=True)

    cache_path = snapshot.config.resolve_path("outputs.cache") / "qc" / "qc_summary.csv"
    if cache_path.exists():
        st.caption(f"Cached QC summary: `{cache_path}`")

    _render_qc_gap_heatmaps(snapshot, nav)

    with st.expander("Reference thresholds (config)"):
        st.json(
            {
                "marker_missing_percent": snapshot.config.get("marker_missing_percent"),
                "gaps": snapshot.config.get("gaps"),
                "artifacts": snapshot.config.get("artifacts"),
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

    cola, colb = st.columns(2)
    repetition_mode = cola.selectbox(
        "Repetition mode",
        ["single", "pooled"],
        index=0,
        format_func=lambda m: {
            "single": "single — T1_R1 vs Tk_R1 (fallback)",
            "pooled": "pooled — T1(R1+R2) vs Tk(R1+R2) (ideal)",
        }[m],
        key="setup_repmode",
    )
    ex_ids = selection.exercise_ids
    colb.markdown(
        f"**Exercise windows:** {'combined' if selection.combine_exercises else 'per-exercise'} "
        f"over exercise_id {ex_ids or 'all (full session)'}.\n\n"
        f"Rows are sliced to these segmentation windows per session before JcvPCA."
    )

    col1, col2, col3 = st.columns(3)
    vt = col1.number_input(
        "variance_threshold", min_value=0.5, max_value=0.99,
        value=float(cfg.get("pca.variance_threshold", 0.80)), step=0.05, key="setup_vt"
    )
    run_sweep = col2.checkbox("Run threshold sweep", key="setup_sweep")
    run_val = col3.checkbox("Run statistical validation", key="setup_val")

    long_sides = (
        f"{reference}(R1+R2) vs " + ", ".join(f"{t}(R1+R2)" for t in timepoints if t != reference)
        if repetition_mode == "pooled"
        else f"{reference}_R1 vs " + ", ".join(f"{t}_R1" for t in timepoints if t != reference)
    )
    st.caption(
        f"Will run: {long_sides} (longitudinal) + {reference} R1-vs-R2 "
        f"(natural variability, never pooled). Participant-specific (N-of-1)."
    )

    if st.button("Run analysis", type="primary", key="setup_run"):
        run_cfg = _config_with_threshold(cfg, vt)
        try:
            run_dir = pipeline.run_analysis(
                run_cfg,
                selection,
                timepoints=timepoints,
                reference_timepoint=reference,
                repetition_mode=repetition_mode,
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

    qc_filtered = _filter_qc_findings_for_selection(
        snapshot.qc_findings, participant, exercise_ids
    )
    default_sel = sel_mod.default_selection(
        "draft",
        participant,
        manifest,
        cfg,
        exercise_ids=exercise_ids,
        combine_exercises=combine,
        qc_findings=qc_filtered,
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
    override_reason = st.text_input(
        "Override reason (required when including a QC-excluded link)",
        key="sel_override_reason",
    )
    if st.button("Save selection", type="primary", key="sel_save"):
        override_needed = False
        for c, (_, row) in zip(default_sel.links, edited.iterrows()):
            new_included = bool(row["include"])
            if (
                new_included
                and not c.included
                and c.qc_recommendation == "exclude"
            ):
                override_needed = True
                break
        if override_needed and not override_reason.strip():
            st.error(
                "Provide an override reason when including links QC recommends excluding."
            )
            return

        for c, (_, row) in zip(default_sel.links, edited.iterrows()):
            new_included = bool(row["include"])
            if new_included != c.included:
                c.user_override = True
                suffix = override_reason.strip() or notes.strip()
                if suffix:
                    c.reason += f" (user override: {suffix})"
                else:
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


def _render_avatars(snapshot) -> None:
    """Interactive body-avatar views built from avater_671_252/tables/ (Phase 7)."""
    import json
    from pathlib import Path

    st.subheader("Avatar Views")
    st.caption(
        "Descriptive above-NV body change vs natural variability, rendered from the "
        "built tables under `avater_671_252/tables/`. Timepoints blinded; not a "
        "treatment effect."
    )

    try:
        from avater_671_252.render.config import (
            RENDER_MODE_MAGNITUDE,
            RENDER_MODE_SIGNED,
            load_render_config,
        )
        from avater_671_252.render.live import SPACES, get_manifest, render_live_figure
    except ImportError as exc:
        st.error(f"Avatar render package unavailable: {exc}")
        return

    avatar_dir = Path(snapshot.config.project_root) / "avater_671_252"
    if not (avatar_dir / "tables").exists():
        st.info("No `avater_671_252/tables/` directory found.")
        return

    config = load_render_config()
    manifest = get_manifest(avatar_dir)
    if not manifest.table_sets:
        st.info("No renderable tables discovered (need link_level + region_space CSVs).")
        return

    participants = manifest.participants
    c1, c2, c3, c4 = st.columns(4)
    participant = c1.selectbox("Participant", participants, key="avatar_participant")
    comparisons = [ts.comparison for ts in manifest.table_sets if ts.participant == participant]
    comparison = c2.selectbox("Comparison", comparisons, key="avatar_comparison")
    space = c3.selectbox("Space", list(SPACES), key="avatar_space")
    render_mode = c4.selectbox(
        "Render mode",
        [RENDER_MODE_MAGNITUDE, RENDER_MODE_SIGNED],
        format_func=lambda m: "Magnitude above NV (default)" if m == RENDER_MODE_MAGNITUDE else "Signed contribution vs T1",
        key="avatar_render_mode",
    )

    try:
        fig, meta = render_live_figure(
            avatar_dir, participant, comparison, space, config, mode=render_mode,
        )
    except Exception as exc:  # noqa: BLE001 - surface any render issue to the user
        st.error(f"Render failed: {exc}")
        return

    st.pyplot(fig)
    import matplotlib.pyplot as plt
    plt.close(fig)

    view_id = f"{participant}_{comparison}_{space}"
    renders_dir = config.renders_dir_for_mode(avatar_dir, render_mode)
    png_path = renders_dir / f"{view_id}.png"
    dcol1, dcol2 = st.columns(2)
    if png_path.exists():
        with open(png_path, "rb") as fh:
            dcol1.download_button(
                "Download PNG", fh.read(), file_name=f"{view_id}.png",
                mime="image/png", key="avatar_dl_png",
            )
    dcol2.download_button(
        "Download metadata JSON", json.dumps(meta, indent=2),
        file_name=f"{view_id}.meta.json", mime="application/json", key="avatar_dl_meta",
    )

    with st.expander("View metadata (traceability)"):
        st.json(meta)

    summary_mag = avatar_dir / "renders" / "summary_2x2_combined.png"
    summary_signed = config.renders_dir_for_mode(avatar_dir, RENDER_MODE_SIGNED) / "summary_2x2_combined.png"
    if summary_mag.exists():
        with st.expander("Investor 2×2 summary (magnitude_nv)"):
            st.image(str(summary_mag))
    if summary_signed.exists():
        with st.expander("Investor 2×2 summary (signed_nv)"):
            st.image(str(summary_signed))


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
