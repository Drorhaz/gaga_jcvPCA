"""End-to-end smoke: selection -> matrices -> comparisons -> validation -> run folder."""

from __future__ import annotations

import copy
import json

import numpy as np
import pandas as pd

from gaga_jcvpca import pipeline, project_io, reporting
from gaga_jcvpca.config import Config
from gaga_jcvpca.selection import default_selection, link_stem


def _synth_matrices(config, participant="671"):
    md = config.resolve_path("data.feature_manifests")
    manifest = project_io.load_feature_manifest(
        md / "group4_core_14link_within_671_feature_manifest.csv"
    )
    features = project_io.feature_names_from_manifest(manifest)
    stems = sorted({link_stem(f) for f in features})
    columns = [f"{s}_{ax}" for s in stems for ax in ("rx", "ry", "rz")]
    rng = np.random.default_rng(7)
    matrices = {}
    for tp in ("T1", "T2", "T3"):
        for rep in ("R1", "R2"):
            drift = {"T1": 0.0, "T2": 0.15, "T3": 0.3}[tp]
            arr = rng.standard_normal((600, len(columns)))
            arr[:, : len(columns) // 2] += drift
            matrices[f"{participant}_{tp}_P1_{rep}"] = pd.DataFrame(arr, columns=columns)
    return manifest, matrices


def _temp_config(config, tmp_path):
    data = copy.deepcopy(config.data)
    data["outputs"] = {
        "root": str(tmp_path / "outputs"),
        "runs": str(tmp_path / "outputs" / "runs"),
        "cache": str(tmp_path / "outputs" / "cache"),
    }
    return Config(data=data, project_root=config.project_root)


def test_full_pipeline_run(config, tmp_path):
    cfg = _temp_config(config, tmp_path)
    manifest, matrices = _synth_matrices(cfg)
    selection = default_selection("671_group4", "671", manifest, cfg)

    run_dir = pipeline.run_analysis(
        cfg,
        selection,
        timepoints=["T1", "T2", "T3"],
        repetitions=["R1", "R2"],
        reference_timepoint="T1",
        run_threshold_sweep=True,
        run_validation=True,
        run_id="smoke_run",
        matrices=matrices,
    )
    assert run_dir.exists()

    # required outputs present
    for name in [
        "run_summary.md",
        "reproducibility_manifest.json",
        "link_level_results.csv",
        "region_level_results.csv",
        "natural_variability_results.csv",
        "selected_m_by_comparison.csv",
        "threshold_sensitivity.csv",
        "validation_results.csv",
        "validation_summary.md",
    ]:
        assert (run_dir / name).exists(), f"missing {name}"

    manifest_json = json.loads((run_dir / "reproducibility_manifest.json").read_text())
    kinds = {c["kind"] for c in manifest_json["comparisons"]}
    assert "longitudinal" in kinds
    assert "natural_variability" in kinds
    ids = {c["comparison_id"] for c in manifest_json["comparisons"]}
    assert "671_T1_vs_T2" in ids
    assert "671_T1_vs_T3" in ids
    assert "671_T1_R1_vs_R2" in ids

    # validation ran and is strength-labeled
    val = pd.read_csv(run_dir / "validation_results.csv")
    assert not val.empty
    assert "strength" in val.columns

    # run discoverable
    runs = reporting.list_runs(cfg)
    assert run_dir in runs
