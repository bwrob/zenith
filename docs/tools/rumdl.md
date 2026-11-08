---
diataxis: reference
purpose: Document GitHub Flavored Markdown linting, formatting rules, and embedded code block validation with rumdl.
---

# Rumdl: Markdown Linter

[![Tool: rumdl](https://img.shields.io/badge/markdown-rumdl-orange.svg)](https://github.com/rvben/rumdl)

`rumdl` is a Rust-based Markdown linter and formatter that enforces GitHub Flavored
Markdown (GFM) structure, an 88-character prose/code line limit, and embedded Python
code block linting/formatting via **[Ruff](ruff.md)** (`[code-block-tools]`).

## Configuration in Zenith

Configured in `rumdl.toml` at the project root:

```python exec="1" result="toml"
import re
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/rumdl.toml")
if not path.exists():
    path = Path("rumdl.toml")
text = path.read_text(encoding="utf-8")
text = re.sub(r"^# =+[^\n]*\n(?:#[^\n]*\n)*# =+[^\n]*\n+", "", text)
print(text.strip())
```

## Key Invocations

```bash
uv run poe lint-md           # Lint Markdown files and Python code blocks
uv run poe format-md         # Auto-format Markdown tables, prose, and snippets
```

## Upstream Documentation

- [rumdl GitHub Repository](https://github.com/rvben/rumdl)
- [CommonMark Specification](https://spec.commonmark.org/)
