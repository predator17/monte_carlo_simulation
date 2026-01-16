# Portfolio Monte Carlo Simulator

A high-performance Monte Carlo simulation tool for portfolio sustainability analysis with an interactive dark-mode GUI.

## Features

- **High-Performance Simulation**: Numba JIT compilation for 100-1000x speedup
- **Interactive GUI**: PySide6-based dark theme interface
- **Real-time Visualization**: PyQtGraph GPU-accelerated charts
- **Lazy Loading Table**: Display 2.76M+ data points efficiently
- **Monthly Granularity**: 276 data points per path (23 years × 12 months)

## Installation

### Using Conda

```bash
# Create conda environment
conda create -n portfolio-sim python=3.12 -y
conda activate portfolio-sim

# Install dependencies
pip install -r requirements.txt
```

### Using Virtualenv (Alternative)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

From the project root:

```bash
python run.py
```

Or using the module:

```bash
python -m src
```

## Project Structure

```
Monte_Carlo_Simulation/
├── src/                          # Source code
│   ├── config.py                 # Configuration classes
│   ├── simulation.py             # Numba JIT simulation
│   ├── results.py                # Result manager (Polars)
│   ├── constants.py              # Colors, fonts, constants
│   ├── theme.py                  # Dark mode styling
│   ├── formatters.py             # Currency/number formatting
│   ├── gui/                      # GUI components
│   │   ├── main_window.py        # Main window
│   │   ├── pages/                # Page widgets
│   │   │   ├── input_page.py     # Input configuration
│   │   │   └── results_page.py   # Results display
│   │   ├── components/           # Reusable components
│   │   │   ├── param_card.py     # Parameter card
│   │   │   ├── summary_card.py   # Summary stat card
│   │   │   ├── success_gauge.py  # Donut chart
│   │   │   ├── advanced_panel.py # Expandable panel
│   │   │   └── chart_tabs.py     # Chart container
│   │   ├── models/               # Qt models
│   │   └── workers/              # Worker threads
│   │       └── simulation_worker.py
│   └── utils/                    # Utilities
├── doc/                          # Documentation
│   └── implementation.md         # Implementation plan
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── run.py                        # Convenience launcher
└── README.md                     # This file
```

## Dependencies

### Production

- **PySide6** >= 6.8.0: GUI framework (6.8+ for Python 3.13)
- **pyqtgraph** >= 0.13.3: GPU-accelerated plotting
- **numpy** >= 1.24.0: Numerical computing
- **numba** >= 0.59.0: JIT compilation
- **polars** >= 0.20.0: Fast data analysis
- **pydantic** >= 2.5.0: Configuration validation

### Development

- **pytest** >= 8.0.0: Testing framework
- **pytest-cov** >= 4.1.0: Coverage reporting
- **pytest-qt** >= 4.3.0: GUI testing
- **pytest-benchmark** >= 4.0.0: Performance testing
- **ruff** >= 0.6.0: Linting
- **mypy** >= 1.9.0: Type checking
- **pre-commit** >= 3.6.0: Git hooks

## License

MIT License

## Documentation

See `doc/implementation.md` for detailed implementation documentation including:
- Research findings and best practices
- GUI design mockups
- Architecture specifications
- Component documentation
- Testing strategy
