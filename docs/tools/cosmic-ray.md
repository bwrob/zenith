---
diataxis: reference
purpose: Document mutation testing and database-backed test suite verification with Cosmic Ray.
---

# Cosmic Ray: Mutation Testing

[![Tool: Cosmic Ray](https://img.shields.io/badge/testing-cosmic--ray-darkred.svg)](https://cosmic-ray.readthedocs.io/)

`Cosmic Ray` is a mutation testing framework for Python. It measures test suite
quality by introducing deliberate faults into the production code Abstract
Syntax Tree.

## What It Does

Mutation testing answers a critical question that traditional code coverage cannot:
**"Do your tests verify correctness, or do they execute code without asserting
behavior?"**

Cosmic Ray parses Python source files into an Abstract Syntax Tree. It introduces
small mutations, such as inverting boolean logic, replacing operators, or deleting
statements. It then executes the test suite against each mutant.

When a test fails, the test suite kills the mutant. This verifies that the
test caught the regression. When all tests pass, the mutant survives. This exposes
a blind spot in test assertion depth.

## Why It Is in Zenith

Achieving 100% line coverage is straightforward even with weak test assertions. AI
coding assistants frequently generate tests that reach full line execution without
validating critical edge-case invariants.

Zenith maintains a dual mutation testing strategy pairing **[mutmut](mutmut.md)** for
fast local developer TDD cycles with Cosmic Ray for exhaustive, cross-platform CI
verification. Because `mutmut` does not support Windows, Cosmic Ray serves as the
universal cross-platform mutation engine, executing reliably across macOS, Linux, and
Windows runners.

Cosmic Ray stores mutation session results in an SQLite database. You can pause,
resume, or distribute assertion audits across worker processes without losing
progress.

## Configuration in Zenith

Configured in `cosmic-ray.toml` at the project root:

```python exec="1" result="toml"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/cosmic-ray.toml")
if not path.exists():
    path = Path("cosmic-ray.toml")
print(path.read_text().strip())
```

## Key Invocations

```bash
# Initialize a new mutation testing session
uv run cosmic-ray init cosmic-ray.toml session.sqlite

# Execute mutation tests against the codebase
uv run cosmic-ray exec session.sqlite

# Generate survival and mutation summary report
uv run cr-report session.sqlite
```

## Upstream Documentation

- [Cosmic Ray Documentation](https://cosmic-ray.readthedocs.io/)
- [Cosmic Ray GitHub Repository](https://github.com/sixty-north/cosmic-ray)
