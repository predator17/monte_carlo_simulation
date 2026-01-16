"""Monthly table component for displaying simulation details.

This module provides the table view component for displaying
monthly simulation data with lazy loading.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableView, QComboBox, QFrame, QHeaderView, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItemModel
from typing import Optional
import datetime

from src.results import ResultManager
from src.constants import Colors, GUI
from src.gui.models.table_model import MonthlyTableModel
from src.gui.components.calculation_help_dialog import CalculationHelpDialog


class MonthlyTable(QWidget):
    """Table view for monthly simulation details.

    Displays monthly data in a table with:
    - Path selector (Median, or specific path)
    - Year selector (All years, or specific year)
    - Lazy loading for performance
    - Color-coded values (green/red for gains/losses)

    Signals:
        path_changed: Emitted when selected path changes.
    """

    path_changed = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the monthly table.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)

        # Store references
        self._results: Optional[ResultManager] = None
        self._model: Optional[MonthlyTableModel] = None
        self._current_year = datetime.datetime.now().year

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(GUI.SPACING_MD)

        # Header with controls
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Path selector
        path_label = QLabel("Showing:")
        path_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")

        self.path_selector = QComboBox()
        self.path_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_INPUT};
                border-radius: {GUI.BORDER_RADIUS_SM}px;
                padding: 4px 8px;
            }}
            QComboBox:focus {{
                border: 1px solid {Colors.BORDER_FOCUS};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
        """)
        self.path_selector.addItems(["Median Path"])
        self.path_selector.currentIndexChanged.connect(self._on_path_changed)

        # Year selector
        year_label = QLabel("Year:")
        year_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; margin-left: 20px;")

        self.year_selector = QComboBox()
        self.year_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_INPUT};
                border-radius: {GUI.BORDER_RADIUS_SM}px;
                padding: 4px 8px;
                min-width: 120px;
            }}
            QComboBox:focus {{
                border: 1px solid {Colors.BORDER_FOCUS};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
        """)
        self.year_selector.addItem("All Years")
        self.year_selector.currentIndexChanged.connect(self._on_year_changed)

        # Help button (before stretch so it's always visible)
        self.help_button = QPushButton("?")
        self.help_button.setFixedSize(40, 40)
        self.help_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_BLUE};
                color: white;
                border: 2px solid {Colors.ACCENT_BLUE};
                border-radius: 20px;
                font-weight: bold;
                font-size: 18pt;
            }}
            QPushButton:hover {{
                background-color: {Colors.ACCENT_BLUE};
                border: 2px solid white;
            }}
        """)
        self.help_button.setToolTip("Show calculation formulas")
        self.help_button.clicked.connect(self._show_help_dialog)

        header_layout.addWidget(path_label)
        header_layout.addWidget(self.path_selector)
        header_layout.addWidget(year_label)
        header_layout.addWidget(self.year_selector)
        header_layout.addWidget(self.help_button)  # Put before stretch
        header_layout.addStretch()

        layout.addWidget(header)

        # Table view - wrap in a container for centering
        table_container = QWidget()
        table_container_layout = QHBoxLayout(table_container)
        table_container_layout.setContentsMargins(10, 0, 10, 0)

        # Small spacers for slight centering
        table_container_layout.addStretch(1)

        self.table_view = QTableView()
        self.table_view.setMinimumSize(1600, 500)  # Wider table for full numbers
        self.table_view.setStyleSheet(f"""
            QTableView {{
                background-color: {Colors.BG_PRIMARY};
                alternate-background-color: {Colors.BG_SECONDARY};
                color: {Colors.TEXT_PRIMARY};
                gridline-color: {Colors.BORDER_SEPARATOR};
                border: none;
                selection-background-color: {Colors.ACCENT_BLUE};
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
        """)

        # Configure table for performance
        self.table_view.setProperty("uniformRowHeights", True)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.verticalHeader().setDefaultSectionSize(GUI.TABLE_ROW_HEIGHT)

        # Set initial column widths with auto-resize
        self._setup_columns()

        table_container_layout.addWidget(self.table_view)

        # Small spacers for slight centering
        table_container_layout.addStretch(1)

        layout.addWidget(table_container)

        # Info label
        self.info_label = QLabel()
        self.info_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 9pt;")
        self.info_label.setText("Run a simulation to see details")
        layout.addWidget(self.info_label)

    def _setup_columns(self) -> None:
        """Set up table column widths with auto-resize."""
        # Set initial column widths (will auto-resize when data is loaded)
        # Columns: Period, Balance, Change, Portfolio Return, Cash Return, Withdrawal, Income
        # Much wider columns to show full numbers with 4 decimal places
        column_widths = [130, 220, 200, 150, 120, 180, 180]
        for i, width in enumerate(column_widths):
            self.table_view.setColumnWidth(i, width)

        # Enable column resize to contents
        self.table_view.resizeColumnsToContents()

    def _on_path_changed(self, index: int) -> None:
        """Handle path selector change.

        Args:
            index: Selected index.
        """
        if self._model is None:
            return

        if index == 0:
            # Median path
            self._model.set_path_id(-1)
        else:
            # Specific path (1-indexed in combo, 0-indexed in model)
            self._model.set_path_id(index - 1)

        self.path_changed.emit(self._model._path_id)

        # Update info label
        self._update_info_label()

        # Fetch all data after path change
        while self._model.canFetchMore():
            self._model.fetchMore()

    def _on_year_changed(self, index: int) -> None:
        """Handle year selector change.

        Args:
            index: Selected index (0 = All Years, 1-N = specific year).
        """
        if self._model is None:
            return

        if index == 0:
            # All years
            self._model.set_year_filter(None)
        else:
            # Specific year (index-1 because 0 is "All Years")
            self._model.set_year_filter(index - 1)

        # Update info label
        self._update_info_label()

        # Fetch all data after year change
        while self._model.canFetchMore():
            self._model.fetchMore()

    def _update_info_label(self) -> None:
        """Update the info label with current selection."""
        if self._results is None or not self._results.is_loaded():
            return

        path_id = self._model._path_id if self._model else -1
        total_months = self._results.total_months
        num_years = total_months // 12

        if path_id == -1:
            text = f"Showing median path across {num_years} years ({total_months} months)"
        else:
            text = f"Showing path {path_id + 1} of {self._results.num_paths} across {num_years} years"

        self.info_label.setText(text)

    def set_results(self, results: ResultManager) -> None:
        """Set the simulation results.

        Args:
            results: ResultManager with simulation data.
        """
        self._results = results

        # Update path selector first (before creating model to avoid triggering set_path_id)
        self.path_selector.blockSignals(True)
        self.path_selector.clear()
        self.path_selector.addItem("Median Path")

        # Add ALL individual simulation paths
        if results.is_loaded() and results.num_paths > 0:
            for i in range(results.num_paths):
                self.path_selector.addItem(f"Path {i + 1}")

        self.path_selector.blockSignals(False)

        # Update year selector
        self.year_selector.blockSignals(True)
        self.year_selector.clear()
        self.year_selector.addItem("All Years")

        if results.is_loaded():
            num_years = results.total_months // 12
            for year_idx in range(num_years):
                calendar_year = self._current_year + year_idx
                self.year_selector.addItem(f"Year {year_idx + 1} ({calendar_year})")

            # Default to Year 1 instead of All Years
            if num_years > 0:
                self.year_selector.setCurrentIndex(1)

        self.year_selector.blockSignals(False)

        # Create model AFTER selectors are updated
        self._model = MonthlyTableModel(results)
        self._model.set_current_year(self._current_year)
        # Default to Year 1 (year_filter=0)
        if results.is_loaded() and results.total_months >= 12:
            self._model.set_year_filter(0)
        self.table_view.setModel(self._model)

        # Update info label
        if results.is_loaded():
            num_years = results.total_months // 12
            self.info_label.setText(f"Showing median path for Year 1 of {num_years} years (12 months)")
        else:
            self.info_label.setText("No simulation data available")

        # Trigger initial data fetch (fetch all rows at once for simplicity)
        if self._model is not None:
            while self._model.canFetchMore():
                self._model.fetchMore()
            # Auto-resize columns after data is loaded
            self.table_view.resizeColumnsToContents()

    def refresh(self) -> None:
        """Refresh the table data."""
        if self._model is not None:
            self._model.refresh()
            self._update_info_label()

    def _show_help_dialog(self) -> None:
        """Show the calculation help dialog with LaTeX formulas."""
        dialog = CalculationHelpDialog(self)
        dialog.exec()
