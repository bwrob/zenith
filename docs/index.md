# Zenith

<p align="center">
  <img src="assets/zenith-star.svg" alt="Zenith Emblem" width="140">
</p>

<p align="center" style="font-size: 1.15rem; font-weight: 500;">
  An opinionated template for modern Python 3.12+ services, packages, and autonomous AI agents.
</p>

---

## Quick Start

> [!TIP]
> **New to modern Python tooling or project templates?**
> If terms like virtual environments, `uv`, or project scaffolding are unfamiliar, start
> with the [First Steps & Core Concepts](first-steps.md) guide.

Scaffold a production-grade repository in seconds using `uvx`:

<div class="termy">

```console
$ uvx cookiecutter https://github.com/bwrob/zenith.git
$ cd my-awesome-service
$ uv sync
$ uv run poe test
100% test coverage reached (statements and branches).
$ uv run poe code-quality
All quality gates passed!
$ uv run poe docs-serve
Serving documentation at http://127.0.0.1:8000
```

</div>

---

## The Four Pillars

Zenith eliminates scaffolding debt and quality decay from commit zero across four
foundational pillars:

<div class="grid cards" markdown>

-   **[Modern Rust-Based Tooling](tools/index.md)**

    ---

    Sub-second developer loops powered by **[uv](tools/uv.md)**,
    **[Ruff](tools/ruff.md)**, **[Pyrefly](tools/pyrefly.md)**,
    **[Tach](tools/tach.md)**, **[complexipy](tools/complexipy.md)**, and
    **[Zensical](tools/zensical.md)**. All tasks run through
    **[Poe the Poet](tools/poethepoet.md)** for identical local and CI execution.

-   **[First-Class AI Agent Readiness](skills/index.md)**

    ---

    Built for autonomous pair-programming with Claude Code, Gemini CLI, Antigravity, and
    Codex. Canonical `AGENTS.md` context, modular skills in
    [`.agents/skills/`](skills/index.md), transparent review standards, and automated
    `llms.txt`.

-   **[Automated Quality Guardrails](philosophy.md)**

    ---

    Zero compromises: **100% mandatory test coverage** (`fail_under = 100`), strict
    static typing with Pyrefly, cognitive complexity <= 10 per function, module boundary
    enforcement, and CI security auditing with **[zizmor](tools/zizmor.md)**.

-   **[Hermetic Delivery & CI/CD](ci-actions.md)**

    ---

    Zero-drift automation: multi-version matrix testing across Python 3.12–3.15,
    isolated wheel package smoke tests, automated documentation publishing, and PyPI
    Trusted Publishing with supply-chain safeguards.

</div>

---

## Architecture at a Glance

Scaffolded projects enforce strict separation between domain logic, public interfaces,
and automated quality guardrails:

```tree
my-awesome-service/
    src/my_awesome_service/     # Core package source, public API, and optional Typer CLI
    tests/                      # Comprehensive test suite with 100% coverage gate
    docs/                       # Zensical documentation site with live preview
    .agents/skills/             # Modular agent skills (workflows, tools, style guides)
    pyproject.toml              # Dependencies and packaging standards (PEP 621)
    poe_tasks.toml              # Hermetic task runner commands (Poe the Poet)
    AGENTS.md                   # Canonical AI agent instructions and boundary rules
```

### Production-Grade Code by Default

Every generated repository produces strictly typed, immutable, and fully tested
Python out of the box:

=== "src/my_awesome_service/core.py"

    ```python
    """Core domain logic with strict typing and immutability."""

    from dataclasses import dataclass


    @dataclass(frozen=True, slots=True)
    class Greeter:
        """Greeting domain entity."""

        recipient: str

        def format(self) -> str:
            """Format greeting with recipient."""
            return f"Hello, {self.recipient}!"
    ```

=== "src/my_awesome_service/cli.py"

    ```python
    """Command line interface powered by Typer and Rich."""

    from typing import Annotated

    from rich.console import Console
    import typer

    from my_awesome_service.core import Greeter

    app = typer.Typer(no_args_is_help=True)
    console = Console()


    @app.command()
    def greet(
        name: Annotated[str, typer.Argument(help="Name to greet.")] = "World",
    ) -> None:
        """Display a personalized greeting."""
        greeter = Greeter(recipient=name)
        console.print(f"[bold green]✨ {greeter.format()}[/bold green]")
    ```

=== "tests/test_cli.py"

    ```python
    """Automated CLI test suite with 100% coverage gate."""

    from typer.testing import CliRunner

    from my_awesome_service.cli import app

    runner = CliRunner()


    def test_greet() -> None:
        result = runner.invoke(app, ["greet", "Zenith"])
        assert result.exit_code == 0
        assert "✨ Hello, Zenith!" in result.stdout
    ```

> [!TIP]
> **Explore the Live Showcase Repository**
>
> Browse instantiated code, commit history, and GitHub Actions runs in
> **[bwrob/zenith-example on GitHub](https://github.com/bwrob/zenith-example)**.
> For release notes and version history, see the **[Changelog](changelog.md)**.
