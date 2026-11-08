---
diataxis: reference
purpose: Document unit test execution, parallel testing, property testing, and test order randomization with pytest.
---

# Pytest: Test Framework

[![Tool: pytest](https://img.shields.io/badge/tests-pytest-blue.svg)](https://docs.pytest.org/)

Zenith configures `pytest` with `--import-mode=importlib`, `--strict-config`,
`--strict-markers`, `xfail_strict = true`, doctest execution (`--doctest-modules`), and
zero-warning tolerance (`filterwarnings = error`, including `EncodingWarning` on package
modules).

## Integrated Pytest Plugins

| Plugin                | Role                   | Usage in Zenith                                                                                                                    |
| :-------------------- | :--------------------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| **`pytest-cov`**      | Coverage Integration   | Tracks statement and branch coverage via **[Coverage.py](coverage.md)** (`uv run poe test`).                                       |
| **`pytest-xdist`**    | Parallel Execution     | Distributes tests across CPU cores with work-stealing (`uv run poe test-fast` runs `-n auto --dist=worksteal`).                    |
| **`pytest-randomly`** | Order Randomization    | Shuffles test order on every run to catch shared-state bugs (reproduce a seed with `--randomly-seed=<seed>`).                      |
| **`pytest-sugar`**    | Terminal Output        | Renders progress bars and surfaces assertion failures immediately.                                                                 |
| **`syrupy`**          | Snapshot Testing       | Compares structured outputs against versioned `.ambr` snapshots (`--snapshot-warn-unused`; update via `poe test-snapshot-update`). |
| **`hypothesis`**      | Property-Based Testing | Generates randomized and edge-case inputs via `@given(strategies...)` decorators.                                                  |

## Configuration in Zenith

Configured in `pytest.ini` at the project root:

```python exec="1" result="ini"
import re
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/pytest.ini")
if not path.exists():
    path = Path("pytest.ini")
text = path.read_text(encoding="utf-8")
text = re.sub(r"^# =+[^\n]*\n(?:#[^\n]*\n)*# =+[^\n]*\n+", "", text)
text = text.replace("{{ cookiecutter.package_name }}", "my_project")
print(text.strip())
```

## Key Invocations

```bash
uv run poe test                           # Full suite with 100% coverage
uv run poe test-fast                      # Parallel execution (pytest-xdist)
uv run poe test-lowest                    # Test against lowest-direct bounds
uv run poe test-dist                      # Test against installed wheel
uv run poe test-sdist                     # Test inside extracted sdist
uv run poe test-snapshot-update           # Update Syrupy .ambr snapshots
uv run pytest tests/test_core.py --no-cov # Run a single test file
```

## Upstream Documentation

- [pytest Official Documentation](https://docs.pytest.org/)
- [pytest-xdist Repository](https://github.com/pytest-dev/pytest-xdist)
- [pytest-randomly Repository](https://github.com/pytest-dev/pytest-randomly)
- [Syrupy Snapshot Testing Guide](https://tophat.github.io/syrupy/)
- [Hypothesis Property-Based Testing](https://hypothesis.readthedocs.io/)
