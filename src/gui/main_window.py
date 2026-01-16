"""Main application window for the Portfolio Monte Carlo Simulator.

This module contains the main window that manages page navigation
and the simulation workflow.
"""

from PySide6.QtWidgets import (
    QMainWindow, QStackedWidget, QVBoxLayout, QWidget,
    QMessageBox, QApplication
)
from PySide6.QtCore import Signal, Qt, QThread
from typing import Optional

from src.config import SimulationConfig
from src.results import ResultManager
from src.theme import apply_dark_theme
from src.constants import GUI, Colors
from src.gui.pages.input_page import InputPage
from src.gui.pages.results_page import ResultsPage
from src.gui.workers.simulation_worker import SimulationWorker


class MainWindow(QMainWindow):
    """Main application window.

    Manages page navigation between input configuration and results display.
    Coordinates the simulation workflow with worker thread handling.

    Signals:
        simulation_started: Emitted when simulation begins.
        simulation_finished: Emitted when simulation completes.
        simulation_failed: Emitted when simulation fails.
    """

    simulation_started = Signal()
    simulation_finished = Signal(object)
    simulation_failed = Signal(str)

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        self.setWindowTitle("Portfolio Simulator")
        self.resize(GUI.WINDOW_DEFAULT_WIDTH, GUI.WINDOW_DEFAULT_HEIGHT)
        self.setMinimumSize(GUI.WINDOW_MIN_WIDTH, GUI.WINDOW_MIN_HEIGHT)

        # Apply dark theme
        apply_dark_theme(QApplication.instance())

        # Central widget with stacked layout
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create pages
        self.input_page = InputPage()
        self.results_page = ResultsPage()

        self.stack.addWidget(self.input_page)
        self.stack.addWidget(self.results_page)

        # Worker and results
        self.worker: Optional[SimulationWorker] = None
        self.thread: Optional[QThread] = None
        self.results = ResultManager()

        # Connect signals
        self.input_page.run_requested.connect(self._run_simulation)
        self.results_page.back_requested.connect(self._show_input_page)

        # Show input page by default
        self._show_input_page()

    def _show_input_page(self) -> None:
        """Switch to input configuration page."""
        self.stack.setCurrentWidget(self.input_page)

    def _show_results_page(self) -> None:
        """Switch to results display page."""
        self.stack.setCurrentWidget(self.results_page)

    def _run_simulation(self, config: SimulationConfig) -> None:
        """Start simulation in worker thread.

        Args:
            config: Simulation configuration.
        """
        if self.worker and self.worker.is_running():
            return

        # Create new thread and worker
        self.thread = QThread()
        self.worker = SimulationWorker(config)
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.input_page.update_progress)
        self.worker.finished.connect(self._on_simulation_finished)
        self.worker.error.connect(self._on_simulation_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Disable run button and show progress
        self.input_page.set_running(True)
        self.simulation_started.emit()

        # Start simulation
        self.thread.start()

    def _on_simulation_finished(self, result_data: dict) -> None:
        """Handle simulation completion.

        Args:
            result_data: Dictionary containing simulation results.
        """
        try:
            # Store results
            self.results.store(
                balances=result_data["balances"],
                withdrawals=result_data.get("withdrawals"),
                initial_balance=result_data["initial_balance"],
                monthly_income=result_data.get("monthly_income", 0),
                stock_alloc=result_data.get("stock_alloc", 0),
                cash_alloc=result_data.get("cash_alloc", 0),
                cash_return_rate=result_data.get("cash_return_rate", 0),
            )

            # Enable run button and hide progress
            self.input_page.set_running(False)

            # Show results page first (charts are already created in __init__)
            self._show_results_page()

            # Update results - charts will update via QTimer.singleShot(0)
            self.results_page.set_results(self.results)

            self.simulation_finished.emit(self.results)
        except Exception as e:
            self.input_page.set_running(False)
            import traceback
            print(f"Error in _on_simulation_finished: {e}")
            traceback.print_exc()

    def _on_simulation_error(self, error_msg: str) -> None:
        """Handle simulation error.

        Args:
            error_msg: Error message.
        """
        self.input_page.set_running(False)

        QMessageBox.critical(
            self,
            "Simulation Error",
            f"An error occurred during simulation:\n\n{error_msg}"
        )

        self.simulation_failed.emit(error_msg)

    def closeEvent(self, event) -> None:
        """Handle window close event.

        Args:
            event: Close event.
        """
        # Clean up worker thread
        if self.worker and self.worker.is_running():
            self.worker.cancel()
            self.thread.wait(3000)  # Wait up to 3 seconds

        event.accept()
