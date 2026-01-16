"""Input configuration page for simulation parameters.

This module provides the input page where users can configure
all simulation parameters.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QScrollArea, QFrame, QProgressBar
)
from PySide6.QtCore import Signal, Qt
from typing import Optional

from src.config import SimulationConfig
from src.constants import GUI, Fonts, Colors
from src.gui.components.param_card import ParamCard
from src.gui.components.advanced_panel import AdvancedPanel


class InputPage(QWidget):
    """Input configuration page.

    Displays parameter input cards for configuring the simulation.
    Includes an expandable advanced options panel.

    Signals:
        run_requested: Emitted with SimulationConfig when run is clicked.
    """

    run_requested = Signal(object)

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the input page.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)

        self._is_running = False

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Container widget
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(GUI.SPACING_XL, GUI.SPACING_XL,
                                            GUI.SPACING_XL, GUI.SPACING_XL)
        container_layout.setSpacing(GUI.SPACING_LG)

        # Title
        title = QLabel("Your Portfolio")
        title.setObjectName("headerLabel")
        title.setStyleSheet(f"font-size: {Fonts.HEADER}pt; font-weight: bold; "
                          f"color: {Colors.TEXT_PRIMARY};")
        container_layout.addWidget(title)

        # Basic parameter cards (2x3 grid)
        cards_layout = QGridLayout()
        cards_layout.setSpacing(GUI.SPACING_MD)

        # Row 1
        # Get defaults from SimulationConfig to avoid duplication
        default_config = SimulationConfig()
        self.initial_balance_card = ParamCard(
            "Starting Balance",
            default_config.initial_balance,
            "CNY",
            min_value=0,
            max_value=100_000_000,
            is_slider=True,
            step_size=50_000,  # 50k steps for large amounts
        )
        self.monthly_withdrawal_card = ParamCard(
            "Monthly Withdrawal",
            default_config.monthly_withdrawal,
            "CNY",
            min_value=0,
            max_value=1_000_000,
            is_slider=True,
            step_size=1_000,  # 1k steps
        )
        self.time_horizon_card = ParamCard(
            "Time Horizon",
            default_config.time_horizon_years,
            "years",
            min_value=1,
            max_value=50,
            integer=True,
            is_slider=True,
            step_size=1,  # 1 year steps
        )

        # Row 2
        self.stock_allocation_card = ParamCard(
            "Stock Allocation",
            default_config.stock_allocation,
            "%",
            min_value=0,
            max_value=100,
            integer=True,
            is_slider=True,
            step_size=1,  # 1% steps
        )
        self.expected_return_card = ParamCard(
            "Expected Return",
            default_config.expected_return,
            "%",
            min_value=-50,
            max_value=100,
            is_slider=True,
            step_size=0.1,  # 0.1% steps
        )
        self.annual_income_card = ParamCard(
            "Annual Income",
            default_config.annual_income,
            "CNY",
            min_value=0,
            max_value=10_000_000,
            is_slider=True,
            step_size=1_000,  # 1k steps to match default 13k
        )

        # Add cards to grid
        cards_layout.addWidget(self.initial_balance_card, 0, 0)
        cards_layout.addWidget(self.monthly_withdrawal_card, 0, 1)
        cards_layout.addWidget(self.time_horizon_card, 0, 2)
        cards_layout.addWidget(self.stock_allocation_card, 1, 0)
        cards_layout.addWidget(self.expected_return_card, 1, 1)
        cards_layout.addWidget(self.annual_income_card, 1, 2)

        container_layout.addLayout(cards_layout)

        # Advanced options panel
        self.advanced_panel = AdvancedPanel("Advanced Options")

        # Advanced cards - use defaults from SimulationConfig
        adv_cards_layout = QGridLayout()
        adv_cards_layout.setSpacing(GUI.SPACING_MD)

        self.stock_volatility_card = ParamCard(
            "Stock Volatility",
            default_config.stock_volatility,
            "%",
            min_value=0,
            max_value=100,
            is_slider=True,
            step_size=0.1,  # 0.1% steps
        )
        self.cash_return_card = ParamCard(
            "Cash Return",
            default_config.cash_return,
            "%",
            min_value=-50,
            max_value=50,
            is_slider=True,
            step_size=0.01,  # 0.01% steps for precision
        )
        self.inflation_rate_card = ParamCard(
            "Inflation Rate",
            default_config.inflation_rate,
            "%",
            min_value=0,
            max_value=50,
            is_slider=True,
            step_size=0.1,  # 0.1% steps
        )
        self.num_paths_card = ParamCard(
            "Number of Paths",
            default_config.num_paths,
            "",
            min_value=100,
            max_value=100_000,
            integer=True,
            is_slider=True,
            step_size=500,  # 500 steps
        )

        adv_cards_layout.addWidget(self.stock_volatility_card, 0, 0)
        adv_cards_layout.addWidget(self.cash_return_card, 0, 1)
        adv_cards_layout.addWidget(self.inflation_rate_card, 0, 2)
        adv_cards_layout.addWidget(self.num_paths_card, 1, 0, 1, 3)

        # Add advanced cards to panel
        adv_widget = QWidget()
        adv_widget.setLayout(adv_cards_layout)
        self.advanced_panel.add_widget(adv_widget)

        container_layout.addWidget(self.advanced_panel)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        container_layout.addWidget(self.progress_bar)

        # Status label (hidden by default)
        self.status_label = QLabel()
        self.status_label.setVisible(False)
        self.status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        container_layout.addWidget(self.status_label)

        # Run button
        self.run_button = ParamCard.create_run_button()
        self.run_button.clicked.connect(self._on_run_clicked)
        container_layout.addWidget(self.run_button, 0, Qt.AlignmentFlag.AlignCenter)

        # Add stretch at bottom
        container_layout.addStretch()

        scroll.setWidget(container)
        layout.addWidget(scroll)

    def _on_run_clicked(self) -> None:
        """Handle run button click."""
        config = self.get_config()
        self.run_requested.emit(config)

    def get_config(self) -> SimulationConfig:
        """Get current configuration from input fields.

        Returns:
            SimulationConfig with current values.
        """
        return SimulationConfig(
            initial_balance=self.initial_balance_card.get_value(),
            monthly_withdrawal=self.monthly_withdrawal_card.get_value(),
            stock_allocation=self.stock_allocation_card.get_value(),
            time_horizon_years=int(self.time_horizon_card.get_value()),
            expected_return=self.expected_return_card.get_value(),
            annual_income=self.annual_income_card.get_value(),
            stock_volatility=self.stock_volatility_card.get_value(),
            cash_return=self.cash_return_card.get_value(),
            inflation_rate=self.inflation_rate_card.get_value(),
            num_paths=int(self.num_paths_card.get_value()),
        )

    def set_config(self, config: SimulationConfig) -> None:
        """Update input fields from configuration.

        Args:
            config: Configuration to apply.
        """
        self.initial_balance_card.set_value(config.initial_balance)
        self.monthly_withdrawal_card.set_value(config.monthly_withdrawal)
        self.stock_allocation_card.set_value(config.stock_allocation)
        self.time_horizon_card.set_value(config.time_horizon_years)
        self.expected_return_card.set_value(config.expected_return)
        self.annual_income_card.set_value(config.annual_income)
        self.stock_volatility_card.set_value(config.stock_volatility)
        self.cash_return_card.set_value(config.cash_return)
        self.inflation_rate_card.set_value(config.inflation_rate)
        self.num_paths_card.set_value(config.num_paths)

    def set_running(self, running: bool) -> None:
        """Set the running state.

        Args:
            running: True if simulation is running.
        """
        self._is_running = running
        self.run_button.setEnabled(not running)

        if running:
            self.progress_bar.setVisible(True)
            self.status_label.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("Initializing...")
        else:
            self.progress_bar.setVisible(False)
            self.status_label.setVisible(False)

    def update_progress(self, current: int, total: int, message: str) -> None:
        """Update progress bar.

        Args:
            current: Current progress value.
            total: Total progress value.
            message: Progress message.
        """
        if total > 0:
            percent = int((current / total) * 100)
            self.progress_bar.setValue(percent)
        self.status_label.setText(message)
