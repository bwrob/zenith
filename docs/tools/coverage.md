---
diataxis: reference
purpose: Document 100% statement and branch coverage enforcement and report analysis with Coverage.py.
---

# Coverage.py: Code Coverage

[![Tool: Coverage.py](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://coverage.readthedocs.io/)

`Coverage.py` measures code coverage for Python. It monitors program execution
during automated test runs, tracks executed statements, and evaluates conditional
branch decisions.

## What It Does

`Coverage.py` measures statement execution and branch coverage across Python packages.
Branch analysis determines whether tests evaluated every conditional path for both
true and false outcomes. This includes `if`, `elif`, `else`, `while`, and exception
clauses.

During test runs, `Coverage.py` compiles execution statistics into a `.coverage`
database. It produces terminal reports that pinpoint missing lines
(`coverage report -m`). It also generates XML manifests for CI reporting and
interactive HTML dashboards.

## Why It Is in Zenith

Zenith establishes a non-negotiable engineering standard:
**100% mandatory statement and branch test coverage** (`fail_under = 100` and
`branch = true`). In Zenith, you must test all code before you commit it. When a test
run misses a statement or branch, CI pipelines fail immediately.

In AI-native workflows, 100% coverage provides a critical structural invariant.
Autonomous coding agents frequently introduce partial implementations, dead branches, or
untested error-handling paths. Mandating full coverage prevents untested code from
reaching `main`, while liberating developers to execute major architectural refactors
without fear of regression.

## Configuration in Zenith

Configured in `.coveragerc` at the project root:

```python exec="1" result="ini"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/.coveragerc")
if not path.exists():
    path = Path(".coveragerc")
print(path.read_text().strip())
```

## Key Invocations

```bash
# Run test suite with mandatory 100% coverage enforcement
uv run poe test

# Display terminal coverage report with missing lines
uv run coverage report -m

# Generate interactive HTML dashboard into htmlcov/
uv run poe coverage
```

## Upstream Documentation

For advanced coverage analysis, exclusion patterns, and reporting configurations,
consult the [Coverage.py documentation](https://coverage.readthedocs.io/) and the
[Coverage.py GitHub repository](https://github.com/nedbat/coveragepy).
