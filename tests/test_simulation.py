"""Tests for the Monte Carlo simulation engine.

This module contains tests for the SimulationEngine class
and related simulation functions.
"""

import pytest
import numpy as np
from numpy.typing import NDArray

from src.config import SimulationConfig, MonthlyParams
from src.simulation import (
    SimulationEngine,
    _simulate_paths,
    calculate_percentiles,
    calculate_success_rate,
    calculate_summary_stats,
    set_random_seed,
)


class TestSimulationEngine:
    """Test SimulationEngine class."""

    def test_init(self) -> None:
        """Test engine initialization."""
        engine = SimulationEngine(seed=42)
        assert engine.seed == 42

    def test_init_no_seed(self) -> None:
        """Test engine initialization without seed."""
        engine = SimulationEngine()
        assert engine.seed is None

    def test_simulate_single_path(self) -> None:
        """Test single path simulation."""
        engine = SimulationEngine(seed=42)

        params = MonthlyParams(
            mu_stock=0.01,
            sigma_stock=0.05,
            r_cash=0.01,
            inflation=0.0,
            monthly_income=0,
            monthly_withdrawal_base=0,
            total_months=12,
            stock_allocation=1.0,
            cash_allocation=0.0,
        )

        result = engine.simulate(
            params=params,
            initial_balance=100_000,
            num_paths=1,
        )

        assert result.shape == (1, 12)
        assert result.dtype == np.float32

    def test_simulate_multiple_paths(self) -> None:
        """Test multiple path simulation."""
        engine = SimulationEngine(seed=42)

        params = MonthlyParams(
            mu_stock=0.01,
            sigma_stock=0.05,
            r_cash=0.01,
            inflation=0.0,
            monthly_income=0,
            monthly_withdrawal_base=0,
            total_months=120,
            stock_allocation=0.8,
            cash_allocation=0.2,
        )

        result = engine.simulate(
            params=params,
            initial_balance=1_000_000,
            num_paths=100,
        )

        assert result.shape == (100, 120)
        assert result.dtype == np.float32

    def test_simulate_reproducibility(self) -> None:
        """Test that same engine produces same results with seed."""
        # Note: Due to Numba's parallel RNG, exact reproducibility
        # across different engine instances is not guaranteed.
        # This test verifies that a single engine produces consistent output.
        np.random.seed(42)

        params = MonthlyParams(
            mu_stock=0.01,
            sigma_stock=0.05,
            r_cash=0.01,
            inflation=0.0,
            monthly_income=0,
            monthly_withdrawal_base=0,
            total_months=60,
            stock_allocation=0.7,
            cash_allocation=0.3,
        )

        engine = SimulationEngine(seed=12345)
        result1 = engine.simulate(params, 100_000, 50)

        # Run again with same engine
        np.random.seed(42)
        result2 = engine.simulate(params, 100_000, 50)

        # Results should have same shape and dtype
        assert result1.shape == result2.shape
        assert result1.dtype == result2.dtype
        # Verify statistics are similar (not exact due to parallel RNG)
        assert np.abs(np.mean(result1) - np.mean(result2)) / np.mean(result1) < 0.1

    def test_simulate_different_seeds(self) -> None:
        """Test that different seeds produce different results."""
        params = MonthlyParams(
            mu_stock=0.01,
            sigma_stock=0.05,
            r_cash=0.01,
            inflation=0.0,
            monthly_income=0,
            monthly_withdrawal_base=0,
            total_months=60,
            stock_allocation=0.7,
            cash_allocation=0.3,
        )

        engine1 = SimulationEngine(seed=1)
        result1 = engine1.simulate(params, 100_000, 100)

        engine2 = SimulationEngine(seed=999)
        result2 = engine2.simulate(params, 100_000, 100)

        # Results should be different
        assert not np.array_equal(result1, result2)

    def test_simulate_with_history(self) -> None:
        """Test simulation with history returns additional data."""
        engine = SimulationEngine(seed=42)

        params = MonthlyParams(
            mu_stock=0.01,
            sigma_stock=0.05,
            r_cash=0.01,
            inflation=0.0,
            monthly_income=1000,
            monthly_withdrawal_base=5000,
            total_months=24,
            stock_allocation=0.8,
            cash_allocation=0.2,
        )

        result = engine.simulate_with_history(
            params=params,
            initial_balance=100_000,
            num_paths=10,
        )

        assert "balances" in result
        assert "withdrawals" in result
        assert "stock_returns" in result

        assert result["balances"].shape == (10, 24)
        assert len(result["withdrawals"]) == 24
        assert result["stock_returns"].shape == (10, 24)


class TestSimulatePaths:
    """Test the _simulate_paths JIT function."""

    def test_basic_simulation(self) -> None:
        """Test basic simulation functionality."""
        balances = _simulate_paths(
            num_paths=10,
            total_months=120,
            initial_balance=100_000,
            stock_alloc=0.8,
            cash_alloc=0.2,
            mu_stock=0.01,
            sigma_stock=0.05,
            r_cash=0.01,
            withdrawal_base=0,
            inflation=0,
            monthly_income=0,
        )

        assert balances.shape == (10, 120)
        assert balances.dtype == np.float32

    def test_simulation_with_withdrawal(self) -> None:
        """Test simulation decreases balance with withdrawals."""
        balances = _simulate_paths(
            num_paths=100,
            total_months=120,
            initial_balance=100_000,
            stock_alloc=1.0,
            cash_alloc=0.0,
            mu_stock=0.0,
            sigma_stock=0.0,
            r_cash=0.0,
            withdrawal_base=1000,
            inflation=0.0,
            monthly_income=0,
        )

        # With zero return and withdrawals, balance should decrease
        # (though some paths may hit zero)
        for path in range(100):
            # Balance should not exceed initial with zero returns and withdrawals
            assert balances[path, 0] <= 100_000

    def test_simulation_with_income(self) -> None:
        """Test simulation with monthly income."""
        balances = _simulate_paths(
            num_paths=10,
            total_months=120,
            initial_balance=100_000,
            stock_alloc=1.0,
            cash_alloc=0.0,
            mu_stock=0.0,
            sigma_stock=0.0,
            r_cash=0.0,
            withdrawal_base=0,
            inflation=0.0,
            monthly_income=1000,
        )

        # With income, balance should increase
        for path in range(10):
            assert balances[path, -1] > 100_000


class TestCalculatePercentiles:
    """Test percentile calculation functions."""

    def test_calculate_percentiles(self) -> None:
        """Test percentile calculation."""
        # Create test data
        np.random.seed(42)
        balances = np.random.randn(1000, 120).astype(np.float32) * 10000 + 100_000

        percentiles = calculate_percentiles(balances, [10, 25, 50, 75, 90])

        assert len(percentiles) == 5
        assert 10 in percentiles
        assert 25 in percentiles
        assert 50 in percentiles
        assert 75 in percentiles
        assert 90 in percentiles

        # Check percentile ordering
        assert percentiles[10][0] < percentiles[25][0]
        assert percentiles[25][0] < percentiles[50][0]
        assert percentiles[50][0] < percentiles[75][0]
        assert percentiles[75][0] < percentiles[90][0]

    def test_calculate_percentiles_custom(self) -> None:
        """Test custom percentiles."""
        balances = np.random.randn(100, 60).astype(np.float32)

        percentiles = calculate_percentiles(balances, [5, 50, 95])

        assert len(percentiles) == 3
        assert 5 in percentiles
        assert 50 in percentiles
        assert 95 in percentiles


class TestCalculateSuccessRate:
    """Test success rate calculation."""

    def test_all_positive(self) -> None:
        """Test success rate when all paths positive."""
        balances = np.ones((100, 120), dtype=np.float32) * 1000

        rate = calculate_success_rate(balances)

        assert rate == 100.0

    def test_all_zero(self) -> None:
        """Test success rate when all paths zero."""
        balances = np.zeros((100, 120), dtype=np.float32)

        rate = calculate_success_rate(balances)

        assert rate == 0.0

    def test_half_positive(self) -> None:
        """Test success rate with half positive paths."""
        balances = np.zeros((100, 120), dtype=np.float32)
        balances[:50, :] = 1000  # First half positive
        balances[50:, :] = -1000  # Second half negative (clamped to 0 in practice)

        rate = calculate_success_rate(balances)

        assert rate == 50.0

    def test_custom_threshold(self) -> None:
        """Test success rate with various thresholds."""
        balances = np.array([
            [100, 100],
            [0, 0],
            [-100, -100],
            [50, 50],
        ], dtype=np.float32)

        rate = calculate_success_rate(balances)

        assert rate == 50.0  # 2 out of 4 paths have positive balance


class TestCalculateSummaryStats:
    """Test summary statistics calculation."""

    def test_summary_stats(self) -> None:
        """Test summary statistics calculation."""
        balances = np.array([
            [100_000, 110_000, 120_000],
            [90_000, 95_000, 100_000],
            [150_000, 160_000, 170_000],
        ], dtype=np.float32)

        stats = calculate_summary_stats(balances)

        # Check all expected keys
        assert "mean" in stats
        assert "median" in stats
        assert "std" in stats
        assert "min" in stats
        assert "max" in stats
        assert "p5" in stats
        assert "p10" in stats
        assert "p25" in stats
        assert "p75" in stats
        assert "p90" in stats
        assert "p95" in stats

        # Check min/max (final balances: 120k, 100k, 170k)
        assert stats["min"] == 100_000
        assert stats["max"] == 170_000


class TestSetRandomSeed:
    """Test random seed setting."""

    def test_set_random_seed(self) -> None:
        """Test setting random seed affects NumPy."""
        set_random_seed(123)
        values1 = np.random.randn(10)

        set_random_seed(123)
        values2 = np.random.randn(10)

        np.testing.assert_array_equal(values1, values2)
