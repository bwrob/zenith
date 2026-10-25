---
diataxis: reference
purpose: Document TOML schema validation, formatting standards, and linter configuration with Taplo.
---

# Taplo: TOML Toolkit

[![Tool: Taplo](https://img.shields.io/badge/toml-taplo-blue.svg)](https://taplo.tamasfe.dev/)

`Taplo` is a versatile TOML toolkit, formatter, and linter written in Rust. It enforces
strict, clean formatting and schema validation across all TOML configuration files.

## What It Does

`Taplo` parses and formats TOML documents with aligned key-value assignments, consistent
4-space indentation, and alphabetically sorted tables. It verifies TOML syntax and
validates configuration files against JSON Schema definitions in milliseconds.

## Why It Is in Zenith

Modern Python projects rely heavily on TOML across all tool configurations
(`pyproject.toml`, `poe_tasks.toml`, `zensical.toml`, `ruff.toml`, `tach.toml`,
`complexipy.toml`, `typos.toml`).

Zenith integrates Taplo to maintain universal formatting harmony across all repository
manifests. By enabling `align_entries = true`, key-value assignments align vertically
for visual clarity, while automated format inspections prevent unformatted configuration
files from entering source control.

## Configuration in Zenith

Configured in `.taplo.toml` at the project root:

```python exec="1" result="toml"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/.taplo.toml")
if not path.exists():
    path = Path(".taplo.toml")
print(path.read_text().strip())
```

## Key Invocations

```bash
uv run taplo format --check  # Verify TOML formatting across the project
uv run taplo format          # Auto-format all TOML files
uv run poe format-check-toml # Wired task in Poe quality sequence
uv run poe format-toml       # Wired auto-formatting task in Poe
```

## Upstream Documentation

- [Taplo Documentation](https://taplo.tamasfe.dev/)
- [Taplo Configuration Reference](https://taplo.tamasfe.dev/configuration/)
- [TOML Specification](https://toml.io/en/)
