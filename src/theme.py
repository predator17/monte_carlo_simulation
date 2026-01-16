"""Dark mode theme styling for the Portfolio Monte Carlo Simulator.

This module provides QSS (Qt Style Sheets) for dark mode styling
across all UI components.
"""

from src.constants import Colors


def get_dark_theme_stylesheet() -> str:
    """Return the complete dark mode stylesheet for the application.

    The stylesheet follows the VS Code dark theme color palette
    specified in the constants module.

    Returns:
        str: Complete QSS stylesheet string.
    """
    return f"""
    /* ========================================================================
       Global Styles
       ======================================================================== */

    * {{
        color: {Colors.TEXT_PRIMARY};
    }}

    QWidget {{
        background-color: {Colors.BG_PRIMARY};
        color: {Colors.TEXT_PRIMARY};
        border: none;
    }}

    /* ========================================================================
       QMainWindow
       ======================================================================== */

    QMainWindow {{
        background-color: {Colors.BG_PRIMARY};
    }}

    /* ========================================================================
       Buttons
       ======================================================================== */

    QPushButton {{
        background-color: {Colors.ACCENT_BLUE};
        color: {Colors.TEXT_PRIMARY};
        border: none;
        border-radius: {4}px;
        padding: 8px 16px;
        font-size: 10pt;
    }}

    QPushButton:hover {{
        background-color: {Colors.ACCENT_BLUE_HOVER};
    }}

    QPushButton:pressed {{
        background-color: {Colors.ACCENT_BLUE_PRESSED};
    }}

    QPushButton:disabled {{
        background-color: {Colors.BORDER_SEPARATOR};
        color: {Colors.TEXT_DISABLED};
    }}

    QPushButton#secondaryButton {{
        background-color: {Colors.BG_SECONDARY};
        border: 1px solid {Colors.BORDER_INPUT};
    }}

    QPushButton#secondaryButton:hover {{
        background-color: {Colors.BG_CARD};
    }}

    /* ========================================================================
       Input Fields
       ======================================================================== */

    QSpinBox, QDoubleSpinBox {{
        background-color: {Colors.BG_INPUT};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER_INPUT};
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 10pt;
    }}

    QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 1px solid {Colors.BORDER_FOCUS};
    }}

    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        background-color: {Colors.BG_SECONDARY};
        border: none;
        width: 16px;
    }}

    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        background-color: {Colors.BG_SECONDARY};
        border: none;
        width: 16px;
    }}

    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
        background-color: {Colors.BG_CARD};
    }}

    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow,
    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
        width: 8px;
        height: 8px;
    }}

    QComboBox {{
        background-color: {Colors.BG_INPUT};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER_INPUT};
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 10pt;
    }}

    QComboBox:focus {{
        border: 1px solid {Colors.BORDER_FOCUS};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}

    QComboBox::down-arrow {{
        width: 10px;
        height: 10px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {Colors.BG_SECONDARY};
        border: 1px solid {Colors.BORDER_INPUT};
        selection-background-color: {Colors.ACCENT_BLUE};
        color: {Colors.TEXT_PRIMARY};
    }}

    /* ========================================================================
       Slider
       ======================================================================== */

    QSlider::groove:horizontal {{
        background-color: {Colors.BG_SECONDARY};
        height: 4px;
        border-radius: 2px;
    }}

    QSlider::handle:horizontal {{
        background-color: {Colors.ACCENT_BLUE};
        width: 16px;
        height: 16px;
        border-radius: 8px;
        margin: -6px 0;
    }}

    QSlider::handle:horizontal:hover {{
        background-color: {Colors.ACCENT_BLUE_HOVER};
    }}

    QSlider::sub-page:horizontal {{
        background-color: {Colors.ACCENT_BLUE};
        border-radius: 2px;
    }}

    /* ========================================================================
       Cards (QFrame)
       ======================================================================== */

    QFrame[frameShape="4"], /* HLine */
    QFrame[frameShape="5"]  /* VLine */ {{
        color: {Colors.BORDER_SEPARATOR};
        background-color: {Colors.BORDER_SEPARATOR};
    }}

    /* ========================================================================
       Table
       ======================================================================== */

    QTableView {{
        background-color: {Colors.BG_PRIMARY};
        alternate-background-color: {Colors.BG_SECONDARY};
        color: {Colors.TEXT_PRIMARY};
        gridline-color: {Colors.BORDER_SEPARATOR};
        border: none;
        selection-background-color: {Colors.ACCENT_BLUE};
        selection-color: {Colors.TEXT_PRIMARY};
    }}

    QTableView::item:selected {{
        background-color: {Colors.ACCENT_BLUE};
    }}

    QTableView::item:hover {{
        background-color: {Colors.BG_CARD};
    }}

    QHeaderView::section {{
        background-color: {Colors.BG_CARD};
        color: {Colors.TEXT_PRIMARY};
        border: none;
        border-bottom: 1px solid {Colors.BORDER_SEPARATOR};
        border-right: 1px solid {Colors.BORDER_SEPARATOR};
        padding: 8px;
        font-weight: bold;
    }}

    QTableView QTableCornerButton::section {{
        background-color: {Colors.BG_CARD};
        border: none;
    }}

    QScrollBar:vertical {{
        background-color: {Colors.BG_SECONDARY};
        width: 12px;
        border-radius: 6px;
    }}

    QScrollBar::handle:vertical {{
        background-color: {Colors.BORDER_SEPARATOR};
        border-radius: 6px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {Colors.TEXT_DISABLED};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar:horizontal {{
        background-color: {Colors.BG_SECONDARY};
        height: 12px;
        border-radius: 6px;
    }}

    QScrollBar::handle:horizontal {{
        background-color: {Colors.BORDER_SEPARATOR};
        border-radius: 6px;
        min-width: 30px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background-color: {Colors.TEXT_DISABLED};
    }}

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* ========================================================================
       Tab Widget
       ======================================================================== */

    QTabWidget::pane {{
        border: none;
        background-color: {Colors.BG_PRIMARY};
    }}

    QTabBar::tab {{
        background-color: {Colors.BG_SECONDARY};
        color: {Colors.TEXT_SECONDARY};
        border: none;
        padding: 10px 20px;
        margin-right: 2px;
    }}

    QTabBar::tab:selected {{
        background-color: {Colors.BG_PRIMARY};
        color: {Colors.TEXT_PRIMARY};
        border-bottom: 2px solid {Colors.ACCENT_BLUE};
    }}

    QTabBar::tab:hover {{
        background-color: {Colors.BG_CARD};
    }}

    /* ========================================================================
       Labels
       ======================================================================== */

    QLabel {{
        color: {Colors.TEXT_PRIMARY};
        background: none;
    }}

    QLabel#secondaryLabel {{
        color: {Colors.TEXT_SECONDARY};
    }}

    QLabel#largeNumber {{
        font-size: 24pt;
        font-weight: bold;
        color: {Colors.TEXT_PRIMARY};
    }}

    QLabel#headerLabel {{
        font-size: 14pt;
        font-weight: bold;
        color: {Colors.TEXT_PRIMARY};
    }}

    /* ========================================================================
       Progress Bar
       ======================================================================== */

    QProgressBar {{
        background-color: {Colors.BG_SECONDARY};
        border: none;
        border-radius: 4px;
        height: 8px;
        text-align: center;
    }}

    QProgressBar::chunk {{
        background-color: {Colors.ACCENT_GREEN};
        border-radius: 4px;
    }}

    /* ========================================================================
       Scroll Area
       ======================================================================== */

    QScrollArea {{
        border: none;
        background-color: {Colors.BG_PRIMARY};
    }}

    QScrollArea > QWidget > QWidget {{
        background-color: {Colors.BG_PRIMARY};
    }}

    /* ========================================================================
       Group Box
       ======================================================================== */

    QGroupBox {{
        background-color: {Colors.BG_CARD};
        border: 1px solid {Colors.BORDER_SEPARATOR};
        border-radius: 8px;
        margin-top: 12px;
        padding: 16px;
        font-size: 10pt;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 4px 8px;
        color: {Colors.TEXT_SECONDARY};
    }}
    """


def apply_dark_theme(app):
    """Apply the dark theme to a QApplication.

    Args:
        app: QApplication instance to style.
    """
    app.setStyleSheet(get_dark_theme_stylesheet())
