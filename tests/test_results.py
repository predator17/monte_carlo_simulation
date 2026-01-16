"""Tests for the ResultManager class.

This module contains tests for the ResultManager class that
handles simulation results using Polars LazyFrame.
"""

import pytest
import numpy as np
import polars as pl

from src.results import ResultManager


class TestResultManager:
    """Test ResultManager class."""

    def test_init(self) -> None:
        """Test ResultManager initialization."""
        manager = ResultManager()

        assert not manager.is_loaded()
        assert manager.num_paths == 0
        assert manager.total_months == 0

    def test_store_basic(self) -> None:
        """Test storing basic simulation results."""
        manager = ResultManager()

        balances = np.array([
            [100_000, 110_000, 120_000],
            [90_000, 95_000, 100_000],
        ], dtype=np.float32)

        withdrawals = np.array([5000, 5100, 5200], dtype=np.float32)

        manager.store(
            balances=balances,
            withdrawals=withdrawals,
            initial_balance=100_000,
        )

        assert manager.is_loaded()
        assert manager.num_paths == 2
        assert manager.total_months == 3

    def test_get_balances(self) -> None:
        """Test getting balances array."""
        manager = ResultManager()

        balances = np.array([
            [100_000, 110_000],
            [90_000, 95_000],
        ], dtype=np.float32)

        manager.store(balances=balances, initial_balance=100_000)

        result = manager.balances
        np.testing.assert_array_equal(result, balances)

    def test_get_balances_not_loaded(self) -> None:
        """Test getting balances when no results loaded."""
        manager = ResultManager()

        with pytest.raises(RuntimeError, match="No results loaded"):
            _ = manager.balances

    def test_get_withdrawals(self) -> None:
        """Test getting withdrawals array."""
        manager = ResultManager()

        withdrawals = np.array([5000, 5100, 5200], dtype=np.float32)
        balances = np.zeros((10, 3), dtype=np.float32)

        manager.store(
            balances=balances,
            withdrawals=withdrawals,
            initial_balance=100_000,
        )

        result = manager.withdrawals
        np.testing.assert_array_equal(result, withdrawals)

    def test_get_final_balances(self) -> None:
        """Test getting final balances."""
        manager = ResultManager()

        balances = np.array([
            [100_000, 110_000, 120_000],
            [90_000, 95_000, 100_000],
            [150_000, 160_000, 170_000],
        ], dtype=np.float32)

        manager.store(balances=balances, initial_balance=100_000)

        final = manager.get_final_balances()

        np.testing.assert_array_equal(final, np.array([120_000, 100_000, 170_000], dtype=np.float32))

    def test_get_success_rate(self) -> None:
        """Test success rate calculation."""
        manager = ResultManager()

        # 3 paths, 2 with positive final balance
        balances = np.array([
            [100_000, 110_000, 120_000],
            [100_000, 90_000, 0],  # Depleted
            [100_000, 110_000, 130_000],
        ], dtype=np.float32)

        manager.store(balances=balances, initial_balance=100_000)

        rate = manager.get_success_rate()

        assert rate == pytest.approx(200/3)  # 2 out of 3 positive

    def test_get_summary_stats(self) -> None:
        """Test summary statistics calculation."""
        manager = ResultManager()

        balances = np.array([
            [100_000, 110_000, 120_000],
            [90_000, 95_000, 100_000],
            [150_000, 160_000, 170_000],
        ], dtype=np.float32)

        manager.store(balances=balances, initial_balance=100_000)

        stats = manager.get_summary_stats()

        assert stats["median"] == 120_000
        assert stats["min"] == 100_000
        assert stats["max"] == 170_000
        assert pytest.approx(stats["mean"], 0.01) == 130_000

    def test_get_percentiles(self) -> None:
        """Test percentile calculation."""
        manager = ResultManager()

        # Create predictable data
        balances = np.array([
            [100_000, 110_000, 120_000],  # Path 1 ends at 120k
            [90_000, 95_000, 100_000],    # Path 2 ends at 100k
            [150_000, 160_000, 170_000],  # Path 3 ends at 170k
            [80_000, 85_000, 90_000],     # Path 4 ends at 90k
            [130_000, 140_000, 150_000],  # Path 5 ends at 150k
        ], dtype=np.float32)

        manager.store(balances=balances, initial_balance=100_000)

        percentiles = manager.get_percentiles([20, 50, 80])

        assert 20 in percentiles
        assert 50 in percentiles
        assert 80 in percentiles

        # Check shapes
        assert percentiles[20].shape == (3,)
        assert percentiles[50].shape == (3,)
        assert percentiles[80].shape == (3,)

        # 50th percentile (median) for each month across paths
        # Month 0: [100k, 90k, 150k, 80k, 130k] -> median is 100k
        # Month 1: [110k, 95k, 160k, 85k, 140k] -> median is 110k
        # Month 2: [120k, 100k, 170k, 90k, 150k] -> median is 120k
        assert percentiles[50][0] == pytest.approx(100_000)
        assert percentiles[50][1] == pytest.approx(110_000)
        assert percentiles[50][2] == pytest.approx(120_000)

    def test_get_median_path(self) -> None:
        """Test getting median path."""
        manager = ResultManager()

        balances = np.array([
            [100_000, 110_000, 120_000],
            [90_000, 95_000, 100_000],
            [150_000, 160_000, 170_000],
        ], dtype=np.float32)

        manager.store(balances=balances, initial_balance=100_000)

        median = manager.get_median_path()

        # Median should be computed across paths for each month:
        # Month 0: [100k, 90k, 150k] -> median = 100k
        # Month 1: [110k, 95k, 160k] -> median = 110k
        # Month 2: [120k, 100k, 170k] -> median = 120k
        assert median[0] == pytest.approx(100_000)
        assert median[1] == pytest.approx(110_000)
        assert median[2] == pytest.approx(120_000)

    def test_get_monthly_data(self) -> None:
        """Test getting monthly data for a specific path."""
        manager = ResultManager()

        balances = np.array([
            [100_000, 110_000, 120_000],
            [90_000, 95_000, 100_000],
        ], dtype=np.float32)

        withdrawals = np.array([5000, 5100, 5200], dtype=np.float32)

        manager.store(
            balances=balances,
            withdrawals=withdrawals,
            initial_balance=100_000,
        )

        # Get data for first path
        df = manager.get_monthly_data(path_id=0)

        assert isinstance(df, pl.DataFrame)
        assert len(df) == 3

        # Check columns (note: uses end_balance, not balance)
        assert "period" in df.columns
        assert "end_balance" in df.columns
        assert "change" in df.columns
        assert "return_pct" in df.columns
        assert "withdrawal" in df.columns

    def test_fetch_rows(self) -> None:
        """Test lazy loading row fetching."""
        manager = ResultManager()

        # Create data for 2 years (24 months = 2 year headers + 24 months = 26 rows)
        balances = np.random.randn(100, 24).astype(np.float32) * 10000 + 100_000
        withdrawals = np.full(24, 5000, dtype=np.float32)

        manager.store(
            balances=balances,
            withdrawals=withdrawals,
            initial_balance=100_000,
        )

        # Fetch first batch
        rows = manager.fetch_rows(0, 10, path_id=-1)

        assert len(rows) == 10
        # Row 0 should be "Jan 2026" - no year headers anymore
        assert rows[0]["period"] == "Jan 2026"

    def test_fetch_rows_year_headers(self) -> None:
        """Test that month rows are correctly formatted with year."""
        manager = ResultManager()

        # Create data for 2 years
        balances = np.random.randn(10, 24).astype(np.float32) * 10000 + 100_000
        withdrawals = np.full(24, 5000, dtype=np.float32)

        manager.store(
            balances=balances,
            withdrawals=withdrawals,
            initial_balance=100_000,
        )

        rows = manager.fetch_rows(0, 20, path_id=-1)

        # Row 0 should be "Jan 2026" (no year headers anymore)
        assert rows[0]["period"] == "Jan 2026"
        assert rows[0]["balance"] is not None

        # Row 12 should be "Jan 2027" (13th month = first month of year 2)
        assert rows[12]["period"] == "Jan 2027"
        assert rows[12]["balance"] is not None

    def test_total_row_count(self) -> None:
        """Test total row count calculation."""
        manager = ResultManager()

        # 23 years = 276 months (no year headers anymore)
        balances = np.zeros((10, 276), dtype=np.float32)
        withdrawals = np.zeros(276, dtype=np.float32)

        manager.store(
            balances=balances,
            withdrawals=withdrawals,
            initial_balance=100_000,
        )

        # 23 years * 12 months = 276 (no year headers)
        assert manager.total_row_count == 276

    def test_to_lazyframe(self) -> None:
        """Test conversion to Polars LazyFrame."""
        manager = ResultManager()

        balances = np.array([
            [100_000, 110_000],
            [90_000, 95_000],
        ], dtype=np.float32)

        manager.store(balances=balances, initial_balance=100_000)

        lf = manager.to_lazyframe()

        assert isinstance(lf, pl.LazyFrame)

        # Collect and check
        df = lf.collect()
        assert len(df) == 4  # 2 paths * 2 months
        assert "path_id" in df.columns
        assert "balance" in df.columns

    def test_get_distribution_data(self) -> None:
        """Test getting distribution data."""
        manager = ResultManager()

        balances = np.array([
            [100_000, 110_000, 120_000],
            [90_000, 95_000, 100_000],
            [150_000, 160_000, 170_000],
        ], dtype=np.float32)

        manager.store(balances=balances, initial_balance=100_000)

        df = manager.get_distribution_data()

        assert isinstance(df, pl.DataFrame)
        assert len(df) == 3
        assert "path_id" in df.columns
        assert "final_balance" in df.columns

    def test_clear(self) -> None:
        """Test clearing results."""
        manager = ResultManager()

        balances = np.ones((10, 12), dtype=np.float32)
        manager.store(balances=balances, initial_balance=100_000)

        assert manager.is_loaded()

        manager.clear()

        assert not manager.is_loaded()
        assert manager.num_paths == 0
        assert manager.total_months == 0
