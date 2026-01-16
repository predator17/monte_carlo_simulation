"""Result manager for Monte Carlo simulation outputs.

This module provides efficient storage and retrieval of simulation results
using Polars LazyFrame for memory-efficient data operations.
"""

import numpy as np
import polars as pl
from typing import Optional, Iterator, Tuple
from numpy.typing import NDArray


class ResultManager:
    """Manage simulation results with efficient data access.

    This class stores simulation results and provides methods for
    accessing statistics, percentiles, and monthly data without
    loading all data into memory at once.

    Thread-safe for use with QThread workers.
    """

    def __init__(self):
        """Initialize an empty ResultManager."""
        self._balances: Optional[NDArray[np.float32]] = None
        self._withdrawals: Optional[NDArray[np.float32]] = None
        self._monthly_income: float = 0
        self._num_paths: int = 0
        self._total_months: int = 0
        self._initial_balance: float = 0
        self._config_hash: Optional[str] = None
        self._stock_alloc: float = 0.0  # Stock allocation for return calculation
        self._cash_alloc: float = 0.0  # Cash allocation for return calculation
        self._cash_return_rate: float = 0.0  # Monthly cash return rate

    def store(
        self,
        balances: NDArray[np.float32],
        withdrawals: Optional[NDArray[np.float32]] = None,
        initial_balance: float = 0,
        config_hash: Optional[str] = None,
        monthly_income: float = 0,
        stock_alloc: float = 0.0,
        cash_alloc: float = 0.0,
        cash_return_rate: float = 0.0,
    ) -> None:
        """Store simulation results.

        Args:
            balances: Array of shape (num_paths, total_months).
            withdrawals: Monthly withdrawal amounts.
            initial_balance: Initial portfolio balance.
            config_hash: Hash of configuration for caching.
            monthly_income: Monthly income amount (from annual_income / 12).
            stock_alloc: Stock allocation (0-1) for return calculation.
            cash_alloc: Cash allocation (0-1) for return calculation.
            cash_return_rate: Monthly cash return rate (e.g., 0.002 for 0.2%).
        """
        self._balances = balances
        self._withdrawals = withdrawals
        self._monthly_income = monthly_income
        self._num_paths, self._total_months = balances.shape
        self._initial_balance = initial_balance
        self._config_hash = config_hash
        self._stock_alloc = stock_alloc
        self._cash_alloc = cash_alloc
        self._cash_return_rate = cash_return_rate

    def is_loaded(self) -> bool:
        """Check if results are loaded.

        Returns:
            True if results are available.
        """
        return self._balances is not None

    @property
    def balances(self) -> NDArray[np.float32]:
        """Get the balances array.

        Returns:
            Array of shape (num_paths, total_months).
        """
        if self._balances is None:
            raise RuntimeError("No results loaded. Call store() first.")
        return self._balances

    @property
    def withdrawals(self) -> NDArray[np.float32]:
        """Get the withdrawals array.

        Returns:
            Array of monthly withdrawal amounts.
        """
        if self._withdrawals is None:
            raise RuntimeError("No results loaded. Call store() first.")
        return self._withdrawals

    @property
    def num_paths(self) -> int:
        """Get the number of simulation paths."""
        return self._num_paths

    @property
    def total_months(self) -> int:
        """Get the total number of months."""
        return self._total_months

    @property
    def total_row_count(self) -> int:
        """Get total number of rows for lazy loading table.

        Returns:
            Total rows (monthly rows only, no year headers).
        """
        return self._total_months

    def get_final_balances(self) -> NDArray[np.float32]:
        """Get final balances for all paths.

        Returns:
            Array of final balances.
        """
        return self.balances[:, -1]

    def get_success_rate(self) -> float:
        """Calculate success rate (paths with positive final balance).

        Returns:
            Success rate as percentage.
        """
        final = self.get_final_balances()
        return float(np.sum(final > 0) / len(final) * 100)

    def get_summary_stats(self) -> dict[str, float]:
        """Get summary statistics of final balances.

        Returns:
            Dictionary with mean, median, std, min, max, percentiles.
        """
        final = self.get_final_balances()
        return {
            "mean": float(np.mean(final)),
            "median": float(np.median(final)),
            "std": float(np.std(final)),
            "min": float(np.min(final)),
            "max": float(np.max(final)),
            "p5": float(np.percentile(final, 5)),
            "p10": float(np.percentile(final, 10)),
            "p25": float(np.percentile(final, 25)),
            "p75": float(np.percentile(final, 75)),
            "p90": float(np.percentile(final, 90)),
            "p95": float(np.percentile(final, 95)),
        }

    def get_percentiles(
        self,
        percentiles: list[int] = [10, 25, 50, 75, 90],
    ) -> dict[int, NDArray[np.float32]]:
        """Get percentile paths over time.

        Args:
            percentiles: List of percentiles to calculate.

        Returns:
            Dictionary mapping percentile to array over time.
        """
        result = {}
        for p in percentiles:
            result[p] = np.percentile(self.balances, p, axis=0).astype(np.float32)
        return result

    def get_median_path(self) -> NDArray[np.float32]:
        """Get the median path balance over time.

        Returns:
            Array of median balances.
        """
        return np.median(self.balances, axis=0).astype(np.float32)

    def get_monthly_data(
        self,
        path_id: int,
        start_month: int = 0,
        end_month: Optional[int] = None,
    ) -> pl.DataFrame:
        """Get monthly data for a specific path.

        Args:
            path_id: Path index (0 to num_paths-1).
            start_month: Starting month index.
            end_month: Ending month index (None for all).

        Returns:
            Polars DataFrame with monthly data.
        """
        if end_month is None:
            end_month = self._total_months

        path_balances = self.balances[path_id, start_month:end_month]
        withdrawals = self.withdrawals[start_month:end_month]

        # Calculate monthly changes and returns
        prev_balance = np.concatenate([[self._initial_balance], path_balances[:-1]])
        changes = path_balances - prev_balance

        # Create year and month columns
        months = np.arange(start_month, end_month)
        years = months // 12
        month_in_year = months % 12

        return pl.DataFrame({
            "period": months,
            "year": years,
            "month": month_in_year,
            "start_balance": prev_balance.astype(np.float32),
            "end_balance": path_balances,
            "change": changes.astype(np.float32),
            "withdrawal": withdrawals,
            "return_pct": np.divide(
                changes,
                prev_balance,
                out=np.zeros_like(changes),
                where=prev_balance != 0,
            ) * 100,
        })

    def fetch_rows(
        self,
        start_row: int,
        count: int,
        path_id: int = -1,  # -1 for median path
        year_filter: int | None = None,  # None for all years, 0-N for specific year
        current_year: int = 2026,  # Starting calendar year
    ) -> dict[int, dict[str, float | int | str]]:
        """Fetch rows for lazy loading table.

        Note: Year header rows are skipped - only month rows are returned.

        Args:
            start_row: Starting row index (virtual index from model).
            count: Number of rows to fetch.
            path_id: Path to use (-1 for median).
            year_filter: Filter to specific year (None for all, 0-N for specific year).
            current_year: Current calendar year for labeling.

        Returns:
            Dictionary mapping virtual row index to row data.
        """
        if path_id == -1:
            balances = self.get_median_path()
        else:
            balances = self.balances[path_id]

        result = {}
        fetched_count = 0

        for i in range(count):
            row_idx = start_row + i

            # When year_filter is active, row_idx is virtual (0-11 for 12 months in that year)
            # When year_filter is None, we need to skip year headers
            if year_filter is not None:
                # Virtual row indexing for single year view (0-11 for 12 months)
                month_idx_in_year = row_idx
                if month_idx_in_year >= 12:
                    break
                year_idx = year_filter
                month_idx = year_idx * 12 + month_idx_in_year
            else:
                # Global row indexing - need to account for year headers
                # Original layout: 1 header + 12 months per year = 13 rows per year
                # New layout: 12 months only, so we need to map accordingly
                year_idx = row_idx // 12
                month_idx_in_year = row_idx % 12
                month_idx = year_idx * 12 + month_idx_in_year

            # Check if we've exceeded total months
            if month_idx >= self._total_months:
                break

            prev_balance = balances[month_idx - 1] if month_idx > 0 else self._initial_balance
            curr_balance = balances[month_idx]
            change = curr_balance - prev_balance
            withdrawal = self.withdrawals[month_idx] if self._withdrawals is not None else 0

            # Monthly income (fixed amount from config)
            income = self._monthly_income

            # Calculate actual returns for each portion
            # During simulation:
            #   1. Start with prev_balance
            #   2. Subtract withdrawal, add income
            #   3. Split balance into stock_amount and cash_amount based on allocation
            #   4. Apply returns: stock_amount * (1 + stock_return) + cash_amount * (1 + r_cash)
            #   5. Result is curr_balance

            if prev_balance > 0:
                # Balance after cash flows (what gets invested)
                balance_for_investment = prev_balance - withdrawal + income

                if balance_for_investment > 0:
                    # Split into stock and cash portions
                    stock_amount = balance_for_investment * self._stock_alloc
                    cash_amount = balance_for_investment * self._cash_alloc

                    # Cash return is the fixed rate (what cash portion actually earns)
                    cash_return = self._cash_return_rate * 100  # Convert to percentage

                    # Back-calculate the actual stock return from the final balance
                    # curr_balance = stock_amount * (1 + stock_return) + cash_amount * (1 + r_cash)
                    # stock_return = (curr_balance - cash_amount * (1 + r_cash)) / stock_amount - 1
                    final_cash = cash_amount * (1 + self._cash_return_rate)
                    stock_return = (curr_balance - final_cash) / stock_amount - 1 if stock_amount > 0 else 0
                    portfolio_return = stock_return * 100
                else:
                    # Depleted portfolio
                    portfolio_return = 0.0
                    cash_return = self._cash_return_rate * 100
            else:
                portfolio_return = 0.0
                cash_return = self._cash_return_rate * 100

            # Get month name with year indicator (e.g., "Jan 2026")
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            calendar_year = current_year + year_idx
            month_name = month_names[month_idx_in_year]

            result[row_idx] = {
                "period": f"{month_name} {calendar_year}",
                "balance": curr_balance,
                "change": change,
                "portfolio_return": portfolio_return,
                "cash_return": cash_return,
                "withdrawal": withdrawal,
                "income": income,
            }

            fetched_count += 1

        return result

    def to_lazyframe(self) -> pl.LazyFrame:
        """Convert results to Polars LazyFrame for advanced analysis.

        Returns:
            LazyFrame with all simulation data.
        """
        # Create path_id and month indices
        path_ids = np.repeat(np.arange(self._num_paths), self._total_months)
        month_indices = np.tile(np.arange(self._total_months), self._num_paths)

        # Flatten balances
        flat_balances = self.balances.flatten()

        return pl.DataFrame({
            "path_id": path_ids.astype(np.uint16),
            "period": month_indices.astype(np.uint16),
            "year": (month_indices // 12).astype(np.uint8),
            "month": (month_indices % 12).astype(np.uint8),
            "balance": flat_balances,
        }).lazy()

    def get_distribution_data(self) -> pl.DataFrame:
        """Get final balance distribution data.

        Returns:
            DataFrame with path_id and final_balance columns.
        """
        return pl.DataFrame({
            "path_id": np.arange(self._num_paths).astype(np.uint16),
            "final_balance": self.get_final_balances(),
        })

    def clear(self) -> None:
        """Clear stored results."""
        self._balances = None
        self._withdrawals = None
        self._num_paths = 0
        self._total_months = 0
        self._initial_balance = 0
        self._config_hash = None
