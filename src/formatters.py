"""Formatting utilities for currency, percentages, and numbers.

This module provides consistent formatting functions for all
displayed values in the application.
"""

import locale
from typing import Literal

# Try to set Chinese locale for proper currency formatting
try:
    locale.setlocale(locale.LC_ALL, "zh_CN.UTF-8")
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, "Chinese_China.UTF8")
    except locale.Error:
        # Fallback to default
        pass


CurrencyStyle = Literal["symbol", "suffix", "compact"]


def format_currency(
    value: float,
    style: CurrencyStyle = "symbol",
    decimals: int = 0,
) -> str:
    """Format a number as currency.

    Args:
        value: Numeric value to format.
        style: Formatting style:
            - "symbol": ¥1,234,567 (default)
            - "suffix": 1,234,567 ¥
            - "compact": 1.23M, 456K
        decimals: Number of decimal places.

    Returns:
        Formatted currency string.
    """
    if style == "compact":
        return _format_compact(value, decimals)

    # Format with thousands separator
    formatted = f"{value:,.{decimals}f}"

    if style == "suffix":
        return f"{formatted} ¥"
    return f"¥{formatted}"


def _format_compact(value: float, decimals: int = 2) -> str:
    """Format a number in compact notation (K, M, B).

    Args:
        value: Numeric value to format.
        decimals: Number of decimal places.

    Returns:
        Compact formatted string.
    """
    abs_value = abs(value)

    if abs_value >= 1_000_000_000:
        suffix = "B"
        divided = value / 1_000_000_000
    elif abs_value >= 1_000_000:
        suffix = "M"
        divided = value / 1_000_000
    elif abs_value >= 1_000:
        suffix = "K"
        divided = value / 1_000
    else:
        return f"¥{value:,.{decimals}f}"

    # Handle negative values
    sign = "-" if value < 0 else ""
    return f"¥{sign}{abs(divided):.{decimals}f}{suffix}"


def format_percentage(
    value: float,
    decimals: int = 2,
    sign: bool = True,
) -> str:
    """Format a number as a percentage.

    Args:
        value: Numeric value (e.g., 5.23 for 5.23%).
        decimals: Number of decimal places.
        sign: Include + sign for positive values.

    Returns:
        Formatted percentage string.
    """
    formatted = f"{abs(value):.{decimals}f}%"

    if sign:
        if value > 0:
            return f"+{formatted}"
        elif value < 0:
            return f"-{formatted}"
    return formatted


def format_number(
    value: float,
    decimals: int = 0,
    thousands: bool = True,
) -> str:
    """Format a number with optional thousands separator.

    Args:
        value: Numeric value to format.
        decimals: Number of decimal places.
        thousands: Use thousands separator.

    Returns:
        Formatted number string.
    """
    if thousands:
        return f"{value:,.{decimals}f}"
    return f"{value:.{decimals}f}"


def format_large_number(value: float, decimals: int = 1) -> str:
    """Format a large number with suffix (K, M, B).

    Args:
        value: Numeric value to format.
        decimals: Number of decimal places.

    Returns:
        Formatted string with suffix.
    """
    abs_value = abs(value)

    if abs_value >= 1_000_000_000:
        suffix = "B"
        divided = value / 1_000_000_000
    elif abs_value >= 1_000_000:
        suffix = "M"
        divided = value / 1_000_000
    elif abs_value >= 1_000:
        suffix = "K"
        divided = value / 1_000
    else:
        return f"{value:.{decimals}f}"

    sign = "-" if value < 0 else ""
    return f"{sign}{abs(divided):.{decimals}f}{suffix}"


def format_month_year(month_idx: int) -> str:
    """Format a month index as "MMM YYYY" string.

    Args:
        month_idx: Zero-based month index.

    Returns:
        Formatted string like "Jan 2025".
    """
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    year = month_idx // 12
    month = months[month_idx % 12]
    return f"{month} {year}"


def format_period_label(month_idx: int) -> str:
    """Format a month index as a period label.

    Args:
        month_idx: Zero-based month index.

    Returns:
        Formatted string like "Y1 M3" for Year 1, Month 3.
    """
    year = month_idx // 12 + 1
    month = month_idx % 12 + 1
    return f"Y{year} M{month}"


def format_success_rate(rate: float) -> str:
    """Format success rate with color indicator.

    Args:
        rate: Success rate percentage (0-100).

    Returns:
        Formatted string.
    """
    return f"{rate:.1f}%"


def get_success_color(rate: float) -> str:
    """Get color code for success rate.

    Args:
        rate: Success rate percentage (0-100).

    Returns:
        Hex color code.
    """
    if rate >= 90:
        return "#4EC9B0"  # Green
    elif rate >= 70:
        return "#569CD6"  # Blue
    elif rate >= 50:
        return "#CE9178"  # Orange
    else:
        return "#F44747"  # Red
