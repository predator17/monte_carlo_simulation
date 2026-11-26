# Portfolio Monte Carlo Simulator

A desktop simulator for exploring portfolio sustainability under configurable return, withdrawal, income and inflation assumptions.

The default scenario simulates **10,000 paths over 23 years (276 months)**, producing 2.76 million monthly balance values. The application combines a Numba-compiled simulation core with a PySide6 interface, Matplotlib charts and on-demand table loading.

This is an educational and scenario-analysis tool. It is **not investment advice or a forecasting guarantee**.

## Features

- Monthly Monte Carlo simulation with Numba JIT compilation and parallel path processing
- Configurable stock/cash allocation, withdrawals, annual income, inflation and time horizon
- Final-balance distribution, percentile tracks and success-rate summaries
- Matplotlib charts embedded in a PySide6 desktop interface
- Monthly details loaded in batches rather than rendering the full result set at once
- Polars DataFrame and LazyFrame conversion for further analysis
- Optional random seed for repeatable runs

## Model boundaries

- Monthly stock returns are sampled independently from a normal distribution. This is a simplified model, not a complete market model.
- Taxes, transaction costs, changing correlations, sequential rebalancing rules and asset-specific behavior are outside the current scope.
- `simulate_with_history` regenerates a stock-return series for visualization. Those draws are not the same random draws used inside the simulation core.
- JIT speed depends on the hardware, path count and whether compilation time is included. The repository does not claim a universal acceleration multiplier.
- A display and working Qt desktop environment are required to run the GUI. The application is not a headless web service.

## Requirements

- Python 3.14
- `uv` for the recommended setup
- A desktop environment supported by PySide6

The original project configuration targets Python 3.14. Other Python versions are not covered by the current dependency configuration and have not been verified.

## Install and run

```bash
uv sync --extra dev
uv run python run.py
```

The package also exposes a launcher:

```bash
uv run portfolio-simulator
```

For a pip-based workflow:

```bash
python -m pip install -e ".[dev]"
python run.py
```

## Tests and quality checks

```bash
uv run pytest
uv run ruff check .
uv run mypy src
```

The test suite covers configuration, simulation, result handling and GUI-related behavior. Tests that require a graphical environment may need a display or a Qt offscreen setup.

## Project structure

```text
src/
  config.py             Validated simulation parameters
  simulation.py         Numba-compiled path simulation
  results.py            Result storage, statistics and lazy data access
  gui/
    main_window.py
    pages/              Input and result pages
    components/         Charts, cards and advanced controls
    models/             On-demand monthly table model
    workers/            Background simulation workers
  utils/                Validation and shared helpers
tests/                  Configuration, simulation, results and GUI tests
doc/implementation.md  Original design and research notes
```

## Reproducibility

`SimulationConfig` accepts an optional `random_seed`. Use it when comparing parameter sets or reporting an experiment. The underlying Numba function also supports cached, parallel execution, so timing should state the hardware and whether the first compilation is included.

## Contributing

Read `CONTRIBUTING.md` before changing the simulation model, GUI or dependency setup. Reproducible tests and clear documentation of model assumptions are especially valuable.

## License

Released under the MIT License. See `LICENSE`.
