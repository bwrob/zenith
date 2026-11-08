---
diataxis: explanation
purpose: Introduce Zenith, showcase the four architectural pillars, and guide developers to quickstart workflows.
---

<p align="center">
  <img src="assets/zenith-banner-dark.svg#gh-dark-mode-only" alt="Zenith" width="420">
  <img src="assets/zenith-banner-light.svg#gh-light-mode-only" alt="Zenith" width="420">
</p>

<p align="center" style="font-size: 1.15rem; font-weight: 500;">
  An opinionated template for modern Python 3.12+ services, packages, and autonomous AI agents.
</p>

> [!NOTE]
> **What Zenith Is**: Zenith is a [Cookiecutter](tools/cookiecutter.md) project
> template and interactive CLI (`zenith-template`) for Python 3.12+. Rather than a
> runtime library you import, it generates a complete repository with fast Rust-based
> tooling, CI workflows, and optional AI agent skills.
>
> **Human-First, AI-Optional**: Every AI config and agent skill is elective during
> scaffolding. You can generate a purely traditional Python repository (`--ai-tools
> none`) or include configs and skills for your preferred coding assistants.

## Quick Start

> [!TIP]
> **Prerequisites & First Steps**
> Zenith requires Astral **`uv`**. If you do not have `uv` installed yet:
>
> ```bash
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```
>
> If terms like virtual environments, `uv`, or project scaffolding are unfamiliar, start
> with the [First Steps & Core Concepts](first-steps.md) guide.

Scaffold a new repository with the interactive terminal wizard via `uvx` (see
[First Steps & Core Concepts](first-steps.md) for headless CLI flags and wizard
options):

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

## The Four Pillars

<div class="grid cards" markdown>

-   **[Modern Rust-Based Tooling](tools/index.md)**

    ---

    Fast local feedback powered by **[uv](tools/uv.md)**,
    **[Ruff](tools/ruff.md)**, **[Pyrefly](tools/pyrefly.md)**,
    **[Tach](tools/tach.md)**, **[Deptry](tools/deptry.md)**,
    **[complexipy](tools/complexipy.md)**, and
    **[Zensical](tools/zensical.md)**. All tasks run through
    **[Poe the Poet](tools/poethepoet.md)** for identical local and CI execution.

-   **[First-Class AI Agent Readiness](skills/index.md)**

    ---

    Built for autonomous pair-programming when desired, yet completely elective.
    Scaffold all assistants, select your preferred tools, or exclude AI configs
    entirely. Audited in the
    [Agentic Tool Matrix](skills/index.md#agentic-tool-compatibility-matrix).

-   **[Automated Quality Guardrails](philosophy.md)**

    ---

    Enforced locally and in CI: **100% statement and branch coverage**
    (`fail_under = 100`), strict static typing with Pyrefly, cognitive complexity
    limits (`<= 10`), module layer boundaries, and workflow security auditing.

-   **[Hermetic Delivery & CI/CD](ci-actions.md)**

    ---

    Multi-OS test matrices across Python 3.12–3.15, lowest-direct dependency checks,
    isolated wheel and sdist smoke tests, GitHub Pages docs deployment, and PyPI
    Trusted Publishing with PEP 740 provenance attestations.

</div>

## Architecture at a Glance

Generated projects separate domain logic, CLI entry points, tests, and documentation:

```tree
my-project/
    src/my_project/             # Core package source, lazy exports, and Typer CLI
    tests/                      # Unit, property (Hypothesis), and snapshot tests
    docs/                       # Zensical documentation site with live preview
    .agents/skills/             # Modular agent skills (workflows, tools, style guides)
    pyproject.toml              # Dependencies and packaging standards (PEP 621)
    poe_tasks.toml              # Hermetic task runner commands (Poe the Poet)
    AGENTS.md                   # Canonical AI agent instructions and boundary rules
```

### Scaffolded Code Out of the Box

Every generated project starts with strictly typed modules and a test suite combining
unit, snapshot, and property-based checks:

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

> [!TIP]
> **Explore the Live Showcase Repository**
>
> Browse instantiated code, commit history, and GitHub Actions runs in
> **[bwrob/zenith-example on GitHub](https://github.com/bwrob/zenith-example)**.
> For release notes and version history, see the **[Changelog](changelog.md)**.
