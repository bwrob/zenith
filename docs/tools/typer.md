---
diataxis: reference
purpose: Document CLI argument parsing, subcommands, and Rich console styling with Typer.
---

# Typer: CLI Framework

[![Tool: Typer](https://img.shields.io/badge/cli-typer-009688.svg)](https://typer.tiangolo.com/)

`Typer` builds command-line interfaces from standard Python 3.12+ type annotations and
renders terminal help and output with Rich. Because Typer commands are ordinary typed
functions using `typing.Annotated`, they pass strict Pyrefly type checking and are
straightforward to test with `typer.testing.CliRunner`.

## Terminal Demonstration

<!-- termynal -->
```console
$ uv run my-project --help

<b>Usage: </b><b>my-project [OPTIONS] COMMAND [ARGS]...</b>

╭─ Options ────────────────────────────────────────────────────────╮
│ --version  -v        Show version and exit.                      │
│ --help               Show this message and exit.                 │
╰──────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────╮
│ greet                Display a personalized greeting.            │
╰──────────────────────────────────────────────────────────────────╯

# Invoke the greet command
$ uv run my-project greet "Developer"

✨ Hello, Developer!
```

## Configuration in Zenith

When `include_cli` is enabled (the default), Zenith scaffolds
`src/<package_name>/cli.py` and wires the console script entry point in
`pyproject.toml`:

```python
from __future__ import annotations

from typing import Annotated

import typer
from my_project import __version__
from my_project.core import get_greeting
from rich.console import Console

app: typer.Typer = typer.Typer(
    name="my-project",
    help="A modern Python project.",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console: Console = Console()


def _version_callback(*, value: bool) -> None:
    """Print version and exit if --version is passed."""
    if value:
        console.print(f"my-project version: [bold cyan]{__version__}[/bold cyan]")
        raise typer.Exit


@app.callback()
def main(
    *,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """CLI root callback."""


@app.command()
def greet(
    name: Annotated[
        str,
        typer.Argument(help="The name of the person to greet."),
    ] = "World",
) -> None:
    """Display a personalized greeting."""
    message = get_greeting(name)
    console.print(f"✨ [bold green]{message}[/bold green]")
```

### Console Script Entry Point

`pyproject.toml` registers the CLI entry point against `my_project.__main__:main` (which
invokes `app()` from `my_project.cli`):

```toml
[project.scripts]
    my-project = "my_project.__main__:main"
```

Meanwhile, `src/my_project/__init__.py` uses PEP 562 lazy `__getattr__` exports so
importing library symbols (`from my_project import get_greeting`) never eagerly imports
`typer` or `my_project.cli`.

## Testing CLI Commands

CLI commands are tested in `tests/test_cli.py` using `typer.testing.CliRunner`:

```python
from __future__ import annotations

from my_project import __version__
from my_project.cli import app
from typer.testing import CliRunner

runner: CliRunner = CliRunner()


def test_cli_greet_default() -> None:
    """Verify default CLI greeting command."""
    result = runner.invoke(app, ["greet"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.stdout


def test_cli_version() -> None:
    """Verify --version flag output."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout
```

## Conditional Scaffolding

For pure libraries that do not need a CLI, pass `--no-cli` to `uvx zenith-template` (or
set `include_cli = false`). The post-generation hook removes `src/<pkg>/cli.py`,
`src/<pkg>/__main__.py`, `tests/test_cli.py`, `[project.scripts]`, and the `typer` and
`termynal` dependencies.

## Key Invocations

```bash
uv run my-project --help          # Display Rich-formatted help
uv run my-project --version       # Print package version
uv run my-project greet "Dev"     # Run the greet subcommand
```

## Upstream Documentation

- [Typer Official Documentation](https://typer.tiangolo.com/)
- [Typer GitHub Repository](https://github.com/fastapi/typer)
