# UV Setup Guide

## Prerequisites

- UV package manager (v0.9.22+)
- Python 3.14

## Quick Start

### 1. Install Dependencies

```bash
# Install production dependencies
uv sync

# Install with dev dependencies (recommended for development)
uv sync --all-extras
```

### 2. Activate Virtual Environment

```bash
# Linux/macOS
source .venv/bin/activate

# Or with UV
uv shell
```

### 3. Run the Application

```bash
# Using UV
uv run python -m src

# Or using the installed script
uv run portfolio-simulator

# Or directly with Python (after activation)
python -m src
```

## Development Workflow

### Running Tests

```bash
# Run all tests with coverage
uv run pytest --cov=src --cov-report=html --cov-report=term

# Run specific test file
uv run pytest tests/test_simulation.py -v

# Run GUI tests (requires display)
uv run pytest tests/test_gui/ -v

# Run tests excluding GUI/offscreen
uv run pytest tests/ -v -m "not gui"
```

### Code Quality Checks

```bash
# Lint with Ruff
uv run ruff check .

# Format code with Ruff
uv run ruff format .

# Type checking with MyPy
uv run mypy src/

# Run all quality checks
uv run ruff check . && uv run mypy src/
```

### Adding Dependencies

```bash
# Add a runtime dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name

# Example: Add a new package
uv add requests@^2.0

# Example: Add dev tool
uv add --dev black
```

## Project Structure

```
.
├── pyproject.toml      # UV project configuration
├── .python-version     # Python version specification (3.14)
├── requirements.txt    # Legacy requirements.txt (for pip compatibility)
├── uv.lock            # Auto-generated lock file (add to .gitignore)
├── src/               # Source code
│   ├── __main__.py    # Entry point
│   ├── config.py      # Configuration with Pydantic
│   ├── simulation.py  # Monte Carlo simulation with Numba JIT
│   ├── results.py     # Result manager with Polars
│   └── gui/           # GUI components (PySide6)
└── tests/             # Test files
```

## Configuration Files

### pyproject.toml

Contains all project configuration:
- Dependencies and dev dependencies
- Ruff configuration (linting/formatting)
- MyPy configuration (type checking)
- Pytest configuration (testing)
- Coverage configuration

### Tool Settings

#### Ruff (Linter & Formatter)
- Line length: 79 characters
- Single quotes for strings
- Auto-fix enabled
- Python 3.14 target

#### MyPy (Type Checker)
- Python 3.14
- Strict mode with some relaxations
- Ignore missing imports for external packages

#### Pytest
- Qt API: PySide6
- Coverage reporting enabled
- Markers: slow, integration, gui

## Common Commands

### Environment Management

```bash
# Create/Update virtual environment
uv sync

# Remove virtual environment
uv venv --clear

# Check Python version
uv python --version

# List installed packages
uv pip list
```

### Building and Distribution

```bash
# Build package
uv build

# Install in editable mode
uv pip install -e .
```

## Troubleshooting

### Issue: UV not found

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Issue: Python version not matching

```bash
# Set Python version explicitly
uv python set 3.14

# Or specify full path
uv python pin /home/predator/.local/share/uv/python/cpython-3.14.2-linux-x86_64-gnu/bin/python3.14
```

### Issue: GUI tests fail on WSL2

```bash
# Tests use offscreen mode automatically
# If you see display errors, set:
export QT_QPA_PLATFORM=offscreen
```

## IDE Integration

### VS Code

Install these extensions:
- Python (Microsoft)
- Ruff (charliermarsh)

Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.linting.enabled": false,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```

### PyCharm

1. File → Settings → Project → Python Interpreter
2. Add Local Interpreter → Select `.venv/bin/python`
3. Enable Ruff plugin for linting/formatting
