"""Run folder assembly + reproducibility manifest."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from gaga_jcvpca import jcvpca, reporting
from gaga_jcvpca.config import Config
from gaga_jcvpca.selection import default_selection, region_of_link


FEATURES = [
    f"{stem}_{ax}"
    for stem in ["Chest_to_Neck", "Neck_to_Head", "LShoulder_to_LUArm", "RShoulder_to_RUArm"]
    for ax in ("rx", "ry", "rz")
]


def _matrix(features, n=200, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame(rng.standard_normal((n, len(features))), columns=features)


@pytest.fixture()
def temp_config(config, tmp_path):
    # Redirect outputs to a temp dir so tests don't pollute the project.
    import copy

    data = copy.deepcopy(config.data)
    data["outputs"] = {
        "root": str(tmp_path / "outputs"),
        "runs": str(tmp_path / "outputs" / "runs"),
        "cache": str(tmp_path / "outputs" / "cache"),
    }
    return Config(data=data, project_root=config.project_root)


def _manifest_671(config):
    from gaga_jcvpca import project_io

    md = config.resolve_path("data.feature_manifests")
    return project_io.load_feature_manifest(md / "group4_core_14link_within_671_feature_manifest.csv")


def _build_ctx(temp_config):
    manifest = _manifest_671(temp_config)
    sel = default_selection("671_group4", "671", manifest, temp_config)
    a = _matrix(FEATURES, seed=1)
    b = _matrix(FEATURES, seed=2)
    r1 = _matrix(FEATURES, seed=3)
    r2 = _matrix(FEATURES, seed=4)
    region_fn = lambda stem: region_of_link(stem, temp_config)
    comparisons = [
        jcvpca.run_comparison(
            "671_T1_vs_T3", "longitudinal", "671_T1", "671_T3", a, b, FEATURES, 0.80, region_fn
        ),
        jcvpca.run_comparison(
            "671_R1_vs_R2", "natural_variability", "671_T1_R1", "671_T1_R2", r1, r2, FEATURES, 0.80, region_fn
        ),
    ]
    sweep = jcvpca.threshold_sweep(a, b, FEATURES, [0.70, 0.80, 0.90])
    return reporting.RunContext(
        run_id="run_test_001",
        participant="671",
        config=temp_config,
        selection=sel,
        filter_settings={"cutoff_hz": 10.0, "order": 4, "filter_type": "butterworth_lowpass"},
        comparisons=comparisons,
        threshold_sweep=sweep,
        marker_set_notes={"671": "T3 uses a different marker-set prefix; interpret with care."},
    )


def test_write_run_creates_self_contained_folder(temp_config):
    ctx = _build_ctx(temp_config)
    run_dir = reporting.write_run(ctx)
    assert run_dir.exists()
    expected = [
        "run_summary.md",
        "config_snapshot.yaml",
        "analysis_selection.yaml",
        "jcvpca_results.csv",
        "link_level_results.csv",
        "region_level_results.csv",
        "functional_space_results.csv",
        "null_space_results.csv",
        "natural_variability_results.csv",
        "selected_m_by_comparison.csv",
        "threshold_sensitivity.csv",
        "reproducibility_manifest.json",
    ]
    for name in expected:
        assert (run_dir / name).exists(), f"missing {name}"
    assert (run_dir / "figures").is_dir()
    assert (run_dir / "logs").is_dir()


def test_manifest_contents(temp_config):
    ctx = _build_ctx(temp_config)
    run_dir = reporting.write_run(ctx)
    manifest = json.loads((run_dir / "reproducibility_manifest.json").read_text())
    assert manifest["run_id"] == "run_test_001"
    assert manifest["participant"] == "671"
    assert manifest["participant_specific"] is True
    assert manifest["variance_threshold"] == 0.80
    assert manifest["science_hash"] == temp_config.science_hash
    assert len(manifest["comparisons"]) == 2
    assert "671" in manifest["marker_set_difference_notes"]
    assert manifest["filter_settings"]["cutoff_hz"] == 10.0


def test_run_summary_mentions_key_facts(temp_config):
    ctx = _build_ctx(temp_config)
    run_dir = reporting.write_run(ctx)
    summary = (run_dir / "run_summary.md").read_text()
    assert "run_test_001" in summary
    assert "671_T1_vs_T3" in summary
    assert "Natural variability" in summary
    assert "selected_m" in summary
    assert "marker-set" in summary.lower() or "marker" in summary.lower()


def test_selected_m_table(temp_config):
    ctx = _build_ctx(temp_config)
    run_dir = reporting.write_run(ctx)
    df = pd.read_csv(run_dir / "selected_m_by_comparison.csv")
    assert set(df["comparison_id"]) == {"671_T1_vs_T3", "671_R1_vs_R2"}
    assert (df["selected_m"] >= 1).all()


def test_list_runs_and_load_manifest(temp_config):
    ctx = _build_ctx(temp_config)
    reporting.write_run(ctx)
    runs = reporting.list_runs(temp_config)
    assert len(runs) == 1
    manifest = reporting.load_manifest(runs[0])
    assert manifest["run_id"] == "run_test_001"
