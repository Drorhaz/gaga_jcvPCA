"""Generate synthetic rotation-vector feature matrices for smoke testing.

Writes one parquet per session ({pid}_T{t}_P1_R{r}.parquet) with the 671 Group-4
feature columns, so the full analysis pipeline can run end-to-end without the
large raw skeleton CSVs. Numbers are synthetic and only exercise the plumbing.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca import project_io  # noqa: E402
from gaga_jcvpca.config import load_config  # noqa: E402
from gaga_jcvpca.selection import link_stem  # noqa: E402


def main() -> None:
    cfg = load_config()
    manifest_dir = cfg.resolve_path("data.feature_manifests")
    manifest = project_io.load_feature_manifest(
        manifest_dir / "group4_core_14link_within_671_feature_manifest.csv"
    )
    features = project_io.feature_names_from_manifest(manifest)
    stems = sorted({link_stem(f) for f in features})
    columns = [f"{s}_{ax}" for s in stems for ax in ("rx", "ry", "rz")]

    out_dir = cfg.resolve_path("data.matrices")
    out_dir.mkdir(parents=True, exist_ok=True)

    participant = "671"
    n_frames = 900
    rng = np.random.default_rng(2026)
    for tp in ("T1", "T2", "T3"):
        for rep in ("R1", "R2"):
            # small per-timepoint drift so comparisons are non-trivial
            drift = {"T1": 0.0, "T2": 0.15, "T3": 0.3}[tp]
            base = rng.standard_normal((n_frames, len(columns)))
            base[:, : len(columns) // 2] += drift
            df = pd.DataFrame(base, columns=columns)
            session_id = f"{participant}_{tp}_P1_{rep}"
            df.to_parquet(out_dir / f"{session_id}.parquet")
            print(f"wrote {session_id}.parquet ({df.shape})")


if __name__ == "__main__":
    main()
