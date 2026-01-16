"""Chart tabs container for simulation visualizations.

This module provides a tabbed container for different
chart views using Matplotlib for stable rendering.

Percentiles Explanation:
- P10: 10th percentile - 10% of outcomes were this value or lower (pessimistic)
- P25: 25th percentile - 25% of outcomes were this value or lower (1st quartile)
- P50: 50th percentile - 50% of outcomes were this value or lower (median)
- P75: 75th percentile - 75% of outcomes were this value or lower (3rd quartile)
- P90: 90th percentile - 90% of outcomes were this value or lower (optimistic)
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel
from PySide6.QtCore import Qt
from typing import Optional

import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.figure import SubplotParams
import matplotlib.pyplot as plt
import matplotlib as mpl

from src.results import ResultManager
from src.constants import Colors, Charts
from src.gui.components.monthly_table import MonthlyTable


# Dark theme colors for matplotlib
DARK_BG = "#1E1E1E"
DARK_GRID = "#3A3A3A"
DARK_TEXT = "#E0E0E0"
DARK_TEXT_DIM = "#A0A0A0"
DARK_LINE_COLORS = {
    10: "#FF6B6B",  # Red for P10 (worst)
    25: "#FFD93D",  # Yellow for P25
    50: "#6BCB77",  # Green for P50 (median)
    75: "#4D96FF",  # Blue for P75
    90: "#9D4EDD",  # Purple for P90 (best)
}


class ChartTabs(QWidget):
    """Tabbed container for chart visualizations.

    Uses Matplotlib for stable chart rendering without
    QGraphicsItem null pointer issues.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the chart tabs.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)

        # State variables
        self._results: Optional[ResultManager] = None
        self._dist_initialized = False
        self._ot_initialized = False

        # Matplotlib figures and canvases
        self._dist_figure = None
        self._dist_canvas = None
        self._dist_ax = None
        self._ot_figure = None
        self._ot_canvas = None
        self._ot_ax = None

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab widget
        self.tabs = QTabWidget()
        # Center-align tabs using setTabBarAutoHide (hides bar when no tabs)
        # and ensure tabs are centered in available space
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {Colors.BG_PRIMARY};
            }}
            QTabBar::tab {{
                background-color: {Colors.BG_SECONDARY};
                color: {Colors.TEXT_SECONDARY};
                border: none;
                padding: 10px 30px;
                margin-right: 2px;
                min-width: 120px;
            }}
            QTabBar::tab:selected {{
                background-color: {Colors.BG_PRIMARY};
                color: {Colors.TEXT_PRIMARY};
            }}
            QTabBar::tab:hover {{
                background-color: {Colors.BG_CARD};
            }}
        """)
        # Center tabs by setting tab bar alignment
        self.tabs.tabBar().setStyleSheet("""
            QTabBar {
                qproperty-drawBase: 0;
            }
        """)

        # Create placeholder labels
        self._dist_placeholder = QLabel("Distribution Chart")
        self._dist_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._dist_placeholder.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; padding: 50px;")

        self._ot_placeholder = QLabel("Over Time Chart")
        self._ot_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._ot_placeholder.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; padding: 50px;")

        self.monthly_table = MonthlyTable()

        # Add tabs
        self.tabs.addTab(self._dist_placeholder, "Distribution")
        self.tabs.addTab(self._ot_placeholder, "Over Time")
        self.tabs.addTab(self.monthly_table, "Monthly Details")

        # Connect tab change signal to lazy initialization
        self.tabs.currentChanged.connect(self._on_tab_changed)

        layout.addWidget(self.tabs)

    def _on_tab_changed(self, index: int) -> None:
        """Handle tab change - initialize chart when tab is first selected.

        Args:
            index: The index of the newly selected tab.
        """
        if index == 0 and not self._dist_initialized:
            self._initialize_distribution_chart()
        elif index == 1 and not self._ot_initialized:
            self._initialize_overtime_chart()

    def _apply_dark_theme(self, ax) -> None:
        """Apply dark theme to matplotlib axis.

        Args:
            ax: Matplotlib axis to style.
        """
        # Set background colors
        ax.set_facecolor(DARK_BG)
        ax.figure.patch.set_facecolor(DARK_BG)

        # Style the spines (axis lines)
        for spine in ax.spines.values():
            spine.set_color(DARK_TEXT_DIM)
            spine.set_linewidth(0.5)

        # Style ticks
        ax.tick_params(colors=DARK_TEXT_DIM, labelsize=9)
        ax.xaxis.label.set_color(DARK_TEXT)
        ax.yaxis.label.set_color(DARK_TEXT)
        ax.title.set_color(DARK_TEXT)

        # Grid
        ax.grid(True, alpha=0.2, color=DARK_GRID, linestyle='-')

        # Legend
        legend = ax.get_legend()
        if legend:
            frame = legend.get_frame()
            frame.set_facecolor(DARK_BG)
            frame.set_edgecolor(DARK_TEXT_DIM)
            for text in legend.get_texts():
                text.set_color(DARK_TEXT)

    def _initialize_distribution_chart(self) -> None:
        """Create the distribution chart widget."""
        self._dist_initialized = True

        # Create matplotlib figure
        self._dist_figure = Figure(
            figsize=(8, 5),
            dpi=100,
            subplotpars=SubplotParams(
                left=0.12, right=0.92, top=0.88, bottom=0.12,
                wspace=0.3, hspace=0.3
            )
        )
        self._dist_canvas = FigureCanvas(self._dist_figure)
        self._dist_ax = self._dist_figure.add_subplot(111)

        # Style with dark theme
        self._dist_ax.set_title(
            "Final Balance Distribution\n(histogram shows all possible outcomes)",
            color=DARK_TEXT, fontsize=13, fontweight='bold', pad=15
        )
        self._dist_ax.set_xlabel("Final Portfolio Balance (CNY) →", color=DARK_TEXT, fontsize=10)
        self._dist_ax.set_ylabel("Frequency (count of outcomes) →", color=DARK_TEXT, fontsize=10)

        self._apply_dark_theme(self._dist_ax)

        # Replace placeholder with chart
        current_index = self.tabs.currentIndex()
        self.tabs.blockSignals(True)
        self.tabs.removeTab(0)
        self.tabs.insertTab(0, self._dist_canvas, "Distribution")
        self.tabs.setCurrentIndex(current_index)
        self.tabs.blockSignals(False)

        # Update with data if available
        if self._results is not None and self._results.is_loaded():
            self._update_distribution()

    def _initialize_overtime_chart(self) -> None:
        """Create the overtime chart widget."""
        self._ot_initialized = True

        # Create matplotlib figure
        self._ot_figure = Figure(
            figsize=(8, 5),
            dpi=100,
            subplotpars=SubplotParams(
                left=0.12, right=0.92, top=0.88, bottom=0.12,
                wspace=0.3, hspace=0.3
            )
        )
        self._ot_canvas = FigureCanvas(self._ot_figure)
        self._ot_ax = self._ot_figure.add_subplot(111)

        # Style with dark theme
        self._ot_ax.set_title(
            "Portfolio Balance Over Time\n(percentile tracks show different outcome scenarios)",
            color=DARK_TEXT, fontsize=13, fontweight='bold', pad=15
        )
        self._ot_ax.set_xlabel("Time (months from start) →", color=DARK_TEXT, fontsize=10)
        self._ot_ax.set_ylabel("Portfolio Balance (CNY) →", color=DARK_TEXT, fontsize=10)

        self._apply_dark_theme(self._ot_ax)

        # Replace placeholder with chart
        current_index = self.tabs.currentIndex()
        self.tabs.blockSignals(True)
        self.tabs.removeTab(1)
        self.tabs.insertTab(1, self._ot_canvas, "Over Time")
        self.tabs.setCurrentIndex(current_index)
        self.tabs.blockSignals(False)

        # Update with data if available
        if self._results is not None and self._results.is_loaded():
            self._update_overtime()

    def set_results(self, results: ResultManager) -> None:
        """Update charts with simulation results.

        Args:
            results: ResultManager with simulation data.
        """
        self._results = results

        if self._results is None or not self._results.is_loaded():
            return

        # Update monthly table (includes initial data fetch)
        self.monthly_table.set_results(self._results)

        # Initialize and update the currently visible chart
        current_index = self.tabs.currentIndex()

        # Distribution tab (index 0)
        if current_index == 0 and not self._dist_initialized:
            self._initialize_distribution_chart()
        elif current_index == 0 and self._dist_initialized:
            self._update_distribution()

        # Over Time tab (index 1)
        elif current_index == 1 and not self._ot_initialized:
            self._initialize_overtime_chart()
        elif current_index == 1 and self._ot_initialized:
            self._update_overtime()

    def _update_distribution(self) -> None:
        """Update the distribution histogram."""
        if not self._dist_initialized or self._dist_ax is None:
            return

        final_balances = self._results.get_final_balances()

        # Clear previous plot
        self._dist_ax.clear()

        # Re-apply title and labels after clear
        self._dist_ax.set_title(
            "Final Balance Distribution\n(histogram shows all possible outcomes)",
            color=DARK_TEXT, fontsize=13, fontweight='bold', pad=15
        )
        self._dist_ax.set_xlabel("Final Portfolio Balance (CNY) →", color=DARK_TEXT, fontsize=10)
        self._dist_ax.set_ylabel("Frequency (count of outcomes) →", color=DARK_TEXT, fontsize=10)
        self._apply_dark_theme(self._dist_ax)

        # Create histogram with dark theme
        n, bins, patches = self._dist_ax.hist(
            final_balances,
            bins=Charts.HISTOGRAM_BINS,
            color="#4A90E2",
            alpha=0.6,
            edgecolor="#2C5F9E"
        )

        # Add percentile lines with descriptions
        stats = self._results.get_summary_stats()
        percentiles = [
            ("P10", stats["p10"], DARK_LINE_COLORS[10], "worst 10%"),
            ("P25", stats["p25"], DARK_LINE_COLORS[25], "1st quartile"),
            ("P50", stats["median"], DARK_LINE_COLORS[50], "median"),
            ("P75", stats["p75"], DARK_LINE_COLORS[75], "3rd quartile"),
            ("P90", stats["p90"], DARK_LINE_COLORS[90], "best 10%"),
        ]

        for name, value, color, desc in percentiles:
            self._dist_ax.axvline(
                value,
                color=color,
                linestyle='--',
                linewidth=2,
                alpha=0.9,
                label=f"{name}: ¥{value:,.0f} ({desc})"
            )

        # Add explanation text box with light text color
        explanation = (
            "Percentiles explain outcomes:\n"
            "• P10: 10% of simulations did worse\n"
            "• P50: 50% did worse, 50% did better (median)\n"
            "• P90: 90% of simulations did worse"
        )
        self._dist_ax.text(
            0.02, 0.98, explanation,
            transform=self._dist_ax.transAxes,
            fontsize=8,
            verticalalignment='top',
            color=DARK_TEXT,
            bbox=dict(boxstyle='round', facecolor='#2A2A2A', alpha=0.8, edgecolor='#444')
        )

        # Redraw
        self._dist_ax.legend(loc='upper right', fontsize=8, facecolor='#2A2A2A', edgecolor='#444', labelcolor=DARK_TEXT)
        self._dist_canvas.draw()

    def _update_overtime(self) -> None:
        """Update the over-time percentile chart."""
        if not self._ot_initialized or self._ot_ax is None:
            return

        # Clear previous plot
        self._ot_ax.clear()

        # Re-apply title and labels after clear
        self._ot_ax.set_title(
            "Portfolio Balance Over Time\n(percentile tracks show different outcome scenarios)",
            color=DARK_TEXT, fontsize=13, fontweight='bold', pad=15
        )
        self._ot_ax.set_xlabel("Time (months from start) →", color=DARK_TEXT, fontsize=10)
        self._ot_ax.set_ylabel("Portfolio Balance (CNY) →", color=DARK_TEXT, fontsize=10)
        self._apply_dark_theme(self._ot_ax)

        # Get percentiles
        percentiles = self._results.get_percentiles([10, 25, 50, 75, 90])
        months = np.arange(self._results.total_months)

        # Plot each percentile line with dark theme colors
        percentile_info = {
            10: (DARK_LINE_COLORS[10], "P10: pessimistic (worst 10%)"),
            25: (DARK_LINE_COLORS[25], "P25: 1st quartile"),
            50: (DARK_LINE_COLORS[50], "P50: median (middle outcome)"),
            75: (DARK_LINE_COLORS[75], "P75: 3rd quartile"),
            90: (DARK_LINE_COLORS[90], "P90: optimistic (best 10%)"),
        }

        for percentile, (color, label) in percentile_info.items():
            self._ot_ax.plot(
                months,
                percentiles[percentile],
                color=color,
                linewidth=2,
                label=label,
                alpha=0.9
            )

        # Fill area between P10 and P90 to show range
        self._ot_ax.fill_between(
            months,
            percentiles[10],
            percentiles[90],
            color=DARK_LINE_COLORS[50],
            alpha=0.1,
            label="80% outcome range (P10-P90)"
        )

        # Add explanation text box at upper LEFT (with bright text color)
        years = self._results.total_months // 12
        explanation = (
            f"Simulation: {self._results.num_paths:,} paths over {years} years\n"
            "• P90 line: best 10% of outcomes\n"
            "• P50 line: median (middle) outcome\n"
            "• P10 line: worst 10% of outcomes\n"
            "• Shaded area: 80% of possible outcomes"
        )
        self._ot_ax.text(
            0.02, 0.77, explanation,
            transform=self._ot_ax.transAxes,
            fontsize=8,
            verticalalignment='top',
            color=DARK_TEXT,
            bbox=dict(boxstyle='round', facecolor='#2A2A2A', alpha=0.9, edgecolor='#444')
        )

        # Legend at upper RIGHT to avoid overlap with explanation
        self._ot_ax.legend(loc='upper right', fontsize=7, facecolor='#2A2A2A', edgecolor='#444', labelcolor=DARK_TEXT)

        # Redraw
        self._ot_canvas.draw()

    def clear(self) -> None:
        """Clear all chart data."""
        self._results = None

        if self._dist_initialized and self._dist_ax is not None:
            self._dist_ax.clear()
            self._dist_canvas.draw()

        if self._ot_initialized and self._ot_ax is not None:
            self._ot_ax.clear()
            self._ot_canvas.draw()
