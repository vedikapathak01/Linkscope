from __future__ import annotations

from typing import Any

import pandas as pd


def safe_numeric(value: Any, default: float = 0.0) -> float:
    """Return a float value while safely handling NaN and None."""
    try:
        if value is None or pd.isna(value):
            return float(default)
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def normalize_series(series: pd.Series) -> pd.Series:
    """Min-max normalize a numeric series with safe handling for empty inputs."""
    if series.empty:
        return pd.Series([], dtype=float)

    min_val = series.min()
    max_val = series.max()
    if pd.isna(min_val) or pd.isna(max_val) or max_val == min_val:
        return pd.Series(0.5, index=series.index, dtype=float)
    return (series - min_val) / (max_val - min_val)


def format_number(value: Any, decimals: int = 0) -> str:
    """Render compact numbers for dashboard labels."""
    try:
        num = float(value)
    except (TypeError, ValueError):
        return "0"

    if abs(num) >= 1_000_000:
        return f"{num / 1_000_000:.{decimals}f}M"
    if abs(num) >= 1_000:
        return f"{num / 1_000:.{decimals}f}K"
    return f"{num:.{decimals}f}"


def empty_frame() -> pd.DataFrame:
    """Return an empty DataFrame with the expected schema."""
    return pd.DataFrame(
        columns=[
            "post_id",
            "user_id",
            "post_text",
            "url",
            "domain",
            "category",
            "likes",
            "comments",
            "shares",
            "timestamp",
            "engagement",
        ]
    )
