---
diataxis: reference
purpose: Document module boundary enforcement, layer hierarchies, and circular dependency prevention with Tach.
---

# Tach: Architecture Boundaries

[![Tool: Tach](https://img.shields.io/badge/architecture-tach-purple.svg)](https://github.com/gauge-sh/tach)

`Tach` is a Rust-based Python import graph analyzer that enforces unidirectional layer
boundaries (`cli -> core`) and blocks circular dependencies. In Zenith,
`uv run poe dependencies` pairs `tach check` (internal module boundaries) with
**[Deptry](deptry.md)** (`deptry src`, third-party dependency declarations).

## Configuration in Zenith

Configured in `tach.toml` at the project root:

```toml
exclude = [
    "**/*__pycache__",
    "**/*egg-info",
    "**/docs",
    "**/tests",
    "**/venv",
    "**/.venv",
    "**/site",
]
interfaces   = []
source_roots = ["src"]

exact                        = true
forbid_circular_dependencies = true
ignore_type_checking_imports = true
layers                       = ["cli", "core"]
respect_gitignore            = true

[rules]
    require_ignore_directive_reasons = "error"
    unused_ignore_directives         = "error"

[[modules]]
    depends_on = []
    layer      = "core"
    path       = "my_project"

[[modules]]
    depends_on = ["my_project.cli"]
    layer      = "cli"
    path       = "my_project.__main__"

[[modules]]
    depends_on = []
    layer      = "cli"
    path       = "my_project.cli"
```

## Key Policy Rules

- **Unidirectional layer hierarchy (`layers = ["cli", "core"]`)**: Higher layers (`cli`)
  may import lower layers (`core`), but `core` modules must never import `cli`.
- **Exact dependency declarations (`exact = true`)**: Every direct module dependency
  must be listed in `depends_on`; unused entries in `depends_on` also fail `tach check`.
- **Zero circular imports (`forbid_circular_dependencies = true`)**: Runtime import
  cycles fail `tach check`. Type-only imports inside `if TYPE_CHECKING:` blocks are
  exempt (`ignore_type_checking_imports = true`).
- **Mandatory ignore reasons**: Any `# tach-ignore` directive must include an explicit
  reason (`require_ignore_directive_reasons = "error"`), and stale directives fail the
  check (`unused_ignore_directives = "error"`).

## Key Invocations

```bash
uv run tach check                              # Verify internal module boundaries
uv run poe dependencies                        # Run tach check + deptry src
uv run poe dependency-graph                    # Export Mermaid dependency graph to docs/dependency_graph.mmd
```

## Upstream Documentation

- [Tach Official Documentation](https://docs.tach.sh/)
- [Tach GitHub Repository](https://github.com/gauge-sh/tach)
