"""Build consolidated per-comparison link exclusion audit from Step 4 run manifests.

Usage:
  PYTHONPATH=src .venv/bin/python scripts/build_comparison_link_exclusions.py \\
    --step04-root results_committee_case/marker_gap_policy_ex09_13/step04_primary_runs
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PARTICIPANTS = ("671", "252", "651", "790")
WINDOW = "ex09_13_contiguous"
MODES = ("pooled", "single")


def _rows_from_manifest(
    participant: str, mode: str, manifest_path: Path
) -> list[dict]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows: list[dict] = []
    for comp in data.get("comparisons", []):
        comp_id = comp["comparison_id"]
        kind = comp.get("kind", "")
        selected_m = comp.get("selected_m")
        n_included = len(comp.get("included_links") or [])
        marker_excl = comp.get("excluded_links_marker_gap") or {}
        other_excl = comp.get("excluded_links_other") or {}
        for link, reason in marker_excl.items():
            rows.append(
                {
                    "participant": participant,
                    "repetition_mode": mode,
                    "comparison_id": comp_id,
                    "comparison_kind": kind,
                    "selected_m": selected_m,
                    "n_included_links": n_included,
                    "link_id": link,
                    "exclusion_source": "marker_gap_policy",
                    "exclusion_reason": reason,
                }
            )
        for link, reason in other_excl.items():
            source = "shared_features_or_qc"
            if str(reason).startswith("marker_gap_policy"):
                source = "marker_gap_policy"
            rows.append(
                {
                    "participant": participant,
                    "repetition_mode": mode,
                    "comparison_id": comp_id,
                    "comparison_kind": kind,
                    "selected_m": selected_m,
                    "n_included_links": n_included,
                    "link_id": link,
                    "exclusion_source": source,
                    "exclusion_reason": reason,
                }
            )
        if not marker_excl and not other_excl:
            rows.append(
                {
                    "participant": participant,
                    "repetition_mode": mode,
                    "comparison_id": comp_id,
                    "comparison_kind": kind,
                    "selected_m": selected_m,
                    "n_included_links": n_included,
                    "link_id": "",
                    "exclusion_source": "none",
                    "exclusion_reason": "",
                }
            )
    return rows


def build_audit(step04_root: Path) -> pd.DataFrame:
    rows: list[dict] = []
    for pid in PARTICIPANTS:
        for mode in MODES:
            manifest = step04_root / pid / f"{WINDOW}_{mode}" / "reproducibility_manifest.json"
            if not manifest.exists():
                continue
            rows.extend(_rows_from_manifest(pid, mode, manifest))
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(
            ["participant", "repetition_mode", "comparison_id", "link_id"],
            na_position="last",
        ).reset_index(drop=True)
    return df


def write_summary_md(df: pd.DataFrame, path: Path) -> None:
    lines = [
        "# Comparison link exclusions — marker-gap policy run",
        "",
        "Consolidated from Step 4 `reproducibility_manifest.json` (pooled + single).",
        "Each row is one excluded link, or a placeholder when no links were excluded.",
        "",
        "## Exclusions by participant (pooled, marker-gap only)",
        "",
        "| participant | comparison | excluded links |",
        "|---|---|---|",
    ]
    sub = df[
        (df["repetition_mode"] == "pooled")
        & (df["exclusion_source"] == "marker_gap_policy")
        & (df["link_id"] != "")
    ]
    if sub.empty:
        lines.append("| — | — | none |")
    else:
        for (pid, comp_id), g in sub.groupby(["participant", "comparison_id"]):
            links = ", ".join(sorted(g["link_id"].unique()))
            lines.append(f"| {pid} | {comp_id} | {links} |")

    lines.extend(
        [
            "",
            "## Full table",
            "",
            "See `comparison_link_exclusions.csv`.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--step04-root",
        type=Path,
        required=True,
        help="Step 4 primary runs directory (contains participant subfolders)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: parent of step04-root)",
    )
    args = parser.parse_args()

    step04 = args.step04_root.resolve()
    out_dir = (args.out_dir or step04.parent).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    df = build_audit(step04)
    csv_path = out_dir / "comparison_link_exclusions.csv"
    md_path = out_dir / "comparison_link_exclusions.md"
    df.to_csv(csv_path, index=False)
    write_summary_md(df, md_path)
    n_excl = len(df[(df["link_id"] != "") & (df["exclusion_source"] != "none")])
    print(f"Wrote {csv_path.relative_to(ROOT)} ({len(df)} rows, {n_excl} exclusions)")
    print(f"Wrote {md_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
