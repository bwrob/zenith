---
diataxis: reference
purpose: Provide the public Python API signature reference and CLI command options generated via mkdocstrings.
---

# API Reference

This page documents the public API of **{{ cookiecutter.project_name }}**, automatically
generated from source code docstrings via **mkdocstrings** and **griffe** static AST
analysis.

The primary entry point is [`get_greeting`](#core-module). Signatures automatically
cross-reference parameter types, link to official Python documentation inventories, and
render collapsible backlink trees indicating which pages reference each symbol.

## Core Module

::: {{ cookiecutter.package_name }}.core

{% if cookiecutter.include_cli in [True, "yes", "true", "True", "1"] -%}

## CLI Module

::: {{ cookiecutter.package_name }}.cli

{% endif -%}

## AI & LLM Documentation Indexing

During documentation builds (`uv run poe docs-build`), the `[project.plugins.llmstxt]`
plugin automatically compiles machine-readable markdown indices under `site/`:

- **`site/llms.txt`**: A concise, curated sitemap of all documentation sections, guides,
  and modules for AI coding assistants.
- **`site/llms-full.txt`**: A complete, concatenated full-text export containing all
  documentation pages and rendered API signatures, optimized for LLM context windows
  (Cursor, Claude Code, Copilot, and Gemini CLI).
