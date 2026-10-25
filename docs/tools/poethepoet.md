---
diataxis: reference
purpose: Document hermetic task definitions, command orchestration, and developer shortcuts with Poe the Poet.
---

# Poe the Poet: Task Automation

[![Tool: poethepoet](https://img.shields.io/badge/tasks-poethepoet-blue.svg)](https://poethepoet.natn.io/)

`Poe the Poet` (`poe`) is a declarative, cross-platform task runner designed for Python
and virtual environment managers like `uv`.

## What It Does

Poe the Poet codifies operations into declarative command sequences. Developers
define tasks in TOML files. Tasks run reliably across Linux, macOS, and Windows
without fragile shell scripts. Poe forwards flags and positional arguments
transparently to underlying tools.

## Why It Is in Zenith

Zenith chooses Poe the Poet to guarantee zero behavioral drift between developer
workstations and CI runners. Instead of maintaining separate script files or relying on
ad-hoc shell invocations, developers and automated workflows execute identical named
tasks like `uv run poe test` or `uv run poe code-quality`.

Poe automatically executes all commands within the hermetic `uv` environment, injecting
strict runtime hygiene settings such as UTF-8 encoding enforcement and standard library
warning traps. By composing individual linters, formatters, type checkers, and test
runners into unified compound tasks, Poe provides a single, unambiguous interface for
repository maintenance.

## Configuration in Zenith

Configured in `poe_tasks.toml` (or `[tool.poe.tasks]` in `pyproject.toml`):

```python exec="1" result="toml"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/poe_tasks.toml")
if not path.exists():
    path = Path("poe_tasks.toml")
print(path.read_text().strip())
```

## Key Invocations

```bash
uv run poe test             # Run test suite
uv run poe code-quality      # Run complete quality validation sequence
uv run poe fix               # Auto-fix all format, lint, and typo issues
uv run poe docs-serve        # Serve documentation locally
uv run poe test -- -k "math" # Forward filter argument to pytest
```

## Upstream Documentation

- [Poe the Poet Documentation](https://poethepoet.natn.io/)
- [Poe the Poet GitHub Repository](https://github.com/nat-n/poethepoet)
