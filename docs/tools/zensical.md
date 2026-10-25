---
diataxis: reference
purpose: Document static documentation compilation, live development serving, and plugin configuration with Zensical.
---

# Zensical: Documentation Generator

[![Tool: Zensical](https://img.shields.io/badge/docs-zensical-teal.svg)](https://github.com/zensical/zensical)

`Zensical` is a fast static documentation site generator written in Rust and Python by
the creators of Material for MkDocs and mkdocstrings. It configures documentation via
typed `zensical.toml` files, replacing legacy `mkdocs.yml` setups.

## What It Does

Zensical generates static technical documentation sites with sub-second live reloading.
It automates API documentation via `mkdocstrings[python]`, client-side MathJax LaTeX
rendering, dynamic code execution through `markdown-exec`, and native Mermaid diagram
support.

It also compiles machine-readable `site/llms.txt` and `site/llms-full.txt` feeds,
allowing AI coding assistants to consume the library's entire API reference surface and
guides in a single, high-signal contextual payload.

## Why It's in Zenith

Zenith chooses Zensical because it standardizes on TOML configuration (`zensical.toml`),
avoiding YAML sprawl and unifying configuration patterns with `pyproject.toml`.

With strict validation enabled (`zensical build --strict`), deployments fail
automatically if an internal link, anchor tag, footnote, or cross-reference is broken.
Designed for dual human and AI consumption, Zensical pairs modern responsive theming
with automated machine-readable feeds.

## Integrated Plugins

Zenith enhances Zensical with specialized plugins configured under `[project.plugins]`:

| Plugin                     | Capability                  | Purpose in Zenith                                                                                                                                                                                                           |
| -------------------------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`gh-admonitions`**       | GitHub Alert Callouts       | Renders GitHub-flavored alert callouts (`> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]`) with styled border accents and icons.                                                                    |
| **`llmstxt`**              | AI Context Manifests        | Compiles structured `site/llms.txt` and `site/llms-full.txt` feeds, allowing AI coding assistants to consume repository guides and API signatures in a single contextual payload.                                           |
| **`markdown-exec`**        | Dynamic Code Execution      | Executes inline Python, Shell, Tree, and Markdown snippets (`python exec="1"`, `sh exec="1"`) during build, ensuring rendered tool configurations and directory trees reflect live repository files without manual copying. |
| **`mkdocstrings[python]`** | Automated API Documentation | Extracts and documents public Python functions, classes, type parameters, and protocols directly from source code docstrings via Griffe with NumPy style parsing.                                                           |

## Markdown Extensions Suite

Zenith enables a suite of Python-Markdown and PyMdown Extensions under
`[project.markdown_extensions]` to support rich technical authoring:

| Extension Category         | Extensions                                                            | Enabled Features                                                                                                                                                               |
| -------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Callouts & Blocks**      | `admonition`, `pymdownx.details`                                      | Collapsible `<details>` blocks (`??? note "Title"`), inline notes, and standard warning callouts.                                                                              |
| **Code & Diagrams**        | `pymdownx.superfences`, `pymdownx.highlight`, `pymdownx.inlinehilite` | Custom fences for interactive **[Mermaid](https://mermaid.js.org/)** diagrams, line numbers (`anchor_linenums`), syntax highlighting, and inline code formatting (`#!python`). |
| **Math & Symbols**         | `pymdownx.arithmatex`, `pymdownx.emoji`, `pymdownx.smartsymbols`      | Client-side **[MathJax](https://www.mathjax.org/)** LaTeX formula rendering (`\( ... \)` and `$$ ... $$`), Twemoji SVG emojis (`:octicons-code-24:`), and typographic arrows.  |
| **Interactive UI**         | `pymdownx.tabbed`, `pymdownx.tasklist`, `zensical.extensions.preview` | Multi-language tabbed code switchers (`=== "Python"`), interactive task checkboxes (`- [x]`), and instant link hover previews.                                                 |
| **Typography & Structure** | `attr_list`, `def_list`, `footnotes`, `abbr`, `toc`                   | HTML attribute attaching (`{: .grid .cards }`), definition lists, footnotes (`[^1]`), glossary tooltips, and permalink anchors.                                                |
| **Content Reuse**          | `pymdownx.snippets`                                                   | Transclusion of external files and code extracts directly into documentation (`--8<-- "path/to/file"`).                                                                        |

## Configuration in Zenith

Configured in `zensical.toml` at the project root:

```python exec="1" result="toml"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/zensical.toml")
if not path.exists():
    path = Path("zensical.toml")
print(path.read_text().strip())
```

## Key Invocations

```bash
uv run poe docs-serve                  # Start live-reloading dev server (localhost:8000)
uv run zensical serve -a 0.0.0.0:8080  # Bind to custom host address and port
uv run zensical serve -o               # Open browser preview automatically
uv run poe docs-build                  # Strict production build into site/
```

### Live Reloading Watchdog

`zensical serve` includes an integrated file watchdog:

- **Instant Millisecond Rebuilds**: Monitors `docs/`, `zensical.toml`, assets, and
  stylesheets, updating pages in milliseconds as Markdown files are modified.
- **WebSocket Live Browser Sync**: Automatically pushes updates to all open browser
  tabs without manual page refreshes.
- **Agent Workflow Note**: When developers run `uv run poe docs-serve` in a terminal
  window, AI agents do not need to execute rebuilds during editing turns because the
  watchdog reloads pages automatically.

## Upstream Documentation

- [Zensical GitHub Repository](https://github.com/zensical/zensical)
- [mkdocstrings Documentation](https://mkdocstrings.github.io/)
- [Material for MkDocs Guide](https://squidfunk.github.io/mkdocs-material/)
