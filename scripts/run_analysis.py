"""CLI: run a participant-specific JcvPCA analysis from a saved selection.

Usage:
    python scripts/run_analysis.py --selection <name> [--timepoints T1 T2 T3]
        [--sweep] [--validate]

Reads matrices from data.matrices, writes a self-contained run folder.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca import pipeline, selection as sel_mod  # noqa: E402
from gaga_jcvpca.config import load_config  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a JcvPCA analysis.")
    parser.add_argument("--selection", required=True, help="selection name (without .yaml)")
    parser.add_argument("--timepoints", nargs="+", default=["T1", "T2", "T3"])
    parser.add_argument("--reference", default="T1")
    parser.add_argument("--sweep", action="store_true")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()

    cfg = load_config()
    sel_dir = cfg.resolve_path("outputs.root") / "selections"
    sel_path = sel_dir / f"{args.selection}.yaml"
    if not sel_path.exists():
        raise SystemExit(f"Selection not found: {sel_path}")
    selection = sel_mod.load_selection(sel_path)

    run_dir = pipeline.run_analysis(
        cfg,
        selection,
        timepoints=args.timepoints,
        reference_timepoint=args.reference,
        run_threshold_sweep=args.sweep,
        run_validation=args.validate,
    )
    print(f"Run written: {run_dir}")


if __name__ == "__main__":
    main()
