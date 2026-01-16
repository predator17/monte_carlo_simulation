"""Entry point for the Portfolio Monte Carlo Simulator.

This module provides the main function to launch the application.
"""

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from src.gui.main_window import MainWindow


def main() -> int:
    """Launch the Portfolio Monte Carlo Simulator application.

    Returns:
        Exit code.
    """
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Portfolio Simulator")
    app.setOrganizationName("Quants Playground")

    # Enable high DPI scaling
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
