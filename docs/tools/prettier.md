---
diataxis: reference
purpose: Document YAML manifest and stylesheet formatting rules and execution with Prettier.
---

# Prettier: YAML & CSS Formatter

[![Tool: Prettier](https://img.shields.io/badge/formatter-prettier-f7b93e.svg)](https://prettier.io/)

`Prettier` is an opinionated code formatter. Zenith utilizes Prettier exclusively
through `prek` to format GitHub Actions YAML manifests, issue templates, and
custom CSS stylesheets.

## What It Does

Prettier parses configuration files and stylesheets, re-printing them to adhere to
strict stylistic standards. In Zenith, it standardizes 4-space indentation, list
formatting, key-value spacing, and scalar wrapping across GitHub Actions workflows
(`.github/workflows/*.yaml`) and custom CSS sheets (`docs/stylesheets/*.css`).

By formatting files automatically, Prettier completely eliminates stylistic noise from
pull request reviews and version control diffs.

## Why It's in Zenith

Zenith enforces consistent 4-space indentation across all languages in the project
(Python, TOML, YAML, and CSS). Prettier is wired exclusively through prek mirrors,
executing formatting without requiring a global Node.js installation or package
manifests in the Python repository.

It integrates directly into dedicated task runners (`poe format-yaml`, `poe format-css`)
and the overarching `poe code-quality` verification pipeline.

## Configuration in Zenith

Configured in `.prettierrc.yaml` at the project root:

```python exec="1" result="yaml"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/.prettierrc.yaml")
if not path.exists():
    path = Path(".prettierrc.yaml")
print(path.read_text().strip())
```

And registered in `prek.toml`:

```toml
[[repos]]
repo = "https://github.com/pre-commit/mirrors-prettier"
rev = "v4.0.0-alpha.8"
hooks = [
    { id = "prettier", name = "🎨 prettier · Format YAML files", types = ["yaml"] },
    { id = "prettier", name = "🎨 prettier · Format CSS files", types = ["css"] },
]
```

## Key Invocations

```bash
uv run poe format-yaml       # Format YAML configuration files
uv run poe format-css        # Format CSS stylesheets
uv run poe fix               # Auto-fix all files including YAML and CSS
```

## Upstream Documentation

- [Prettier Official Documentation](https://prettier.io/)
- [Prettier Configuration Options](https://prettier.io/docs/en/options.html)
