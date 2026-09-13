"""Step 9 — T2 vs T3 persistence (post-hoc on NV_PROFILE.csv).

Checks whether a per-link change seen at T2 is sustained at T3, using the v6 signed
matched single-rep effect:

- **sign agreement:** ``sign(long_signed_single@T2) == sign(long_signed_single@T3)``
- **persistence flag:**
    - ``persistent``   — A2 pass (S2/S3) at both T2 and T3, same sign
    - ``emergent_T3``  — A2 at T3 only
    - ``transient_T2`` — A2 at T2 only
    - ``none``         — A2 at neither

Persistence is descriptive within-participant; it does **not** separate instruction
from lasting change (design limit).

Usage: PYTHONPATH=src .venv/bin/python scripts/step09_persistence_t2_t3.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PARTICIPANTS = ("671", "252", "651", "790")


def _flag(a2_t2: bool, a2_t3: bool, sign_ok: bool) -> str:
    if a2_t2 and a2_t3:
        return "persistent" if sign_ok else "sign_flip"
    if a2_t3 and not a2_t2:
        return "emergent_T3"
    if a2_t2 and not a2_t3:
        return "transient_T2"
    return "none"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--step08-root",
        type=Path,
        default=ROOT / "results_committee_case" / "step08_nv_and_stability",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "results_committee_case" / "step09_persistence_t2_t3",
    )
    args = parser.parse_args()
    step08 = args.step08_root.resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    profile = pd.read_csv(step08 / "NV_PROFILE.csv")
    profile["participant"] = profile["participant"].astype(str)

    rows: list[dict] = []
    for pid in PARTICIPANTS:
        prof = profile[profile["participant"] == pid]
        t2 = prof[prof["comparison_id"] == f"{pid}_T1_vs_T2"].set_index("link_id")
        t3 = prof[prof["comparison_id"] == f"{pid}_T1_vs_T3"].set_index("link_id")
        links = sorted(set(t2.index) & set(t3.index))
        for link in links:
            r2, r3 = t2.loc[link], t3.loc[link]
            s2, s3 = np.sign(r2["long_signed_single"]), np.sign(r3["long_signed_single"])
            sign_ok = bool(s2 != 0 and s2 == s3)
            rows.append(
                {
                    "participant": pid,
                    "link_id": link,
                    "long_signed_T2": r2["long_signed_single"],
                    "long_signed_T3": r3["long_signed_single"],
                    "tier_T2": r2["nv_profile_tier"],
                    "tier_T3": r3["nv_profile_tier"],
                    "a2_T2": bool(r2["a2_pass"]),
                    "a2_T3": bool(r3["a2_pass"]),
                    "sign_agreement": sign_ok,
                    "persistence": _flag(bool(r2["a2_pass"]), bool(r3["a2_pass"]), sign_ok),
                }
            )

    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "persistence_results.csv", index=False)

    lines = [
        "# Step 9 — T2 vs T3 persistence",
        "",
        "Per-link agreement of the v6 signed matched single-rep effect between T2 and T3. "
        "Descriptive only — does not separate instruction from lasting change.",
        "",
        "| participant | persistent | emergent_T3 | transient_T2 | sign_flip | sign-agree (all links) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for pid in PARTICIPANTS:
        sub = df[df["participant"] == pid]
        if sub.empty:
            continue
        counts = sub["persistence"].value_counts()
        sign_rate = f"{sub['sign_agreement'].mean():.0%}"
        lines.append(
            f"| {pid} | {counts.get('persistent', 0)} | {counts.get('emergent_T3', 0)} | "
            f"{counts.get('transient_T2', 0)} | {counts.get('sign_flip', 0)} | {sign_rate} |"
        )
    lines += [
        "",
        "## Persistent A2 links (S2/S3 at both T2 and T3, same sign)",
        "",
    ]
    for pid in PARTICIPANTS:
        persist = df[(df["participant"] == pid) & (df["persistence"] == "persistent")]["link_id"].tolist()
        lines.append(f"- **{pid}:** {', '.join(persist) if persist else '— none'}")
    lines.append("")
    (out_dir / "persistence_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_dir.relative_to(ROOT)} ({len(df)} rows)")
    print("\n".join(lines[4:6 + len(PARTICIPANTS)]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
