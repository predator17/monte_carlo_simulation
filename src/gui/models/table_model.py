"""Lazy-loading table model for monthly simulation data.

This module provides a QAbstractTableModel that implements Qt's
fetchMore/canFetchMore pattern for efficient display of large datasets.
"""

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtGui import QBrush, QColor
from typing import Any, Optional
import numpy as np

from src.results import ResultManager
from src.constants import Colors, GUI


class MonthlyTableModel(QAbstractTableModel):
    """Lazy-loading table model for simulation results.

    Only loads rows as they are needed for display.
    Implements Qt's fetchMore/canFetchMore pattern for handling
    large datasets (2.76M+ cells) without performance degradation.

    The table displays:
    - Period (Year/Month labels)
    - Balance (End of month balance)
    - Change (Monthly change amount - how much balance changed from previous month)
    - Return (Monthly return percentage)
    - Withdrawal (Monthly withdrawal)
    - Income (Monthly income added to portfolio)
    """

    COLUMNS = ["Period", "Balance", "Change", "Portfolio Return", "Cash Return", "Withdrawal", "Income"]

    def __init__(self, result_manager: ResultManager, parent: Optional[Any] = None):
        """Initialize the table model.

        Args:
            result_manager: ResultManager with simulation data.
            parent: Parent object.
        """
        super().__init__(parent)
        self._results = result_manager
        self._loaded_rows = 0
        self._fetch_batch_size = GUI.TABLE_FETCH_BATCH_SIZE
        self._row_cache = {}
        self._path_id = -1  # -1 for median path
        self._year_filter = None  # None = all years, 0-N = specific year
        self._current_year = 2026  # Starting calendar year

    def set_path_id(self, path_id: int) -> None:
        """Set which path to display data for.

        Args:
            path_id: Path index (-1 for median).
        """
        if path_id != self._path_id:
            # Use beginResetModel/endResetModel when entire data changes
            # This tells the view to completely reset its understanding
            self.beginResetModel()
            self._path_id = path_id
            self._loaded_rows = 0
            self._row_cache = {}
            self.endResetModel()

    def set_year_filter(self, year_filter: int | None) -> None:
        """Set which year to display data for.

        Args:
            year_filter: Year index (0-N for specific year, None for all).
        """
        if year_filter != self._year_filter:
            self.beginResetModel()
            self._year_filter = year_filter
            self._loaded_rows = 0
            self._row_cache = {}
            self.endResetModel()

    def set_current_year(self, current_year: int) -> None:
        """Set the starting calendar year for display.

        Args:
            current_year: The starting calendar year (e.g., 2026).
        """
        self._current_year = current_year
        # Refresh the display with new year labels
        self._loaded_rows = 0
        self._row_cache = {}

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return total row count (not loaded count).

        Args:
            parent: Parent index (unused).

        Returns:
            Total number of rows (12 months per year, no year headers).
        """
        if not self._results.is_loaded():
            return 0

        # If filtering by specific year, only count rows for that year
        if self._year_filter is not None:
            # Check if the filtered year exists
            num_years = self._results.total_months // 12
            if self._year_filter >= num_years:
                return 0
            # Check if it's a partial year (less than 12 months)
            remaining_months = self._results.total_months - (self._year_filter * 12)
            return min(12, remaining_months)

        # Otherwise return total months (no year headers)
        return self._results.total_months

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Return column count.

        Args:
            parent: Parent index (unused).

        Returns:
            Number of columns.
        """
        return len(self.COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return data for given index.

        Args:
            index: Model index.
            role: Data role.

        Returns:
            Data for the role, or None if not available.
        """
        if not index.isValid():
            return None

        row, col = index.row(), index.column()

        # Ensure row is loaded
        if row >= self._loaded_rows:
            if role == Qt.ItemDataRole.DisplayRole:
                return "..."
            return None

        # Get cached data
        row_data = self._get_cached_data(row, col)

        if role == Qt.ItemDataRole.DisplayRole:
            # Format the data for display
            return self._format_data(row_data, col)
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            # Center-align all data
            return Qt.AlignmentFlag.AlignCenter
        elif role == Qt.ItemDataRole.BackgroundRole:
            # Year-based alternating colors for visual separation
            # Group rows by year (12 months per year)
            year_num = row // 12
            if year_num % 2 == 1:
                # Darker background for even-numbered years
                return QBrush(QColor(Colors.BG_SECONDARY))
            # Odd-numbered years get default background
        elif role == Qt.ItemDataRole.ForegroundRole:
            value = row_data
            if value is None or value == "":
                return None
            if col in [2, 3]:  # Change and Return columns
                # Color based on value (RED for positive/increase, GREEN for negative/decrease)
                if isinstance(value, str):
                    value = value.replace("+", "").replace("%", "").replace("¥", "").replace(",", "")
                    try:
                        val = float(value)
                    except ValueError:
                        return None
                    else:
                        if val > 0:
                            # Positive value (increase) -> RED
                            return QBrush(QColor(Colors.SUCCESS_DANGER))
                        elif val < 0:
                            # Negative value (decrease) -> GREEN
                            return QBrush(QColor(Colors.SUCCESS_HIGH))
                # String-based fallback
                if "-" in str(value):
                    # Negative -> GREEN
                    return QBrush(QColor(Colors.SUCCESS_HIGH))
                else:
                    # Positive -> RED
                    return QBrush(QColor(Colors.SUCCESS_DANGER))
        return None

    def _format_data(self, value: Any, col: int) -> str | None:
        """Format data for display with exact numbers (4 decimal places).

        Args:
            value: The value to format.
            col: Column index.

        Returns:
            Formatted string or None.
        """
        if value is None:
            return None

        # Convert column name to data key (lowercase with underscores)
        col_name = self.COLUMNS[col].lower().replace(" ", "_")

        if col_name == "period":
            return str(value)
        elif col_name == "balance":
            # Show exact number with 4 decimal places
            val = float(value)
            return f"{val:,.4f}"
        elif col_name == "change":
            # Show exact number with 4 decimal places and sign
            val = float(value)
            sign = "+" if val >= 0 else ""
            return f"{sign}{val:,.4f}"
        elif col_name == "return" or col_name == "portfolio_return" or col_name == "cash_return":
            # Show percentage with 4 decimal places
            val = float(value)
            return f"{val:.4f}%"
        elif col_name == "withdrawal" or col_name == "income":
            # Show exact number with 4 decimal places
            val = float(value)
            return f"{val:,.4f}"

        return str(value)

    def _get_cached_data(self, row: int, col: int) -> Any:
        """Get cached data for a specific cell.

        Args:
            row: Row index.
            col: Column index.

        Returns:
            Cached cell data.
        """
        if row not in self._row_cache:
            return None
        # Convert column name to data key (lowercase with underscores)
        # "Portfolio Return" -> "portfolio_return"
        col_name = self.COLUMNS[col].lower().replace(" ", "_")
        return self._row_cache[row].get(col_name)

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Return header data.

        Args:
            section: Section index.
            orientation: Header orientation.
            role: Data role.

        Returns:
            Header data.
        """
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            return self.COLUMNS[section]
        elif (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.BackgroundRole
        ):
            return QBrush(QColor(Colors.BG_CARD))
        elif (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.ForegroundRole
        ):
            return QBrush(QColor(Colors.TEXT_SECONDARY))
        return None

    def canFetchMore(self, parent: QModelIndex = QModelIndex()) -> bool:
        """Check if more rows can be fetched.

        Args:
            parent: Parent index (unused).

        Returns:
            True if more rows can be fetched.
        """
        if not self._results.is_loaded():
            return False
        return self._loaded_rows < self.rowCount()

    def fetchMore(self, parent: QModelIndex = QModelIndex()) -> None:
        """Load next batch of rows.

        Args:
            parent: Parent index (unused).
        """
        if not self._results.is_loaded():
            return

        remaining = self.rowCount() - self._loaded_rows
        items_to_fetch = min(remaining, self._fetch_batch_size)

        # Fetch from result manager FIRST
        # fetch_rows may return fewer rows than requested (e.g., at end of data)
        new_data = self._results.fetch_rows(
            self._loaded_rows, items_to_fetch, self._path_id,
            self._year_filter, self._current_year
        )

        # Use actual count of rows fetched
        actual_fetched = len(new_data)
        if actual_fetched == 0:
            return  # Nothing to fetch

        self.beginInsertRows(
            parent,
            self._loaded_rows,
            self._loaded_rows + actual_fetched - 1
        )

        self._row_cache.update(new_data)
        self._loaded_rows += actual_fetched

        self.endInsertRows()

    def refresh(self) -> None:
        """Refresh the model data."""
        self._loaded_rows = 0
        self._row_cache = {}
        self.layoutChanged.emit()
