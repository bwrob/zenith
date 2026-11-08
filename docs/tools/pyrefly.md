---
diataxis: reference
purpose: Document strict static type checking, generic type parameters, and type configuration with Pyrefly.
---

# Pyrefly: Static Type Checking

[![Tool: Pyrefly](https://img.shields.io/badge/types-pyrefly%20strict-blueviolet.svg)](https://github.com/facebook/pyrefly)

`Pyrefly` is Meta's Rust-based static type checker for Python. Zenith configures Pyrefly
with `preset = "strict"`, `infer-with-first-use = false`, and
`enabled-ignores = ["pyrefly"]`, and enforces **100% strict type coverage** across
`src/` via `pyrefly coverage check`.

## Configuration in Zenith

Configured in `pyrefly.toml` at the project root:

```python exec="1" result="toml"
import re
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/pyrefly.toml")
if not path.exists():
    path = Path("pyrefly.toml")
text = path.read_text(encoding="utf-8")
text = re.sub(r"^# =+[^\n]*\n(?:#[^\n]*\n)*# =+[^\n]*\n+", "", text)
text = text.replace("{{ cookiecutter.python_version }}", "3.12")
print(text.strip())
```

## Strict Mode & Type Completeness Rules

- **100% strict type coverage (`poe type-coverage`)**:
  `pyrefly coverage check src --fail-under 100 --strict` verifies that every function
  parameter, return type, class attribute, and module-level variable in `src/` has an
  explicit annotation. Under `--strict`, annotations that resolve to `Any` count as
  untyped and fail the gate.
- **Scoped `# pyrefly: ignore[code]` only**: Because `enabled-ignores = ["pyrefly"]`,
  generic `# type: ignore` comments are ignored. Suppressions must name the specific
  Pyrefly error code (`# pyrefly: ignore[bad-assignment]`) with a rationale comment.
- **Editor integration**: Pyrefly runs via LSP or alongside Pylance/Pyright in VS Code,
  Cursor, Zed, and Neovim, and executes on `pre-push` via `prek` and in
  `uv run poe code-quality`.

## Key Invocations

```bash
uv run poe type-check                              # Run pyrefly check
uv run poe type-coverage                           # Enforce 100% strict coverage
uv run poe type-coverage-report                    # Output JSON coverage report
uv run pyrefly coverage check src --public-only    # Verify PEP 561 public API types
```

## Upstream Documentation

- [Pyrefly GitHub Repository](https://github.com/facebook/pyrefly)
- [Pyrefly Type Coverage Documentation](https://pyrefly.org/en/docs/report/)
- [Python Typing Documentation](https://docs.python.org/3/library/typing.html)
