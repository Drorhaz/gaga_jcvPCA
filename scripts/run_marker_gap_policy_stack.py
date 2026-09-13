"""Run full marker-gap-policy analysis stack into one dedicated results tree.

Usage:
  PYTHONPATH=src .venv/bin/python scripts/run_marker_gap_policy_stack.py
  PYTHONPATH=src .venv/bin/python scripts/run_marker_gap_policy_stack.py --skip-step4 --skip-step8
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
ENV = {"PYTHONPATH": str(ROOT / "src")}


def _run(label: str, script: str, *args: str) -> None:
    cmd = [str(PY), str(ROOT / "scripts" / script), *args]
    print(f"\n{'=' * 60}\n{label}\n{'=' * 60}")
    subprocess.run(cmd, cwd=ROOT, env={**subprocess.os.environ, **ENV}, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-root",
        type=Path,
        default=ROOT / "results_committee_case" / "marker_gap_policy_ex09_13",
    )
    parser.add_argument("--skip-step4", action="store_true")
    parser.add_argument("--skip-step8", action="store_true")
    parser.add_argument("--skip-downstream", action="store_true")
    args = parser.parse_args()

    results_root = args.results_root.resolve()
    step04 = results_root / "step04_primary_runs"
    step05 = results_root / "step05_amplitude_vs_organization"
    step06 = results_root / "step06_underused_at_t1"
    step07 = results_root / "step07_contribution_distribution"
    step08 = results_root / "step08_nv_and_stability"
    step09 = results_root / "step09_persistence_t2_t3"
    figures = ROOT / "docs" / f"supervisor_meeting_figures_{results_root.name}"

    results_root.mkdir(parents=True, exist_ok=True)

    if not args.skip_step4:
        _run("Step 4 — primary pooled", "run_step04_primary.py", "--output-root", str(step04))
        _run("Step 4b — single + robustness", "run_step04b_robustness.py", "--output-root", str(step04))

    # Step 5 must precede Step 8: observed_nv.py reads Step 5's organization
    # classification to elevate S2 links to S3. Running Step 8 first leaves
    # step5_organization False for every link and makes S3 unreachable.
    _run(
        "Step 5 — amplitude covariate",
        "compute_amplitude_covariate.py",
        "--out-dir",
        str(step05),
        "--primary-root",
        str(step04),
    )

    if not args.skip_step8:
        _run(
            "Step 8 — observed NV",
            "observed_nv.py",
            "--output-dir",
            str(step08),
            "--primary-root",
            str(step04),
            "--step05-root",
            str(step05),
        )

    _run(
        "Exclusion audit",
        "build_comparison_link_exclusions.py",
        "--step04-root",
        str(step04),
        "--out-dir",
        str(results_root),
    )

    if args.skip_downstream:
        print("\nSkipped Steps 6–7, 9, curated tables, figures (--skip-downstream).")
        return 0

    _run(
        "Step 6 — underused at T1",
        "step06_underused_at_t1.py",
        "--step04-root",
        str(step04),
        "--step08-root",
        str(step08),
        "--out-dir",
        str(step06),
    )
    _run(
        "Step 7 — contribution distribution",
        "step07_contribution_distribution.py",
        "--step04-root",
        str(step04),
        "--out-dir",
        str(step07),
    )
    _run(
        "Step 9 — persistence T2/T3",
        "step09_persistence_t2_t3.py",
        "--step08-root",
        str(step08),
        "--out-dir",
        str(step09),
    )
    _run(
        "Curated tables (05/06/09)",
        "build_tables_to_show.py",
        "--results-root",
        str(results_root),
    )
    _run(
        "Supervisor figures",
        "supervisor_meeting_figures.py",
        "--results-root",
        str(results_root),
        "--out-dir",
        str(figures),
    )
    _run(
        "Diff vs pre-policy",
        "diff_marker_gap_policy_results.py",
        "--new-root",
        str(results_root),
    )

    print(f"\nDone. Results tree: {results_root.relative_to(ROOT)}")
    print(f"Figures: {figures.relative_to(ROOT)}")
    print(f"Diff: {(results_root / 'DIFF_vs_pre_policy.md').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
