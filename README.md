# Portfolio Monte Carlo Simulator

**一笔资产，在持续支出下能撑多久？**

假设有 180 万本金，每月取出 1 万作为支出，每年再补入 1.3 万收入；90% 放在股票，10% 放在现金，计划维持 23 年。收益会波动，现金也有收益，通胀则让每月支出逐渐增加。

这个项目把未来 23 年拆成 276 个月，每个月依次结算支出、收入、资产收益和通胀，再用不同的随机收益序列模拟 **10,000 种可能的未来**。每一种未来称为一条“路径”，全部路径合计产生 276 万条月度余额记录。

它回答的不是“哪只股票会涨”，而是：**这套现金流规则，在不同未来下还能不能维持下去？**

## 怎样读结果

- **成功率**：到期时余额大于 0 的路径占比。它不是投资收益率，也不代表未来承诺。
- **最终余额分布**：一万条路径最后分别剩下多少钱，而不只看一个平均数。
- **百分位轨迹**：用 P10、P50、P90 观察较差、中间和较好的结果随时间怎样变化。
- **月度明细**：逐月检查余额、支出、收入、现金流和变化，找出资产在哪一年开始承压。

默认参数可以全部修改。这个工具用于教育和情景分析，**不是投资建议或收益预测**。

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
