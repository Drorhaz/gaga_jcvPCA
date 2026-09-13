"""Step 5 — ROM/RMS amplitude covariate joined to primary jcvPCA link tables.

Usage:
  PYTHONPATH=src .venv/bin/python scripts/compute_amplitude_covariate.py
  PYTHONPATH=src .venv/bin/python scripts/compute_amplitude_covariate.py --participant 671
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca.config import load_config
from gaga_jcvpca import pipeline
from gaga_jcvpca.nv_profile import ROM_FLAT_HIGH, ROM_FLAT_LOW
from gaga_jcvpca.selection import load_selection

PARTICIPANTS = ("671", "252", "651", "790")
WINDOW = "ex09_13_contiguous"
EXERCISE_IDS = [9, 10, 11, 12, 13]
NV_EXCEED_THRESHOLD = 1.0


def _pooled_matrix(config, participant: str, timepoint: str) -> pd.DataFrame | None:
    task = config.get("mode.task_part", "P1")
    segs_by = pipeline._segments_by_session(config)
    reps = ["R1", "R2"]
    frames = []
    for rep in reps:
        sid = pipeline._timepoint_session(participant, timepoint, rep, task)
        df = pipeline.load_matrix(config, sid)
        if df is None:
            continue
        sliced = pipeline.slice_matrix_to_exercises(
            df, segs_by.get(sid, []), EXERCISE_IDS
        )
        frames.append(sliced)
    if not frames:
        return None
    return pd.concat(frames, ignore_index=True)


def _link_axes(link_id: str, columns: list[str]) -> list[str]:
    axes = [f"{link_id}_rx", f"{link_id}_ry", f"{link_id}_rz"]
    return [c for c in axes if c in columns]


def _rotvec_magnitude_series(df: pd.DataFrame, axes: list[str]) -> np.ndarray:
    vals = df[axes].to_numpy(dtype=float)
    return np.sqrt(np.sum(vals ** 2, axis=1))


def _rom_rms(mag: np.ndarray) -> tuple[float, float]:
    if mag.size == 0:
        return float("nan"), float("nan")
    rom = float(np.nanmax(mag) - np.nanmin(mag))
    rms = float(np.sqrt(np.nanmean(mag ** 2)))
    return rom, rms


def _classify(
    exceeds_nv: bool,
    rom_ratio: float,
    jcvpca_mean: float,
) -> str:
    if not np.isfinite(rom_ratio):
        return "missing_amplitude"
    flat = ROM_FLAT_LOW <= rom_ratio <= ROM_FLAT_HIGH
    if not exceeds_nv:
        return "within_variability" if flat else "amplitude_only"
    if flat:
        return "organization"
    if rom_ratio > ROM_FLAT_HIGH and jcvpca_mean > 0:
        return "amplitude"
    if rom_ratio < ROM_FLAT_LOW and jcvpca_mean < 0:
        return "amplitude"
    return "mixed"


def _parse_nv_ratios(validation_csv: Path) -> dict[tuple[str, str], float]:
    df = pd.read_csv(validation_csv)
    nv = df[(df["method"] == "natural_variability") & (df["metric"] == "effect_ratio_vs_nv")]
    out: dict[tuple[str, str], float] = {}
    for _, row in nv.iterrows():
        scope = str(row["scope"])
        m = re.match(r"^(.+)@(.+)$", scope)
        if not m:
            continue
        out[(m.group(1), m.group(2))] = float(row["value"])
    return out


def process_participant(config, participant: str, run_dir: Path) -> pd.DataFrame:
    sel = load_selection(
        config.resolve_path("outputs.root") / "selections" / f"{participant}_{WINDOW}.yaml"
    )
    links = sel.included_links()
    nv_ratios = _parse_nv_ratios(run_dir / "validation_results.csv")
    link_lt = pd.read_csv(run_dir / "link_level_results.csv")
    long_lt = link_lt[link_lt["kind"] == "longitudinal"].copy()
    jcvpca_means = (
        long_lt.groupby(["comparison_id", "link_id"])["JcvPCA_link"]
        .mean()
        .reset_index(name="jcvpca_mean")
    )
    jrw_a = (
        long_lt.groupby(["comparison_id", "link_id"])["JRW_A_link"]
        .mean()
        .reset_index(name="jrw_a_mean")
    )
    jrw_b = (
        long_lt.groupby(["comparison_id", "link_id"])["JRW_B_link"]
        .mean()
        .reset_index(name="jrw_b_mean")
    )

    t1 = _pooled_matrix(config, participant, "T1")
    t2 = _pooled_matrix(config, participant, "T2")
    t3 = _pooled_matrix(config, participant, "T3")
    if t1 is None:
        raise FileNotFoundError(f"No pooled T1 matrix for {participant}")

    cols_t1 = list(t1.columns)
    amp_t1: dict[str, tuple[float, float]] = {}
    amp_t2: dict[str, tuple[float, float]] = {}
    amp_t3: dict[str, tuple[float, float]] = {}
    for link in links:
        axes_t1 = _link_axes(link, cols_t1)
        if len(axes_t1) < 3:
            continue
        amp_t1[link] = _rom_rms(_rotvec_magnitude_series(t1, axes_t1))
        if t2 is not None:
            axes_t2 = _link_axes(link, list(t2.columns))
            if len(axes_t2) == 3:
                amp_t2[link] = _rom_rms(_rotvec_magnitude_series(t2, axes_t2))
        if t3 is not None:
            axes_t3 = _link_axes(link, list(t3.columns))
            if len(axes_t3) == 3:
                amp_t3[link] = _rom_rms(_rotvec_magnitude_series(t3, axes_t3))

    rows: list[dict] = []
    for comp_id in sorted(jcvpca_means["comparison_id"].unique()):
        tp = "T2" if comp_id.endswith("T2") else "T3"
        b_amp = amp_t2 if tp == "T2" else amp_t3
        for link in links:
            if link not in amp_t1 or link not in b_amp:
                continue
            rom_t1, rms_t1 = amp_t1[link]
            rom_b, rms_b = b_amp.get(link, (float("nan"), float("nan")))
            rom_ratio = rom_b / rom_t1 if rom_t1 > 0 else float("nan")
            rms_ratio = rms_b / rms_t1 if rms_t1 > 0 else float("nan")
            jm = jcvpca_means[
                (jcvpca_means.comparison_id == comp_id)
                & (jcvpca_means.link_id == link)
            ]
            ja = jrw_a[
                (jrw_a.comparison_id == comp_id) & (jrw_a.link_id == link)
            ]
            jb = jrw_b[
                (jrw_b.comparison_id == comp_id) & (jrw_b.link_id == link)
            ]
            if jm.empty:
                continue
            jcvpca_mean = float(jm["jcvpca_mean"].iloc[0])
            effect_ratio = nv_ratios.get((link, comp_id), float("nan"))
            exceeds_nv = (
                np.isfinite(effect_ratio) and effect_ratio > NV_EXCEED_THRESHOLD
            )
            rows.append(
                {
                    "participant": participant,
                    "comparison_id": comp_id,
                    "followup_timepoint": tp,
                    "link_id": link,
                    "rom_t1": rom_t1,
                    "rms_t1": rms_t1,
                    f"rom_{tp.lower()}": rom_b,
                    f"rms_{tp.lower()}": rms_b,
                    "rom_ratio": rom_ratio,
                    "rms_ratio": rms_ratio,
                    "jcvpca_mean": jcvpca_mean,
                    "jcvpca_abs_mean": abs(jcvpca_mean),
                    "jrw_a_mean": float(ja["jrw_a_mean"].iloc[0]) if not ja.empty else float("nan"),
                    "jrw_b_mean": float(jb["jrw_b_mean"].iloc[0]) if not jb.empty else float("nan"),
                    "effect_ratio_vs_nv": effect_ratio,
                    "exceeds_nv": exceeds_nv,
                    "classification": _classify(exceeds_nv, rom_ratio, jcvpca_mean),
                }
            )
    return pd.DataFrame(rows)


def _write_summary(df: pd.DataFrame, out_md: Path) -> None:
    lines = [
        "# Amplitude vs organization — Step 5 classification summary",
        "",
        f"ROM flat band: **{ROM_FLAT_LOW}–{ROM_FLAT_HIGH}** (follow-up / T1 pooled).",
        f"Exceeds observed NV: `effect_ratio_vs_nv` > **{NV_EXCEED_THRESHOLD}** (descriptive).",
        "",
        "## Classification rules",
        "",
        "| Label | Rule |",
        "|---|---|",
        "| `organization` | exceeds NV **and** ROM ratio in flat band |",
        "| `amplitude` | exceeds NV **and** ROM ratio outside band **with** consistent JcvPCA sign |",
        "| `mixed` | exceeds NV **and** ROM shifts without consistent sign |",
        "| `within_variability` | does not exceed NV **and** flat ROM |",
        "| `amplitude_only` | does not exceed NV **but** ROM ratio outside flat band |",
        "",
        "## Counts per participant × comparison",
        "",
    ]
    if df.empty:
        lines.append("_No rows._")
    else:
        counts = (
            df.groupby(["participant", "comparison_id", "classification"])
            .size()
            .reset_index(name="n_links")
        )
        pivot = counts.pivot_table(
            index=["participant", "comparison_id"],
            columns="classification",
            values="n_links",
            fill_value=0,
            aggfunc="sum",
        )
        pivot = pivot.reset_index()
        headers = list(pivot.columns)
        lines.append("| " + " | ".join(str(h) for h in headers) + " |")
        lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for _, row in pivot.iterrows():
            lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
        lines.extend(["", "## Participant headlines", ""])
        for (pid, comp), sub in df.groupby(["participant", "comparison_id"]):
            n_org = int((sub["classification"] == "organization").sum())
            n_amp = int((sub["classification"] == "amplitude").sum())
            n_mix = int((sub["classification"] == "mixed").sum())
            n_ex = int(sub["exceeds_nv"].sum())
            n_flat = int(
                ((sub["rom_ratio"] >= ROM_FLAT_LOW) & (sub["rom_ratio"] <= ROM_FLAT_HIGH)).sum()
            )
            lines.append(
                f"- **{pid} {comp}:** {n_ex} links exceed NV; "
                f"{n_org} organization / {n_amp} amplitude / {n_mix} mixed; "
                f"{n_flat} links with flat ROM ratio."
            )
        lines.extend(
            [
                "",
                "## Interpretation guide (committee)",
                "",
                "- Many **organization** labels → redistribution language better supported.",
                "- Dominant **amplitude** or **mixed** → soften to combined amplitude + organization change.",
                "- Mostly **within_variability** → descriptive only; no organization headline.",
                "",
                "See `rom_rms_by_link.csv` for link-level detail.",
            ]
        )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Step 5 ROM/RMS amplitude covariate")
    parser.add_argument("--participant", choices=PARTICIPANTS)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "results_committee_case" / "step05_amplitude_vs_organization",
    )
    parser.add_argument(
        "--primary-root",
        type=Path,
        default=ROOT / "results_committee_case" / "step04_primary_runs",
        help="Step 4 pooled run root",
    )
    args = parser.parse_args()
    config = load_config(ROOT / "configs" / "default.yaml")
    pids = [args.participant] if args.participant else list(PARTICIPANTS)
    primary_root = args.primary_root.resolve()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for pid in pids:
        run_dir = primary_root / pid / f"{WINDOW}_pooled"
        if not run_dir.is_dir():
            raise FileNotFoundError(run_dir)
        print(f"  {pid}...")
        frames.append(process_participant(config, pid, run_dir))

    df = pd.concat(frames, ignore_index=True)
    csv_path = args.out_dir / "rom_rms_by_link.csv"
    df.to_csv(csv_path, index=False)
    _write_summary(df, args.out_dir / "classification_summary.md")
    print(f"Wrote {csv_path} ({len(df)} rows)")
    print(f"Wrote {args.out_dir / 'classification_summary.md'}")


if __name__ == "__main__":
    main()
