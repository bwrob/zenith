---
diataxis: reference
purpose: Document static documentation compilation, live development serving, and plugin configuration with Zensical.
---

# Zensical: Documentation Generator

[![Tool: Zensical](https://img.shields.io/badge/docs-zensical-teal.svg)](https://github.com/zensical/zensical)

`Zensical` is a static documentation generator configured entirely in TOML
(`zensical.toml`). Zenith enables strict validation (`zensical build --strict --clean`)
so broken internal links, invalid heading anchors, or unresolved footnotes fail the
build immediately.

## Integrated Plugins

| Plugin                     | Capability                  | Purpose in Zenith                                                                                                                                     |
| :------------------------- | :-------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`gh-admonitions`**       | GitHub Alert Callouts       | Renders GitHub-flavored alerts (`> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]`).                                           |
| **`llmstxt`**              | AI Context Feeds            | Generates `site/llms.txt` and `site/llms-full.txt` during `docs-build` so AI coding assistants can ingest full project documentation and API symbols. |
| **`markdown-exec`**        | Dynamic Code Execution      | Executes fenced blocks marked with `exec="1"` (`python`, `bash`, `sh`, `tree`, `md`) at build time.                                                   |
| **`mkdocstrings[python]`** | Automated API Documentation | Extracts public signatures, type parameters, and Google-style docstrings offline via **[Griffe](griffe.md)** (`::: my_project.core`).                 |

## Markdown Extensions

| Category                   | Extensions                                                            | Enabled Syntax                                                                                        |
| :------------------------- | :-------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------- |
| **Callouts & Details**     | `admonition`, `pymdownx.details`                                      | Collapsible `??? note "Title"` / `???+ tip` blocks and standard admonitions.                          |
| **Code & Diagrams**        | `pymdownx.superfences`, `pymdownx.highlight`, `pymdownx.inlinehilite` | Fenced `mermaid` diagrams, `tree` directory blocks, line anchors, and inline `#!python` highlighting. |
| **Math & Symbols**         | `pymdownx.arithmatex`, `pymdownx.emoji`, `pymdownx.smartsymbols`      | Client-side MathJax LaTeX rendering (`\( ... \)` and `$$ ... $$`) and Twemoji SVG icons.              |
| **Interactive UI**         | `pymdownx.tabbed`, `pymdownx.tasklist`, `zensical.extensions.preview` | Linked content tabs (`=== "Tab"`), task checkboxes (`- [x]`), and internal link hover previews.       |
| **Transclusion & Console** | `pymdownx.snippets`, `termynal`                                       | File transclusion (`--8<-- "path/to/file"`) and **[Termynal](termynal.md)** animated console blocks.  |

## Configuration Excerpt

Representative `zensical.toml` configuration:

```toml
[project]
    repo_name        = "author/my-project"
    repo_url         = "https://github.com/author/my-project"
    site_description = "A modern Python project."
    site_name        = "My Project"

    nav = [
        { "Overview" = "index.md" },
        { "Getting Started" = "getting-started.md" },
        { "API Reference" = "reference.md" },
        { "Architecture Decisions" = [
            "adr/index.md",
            "adr/0001-record-architecture-decisions.md",
        ] },
        { "Changelog" = "changelog.md" },
    ]

    [project.validation]
        invalid_link_anchors  = true
        invalid_links         = true
        shadowed_definitions  = true
        shadowed_footnotes    = true
        unresolved_footnotes  = true
        unresolved_references = true
        unused_definitions    = true
        unused_footnotes      = true

    [project.plugins.gh-admonitions]

    [project.plugins.llmstxt]
        full_output = "llms-full.txt"

    [project.plugins.markdown-exec]

    [project.plugins.mkdocstrings.handlers.python]
        inventories = ["https://docs.python.org/3/objects.inv"]
        paths       = ["src"]
```

## Key Invocations

```bash
uv run poe docs-serve                  # Start dev server at http://127.0.0.1:8000
uv run zensical serve -a 0.0.0.0:8080  # Bind dev server to custom host and port
uv run poe docs-build                  # Strict build into site/
```

> [!TIP]
> **Live Reloading Watchdog**: When `uv run poe docs-serve` is running in a terminal,
> Zensical watches `docs/` and `zensical.toml` and hot-reloads open browser tabs
> automatically. Avoid running `zensical build` while `zensical serve` is active; run
> `uv run poe docs-build` once during final pre-flight verification.

## Upstream Documentation

- [Zensical GitHub Repository](https://github.com/zensical/zensical)
- [mkdocstrings Documentation](https://mkdocstrings.github.io/)
