"""Worker thread for Monte Carlo simulation.

This module provides a QThread worker that runs simulations
without blocking the GUI.
"""

from PySide6.QtCore import QObject, Signal
from typing import Optional
import numpy as np

from src.config import SimulationConfig
from src.simulation import SimulationEngine


class SimulationWorker(QObject):
    """Worker for running Monte Carlo simulations in a separate thread.

    Uses the moveToThread pattern for proper Qt threading.
    Emits progress updates during simulation.

    Signals:
        progress: Emitted with (current, total, message) during simulation.
        finished: Emitted with result dictionary when complete.
        error: Emitted with error message on failure.
    """

    progress = Signal(int, int, str)  # current, total, message
    finished = Signal(dict)  # results
    error = Signal(str)  # error message

    def __init__(self, config: SimulationConfig):
        """Initialize the worker.

        Args:
            config: Simulation configuration.
        """
        super().__init__()
        self.config = config
        self._cancelled = False
        self._running = False
        self._engine = SimulationEngine(seed=config.random_seed)

    def run(self) -> None:
        """Run the simulation.

        This method is called when the thread starts.
        Emits progress updates and results when complete.
        """
        self._running = True
        self._cancelled = False

        try:
            # Get monthly parameters
            params = self.config.to_monthly_params()
            num_paths = self.config.num_paths

            # Emit start signal
            self.progress.emit(0, num_paths, "Initializing simulation...")

            # Run simulation with progress tracking
            result = self._engine.simulate_with_history(
                params=params,
                initial_balance=self.config.initial_balance,
                num_paths=num_paths,
            )

            # Check for cancellation
            if self._cancelled:
                self.error.emit("Simulation cancelled")
                return

            # Emit completion signal
            self.progress.emit(num_paths, num_paths, "Simulation complete")

            # Return results
            self.finished.emit({
                "balances": result["balances"],
                "withdrawals": result["withdrawals"],
                "stock_returns": result["stock_returns"],
                "initial_balance": self.config.initial_balance,
                "monthly_income": params.monthly_income,
                "stock_alloc": params.stock_allocation,
                "cash_alloc": params.cash_allocation,
                "cash_return_rate": params.r_cash,
                "config": self.config,
            })

        except Exception as e:
            self.error.emit(f"Simulation failed: {str(e)}")
        finally:
            self._running = False

    def cancel(self) -> None:
        """Request cancellation of the running simulation."""
        self._cancelled = True

    def is_running(self) -> bool:
        """Check if the worker is currently running.

        Returns:
            True if running, False otherwise.
        """
        return self._running
