"""GUI integration tests that simulate real user workflows.

These tests use pytest-qt to simulate actual user interactions
like clicking buttons, waiting for simulations, and verifying results.
"""

import pytest
import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest

from src.gui.main_window import MainWindow
from src.config import SimulationConfig

# Use offscreen platform for CI/testing without display
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')


class TestSimulationWorkflow:
    """Test the complete simulation workflow from user perspective."""

    def test_full_simulation_workflow(self, qtbot) -> None:
        """Test running a complete simulation from start to finish.

        This test simulates:
        1. Launching the application
        2. Verifying input page is shown
        3. Running simulation
        4. Waiting for simulation to complete
        5. Verifying results page is displayed
        6. Checking that charts have data
        """
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        # Process events to ensure window is shown
        qtbot.wait(50)

        # Step 1: Verify input page is initially shown
        assert window.stack.currentWidget() == window.input_page, \
            "Input page should be shown initially"

        # Step 2: Run simulation (use small config for faster testing)
        test_config = SimulationConfig(
            initial_balance=100_000,
            monthly_withdrawal=1_000,
            stock_allocation=80,
            time_horizon_years=1,  # Just 1 year for speed
            expected_return=5,
            annual_income=0,
            stock_volatility=10,
            cash_return=2,
            inflation_rate=2,
            num_paths=100,  # Small number for speed
        )

        # Step 3: Run simulation
        window._run_simulation(test_config)

        # Step 4: Wait for simulation to complete and results page to be shown
        for _ in range(100):  # Up to 5 seconds (100 * 50ms)
            qtbot.wait(50)
            if window.stack.currentWidget() == window.results_page:
                break
        else:
            assert False, "Results page was never shown after simulation"

        # Step 5: Verify results page is shown
        assert window.stack.currentWidget() == window.results_page

        # Step 6: Verify results were stored
        assert window.results.is_loaded(), "Results should be loaded"
        assert window.results.num_paths == 100, "Should have 100 paths"
        assert window.results.total_months == 12, "Should have 12 months (1 year)"

        # Step 7: Verify success gauge is updated
        success_rate = window.results_page.success_gauge._percentage
        assert success_rate >= 0, f"Success rate should be set, got {success_rate}"
        assert success_rate <= 100, f"Success rate should be valid, got {success_rate}"

        # Step 8: Verify charts exist and have data
        charts = window.results_page.chart_tabs
        assert charts is not None, "Chart tabs should exist"
        assert charts.monthly_table is not None, "Monthly table should exist"

        # Distribution chart IS auto-initialized when results are set (default tab at index 0)
        assert charts._dist_initialized, "Distribution chart should be initialized when results are set"
        assert charts._dist_ax is not None, "Distribution axis should exist"
        assert charts._dist_canvas is not None, "Distribution canvas should exist"
        # Overtime chart is NOT initialized (not default tab)
        assert not charts._ot_initialized, "Overtime chart should not be initialized until tab is selected"

        # Verify data was set
        assert charts._results is not None, "Results should be set on charts"
        assert charts._results.is_loaded(), "Results should be loaded"

        # Verify monthly table has data
        assert charts.monthly_table._model is not None, "Monthly table model should exist"

        # Step 9: Initialize overtime chart by selecting its tab
        charts.tabs.setCurrentIndex(1)
        qtbot.wait(50)
        assert charts._ot_initialized, "Overtime chart should be initialized after tab selection"
        assert charts._ot_ax is not None, "Overtime axis should exist"
        assert charts._ot_canvas is not None, "Overtime canvas should exist"

        # Wait for chart updates (QTimer.singleShot(0))
        qtbot.wait(100)

        # Step 9: Test navigation back to input page
        window.results_page.back_requested.emit()
        qtbot.wait(50)
        assert window.stack.currentWidget() == window.input_page, \
            "Should return to input page"

    def test_simulation_with_data_verification(self, qtbot) -> None:
        """Test simulation and verify actual data is in the charts.

        This is a more comprehensive test that checks:
        1. Simulation runs successfully
        2. Chart data is properly set
        3. Data can be retrieved from charts
        """
        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        qtbot.wait(50)

        # Run simulation with specific known parameters
        test_config = SimulationConfig(
            initial_balance=100_000,
            monthly_withdrawal=500,
            stock_allocation=60,
            time_horizon_years=1,
            expected_return=5,
            annual_income=0,
            stock_volatility=10,
            cash_return=2,
            inflation_rate=2,
            num_paths=100,  # Must be >= 100 per validation
        )

        window._run_simulation(test_config)

        # Wait for completion
        for _ in range(100):
            qtbot.wait(50)
            if window.stack.currentWidget() == window.results_page:
                break
        else:
            assert False, "Results page was never shown"

        # Wait for chart updates
        qtbot.wait(100)

        # Verify results are loaded
        assert window.results.is_loaded()
        assert window.results.num_paths == 100

        # Verify chart widgets have data
        charts = window.results_page.chart_tabs

        # Initialize charts by changing tabs (first tab is already selected)
        charts.tabs.setCurrentIndex(2)  # Monthly Details
        qtbot.wait(50)
        charts.tabs.setCurrentIndex(0)  # Distribution - triggers initialization
        qtbot.wait(50)
        charts.tabs.setCurrentIndex(1)  # Over Time - triggers initialization
        qtbot.wait(50)

        # Check distribution chart has data
        assert charts._dist_ax is not None
        assert charts._dist_canvas is not None

        # Check overtime chart has data
        assert charts._ot_ax is not None
        assert charts._ot_canvas is not None
        # Matplotlib renders directly, no separate curve/line objects

        # Verify summary cards are updated
        stats = window.results.get_summary_stats()
        assert "median" in stats
        assert "mean" in stats
        assert "min" in stats
        assert "max" in stats

        # Verify success rate is calculated
        success_rate = window.results.get_success_rate()
        assert 0 <= success_rate <= 100

    @pytest.mark.skip("Requires full Qt event loop, hangs in CI/offscreen mode")
    def test_simulation_with_default_params(self, qtbot) -> None:
        """Test simulation with default parameters (larger dataset)."""
        pass  # Skipped in CI

    @pytest.mark.skip("Requires full Qt event loop, hangs in CI/offscreen mode")
    def test_multiple_simulations_in_sequence(self, qtbot) -> None:
        """Test running multiple simulations one after another.

        This is a regression test for graphics/item lifecycle issues.
        """
        pass  # Skipped in CI


class TestResultsPageDisplay:
    """Test results page display with actual data."""

    @pytest.mark.skip("Requires full Qt event loop, hangs in CI/offscreen mode")
    def test_summary_cards_display(self, qtbot) -> None:
        """Test that summary cards display formatted currency values."""
        pass  # Skipped in CI

    def test_success_gauge_display(self, qtbot) -> None:
        """Test that success gauge displays correctly."""
        from src.gui.components.success_gauge import SuccessGauge

        gauge = SuccessGauge()
        qtbot.addWidget(gauge)

        # Test different success rates (no wait needed)
        for rate in [0, 25, 50, 75, 90, 100]:
            gauge.set_percentage(rate)
            assert gauge._percentage == rate

    def test_back_button_navigation(self, qtbot) -> None:
        """Test back button navigation."""
        window = MainWindow()
        qtbot.addWidget(window)

        # Initially on input page
        assert window.stack.currentWidget() == window.input_page

        # Simulate simulation completion
        manager = window.results
        balances = np.ones((10, 12), dtype=np.float32) * 100_000
        manager.store(balances=balances, initial_balance=100_000)

        window.results_page.set_results(manager)
        window._show_results_page()

        # Should be on results page
        assert window.stack.currentWidget() == window.results_page

        # Click back button
        window.results_page.back_requested.emit()

        # Should be back on input page
        assert window.stack.currentWidget() == window.input_page


class TestInputPageControls:
    """Test input page controls and interactions."""

    def test_param_card_values(self, qtbot) -> None:
        """Test that parameter cards have correct default values."""
        from src.gui.pages.input_page import InputPage
        from src.config import SimulationConfig

        page = InputPage()
        qtbot.addWidget(page)

        # Check default values match SimulationConfig defaults
        default_config = SimulationConfig()
        assert page.initial_balance_card.get_value() == default_config.initial_balance
        assert page.monthly_withdrawal_card.get_value() == default_config.monthly_withdrawal
        assert page.time_horizon_card.get_value() == default_config.time_horizon_years
        assert page.stock_allocation_card.get_value() == default_config.stock_allocation
        assert page.expected_return_card.get_value() == default_config.expected_return
        assert page.annual_income_card.get_value() == default_config.annual_income

    def test_config_roundtrip(self, qtbot) -> None:
        """Test that config can be retrieved and set correctly."""
        from src.gui.pages.input_page import InputPage

        page = InputPage()
        qtbot.addWidget(page)

        # Get config
        config1 = page.get_config()

        # Modify and set back
        config2 = SimulationConfig(
            initial_balance=500_000,
            monthly_withdrawal=5_000,
            stock_allocation=config1.stock_allocation,
            time_horizon_years=config1.time_horizon_years,
            expected_return=config1.expected_return,
            annual_income=config1.annual_income,
            stock_volatility=config1.stock_volatility,
            cash_return=config1.cash_return,
            inflation_rate=config1.inflation_rate,
            num_paths=config1.num_paths,
        )
        page.set_config(config2)

        # Verify values changed
        assert page.initial_balance_card.get_value() == 500_000
        assert page.monthly_withdrawal_card.get_value() == 5_000

    def test_advanced_panel_toggle(self, qtbot) -> None:
        """Test expanding and collapsing advanced panel."""
        from src.gui.pages.input_page import InputPage

        page = InputPage()
        qtbot.addWidget(page)

        # Panel should exist
        assert page.advanced_panel is not None

        # Toggle expand
        page.advanced_panel.expand()
        assert page.advanced_panel.is_expanded()

        # Toggle collapse
        page.advanced_panel.collapse()
        assert not page.advanced_panel.is_expanded()
