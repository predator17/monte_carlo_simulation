"""Constants for the Portfolio Monte Carlo Simulator.

This module contains all color, font, and formatting constants
used throughout the application, following the dark mode theme.
"""

from PySide6.QtGui import QColor, QPalette, QFont
from PySide6.QtCore import Qt

# =============================================================================
# Color Palette - Dark Mode Theme
# =============================================================================

class Colors:
    """Dark mode color palette."""

    # Background colors
    BG_PRIMARY = "#1E1E1E"
    BG_SECONDARY = "#252526"
    BG_CARD = "#2D2D30"
    BG_INPUT = "#252526"

    # Text colors
    TEXT_PRIMARY = "#E0E0E0"
    TEXT_SECONDARY = "#A0A0A0"
    TEXT_DISABLED = "#5A5A5A"

    # Accent colors
    ACCENT_BLUE = "#007ACC"
    ACCENT_BLUE_HOVER = "#1F8AD2"
    ACCENT_BLUE_PRESSED = "#1785D4"
    ACCENT_GREEN = "#4EC9B0"
    ACCENT_ORANGE = "#CE9178"
    ACCENT_RED = "#F44747"

    # Border colors
    BORDER_SEPARATOR = "#3E3E42"
    BORDER_FOCUS = "#007ACC"
    BORDER_INPUT = "#3E3E42"

    # Chart colors
    CHART_GRID = "#3E3E42"
    CHART_AXIS_TEXT = "#A0A0A0"
    CHART_LINE_1 = "#4EC9B0"
    CHART_LINE_2 = "#569CD6"
    CHART_LINE_3 = "#DCDCAA"
    CHART_LINE_4 = "#C586C0"
    CHART_LINE_5 = "#FF6B6B"
    CHART_FILL = QColor(78, 201, 176, 50)  # Transparent green

    # Success gauge colors
    SUCCESS_HIGH = "#4EC9B0"  # >= 90%
    SUCCESS_MEDIUM = "#569CD6"  # 70-89%
    SUCCESS_LOW = "#CE9178"  # 50-69%
    SUCCESS_DANGER = "#F44747"  # < 50%


# =============================================================================
# Typography
# =============================================================================

class Fonts:
    """Font size and weight constants."""

    # Font sizes (in points)
    WINDOW_TITLE = 12
    HEADER = 14
    BODY = 10
    BODY_SMALL = 9
    LARGE_NUMBER = 24
    INPUT = 10

    # Font weights
    WEIGHT_NORMAL = QFont.Weight.Normal
    WEIGHT_MEDIUM = QFont.Weight.Medium
    WEIGHT_BOLD = QFont.Weight.Bold


# =============================================================================
# Formatting
# =============================================================================

class Format:
    """Number and currency formatting constants."""

    CURRENCY_SYMBOL = "¥"
    CURRENCY_LOCALE = "zh_CN"
    DECIMAL_PLACES = 2
    PERCENT_DECIMAL_PLACES = 2

    # Large number suffixes
    SUFFIX_K = 1_000  # Thousand
    SUFFIX_M = 1_000_000  # Million
    SUFFIX_B = 1_000_000_000  # Billion


# =============================================================================
# GUI Constants
# =============================================================================

class GUI:
    """GUI layout and sizing constants."""

    # Window
    WINDOW_MIN_WIDTH = 1200
    WINDOW_MIN_HEIGHT = 1200  # Increased for better visibility
    WINDOW_DEFAULT_WIDTH = 1400
    WINDOW_DEFAULT_HEIGHT = 1350  # Increased by 50% from 900

    # Spacing
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 16
    SPACING_LG = 24
    SPACING_XL = 32

    # Borders
    BORDER_RADIUS_SM = 4
    BORDER_RADIUS_MD = 8

    # Cards
    CARD_MARGIN = 16
    CARD_PADDING = 16

    # Animation
    ANIMATION_DURATION_MS = 150
    PROGRESS_UPDATE_INTERVAL_MS = 100

    # Table
    TABLE_ROW_HEIGHT = 28
    TABLE_HEADER_HEIGHT = 36
    TABLE_FETCH_BATCH_SIZE = 100


# =============================================================================
# Chart Constants
# =============================================================================>

class Charts:
    """PyQtGraph chart configuration constants."""

    # Plot background
    BACKGROUND = Colors.BG_PRIMARY

    # Axis configuration
    AXIS_COLOR = Colors.CHART_AXIS_TEXT
    GRID_COLOR = Colors.CHART_GRID

    # Line styles
    LINE_WIDTH = 2
    LINE_WIDTH_THICK = 3

    # Histogram
    HISTOGRAM_BINS = 50
    HISTOGRAM_FILL_LEVEL = 0
    HISTOGRAM_BRUSH = QColor(78, 201, 176, 100)

    # Percentile lines
    PERCENTILES = [10, 25, 50, 75, 90]
    PERCENTILE_COLORS = {
        10: Colors.CHART_LINE_5,
        25: Colors.CHART_LINE_4,
        50: Colors.CHART_LINE_1,
        75: Colors.CHART_LINE_2,
        90: Colors.CHART_LINE_3,
    }
