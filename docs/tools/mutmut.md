---
diataxis: reference
purpose: Document fast local AST mutation testing and survivor mutant elimination with mutmut.
---

# Mutmut: Fast Mutation Testing

[![Tool: mutmut](https://img.shields.io/badge/mutation-mutmut-orange.svg)](https://mutmut.readthedocs.io/)

While 100% statement and branch coverage proves that every line and branch *ran*,
mutation testing verifies that your test assertions *fail* when production logic is
altered. `mutmut` mutates the Python AST in `src/` (flipping `<` to `<=`, changing
constants, negating conditions) and runs `pytest` against each mutant to detect
surviving mutants (weak assertions).

> [!WARNING]
> **Windows Limitation**: `mutmut` relies on POSIX `fork` and process semantics and is
> not supported on Windows. On Windows (or for resumable SQLite-backed runs), use
> **[Cosmic Ray](cosmic-ray.md)** via `uv run poe test-mutation-cosmic`.

## Dual Mutation Strategy: Mutmut Vs. Cosmic Ray

| Capability          | `mutmut`                                  | `cosmic-ray`                               |
| :------------------ | :---------------------------------------- | :----------------------------------------- |
| **Primary Role**    | Fast local TDD mutation loops             | Resumable, cross-platform mutation sweeps  |
| **Execution Model** | In-process AST mutation + `.mutmut-cache` | SQLite session database (`session.sqlite`) |
| **Windows Support** | ❌ macOS & Linux only                     | ✅ Linux, macOS, and Windows               |
| **Poe Task**        | `uv run poe test-mutation`                | `uv run poe test-mutation-cosmic`          |

## Configuration in Zenith

Configured in `pyproject.toml` under `[tool.mutmut]`:

```toml
[tool.mutmut]
    runner       = "pytest"
    source_paths = ["src/"]
```

## Key Invocations

```bash
uv run poe test-mutation       # Run mutmut across src/
uv run mutmut results          # List surviving and suspicious mutants
uv run mutmut show <id>        # Show diff for a surviving mutant
uv run mutmut html             # Generate HTML mutation report in html/
```

## Upstream Documentation

- [mutmut Documentation](https://mutmut.readthedocs.io/)
- [mutmut GitHub Repository](https://github.com/boxed/mutmut)
