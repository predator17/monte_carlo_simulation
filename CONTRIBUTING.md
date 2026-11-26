# Contributing

Thank you for helping improve the Portfolio Monte Carlo Simulator.

## Before changing the model

Read the **Model boundaries** section in `README.md`. This is an educational scenario-analysis tool, not investment advice or a forecasting guarantee. New assumptions, return models and financial interpretations should be documented explicitly.

## Development setup

Use Python 3.14 and install the development dependencies:

```bash
uv sync --extra dev
```

Run the application with `uv run python run.py`. A working display and Qt desktop environment are required for GUI verification.

## Verification

Run the relevant checks before opening a pull request:

```bash
uv run pytest
uv run ruff check .
uv run mypy src
```

When changing simulation logic, include repeatable runs with an explicit random seed, path count and time horizon. When benchmarking, state the hardware and whether initial JIT compilation is included.

When changing the GUI, verify the input, run, chart and monthly-details workflow. Tests that require a display may use a Qt offscreen setup where appropriate.

## Documentation

Update the README and relevant documents when behavior, dependencies or model assumptions change. Do not describe regenerated visualization returns as the same random draws used by the simulation core.

Do not commit generated environments, build outputs, coverage artifacts, credentials or local machine configuration.

## License

By contributing, you agree that your contributions are licensed under the MIT License used by this repository.
