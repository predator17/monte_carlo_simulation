"""Configuration classes for the Monte Carlo simulation.

This module uses Pydantic for type-safe configuration with validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import ClassVar
import math


class SimulationConfig(BaseModel):
    """Configuration for Monte Carlo simulation.

    All monetary values are in CNY (Chinese Yuan). Percentages are
    expressed as actual numbers (e.g., 5 for 5%, not 0.05).

    Attributes:
        initial_balance: Starting portfolio amount in CNY.
        monthly_withdrawal: Base monthly withdrawal amount in CNY.
        stock_allocation: Percentage of portfolio allocated to stocks (0-100).
        time_horizon_years: Investment duration in years.
        expected_return: Expected annual stock return percentage.
        annual_income: Fixed annual income added to portfolio.
        stock_volatility: Annual stock volatility (standard deviation) percentage.
        cash_return: Fixed annual cash return percentage.
        inflation_rate: Annual inflation rate percentage.
        num_paths: Number of Monte Carlo simulation paths.
    """

    # Basic parameters (always visible in GUI)
    initial_balance: float = Field(gt=0, default=1_800_000, description="Initial portfolio balance in CNY")
    monthly_withdrawal: float = Field(gt=0, default=10_000, description="Monthly withdrawal amount in CNY")
    stock_allocation: float = Field(ge=0, le=100, default=90, description="Stock allocation percentage")
    time_horizon_years: int = Field(ge=1, le=50, default=23, description="Time horizon in years")
    expected_return: float = Field(ge=-50, le=100, default=10, description="Expected annual stock return percentage")
    annual_income: float = Field(ge=0, default=13_000, description="Annual income in CNY")

    # Advanced parameters (hidden by default)
    stock_volatility: float = Field(ge=0, le=100, default=10, description="Annual stock volatility percentage")
    cash_return: float = Field(ge=-50, le=50, default=1.15, description="Annual cash return percentage")
    inflation_rate: float = Field(ge=0, le=50, default=3, description="Annual inflation rate percentage")
    num_paths: int = Field(ge=100, le=100_000, default=10_000, description="Number of simulation paths")

    # Random seed for reproducibility
    random_seed: int | None = Field(default=None, description="Random seed for reproducibility")

    @field_validator('stock_allocation')
    @classmethod
    def validate_allocation(cls, v: float) -> float:
        """Ensure stock allocation is valid."""
        if not 0 <= v <= 100:
            raise ValueError("Stock allocation must be between 0 and 100")
        return float(v)

    @property
    def cash_allocation(self) -> float:
        """Calculate cash allocation from stock allocation.

        Returns:
            Cash allocation percentage.
        """
        return 100.0 - self.stock_allocation

    @property
    def total_months(self) -> int:
        """Calculate total number of months in the simulation.

        Returns:
            Total months.
        """
        return self.time_horizon_years * 12

    def to_monthly_params(self) -> 'MonthlyParams':
        """Convert annual parameters to monthly.

        Uses geometric mean for multiplicative returns:
        monthly_rate = (1 + annual_rate)^(1/12) - 1

        Volatility scales by square root of time:
        monthly_volatility = annual_volatility / sqrt(12)

        Returns:
            MonthlyParams: Monthly simulation parameters.
        """
        # Convert percentage to decimal
        mu_annual = self.expected_return / 100
        sigma_annual = self.stock_volatility / 100
        r_cash_annual = self.cash_return / 100
        inflation_annual = self.inflation_rate / 100

        return MonthlyParams(
            mu_stock=(1 + mu_annual) ** (1 / 12) - 1,
            sigma_stock=sigma_annual / math.sqrt(12),
            r_cash=(1 + r_cash_annual) ** (1 / 12) - 1,
            inflation=(1 + inflation_annual) ** (1 / 12) - 1,
            monthly_income=self.annual_income / 12,
            monthly_withdrawal_base=self.monthly_withdrawal,
            total_months=self.total_months,
            stock_allocation=self.stock_allocation / 100,
            cash_allocation=self.cash_allocation / 100,
        )

    @classmethod
    def from_preset(cls, preset: str) -> 'SimulationConfig':
        """Create configuration from a preset.

        Args:
            preset: Preset name ("conservative", "balanced", "aggressive").

        Returns:
            SimulationConfig with preset values.

        Raises:
            ValueError: If preset name is unknown.
        """
        presets = {
            "conservative": cls(
                stock_allocation=60,
                expected_return=4,
                stock_volatility=8,
                monthly_withdrawal=8_000,
            ),
            "balanced": cls(
                stock_allocation=80,
                expected_return=5,
                stock_volatility=10,
                monthly_withdrawal=10_000,
            ),
            "aggressive": cls(
                stock_allocation=95,
                expected_return=6,
                stock_volatility=14,
                monthly_withdrawal=12_000,
            ),
        }

        preset_lower = preset.lower()
        if preset_lower not in presets:
            raise ValueError(f"Unknown preset: {preset}. Choose from: {list(presets.keys())}")

        return presets[preset_lower]


class MonthlyParams(BaseModel):
    """Monthly simulation parameters derived from SimulationConfig.

    These values are pre-computed to avoid redundant calculations
    during the simulation loop.

    Attributes:
        mu_stock: Monthly stock return mean.
        sigma_stock: Monthly stock return standard deviation.
        r_cash: Monthly cash return rate.
        inflation: Monthly inflation rate.
        monthly_income: Monthly income amount.
        monthly_withdrawal_base: Base monthly withdrawal amount.
        total_months: Total number of months to simulate.
        stock_allocation: Stock allocation fraction (0-1).
        cash_allocation: Cash allocation fraction (0-1).
    """

    mu_stock: float
    sigma_stock: float
    r_cash: float
    inflation: float
    monthly_income: float
    monthly_withdrawal_base: float
    total_months: int
    stock_allocation: float
    cash_allocation: float

    def get_withdrawal(self, month: int) -> float:
        """Get inflation-adjusted withdrawal for a given month.

        Args:
            month: Month index (0-based).

        Returns:
            Withdrawal amount for the month.
        """
        return self.monthly_withdrawal_base * ((1 + self.inflation) ** month)
