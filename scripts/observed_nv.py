"""Step 8 / 8h — observed NV (Layer 1), coverage gate, matched single-rep ratio.

Usage:
  PYTHONPATH=src .venv/bin/python scripts/observed_nv.py
  PYTHONPATH=src .venv/bin/python scripts/observed_nv.py --participant 671
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca import jcvpca, marker_gap_policy, nv_profile, pipeline
from gaga_jcvpca.config import load_config
from gaga_jcvpca.selection import load_selection, region_of_link
from gaga_jcvpca.subspace_coverage import compute_subspace_coverage

PARTICIPANTS = ("671", "252", "651", "790")
WINDOW = "ex09_13_contiguous"
GROUP4_IDS = [9, 10, 11, 12, 13]
EX11_13_IDS = [11, 12, 13]
LOO_SETS = {
    "ex11_12": [11, 12],
    "ex11_13": [11, 13],
    "ex12_13": [12, 13],
}
TIMEPOINTS = ("T1", "T2", "T3")
EVR_FUNCTIONAL_50 = 0.50
EVR_FUNCTIONAL_60 = 0.60
EPS = 1e-9
NV_EXCEED = 1.0


def _pc_band_sizes(evr: np.ndarray, selected_m: int) -> dict[str, float | int]:
    evr = np.asarray(evr, dtype=float)[:selected_m]
    cum = np.cumsum(evr)

    def _p_at(th: float) -> int:
        return int(min(selected_m, np.searchsorted(cum, th) + 1))

    return {
        "p_functional_50": _p_at(EVR_FUNCTIONAL_50),
        "p_functional_60": _p_at(EVR_FUNCTIONAL_60),
        "evr_pc1": round(float(evr[0]), 4) if len(evr) else float("nan"),
        "evr_pc1_pc2": round(float(cum[1]), 4) if len(cum) > 1 else round(float(cum[0]), 4),
    }


def _session_matrix(
    config,
    participant: str,
    timepoint: str,
    repetition: str,
    exercise_ids: list[int],
) -> pd.DataFrame | None:
    task = config.get("mode.task_part", "P1")
    sid = pipeline._timepoint_session(participant, timepoint, repetition, task)
    df = pipeline.load_matrix(config, sid)
    if df is None:
        return None
    segs = pipeline._segments_by_session(config).get(sid, [])
    return pipeline.slice_matrix_to_exercises(df, segs, exercise_ids)


def _centered_concat(participant: str, timepoint: str, rep: str, exercise_ids: list[int], config) -> pd.DataFrame | None:
    parts: list[pd.DataFrame] = []
    for ex_id in exercise_ids:
        df = _session_matrix(config, participant, timepoint, rep, [ex_id])
        if df is None or df.empty:
            continue
        parts.append(df - df.mean(numeric_only=True))
    if not parts:
        return None
    return pd.concat(parts, ignore_index=True)


def _safe_comparison(
    comparison_id: str,
    kind: str,
    a_label: str,
    b_label: str,
    a_df: pd.DataFrame | None,
    b_df: pd.DataFrame | None,
    features: list[str],
    vt: float,
    region_fn,
    *,
    config=None,
    participant: str | None = None,
    a_session_ids: list[str] | None = None,
    b_session_ids: list[str] | None = None,
) -> jcvpca.ComparisonResult | None:
    if a_df is None or b_df is None or a_df.empty or b_df.empty:
        return None
    pre_excluded: dict[str, str] = {}
    if config is not None and participant is not None:
        policy = marker_gap_policy.load_policy(config)
        pre_excluded = marker_gap_policy.pre_excluded_for_comparison(
            participant,
            a_session_ids or [],
            b_session_ids or [],
            policy,
        )
    try:
        return jcvpca.run_comparison(
            comparison_id,
            kind,
            a_label,
            b_label,
            a_df,
            b_df,
            features,
            variance_threshold=vt,
            region_of_link=region_fn,
            sensitivity_p=2,
            min_rows_for_pca=10,
            export_weighted=True,
            pre_excluded_links=pre_excluded,
        )
    except jcvpca.ValidationError:
        return None


def _comp_on(
    participant: str,
    config,
    features: list[str],
    vt: float,
    region_fn,
    *,
    a_tp: str,
    a_rep: str,
    b_tp: str,
    b_rep: str,
    exercise_ids: list[int],
    comparison_id: str,
    kind: str = "longitudinal",
) -> jcvpca.ComparisonResult | None:
    """Generic single-rep comparison A(a_tp,a_rep) vs B(b_tp,b_rep) on a window."""
    a_df = _session_matrix(config, participant, a_tp, a_rep, exercise_ids)
    b_df = _session_matrix(config, participant, b_tp, b_rep, exercise_ids)
    a_sid = marker_gap_policy.timepoint_session(participant, a_tp, a_rep)
    b_sid = marker_gap_policy.timepoint_session(participant, b_tp, b_rep)
    return _safe_comparison(
        comparison_id,
        kind,
        f"{participant}_{a_tp}_{a_rep}",
        f"{participant}_{b_tp}_{b_rep}",
        a_df,
        b_df,
        features,
        vt,
        region_fn,
        config=config,
        participant=participant,
        a_session_ids=[a_sid],
        b_session_ids=[b_sid],
    )


class Step5JoinError(RuntimeError):
    """Step-5 organization evidence is missing or could not be joined cleanly."""


def default_step05_root(step04_root: Path) -> Path:
    """Conventional Step-5 folder for a given Step-4 output root."""
    return step04_root.parent / "step05_amplitude_vs_organization"


def load_step5_evidence(
    participant: str,
    step05_root: Path,
    *,
    require: bool = True,
) -> tuple[dict[tuple[str, str], bool], dict[tuple[str, str], bool], dict]:
    """Load Step-5 evidence keyed by ``(comparison_id, link_id)``.

    Returns ``(organization, rom_flat, info)``.

    ``organization`` is the **governing** S3 input: Step-5 ``classification ==
    'organization'``, which bundles a flat ROM ratio with Step-5's own pooled-footing
    NV read. ``rom_flat`` is a **sensitivity** variant carrying ROM flatness alone;
    S2 already applies a stricter matched single-rep floor, so the pooled NV test
    inside ``classification`` is partly redundant. Both are written to NV_PROFILE;
    only ``organization`` sets ``nv_profile_tier``.
    """
    path = step05_root / "rom_rms_by_link.csv"
    info = {
        "source": str(path),
        "available": path.exists(),
        "n_source_rows": 0,
        "n_organization": 0,
    }
    if not path.exists():
        if require:
            raise Step5JoinError(
                f"Step-5 evidence not found: {path}\n"
                "S3 is unreachable without it. Run scripts/compute_amplitude_covariate.py "
                "BEFORE scripts/observed_nv.py, point --step05-root at the right tree, or "
                "pass --allow-missing-step05 to accept step5_organization=False everywhere."
            )
        print(f"  [step5] WARNING: {path} not found -> step5_organization=False for all links")
        return {}, {}, info

    df = pd.read_csv(path)
    df = df[df["participant"].astype(str) == str(participant)]
    dup = df.duplicated(subset=["comparison_id", "link_id"], keep=False)
    if dup.any():
        keys = df.loc[dup, ["comparison_id", "link_id"]].drop_duplicates()
        raise Step5JoinError(
            f"Duplicate Step-5 (comparison_id, link_id) keys for {participant} in {path}:\n"
            f"{keys.to_string(index=False)}"
        )

    organization: dict[tuple[str, str], bool] = {}
    rom_flat: dict[tuple[str, str], bool] = {}
    for _, r in df.iterrows():
        key = (str(r["comparison_id"]), str(r["link_id"]))
        organization[key] = str(r.get("classification", "")) == "organization"
        rom_flat[key] = nv_profile.rom_is_flat(
            pd.to_numeric(r.get("rom_ratio"), errors="coerce")
        )
    info["n_source_rows"] = len(df)
    info["n_organization"] = int(sum(organization.values()))
    return organization, rom_flat, info


def validate_step5_join(participant: str, profile_rows: list[dict], info: dict) -> dict:
    """Guard the Step-5 -> NV-profile join; raise on a silently-empty merge.

    The failure this exists to catch: Step 8 running before Step 5, or pointed at the
    wrong results tree, which yields ``step5_organization=False`` for every link and
    makes S3 unreachable for pipeline reasons rather than scientific ones.
    """
    if not profile_rows:
        return {"n_profile_rows": 0, "n_matched": 0, "n_unmatched": 0, "n_org_true": 0}

    matched = [r for r in profile_rows if r.get("step5_matched")]
    unmatched = [r for r in profile_rows if not r.get("step5_matched")]
    n_org_true = sum(1 for r in profile_rows if r.get("step5_organization"))
    report = {
        "n_profile_rows": len(profile_rows),
        "n_matched": len(matched),
        "n_unmatched": len(unmatched),
        "n_org_true": n_org_true,
    }

    if info.get("n_source_rows", 0) and not matched:
        raise Step5JoinError(
            f"{participant}: Step-5 file has {info['n_source_rows']} rows but none joined "
            f"onto the {len(profile_rows)} NV-profile rows. Check comparison_id / link_id "
            f"naming in {info['source']}."
        )
    if info.get("n_organization", 0) and n_org_true == 0:
        raise Step5JoinError(
            f"{participant}: Step-5 reports {info['n_organization']} 'organization' links but "
            f"step5_organization is False for all {len(profile_rows)} NV-profile rows. "
            f"The join is broken — S3 would be unreachable for pipeline reasons. "
            f"Source: {info['source']}"
        )
    if unmatched:
        names = ", ".join(sorted({r["link_id"] for r in unmatched}))
        print(
            f"  [step5] {len(unmatched)} link×comparison rows have no Step-5 amplitude row "
            f"(organization=False, conservative): {names}"
        )
    print(
        f"  [step5] joined {len(matched)}/{len(profile_rows)} rows from {info['source']}; "
        f"organization=True for {n_org_true}"
    )
    return report


def _load_rep_pass(participant: str, step04_root: Path) -> dict[str, bool]:
    """Map comparison_id -> repetition/robustness pass (min top5_overlap >= 0.6)."""
    path = step04_root / "robustness.csv"
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    df = df[df["participant"].astype(str) == str(participant)]
    out: dict[str, bool] = {}
    for comp_id, g in df.groupby("comparison_id"):
        ov = pd.to_numeric(g["top5_overlap"], errors="coerce").dropna()
        out[str(comp_id)] = bool(len(ov) and ov.min() >= 0.6)
    return out


def _link_rows_from_comparison(
    comp: jcvpca.ComparisonResult,
    participant: str,
    *,
    timepoint: str,
    aggregation_level: str,
    exercise_set: str,
    exercise_id: int | None,
    n_exercises: int,
    excluded_exercise: str,
    reference_direction: str,
    coverage: dict,
    qc_status: str,
    valid_frames_a: int,
    valid_frames_b: int,
) -> list[dict]:
    lt = comp.link_table
    grouped = lt.groupby("link_id")["JcvPCA_link"]
    signed_means = grouped.mean()
    mag_means = grouped.apply(lambda s: float(np.mean(np.abs(s.to_numpy()))))
    evr = comp.evr_table["explained_variance_ratio"].to_numpy()
    bands = _pc_band_sizes(evr, comp.selected_m)
    rows: list[dict] = []
    for link_id, signed in signed_means.items():
        mag = float(mag_means[link_id])
        rows.append(
            {
                "participant": participant,
                "timepoint": timepoint,
                "comparison_id": comp.comparison_id,
                "aggregation_level": aggregation_level,
                "exercise_set": exercise_set,
                "exercise_id": exercise_id if exercise_id is not None else "",
                "n_exercises": n_exercises,
                "excluded_exercise": excluded_exercise,
                "reference_direction": reference_direction,
                "selected_m": comp.selected_m,
                **bands,
                "link_id": link_id,
                "delta_jcvpca_signed": round(float(signed), 6),
                "delta_jcvpca_abs": round(abs(float(signed)), 6),
                "delta_jcvpca_mag": round(mag, 6),
                "coverage_abs": coverage.get("coverage_abs", float("nan")),
                "coverage_rel": coverage.get("coverage_rel", float("nan")),
                "coverage_band": coverage.get("coverage_band", ""),
                "valid_frames_reference": valid_frames_a,
                "valid_frames_comparison": valid_frames_b,
                "qc_status": qc_status,
            }
        )
    return rows


def _coverage_record(
    participant: str,
    comparison_id: str,
    comparison_kind: str,
    a_label: str,
    b_label: str,
    a_df: pd.DataFrame,
    b_df: pd.DataFrame,
    features: list[str],
    vt: float,
    *,
    timepoint: str = "",
    aggregation_level: str = "",
) -> dict:
    cov = compute_subspace_coverage(a_df, b_df, features, vt)
    return {
        "participant": participant,
        "comparison_id": comparison_id,
        "comparison_kind": comparison_kind,
        "timepoint": timepoint,
        "aggregation_level": aggregation_level,
        "a_label": a_label,
        "b_label": b_label,
        "n_rows_a": len(a_df),
        "n_rows_b": len(b_df),
        **cov,
    }


def _add_nv_comparison(
    participant: str,
    config,
    selection,
    features: list[str],
    vt: float,
    region_fn,
    *,
    timepoint: str,
    aggregation_level: str,
    exercise_set: str,
    exercise_ids: list[int],
    exercise_id: int | None,
    n_exercises: int,
    excluded_exercise: str,
    a_rep: str,
    b_rep: str,
    reference_direction: str,
    nv_rows: list[dict],
    coverage_rows: list[dict],
) -> None:
    a_df = (
        _centered_concat(participant, timepoint, a_rep, exercise_ids, config)
        if aggregation_level == "ex11_13_aggregate"
        else _session_matrix(config, participant, timepoint, a_rep, exercise_ids)
    )
    b_df = (
        _centered_concat(participant, timepoint, b_rep, exercise_ids, config)
        if aggregation_level == "ex11_13_aggregate"
        else _session_matrix(config, participant, timepoint, b_rep, exercise_ids)
    )
    if a_df is None or b_df is None:
        return

    ex_tag = f"ex{exercise_id:02d}" if exercise_id is not None else exercise_set
    comp_id = f"{participant}_{timepoint}_{reference_direction}_{ex_tag}"
    a_label = f"{participant}_{timepoint}_{a_rep}"
    b_label = f"{participant}_{timepoint}_{b_rep}"

    cov = compute_subspace_coverage(a_df, b_df, features, vt)
    coverage_rows.append(
        _coverage_record(
            participant,
            comp_id,
            "natural_variability",
            a_label,
            b_label,
            a_df,
            b_df,
            features,
            vt,
            timepoint=timepoint,
            aggregation_level=aggregation_level,
        )
    )

    comp = _safe_comparison(
        comp_id,
        "natural_variability",
        a_label,
        b_label,
        a_df,
        b_df,
        features,
        vt,
        region_fn,
        config=config,
        participant=participant,
        a_session_ids=[marker_gap_policy.timepoint_session(participant, timepoint, a_rep)],
        b_session_ids=[marker_gap_policy.timepoint_session(participant, timepoint, b_rep)],
    )
    if comp is None:
        return

    nv_rows.extend(
        _link_rows_from_comparison(
            comp,
            participant,
            timepoint=timepoint,
            aggregation_level=aggregation_level,
            exercise_set=exercise_set,
            exercise_id=exercise_id,
            n_exercises=n_exercises,
            excluded_exercise=excluded_exercise,
            reference_direction=reference_direction,
            coverage=cov,
            qc_status="ok",
            valid_frames_a=len(a_df),
            valid_frames_b=len(b_df),
        )
    )


def _link_mean_abs(comp: jcvpca.ComparisonResult | None) -> pd.Series:
    """Deprecated-secondary abs read: |signed mean of per-PC ΔJcvPCA_link|."""
    if comp is None:
        return pd.Series(dtype=float)
    return (
        comp.link_table.groupby("link_id")["JcvPCA_link"]
        .mean()
        .abs()
        .rename("abs_delta")
    )


def build_nv_evidence_and_profile(
    participant: str,
    config,
    selection,
    vt: float,
    region_fn,
    coverage_rows: list[dict],
    pooled_primary_dir: Path,
    step04_root: Path,
    step05_root: Path | None = None,
    require_step05: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Matched single-rep footing → NV_EVIDENCE (abs + signed) and NV_PROFILE (v6 tiers).

    Floor (``T1_R1 vs T1_R2``) and effect (``T1_R1 vs T{k}_R1``) share A = ``T1_R1``,
    so EVR weights are identical → clean signed comparison. The reverse-anchor effect
    (``T1_R2 vs T{k}_R1``) probes reference-direction stability (S2 gate).
    """
    features = selection.feature_columns()
    step5_org, step5_rom_flat, step5_info = load_step5_evidence(
        participant,
        step05_root or default_step05_root(step04_root),
        require=require_step05,
    )
    rep_pass_map = _load_rep_pass(participant, step04_root)

    nv_comp = _comp_on(
        participant, config, features, vt, region_fn,
        a_tp="T1", a_rep="R1", b_tp="T1", b_rep="R2",
        exercise_ids=GROUP4_IDS, comparison_id=f"{participant}_T1_R1_vs_R2_ex09_13",
        kind="natural_variability",
    )
    nv_rev_comp = _comp_on(
        participant, config, features, vt, region_fn,
        a_tp="T1", a_rep="R2", b_tp="T1", b_rep="R1",
        exercise_ids=GROUP4_IDS, comparison_id=f"{participant}_T1_R2_vs_R1_ex09_13",
        kind="natural_variability",
    )
    nv_abs = _link_mean_abs(nv_comp)
    nv_signed = nv_profile.link_signed_value(nv_comp.link_table if nv_comp else None)
    nv_signed_rev = nv_profile.link_signed_value(nv_rev_comp.link_table if nv_rev_comp else None)

    evidence_rows: list[dict] = []
    profile_rows: list[dict] = []
    for followup in ("T2", "T3"):
        comp_id = f"{participant}_T1_vs_{followup}"
        long_comp = _comp_on(
            participant, config, features, vt, region_fn,
            a_tp="T1", a_rep="R1", b_tp=followup, b_rep="R1",
            exercise_ids=GROUP4_IDS, comparison_id=f"{comp_id}_single_R1",
        )
        long_rev_comp = _comp_on(
            participant, config, features, vt, region_fn,
            a_tp="T1", a_rep="R2", b_tp=followup, b_rep="R1",
            exercise_ids=GROUP4_IDS, comparison_id=f"{comp_id}_single_R2anchor",
        )
        if long_comp is not None:
            a_df = _session_matrix(config, participant, "T1", "R1", GROUP4_IDS)
            b_df = _session_matrix(config, participant, followup, "R1", GROUP4_IDS)
            if a_df is not None and b_df is not None:
                coverage_rows.append(
                    _coverage_record(
                        participant, f"{comp_id}_single_R1", "longitudinal_single",
                        f"{participant}_T1_R1", f"{participant}_{followup}_R1",
                        a_df, b_df, features, vt,
                        timepoint=followup, aggregation_level="ex09_13_matched_single",
                    )
                )
        cov_row = next(
            (r for r in coverage_rows if r["comparison_id"] == f"{comp_id}_single_R1"), {}
        )
        coverage_band = cov_row.get("coverage_band", "")
        coverage_rel = cov_row.get("coverage_rel", np.nan)
        coverage_ok = coverage_band == "adequate"
        rep_pass = bool(rep_pass_map.get(comp_id, False))

        long_abs = _link_mean_abs(long_comp)

        pooled_path = pooled_primary_dir / "link_level_results.csv"
        pooled_means = pd.Series(dtype=float)
        if pooled_path.exists():
            pooled_lt = pd.read_csv(pooled_path)
            pooled_lt = pooled_lt[pooled_lt["comparison_id"] == comp_id]
            if not pooled_lt.empty:
                pooled_means = pooled_lt.groupby("link_id")["JcvPCA_link"].mean().abs()

        # --- v6 signed profile ---
        profile = nv_profile.compute_link_nv_metrics(
            nv_comp.link_table if nv_comp else pd.DataFrame(),
            long_comp.link_table if long_comp else pd.DataFrame(),
            long_rev_comp.link_table if long_rev_comp else None,
            weighted=True,
            eps_sign=nv_profile.EPS_SIGN,
        )
        for _, r in profile.iterrows():
            link = r["link_id"]
            base_tier = r["nv_profile_tier"]
            key = (comp_id, link)
            org = bool(step5_org.get(key, False))
            rom_flat = bool(step5_rom_flat.get(key, False))
            final_tier = nv_profile.elevate_to_s3(base_tier, coverage_ok, rep_pass, org)
            # Sensitivity only: ROM flatness without Step-5's pooled-footing NV test,
            # which S2's matched single-rep floor already supersedes. Never governing.
            romflat_tier = nv_profile.elevate_to_s3(base_tier, coverage_ok, rep_pass, rom_flat)
            profile_rows.append(
                {
                    "participant": participant,
                    "comparison_id": comp_id,
                    "link_id": link,
                    "nv_signed_t1": r["nv_signed_t1"],
                    "nv_signed_t1_reverse": round(float(nv_signed_rev.get(link, np.nan)), 6)
                    if link in nv_signed_rev.index else np.nan,
                    "long_signed_single": r["long_signed_single"],
                    "long_signed_single_rev": r["long_signed_single_rev"],
                    "matched_abs_ratio": r["matched_abs_ratio"],
                    "magnitude_exceed": bool(r["magnitude_exceed"]),
                    "sign_reference_stable": bool(r["sign_reference_stable"]),
                    "nv_floor_unstable": bool(r["nv_floor_unstable"]),
                    "nv_profile_tier_base": base_tier,
                    "coverage_band": coverage_band,
                    "coverage_rel": coverage_rel,
                    "coverage_ok": coverage_ok,
                    "rep_pass": rep_pass,
                    "step5_organization": org,
                    "step5_rom_flat": rom_flat,
                    "step5_matched": key in step5_org,
                    "nv_profile_tier": final_tier,
                    "nv_profile_tier_romflat": romflat_tier,
                    "a2_pass": final_tier in (nv_profile.TIER_S2, nv_profile.TIER_S3),
                }
            )

        # --- deprecated-secondary abs evidence (retained one release) ---
        links = sorted(set(nv_abs.index) | set(long_abs.index) | set(pooled_means.index))
        signed_lookup = {row["link_id"]: row for row in profile_rows if row["comparison_id"] == comp_id}
        for link in links:
            nv_v = float(nv_abs.get(link, np.nan))
            long_v = float(long_abs.get(link, np.nan))
            ratio = long_v / (nv_v + EPS) if np.isfinite(long_v) and np.isfinite(nv_v) else float("nan")
            sr = signed_lookup.get(link, {})
            evidence_rows.append(
                {
                    "participant": participant,
                    "comparison_id": comp_id,
                    "link_id": link,
                    "longitudinal_abs_delta_single": round(long_v, 6) if np.isfinite(long_v) else np.nan,
                    "nv_abs_delta_single_t1": round(nv_v, 6) if np.isfinite(nv_v) else np.nan,
                    "matched_single_rep_ratio": round(ratio, 4) if np.isfinite(ratio) else np.nan,
                    "exceeds_observed_variability": bool(np.isfinite(ratio) and ratio > NV_EXCEED),
                    "long_signed_single": sr.get("long_signed_single", np.nan),
                    "nv_signed_t1": sr.get("nv_signed_t1", np.nan),
                    "nv_profile_tier": sr.get("nv_profile_tier", ""),
                    "a2_pass": sr.get("a2_pass", False),
                    "longitudinal_abs_delta_pooled": round(float(pooled_means.get(link, np.nan)), 6)
                    if link in pooled_means.index else np.nan,
                    "coverage_abs": cov_row.get("coverage_abs", np.nan),
                    "coverage_rel": coverage_rel,
                    "coverage_band": coverage_band,
                }
            )
    validate_step5_join(participant, profile_rows, step5_info)
    return pd.DataFrame(evidence_rows), pd.DataFrame(profile_rows)


def build_link_exercise_longitudinal(
    participant: str,
    config,
    selection,
    vt: float,
    region_fn,
) -> pd.DataFrame:
    """Per-exercise signed stratum (diagnostic; protocol-openness only, NOT the A2 gate).

    For each exercise: nv_ex (``T1_R1 vs T1_R2``) vs long_ex (``T1_R1 vs T{k}_R1``),
    with reverse anchor (``T1_R2 vs T{k}_R1``) for direction stability. Same-movement
    matched footing on a single exercise.
    """
    features = selection.feature_columns()
    rows: list[dict] = []
    for ex_id in GROUP4_IDS:
        ex_tag = f"ex{ex_id:02d}"
        nv_ex = _comp_on(
            participant, config, features, vt, region_fn,
            a_tp="T1", a_rep="R1", b_tp="T1", b_rep="R2",
            exercise_ids=[ex_id], comparison_id=f"{participant}_T1_R1vsR2_{ex_tag}",
            kind="natural_variability",
        )
        if nv_ex is None:
            continue
        for followup in ("T2", "T3"):
            long_ex = _comp_on(
                participant, config, features, vt, region_fn,
                a_tp="T1", a_rep="R1", b_tp=followup, b_rep="R1",
                exercise_ids=[ex_id], comparison_id=f"{participant}_T1vs{followup}_{ex_tag}",
            )
            long_ex_rev = _comp_on(
                participant, config, features, vt, region_fn,
                a_tp="T1", a_rep="R2", b_tp=followup, b_rep="R1",
                exercise_ids=[ex_id], comparison_id=f"{participant}_T1R2vs{followup}_{ex_tag}",
            )
            if long_ex is None:
                continue
            profile = nv_profile.compute_link_nv_metrics(
                nv_ex.link_table,
                long_ex.link_table,
                long_ex_rev.link_table if long_ex_rev else None,
                weighted=True,
            )
            for _, r in profile.iterrows():
                rows.append(
                    {
                        "participant": participant,
                        "comparison_id": f"{participant}_T1_vs_{followup}",
                        "exercise": ex_tag,
                        "link_id": r["link_id"],
                        "nv_signed_ex_t1": r["nv_signed_t1"],
                        "long_signed_ex": r["long_signed_single"],
                        "long_signed_ex_rev": r["long_signed_single_rev"],
                        "matched_abs_ratio": r["matched_abs_ratio"],
                        "stratum_tier": r["nv_profile_tier"],
                        "sign_reference_stable": bool(r["sign_reference_stable"]),
                        "nv_floor_unstable": bool(r["nv_floor_unstable"]),
                        "interpretation_note": "per-exercise diagnostic; not pooled A2 estimand",
                    }
                )
    return pd.DataFrame(rows)


def build_link_exercise_nv(nv_observed: pd.DataFrame, participant: str) -> pd.DataFrame:
    """Per link × exercise × timepoint × direction signed NV (no cross-link means)."""
    sub = nv_observed[
        (nv_observed["participant"] == participant)
        & (nv_observed["aggregation_level"] == "single_exercise")
    ].copy()
    if sub.empty:
        return pd.DataFrame()
    keep = [
        "participant", "timepoint", "exercise_set", "exercise_id", "reference_direction",
        "link_id", "delta_jcvpca_signed", "delta_jcvpca_abs", "delta_jcvpca_mag", "selected_m",
        "p_functional_50", "p_functional_60", "coverage_band",
    ]
    keep = [c for c in keep if c in sub.columns]
    return sub[keep].reset_index(drop=True)


def build_exercise_level_nv(nv_observed: pd.DataFrame, participant: str) -> pd.DataFrame:
    sub = nv_observed[
        (nv_observed["participant"] == participant)
        & (nv_observed["aggregation_level"] == "single_exercise")
        & (nv_observed["reference_direction"] == "R1_to_R2")
    ].copy()
    if sub.empty:
        return pd.DataFrame()

    mag_col = "delta_jcvpca_mag" if "delta_jcvpca_mag" in sub.columns else "delta_jcvpca_abs"
    rows: list[dict] = []
    for (tp, ex_id), g in sub.groupby(["timepoint", "exercise_id"]):
        ex_label = f"ex{int(ex_id):02d}"
        mean_mag = float(g[mag_col].mean())
        median_mag = float(g[mag_col].median())
        rows.append(
            {
                "participant": participant,
                "timepoint": tp,
                "exercise": ex_label,
                "mean_abs_nv": round(mean_mag, 6),
                "median_abs_nv": round(median_mag, 6),
                "max_abs_nv": round(float(g[mag_col].max()), 6),
                "top_link": g.sort_values(mag_col, ascending=False).iloc[0]["link_id"],
                "n_links": len(g),
                "selected_m": int(g["selected_m"].iloc[0]),
                "p_functional_50": int(g["p_functional_50"].iloc[0]),
                "p_functional_60": int(g["p_functional_60"].iloc[0]),
            }
        )

    df = pd.DataFrame(rows)
    for tp, tp_df in df.groupby("timepoint"):
        order = tp_df.sort_values("median_abs_nv", ascending=False)["exercise"].tolist()
        rank_map = {ex: i + 1 for i, ex in enumerate(order)}
        df.loc[df["timepoint"] == tp, "exercise_nv_rank"] = df.loc[df["timepoint"] == tp, "exercise"].map(rank_map)
        ex09 = tp_df.loc[tp_df["exercise"] == "ex09", "median_abs_nv"]
        ex13 = tp_df.loc[tp_df["exercise"] == "ex13", "median_abs_nv"]
        if len(ex09) and len(ex13) and float(ex09.iloc[0]) > 0:
            ratio = float(ex13.iloc[0]) / float(ex09.iloc[0])
            df.loc[(df["timepoint"] == tp) & (df["exercise"] == "ex13"), "ex13_over_ex09_ratio"] = round(ratio, 3)
        df.loc[(df["timepoint"] == tp) & (df["exercise"] != "ex13"), "ex13_over_ex09_ratio"] = np.nan
    df["interpretation_note"] = "descriptive protocol-openness only; not skill or treatment"
    return df


def build_nv_summary(
    nv_evidence: pd.DataFrame,
    nv_observed: pd.DataFrame,
    participant: str,
    nv_profile_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    ev = nv_evidence[nv_evidence["participant"] == participant].copy()
    if ev.empty:
        return pd.DataFrame()

    prof = (
        nv_profile_df[nv_profile_df["participant"] == participant]
        if nv_profile_df is not None and not nv_profile_df.empty
        else pd.DataFrame()
    )
    tier_by_link: dict[str, dict] = {}
    if not prof.empty:
        for link, g in prof.groupby("link_id"):
            tier_by_link[link] = {
                "n_S2": int((g["nv_profile_tier"] == "S2").sum()),
                "n_S3": int((g["nv_profile_tier"] == "S3").sum()),
                "n_a2_pass": int(g["a2_pass"].sum()),
                "tiers": ",".join(f"{r.comparison_id.split('_')[-1]}:{r.nv_profile_tier}" for r in g.itertuples()),
            }

    t1_ex = nv_observed[
        (nv_observed["participant"] == participant)
        & (nv_observed["aggregation_level"] == "single_exercise")
        & (nv_observed["timepoint"] == "T1")
        & (nv_observed["reference_direction"] == "R1_to_R2")
    ]
    mag_col = "delta_jcvpca_mag" if "delta_jcvpca_mag" in t1_ex.columns else "delta_jcvpca_abs"
    ex_medians = (
        t1_ex.groupby("exercise_id")[mag_col].median().sort_values(ascending=False)
        if not t1_ex.empty
        else pd.Series(dtype=float)
    )
    dominant_ex = str(ex_medians.index[0]) if len(ex_medians) else ""
    dominant_flag = False
    if len(ex_medians) >= 2:
        dominant_flag = float(ex_medians.iloc[0]) > 2.0 * float(ex_medians.iloc[1:].median())

    rows = []
    for link, g in ev.groupby("link_id"):
        tinfo = tier_by_link.get(link, {})
        rows.append(
            {
                "participant": participant,
                "link_id": link,
                "n_comparisons": len(g),
                "n_S2_signed_consistent": tinfo.get("n_S2", 0),
                "n_S3_candidate": tinfo.get("n_S3", 0),
                "n_a2_pass": tinfo.get("n_a2_pass", 0),
                "signed_tiers": tinfo.get("tiers", ""),
                "n_exceed_matched_ratio_abs": int(g["exceeds_observed_variability"].sum()),
                "median_matched_single_rep_ratio": round(float(g["matched_single_rep_ratio"].median()), 4),
                "max_matched_single_rep_ratio": round(float(g["matched_single_rep_ratio"].max()), 4),
                "dominant_exercise_flag": dominant_flag,
                "dominant_exercise_id_t1": dominant_ex,
                "interpretation_note": "v6: A2 = signed S2/S3; abs ratio deprecated-secondary",
            }
        )
    return pd.DataFrame(rows)


def write_protocol_openness(path: Path, exercise_nv: pd.DataFrame) -> None:
    lines = [
        "# Exercise protocol openness — Step 8h (descriptive)",
        "",
        "Compares per-exercise observed NV (T{k}_R1 vs T{k}_R2, R1→R2, single segment) across T1/T2/T3.",
        "Per link: mean(|JcvPCA_link|) over PCs; per exercise: median across links.",
        "**Not** improvisation skill, learning, or treatment effect.",
        "",
        "## ex13 / ex09 ratio (median link mean-|ΔJcvPCA|)",
        "",
        "| participant | T1 | T2 | T3 |",
        "|---|---:|---:|---:|",
    ]
    for pid in PARTICIPANTS:
        sub = exercise_nv[exercise_nv["participant"] == pid]
        vals = []
        for tp in TIMEPOINTS:
            row = sub[(sub["timepoint"] == tp) & (sub["exercise"] == "ex13")]
            vals.append(str(row["ex13_over_ex09_ratio"].iloc[0]) if len(row) else "—")
        lines.append(f"| {pid} | {' | '.join(vals)} |")

    lines.extend(["", "## Rank order by median_abs_nv (T1)", ""])
    for pid in PARTICIPANTS:
        sub = exercise_nv[(exercise_nv["participant"] == pid) & (exercise_nv["timepoint"] == "T1")]
        if sub.empty:
            continue
        ordered = sub.sort_values("exercise_nv_rank")["exercise"].tolist()
        lines.append(f"- **{pid}:** {', '.join(ordered)}")

    lines.extend(
        [
            "",
            "## Limits",
            "",
            "- n ≈ 5 exercise units × 2 reps — descriptive reference range only.",
            "- Cross-check ROM rep spread (Step 5) before interpretive protocol-openness language.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_supervisor_template(path: Path) -> None:
    # v6: never clobber a filled-in Phase-0 decision doc.
    if path.exists():
        return
    path.write_text(
        """# Supervisor NV decision — Step 8

**Status:** pending supervisor meeting

## Adopted wording for committee brief

| Field | Decision |
|---|---|
| NV reference label | _e.g. observed repetition variability / reference range_ |
| Exceed-floor rule | matched single-rep ratio > 1 (descriptive) |
| Coverage-limited pairs | _list participant × comparison if any severe_ |
| Protocol-openness language | _adopt / soften / omit ex13 vs ex09 read_ |
| Interpretive claims approved | _participant × comparison list or none_ |

## Sign-off

| Name | Date | Notes |
|---|---|---|
| | | |

""",
        encoding="utf-8",
    )


def process_participant(
    config,
    participant: str,
    out_dir: Path,
    primary_root: Path,
    step05_root: Path | None = None,
    require_step05: bool = True,
) -> tuple[pd.DataFrame, ...]:
    sel_path = config.resolve_path("outputs.root") / "selections" / f"{participant}_{WINDOW}.yaml"
    selection = load_selection(sel_path)
    features = selection.feature_columns()
    vt = float(config.get("pca.variance_threshold", 0.80))
    region_fn = lambda stem: region_of_link(stem, config)

    nv_rows: list[dict] = []
    coverage_rows: list[dict] = []

    for tp in TIMEPOINTS:
        for ex_id in GROUP4_IDS:
            for direction, a_rep, b_rep in (
                ("R1_to_R2", "R1", "R2"),
                ("R2_to_R1", "R2", "R1"),
            ):
                _add_nv_comparison(
                    participant,
                    config,
                    selection,
                    features,
                    vt,
                    region_fn,
                    timepoint=tp,
                    aggregation_level="single_exercise",
                    exercise_set=f"ex{ex_id:02d}",
                    exercise_ids=[ex_id],
                    exercise_id=ex_id,
                    n_exercises=1,
                    excluded_exercise="",
                    a_rep=a_rep,
                    b_rep=b_rep,
                    reference_direction=direction,
                    nv_rows=nv_rows,
                    coverage_rows=coverage_rows,
                )

        for direction, a_rep, b_rep in (("R1_to_R2", "R1", "R2"), ("R2_to_R1", "R2", "R1")):
            _add_nv_comparison(
                participant,
                config,
                selection,
                features,
                vt,
                region_fn,
                timepoint=tp,
                aggregation_level="ex09_13_protocol_reference",
                exercise_set="ex09_13",
                exercise_ids=GROUP4_IDS,
                exercise_id=None,
                n_exercises=5,
                excluded_exercise="",
                a_rep=a_rep,
                b_rep=b_rep,
                reference_direction=direction,
                nv_rows=nv_rows,
                coverage_rows=coverage_rows,
            )

        for direction, a_rep, b_rep in (("R1_to_R2", "R1", "R2"), ("R2_to_R1", "R2", "R1")):
            _add_nv_comparison(
                participant,
                config,
                selection,
                features,
                vt,
                region_fn,
                timepoint=tp,
                aggregation_level="ex11_13_aggregate",
                exercise_set="ex11_13",
                exercise_ids=EX11_13_IDS,
                exercise_id=None,
                n_exercises=3,
                excluded_exercise="",
                a_rep=a_rep,
                b_rep=b_rep,
                reference_direction=direction,
                nv_rows=nv_rows,
                coverage_rows=coverage_rows,
            )

        for loo_name, loo_ids in LOO_SETS.items():
            _add_nv_comparison(
                participant,
                config,
                selection,
                features,
                vt,
                region_fn,
                timepoint=tp,
                aggregation_level="leave_one_exercise_out",
                exercise_set=loo_name,
                exercise_ids=loo_ids,
                exercise_id=None,
                n_exercises=len(loo_ids),
                excluded_exercise="",
                a_rep="R1",
                b_rep="R2",
                reference_direction="R1_to_R2",
                nv_rows=nv_rows,
                coverage_rows=coverage_rows,
            )

    nv_observed = pd.DataFrame(nv_rows)
    pooled_dir = primary_root / participant / f"{WINDOW}_pooled"
    nv_evidence, nv_profile_df = build_nv_evidence_and_profile(
        participant, config, selection, vt, region_fn, coverage_rows, pooled_dir, primary_root,
        step05_root=step05_root, require_step05=require_step05,
    )
    link_exercise_long = build_link_exercise_longitudinal(
        participant, config, selection, vt, region_fn
    )
    link_exercise_nv = build_link_exercise_nv(nv_observed, participant)
    exercise_nv = build_exercise_level_nv(nv_observed, participant)
    nv_summary = build_nv_summary(nv_evidence, nv_observed, participant, nv_profile_df)
    coverage_df = pd.DataFrame(coverage_rows)

    return (
        nv_observed, nv_evidence, nv_profile_df, exercise_nv,
        nv_summary, coverage_df, link_exercise_long, link_exercise_nv,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--participant", choices=PARTICIPANTS)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results_committee_case" / "step08_nv_and_stability",
        help="Committee-case folder for NV tables and summaries",
    )
    parser.add_argument(
        "--primary-root",
        type=Path,
        default=ROOT / "results_committee_case" / "step04_primary_runs",
        help="Step 4 primary runs folder (pooled runs for selected_m lookup)",
    )
    parser.add_argument(
        "--step05-root",
        type=Path,
        default=None,
        help=(
            "Step 5 amplitude-vs-organization folder supplying the S3 organization gate. "
            "Defaults to <primary-root>/../step05_amplitude_vs_organization. Step 5 must "
            "have run first, otherwise S3 is unreachable."
        ),
    )
    parser.add_argument(
        "--allow-missing-step05",
        action="store_true",
        help="Proceed with step5_organization=False (no S3) instead of failing when Step 5 is absent",
    )
    args = parser.parse_args()

    config = load_config()
    out_dir = args.output_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    primary_root = args.primary_root.resolve()
    step05_root = (
        args.step05_root.resolve() if args.step05_root else default_step05_root(primary_root)
    )
    print(f"Step-5 evidence root: {step05_root}")
    pids = [args.participant] if args.participant else list(PARTICIPANTS)

    # Fail before the (multi-minute) NV recomputation rather than after it.
    for pid in pids:
        load_step5_evidence(pid, step05_root, require=not args.allow_missing_step05)

    nv_frames, ev_frames, prof_frames = [], [], []
    ex_frames, sum_frames, cov_frames = [], [], []
    lex_long_frames, lex_nv_frames = [], []
    for pid in pids:
        print(f"=== {pid} ===")
        nv, ev, prof, ex, sm, cov, lex_long, lex_nv = process_participant(
            config, pid, out_dir, primary_root,
            step05_root=step05_root,
            require_step05=not args.allow_missing_step05,
        )
        nv_frames.append(nv)
        ev_frames.append(ev)
        prof_frames.append(prof)
        ex_frames.append(ex)
        sum_frames.append(sm)
        cov_frames.append(cov)
        lex_long_frames.append(lex_long)
        lex_nv_frames.append(lex_nv)
        n_s2 = int((prof["nv_profile_tier"] == "S2").sum()) if not prof.empty else 0
        n_s3 = int((prof["nv_profile_tier"] == "S3").sum()) if not prof.empty else 0
        print(f"  nv_observed: {len(nv)} rows, profile: {len(prof)} rows, S2={n_s2}, S3={n_s3}")

    def _concat(frames):
        frames = [f for f in frames if f is not None and not f.empty]
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    nv_observed = _concat(nv_frames)
    nv_evidence = _concat(ev_frames)
    nv_profile_df = _concat(prof_frames)
    exercise_nv = _concat(ex_frames)
    nv_summary = _concat(sum_frames)
    coverage = _concat(cov_frames)
    if not coverage.empty:
        coverage = coverage.drop_duplicates(subset=["participant", "comparison_id"])
    link_exercise_long = _concat(lex_long_frames)
    link_exercise_nv = _concat(lex_nv_frames)

    nv_observed.to_csv(out_dir / "nv_observed.csv", index=False)
    nv_evidence.to_csv(out_dir / "NV_EVIDENCE.csv", index=False)
    nv_profile_df.to_csv(out_dir / "NV_PROFILE.csv", index=False)
    exercise_nv.to_csv(out_dir / "exercise_level_nv.csv", index=False)
    nv_summary.to_csv(out_dir / "nv_summary.csv", index=False)
    coverage.to_csv(out_dir / "coverage.csv", index=False)
    link_exercise_long.to_csv(out_dir / "link_exercise_longitudinal.csv", index=False)
    link_exercise_nv.to_csv(out_dir / "link_exercise_nv.csv", index=False)
    write_protocol_openness(out_dir / "EXERCISE_PROTOCOL_OPENNESS.md", exercise_nv)
    write_supervisor_template(out_dir / "SUPERVISOR_NV_DECISION.md")

    print(f"\nWrote {out_dir.relative_to(ROOT)}")
    if not nv_profile_df.empty:
        tiers = nv_profile_df.groupby(["participant", "comparison_id"])["nv_profile_tier"].value_counts()
        print("Signed NV tier counts (links):")
        print(tiers.to_string())
        n_s3 = int((nv_profile_df["nv_profile_tier"] == nv_profile.TIER_S3).sum())
        n_s3_rf = int((nv_profile_df["nv_profile_tier_romflat"] == nv_profile.TIER_S3).sum())
        print(
            f"S3 (governing, Step-5 organization): {n_s3} · "
            f"S3 (sensitivity, ROM-flat only): {n_s3_rf}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
