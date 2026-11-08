---
diataxis: reference
purpose: Document vector layout markup, SVG logo authoring, and mathematical diagram compilation with Typst.
---

# Typst: Vector Layout Engine

[![Tool: Typst](https://img.shields.io/badge/typesetting-typst-239dad.svg)](https://typst.app)

`Typst` is a Rust-based typesetting and vector layout engine. Generated Zenith projects
store documentation hero banners and logos as plain-text `.typ` source files under
`docs/assets/` (`python-banner-dark.typ`, `python-banner-light.typ`, and
`python-logo.typ`), compiling them into theme-aware `.svg` files via
`uv run poe docs-logo`.

## Configuration in Zenith

Wired in `poe_tasks.toml` through the `docs-logo` task (using `typst` and
`fontpkg-cinzel` from the `docs` dependency group):

```python exec="1" result="toml"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/poe_tasks.toml")
if not path.exists():
    path = Path("poe_tasks.toml")
content = path.read_text(encoding="utf-8")
if "[tasks.docs-logo]" in content:
    start = content.index("[tasks.docs-logo]")
    end = content.find("\n\n[", start + 1)
    print(content[start : end if end != -1 else len(content)].strip())
```

## Key Invocations

```bash
uv run poe docs-logo                         # Compile dark/light SVG banners from docs/assets/*.typ
uv run typst compile docs/assets/python-logo.typ docs/assets/python-logo.svg
```

## Upstream Documentation

- [Typst Official Documentation](https://typst.app/docs/)
- [Typst GitHub Repository](https://github.com/typst/typst)
