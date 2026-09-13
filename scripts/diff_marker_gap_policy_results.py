"""Diff marker-gap-policy run vs pre-policy committee results.

Usage:
  PYTHONPATH=src .venv/bin/python scripts/diff_marker_gap_policy_results.py \\
    --new-root results_committee_case/marker_gap_policy_ex09_13 \\
    --old-step04 results_committee_case/step04_primary_runs \\
    --old-step08 results_committee_case/step08_nv_and_stability
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PARTICIPANTS = ("671", "252", "651", "790")
WINDOW = "ex09_13_contiguous"


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def _top5_links(link_csv: Path, comp_id: str) -> list[str]:
    lt = _read_csv(link_csv)
    if lt.empty:
        return []
    g = lt[lt["comparison_id"] == comp_id]
    if g.empty:
        return []
    means = g.groupby("link_id")["JcvPCA_link"].mean().abs().sort_values(ascending=False)
    return list(means.index[:5])


def _a2_counts(prof: pd.DataFrame) -> pd.DataFrame:
    if prof.empty:
        return pd.DataFrame()
    rows = []
    for pid in PARTICIPANTS:
        for tp in ("T2", "T3"):
            g = prof[
                (prof["participant"].astype(str) == pid)
                & (prof["comparison_id"] == f"{pid}_T1_vs_{tp}")
            ]
            if g.empty:
                continue
            rows.append(
                {
                    "participant": pid,
                    "comparison": f"T1_vs_{tp}",
                    "n_links": len(g),
                    "a2_pass": int(g["a2_pass"].sum()),
                    "s2": int((g["nv_profile_tier"] == "S2").sum()),
                    "s3": int((g["nv_profile_tier"] == "S3").sum()),
                }
            )
    return pd.DataFrame(rows)


def _selected_m_table(step04: Path) -> pd.DataFrame:
    rows = []
    for pid in PARTICIPANTS:
        path = step04 / pid / f"{WINDOW}_pooled" / "selected_m_by_comparison.csv"
        sm = _read_csv(path)
        if sm.empty:
            continue
        for _, r in sm.iterrows():
            rows.append(
                {
                    "participant": pid,
                    "comparison_id": r["comparison_id"],
                    "selected_m": int(r["selected_m"]),
                    "n_included_links": int(r["n_included_links"]),
                    "n_excluded_links": int(r["n_excluded_links"]),
                }
            )
    return pd.DataFrame(rows)


def _robustness_labels(step04: Path) -> pd.DataFrame:
    path = step04 / "robustness.csv"
    rb = _read_csv(path)
    if rb.empty:
        return pd.DataFrame()
    sub = rb[rb["robustness_label"] != ""][["participant", "comparison_id", "robustness_label"]]
    return sub.drop_duplicates()


def build_diff(
    new_root: Path,
    old_step04: Path,
    old_step08: Path,
) -> str:
    new_step04 = new_root / "step04_primary_runs"
    new_step08 = new_root / "step08_nv_and_stability"

    lines = [
        "# Diff — marker-gap policy run vs pre-policy baseline",
        "",
        f"**New run root:** `{new_root.relative_to(ROOT)}`",
        f"**Old Step 4:** `{old_step04.relative_to(ROOT)}`",
        f"**Old Step 8:** `{old_step08.relative_to(ROOT)}`",
        "",
        "Policy change: session-scoped marker-gap link exclusions wired into `run_analysis`.",
        "",
    ]

    # Exclusions (new only)
    excl = _read_csv(new_root / "comparison_link_exclusions.csv")
    marker_excl = excl[
        (excl["repetition_mode"] == "pooled")
        & (excl["exclusion_source"] == "marker_gap_policy")
        & (excl["link_id"].astype(str) != "")
    ]
    lines.extend(
        [
            "## 1. New marker-gap exclusions (pooled comparisons)",
            "",
        ]
    )
    if marker_excl.empty:
        lines.append("No marker-gap exclusions in pooled runs.")
    else:
        lines.append("| participant | comparison | link | reason (truncated) |")
        lines.append("|---|---|---|---|")
        for _, r in marker_excl.iterrows():
            reason = str(r["exclusion_reason"])[:80].replace("|", "/")
            lines.append(f"| {r['participant']} | {r['comparison_id']} | {r['link_id']} | {reason} |")
    lines.append("")

    # selected_m + link counts
    old_sm = _selected_m_table(old_step04).rename(
        columns={
            "selected_m": "old_m",
            "n_included_links": "old_n_links",
            "n_excluded_links": "old_n_excl",
        }
    )
    new_sm = _selected_m_table(new_step04).rename(
        columns={
            "selected_m": "new_m",
            "n_included_links": "new_n_links",
            "n_excluded_links": "new_n_excl",
        }
    )
    merged = old_sm.merge(new_sm, on=["participant", "comparison_id"], how="outer")
    lines.extend(
        [
            "## 2. Selected m and link counts (pooled Step 4)",
            "",
            "| participant | comparison | old m | new m | old links | new links | old excl | new excl |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, r in merged.iterrows():
        lines.append(
            f"| {r['participant']} | {r['comparison_id']} | "
            f"{r.get('old_m', '—')} | {r.get('new_m', '—')} | "
            f"{r.get('old_n_links', '—')} | {r.get('new_n_links', '—')} | "
            f"{r.get('old_n_excl', '—')} | {r.get('new_n_excl', '—')} |"
        )
    lines.append("")

    # A2 / tiers
    old_prof = _read_csv(old_step08 / "NV_PROFILE.csv")
    new_prof = _read_csv(new_step08 / "NV_PROFILE.csv")
    old_a2 = _a2_counts(old_prof).rename(
        columns={"a2_pass": "old_a2", "s2": "old_s2", "s3": "old_s3", "n_links": "old_n"}
    )
    new_a2 = _a2_counts(new_prof).rename(
        columns={"a2_pass": "new_a2", "s2": "new_s2", "s3": "new_s3", "n_links": "new_n"}
    )
    a2m = old_a2.merge(new_a2, on=["participant", "comparison"], how="outer")
    lines.extend(
        [
            "## 3. Signed NV profile (A2 / tiers)",
            "",
            "| participant | comparison | old A2 | new A2 | Δ A2 | old S2/S3 | new S2/S3 | old n | new n |",
            "|---|---|---:|---:|---:|---|---:|---:|---:|",
        ]
    )
    for _, r in a2m.iterrows():
        old_a2v = r.get("old_a2")
        new_a2v = r.get("new_a2")
        delta = "—"
        if pd.notna(old_a2v) and pd.notna(new_a2v):
            delta = int(new_a2v - old_a2v)
            delta = f"{delta:+d}"
        lines.append(
            f"| {r['participant']} | {r['comparison']} | "
            f"{r.get('old_a2', '—')} | {r.get('new_a2', '—')} | {delta} | "
            f"{int(r.get('old_s2', 0) or 0)}/{int(r.get('old_s3', 0) or 0)} | "
            f"{int(r.get('new_s2', 0) or 0)}/{int(r.get('new_s3', 0) or 0)} | "
            f"{r.get('old_n', '—')} | {r.get('new_n', '—')} |"
        )
    lines.append("")

    # Top-5 overlap per longitudinal comparison
    lines.extend(
        [
            "## 4. Top-5 link ranking (pooled |JcvPCA|, longitudinal only)",
            "",
            "| participant | comparison | overlap | old top-5 | new top-5 |",
            "|---|---|---:|---|---|",
        ]
    )
    for pid in PARTICIPANTS:
        old_lt = old_step04 / pid / f"{WINDOW}_pooled" / "link_level_results.csv"
        new_lt = new_step04 / pid / f"{WINDOW}_pooled" / "link_level_results.csv"
        for tp in ("T2", "T3"):
            comp = f"{pid}_T1_vs_{tp}"
            old5 = _top5_links(old_lt, comp)
            new5 = _top5_links(new_lt, comp)
            overlap = len(set(old5) & set(new5)) / 5 if old5 and new5 else float("nan")
            ov = f"{overlap:.1f}" if overlap == overlap else "—"
            lines.append(
                f"| {pid} | T1_vs_{tp} | {ov} | {', '.join(old5) or '—'} | {', '.join(new5) or '—'} |"
            )
    lines.append("")

    # Robustness labels
    old_rb = _robustness_labels(old_step04)
    new_rb = _robustness_labels(new_step04)
    rbm = old_rb.merge(
        new_rb,
        on=["participant", "comparison_id"],
        how="outer",
        suffixes=("_old", "_new"),
    )
    lines.extend(
        [
            "## 5. Step 4b robustness labels",
            "",
            "| participant | comparison | old | new |",
            "|---|---|---|---|",
        ]
    )
    for _, r in rbm.iterrows():
        lines.append(
            f"| {r['participant']} | {r['comparison_id']} | "
            f"{r.get('robustness_label_old', '—')} | {r.get('robustness_label_new', '—')} |"
        )
    lines.append("")

    # Step 5-7-9 summaries if present
    for step, fname, col, label in [
        ("step05_amplitude_vs_organization", "rom_rms_by_link.csv", "classification", "Step 5 org/amp mix"),
        ("step09_persistence_t2_t3", "persistence_results.csv", "persistence", "Step 9 persistence flags"),
    ]:
        old_p = new_root.parent / old_step04.name.replace("step04_primary_runs", step)
        # use canonical old paths
        old_paths = {
            "step05_amplitude_vs_organization": old_step04.parent / "step05_amplitude_vs_organization",
            "step09_persistence_t2_t3": old_step04.parent / "step09_persistence_t2_t3",
        }
        new_p = new_root / step
        old_csv = old_paths[step] / fname
        new_csv = new_p / fname
        if not new_csv.exists():
            continue
        old_df = _read_csv(old_csv)
        new_df = _read_csv(new_csv)
        if old_df.empty or new_df.empty or col not in new_df.columns:
            continue
        lines.extend([f"## 6. {label}", ""])
        if step == "step09_persistence_t2_t3":
            for pid in PARTICIPANTS:
                o = old_df[old_df["participant"].astype(str) == pid]["persistence"].value_counts()
                n = new_df[new_df["participant"].astype(str) == pid]["persistence"].value_counts()
                lines.append(f"- **{pid}** old persistent={o.get('persistent', 0)} → new {n.get('persistent', 0)}")
        else:
            for pid in PARTICIPANTS:
                for tp in ("T2", "T3"):
                    comp = f"{pid}_T1_vs_{tp}"
                    o = old_df[old_df["comparison_id"] == comp][col].value_counts()
                    n = new_df[new_df["comparison_id"] == comp][col].value_counts()
                    if o.empty and n.empty:
                        continue
                    lines.append(f"- **{comp}** org old={o.get('organization', 0)} new={n.get('organization', 0)}")
        lines.append("")

    lines.extend(
        [
            "## Summary interpretation",
            "",
            "- **Link count changes** reflect marker-gap drops (and any shared-feature intersection shifts).",
            "- **A2 / tier changes** can come from fewer links, different subspaces, or shifted signed effects.",
            "- **Top-5 overlap < 1.0** flags comparisons worth checking in run summaries; Step 4b k-grid remains the formal sensitivity check.",
            "- Pre-policy Step 5–9 used old Step 4/8 inputs; new Step 5–9 in this run tree are internally consistent with marker-gap Step 4/8.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--new-root",
        type=Path,
        default=ROOT / "results_committee_case" / "marker_gap_policy_ex09_13",
    )
    parser.add_argument(
        "--old-step04",
        type=Path,
        default=ROOT / "results_committee_case" / "step04_primary_runs",
    )
    parser.add_argument(
        "--old-step08",
        type=Path,
        default=ROOT / "results_committee_case" / "step08_nv_and_stability",
    )
    args = parser.parse_args()

    new_root = args.new_root.resolve()
    text = build_diff(new_root, args.old_step04.resolve(), args.old_step08.resolve())
    out_path = new_root / "DIFF_vs_pre_policy.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    print(f"Wrote {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
