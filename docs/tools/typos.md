---
diataxis: reference
purpose: Document automated source code, docstring, and commit message spell-checking with typos.
---

# Typos: Spell Checker

[![Tool: typos](https://img.shields.io/badge/spelling-typos-blue.svg)](https://github.com/crate-ci/typos)

`typos` is an extremely fast source code and documentation spell checker written in Rust
by the crate-ci team.

## What It Does

`typos` is a low-overhead spell checker that evaluates multi-language repositories.
Designed with code-aware tokenization, it respects camelCase, snake_case, and kebab-case
identifiers while referencing a curated technical dictionary to eliminate false
positives.

It scans source files, docstrings, markdown guides, configuration manifests, and commit
messages across the entire tree, applying automated in-place fixes via `typos -w`.

## Why It's in Zenith

Spelling errors in public API identifiers, command-line arguments, or documentation
erode user trust. Zenith integrates `typos` to maintain professional polish across all
repository assets.

Because `typos` scans the entire repository in under 50 milliseconds, it runs on every
pre-commit check and CI workflow without noticeable overhead or the false-positive noise
common in legacy spell checkers.

## Configuration in Zenith

Configured in `typos.toml` at the project root:

```python exec="1" result="toml"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/typos.toml")
if not path.exists():
    path = Path("typos.toml")
print(path.read_text().strip())
```

## Key Invocations

```bash
uv run typos                 # Scan repository for spelling errors
uv run typos -w              # Automatically fix detected typos in place
uv run poe typos             # Wired quality check task in Poe
uv run poe typos-fix         # Wired auto-fixing task in Poe
```

## Upstream Documentation

- [typos GitHub Repository](https://github.com/crate-ci/typos)
