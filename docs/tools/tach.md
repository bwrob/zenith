---
diataxis: reference
purpose: Document module boundary enforcement, layer hierarchies, and circular dependency prevention with Tach.
---

# Tach: Architecture Boundaries

[![Tool: Tach](https://img.shields.io/badge/architecture-tach-purple.svg)](https://github.com/gauge-sh/tach)

`Tach` is an architectural boundary tool for Python written in Rust. It enforces
strict layering and prevents circular dependencies. Deptry checks third-party
dependency declarations.

## What It Does

Tach evaluates the import graph of a Python repository to enforce modular boundaries and
eliminate circular dependencies. It defines explicit, unidirectional boundaries between
layers—preventing low-level models and core logic from coupling to high-level CLI or API
orchestrators.

Tach can generate visual Mermaid diagrams directly from the verified import graph.
The `dependencies` Poe task runs `tach check` for internal boundaries and `deptry src`
for declared dependencies.

## Why It Is in Zenith

Over time, codebases naturally suffer from architectural erosion as developers and AI
assistants import utilities opportunistically across modules, eventually creating an
untestable monolith. Zenith integrates Tach to enforce clear layer boundaries and catch
circular references at commit time. Deptry checks that package imports match declared
dependencies.

## Configuration in Zenith

Configured in `tach.toml` at the project root:

```python exec="1" result="toml"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/tach.toml")
if not path.exists():
    path = Path("tach.toml")
print(path.read_text().strip())
```

### Boundary Rules

Lower-level domains such as `core` and `models` must never import higher-level
orchestration layers like `cli`. All cross-module interactions must pass through
explicit, public interfaces.

## Key Invocations

```bash
# Verify module architecture boundaries.
uv run tach check

# Verify declared dependencies.
uv run deptry src

# Run the configured architecture task.
uv run poe dependencies

# Export a Mermaid architecture diagram.
uv run tach show --mermaid -o docs/assets/architecture.mmd
```

## Upstream Documentation

- [Tach Official Documentation](https://docs.tach.sh/)
- [Tach GitHub Repository](https://github.com/gauge-sh/tach)
- [Deptry Usage](https://github.com/osprey-oss/deptry/blob/main/docs/usage.md)
