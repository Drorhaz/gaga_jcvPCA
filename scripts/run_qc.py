"""Run raw-marker QC offline and write outputs/cache/qc/qc_summary.csv."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca.config import load_config  # noqa: E402
from gaga_jcvpca.inventory import build_inventory  # noqa: E402
from gaga_jcvpca.qc_markers import run_marker_qc  # noqa: E402


def main() -> None:
    cfg = load_config()
    inv = build_inventory(cfg)
    n_marker = sum(1 for r in inv.rows if r.has_marker_csv)
    if n_marker == 0:
        print(
            "No marker CSV files found. Set data.raw_markers or data.raw_skeleton in "
            "configs/paths.yaml (expected: data/raw_markers/{participant}/)."
        )
        return

    findings, df = run_marker_qc(cfg, inv, write_cache=True)
    out_path = cfg.resolve_path("outputs.cache") / "qc" / "qc_summary.csv"
    print(f"wrote {out_path} ({len(findings)} findings, {len(df)} rows)")


if __name__ == "__main__":
    main()
