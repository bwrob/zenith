---
diataxis: reference
purpose: Document public API docstring parsing, signature inspection, and breaking change detection with Griffe.
---

# Griffe: Static Analysis & API Guard

[![Tool: Griffe](https://img.shields.io/badge/api-griffe-blue.svg)](https://mkdocstrings.github.io/griffe/)

`Griffe` parses Python modules into an Abstract Syntax Tree (AST) without importing or
executing code. In Zenith, Griffe serves two roles:

1. **Automated API reference generation**: Powers `mkdocstrings[python]` in
   **[Zensical](zensical.md)** (along with the `griffe-warnings-deprecated` extension)
   to render Google-style docstrings, PEP 695 type parameters, and `@deprecated`
   notices.
2. **Breaking API change detection**: `uv run poe check-api` (`griffe check`) compares
   current public signatures against the previous Git tag (or a target ref in SDD
   reviews via `uv run poe sdd-check-api <feature-id>`) and flags removed exports,
   reordered positional arguments, or narrowed parameter types.

## Configuration in Zenith

Configured in `poe_tasks.toml`:

```toml
[tasks.check-api]
    cmd  = "griffe check my_project --search src"
    help = "Detect breaking public API changes against the previous git tag with Griffe."
```

## Key Invocations

```bash
# Check for breaking API changes against the latest Git tag
uv run poe check-api

# Compare public API against a specific branch or ref
uv run griffe check my_project --search src --against "origin/main"

# Dump parsed public API metadata to JSON
uv run griffe dump my_project --search src -o api.json
```

## Upstream Documentation

- [Griffe Official Documentation](https://mkdocstrings.github.io/griffe/)
- [Griffe CLI Reference](https://mkdocstrings.github.io/griffe/reference/cli/)
- [Griffe GitHub Repository](https://github.com/mkdocstrings/griffe)
