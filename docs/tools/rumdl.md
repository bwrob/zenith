---
diataxis: reference
purpose: Document GitHub Flavored Markdown linting, formatting rules, and embedded code block validation with rumdl.
---

# Rumdl: Markdown Linter

[![Tool: rumdl](https://img.shields.io/badge/markdown-rumdl-orange.svg)](https://github.com/rvben/rumdl)

`rumdl` is a high-performance Markdown linter and formatter written in Rust. It enforces
strict CommonMark and GitHub Flavored Markdown (GFM) standards, and directly checks
embedded code blocks.

## What It Does

`rumdl` analyzes Markdown files across the codebase to enforce CommonMark and GitHub
Flavored Markdown specifications. It checks heading hierarchies, list indentation,
and table formatting.

Rumdl also integrates with Python linters like Ruff to check embedded Python code
blocks (` ```python `). This guarantees that examples never contain broken syntax,
invalid imports, or outdated conventions.

## Why It Is in Zenith

Legacy Markdown linters require Node.js or Ruby runtimes. Zenith chooses rumdl to
eliminate `npm` dependencies, keeping development environments strictly hermetic with
Rust and Python binaries.

Automated Markdown formatting (`rumdl fmt`) ensures documentation authored by developers
and AI agents adheres to identical formatting standards and maintains clean Git diffs.

## Configuration in Zenith

Configured in `rumdl.toml` at the project root:

```python exec="1" result="toml"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/rumdl.toml")
if not path.exists():
    path = Path("rumdl.toml")
print(path.read_text().strip())
```

## Key Invocations

```bash
uv run rumdl check           # Check all Markdown files
uv run rumdl fmt             # Auto-format Markdown files
uv run poe lint-md           # Wired development task in Poe
uv run poe format-md         # Wired formatting task in Poe
```

## Upstream Documentation

- [rumdl GitHub Repository](https://github.com/rvben/rumdl)
- [CommonMark Specification](https://spec.commonmark.org/)
