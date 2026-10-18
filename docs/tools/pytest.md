# pytest: Test Framework

[![Tool: pytest](https://img.shields.io/badge/tests-pytest-blue.svg)](https://docs.pytest.org/)

`pytest` is the foundational testing framework for Python applications and libraries. Zenith enhances pytest with an integrated ecosystem of specialized plugins that enforce assertion rigor, prevent state flakiness, and accelerate parallel execution.

---

## What It Does

`pytest` provides a powerful, fixture-driven testing engine with deep assertion introspection. Tests are authored as idiomatic Python functions, leveraging dependency injection via fixtures, parameterized test matrices, and comprehensive filter mechanisms to target specific subsystems.

Zenith configures pytest with strict validation flags: tests must declare valid markers, configuration files are strictly validated, doctests inside source docstrings are automatically discovered and executed, and unused snapshot assertions trigger warnings.

---

## Why It's in Zenith

Testing in Zenith is designed to eliminate false confidence. Beyond standard unit assertions, pytest operates under a strict zero-warning tolerance policy (`filterwarnings = "error"`). Deprecation notices, unclosed resources, or encoding anomalies fail the test suite immediately.

By pairing pytest with specialized plugins, Zenith transforms the test runner into a comprehensive behavioral verification engine. Parallel test execution keeps local developer loops fast, randomized ordering eliminates state pollution, and snapshot and property-based plugins catch edge-case regressions that manual test cases often overlook.

---

## Integrated pytest Plugins

Zenith integrates a curated set of plugins into the test environment:

| Plugin | Role | Primary Guarantee |
|---|---|---|
| **`pytest-cov`** | Coverage Integration | Bridges pytest with **[Coverage.py](coverage.md)** to track execution and enforce 100% statement and branch coverage. |
| **`pytest-xdist`** | Parallel Execution | Distributes test runs across available CPU cores (`uv run poe test-fast` via `-n auto`), accelerating local and CI feedback loops. |
| **`pytest-randomly`** | Test Order Shuffling | Randomizes execution sequences on every run to detect global state leakage, unclosed resources, or order-dependent assertions. |
| **`pytest-sugar`** | Terminal Diagnostics | Replaces default dot progress with an interactive progress meter and surfaces test failures immediately as they occur. |
| **`syrupy`** | Snapshot Testing | Provides declarative snapshot fixtures (`snapshot`) that assert structured outputs (CLI menus, JSON payloads, AST trees) against versioned `.ambr` files. |
| **`hypothesis`** | Property-Based Testing | Generates hundreds of pseudo-random inputs to find hidden edge cases, boundary errors, and numeric overflow traps across algorithmic functions. |

---

## Configuration in Zenith

Configured in `pytest.ini` at the project root:

```python exec="1" result="ini"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/pytest.ini")
if not path.exists():
    path = Path("pytest.ini")
print(path.read_text().strip())
```

---

## Key Invocations

```bash
uv run poe test                 # Run complete test suite with 100% coverage
uv run poe test-fast            # Run tests in parallel with pytest-xdist
uv run poe test-lowest          # Verify against lowest-direct dependencies
uv run poe test-snapshot-update # Update Syrupy snapshots (.ambr files)
uv run pytest -k "test_filter"  # Run filtered subset of tests
```

---

## Upstream Documentation

- [pytest Official Documentation](https://docs.pytest.org/)
- [pytest-xdist Repository](https://github.com/pytest-dev/pytest-xdist)
- [pytest-randomly Repository](https://github.com/pytest-dev/pytest-randomly)
- [pytest-sugar Repository](https://github.com/Teemu/pytest-sugar)
- [Syrupy Snapshot Testing Guide](https://tophat.github.io/syrupy/)
- [Hypothesis Property-Based Testing](https://hypothesis.readthedocs.io/)
