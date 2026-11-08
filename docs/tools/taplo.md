---
diataxis: reference
purpose: Document TOML schema validation, formatting standards, and linter configuration with Taplo.
---

# Taplo: TOML Toolkit

[![Tool: Taplo](https://img.shields.io/badge/toml-taplo-blue.svg)](https://taplo.tamasfe.dev/)

`Taplo` is a Rust-based TOML formatter and schema validator. Zenith configures Taplo in
`.taplo.toml` to enforce 4-space indentation, vertically aligned key-value entries
(`align_entries = true`), and alphabetically reordered keys (`reorder_keys = true`)
across all root `.toml` configuration files.

## Configuration in Zenith

Configured in `.taplo.toml` at the project root:

```python exec="1" result="toml"
import re
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/.taplo.toml")
if not path.exists():
    path = Path(".taplo.toml")
text = path.read_text(encoding="utf-8")
text = re.sub(r"^# =+[^\n]*\n(?:#[^\n]*\n)*# =+[^\n]*\n+", "", text)
print(text.strip())
```

## Key Invocations

```bash
uv run poe format-toml        # Auto-format all TOML files (taplo format)
uv run poe format-check-toml  # Check TOML formatting (taplo format --check)
```

## Upstream Documentation

- [Taplo Documentation](https://taplo.tamasfe.dev/)
- [Taplo Configuration Reference](https://taplo.tamasfe.dev/configuration/)
- [TOML Specification](https://toml.io/en/)
