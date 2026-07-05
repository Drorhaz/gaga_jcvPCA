"""Config loading + science hash."""

from __future__ import annotations


def test_config_merges_includes(config):
    # value from analysis_defaults.yaml
    assert config.get("pca.variance_threshold") == 0.80
    # value from qc_thresholds.yaml
    assert config.get("capture.frame_rate_hz") == 120.0
    # value from exercise_map.yaml
    assert config.get("primary_group") == "Group4"


def test_science_hash_is_stable_and_changes_with_science(config):
    h1 = config.science_hash
    assert isinstance(h1, str) and len(h1) == 16
    # mutating a science key changes the hash
    import copy

    from gaga_jcvpca.config import Config

    data2 = copy.deepcopy(config.data)
    data2["pca"]["variance_threshold"] = 0.90
    h2 = Config(data=data2, project_root=config.project_root).science_hash
    assert h1 != h2


def test_science_hash_ignores_non_science_keys(config):
    import copy

    from gaga_jcvpca.config import Config

    data2 = copy.deepcopy(config.data)
    data2["outputs"] = {"root": "somewhere_else"}
    h2 = Config(data=data2, project_root=config.project_root).science_hash
    assert h2 == config.science_hash


def test_resolve_path_is_absolute(config):
    p = config.resolve_path("data.segmentation")
    assert p.is_absolute()
    assert p.name == "segmentation"
