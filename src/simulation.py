"""Monte Carlo simulation engine with Numba JIT compilation.

This module provides high-performance Monte Carlo simulation for
portfolio sustainability analysis. The core simulation loop is
JIT-compiled with Numba for 100-1000x speedup vs pure Python.

The simulation follows this monthly sequence:
1. Withdrawal at start of month
2. Income at start of month
3. Rebalance to target allocation
4. Generate random stock return
5. Apply returns to both portions
6. Record end-of-month balance
"""

import numpy as np
from numba import njit, prange
import numpy.typing as npt
from typing import Tuple
from src.config import MonthlyParams


# Set random seed for reproducibility
_RNG_SEED: int | None = None


def set_random_seed(seed: int | None) -> None:
    """Set the random seed for NumPy.

    Args:
        seed: Random seed value, or None for random.
    """
    global _RNG_SEED
    _RNG_SEED = seed
    if seed is not None:
        np.random.seed(seed)


@njit(parallel=True, cache=True)
def _simulate_paths(
    num_paths: int,
    total_months: int,
    initial_balance: float,
    stock_alloc: float,
    cash_alloc: float,
    mu_stock: float,
    sigma_stock: float,
    r_cash: float,
    withdrawal_base: float,
    inflation: float,
    monthly_income: float,
) -> npt.NDArray[np.float32]:
    """Simulate multiple portfolio paths using Numba JIT.

    This is the core simulation loop, compiled to machine code for
    maximum performance. Uses parallel processing for multiple paths.

    Args:
        num_paths: Number of simulation paths.
        total_months: Number of months to simulate.
        initial_balance: Starting portfolio balance.
        stock_alloc: Fraction allocated to stocks (0-1).
        cash_alloc: Fraction allocated to cash (0-1).
        mu_stock: Monthly stock return mean.
        sigma_stock: Monthly stock return std dev.
        r_cash: Monthly cash return rate.
        withdrawal_base: Base monthly withdrawal amount.
        inflation: Monthly inflation rate.
        monthly_income: Monthly income amount.

    Returns:
        Array of shape (num_paths, total_months) containing end balances.
    """
    # Pre-allocate output array
    balances = np.zeros((num_paths, total_months), dtype=np.float32)

    # Simulate each path
    for path in prange(num_paths):
        balance = initial_balance

        for month in range(total_months):
            # Calculate inflation-adjusted withdrawal
            withdrawal = withdrawal_base * ((1 + inflation) ** month)

            # Step 1: Withdrawal at start of month
            balance -= withdrawal

            # Step 2: Income at start of month
            balance += monthly_income

            # Check if depleted
            if balance <= 0:
                balances[path, month:] = 0
                break

            # Step 3: Rebalance to target allocation
            stock_amount = balance * stock_alloc
            cash_amount = balance * cash_alloc

            # Step 4: Generate random stock return
            stock_return = np.random.normal(mu_stock, sigma_stock)

            # Step 5: Apply returns (compound)
            stock_amount *= (1 + stock_return)
            cash_amount *= (1 + r_cash)

            # Step 6: Record end-of-month balance
            balance = stock_amount + cash_amount
            balances[path, month] = max(balance, 0)

    return balances


class SimulationEngine:
    """Monte Carlo simulation engine.

    This class provides a high-level interface to the Numba-compiled
    simulation core. It handles parameter conversion and result processing.
    """

    def __init__(self, seed: int | None = None):
        """Initialize the simulation engine.

        Args:
            seed: Random seed for reproducibility.
        """
        self.seed = seed
        if seed is not None:
            set_random_seed(seed)

    def simulate(
        self,
        params: MonthlyParams,
        initial_balance: float,
        num_paths: int,
    ) -> npt.NDArray[np.float32]:
        """Run Monte Carlo simulation.

        Args:
            params: Monthly simulation parameters.
            initial_balance: Starting portfolio balance.
            num_paths: Number of paths to simulate.

        Returns:
            Array of shape (num_paths, total_months) containing end balances.
        """
        return _simulate_paths(
            num_paths=num_paths,
            total_months=params.total_months,
            initial_balance=initial_balance,
            stock_alloc=params.stock_allocation,
            cash_alloc=params.cash_allocation,
            mu_stock=params.mu_stock,
            sigma_stock=params.sigma_stock,
            r_cash=params.r_cash,
            withdrawal_base=params.monthly_withdrawal_base,
            inflation=params.inflation,
            monthly_income=params.monthly_income,
        )

    def simulate_with_history(
        self,
        params: MonthlyParams,
        initial_balance: float,
        num_paths: int,
    ) -> dict[str, npt.NDArray[np.float32]]:
        """Run simulation and return detailed history.

        In addition to balances, this method returns the full monthly
        breakdown for analysis and visualization.

        Args:
            params: Monthly simulation parameters.
            initial_balance: Starting portfolio balance.
            num_paths: Number of paths to simulate.

        Returns:
            Dictionary containing:
                - balances: End balances (num_paths, total_months)
                - withdrawals: Monthly withdrawals (total_months,)
                - stock_returns: Generated returns (num_paths, total_months)
        """
        balances = self.simulate(params, initial_balance, num_paths)

        # Calculate withdrawal schedule
        months = np.arange(params.total_months)
        withdrawals = params.monthly_withdrawal_base * ((1 + params.inflation) ** months)

        # Generate stock returns (for visualization)
        # Note: These are re-generated for visualization; actual simulation
        # uses different random draws internally
        stock_returns = np.random.normal(
            params.mu_stock,
            params.sigma_stock,
            (num_paths, params.total_months),
        ).astype(np.float32)

        return {
            "balances": balances,
            "withdrawals": withdrawals.astype(np.float32),
            "stock_returns": stock_returns,
        }


def calculate_percentiles(
    balances: npt.NDArray[np.float32],
    percentiles: list[int] = [10, 25, 50, 75, 90],
) -> dict[int, npt.NDArray[np.float32]]:
    """Calculate percentile paths from simulation results.

    Args:
        balances: Array of shape (num_paths, total_months).
        percentiles: List of percentiles to calculate (0-100).

    Returns:
        Dictionary mapping percentile to array of values over time.
    """
    result = {}
    for p in percentiles:
        result[p] = np.percentile(balances, p, axis=0).astype(np.float32)
    return result


def calculate_success_rate(
    balances: npt.NDArray[np.float32],
) -> float:
    """Calculate the success rate (fraction of paths with positive balance).

    Args:
        balances: Array of shape (num_paths, total_months).

    Returns:
        Success rate as a percentage (0-100).
    """
    final_balances = balances[:, -1]
    success = np.sum(final_balances > 0) / len(final_balances)
    return success * 100


def calculate_summary_stats(
    balances: npt.NDArray[np.float32],
) -> dict[str, float]:
    """Calculate summary statistics from simulation results.

    Args:
        balances: Array of shape (num_paths, total_months).

    Returns:
        Dictionary containing summary statistics.
    """
    final_balances = balances[:, -1]

    return {
        "mean": float(np.mean(final_balances)),
        "median": float(np.median(final_balances)),
        "std": float(np.std(final_balances)),
        "min": float(np.min(final_balances)),
        "max": float(np.max(final_balances)),
        "p5": float(np.percentile(final_balances, 5)),
        "p10": float(np.percentile(final_balances, 10)),
        "p25": float(np.percentile(final_balances, 25)),
        "p75": float(np.percentile(final_balances, 75)),
        "p90": float(np.percentile(final_balances, 90)),
        "p95": float(np.percentile(final_balances, 95)),
    }
