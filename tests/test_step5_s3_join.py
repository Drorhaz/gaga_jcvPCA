"""Guards for the Step-5 -> NV-profile join that feeds the S3 tier.

Regression target: Step 8 running before Step 5 (or pointed at the wrong results
tree) silently produced ``step5_organization=False`` for every link, making S3
unreachable for pipeline reasons rather than scientific ones.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pytest

from gaga_jcvpca import nv_profile

ROOT = Path(__file__).resolve().parents[1]


def _load_observed_nv():
    spec = importlib.util.spec_from_file_location(
        "observed_nv", ROOT / "scripts" / "observed_nv.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["observed_nv"] = module
    spec.loader.exec_module(module)
    return module


observed_nv = _load_observed_nv()


def _step5_csv(tmp_path: Path, rows: list[dict]) -> Path:
    root = tmp_path / "step05_amplitude_vs_organization"
    root.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(root / "rom_rms_by_link.csv", index=False)
    return root


def _row(link: str, classification: str, rom_ratio: float, comp: str = "671_T1_vs_T2") -> dict:
    return {
        "participant": "671",
        "comparison_id": comp,
        "link_id": link,
        "rom_ratio": rom_ratio,
        "classification": classification,
    }


# --- rom_is_flat -----------------------------------------------------------

@pytest.mark.parametrize(
    "ratio,expected",
    [(1.0, True), (0.7, True), (1.3, True), (0.69, False), (1.31, False), (float("nan"), False)],
)
def test_rom_is_flat_band(ratio, expected):
    assert nv_profile.rom_is_flat(ratio) is expected


def test_rom_flat_band_shared_with_step5_script():
    """Step 5 must classify off the same band the S3 gate uses."""
    spec = importlib.util.spec_from_file_location(
        "compute_amplitude_covariate", ROOT / "scripts" / "compute_amplitude_covariate.py"
    )
    step5 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(step5)
    assert step5.ROM_FLAT_LOW == nv_profile.ROM_FLAT_LOW
    assert step5.ROM_FLAT_HIGH == nv_profile.ROM_FLAT_HIGH


# --- load_step5_evidence ---------------------------------------------------

def test_missing_step5_raises_by_default(tmp_path):
    with pytest.raises(observed_nv.Step5JoinError, match="not found"):
        observed_nv.load_step5_evidence("671", tmp_path / "nope")


def test_missing_step5_allowed_when_opted_in(tmp_path):
    org, flat, info = observed_nv.load_step5_evidence(
        "671", tmp_path / "nope", require=False
    )
    assert org == {} and flat == {}
    assert info["available"] is False


def test_duplicate_keys_raise(tmp_path):
    root = _step5_csv(
        tmp_path,
        [_row("LFArm_to_LHand", "organization", 1.0), _row("LFArm_to_LHand", "amplitude", 2.0)],
    )
    with pytest.raises(observed_nv.Step5JoinError, match="Duplicate"):
        observed_nv.load_step5_evidence("671", root)


def test_organization_and_rom_flat_are_distinct(tmp_path):
    """A link inside the flat band but not exceeding Step-5's NV read is rom_flat, not organization."""
    root = _step5_csv(
        tmp_path,
        [
            _row("LFArm_to_LHand", "organization", 1.05),
            _row("LShin_to_LFoot", "within_variability", 0.95),
            _row("RUArm_to_RFArm", "amplitude", 1.80),
        ],
    )
    org, flat, info = observed_nv.load_step5_evidence("671", root)
    key = lambda link: ("671_T1_vs_T2", link)
    assert org[key("LFArm_to_LHand")] and flat[key("LFArm_to_LHand")]
    assert not org[key("LShin_to_LFoot")] and flat[key("LShin_to_LFoot")]
    assert not org[key("RUArm_to_RFArm")] and not flat[key("RUArm_to_RFArm")]
    assert info["n_source_rows"] == 3
    assert info["n_organization"] == 1


def test_other_participants_are_filtered_out(tmp_path):
    rows = [_row("LFArm_to_LHand", "organization", 1.0)]
    rows.append({**_row("LFArm_to_LHand", "organization", 1.0), "participant": "252"})
    root = _step5_csv(tmp_path, rows)
    org, _, info = observed_nv.load_step5_evidence("671", root)
    assert info["n_source_rows"] == 1
    assert set(org) == {("671_T1_vs_T2", "LFArm_to_LHand")}


# --- validate_step5_join ---------------------------------------------------

def _profile_row(link: str, org: bool, matched: bool = True) -> dict:
    return {"link_id": link, "step5_organization": org, "step5_matched": matched}


def test_validate_raises_when_org_column_is_all_false(tmp_path):
    info = {"source": "x.csv", "available": True, "n_source_rows": 5, "n_organization": 3}
    rows = [_profile_row("A", False), _profile_row("B", False)]
    with pytest.raises(observed_nv.Step5JoinError, match="step5_organization is False for all"):
        observed_nv.validate_step5_join("671", rows, info)


def test_validate_raises_when_nothing_joined(tmp_path):
    info = {"source": "x.csv", "available": True, "n_source_rows": 5, "n_organization": 0}
    rows = [_profile_row("A", False, matched=False)]
    with pytest.raises(observed_nv.Step5JoinError, match="none joined"):
        observed_nv.validate_step5_join("671", rows, info)


def test_validate_passes_and_reports_unmatched():
    info = {"source": "x.csv", "available": True, "n_source_rows": 3, "n_organization": 1}
    rows = [
        _profile_row("A", True),
        _profile_row("B", False),
        _profile_row("C", False, matched=False),
    ]
    report = observed_nv.validate_step5_join("671", rows, info)
    assert report == {"n_profile_rows": 3, "n_matched": 2, "n_unmatched": 1, "n_org_true": 1}


def test_validate_silent_when_step5_absent():
    """--allow-missing-step05 must not trip the all-False guard."""
    info = {"source": "x.csv", "available": False, "n_source_rows": 0, "n_organization": 0}
    report = observed_nv.validate_step5_join("671", [_profile_row("A", False, matched=False)], info)
    assert report["n_org_true"] == 0


# --- S3 elevation ----------------------------------------------------------

def test_s3_requires_every_gate():
    assert nv_profile.elevate_to_s3("S2", True, True, True) == "S3"
    for cov, rep, org in [(False, True, True), (True, False, True), (True, True, False)]:
        assert nv_profile.elevate_to_s3("S2", cov, rep, org) == "S2"
