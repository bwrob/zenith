# Zensical: Documentation Generator

[![Tool: Zensical](https://img.shields.io/badge/docs-zensical-teal.svg)](https://github.com/zensical/zensical)

`Zensical` is a fast static documentation site generator written in Rust and Python by the creators of Material for MkDocs and mkdocstrings. It configures documentation via typed `zensical.toml` files, replacing legacy `mkdocs.yml` setups.

---

## What It Does

Zensical generates static technical documentation sites with sub-second live reloading. It automates API documentation via `mkdocstrings[python]`, client-side MathJax LaTeX rendering, dynamic code execution through `markdown-exec`, and native Mermaid diagram support.

It also automatically compiles machine-readable `site/llms.txt` and `site/llms-full.txt` feeds, allowing AI coding assistants to consume project architecture guides and API reference surfaces in a single contextual payload.

---

## Why It's in Zenith

Zenith chooses Zensical because it standardizes on TOML configuration (`zensical.toml`), avoiding YAML sprawl and unifying configuration patterns with `pyproject.toml`.

With strict validation enabled (`zensical build --strict`), deployments fail automatically if an internal link, anchor tag, footnote, or cross-reference is broken. Designed for dual human and AI consumption, Zensical pairs modern responsive theming with automated machine-readable feeds.

---

## Configuration in Zenith

Configured in `zensical.toml` at the project root:

```python exec="1" result="toml"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/zensical.toml")
if not path.exists():
    path = Path("zensical.toml")
print(path.read_text().strip())
```

---

## Key Invocations

```bash
uv run poe docs-serve                  # Start live-reloading dev server (localhost:8000)
uv run zensical serve -a 0.0.0.0:8080  # Bind to custom host address and port
uv run zensical serve -o               # Open browser preview automatically
uv run poe docs-build                  # Strict production build into site/
```

### Live Reloading Watchdog

`zensical serve` includes an integrated file watchdog:
- **Instant Millisecond Rebuilds**: Monitors `docs/`, `zensical.toml`, assets, and stylesheets, updating pages in milliseconds as Markdown files are modified.
- **WebSocket Live Browser Sync**: Automatically pushes changes to all open browser tabs without manual page refreshes.
- **Agent Workflow Note**: When developers run `uv run poe docs-serve` in a terminal window, AI agents do not need to execute rebuilds during editing turns because the watchdog reloads pages automatically.

---

## Upstream Documentation

- [Zensical GitHub Repository](https://github.com/zensical/zensical)
- [mkdocstrings Documentation](https://mkdocstrings.github.io/)
- [Material for MkDocs Guide](https://squidfunk.github.io/mkdocs-material/)
