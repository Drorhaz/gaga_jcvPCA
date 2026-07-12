"""Load and expose ``render_config.yaml`` (RENDER_PLAN E1-E10 visual locks)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

# render/config.py -> avater_671_252/ is one parent up.
_AVATAR_DIR = Path(__file__).resolve().parents[1]
_DEFAULT_CONFIG = _AVATAR_DIR / "render_config.yaml"

RENDER_MODE_MAGNITUDE = "magnitude_nv"
RENDER_MODE_SIGNED = "signed_nv"
RENDER_MODES = (RENDER_MODE_MAGNITUDE, RENDER_MODE_SIGNED)


@dataclass(frozen=True)
class RenderConfig:
    """Thin typed wrapper over the render config dict with dotted access."""

    data: dict[str, Any]
    path: Path
    avatar_dir: Path

    def get(self, dotted_key: str, default: Any = None) -> Any:
        node: Any = self.data
        for part in dotted_key.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return default
        return node

    # --- E1 intensity ---
    def intensity_color(self, ratio: float | None) -> str:
        """Map an effect_ratio_vs_nv to a fill hex per the configured ascending bands.

        Bands are half-open, ordered by ``max`` ascending; the final band has a
        null ``max`` meaning "and above". A ratio at or below the first band's
        max (1.0) resolves to the within-NV gray automatically.
        """
        neutral = self.get("intensity.neutral_color", "#B0B0B0")
        if ratio is None:
            return neutral
        for band in self.get("intensity.bands", []) or []:
            hi = band.get("max")
            if hi is None or float(ratio) <= float(hi) + 1e-12:
                return band["color"]
        return neutral

    @property
    def top_n(self) -> int:
        return int(self.get("callouts.top_n", 3))

    @property
    def regions_order(self) -> list[str]:
        return list(self.get("regions.order", []) or [])

    def is_t3_confound(self, participant: str) -> bool:
        return str(participant) in set(self.get("footer.t3_confound_participants", []) or [])

    @property
    def strong_ratio_threshold(self) -> float:
        return float(self.get("signed_nv.strong_ratio_threshold", 3.0))

    @property
    def signed_output_subdir(self) -> str:
        return str(self.get("signed_nv.output_subdir", "signed_nv"))

    @property
    def signed_tables_subdir(self) -> str:
        return str(self.get("signed_nv.tables_subdir", "signed_nv"))

    def signed_palette(self) -> dict[str, str]:
        return dict(self.get("signed_nv.palette", {}) or {})

    def signed_color(self, signed_value: float, ratio: float, exceeds: bool) -> str:
        """Map signed JcvPCA change + NV exceedance to a fill hex (signed_nv mode).

        Within NV -> neutral gray. Above NV: direction from ``signed_value`` sign,
        strength from ``effect_ratio_vs_nv`` vs ``strong_ratio_threshold``.
        """
        return self.signed_color_continuous(signed_value, ratio, exceeds, discrete=True)

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
        h = hex_color.lstrip("#")
        return tuple(int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))

    @staticmethod
    def _rgb_to_hex(rgb: tuple[float, float, float]) -> str:
        return "#{:02X}{:02X}{:02X}".format(
            *(max(0, min(255, int(round(c * 255)))) for c in rgb)
        )

    @classmethod
    def _lerp_hex(cls, c1: str, c2: str, t: float) -> str:
        t = max(0.0, min(1.0, float(t)))
        a = cls._hex_to_rgb(c1)
        b = cls._hex_to_rgb(c2)
        return cls._rgb_to_hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))

    def signed_color_continuous(
        self,
        signed_value: float,
        ratio: float,
        exceeds: bool,
        *,
        discrete: bool = False,
    ) -> str:
        """Signed fill color with optional continuous ratio gradient (region heatmaps)."""
        pal = self.signed_palette()
        neutral = pal.get("neutral", self.get("intensity.neutral_color", "#B0B0B0"))
        if not exceeds or float(ratio) <= 1.0 + 1e-12:
            return neutral

        strong_hi = self.strong_ratio_threshold
        if discrete:
            is_strong = float(ratio) > strong_hi + 1e-12
            if signed_value < 0:
                return pal.get(
                    "dark_blue" if is_strong else "light_blue",
                    "#08519C" if is_strong else "#9ECAE1",
                )
            if signed_value > 0:
                return pal.get(
                    "strong_positive" if is_strong else "moderate_positive",
                    "#DC143C" if is_strong else "#FFD700",
                )
            return neutral

        # Continuous blend: ratio 1.0 -> moderate tone, ratio >= strong_hi -> strong tone.
        span = max(strong_hi - 1.0, 1e-6)
        t = min(1.0, max(0.0, (float(ratio) - 1.0) / span))
        if signed_value < 0:
            return self._lerp_hex(
                pal.get("light_blue", "#9ECAE1"),
                pal.get("dark_blue", "#08519C"),
                t,
            )
        if signed_value > 0:
            return self._lerp_hex(
                pal.get("moderate_positive", "#FFD700"),
                pal.get("strong_positive", "#DC143C"),
                t,
            )
        return neutral

    @property
    def region_heatmap_output_subdir(self) -> str:
        return str(self.get("region_heatmap.output_subdir", "signed_nv/region_heatmap"))

    def renders_dir_for_mode(self, avatar_dir: Path, mode: str) -> Path:
        base = avatar_dir / "renders"
        if mode == RENDER_MODE_SIGNED:
            return base / self.signed_output_subdir
        return base

    def tables_dir_for_mode(self, avatar_dir: Path, mode: str) -> Path:
        base = avatar_dir / "tables"
        if mode == RENDER_MODE_SIGNED:
            return base / self.signed_tables_subdir
        return base

    def legend_lines_for_mode(self, mode: str) -> list[str]:
        if mode == RENDER_MODE_SIGNED:
            return list(self.get("signed_nv.legend_lines", []) or [])
        return list(self.get("legend_lines", []) or [])


def load_render_config(path: str | Path | None = None) -> RenderConfig:
    cfg_path = Path(path) if path is not None else _DEFAULT_CONFIG
    with open(cfg_path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return RenderConfig(data=data, path=cfg_path, avatar_dir=_AVATAR_DIR)
