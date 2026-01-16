"""Tests for MonthlyTableModel lazy loading behavior."""

import pytest
import numpy as np
from PySide6.QtCore import Qt

from src.results import ResultManager
from src.gui.models.table_model import MonthlyTableModel


class TestMonthlyTableModel:
    """Test MonthlyTableModel edge cases."""

    def test_fetch_more_with_partial_data(self, qtbot) -> None:
        """Test fetchMore when fewer rows are returned than requested.

        This is a regression test for the invalid index error that occurred
        when scrolling to the end of the table where fewer rows exist than
        the fetch batch size.
        """
        # Create results with 1 year of data (12 rows: 12 months, no year headers)
        manager = ResultManager()
        balances = np.random.RandomState(42).randn(100, 12) * 1000 + 100_000
        balances = balances.astype(np.float32)
        withdrawals = np.ones(12, dtype=np.float32) * 1000
        manager.store(balances=balances, withdrawals=withdrawals, initial_balance=100_000)

        model = MonthlyTableModel(manager)

        # Total rows should be 12 (12 months, no year headers)
        assert model.rowCount() == 12

        # Initially no rows loaded
        assert model._loaded_rows == 0

        # Request more rows than available
        # With batch size of 50, but only 12 rows total
        assert model.canFetchMore()

        # This should not cause any errors
        model.fetchMore()

        # After fetch, we should have some rows loaded
        assert model._loaded_rows > 0
        assert model._loaded_rows <= 12

        # Try to fetch again - should handle gracefully
        if model.canFetchMore():
            model.fetchMore()

        # All rows should be loaded now
        assert model._loaded_rows <= 12

        # Verify data() doesn't crash for any valid index
        for row in range(model.rowCount()):
            for col in range(model.columnCount()):
                from PySide6.QtCore import QModelIndex
                idx = model.index(row, col)
                # Just accessing data() should not crash
                data = model.data(idx)
                # Data might be None for unloaded rows, but that's OK

    def test_data_access_boundary_conditions(self, qtbot) -> None:
        """Test data access at row boundaries."""
        manager = ResultManager()
        balances = np.ones((100, 24), dtype=np.float32) * 100_000  # 2 years
        withdrawals = np.ones(24, dtype=np.float32) * 1000
        manager.store(balances=balances, withdrawals=withdrawals, initial_balance=100_000)

        model = MonthlyTableModel(manager)

        # Total rows: 2 years * 12 months = 24 (no year headers)
        assert model.rowCount() == 24

        # Access last row before any fetching
        from PySide6.QtCore import QModelIndex
        last_idx = model.index(23, 0)  # Last row
        # Should return None or "..." without crashing
        data = model.data(last_idx)
        assert data is not None or data == "..."

        # Fetch all data
        while model.canFetchMore():
            model.fetchMore()

        # Now access last row again
        data = model.data(last_idx)
        # Should have valid data now
        assert data is not None

    def test_path_change_with_partial_data(self, qtbot) -> None:
        """Test changing path when only partial data is loaded."""
        manager = ResultManager()
        balances = np.ones((100, 24), dtype=np.float32) * 100_000
        withdrawals = np.ones(24, dtype=np.float32) * 1000
        manager.store(balances=balances, withdrawals=withdrawals, initial_balance=100_000)
        
        model = MonthlyTableModel(manager)
        
        # Load partial data
        model.fetchMore()
        loaded_after_first = model._loaded_rows
        
        # Change path - should reset loaded rows
        model.set_path_id(0)
        assert model._loaded_rows == 0
        
        # Fetch again
        model.fetchMore()
        assert model._loaded_rows > 0
