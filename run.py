#!/usr/bin/env python3
"""Convenience launcher for the Portfolio Monte Carlo Simulator.

This script can be run from anywhere to launch the application.
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.__main__ import main

if __name__ == "__main__":
    sys.exit(main())
