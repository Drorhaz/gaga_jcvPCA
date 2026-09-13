"""Run folders + reproducibility manifest + interpretation text.

Each analysis run produces one self-contained folder ``outputs/runs/<run_id>/``
containing every table, the config + selection snapshots, an interpretation
``run_summary.md``, and a ``reproducibility_manifest.json`` that ties the run to
its exact inputs and parameters. Nothing outside the run folder is needed to
understand or reproduce a run.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import yaml

from gaga_jcvpca.config import Config
from gaga_jcvpca.jcvpca import ComparisonResult
from gaga_jcvpca.marker_gap_policy import partition_excluded_links
from gaga_jcvpca.selection import AnalysisSelection


def new_run_id(prefix: str = "run") -> str:
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def _git_hash(project_root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _file_checksum(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()[:16]
    except OSError:
        return "unavailable"


@dataclass
class RunContext:
    """Everything needed to assemble and reproduce a run."""

    run_id: str
    participant: str
    config: Config
    selection: AnalysisSelection
    filter_settings: dict
    comparisons: list[ComparisonResult] = field(default_factory=list)
    threshold_sweep: Optional[pd.DataFrame] = None
    validation_results: Optional[pd.DataFrame] = None
    validation_summary_md: Optional[str] = None
    input_files: list[Path] = field(default_factory=list)
    marker_set_notes: dict = field(default_factory=dict)
    marker_gap_policy_enabled: bool = False
    marker_gap_removals_path: str = ""


def _kind_label(kind: str) -> str:
    return {
        "longitudinal": "Longitudinal change",
        "natural_variability": "Natural variability (R1 vs R2)",
        "exploratory": "Exploratory (non-inferential)",
    }.get(kind, kind)


def _concat_tables(comparisons: list[ComparisonResult], attr: str) -> pd.DataFrame:
    frames = []
    for c in comparisons:
        df = getattr(c, attr)
        if df is None or df.empty:
            continue
        df = df.copy()
        df.insert(0, "comparison_id", c.comparison_id)
        df.insert(1, "kind", c.kind)
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _top_links(comparison: ComparisonResult, n: int = 5) -> pd.DataFrame:
    lt = comparison.link_table
    if lt.empty:
        return lt
    return (
        lt.assign(abs_delta=lt["JcvPCA_link"].abs())
        .groupby("link_id", as_index=False)["abs_delta"]
        .mean()
        .sort_values("abs_delta", ascending=False)
        .head(n)
    )


def build_run_summary_md(ctx: RunContext) -> str:
    lines: list[str] = []
    lines.append(f"# Run summary — {ctx.run_id}")
    lines.append("")
    lines.append(f"- Participant: **{ctx.participant}** (participant-specific, N-of-1)")
    lines.append(f"- Selection: `{ctx.selection.name}` — {len(ctx.selection.included_links())} links included")
    lines.append(f"- Exercises (authoritative exercise_id): {ctx.selection.exercise_ids}")
    lines.append(
        f"- Variance threshold: {ctx.config.get('pca.variance_threshold')}; "
        f"filter cutoff {ctx.filter_settings.get('cutoff_hz')} Hz "
        f"(order {ctx.filter_settings.get('order')})"
    )
    if ctx.marker_gap_policy_enabled:
        lines.append(
            f"- Marker-gap policy: **on** (`{ctx.marker_gap_removals_path}`) — "
            "session-scoped exclusions listed per comparison when applicable."
        )
    lines.append("")

    if ctx.marker_set_notes:
        lines.append("## Comparability notes")
        for subject, note in ctx.marker_set_notes.items():
            lines.append(f"- **{subject}**: {note}")
        lines.append("")

    lines.append("## Comparisons")
    for c in ctx.comparisons:
        lines.append(f"### {c.comparison_id} — {_kind_label(c.kind)}")
        lines.append(f"- {c.a_label} (reference A) vs {c.b_label} (B)")
        lines.append(f"- selected_m = {c.selected_m} at variance_threshold {c.variance_threshold}")
        lines.append(
            f"- {len(c.included_links)} links analyzed; {len(c.excluded_links)} excluded."
        )
        for w in c.warnings:
            lines.append(f"- Note: {w}")
        top = _top_links(c)
        if not top.empty:
            names = ", ".join(
                f"{r.link_id} ({r.abs_delta:.3f})" for r in top.itertuples()
            )
            lines.append(f"- Largest contribution changes (mean |ΔJcvPCA|): {names}")
        if c.excluded_links:
            marker_excl, other_excl = partition_excluded_links(c.excluded_links)
            if marker_excl:
                excl = "; ".join(f"{k} — {v}" for k, v in marker_excl.items())
                lines.append(f"- Excluded (marker-gap policy): {excl}")
            if other_excl:
                excl = "; ".join(f"{k} — {v}" for k, v in other_excl.items())
                lines.append(f"- Excluded (matrix / rotvec QC): {excl}")
        lines.append("")

    if ctx.threshold_sweep is not None and not ctx.threshold_sweep.empty:
        lines.append("## Variance-threshold sweep")
        lines.append("Threshold robustness of selected_m and the top link:")
        for r in ctx.threshold_sweep.itertuples():
            lines.append(
                f"- threshold {r.variance_threshold}: selected_m={r.selected_m}, "
                f"top link {r.top1_link}"
            )
        lines.append("")

    if ctx.validation_summary_md:
        lines.append("## Statistical validation")
        lines.append(ctx.validation_summary_md)
        lines.append("")
    else:
        lines.append("## Statistical validation")
        lines.append("Not run for this analysis (optional stage).")
        lines.append("")

    lines.append("---")
    lines.append(
        "JcvPCA reports how each body link's contribution to the shared movement-"
        "variance structure differs between the two matched datasets. Values are "
        "descriptive; see the validation section for evidence strength."
    )
    return "\n".join(lines)


def build_manifest(ctx: RunContext) -> dict:
    cfg = ctx.config
    per_comparison = []
    for c in ctx.comparisons:
        per_comparison.append(
            {
                "comparison_id": c.comparison_id,
                "kind": c.kind,
                "a_label": c.a_label,
                "b_label": c.b_label,
                "selected_m": c.selected_m,
                "variance_threshold": c.variance_threshold,
                "included_links": c.included_links,
                "excluded_links": c.excluded_links,
                "excluded_links_marker_gap": partition_excluded_links(c.excluded_links)[0],
                "excluded_links_other": partition_excluded_links(c.excluded_links)[1],
                "warnings": c.warnings,
            }
        )
    return {
        "run_id": ctx.run_id,
        "datetime": datetime.now().isoformat(timespec="seconds"),
        "git_hash": _git_hash(cfg.project_root),
        "science_hash": cfg.science_hash,
        "participant": ctx.participant,
        "participant_specific": True,
        "variance_threshold": cfg.get("pca.variance_threshold"),
        "filter_settings": ctx.filter_settings,
        "selection": ctx.selection.to_dict(),
        "comparisons": per_comparison,
        "marker_gap_policy": {
            "enabled": ctx.marker_gap_policy_enabled,
            "removals_csv": ctx.marker_gap_removals_path,
        },
        "marker_set_difference_notes": ctx.marker_set_notes,
        "input_files": [
            {"path": str(p), "sha256_16": _file_checksum(p)} for p in ctx.input_files
        ],
        "user_overrides": [
            {"link": c.link, "reason": c.reason}
            for c in ctx.selection.links
            if c.user_override
        ],
    }


def write_run(ctx: RunContext) -> Path:
    """Write the self-contained run folder and return its path."""
    runs_root = ctx.config.resolve_path("outputs.runs")
    run_dir = runs_root / ctx.run_id
    (run_dir / "figures").mkdir(parents=True, exist_ok=True)
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)

    # config + selection snapshots
    with open(run_dir / "config_snapshot.yaml", "w", encoding="utf-8") as fh:
        yaml.safe_dump(ctx.config.data, fh, sort_keys=False, allow_unicode=True)
    with open(run_dir / "analysis_selection.yaml", "w", encoding="utf-8") as fh:
        yaml.safe_dump(ctx.selection.to_dict(), fh, sort_keys=False, allow_unicode=True)

    # result tables
    _concat_tables(ctx.comparisons, "axis_table").to_csv(run_dir / "jcvpca_results.csv", index=False)
    _concat_tables(ctx.comparisons, "link_table").to_csv(run_dir / "link_level_results.csv", index=False)
    _concat_tables(ctx.comparisons, "region_table").to_csv(run_dir / "region_level_results.csv", index=False)

    space = _concat_tables(ctx.comparisons, "space_table")
    if not space.empty:
        space[space["space"] == "functional"].to_csv(run_dir / "functional_space_results.csv", index=False)
        space[space["space"] == "null"].to_csv(run_dir / "null_space_results.csv", index=False)

    nv = [c for c in ctx.comparisons if c.kind == "natural_variability"]
    if nv:
        _concat_tables(nv, "link_table").to_csv(run_dir / "natural_variability_results.csv", index=False)

    # selected_m per comparison
    pd.DataFrame(
        [
            {
                "comparison_id": c.comparison_id,
                "kind": c.kind,
                "selected_m": c.selected_m,
                "variance_threshold": c.variance_threshold,
                "n_included_links": len(c.included_links),
                "n_excluded_links": len(c.excluded_links),
            }
            for c in ctx.comparisons
        ]
    ).to_csv(run_dir / "selected_m_by_comparison.csv", index=False)

    if ctx.threshold_sweep is not None and not ctx.threshold_sweep.empty:
        ctx.threshold_sweep.to_csv(run_dir / "threshold_sensitivity.csv", index=False)

    if ctx.validation_results is not None and not ctx.validation_results.empty:
        ctx.validation_results.to_csv(run_dir / "validation_results.csv", index=False)
    if ctx.validation_summary_md:
        with open(run_dir / "validation_summary.md", "w", encoding="utf-8") as fh:
            fh.write(ctx.validation_summary_md)

    marker_gap_audit = {
        c.comparison_id: partition_excluded_links(c.excluded_links)[0]
        for c in ctx.comparisons
        if partition_excluded_links(c.excluded_links)[0]
    }
    if marker_gap_audit:
        with open(run_dir / "marker_gap_excluded_links.json", "w", encoding="utf-8") as fh:
            json.dump(marker_gap_audit, fh, indent=2)

    # interpretation + manifest
    with open(run_dir / "run_summary.md", "w", encoding="utf-8") as fh:
        fh.write(build_run_summary_md(ctx))
    with open(run_dir / "reproducibility_manifest.json", "w", encoding="utf-8") as fh:
        json.dump(build_manifest(ctx), fh, indent=2, default=str)

    return run_dir


def list_runs(config: Config) -> list[Path]:
    runs_root = config.resolve_path("outputs.runs")
    if not runs_root.exists():
        return []
    return sorted((p for p in runs_root.iterdir() if p.is_dir()), reverse=True)


def load_manifest(run_dir: Path) -> dict:
    with open(run_dir / "reproducibility_manifest.json", "r", encoding="utf-8") as fh:
        return json.load(fh)
