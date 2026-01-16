"""Expandable advanced options panel component.

This module provides a collapsible panel for advanced
simulation parameters.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFrame
)
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QEasingCurve
from typing import Optional

from src.constants import Colors, GUI


class AdvancedPanel(QFrame):
    """Expandable panel for advanced options.

    Collapsed:
    ┌─────────────────────────────┐
    │  Advanced Options      [▼]  │
    └─────────────────────────────┘

    Expanded:
    ┌─────────────────────────────┐
    │  Advanced Options      [▲]  │
    ├─────────────────────────────┤
    │  [Advanced content here]    │
    │                             │
    └─────────────────────────────┘

    Signals:
        toggled: Emitted with (is_expanded) when panel is toggled.
    """

    toggled = Signal(bool)

    def __init__(self, title: str = "Advanced Options", parent: Optional[QWidget] = None):
        """Initialize the advanced panel.

        Args:
            title: Panel title text.
            parent: Parent widget.
        """
        super().__init__(parent)

        self._title_text = title
        self._is_expanded = True  # Start expanded by default
        self._max_height = 600  # Maximum height when expanded

        # Setup panel frame
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER_SEPARATOR};
                border-radius: {GUI.BORDER_RADIUS_MD}px;
            }}
        """)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toggle button
        self.toggle_button = QPushButton(f"{title} ▲")  # Start with up arrow since expanded
        self.toggle_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_PRIMARY};
                text-align: left;
                padding: {GUI.SPACING_MD}px {GUI.SPACING_LG}px;
                font-size: 11pt;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_SECONDARY};
            }}
        """)
        self.toggle_button.clicked.connect(self._toggle)
        layout.addWidget(self.toggle_button)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"background-color: {Colors.BORDER_SEPARATOR}; max-height: 1px;")
        separator.setVisible(True)  # Visible since expanded by default
        layout.addWidget(separator)
        self._separator = separator

        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(
            GUI.SPACING_LG, GUI.SPACING_MD,
            GUI.SPACING_LG, GUI.SPACING_LG
        )
        self.content_widget.setVisible(True)  # Visible since expanded by default
        self.content_widget.setMaximumHeight(16777215)  # No max height when expanded
        layout.addWidget(self.content_widget)

    def _toggle(self) -> None:
        """Toggle expanded state."""
        if self._is_expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self) -> None:
        """Show advanced options."""
        self._is_expanded = True
        self.toggle_button.setText(f"{self._title_text} ▲")
        self._separator.setVisible(True)
        self.content_widget.setVisible(True)
        self.content_widget.setMaximumHeight(16777215)  # Remove max height
        self.toggled.emit(True)

    def collapse(self) -> None:
        """Hide advanced options."""
        self._is_expanded = False
        self.toggle_button.setText(f"{self._title_text} ▼")
        self._separator.setVisible(False)
        self.content_widget.setVisible(False)
        self.content_widget.setMaximumHeight(0)
        self.toggled.emit(False)

    def add_widget(self, widget: QWidget) -> None:
        """Add widget to content area.

        Args:
            widget: Widget to add.
        """
        self.content_layout.addWidget(widget)

    def is_expanded(self) -> bool:
        """Check if panel is expanded.

        Returns:
            True if expanded.
        """
        return self._is_expanded
