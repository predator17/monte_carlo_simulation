"""Summary card component for displaying statistics.

This module provides a card widget for displaying a single
statistical value with a title.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import Optional

from src.constants import Colors, GUI


class SummaryCard(QFrame):
    """A card widget displaying a summary statistic.

    Shows a title and a large formatted value.

    Layout:
    ┌─────────────────────┐
    │  Title              │
    │                     │
    │     Value           │
    │                     │
    └─────────────────────┘
    """

    def __init__(
        self,
        title: str,
        value: str,
        subtitle: str = "",
        parent: Optional[QWidget] = None,
    ):
        """Initialize the summary card.

        Args:
            title: Card title text.
            value: Primary value to display.
            subtitle: Optional subtitle text.
            parent: Parent widget.
        """
        super().__init__(parent)

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
        layout.setSpacing(GUI.SPACING_XS)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 9pt;")
        layout.addWidget(self.title_label)

        # Value
        self.value_label = QLabel(value)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.value_label.setFont(font)
        self.value_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.value_label)

        # Subtitle (optional)
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 8pt;")
        self.subtitle_label.setVisible(bool(subtitle))
        layout.addWidget(self.subtitle_label)

        layout.addStretch()

    def update_title(self, title: str) -> None:
        """Update the card title.

        Args:
            title: New title text.
        """
        self.title_label.setText(title)

    def update_value(self, value: str) -> None:
        """Update the displayed value.

        Args:
            value: New value text.
        """
        self.value_label.setText(value)

    def update_subtitle(self, subtitle: str) -> None:
        """Update the subtitle.

        Args:
            subtitle: New subtitle text (empty to hide).
        """
        self.subtitle_label.setText(subtitle)
        self.subtitle_label.setVisible(bool(subtitle))
