"""Signed NV profile (v6): per-link signed metrics + S0–S3 tier classification.

Shared by ``scripts/observed_nv.py`` (Step 8h authoritative) and
``validation.py`` (per-run secondary). Does **not** touch the sacred jcvPCA core.

Design locks (see docs/MASTER_EXECUTION_PLAN.md v6 + SUPERVISOR_NV_DECISION.md):

- **Per-link signed value** = EVR-weighted signed sum of ``JcvPCA_link`` across the
  retained PCs (``weighted_JcvPCA_link``); falls back to a plain signed sum of
  ``JcvPCA_link`` when the weighted column is absent. **Never** ``mean(|Δ|)`` (that
  discards sign) and **never** an average across links.
- **A2 = tier S2** = magnitude exceed (``|long_signed| > |nv_signed|``) **and**
  reference-direction stability: ``sign(long_signed) == sign(long_signed_rev)``,
  where ``long_signed_rev`` anchors on ``T1_R2`` instead of ``T1_R1``. Sign
  consistency is stability under the arbitrary R1/R2 relabelling — **not** "same
  sign as the R1→R2 rep difference" (which would be label-dependent).
- **S1** = magnitude exceed but direction not reference-stable (report, not A2).
- **S3** = S2 + coverage adequate + repetition pass + Step-5 organization (+ optional
  stratum-K); set downstream where that evidence is joined. The Step-5 gate is joined on
  ``(comparison_id, link_id)`` in ``scripts/observed_nv.py``; that join is guarded because a
  silently-empty merge makes S3 unreachable for pipeline rather than scientific reasons.
- ``ε_sign`` (``EPS_SIGN``): links with ``|nv_signed| < ε_sign`` are flagged
  ``nv_floor_unstable`` (tiny denominator inflates any ratio).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

EPS_SIGN = 1e-6

SIGNED_COL_WEIGHTED = "weighted_JcvPCA_link"
SIGNED_COL_PLAIN = "JcvPCA_link"

TIER_S0 = "S0"
TIER_S1 = "S1"
TIER_S2 = "S2"
TIER_S3 = "S3"

# Step-5 ROM "flat band": follow-up/T1 pooled rotvec-magnitude range ratio inside
# this band means the link's contribution shifted without the link moving
# appreciably more or less. Defined here (not in the Step-5 script) so the
# Step-5 classifier and the S3 gate cannot drift apart.
ROM_FLAT_LOW = 0.7
ROM_FLAT_HIGH = 1.3


def rom_is_flat(rom_ratio: float, low: float = ROM_FLAT_LOW, high: float = ROM_FLAT_HIGH) -> bool:
    """True when a follow-up/T1 ROM ratio sits inside the flat band."""
    r = float(rom_ratio) if rom_ratio is not None else float("nan")
    return bool(np.isfinite(r) and low <= r <= high)


def link_signed_value(link_table: pd.DataFrame | None, weighted: bool = True) -> pd.Series:
    """Collapse a per-PC link table to **one signed scalar per link**.

    ``weighted=True`` uses the EVR-weighted signed sum (``weighted_JcvPCA_link``) when
    present, else falls back to the plain signed sum of ``JcvPCA_link``. Sign is always
    preserved (never absolute value). Returns a Series indexed by ``link_id``.
    """
    if link_table is None or len(link_table) == 0:
        return pd.Series(dtype=float)
    col = (
        SIGNED_COL_WEIGHTED
        if weighted and SIGNED_COL_WEIGHTED in link_table.columns
        else SIGNED_COL_PLAIN
    )
    return link_table.groupby("link_id")[col].sum()


def classify_nv_profile_tier(
    long_signed: float,
    nv_signed: float,
    long_signed_rev: float,
    eps_sign: float = EPS_SIGN,
) -> dict:
    """Classify one link into base tier S0/S1/S2 from three signed scalars.

    S3 is **not** assigned here (needs coverage/rep/Step-5 evidence) — see
    :func:`elevate_to_s3`.
    """
    nv_mag = abs(nv_signed)
    floor_unstable = nv_mag < eps_sign
    magnitude_exceed = abs(long_signed) > nv_mag

    sl = np.sign(long_signed)
    sign_reference_stable = bool(
        np.isfinite(long_signed_rev)
        and sl != 0
        and sl == np.sign(long_signed_rev)
    )

    if not magnitude_exceed:
        tier = TIER_S0
    elif sign_reference_stable:
        tier = TIER_S2
    else:
        tier = TIER_S1

    return {
        "nv_profile_tier": tier,
        "magnitude_exceed": bool(magnitude_exceed),
        "sign_reference_stable": sign_reference_stable,
        "nv_floor_unstable": bool(floor_unstable),
        "exceeds_signed_consistent": tier == TIER_S2,
    }


def elevate_to_s3(
    base_tier: str,
    coverage_ok: bool,
    rep_pass: bool,
    step5_organization: bool,
    stratum_ok: bool = True,
) -> str:
    """Elevate an S2 link to S3 when the full evidence stack passes."""
    if base_tier == TIER_S2 and coverage_ok and rep_pass and step5_organization and stratum_ok:
        return TIER_S3
    return base_tier


def compute_link_nv_metrics(
    nv_link_table: pd.DataFrame,
    long_link_table: pd.DataFrame,
    long_rev_link_table: pd.DataFrame | None = None,
    *,
    weighted: bool = True,
    eps_sign: float = EPS_SIGN,
) -> pd.DataFrame:
    """Join floor + longitudinal (+ reverse-anchor) into a per-link signed profile.

    ``nv_link_table``   : ``T1_R1 vs T1_R2`` comparison link table (floor).
    ``long_link_table`` : ``T1_R1 vs T{k}_R1`` comparison link table (A2 estimand).
    ``long_rev_link_table`` : ``T1_R2 vs T{k}_R1`` comparison link table (direction probe);
        when ``None``, ``sign_reference_stable`` is ``False`` (cannot be confirmed).
    """
    nv = link_signed_value(nv_link_table, weighted)
    lon = link_signed_value(long_link_table, weighted)
    rev = link_signed_value(long_rev_link_table, weighted)

    links = sorted(set(nv.index) | set(lon.index))
    rows: list[dict] = []
    for link in links:
        nv_v = float(nv.get(link, np.nan))
        lon_v = float(lon.get(link, np.nan))
        rev_v = float(rev.get(link, np.nan)) if len(rev) else np.nan
        if not (np.isfinite(nv_v) and np.isfinite(lon_v)):
            continue
        cls = classify_nv_profile_tier(lon_v, nv_v, rev_v, eps_sign)
        ratio = abs(lon_v) / (abs(nv_v) + eps_sign)
        rows.append(
            {
                "link_id": link,
                "nv_signed_t1": round(nv_v, 6),
                "long_signed_single": round(lon_v, 6),
                "long_signed_single_rev": round(rev_v, 6) if np.isfinite(rev_v) else np.nan,
                "matched_abs_ratio": round(ratio, 4),
                **cls,
            }
        )
    return pd.DataFrame(rows)
