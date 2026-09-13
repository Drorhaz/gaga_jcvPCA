"""Discover participants missing feature manifests and offer to generate them.

Scans ``data/raw_skeleton/`` for participants without a matching manifest CSV,
classifies skeleton topology against known 671 (14-link) and 252 (16-link) layouts,
and optionally writes a cloned manifest file.

Usage:
  .venv/bin/python scripts/generate_feature_manifest.py              # report only
  .venv/bin/python scripts/generate_feature_manifest.py --apply      # prompt per participant
  .venv/bin/python scripts/generate_feature_manifest.py --apply --yes  # generate all safe matches
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaga_jcvpca.config import load_config
from gaga_jcvpca.feature_manifest_gen import (
    TopologyKind,
    discover_missing_manifests,
    format_report,
    generate_manifest_csv,
    verify_manifest_links,
)


def _prompt_yes_no(message: str, default_no: bool = True) -> bool:
    suffix = " [y/N]: " if default_no else " [Y/n]: "
    try:
        answer = input(message + suffix).strip().lower()
    except EOFError:
        return False
    if not answer:
        return not default_no
    return answer in {"y", "yes"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write manifest CSV files (prompts unless --yes is set)",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="With --apply, generate without prompting (skips UNKNOWN topology)",
    )
    parser.add_argument(
        "--participant",
        action="append",
        default=[],
        help="Limit to participant id(s); default = all missing",
    )
    args = parser.parse_args()

    cfg = load_config()
    reports = discover_missing_manifests(cfg)
    if args.participant:
        wanted = set(args.participant)
        reports = [r for r in reports if r.participant in wanted]

    if not reports:
        print("All participants with skeleton data already have feature manifests.")
        return 0

    print(f"Found {len(reports)} participant(s) missing feature manifests:\n")
    for report in reports:
        print(format_report(report))
        print()

    if not args.apply:
        print(
            "Dry run only. Re-run with --apply to generate manifests, "
            "or --apply --yes to accept all known-topology matches."
        )
        return 0

    manifest_dir = cfg.resolve_path("data.feature_manifests")
    generated = 0
    skipped = 0

    for report in reports:
        if report.assessment.kind == TopologyKind.UNKNOWN:
            print(f"skip {report.participant}: unknown topology — create manifest manually")
            skipped += 1
            continue
        if not report.assessment.bone_names_match_reference:
            print(
                f"warning {report.participant}: bone names differ from "
                f"{report.assessment.reference_participant} reference"
            )
            if not args.yes and not _prompt_yes_no(
                f"Generate anyway for {report.participant}?", default_no=True
            ):
                skipped += 1
                continue
        elif not args.yes and not _prompt_yes_no(
            f"Generate {report.proposed_filename} for {report.participant}?",
            default_no=False,
        ):
            skipped += 1
            continue

        out_path = manifest_dir / report.proposed_filename
        if out_path.exists():
            print(f"skip {report.participant}: {out_path.name} already exists")
            skipped += 1
            continue

        generate_manifest_csv(
            report.participant,
            report.template_manifest,
            out_path,
            report.assessment.reference_participant,
        )
        ok, missing_links = verify_manifest_links(report.hierarchy, out_path)
        if not ok:
            out_path.unlink(missing_ok=True)
            print(
                f"error {report.participant}: generated manifest missing skeleton links: "
                f"{', '.join(missing_links)}"
            )
            skipped += 1
            continue

        print(f"wrote {out_path.relative_to(ROOT)}")
        generated += 1

    print(f"\nDone: {generated} generated, {skipped} skipped.")
    if generated:
        print(
            "Next: add participant to configs/default.yaml if needed; "
            "run scripts/generate_datadescriptions.py for sidecars; "
            "run scripts/run_convert.py after segmentation is available."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
