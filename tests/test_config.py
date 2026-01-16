"""Tests for configuration classes.

This module contains tests for the SimulationConfig and MonthlyParams classes.
"""

import pytest
import math
from src.config import SimulationConfig, MonthlyParams


class TestSimulationConfig:
    """Test SimulationConfig validation and conversion."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = SimulationConfig()

        assert config.initial_balance == 1_800_000
        assert config.monthly_withdrawal == 10_000
        assert config.stock_allocation == 90
        assert config.time_horizon_years == 23
        assert config.expected_return == 10
        assert config.annual_income == 13_000
        assert config.stock_volatility == 10
        assert config.cash_return == 1.15
        assert config.inflation_rate == 3
        assert config.num_paths == 10_000

    def test_cash_allocation_property(self) -> None:
        """Test cash allocation calculation."""
        config = SimulationConfig(stock_allocation=70)
        assert config.cash_allocation == 30

        config = SimulationConfig(stock_allocation=100)
        assert config.cash_allocation == 0

    def test_total_months_property(self) -> None:
        """Test total months calculation."""
        config = SimulationConfig(time_horizon_years=10)
        assert config.total_months == 120

        config = SimulationConfig(time_horizon_years=23)
        assert config.total_months == 276

    def test_stock_allocation_validation(self) -> None:
        """Test stock allocation validation."""
        # Valid values
        SimulationConfig(stock_allocation=0)
        SimulationConfig(stock_allocation=50)
        SimulationConfig(stock_allocation=100)

        # Invalid values
        with pytest.raises(ValueError):
            SimulationConfig(stock_allocation=-1)

        with pytest.raises(ValueError):
            SimulationConfig(stock_allocation=101)

    def test_to_monthly_params(self) -> None:
        """Test conversion to monthly parameters."""
        config = SimulationConfig(
            expected_return=6,      # 6% annual
            stock_volatility=12,    # 12% annual
            cash_return=3,          # 3% annual
            inflation_rate=2,       # 2% annual
            annual_income=12000,    # 12,000 annual
            monthly_withdrawal=5000,
            time_horizon_years=20,
            stock_allocation=80,
        )

        monthly = config.to_monthly_params()

        assert monthly.total_months == 240
        assert monthly.stock_allocation == 0.8
        assert monthly.cash_allocation == 0.2
        assert monthly.monthly_income == 1000  # 12000 / 12
        assert monthly.monthly_withdrawal_base == 5000

        # Check monthly return conversion using geometric mean
        # (1 + 0.06)^(1/12) - 1 ≈ 0.00487
        expected_mu = (1 + 0.06) ** (1 / 12) - 1
        assert math.isclose(monthly.mu_stock, expected_mu, rel_tol=1e-10)

        # Check monthly volatility using square root of time
        # 0.12 / sqrt(12) ≈ 0.03464
        expected_sigma = 0.12 / math.sqrt(12)
        assert math.isclose(monthly.sigma_stock, expected_sigma, rel_tol=1e-10)

        # Check cash return
        expected_r = (1 + 0.03) ** (1 / 12) - 1
        assert math.isclose(monthly.r_cash, expected_r, rel_tol=1e-10)

        # Check inflation
        expected_inf = (1 + 0.02) ** (1 / 12) - 1
        assert math.isclose(monthly.inflation, expected_inf, rel_tol=1e-10)

    def test_from_preset_conservative(self) -> None:
        """Test conservative preset configuration."""
        config = SimulationConfig.from_preset("conservative")

        assert config.stock_allocation == 60
        assert config.expected_return == 4
        assert config.stock_volatility == 8
        assert config.monthly_withdrawal == 8_000

    def test_from_preset_balanced(self) -> None:
        """Test balanced preset configuration."""
        config = SimulationConfig.from_preset("balanced")

        assert config.stock_allocation == 80
        assert config.expected_return == 5
        assert config.stock_volatility == 10
        assert config.monthly_withdrawal == 10_000

    def test_from_preset_aggressive(self) -> None:
        """Test aggressive preset configuration."""
        config = SimulationConfig.from_preset("aggressive")

        assert config.stock_allocation == 95
        assert config.expected_return == 6
        assert config.stock_volatility == 14
        assert config.monthly_withdrawal == 12_000

    def test_from_preset_invalid(self) -> None:
        """Test invalid preset name raises error."""
        with pytest.raises(ValueError, match="Unknown preset"):
            SimulationConfig.from_preset("invalid")


class TestMonthlyParams:
    """Test MonthlyParams class."""

    def test_get_withdrawal_no_inflation(self) -> None:
        """Test withdrawal calculation with zero inflation."""
        params = MonthlyParams(
            mu_stock=0.01,
            sigma_stock=0.05,
            r_cash=0.01,
            inflation=0.0,
            monthly_income=1000,
            monthly_withdrawal_base=5000,
            total_months=120,
            stock_allocation=0.8,
            cash_allocation=0.2,
        )

        # All months should have same withdrawal with no inflation
        for month in range(120):
            assert params.get_withdrawal(month) == 5000

    def test_get_withdrawal_with_inflation(self) -> None:
        """Test withdrawal calculation with inflation."""
        params = MonthlyParams(
            mu_stock=0.01,
            sigma_stock=0.05,
            r_cash=0.01,
            inflation=0.01,  # 1% monthly
            monthly_income=1000,
            monthly_withdrawal_base=5000,
            total_months=12,
            stock_allocation=0.8,
            cash_allocation=0.2,
        )

        # First month
        assert params.get_withdrawal(0) == 5000

        # Second month (1% inflation)
        assert math.isclose(params.get_withdrawal(1), 5000 * 1.01)

        # 12th month
        expected = 5000 * (1.01 ** 11)
        assert math.isclose(params.get_withdrawal(11), expected)

    def test_withdrawal_grows_over_time(self) -> None:
        """Test that withdrawals increase with inflation."""
        params = MonthlyParams(
            mu_stock=0.01,
            sigma_stock=0.05,
            r_cash=0.01,
            inflation=0.005,  # 0.5% monthly
            monthly_income=1000,
            monthly_withdrawal_base=5000,
            total_months=24,
            stock_allocation=0.8,
            cash_allocation=0.2,
        )

        for month in range(23):
            assert params.get_withdrawal(month + 1) > params.get_withdrawal(month)
