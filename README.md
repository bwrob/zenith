<p align="center">
  <img src="assets/zenith-star.svg" alt="Zenith Emblem" width="160">
</p>

# Zenith

[![Template: Cookiecutter](https://img.shields.io/badge/template-cookiecutter-D4B830.svg)](https://github.com/cookiecutter/cookiecutter)
[![Python: 3.12+](https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14%20%7C%203.15-blue.svg)](https://www.python.org/)
[![Package Manager: uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type Checked: Pyrefly](https://img.shields.io/badge/types-pyrefly%20strict-blueviolet.svg)](https://github.com/facebook/pyrefly)
[![Documentation: Zensical](https://img.shields.io/badge/docs-zensical-teal.svg)](https://github.com/zensical/zensical)
[![Markdown: rumdl](https://img.shields.io/badge/markdown-rumdl-orange.svg)](https://github.com/rvben/rumdl)
[![Spelling: typos](https://img.shields.io/badge/spelling-typos-blue.svg)](https://github.com/crate-ci/typos)
[![Complexity: complexipy](https://img.shields.io/badge/complexity-complexipy-crimson.svg)](https://github.com/rohaquinlop/complexipy)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An opinionated Cookiecutter template for modern Python 3.12+ projects, built with Rust-based developer tooling, autonomous AI agent workflows, and automated quality guardrails.

---

## Elevator Pitch

Starting a new Python project usually means spending days wiring up linters, formatters, type checkers, test coverage, and documentation generators—or copying decaying configs from older repos and fixing whatever broke.

Zenith scaffolds a production-ready repository in seconds:
- **⚡ Modern Tooling**: Fast package management with `uv`, linting and formatting with `ruff`, strict type checking with Meta's `pyrefly`, modular boundaries with `tach`, cognitive complexity limits with `complexipy`, and documentation with `zensical`.
- **🤖 First-Class AI Agent Readiness**: Autonomous agent context discovery (`AGENTS.md`), modular lifecycle skills in `.agents/skills/`, machine-readable `llms.txt`, and clear AI governance policies.
- **🛡️ Strict Quality Guardrails**: 100% statement and branch test coverage (`fail_under = 100`), strict typing, and automated CI security analysis with `zizmor`.

> [!NOTE]
> **Project Scope**: Zenith is built for serious production packages, services, and libraries intended for long-term maintenance by teams of humans and AI agents. It is **deliberately not suited** for small two-script throwaway hacks where strict guardrails feel like friction.

---

## 📖 Documentation

For full guides, detailed architectural deep-dives, and tool configurations, visit the **[Zenith Documentation Website](https://bwrob.github.io/zenith/)**.

- **[First Steps & Core Concepts](https://bwrob.github.io/zenith/first-steps/)**: Plain-English onboarding for developers new to modern Python tooling.
- **[Philosophy & Sizing](https://bwrob.github.io/zenith/philosophy/)**: Modern tooling, AI readiness, quality guardrails, and project sizing rubric.
- **[CLI Architecture](https://bwrob.github.io/zenith/tools/typer/)**: Typer CLI structure, Rich terminal rendering, and animated Termynal demos.
- **[Tooling Stack Reference](https://bwrob.github.io/zenith/tools/)**: In-depth explanations, configuration breakdowns, and upstream links for the integrated tool stack.
- **[Agent Skills Architecture](https://bwrob.github.io/zenith/skills/)**: Lifecycle workflows for autonomous coding assistants in `.agents/skills/`.
- **[CI/CD Pipelines](https://bwrob.github.io/zenith/ci-actions/)**: GitHub Actions test matrix across Python 3.12–3.15, wheel smoke testing, and supply-chain protection.
- **[Changelog](https://bwrob.github.io/zenith/changelog/)**: Release history and version notes.

---

## Quick Start

Scaffold a new project in seconds using `uvx`:

```bash
uvx cookiecutter https://github.com/bwrob/zenith.git
```

Or using a local `cookiecutter` install:

```bash
cookiecutter gh:bwrob/zenith
```

### Initializing the Project

```bash
cd <project-slug>
uv sync
uv run poe test             # Runs test suite (100% coverage enforced)
uv run poe code-quality      # Runs full linter, formatter, type, and complexity gate
uv run poe docs-serve        # Starts live-reloading documentation server
```

---

## Essential Tasks

Every workflow in Zenith is codified through **Poe the Poet** (`uv run poe <task>`):

| Task | What it does |
|---|---|
| `uv run poe test` | Runs pytest suite enforcing 100% statement and branch coverage |
| `uv run poe test-fast` | Runs tests in parallel across CPU cores with `pytest-xdist` |
| `uv run poe code-quality` | Complete quality check: lint, format, TOML/YAML/CSS, types, complexity, boundaries |
| `uv run poe fix` | Auto-fixes lint violations, formatting, markdown, and typos |
| `uv run poe docs-serve` | Starts local Zensical live-reloading documentation dev server |
| `uv run poe docs-build` | Builds production static HTML documentation site into `site/` with strict checks |

---

## License

Distributed under the [MIT License](LICENSE).
