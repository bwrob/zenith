---
diataxis: reference
purpose: Document template variables, lifecycle hooks, and project generation mechanics with Cookiecutter.
---

# Cookiecutter: Templating Engine

[![Tool: Cookiecutter](https://img.shields.io/badge/template-cookiecutter-D4B830.svg)](https://github.com/cookiecutter/cookiecutter)

`Cookiecutter` is a cross-platform command-line utility that creates projects from
project templates (cookiecutters). Zenith uses the Cookiecutter template format.

## What It Does

Cookiecutter renders directory structures and configuration files using Jinja
templating. By evaluating user inputs against interactive prompts and choice matrices
defined in `cookiecutter.json`, it dynamically scaffolds complete projects. Lifecycle
hooks executed before and after file generation validate input parameters and perform
programmatic filesystem adjustments.

## Why It Is in Zenith

Zenith operates as a Cookiecutter template to provide instant, zero-install
scaffolding via `uvx cookiecutter gh:bwrob/zenith`. As the universal standard for
project templating across the Python community, Cookiecutter ensures broad
compatibility with existing developer workflows.

Zenith uses post-generation lifecycle hooks (`hooks/post_gen_project.py`) to enforce
project hygiene. Hooks strip unselected features like CLI code, remove explanatory
comments, and configure symlinks for AI coding agents.

## Configuration in Zenith

Configured in `cookiecutter.json` at the repository root:

```python exec="1" result="json"
from pathlib import Path

print(Path("cookiecutter.json").read_text().strip())
```

## Key Invocations

```bash
# Scaffold a new project from remote repository
uvx cookiecutter https://github.com/bwrob/zenith.git

# Scaffold locally during template development
cookiecutter .
```

## Upstream Documentation

- [Cookiecutter Documentation](https://cookiecutter.readthedocs.io/)
- [Cookiecutter GitHub Repository](https://github.com/cookiecutter/cookiecutter)
