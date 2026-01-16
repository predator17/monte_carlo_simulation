"""Results display page for simulation outputs.

This module provides the results page where users can view
simulation results through charts and tables.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QPushButton, QLabel
)
from PySide6.QtCore import Signal, Qt
from typing import Optional

from src.results import ResultManager
from src.constants import GUI, Colors, Fonts
from src.gui.components.success_gauge import SuccessGauge
from src.gui.components.summary_card import SummaryCard
from src.gui.components.chart_tabs import ChartTabs


class ResultsPage(QWidget):
    """Results display page.

    Shows simulation success rate, summary statistics, and
    interactive charts for detailed analysis.

    Signals:
        back_requested: Emitted when user clicks back to inputs.
    """

    back_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the results page.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header with back button
        header = QWidget()
        header.setStyleSheet(f"background-color: {Colors.BG_SECONDARY};")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(GUI.SPACING_LG, GUI.SPACING_MD,
                                         GUI.SPACING_LG, GUI.SPACING_MD)

        self.back_button = QPushButton("◀ Edit Inputs")
        self.back_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_PRIMARY};
                border: none;
                padding: 8px 16px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_CARD};
            }}
        """)
        self.back_button.clicked.connect(self.back_requested.emit)

        title = QLabel("Simulation Results")
        title.setStyleSheet(f"font-size: {Fonts.HEADER}pt; font-weight: bold; "
                          f"color: {Colors.TEXT_PRIMARY};")

        header_layout.addWidget(self.back_button)
        header_layout.addStretch()
        header_layout.addWidget(title)
        header_layout.addStretch()

        layout.addWidget(header)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {Colors.BORDER_SEPARATOR};")
        layout.addWidget(separator)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Container widget
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(GUI.SPACING_XL, GUI.SPACING_XL,
                                            GUI.SPACING_XL, GUI.SPACING_XL)
        container_layout.setSpacing(GUI.SPACING_LG)

        # Success section with gauge and summary cards
        success_section = QWidget()
        success_layout = QHBoxLayout(success_section)
        success_layout.setSpacing(GUI.SPACING_LG)

        # Success gauge
        self.success_gauge = SuccessGauge()
        self.success_gauge.setFixedSize(280, 200)
        success_layout.addWidget(self.success_gauge, 0, Qt.AlignmentFlag.AlignLeft)

        # Summary cards
        cards_layout = QGridLayout()
        cards_layout.setSpacing(GUI.SPACING_MD)

        self.median_card = SummaryCard("Median Balance", "")
        self.average_card = SummaryCard("Average Balance", "")
        self.worst_card = SummaryCard("Worst Case Balance", "")
        self.best_card = SummaryCard("Best Case Balance", "")

        cards_layout.addWidget(self.median_card, 0, 0)
        cards_layout.addWidget(self.average_card, 0, 1)
        cards_layout.addWidget(self.worst_card, 1, 0)
        cards_layout.addWidget(self.best_card, 1, 1)

        success_layout.addLayout(cards_layout)
        success_layout.addStretch()

        container_layout.addWidget(success_section)

        # Chart tabs
        self.chart_tabs = ChartTabs()
        container_layout.addWidget(self.chart_tabs, 1)

        scroll.setWidget(container)
        layout.addWidget(scroll)

        # Placeholder message
        self._show_placeholder(container_layout)

    def _show_placeholder(self, layout: QVBoxLayout) -> None:
        """Show placeholder when no results are available.

        Args:
            layout: Layout to add placeholder to.
        """
        placeholder = QWidget()
        placeholder_layout = QVBoxLayout(placeholder)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("Run a simulation to see results")
        label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12pt;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        placeholder_layout.addWidget(label)
        placeholder_layout.addStretch()

        self._placeholder = placeholder
        layout.addWidget(placeholder)

    def _hide_placeholder(self) -> None:
        """Hide the placeholder widget."""
        if hasattr(self, '_placeholder'):
            self._placeholder.setVisible(False)

    def set_results(self, results: ResultManager) -> None:
        """Update the page with simulation results.

        Args:
            results: ResultManager with simulation data.
        """
        try:
            self._hide_placeholder()

            # Update success gauge
            success_rate = results.get_success_rate()
            self.success_gauge.set_percentage(success_rate)

            # Update summary cards
            stats = results.get_summary_stats()
            from src.formatters import format_currency

            self.median_card.update_value(format_currency(stats["median"]))
            self.average_card.update_value(format_currency(stats["mean"]))
            self.worst_card.update_value(format_currency(stats["min"]))
            self.best_card.update_value(format_currency(stats["max"]))

            # Update charts (this is now deferred and async-safe)
            self.chart_tabs.set_results(results)
        except Exception as e:
            # Log error but don't crash the UI
            import traceback
            print(f"Error in set_results: {e}")
            traceback.print_exc()
