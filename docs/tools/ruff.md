---
diataxis: reference
purpose: Document strict Python linting, rule presets, inline diagnostic overrides, and formatting with Astral Ruff.
---

# Ruff: Linter & Formatter

[![Tool: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

`Ruff` is Astral's Rust-based Python linter and code formatter, replacing Flake8, Black,
isort, pydocstyle, pyupgrade, and dozens of lint plugins in a single binary. Zenith
enables the full rule catalog (`select = ["ALL"]`) with `preview = true` and docstring
code formatting (`docstring-code-format = true`).

## Configuration in Zenith

Configured in `ruff.toml` at the project root:

```python exec="1" result="toml"
import re
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/ruff.toml")
if not path.exists():
    path = Path("ruff.toml")
text = path.read_text(encoding="utf-8")
text = re.sub(r"^# =+[^\n]*\n(?:#[^\n]*\n)*# =+[^\n]*\n+", "", text)
print(text.strip())
```

## Key Policy Rules

- **No `# noqa` comments (`# ruff: ignore[rule-name]` only)**: Bare `# noqa` directives
  and letter-digit rule codes (`E501`, `S603`, `PLR0913`) are banned across the
  codebase. When a suppression is genuinely required, use Ruff's native directive with
  the **full lowercase rule name** and an explanatory comment:

  ```python
  # side-effect import registers plugin handlers at startup
  import my_project.plugins  # ruff: ignore[unused-import]
  ```

  For module-level rules (such as `complex-structure`), place `# ruff: ignore[...]` on
  line 1 of the file.
- **Full rule names in `ruff.toml`**: Every entry in `ignore` and `per-file-ignores`
  uses the descriptive rule name (`"missing-trailing-comma"`, `"assert"`,
  `"suspicious-subprocess-import"`) rather than opaque letter-digit codes.
- **Mandatory `from __future__ import annotations`**: Enforced via
  `isort.required-imports` and `future-annotations = true`, allowing
  `flake8-type-checking` to move type-only imports into `if TYPE_CHECKING:` blocks
  safely while keeping runtime annotations on Pydantic/dataclasses/Typer intact.
- **Absolute imports only**: `ban-relative-imports = "all"` prohibits
  `from .foo import bar`.

## Key Invocations

```bash
uv run poe lint          # Run ruff check --config ruff.toml
uv run poe format        # Format Python files and docstring snippets
uv run poe format-check  # Verify formatting without modifying files
uv run poe fix           # Auto-fix lint issues and format all files
```

## Upstream Documentation

- [Ruff Official Documentation](https://docs.astral.sh/ruff/)
- [Ruff Rules Reference](https://docs.astral.sh/ruff/rules/)
- [Ruff GitHub Repository](https://github.com/astral-sh/ruff)
