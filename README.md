# Portfolio Monte Carlo Simulator

**Can your money last through years of ongoing withdrawals?**

Imagine starting with CNY 1.8 million, withdrawing CNY 10,000 every month, adding CNY 13,000 in annual income, allocating 90% to stocks and 10% to cash, and needing the portfolio to last 23 years. Stock returns vary, cash earns a return, and inflation gradually increases the monthly withdrawals.

The simulator breaks those 23 years into 276 monthly settlements. It then uses different random return sequences to simulate **10,000 possible futures**. Each possible future is called a path, producing 2.76 million monthly balance records in total.

The question is not which stock will rise. It is: **can this cash-flow strategy survive across many different futures?**

## How to read the results

- **Success rate**: the percentage of paths that end with a positive balance. It is not an investment return or a promise about the future.
- **Final-balance distribution**: how much money remains at the end of each path, rather than a single average outcome.
- **Percentile tracks**: how P10, P50 and P90 outcomes change over time, making weaker, median and stronger scenarios visible.
- **Monthly details**: balance, withdrawals, income, cash flow and monthly change, so you can see when the portfolio starts to come under pressure.

All default assumptions are editable. This is an educational scenario-analysis tool, **not investment advice or a forecasting guarantee**.

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

During local verification, the full test run completed with **90 passed and 3 skipped**. The skipped integration tests require a full Qt event loop and are skipped in offscreen mode.

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
