"""Step 4 — primary ex09_13_contiguous pooled runs for all four participants.

Usage:
  PYTHONPATH=src .venv/bin/python scripts/run_step04_primary.py
  PYTHONPATH=src .venv/bin/python scripts/run_step04_primary.py --participant 671
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca.config import load_config
from gaga_jcvpca import pipeline, reporting
from gaga_jcvpca.selection import load_selection

PARTICIPANTS = ("671", "252", "651", "790")
WINDOW_LABEL = "ex09_13_contiguous"
MODE = "pooled"


def _git_hash() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _copy_run(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def run_one(config, participant: str, out_root: Path) -> dict:
    sel_name = f"{participant}_{WINDOW_LABEL}"
    sel_path = config.resolve_path("outputs.root") / "selections" / f"{sel_name}.yaml"
    if not sel_path.exists():
        raise FileNotFoundError(f"Missing selection: {sel_path}")
    selection = load_selection(sel_path)
    run_id = f"{participant}_{WINDOW_LABEL}_{MODE}"

    print(f"\n=== {participant}: {sel_name} ({MODE}) ===")
    run_dir = pipeline.run_analysis(
        config,
        selection,
        timepoints=["T1", "T2", "T3"],
        repetitions=["R1", "R2"],
        reference_timepoint="T1",
        repetition_mode=MODE,
        run_validation=True,
        run_id=run_id,
    )
    print(f"  run: {run_dir}")

    dst = out_root / participant / f"{WINDOW_LABEL}_{MODE}"
    _copy_run(run_dir, dst)

    # selection provenance
    step3_sel = ROOT / "results_committee_case" / "step03_trunk_extension" / "selections" / f"{sel_name}.yaml"
    if step3_sel.exists():
        shutil.copy2(step3_sel, dst / "selection_source.yaml")

    m_path = dst / "selected_m_by_comparison.csv"
    m_df = pd.read_csv(m_path) if m_path.exists() else pd.DataFrame()
    n_links = len(selection.included_links())
    return {
        "participant": participant,
        "run_id": run_id,
        "run_dir": str(dst.relative_to(ROOT)),
        "n_included_links": n_links,
        "selected_m": dict(zip(m_df.get("comparison_id", []), m_df.get("selected_m", []))),
        "comparisons": m_df["comparison_id"].tolist() if "comparison_id" in m_df.columns else [],
    }


def write_index(path: Path, rows: list[dict], git_hash: str) -> None:
    lines = [
        "# Primary run index — Step 4",
        "",
        f"**Generated:** {datetime.now().isoformat(timespec='seconds')}",
        f"**Git hash:** `{git_hash}`",
        f"**Window:** `{WINDOW_LABEL}` · **Mode:** `{MODE}`",
        f"**Parameters:** variance_threshold=0.80, sensitivity_p=2, validate=true",
        "",
        "## Runs",
        "",
        "| Participant | Links | Run folder | T1→T2 m | T1→T3 m | NV m |",
        "|---|---:|---|---:|---:|---:|",
    ]
    for r in rows:
        sm = r["selected_m"]
        pid = r["participant"]
        m_t2 = sm.get(f"{pid}_T1_vs_T2", "—")
        m_t3 = sm.get(f"{pid}_T1_vs_T3", "—")
        m_nv = sm.get(f"{pid}_T1_R1_vs_R2", "—")
        lines.append(
            f"| {pid} | {r['n_included_links']} | `{r['run_dir']}` | "
            f"{m_t2} | {m_t3} | {m_nv} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Authoritative committee primary runs (trunk-inclusive manifests from Step 3).",
            "- Step 1 baseline audit retains pre-trunk exploration snapshots for delta comparison.",
            "- 651/671: shared-link restriction may apply where T2/T3 matrices lack full link columns.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--participant", action="append", default=[])
    parser.add_argument(
        "--output-root",
        type=Path,
        default=ROOT / "results_committee_case" / "step04_primary_runs",
        help="Committee-case folder for copied primary run artifacts",
    )
    args = parser.parse_args()

    config = load_config()
    out_root = args.output_root.resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    pids = args.participant or list(PARTICIPANTS)
    rows: list[dict] = []
    for pid in pids:
        rows.append(run_one(config, pid, out_root))

    write_index(out_root / "PRIMARY_RUN_INDEX.md", rows, _git_hash())
    print(f"\nWrote {out_root.relative_to(ROOT)}/PRIMARY_RUN_INDEX.md ({len(rows)} runs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
