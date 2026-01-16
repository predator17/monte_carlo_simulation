"""Success gauge donut chart widget.

This module provides a custom donut chart widget for
displaying simulation success rate.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QRadialGradient
from typing import Optional

from src.constants import Colors


class SuccessGauge(QWidget):
    """A donut chart widget for displaying success rate.

    Displays the success rate as a colored arc with percentage
    text in the center.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the success gauge.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)

        self._percentage = 0.0
        self._message = "Portfolio lasts full term"

        # Set default size
        self.setMinimumSize(200, 150)

    def set_percentage(self, percentage: float) -> None:
        """Set the success rate percentage.

        Args:
            percentage: Success rate (0-100).
        """
        self._percentage = max(0, min(100, percentage))
        self.update()

    def set_message(self, message: str) -> None:
        """Set the message displayed below the percentage.

        Args:
            message: Message text.
        """
        self._message = message
        self.update()

    def _get_color(self) -> str:
        """Get color based on percentage.

        Returns:
            Hex color code.
        """
        if self._percentage >= 90:
            return Colors.SUCCESS_HIGH
        elif self._percentage >= 70:
            return Colors.ACCENT_BLUE
        elif self._percentage >= 50:
            return Colors.SUCCESS_LOW
        else:
            return Colors.SUCCESS_DANGER

    def paintEvent(self, event) -> None:
        """Paint the gauge widget.

        Args:
            event: Paint event.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get dimensions
        width = self.width()
        height = self.height()

        # Calculate gauge geometry
        rect = QRectF(20, 20, width - 40, height - 80)

        # Background circle (gray track)
        track_pen = QPen(QColor(Colors.BG_SECONDARY))
        track_pen.setWidth(16)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        painter.setPen(track_pen)
        painter.drawArc(rect, 0, 180 * 16)  # Half circle (top)

        # Get progress color
        color = QColor(self._get_color())

        # Progress arc
        if self._percentage > 0:
            progress_pen = QPen(color)
            progress_pen.setWidth(16)
            progress_pen.setCapStyle(Qt.PenCapStyle.RoundCap)

            painter.setPen(progress_pen)
            # Draw arc from left to right based on percentage
            span_angle = int((self._percentage / 100) * 180 * 16)
            painter.drawArc(rect, 0, span_angle)

        # Percentage text
        painter.setPen(QColor(Colors.TEXT_PRIMARY))

        percent_font = QFont()
        percent_font.setPointSize(24)
        percent_font.setBold(True)
        painter.setFont(percent_font)

        percent_text = f"{self._percentage:.1f}%"
        percent_rect = QRectF(0, height / 2 - 20, width, 40)
        painter.drawText(percent_rect, Qt.AlignmentFlag.AlignCenter, percent_text)

        # Message text
        message_font = QFont()
        message_font.setPointSize(10)
        painter.setFont(message_font)
        painter.setPen(QColor(Colors.TEXT_SECONDARY))

        message_rect = QRectF(0, height / 2 + 20, width, 30)
        painter.drawText(message_rect, Qt.AlignmentFlag.AlignCenter, self._message)
