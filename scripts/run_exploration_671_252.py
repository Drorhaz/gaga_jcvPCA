"""Batch driver: contiguous exercise-window jcvPCA sweep for participants 671 & 252.

For each participant this enumerates every single exercise and every contiguous
span over an exercise range (default ex09..ex15), authors a selection YAML, and
runs the analysis in both repetition modes (pooled ideal + single fallback) with
statistical validation. Each run folder is copied under a results tree, and a
ranking summary + decision log are built from the validation outputs.

The script is generic over participant, exercise range, and manifest (nothing is
hardcoded to Group 4), so it scales to ex01..ex17 and future participants.

Usage:
    python scripts/run_exploration_671_252.py
    python scripts/run_exploration_671_252.py --participants 671 --ex-range 9 15
    python scripts/run_exploration_671_252.py --rank-only        # rebuild summaries
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca import pipeline, project_io  # noqa: E402
from gaga_jcvpca.config import load_config  # noqa: E402
from gaga_jcvpca.feature_manifest_gen import (  # noqa: E402
    DEFAULT_MANIFEST_BY_PARTICIPANT,
    resolve_manifest_path,
)
from gaga_jcvpca.selection import AnalysisSelection, default_selection, save_selection  # noqa: E402

RESULTS_DIRNAME = "results_exploration_671_252"
MODES = ("pooled", "single")


def contiguous_spans(ex_ids: list[int]) -> list[tuple[int, ...]]:
    """All contiguous subsequences (length >= 1) of a sorted exercise-id list."""
    spans: list[tuple[int, ...]] = []
    n = len(ex_ids)
    for i in range(n):
        for j in range(i, n):
            spans.append(tuple(ex_ids[i : j + 1]))
    return spans


def span_label(span: tuple[int, ...]) -> str:
    if len(span) == 1:
        return f"ex{span[0]:02d}_single"
    return f"ex{span[0]:02d}_{span[-1]:02d}_contiguous"


def base_link_choices(config, participant: str):
    """Default (QC-driven) link set for a participant from its feature manifest."""
    manifest_dir = config.resolve_path("data.feature_manifests")
    manifest_path = resolve_manifest_path(participant, manifest_dir, DEFAULT_MANIFEST_BY_PARTICIPANT)
    if manifest_path is None:
        raise SystemExit(f"No feature manifest for participant {participant}")
    manifest = project_io.load_feature_manifest(manifest_path)
    sel = default_selection(f"{participant}_base", participant, manifest, config)
    return sel.links


def build_selection(config, participant: str, span: tuple[int, ...], links) -> AnalysisSelection:
    return AnalysisSelection(
        name=f"{participant}_{span_label(span)}",
        participant=participant,
        exercise_ids=list(span),
        combine_exercises=len(span) > 1,
        links=links,
        notes=(
            f"Exploration selection: {'combined' if len(span) > 1 else 'single'} "
            f"exercise window(s) {list(span)} for participant {participant}."
        ),
        created_at=datetime.now().isoformat(timespec="seconds"),
    )


def run_sweep(config, participants: list[str], ex_range: tuple[int, int]) -> Path:
    results_root = config.project_root / RESULTS_DIRNAME
    sel_dir = results_root / "selections"
    runs_root_dst = results_root / "runs"
    outputs_sel_dir = config.resolve_path("outputs.root") / "selections"
    ex_ids = list(range(ex_range[0], ex_range[1] + 1))
    spans = contiguous_spans(ex_ids)

    for participant in participants:
        links = base_link_choices(config, participant)
        n_links = sum(1 for c in links if c.included)
        print(f"\n=== participant {participant}: {len(spans)} spans x {len(MODES)} modes, {n_links} links ===")
        for span in spans:
            label = span_label(span)
            selection = build_selection(config, participant, span, links)
            # persist selection both in the results tree and where the CLI looks
            save_selection(selection, sel_dir)
            save_selection(selection, outputs_sel_dir)
            for mode in MODES:
                run_id = f"{participant}_{label}_{mode}"
                try:
                    run_dir = pipeline.run_analysis(
                        config,
                        selection,
                        timepoints=["T1", "T2", "T3"],
                        repetitions=["R1", "R2"],
                        reference_timepoint="T1",
                        repetition_mode=mode,
                        run_validation=True,
                        run_id=run_id,
                    )
                except Exception as exc:  # keep the sweep going; log and continue
                    print(f"  FAIL {run_id}: {exc}")
                    continue
                dst = runs_root_dst / participant / label / mode
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(run_dir, dst)
                print(f"  ok {run_id} -> {dst.relative_to(config.project_root)}")
    return results_root


# --- ranking ---

def _parse_nv_rows(val_df: pd.DataFrame) -> pd.DataFrame:
    """Extract per-link effect_ratio_vs_nv rows, split scope into link + comparison."""
    nv = val_df[val_df["method"] == "natural_variability"].copy()
    if nv.empty:
        return nv
    def _link(scope: str) -> str:
        return scope.split("@", 1)[0]
    def _cmp(scope: str) -> str:
        return scope.split("@", 1)[1] if "@" in scope else "primary"
    nv["link"] = nv["scope"].map(_link)
    nv["comparison"] = nv["scope"].map(_cmp)
    nv["effect_ratio"] = pd.to_numeric(nv["value"], errors="coerce")
    return nv


def build_rankings(config, participants: list[str]) -> None:
    results_root = config.project_root / RESULTS_DIRNAME
    runs_root = results_root / "runs"
    summaries_dir = results_root / "summaries"
    summaries_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for participant in participants:
        p_root = runs_root / participant
        if not p_root.exists():
            continue
        for group_dir in sorted(p_root.iterdir()):
            if not group_dir.is_dir():
                continue
            for mode_dir in sorted(group_dir.iterdir()):
                val_path = mode_dir / "validation_results.csv"
                if not val_path.exists():
                    continue
                val_df = pd.read_csv(val_path)
                nv = _parse_nv_rows(val_df)
                boot_links = val_df[
                    (val_df["method"] == "bootstrap") & (val_df["scope"] != "run")
                ]["scope"].nunique()

                row = {
                    "participant": participant,
                    "group": group_dir.name,
                    "mode": mode_dir.name,
                    "n_bootstrap_supported": int(boot_links),
                }
                comparisons = sorted(nv["comparison"].unique()) if not nv.empty else []
                exceed_counts = []
                mean_ratios = []
                for cmp_id in comparisons:
                    sub = nv[nv["comparison"] == cmp_id]
                    n_exceed = int((sub["effect_ratio"] > 1.0).sum())
                    mean_ratio = float(sub["effect_ratio"].mean()) if not sub.empty else 0.0
                    tag = cmp_id.split("_vs_")[-1] if "_vs_" in cmp_id else cmp_id
                    row[f"n_exceed_nv_{tag}"] = n_exceed
                    row[f"mean_ratio_{tag}"] = round(mean_ratio, 3)
                    exceed_counts.append(n_exceed)
                    mean_ratios.append(mean_ratio)
                row["total_links_exceeding_nv"] = int(sum(exceed_counts))
                row["mean_effect_ratio"] = round(
                    float(sum(mean_ratios) / len(mean_ratios)) if mean_ratios else 0.0, 3
                )
                # consistency: exceeds NV in every scored longitudinal comparison
                row["consistent_across_timepoints"] = bool(
                    len(exceed_counts) >= 2 and all(c > 0 for c in exceed_counts)
                )
                rows.append(row)

    if not rows:
        print("No runs found to rank.")
        return

    df = pd.DataFrame(rows).fillna(0)
    df = df.sort_values(
        ["participant", "total_links_exceeding_nv", "mean_effect_ratio", "n_bootstrap_supported"],
        ascending=[True, False, False, False],
    )
    out_csv = summaries_dir / "ranking.csv"
    df.to_csv(out_csv, index=False)
    print(f"wrote {out_csv} ({len(df)} rows)")

    _write_decision_log(results_root, df, participants)


def _markdown_table(df: pd.DataFrame) -> str:
    """Render a DataFrame as a GitHub markdown table without external deps."""
    cols = list(df.columns)
    header = "| " + " | ".join(str(c) for c in cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    rows = [
        "| " + " | ".join(str(v) for v in rec) + " |"
        for rec in df.itertuples(index=False, name=None)
    ]
    return "\n".join([header, sep, *rows])


def _write_decision_log(results_root: Path, df: pd.DataFrame, participants: list[str]) -> None:
    lines = ["# Decision log — contiguous ex09-15 jcvPCA signal (671 & 252)", ""]
    lines.append(f"_Generated {datetime.now().isoformat(timespec='seconds')}._")
    lines.append("")
    lines.append(
        "Scoring per plan section 7: per link, `effect_ratio = |longitudinal ΔJcvPCA| / "
        "(|NV ΔJcvPCA| + eps)`; a link `exceeds NV` when ratio > 1. Groups are ranked by "
        "(1) total links exceeding NV across T1-vs-T2 and T1-vs-T3, (2) mean effect ratio, "
        "(3) bootstrap-supported links, preferring groups strong in both longitudinal "
        "comparisons. Statistics are strictly within-participant."
    )
    lines.append("")
    for participant in participants:
        pdf = df[df["participant"].astype(str) == str(participant)]
        if pdf.empty:
            continue
        lines.append(f"## Participant {participant}")
        lines.append("")
        # Prefer pooled (ideal) when it has support; otherwise fall back to single.
        pooled = pdf[pdf["mode"] == "pooled"]
        chosen_pool = pooled if not pooled.empty and pooled.iloc[0]["total_links_exceeding_nv"] > 0 else pdf
        winner = chosen_pool.iloc[0]
        design = winner["mode"]
        why = (
            "pooled (ideal: T1(R1+R2) vs T2/T3(R1+R2)) — more frames and cross-take robustness"
            if design == "pooled"
            else "single (fallback: T1_R1 vs Tk_R1) — pooled showed no links beyond NV, so the "
            "single-rep design is reported"
        )
        lines.append(f"- **Winning group:** `{winner['group']}` using **{design}** design.")
        lines.append(f"- **Why this design:** {why}.")
        lines.append(
            f"- **Support:** {int(winner['total_links_exceeding_nv'])} link-comparisons exceed NV; "
            f"mean effect ratio {winner['mean_effect_ratio']}; "
            f"{int(winner['n_bootstrap_supported'])} bootstrap-supported link(s); "
            f"consistent across timepoints: {bool(winner['consistent_across_timepoints'])}."
        )
        lines.append(
            "- **Caveats:** only 2 repetitions -> NV is a descriptive floor, not significance; "
            "single-exercise windows are borderline for bootstrap (down-weighted); Gaga is "
            "improvisational so within-timepoint variability is high. 671 carries a T3 marker-set "
            "prefix confound (skeleton hierarchy taken from the session's own raw header)."
        )
        lines.append("")
        lines.append("Top 5 groups (this participant):")
        lines.append("")
        cols = [c for c in ["group", "mode", "total_links_exceeding_nv", "mean_effect_ratio",
                            "n_bootstrap_supported", "consistent_across_timepoints"] if c in pdf.columns]
        lines.append(_markdown_table(pdf.head(5)[cols]))
        lines.append("")
    (results_root / "decision_log.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {results_root / 'decision_log.md'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Contiguous-exercise jcvPCA exploration sweep.")
    parser.add_argument("--participants", nargs="+", default=["671", "252"])
    parser.add_argument("--ex-range", nargs=2, type=int, default=[9, 15], metavar=("START", "END"))
    parser.add_argument("--rank-only", action="store_true", help="Rebuild summaries from existing runs.")
    args = parser.parse_args()

    cfg = load_config()
    if not args.rank_only:
        run_sweep(cfg, args.participants, (args.ex_range[0], args.ex_range[1]))
    build_rankings(cfg, args.participants)


if __name__ == "__main__":
    main()
