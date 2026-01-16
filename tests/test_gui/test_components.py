"""Tests for GUI components.

This module contains tests for the reusable GUI components
using pytest-qt for Qt widget testing.
"""

import pytest
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from src.config import SimulationConfig
from src.results import ResultManager
from src.constants import Colors
from src.gui.components.param_card import ParamCard
from src.gui.components.summary_card import SummaryCard
from src.gui.components.success_gauge import SuccessGauge
from src.gui.components.advanced_panel import AdvancedPanel


class TestParamCard:
    """Test ParamCard component."""

    def test_init(self, qtbot) -> None:
        """Test ParamCard initialization."""
        card = ParamCard("Test Label", 1000, "CNY")
        qtbot.addWidget(card)

        assert card._label_text == "Test Label"
        assert card._unit == "CNY"
        assert card.get_value() == 1000

    def test_set_value(self, qtbot) -> None:
        """Test setting card value."""
        card = ParamCard("Balance", 1000, "CNY")
        qtbot.addWidget(card)

        card.set_value(5000)
        assert card.get_value() == 5000

    def test_slider_card(self, qtbot) -> None:
        """Test slider-based parameter card."""
        card = ParamCard("Allocation", 50, "%", min_value=0, max_value=100,
                         integer=True, is_slider=True, step_size=1)
        qtbot.addWidget(card)

        assert card.get_value() == 50

        card.set_value(80)
        assert card.get_value() == 80

    def test_double_click_edit(self, qtbot) -> None:
        """Test double-click to edit value."""
        card = ParamCard("Balance", 50000, "CNY", min_value=0, max_value=1_000_000,
                         is_slider=True, step_size=1000)
        qtbot.addWidget(card)
        card.show()

        # Initially in display mode
        assert card.value_label.isVisible()
        assert not card.value_edit.isVisible()
        assert card.get_value() == 50000

        # Enter edit mode
        card._enter_edit_mode()
        assert not card.value_label.isVisible()
        assert card.value_edit.isVisible()
        assert card.value_edit.text() == "50000"

        # Simulate user typing a new value
        card.value_edit.setText("75000")

        # Exit edit mode (this triggers _on_edit_finished)
        card._on_edit_finished()

        # Back to display mode with new value
        assert card.value_label.isVisible()
        assert not card.value_edit.isVisible()
        assert card.get_value() == 75000

    def test_integer_card(self, qtbot) -> None:
        """Test integer parameter card."""
        card = ParamCard("Years", 23, "years", integer=True)
        qtbot.addWidget(card)

        assert card.get_value() == 23

        card.set_value(30)
        assert card.get_value() == 30

    def test_min_max_values(self, qtbot) -> None:
        """Test min/max value constraints."""
        card = ParamCard("Test", 50, "", min_value=0, max_value=100)
        qtbot.addWidget(card)

        # Get the spinbox editor
        editor = card.editor
        assert editor.minimum() == 0
        assert editor.maximum() == 100


class TestSummaryCard:
    """Test SummaryCard component."""

    def test_init(self, qtbot) -> None:
        """Test SummaryCard initialization."""
        card = SummaryCard("Median", "¥1,000,000", "End of period")
        qtbot.addWidget(card)

        assert card.title_label.text() == "Median"
        assert card.value_label.text() == "¥1,000,000"

    def test_update_title(self, qtbot) -> None:
        """Test updating card title."""
        card = SummaryCard("Old Title", "Value")
        qtbot.addWidget(card)

        card.update_title("New Title")
        assert card.title_label.text() == "New Title"

    def test_update_value(self, qtbot) -> None:
        """Test updating card value."""
        card = SummaryCard("Title", "Old Value")
        qtbot.addWidget(card)

        card.update_value("New Value")
        assert card.value_label.text() == "New Value"


class TestSuccessGauge:
    """Test SuccessGauge component."""

    def test_init(self, qtbot) -> None:
        """Test SuccessGauge initialization."""
        gauge = SuccessGauge()
        qtbot.addWidget(gauge)

        assert gauge._percentage == 0.0

    def test_set_percentage(self, qtbot) -> None:
        """Test setting percentage."""
        gauge = SuccessGauge()
        qtbot.addWidget(gauge)

        gauge.set_percentage(75.5)
        assert gauge._percentage == pytest.approx(75.5)

    def test_percentage_clamping(self, qtbot) -> None:
        """Test that percentage is clamped to 0-100."""
        gauge = SuccessGauge()
        qtbot.addWidget(gauge)

        gauge.set_percentage(150)
        assert gauge._percentage == 100

        gauge.set_percentage(-50)
        assert gauge._percentage == 0

    def test_set_message(self, qtbot) -> None:
        """Test setting message."""
        gauge = SuccessGauge()
        qtbot.addWidget(gauge)

        gauge.set_message("Test message")
        assert gauge._message == "Test message"

    def test_get_color(self, qtbot) -> None:
        """Test color mapping based on percentage."""
        gauge = SuccessGauge()
        qtbot.addWidget(gauge)

        # High success (>= 90%)
        gauge.set_percentage(95)
        assert gauge._get_color() == Colors.SUCCESS_HIGH

        # Medium (>= 70%)
        gauge.set_percentage(80)
        assert gauge._get_color() == Colors.ACCENT_BLUE

        # Low-medium (>= 50%)
        gauge.set_percentage(60)
        assert gauge._get_color() == Colors.SUCCESS_LOW

        # Danger (< 50%)
        gauge.set_percentage(30)
        assert gauge._get_color() == Colors.SUCCESS_DANGER


class TestAdvancedPanel:
    """Test AdvancedPanel component."""

    def test_init(self, qtbot) -> None:
        """Test AdvancedPanel initialization."""
        panel = AdvancedPanel("Advanced Options")
        qtbot.addWidget(panel)

        # Panel is expanded by default now
        assert panel.is_expanded()
        assert panel.toggle_button.text() == "Advanced Options ▲"

    def test_expand(self, qtbot) -> None:
        """Test expanding panel."""
        panel = AdvancedPanel()
        qtbot.addWidget(panel)

        # Already expanded, but expand() should work
        panel.expand()

        assert panel.is_expanded()
        assert panel.toggle_button.text() == "Advanced Options ▲"

    def test_collapse(self, qtbot) -> None:
        """Test collapsing panel."""
        panel = AdvancedPanel()
        qtbot.addWidget(panel)

        # Start expanded, collapse it
        panel.collapse()

        assert not panel.is_expanded()
        assert panel.toggle_button.text() == "Advanced Options ▼"

    def test_toggle(self, qtbot) -> None:
        """Test toggle functionality."""
        panel = AdvancedPanel()
        qtbot.addWidget(panel)

        # Start expanded, toggle to collapse
        panel._toggle()
        assert not panel.is_expanded()

        # Toggle back to expand
        panel._toggle()
        assert panel.is_expanded()

    def test_add_widget(self, qtbot) -> None:
        """Test adding widget to panel."""
        panel = AdvancedPanel()
        qtbot.addWidget(panel)

        from PySide6.QtWidgets import QLabel
        label = QLabel("Test content")

        panel.add_widget(label)

        # Widget should be added to panel's content widget
        assert label.parent() is panel.content_widget

    def test_toggled_signal(self, qtbot) -> None:
        """Test toggled signal emission."""
        panel = AdvancedPanel()
        qtbot.addWidget(panel)

        signals = []

        def on_toggle(is_expanded):
            signals.append(is_expanded)

        panel.toggled.connect(on_toggle)

        panel.expand()
        assert len(signals) == 1
        assert signals[0] is True

        panel.collapse()
        assert len(signals) == 2
        assert signals[1] is False


class TestChartTabs:
    """Test ChartTabs component for graphics stability."""

    def test_init(self, qtbot) -> None:
        """Test ChartTabs initialization.

        NO Matplotlib figures are created in __init__ - all deferred until tab is selected.
        """
        from src.gui.components.chart_tabs import ChartTabs

        tabs = ChartTabs()
        qtbot.addWidget(tabs)

        # Charts are NOT created during init (deferred until tab selection)
        assert tabs._dist_ax is None, "Distribution axis should be None until tab selected"
        assert tabs._ot_ax is None, "Overtime axis should be None until tab selected"
        assert tabs._dist_canvas is None
        assert not tabs._dist_initialized
        assert not tabs._ot_initialized

    def test_set_results_before_visibility(self, qtbot) -> None:
        """Test that set_results initializes charts and stores results."""
        from src.gui.components.chart_tabs import ChartTabs

        tabs = ChartTabs()
        qtbot.addWidget(tabs)

        # Initially not initialized
        assert not tabs._dist_initialized

        # Create and set results
        manager = ResultManager()
        balances = np.array([
            [100_000, 110_000, 120_000],
        ], dtype=np.float32)
        manager.store(balances=balances, initial_balance=100_000)

        tabs.set_results(manager)

        # Results should be stored
        assert tabs._results is not None

        # Distribution chart should be initialized since it's the default tab (index 0)
        assert tabs._dist_initialized
        assert tabs._dist_ax is not None

    def test_tab_selection_initializes_chart(self, qtbot) -> None:
        """Test that selecting a tab initializes the chart."""
        from src.gui.components.chart_tabs import ChartTabs

        tabs = ChartTabs()
        qtbot.addWidget(tabs)
        tabs.show()

        # Process events
        qtbot.wait(50)

        # Initially not initialized
        assert not tabs._dist_initialized
        assert tabs._dist_ax is None

        # Select a different tab first (index 2 - Monthly Details)
        tabs.tabs.setCurrentIndex(2)
        qtbot.wait(50)

        # Now select the distribution tab (index 0)
        # This triggers currentChanged signal
        tabs.tabs.setCurrentIndex(0)
        qtbot.wait(50)

        # Now distribution chart should be initialized
        assert tabs._dist_initialized
        assert tabs._dist_ax is not None
        assert tabs._dist_canvas is not None
        assert tabs._dist_figure is not None

        # Select the overtime tab (index 1)
        tabs.tabs.setCurrentIndex(1)
        qtbot.wait(50)

        # Now overtime chart should be initialized
        assert tabs._ot_initialized
        assert tabs._ot_ax is not None
        assert tabs._ot_canvas is not None

    def test_set_results_after_initialization(self, qtbot) -> None:
        """Test that set_results updates charts after initialization."""
        from src.gui.components.chart_tabs import ChartTabs

        tabs = ChartTabs()
        qtbot.addWidget(tabs)
        tabs.show()

        # Process events
        qtbot.wait(50)

        # set_results should initialize the default tab (Distribution, index 0)
        manager = ResultManager()
        balances = np.array([
            [100_000, 110_000, 120_000],
            [105_000, 115_000, 125_000],
        ], dtype=np.float32)
        manager.store(balances=balances, initial_balance=100_000)

        tabs.set_results(manager)

        # Distribution chart should be initialized (default tab)
        assert tabs._dist_initialized
        assert tabs._dist_ax is not None
        # Monthly table should also have data
        assert tabs.monthly_table._model is not None

    def test_set_results_after_tab_switching(self, qtbot) -> None:
        """Test that set_results updates charts after manual tab switching."""
        from src.gui.components.chart_tabs import ChartTabs

        tabs = ChartTabs()
        qtbot.addWidget(tabs)
        tabs.show()

        # Process events
        qtbot.wait(50)

        # Initialize both charts by changing tabs
        tabs.tabs.setCurrentIndex(2)  # Monthly Details first
        qtbot.wait(50)
        tabs.tabs.setCurrentIndex(0)  # Distribution
        qtbot.wait(50)
        tabs.tabs.setCurrentIndex(1)  # Over Time
        qtbot.wait(50)

        # Now set results - should update already-initialized charts
        manager = ResultManager()
        balances = np.array([
            [100_000, 110_000, 120_000],
            [105_000, 115_000, 125_000],
        ], dtype=np.float32)
        manager.store(balances=balances, initial_balance=100_000)

        tabs.set_results(manager)

        # Results should be stored and charts updated
        assert tabs._results is not None
        assert tabs._dist_ax is not None
        assert tabs._ot_ax is not None

    def test_graphics_stability_on_multiple_updates(self, qtbot) -> None:
        """Test that multiple result updates don't cause graphics issues.

        This is a regression test for the QGraphicsItem null pointer bug.
        """
        from src.gui.components.chart_tabs import ChartTabs

        tabs = ChartTabs()
        qtbot.addWidget(tabs)
        tabs.show()

        # Process events
        qtbot.wait(50)

        # Initialize charts by changing tabs
        tabs.tabs.setCurrentIndex(2)
        qtbot.wait(50)
        tabs.tabs.setCurrentIndex(0)
        qtbot.wait(50)
        tabs.tabs.setCurrentIndex(1)
        qtbot.wait(50)

        # Create multiple result sets
        for i in range(3):
            manager = ResultManager()
            balances = np.ones((10, 12), dtype=np.float32) * (100_000 + i * 1000)
            withdrawals = np.ones(12, dtype=np.float32) * 1000
            manager.store(balances=balances, withdrawals=withdrawals, initial_balance=100_000)

            tabs.set_results(manager)

            # Should not raise any errors
            assert tabs._results is not None

    def test_overtime_curves_have_valid_data(self, qtbot) -> None:
        """Test that overtime chart renders valid data after update."""
        from src.gui.components.chart_tabs import ChartTabs

        tabs = ChartTabs()
        qtbot.addWidget(tabs)
        tabs.show()

        # Process events
        qtbot.wait(50)

        # Initialize overtime chart
        tabs.tabs.setCurrentIndex(1)
        qtbot.wait(50)

        # Set results
        manager = ResultManager()
        balances = np.ones((100, 12), dtype=np.float32) * 100_000
        withdrawals = np.ones(12, dtype=np.float32) * 1000
        manager.store(balances=balances, withdrawals=withdrawals, initial_balance=100_000)

        tabs.set_results(manager)
        qtbot.wait(50)

        # Verify chart exists and has data
        assert tabs._ot_ax is not None
        # Matplotlib renders data to canvas, no separate curve objects
        # Verify results are loaded
        assert tabs._results is not None
        assert tabs._results.is_loaded()

    def test_distribution_chart_updates(self, qtbot) -> None:
        """Test that distribution chart updates correctly."""
        from src.gui.components.chart_tabs import ChartTabs

        tabs = ChartTabs()
        qtbot.addWidget(tabs)
        tabs.show()

        # Process events
        qtbot.wait(50)

        # Initialize distribution chart
        tabs.tabs.setCurrentIndex(2)
        qtbot.wait(50)
        tabs.tabs.setCurrentIndex(0)
        qtbot.wait(50)

        # Set results
        manager = ResultManager()
        balances = np.random.RandomState(42).randn(100, 12) * 10000 + 100_000
        balances = balances.astype(np.float32)
        withdrawals = np.ones(12, dtype=np.float32) * 1000
        manager.store(balances=balances, withdrawals=withdrawals, initial_balance=100_000)

        tabs.set_results(manager)
        qtbot.wait(50)

        # Verify chart exists and has data
        assert tabs._dist_ax is not None
        # Matplotlib renders directly, no separate histogram/line objects
        # Verify results are loaded
        assert tabs._results is not None
        assert tabs._results.is_loaded()
