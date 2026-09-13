"""Self-contained body-avatar rendering for the 671/252 JcvPCA tables.

Reads the already-built, validated tables under ``avater_671_252/tables/`` and
turns them into annotated static avatar views (matplotlib PNGs) plus per-view
traceability metadata. No JcvPCA re-run happens here.

The package auto-discovers participants, comparisons, and spaces from the tables
directory, so adding a new participant's tables renders with zero code edits.
"""

from __future__ import annotations

__all__ = [
    "load_render_config",
    "RenderConfig",
]

from .config import RenderConfig, load_render_config
