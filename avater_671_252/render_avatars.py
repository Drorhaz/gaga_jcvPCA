#!/usr/bin/env python
"""Entry point: render the 671/252 body-avatar views from the built tables.

Self-contained under ``avater_671_252/``; imports the read-only ``gaga_jcvpca``
package for Motive parsing and config. Auto-discovers participants, comparisons,
and spaces from ``avater_671_252/tables/`` so new tables render with no edits.

Usage:
    python avater_671_252/render_avatars.py --all
    python avater_671_252/render_avatars.py --all --render-mode signed_nv
    python avater_671_252/render_avatars.py --all --render-mode both --summary-2x2 --validate
    python avater_671_252/render_avatars.py --region-heatmap
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_AVATAR_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _AVATAR_DIR.parent
for _p in (str(_PROJECT_ROOT), str(_PROJECT_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from avater_671_252.render.config import (  # noqa: E402
    RENDER_MODE_MAGNITUDE,
    RENDER_MODE_SIGNED,
    RENDER_MODES,
    load_render_config,
)
from avater_671_252.render.pipeline import render_all  # noqa: E402
from avater_671_252.render.region_heatmap import render_all_region_heatmaps  # noqa: E402
from avater_671_252.render.summary import render_summary_2x2  # noqa: E402
from avater_671_252.render.validate import write_report  # noqa: E402


def _modes_from_arg(render_mode: str) -> list[str]:
    if render_mode == "both":
        return [RENDER_MODE_MAGNITUDE, RENDER_MODE_SIGNED]
    return [render_mode]


def main() -> None:
    parser = argparse.ArgumentParser(description="Render 671/252 avatar views.")
    parser.add_argument("--all", action="store_true", help="Render all 12 views + meta JSON.")
    parser.add_argument("--summary-2x2", action="store_true", help="Render the 2x2 combined summary.")
    parser.add_argument("--validate", action="store_true", help="Write render_validation.md.")
    parser.add_argument("--rebuild-pose", action="store_true", help="Re-extract reference poses.")
    parser.add_argument(
        "--render-mode",
        choices=[*RENDER_MODES, "both"],
        default=RENDER_MODE_MAGNITUDE,
        help="magnitude_nv (default), signed_nv, or both.",
    )
    parser.add_argument("--config", default=None, help="Path to an alternate render_config.yaml.")
    parser.add_argument(
        "--region-heatmap",
        action="store_true",
        help="Render signed region-space body heatmaps (full-region fill).",
    )
    args = parser.parse_args()

    if not (args.all or args.summary_2x2 or args.validate or args.region_heatmap):
        parser.error("Nothing to do: pass --all, --summary-2x2, --region-heatmap, and/or --validate.")

    config = load_render_config(args.config)
    modes = _modes_from_arg(args.render_mode)

    if args.all:
        for mode in modes:
            results = render_all(
                _AVATAR_DIR, config=config, rebuild_pose=args.rebuild_pose, mode=mode,
            )
            out_dir = config.renders_dir_for_mode(_AVATAR_DIR, mode)
            for r in results:
                print(f"rendered [{mode}] {r.view_id}")
            print(f"\n{len(results)} views -> {out_dir}")

    if args.summary_2x2:
        for mode in modes:
            out = render_summary_2x2(_AVATAR_DIR, config=config, mode=mode)
            print(f"summary [{mode}] -> {out}")

    if args.validate:
        report = write_report(_AVATAR_DIR, config=config, modes=modes)
        print(f"validation -> {report}")

    if args.region_heatmap:
        results = render_all_region_heatmaps(_AVATAR_DIR, config=config, rebuild_pose=args.rebuild_pose)
        for r in results:
            print(f"region heatmap {r.view_id} <- {Path(r.source_csv).name}")
        print(f"\n{len(results)} region heatmaps -> {_AVATAR_DIR / 'renders' / config.region_heatmap_output_subdir}")


if __name__ == "__main__":
    main()
