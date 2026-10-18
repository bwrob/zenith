# Coverage.py: Code Coverage

[![Tool: Coverage.py](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://coverage.readthedocs.io/)

`Coverage.py` is the industry-standard code coverage measurement engine for Python. It
monitors program execution during automated test runs, measuring which statements were
executed and evaluating conditional branch decisions.

---

## What It Does

`Coverage.py` measures both statement execution and branch coverage across Python
packages. Rather than merely recording which lines were executed, branch analysis
determines whether every conditional path (`if`, `elif`, `else`, `while`, and exception
clauses) was evaluated for both true and false outcomes.

During test runs, `Coverage.py` compiles precise execution statistics into a binary
`.coverage` database. It produces detailed terminal reports pinpointing missing line
numbers (`coverage report -m`), machine-readable XML manifests (`coverage.xml`) for
continuous integration reporting, and interactive HTML dashboards highlighting exact
covered and missed branches in source files.

---

## Why It's in Zenith

Zenith establishes a non-negotiable engineering standard:
**100% mandatory statement and branch test coverage** (`fail_under = 100` and
`branch = true`). In Zenith, untested code is considered uncommitted code. If a single
statement or conditional branch is missed, continuous integration pipelines fail
immediately.

In AI-native workflows, 100% coverage provides a critical structural invariant.
Autonomous coding agents frequently introduce partial implementations, dead branches, or
untested error-handling paths. Mandating full coverage prevents untested code from
reaching `main`, while liberating developers to execute major architectural refactors
without fear of regression.

---

## Configuration in Zenith

Configured in `.coveragerc` at the project root:

```python exec="1" result="ini"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/.coveragerc")
if not path.exists():
    path = Path(".coveragerc")
print(path.read_text().strip())
```

---

## Key Invocations

```bash
# Run test suite with mandatory 100% coverage enforcement
uv run poe test

# Display terminal coverage report with missing lines
uv run coverage report -m

# Generate interactive HTML dashboard into htmlcov/
uv run poe coverage
```

---

## Upstream Documentation

For advanced coverage analysis, exclusion patterns, and reporting configurations,
consult the [Coverage.py documentation](https://coverage.readthedocs.io/) and the
[Coverage.py GitHub repository](https://github.com/nedbat/coveragepy).
