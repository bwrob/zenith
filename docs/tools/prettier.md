---
diataxis: reference
purpose: Document YAML manifest and stylesheet formatting rules and execution with Prettier.
---

# Prettier: YAML & CSS Formatter

[![Tool: Prettier](https://img.shields.io/badge/formatter-prettier-f7b93e.svg)](https://prettier.io/)

Zenith runs `Prettier` through **[prek](prek.md)** to format GitHub Actions workflows
(`.github/workflows/*.yaml`), YAML configuration files, and documentation stylesheets
(`docs/stylesheets/*.css`) with 4-space indentation (`tabWidth: 4`) without requiring a
project-level `package.json`.

## Configuration in Zenith

Configured in `.prettierrc.yaml` at the project root:

```python exec="1" result="yaml"
import re
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/.prettierrc.yaml")
if not path.exists():
    path = Path(".prettierrc.yaml")
text = path.read_text(encoding="utf-8")
text = re.sub(r"^# =+[^\n]*\n(?:#[^\n]*\n)*# =+[^\n]*\n+", "", text)
print(text.strip())
```

And wired in `prek.toml`:

```toml
[[repos]]
    hooks = [
        { id = "prettier", name = "🎨 prettier · Format YAML files", types = [
            "yaml",
        ], priority = "independent_formatters" },
        { id = "prettier", alias = "prettier-css", types = [
            "css",
        ], priority = "independent_formatters" },
    ]
    repo = "https://github.com/pre-commit/mirrors-prettier"
    rev = "v3.1.0"
```

## Key Invocations

```bash
uv run poe format-yaml       # Format all YAML files (prek run prettier --all-files)
uv run poe format-css        # Format all CSS stylesheets (prek run prettier-css --all-files)
uv run poe fix               # Run all project formatters including YAML and CSS
```

## Upstream Documentation

- [Prettier Official Documentation](https://prettier.io/)
- [Prettier Configuration Options](https://prettier.io/docs/en/options.html)
