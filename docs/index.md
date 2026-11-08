---
diataxis: explanation
purpose: Introduce Zenith, showcase the four architectural pillars, and guide developers from quickstart scaffolding to the full documentation suite.
---

<p align="center">
  <img src="assets/zenith-banner-dark.svg#gh-dark-mode-only" alt="Zenith" width="420">
  <img src="assets/zenith-banner-light.svg#gh-light-mode-only" alt="Zenith" width="420">
</p>

<p align="center" style="font-size: 1.15rem; font-weight: 500;">
  An opinionated project template and interactive CLI for Python 3.12+ packages, services, and AI-assisted engineering.
</p>

Starting a production Python repository usually means spending days wiring linters, type
checkers, test coverage, and CI pipelines—or copying decaying configuration files from
an older project. **Zenith** (`zenith-template`) is a
[Cookiecutter](tools/cookiecutter.md) template and terminal wizard that generates a
complete, ready-to-ship Python 3.12+ repository in seconds.

Every generated project is **human-first and AI-optional**: you can scaffold a purely
traditional Python repository (`--ai-tools none`), enable configurations only for your
preferred coding assistants, or include the full suite of modular agent skills.

## The Four Pillars

<div class="grid cards" markdown>

-   **[Modern Rust-Based Tooling](tools/index.md)**

    ---

    Sub-second local feedback powered by **[uv](tools/uv.md)**,
    **[Ruff](tools/ruff.md)**, **[Pyrefly](tools/pyrefly.md)**,
    **[Tach](tools/tach.md)**, **[Deptry](tools/deptry.md)**,
    **[complexipy](tools/complexipy.md)**, and
    **[Zensical](tools/zensical.md)**—all orchestrated through
    **[Poe the Poet](tools/poethepoet.md)** for identical local and CI runs.

-   **[Automated Quality Guardrails](philosophy.md)**

    ---

    Enforced locally via **[prek](tools/prek.md)** hooks and in CI: **100% statement and
    branch coverage** (`fail_under = 100`), strict static typing, cognitive complexity
    limits (`<= 10`), module boundary checks, and GitHub Actions security auditing.

-   **[Hermetic Delivery & CI/CD](ci-actions.md)**

    ---

    Multi-OS test matrices across Python 3.12–3.15, lowest-direct dependency checks,
    isolated wheel and sdist smoke tests, GitHub Pages docs deployment, and PyPI
    Trusted Publishing with PEP 740 provenance attestations.

-   **[Elective AI Agent Readiness](skills/index.md)**

    ---

    Pre-wired context discovery (`AGENTS.md`), 36 modular `.agents/skills/`, and a
    Spec-Driven Development (`sdd`) lifecycle across
    [13 coding assistants](skills/index.md#agentic-tool-compatibility-matrix)—or zero
    AI files when disabled.

</div>

## Quick Start

Scaffold a new project using the interactive terminal wizard, headless CLI flags, or
Cookiecutter:

=== "Interactive Wizard (Recommended)"

    ```bash
    uvx zenith-template
    ```

=== "Headless CLI"

    ```bash
    uvx zenith-template --no-input --name "My Project" --ai-tools recommended --sync
    ```

=== "Cookiecutter"

    ```bash
    uvx cookiecutter gh:bwrob/zenith
    ```

Requires [Astral `uv`](https://docs.astral.sh/uv/getting-started/installation/). New to
`uv`, virtual environments, or project templates? Start with
[First Steps & Core Concepts](first-steps.md).

Once generated, verify your repository immediately:

<!-- termynal -->
```console
$ uvx zenith-template
✦ Project successfully scaffolded at ./my-project
$ cd my-project
$ uv sync
$ uv run poe test
100% test coverage reached (statements and branches).
$ uv run poe code-quality
All quality gates passed!
$ uv run poe docs-serve
Serving documentation at http://127.0.0.1:8000
```

## What Gets Generated

Generated projects use a `src/` layout that separates domain logic, CLI entry points,
tests, documentation, and automation configs:

```tree
my-project/
    src/my_project/             # Core package source, lazy exports, and Typer CLI
    tests/                      # Unit, property (Hypothesis), and snapshot tests
    docs/                       # Zensical documentation site with live preview
    .github/workflows/          # CI test matrix, docs deployment, and PyPI publishing
    .agents/skills/             # Elective agent skills (workflows, tools, style guides)
    pyproject.toml              # Dependencies and PEP 621 package metadata
    poe_tasks.toml              # Unified task runner definitions (Poe the Poet)
    prek.toml                   # Fast pre-commit and pre-push verification hooks
```

Every repository starts with strictly typed modules and a passing test suite combining
unit, snapshot, and property-based checks. Want to inspect a complete rendered project
with live GitHub Actions runs before scaffolding? Browse
**[bwrob/zenith-example on GitHub](https://github.com/bwrob/zenith-example)**.

=== "src/my_project/core.py"

    ```python
    """Core functions for my-project."""


    def get_greeting(name: str) -> str:
        """Return a personalized greeting message."""
        clean_name = name.strip()
        if not clean_name:
            clean_name = "World"
        return f"Hello, {clean_name}!"
    ```

=== "src/my_project/cli.py"

    ```python
    """Command line interface for my-project."""

    from __future__ import annotations

    from typing import Annotated

    import typer
    from my_project.core import get_greeting
    from rich.console import Console

    app: typer.Typer = typer.Typer(
        name="my-project",
        no_args_is_help=True,
        rich_markup_mode="rich",
    )
    console: Console = Console()


    @app.command()
    def greet(
        name: Annotated[
            str,
            typer.Argument(help="The name to greet."),
        ] = "World",
    ) -> None:
        """Display a personalized greeting."""
        greeting = get_greeting(name)
        console.print(f"[bold green]✨ {greeting}[/bold green]")
    ```

=== "tests/test_core.py"

    ```python
    """Unit tests for core functionality."""

    from hypothesis import given, strategies
    from my_project.core import get_greeting


    def test_get_greeting_default() -> None:
        """Test get_greeting with empty string defaults to World."""
        assert get_greeting("") == "Hello, World!"
        assert get_greeting("   ") == "Hello, World!"


    @given(strategies.text())
    def test_get_greeting_property(name: str) -> None:
        """Property-based test: get_greeting always returns a well-formed greeting."""
        greeting = get_greeting(name)
        assert greeting.startswith("Hello, ")
        assert greeting.endswith("!")
    ```

## Everyday Commands

All development workflows run hermetically through
**[Poe the Poet](tools/poethepoet.md)** (`uv run poe <task>`):

| Command                       | Purpose                                                                                |
| :---------------------------- | :------------------------------------------------------------------------------------- |
| `uv run poe test`             | Run `pytest` across CPU cores and enforce 100% statement and branch coverage.          |
| `uv run poe code-quality`     | Run the full static quality pipeline (Ruff, Taplo, Prettier, rumdl, Pyrefly, Tach).    |
| `uv run poe fix`              | Auto-fix Python lint/format issues, TOML/Markdown formatting, and common spelling.     |
| `uv run poe docs-serve`       | Start the local live-reloading Zensical documentation server at `127.0.0.1:8000`.      |
| `uv run poe docs-build`       | Build the static HTML documentation site in `--strict` mode.                           |
| `uv run prek run --all-files` | Run all configured `pre-commit` formatting and validation hooks across the repository. |

## Explore the Documentation

| Guide                                             | What You Will Find                                                                                          |
| :------------------------------------------------ | :---------------------------------------------------------------------------------------------------------- |
| **[First Steps & Core Concepts](first-steps.md)** | Plain-English onboarding for `uv`, `poe`, interactive scaffolding, and adding your first feature.           |
| **[Philosophy & Project Sizing](philosophy.md)**  | Architectural trade-offs, strict quality guardrails, and deciding when Zenith fits your project.            |
| **[Tooling Stack Reference](tools/index.md)**     | Deep-dives and exact configuration breakdowns for all 22 integrated tools.                                  |
| **[CI/CD Pipelines](ci-actions.md)**              | GitHub Actions test matrices, Dependabot pass-through gates, and PyPI Trusted Publishing.                   |
| **[Agent Skills Architecture](skills/index.md)**  | Compatibility across 13 coding assistants, `.agents/skills/` taxonomy, and Spec-Driven Development (`sdd`). |
| **[Changelog](changelog.md)**                     | Release history, version milestones, and upgrade notes.                                                     |
