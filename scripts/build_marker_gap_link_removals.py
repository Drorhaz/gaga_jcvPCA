"""Build session-scoped link removal table from marker gap QC (ex09-13).

Policy (advisory; not yet applied in run_analysis by default):
  REMOVE link for participant × session × rep if either:
    - any manifest-mapped supporting marker has >=10% of ex09-13 window in
      large gaps (>0.5 s), or
    - >=2 supporting markers each have >=5% in large gaps.

  WATCH (document only): max gap 5–10% on supporting markers.

Output:
  results_committee_case/step03_trunk_extension/marker_gap_link_removals_ex09_13.csv

Usage:
  PYTHONPATH=src .venv/bin/python scripts/build_marker_gap_link_removals.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

GAP_DIR = ROOT / "results_committee_case" / "step03_trunk_extension" / "marker_gap_tables_ex09_13"
OUT_CSV = ROOT / "results_committee_case" / "step03_trunk_extension" / "marker_gap_link_removals_ex09_13.csv"
OUT_README = OUT_CSV.with_suffix(".md")

GAP_REMOVE_PCT = 10.0
GAP_MULTI_PCT = 5.0
GAP_MULTI_MIN_MARKERS = 2
GAP_WATCH_PCT = 5.0


def session_label(session_id: str) -> tuple[str, str, str]:
    parts = session_id.split("_")
    if len(parts) >= 4:
        return parts[1], parts[3], f"{parts[1]}_{parts[3]}"
    return session_id, "", session_id


def classify_link_session(group: pd.DataFrame) -> dict:
    max_gap = float(group["pct_frames_in_large_gaps_of_window"].max())
    n_markers = int(group["marker_name"].nunique())
    n_gap10 = int((group["pct_frames_in_large_gaps_of_window"] >= GAP_REMOVE_PCT).sum())
    n_gap5 = int((group["pct_frames_in_large_gaps_of_window"] >= GAP_MULTI_PCT).sum())
    worst = group.loc[group["pct_frames_in_large_gaps_of_window"].idxmax()]

    if max_gap >= GAP_REMOVE_PCT:
        tier = "remove_from_comparison"
        rule = f"max_gap>={GAP_REMOVE_PCT:.0f}%"
        reason = (
            f"Supporting marker `{worst['marker_name']}` has {max_gap:.1f}% of ex09-13 "
            f"window in large gaps (>0.5 s, {int(worst['n_gaps_gt_0p5s'])} runs); "
            f"Motive likely interpolated bone motion."
        )
    elif n_gap5 >= GAP_MULTI_MIN_MARKERS:
        tier = "remove_from_comparison"
        rule = f">={GAP_MULTI_MIN_MARKERS}_markers>={GAP_MULTI_PCT:.0f}%"
        reason = (
            f"{n_gap5}/{n_markers} supporting markers each have >={GAP_MULTI_PCT:.0f}% "
            f"of ex09-13 in large gaps (max {max_gap:.1f}% on `{worst['marker_name']}`)."
        )
    elif max_gap >= GAP_WATCH_PCT:
        tier = "watch"
        rule = f"max_gap>={GAP_WATCH_PCT:.0f}%"
        reason = (
            f"Supporting marker `{worst['marker_name']}` has {max_gap:.1f}% of ex09-13 "
            f"in large gaps; keep but document if this rep is in a comparison."
        )
    else:
        tier = "ok"
        rule = ""
        reason = ""

    return {
        "max_gap_pct": round(max_gap, 3),
        "n_supporting_markers": n_markers,
        "n_markers_gap_ge_10pct": n_gap10,
        "n_markers_gap_ge_5pct": n_gap5,
        "worst_marker": worst["marker_name"],
        "worst_n_large_gaps": int(worst["n_gaps_gt_0p5s"]),
        "removal_tier": tier,
        "policy_rule": rule,
        "reason": reason,
    }


def build_table() -> pd.DataFrame:
    rows: list[dict] = []
    for csv in sorted(GAP_DIR.glob("*_ex09_13_marker_gaps.csv")):
        df = pd.read_csv(csv)
        mapped = df[~df["related_links"].str.startswith(("no link match", "unlabeled", "bone="))].copy()
        long_rows: list[dict] = []
        for _, r in mapped.iterrows():
            for stem in str(r["related_links"]).split("; "):
                stem = stem.strip()
                if not stem:
                    continue
                long_rows.append(
                    {
                        "participant": r["participant"],
                        "session_id": r["session_id"],
                        "link_stem": stem,
                        "marker_name": r["marker_name"],
                        "pct_frames_in_large_gaps_of_window": r["pct_frames_in_large_gaps_of_window"],
                        "n_gaps_gt_0p5s": r["n_gaps_gt_0p5s"],
                    }
                )
        if not long_rows:
            continue
        ml = pd.DataFrame(long_rows)
        for (pid, sid, link), grp in ml.groupby(["participant", "session_id", "link_stem"]):
            tp, rep, t_r = session_label(sid)
            meta = classify_link_session(grp)
            if meta["removal_tier"] == "ok":
                continue
            rows.append(
                {
                    "participant": pid,
                    "session_id": sid,
                    "timepoint": tp,
                    "repetition": rep,
                    "T_R": t_r,
                    "link_stem": link,
                    **meta,
                }
            )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(
        ["participant", "T_R", "link_stem", "removal_tier"],
        ascending=[True, True, True, False],
    ).reset_index(drop=True)


def write_readme(path: Path, df: pd.DataFrame) -> None:
    n_remove = int((df["removal_tier"] == "remove_from_comparison").sum()) if len(df) else 0
    n_watch = int((df["removal_tier"] == "watch").sum()) if len(df) else 0
    lines = [
        "# Marker-gap link removals (ex09-13)",
        "",
        "Advisory table: links to **withhold from comparisons** that use the listed session/rep.",
        "Does not remove links globally from the participant selection YAML.",
        "",
        "## Policy",
        "",
        f"- **remove_from_comparison:** max supporting-marker gap >= {GAP_REMOVE_PCT:.0f}% "
        f"OR >= {GAP_MULTI_MIN_MARKERS} markers each >= {GAP_MULTI_PCT:.0f}% (large gap = contiguous missing > 0.5 s)",
        f"- **watch:** max gap {GAP_WATCH_PCT:.0f}–{GAP_REMOVE_PCT:.0f}% — document only",
        "",
        f"**Rows:** {len(df)} total ({n_remove} remove, {n_watch} watch)",
        "",
        "## Regenerate",
        "",
        "```bash",
        "PYTHONPATH=src .venv/bin/python scripts/build_marker_gap_link_removals.py",
        "```",
        "",
        "## Wire to pipeline",
        "",
        "See `docs/MARKER_GAP_REMOVAL_WIRING.md`.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    df = build_table()
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    write_readme(OUT_README, df)
    n_remove = int((df["removal_tier"] == "remove_from_comparison").sum()) if len(df) else 0
    n_watch = int((df["removal_tier"] == "watch").sum()) if len(df) else 0
    print(f"wrote {OUT_CSV} ({len(df)} rows: {n_remove} remove, {n_watch} watch)")
    print(f"wrote {OUT_README}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
