# Tach: Architecture Boundaries

[![Tool: Tach](https://img.shields.io/badge/architecture-tach-purple.svg)](https://github.com/gauge-sh/tach)

`Tach` is an architectural boundary and modular dependency management tool for Python written in Rust. It enforces strict layering, prevents circular dependencies, and validates third-party dependency declarations.

---

## What It Does

Tach evaluates the import graph of a Python repository to enforce modular boundaries and eliminate circular dependencies. It defines explicit, unidirectional boundaries between layers—preventing low-level models and core logic from coupling to high-level CLI or API orchestrators.

Tach also includes `tach check-external`, which audits all source imports against declared dependencies in `pyproject.toml` to prevent undeclared transitive dependencies from leaking into code. It can also generate visual Mermaid diagrams directly from the verified import graph.

---

## Why It's in Zenith

Over time, codebases naturally suffer from architectural erosion as developers and AI assistants import utilities opportunistically across modules, eventually creating an untestable monolith. Zenith integrates Tach to enforce clear layer boundaries and catch circular references at commit time.

Enforcing `check_external = true` prevents ghost dependencies that happen to exist in the developer environment from slipping into releases, guaranteeing clean installations for downstream consumers.

---

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

Lower-level domains such as `core` and `models` must never import higher-level orchestration layers like `cli`. All cross-module interactions must pass through explicit, public interfaces, and `check_external = true` blocks imports of any third-party library not explicitly declared in `pyproject.toml`.

---

## Key Invocations

```bash
uv run tach check                                              # Verify module architecture boundaries
uv run tach check-external                                     # Verify external dependencies
uv run poe dependencies                                        # Wired development task in Poe
uv run tach show --mermaid -o docs/assets/architecture.mmd    # Export visual Mermaid diagram
```

---

## Upstream Documentation

- [Tach Official Documentation](https://docs.tach.sh/)
- [Tach GitHub Repository](https://github.com/gauge-sh/tach)
