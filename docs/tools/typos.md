---
diataxis: reference
purpose: Document automated source code, docstring, and commit message spell-checking with typos.
---

# Typos: Spell Checker

[![Tool: typos](https://img.shields.io/badge/spelling-typos-blue.svg)](https://github.com/crate-ci/typos)

`typos` is a Rust-based source code and documentation spell checker that splits
`snake_case`, `camelCase`, and `kebab-case` identifiers to catch common misspellings
with low false-positive noise. It runs automatically on `git commit` via `prek`, inside
`uv run poe fix`, and in `uv run poe code-quality`.

## Configuration in Zenith

Configured in `typos.toml` at the project root:

```python exec="1" result="toml"
import re
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/typos.toml")
if not path.exists():
    path = Path("typos.toml")
text = path.read_text(encoding="utf-8")
text = re.sub(r"^# =+[^\n]*\n(?:#[^\n]*\n)*# =+[^\n]*\n+", "", text)
print(text.strip())
```

To allow project-specific domain acronyms or proper nouns, add entries under
`[default.extend-words]` in `typos.toml`, or append `# spellchecker:disable-line` to a
specific line.

## Key Invocations

```bash
uv run poe typos             # Scan repository for spelling mistakes
uv run poe typos-fix         # Auto-fix detected spelling mistakes in place (typos -w)
```

## Upstream Documentation

- [typos GitHub Repository](https://github.com/crate-ci/typos)
