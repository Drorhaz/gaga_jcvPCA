"""Load and slice the avatar link-level and region-space tables for a view."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .discovery import TableSet, ViewSpec

# The ``space`` column contains the literal value "null", which pandas would
# otherwise coerce to NaN (it is a default NA token). Read with a curated NA
# list so "null" survives as a string while genuinely blank cells still parse
# as missing.
_NA_VALUES = ["", "#N/A", "N/A", "NA", "NaN", "nan", "None"]


_BOOL_COLUMNS = ("exceeds_nv", "exceeds_nv_region")


def _coerce_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.strip().str.lower().isin(["true", "1", "yes"])


def _read_avatar_csv(path) -> pd.DataFrame:
    df = pd.read_csv(path, keep_default_na=False, na_values=_NA_VALUES)
    for col in _BOOL_COLUMNS:
        if col in df.columns:
            df[col] = _coerce_bool(df[col])
    return df


@dataclass(frozen=True)
class ViewTables:
    """All table rows relevant to a single participant x comparison x space view."""

    view: ViewSpec
    links_all_spaces: pd.DataFrame   # every space row for this comparison
    links_space: pd.DataFrame        # rows for the active space only
    region_space: pd.DataFrame       # region rollup for the active space only
    warnings_text: str               # first non-empty warning string, if any


def _first_warning(df: pd.DataFrame) -> str:
    if "warnings" not in df.columns:
        return ""
    for val in df["warnings"].dropna():
        text = str(val).strip()
        if text and text.lower() != "nan":
            return text
    return ""


def load_view_tables(table_set: TableSet, view: ViewSpec) -> ViewTables:
    links = _read_avatar_csv(table_set.link_level_csv)
    region_space = _read_avatar_csv(table_set.region_space_csv)

    links_space = links[links["space"] == view.space].copy()
    region_slice = region_space[region_space["space"] == view.space].copy()

    return ViewTables(
        view=view,
        links_all_spaces=links,
        links_space=links_space,
        region_space=region_slice,
        warnings_text=_first_warning(links),
    )
