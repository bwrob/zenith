---
diataxis: reference
purpose: Document unit test execution, parallel testing, property testing, and test order randomization with pytest.
---

# Pytest: Test Framework

[![Tool: pytest](https://img.shields.io/badge/tests-pytest-blue.svg)](https://docs.pytest.org/)

`pytest` is the foundational testing framework for Python applications and libraries.
Zenith enhances pytest with an integrated ecosystem of specialized plugins that enforce
assertion rigor, prevent state flakiness, and accelerate parallel execution.

## What It Does

`pytest` provides a fixture-driven testing engine with assertion introspection. You
author tests as idiomatic Python functions. Tests leverage dependency injection via
fixtures, parameterized matrices, and filtering mechanisms.

Zenith configures pytest with strict validation flags. Tests must declare valid
markers. Pytest validates configuration files strictly, executes docstring tests
automatically, and warns on unused snapshots.

## Why It Is in Zenith

Testing in Zenith eliminates false confidence. Beyond standard unit assertions, pytest
operates under a strict zero-warning policy (`filterwarnings = "error"`). Deprecation
notices, unclosed resources, or encoding anomalies fail the test suite immediately.

By pairing pytest with specialized plugins, Zenith verifies behavior across multiple
dimensions. Parallel test execution accelerates developer loops. Randomized ordering
eliminates state pollution. Snapshot and property-based plugins catch edge-case
regressions that manual test cases miss.

## Integrated Pytest Plugins

Zenith integrates a curated set of plugins into the test environment:

| Plugin                | Role                   | Primary Guarantee                                                                                                                                         |
| --------------------- | ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`pytest-cov`**      | Coverage Integration   | Bridges pytest with **[Coverage.py](coverage.md)** to track execution and enforce 100% statement and branch coverage.                                     |
| **`pytest-xdist`**    | Parallel Execution     | Distributes test runs across available CPU cores (`uv run poe test-fast` via `-n auto`), accelerating local and CI feedback loops.                        |
| **`pytest-randomly`** | Test Order Shuffling   | Randomizes execution sequences on every run to detect global state leakage, unclosed resources, or order-dependent assertions.                            |
| **`pytest-sugar`**    | Terminal Diagnostics   | Replaces default dot progress with an interactive progress meter and surfaces test failures immediately as they occur.                                    |
| **`syrupy`**          | Snapshot Testing       | Provides declarative snapshot fixtures (`snapshot`) that assert structured outputs (CLI menus, JSON payloads, AST trees) against versioned `.ambr` files. |
| **`hypothesis`**      | Property-Based Testing | Generates hundreds of pseudo-random inputs to find hidden edge cases, boundary errors, and numeric overflow traps across algorithmic functions.           |

## Configuration in Zenith

Configured in `pytest.ini` at the project root:

```python exec="1" result="ini"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/pytest.ini")
if not path.exists():
    path = Path("pytest.ini")
print(path.read_text().strip())
```

## Key Invocations

```bash
uv run poe test                 # Run complete test suite with 100% coverage
uv run poe test-fast            # Run tests in parallel with pytest-xdist
uv run poe test-lowest          # Verify against lowest-direct dependencies
uv run poe test-snapshot-update # Update Syrupy snapshots (.ambr files)
uv run pytest -k "test_filter"  # Run filtered subset of tests
```

## Upstream Documentation

- [pytest Official Documentation](https://docs.pytest.org/)
- [pytest-xdist Repository](https://github.com/pytest-dev/pytest-xdist)
- [pytest-randomly Repository](https://github.com/pytest-dev/pytest-randomly)
- [pytest-sugar Repository](https://github.com/Teemu/pytest-sugar)
- [Syrupy Snapshot Testing Guide](https://tophat.github.io/syrupy/)
- [Hypothesis Property-Based Testing](https://hypothesis.readthedocs.io/)
