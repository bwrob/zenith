---
diataxis: reference
purpose: Document public API docstring parsing, signature inspection, and breaking change detection with Griffe.
---

# Griffe: Static Analysis & API Guard

[![Tool: Griffe](https://img.shields.io/badge/api-griffe-blue.svg)](https://mkdocstrings.github.io/griffe/)

`Griffe` is a fast static analysis tool for Python created by Timothée Mazzucotelli. It
parses Python source code into rich Abstract Syntax Trees (AST) without executing or
importing modules, extracting signatures, type annotations, docstrings, and public API
representations.

## What It Does

Griffe powers offline API inspection, automated documentation generation, and API
stability enforcement. It parses Python modules, classes, and functions into structured
AST representations without importing code or executing side-effects.

Griffe automatically parses Google, NumPy, and Sphinx docstrings, detects deprecated
APIs decorated with `@warnings.deprecated`, and powers `mkdocstrings[python]` to
generate API documentation. Through `griffe check`, it compares the active
codebase against previous Git revisions or tags to pinpoint breaking public API
alterations.

## Why It Is in Zenith

Importing untrusted or complex packages at documentation build time can trigger
unexpected side effects, uninitialized database connections, or missing C-extension
crashes. Griffe extracts signatures, type hints, and docstrings completely offline and
safely.

To protect library consumers, Zenith wires `griffe check` into continuous
integration and the `poe check-api` task. This prevents pull requests from
introducing breaking API changes in minor or patch releases.

## Configuration in Zenith

Configured in `poe_tasks.toml` through the `check-api` task definition and integrated
into `mkdocstrings[python]` within `zensical.toml`:

```python exec="1" result="toml"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/poe_tasks.toml")
if not path.exists():
    path = Path("poe_tasks.toml")
content = path.read_text()
if "[tasks.check-api]" in content:
    start = content.index("[tasks.check-api]")
    end = content.find("\n\n[", start + 1)
    print(content[start : end if end != -1 else len(content)].strip())
```

## Key Invocations

```bash
# Check for breaking API changes against the previous git tag
uv run poe check-api

# Check public API against a specific git reference
uv run griffe check my_package --search src --against "origin/main"

# Dump parsed API representation to JSON
uv run griffe dump my_package --search src -o api.json
```

## Upstream Documentation

- [Griffe Official Documentation](https://mkdocstrings.github.io/griffe/)
- [Griffe CLI Reference](https://mkdocstrings.github.io/griffe/reference/cli/)
- [Griffe GitHub Repository](https://github.com/mkdocstrings/griffe)
