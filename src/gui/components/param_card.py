"""Parameter card component for input display.

This module provides a reusable card widget for displaying
and editing single simulation parameters.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSpinBox, QDoubleSpinBox,
    QSlider, QPushButton, QFrame, QLineEdit
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from typing import Optional

from src.constants import Colors, GUI


class ParamCard(QFrame):
    """A card widget displaying a single parameter.

    Layout:
    ┌─────────────────────┐
    │  Label              │
    │                     │
    │    Value            │
    │    [Editor]         │
    │                     │
    │  Unit               │
    └─────────────────────┘

    Signals:
        value_changed: Emitted when value changes.
    """

    value_changed = Signal(object)

    # Slider resolution - higher = smoother, lower = more discrete steps
    SLIDER_STEPS = 10_000

    def __init__(
        self,
        label: str,
        value: float,
        unit: str = "",
        min_value: float = 0,
        max_value: float = 100_000_000,
        integer: bool = False,
        is_slider: bool = False,
        step_size: float | None = None,
        parent: Optional[QWidget] = None,
    ):
        """Initialize the parameter card.

        Args:
            label: Parameter label text.
            value: Initial value.
            unit: Unit suffix (e.g., "%", "CNY").
            min_value: Minimum allowed value.
            max_value: Maximum allowed value.
            integer: True for integer values only.
            is_slider: True to use slider instead of spinbox.
            step_size: Slider step size (auto-calculated if None).
            parent: Parent widget.
        """
        super().__init__(parent)

        self._label_text = label
        self._unit = unit
        self._min_value = min_value
        self._max_value = max_value
        self._integer = integer
        self._value = value
        self._step_size = step_size

        # Setup card frame
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER_SEPARATOR};
                border-radius: {GUI.BORDER_RADIUS_MD}px;
            }}
        """)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(GUI.CARD_PADDING, GUI.CARD_PADDING,
                                  GUI.CARD_PADDING, GUI.CARD_PADDING)
        layout.setSpacing(GUI.SPACING_SM)

        # Label
        self.label_widget = QLabel(label)
        self.label_widget.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 10pt;")
        self.label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_widget)

        # Value display
        self.value_label = QLabel(self._format_value(value))
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.value_label.setFont(font)
        self.value_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Enable double-click to edit
        self.value_label.setProperty("valueLabel", True)
        layout.addWidget(self.value_label)

        # Line edit for manual value entry (hidden by default)
        self.value_edit = QLineEdit(self._format_edit_value(value))
        self.value_edit.setVisible(False)
        self.value_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_FOCUS};
                border-radius: {GUI.BORDER_RADIUS_SM}px;
                padding: 6px 12px;
                font-size: 18pt;
                font-weight: bold;
            }}
        """)
        layout.addWidget(self.value_edit)

        # Install event filter for double-click on value label
        self.value_label.installEventFilter(self)

        # Connect edit signals
        self.value_edit.editingFinished.connect(self._on_edit_finished)
        self.value_edit.returnPressed.connect(self._on_edit_finished)

        # Editor
        if is_slider:
            self.editor = self._create_slider()
        else:
            self.editor = self._create_spinbox()
        layout.addWidget(self.editor)

        # Unit
        if unit:
            self.unit_label = QLabel(unit)
            self.unit_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 9pt;")
            self.unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(self.unit_label)

        layout.addStretch()

    def _create_spinbox(self) -> QSpinBox | QDoubleSpinBox:
        """Create a spinbox editor.

        Returns:
            Spinbox widget configured for this parameter.
        """
        if self._integer:
            editor = QSpinBox()
            editor.setRange(int(self._min_value), int(self._max_value))
            editor.setValue(int(self._value))
            editor.setSingleStep(1)
        else:
            editor = QDoubleSpinBox()
            editor.setRange(self._min_value, self._max_value)
            editor.setValue(self._value)
            editor.setSingleStep(0.1)
            editor.setDecimals(2)

        editor.setStyleSheet(f"""
            QSpinBox, QDoubleSpinBox {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_INPUT};
                border-radius: {GUI.BORDER_RADIUS_SM}px;
                padding: 6px 12px;
                font-size: 11pt;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 1px solid {Colors.BORDER_FOCUS};
            }}
        """)
        editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        editor.valueChanged.connect(self._on_value_changed)

        return editor

    def _create_slider(self) -> QWidget:
        """Create a slider editor widget.

        Uses normalized 0-SLIDER_STEPS range mapped to actual value range
        for proper sensitivity across different value ranges.

        Returns:
            Slider widget with value display.
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(GUI.SPACING_XS)

        slider = QSlider(Qt.Orientation.Horizontal)
        # Use normalized range for consistent sensitivity
        slider.setRange(0, self.SLIDER_STEPS)
        slider.setValue(self._value_to_slider_pos(self._value))
        slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background-color: {Colors.BG_SECONDARY};
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background-color: {Colors.ACCENT_BLUE};
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -7px 0;
            }}
            QSlider::handle:horizontal:hover {{
                background-color: {Colors.ACCENT_BLUE_HOVER};
            }}
            QSlider::sub-page:horizontal {{
                background-color: {Colors.ACCENT_BLUE};
                border-radius: 2px;
            }}
        """)
        slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(slider)

        # Store slider reference
        self._slider = slider
        container.slider = slider

        return container

    def _value_to_slider_pos(self, value: float) -> int:
        """Convert actual value to slider position.

        Args:
            value: Actual value.

        Returns:
            Slider position (0 to SLIDER_STEPS).
        """
        range_size = self._max_value - self._min_value
        if range_size == 0:
            return 0
        ratio = (value - self._min_value) / range_size
        return int(ratio * self.SLIDER_STEPS)

    def _slider_pos_to_value(self, pos: int) -> float:
        """Convert slider position to actual value.

        Args:
            pos: Slider position (0 to SLIDER_STEPS).

        Returns:
            Actual value.
        """
        ratio = pos / self.SLIDER_STEPS
        value = self._min_value + ratio * (self._max_value - self._min_value)

        # Apply step size quantization if specified
        if self._step_size is not None and self._step_size > 0:
            steps = round(value / self._step_size)
            value = steps * self._step_size

        # Clamp to range
        value = max(self._min_value, min(self._max_value, value))

        # Round to integer if needed
        if self._integer:
            value = round(value)

        return value

    def _on_value_changed(self, value: float) -> None:
        """Handle value change from spinbox.

        Args:
            value: New value.
        """
        self._value = value
        self.value_label.setText(self._format_value(value))
        self.value_changed.emit(value)

    def _on_slider_changed(self, slider_pos: int) -> None:
        """Handle value change from slider.

        Args:
            slider_pos: New slider position.
        """
        value = self._slider_pos_to_value(slider_pos)
        self._value = value
        self.value_label.setText(self._format_value(value))
        self.value_changed.emit(value)

    def _format_value(self, value: float) -> str:
        """Format value for display.

        Args:
            value: Value to format.

        Returns:
            Formatted string.
        """
        if self._integer:
            return f"{int(value):,}"
        else:
            return f"{value:,.2f}"

    def set_value(self, value: float) -> None:
        """Update value display and editor.

        Args:
            value: New value.
        """
        self._value = value
        self.value_label.setText(self._format_value(value))

        # Update editor
        if hasattr(self, '_slider'):
            self._slider.blockSignals(True)
            self._slider.setValue(self._value_to_slider_pos(value))
            self._slider.blockSignals(False)
        elif hasattr(self.editor, 'setValue'):
            self.editor.blockSignals(True)
            self.editor.setValue(value)
            self.editor.blockSignals(False)

    def get_value(self) -> float:
        """Get current value from editor.

        Returns:
            Current value.
        """
        if hasattr(self, '_slider'):
            return self._slider_pos_to_value(self._slider.value())
        elif hasattr(self.editor, 'value'):
            return float(self.editor.value())
        return self._value

    def eventFilter(self, obj, event) -> bool:
        """Filter events for double-click on value label.

        Args:
            obj: Object receiving the event.
            event: Event object.

        Returns:
            True if event was handled, False otherwise.
        """
        if obj == self.value_label and event.type() == event.Type.MouseButtonDblClick:
            self._enter_edit_mode()
            return True
        return super().eventFilter(obj, event)

    def _enter_edit_mode(self) -> None:
        """Enter edit mode by showing line edit and hiding value label."""
        self.value_label.setVisible(False)
        self.value_edit.setText(self._format_edit_value(self._value))
        self.value_edit.setVisible(True)
        self.value_edit.selectAll()
        self.value_edit.setFocus()

    def _exit_edit_mode(self) -> None:
        """Exit edit mode by showing value label and hiding line edit."""
        self.value_edit.setVisible(False)
        self.value_label.setVisible(True)

    def _on_edit_finished(self) -> None:
        """Handle edit finished (Enter pressed or focus lost).

        Parses the entered value and updates the parameter.
        """
        text = self.value_edit.text().strip()
        if not text:
            # If empty, revert to current value
            self._exit_edit_mode()
            return

        try:
            # Remove commas and convert to float
            clean_text = text.replace(',', '').replace('¥', '').replace('%', '').strip()
            new_value = float(clean_text)

            # Clamp to valid range
            new_value = max(self._min_value, min(self._max_value, new_value))

            # Apply step size quantization if specified
            if self._step_size is not None and self._step_size > 0:
                steps = round(new_value / self._step_size)
                new_value = steps * self._step_size

            # Round to integer if needed
            if self._integer:
                new_value = round(new_value)

            # Update value
            self._value = new_value
            self.value_label.setText(self._format_value(new_value))
            self.value_changed.emit(new_value)

            # Update slider/spinbox if exists
            if hasattr(self, '_slider'):
                self._slider.blockSignals(True)
                self._slider.setValue(self._value_to_slider_pos(new_value))
                self._slider.blockSignals(False)
            elif hasattr(self.editor, 'setValue'):
                self.editor.blockSignals(True)
                self.editor.setValue(new_value)
                self.editor.blockSignals(False)

        except (ValueError, AttributeError):
            # If invalid input, revert to display of current value
            pass

        self._exit_edit_mode()

    def _format_edit_value(self, value: float) -> str:
        """Format value for editing in line edit.

        Args:
            value: Value to format.

        Returns:
            String without formatting (no commas, etc.).
        """
        if self._integer:
            return str(int(value))
        else:
            # Show up to 2 decimal places, remove trailing zeros
            return f"{value:.2f}".rstrip('0').rstrip('.')

    @staticmethod
    def create_run_button(text: str = "Run Simulation") -> QPushButton:
        """Create a styled run button.

        Args:
            text: Button text.

        Returns:
            Styled QPushButton.
        """
        button = QPushButton(text)
        button.setFixedHeight(48)
        button.setMinimumWidth(200)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_BLUE};
                color: {Colors.TEXT_PRIMARY};
                border: none;
                border-radius: {GUI.BORDER_RADIUS_MD}px;
                padding: 12px 32px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.ACCENT_BLUE_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.ACCENT_BLUE_PRESSED};
            }}
            QPushButton:disabled {{
                background-color: {Colors.BORDER_SEPARATOR};
                color: {Colors.TEXT_DISABLED};
            }}
        """)
        return button
