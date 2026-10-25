---
diataxis: reference
purpose: Document CLI argument parsing, subcommands, and Rich console styling with Typer.
---

# Typer: CLI Framework

[![Tool: Typer](https://img.shields.io/badge/cli-typer-009688.svg)](https://typer.tiangolo.com/)

`Typer` is a modern library for building command-line applications based on Python type
hints, created by Sebastián Ramírez (tiangolo). It brings the developer ergonomics,
automatic validation, and modern typing of FastAPI to the command line.

## What It Does

Typer parses command-line arguments and options using standard Python type annotations.
Using modern `typing.Annotated` metadata, parameter definitions cleanly decouple
argument validation from descriptive help text, flags, and environment fallbacks. String
inputs are automatically converted into native Python types including numbers, paths,
booleans, enums, and UUIDs.

Through its integration with Rich, Typer automatically generates colored, structured
terminal help screens, elegant error dialogs, and progress displays directly from
function signatures and docstrings. It also provides automatic tab-completion support
across all major shells.

## Why It's in Zenith

Zenith chooses Typer for projects that require a command-line interface because it
harmonizes completely with strict static type checking. Unlike legacy `argparse` or
decorator-heavy alternatives, Typer functions remain ordinary, fully typed Python
functions that pass Pyrefly strict analysis without escaping into dynamic reflection.

This design makes CLI commands trivial to unit test via `typer.testing.CliRunner`. As
applications scale from a single entry point to deep subcommand trees, Typer preserves
strict type guarantees and clean architectural boundaries.

## Terminal Demonstration

The interactive terminal below showcases the Typer CLI running with Rich formatting
using the **[Termynal](termynal.md)** widget:

<div class="termy">

```console
$ uv run zenith-example --help

<b>Usage: </b><b>zenith-example [OPTIONS] COMMAND [ARGS]...</b>

╭─ Options ────────────────────────────────────────────────────────╮
│ --version  -v        Show version and exit.                      │
│ --help               Show this message and exit.                 │
╰──────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────╮
│ greet                Display a personalized greeting.            │
╰──────────────────────────────────────────────────────────────────╯

// Invoke the greet command
$ uv run zenith-example greet "Developer"

Hello, Developer!

// View greet command help
$ uv run zenith-example greet --help

<b>Usage: </b><b>zenith-example greet [OPTIONS] [NAME]</b>

Display a personalized greeting.

╭─ Arguments ──────────────────────────────────────────────────────╮
│   name      [NAME]  Name of the person to greet. [default: World]│
╰──────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────╮
│ --help              Show this message and exit.                  │
╰──────────────────────────────────────────────────────────────────╯
```

</div>

## Configuration in Zenith

Configured in `src/<package_name>/cli.py` and registered under `[project.scripts]` in
`pyproject.toml`:

=== "Rendered Code (`my_awesome_service/cli.py`)"

    ```python
    from typing import Annotated

    from rich.console import Console
    import typer

    from my_awesome_service.core import get_greeting

    app = typer.Typer(
        name="my-awesome-service",
        help="High performance analytics engine.",
        no_args_is_help=True,  # (1)
        rich_markup_mode="rich",
    )
    console = Console()


    @app.command()
    def greet(
        name: Annotated[
            str,
            typer.Argument(help="The name to greet."),  # (2)
        ] = "World",
    ) -> None:
        """Display a personalized greeting."""
        greeting = get_greeting(name)
        console.print(f"[bold green]✨ {greeting}[/bold green]")
    ```

    1. Displays formatted Rich help automatically when invoked without arguments.
    2. Combines PEP 593 `typing.Annotated` with Typer metadata while keeping
       static type checking intact.

=== "Template Source (`{{ cookiecutter.package_name }}/cli.py`)"

```python
from typing import Annotated

import typer
from my_package.core import get_greeting
from rich.console import Console

app = typer.Typer(
    name="{{ cookiecutter.project_slug }}",
    help="{{ cookiecutter.description }}",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()


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

### Console Script Entry Points

Zenith automatically configures entry points in `pyproject.toml`:

```toml
[project.scripts]
my-awesome-service = "my_awesome_service.cli:app"
```

Because Zenith manages the environment with `uv`, you can execute the CLI immediately:

```console
$ uv run my-awesome-service --help
Usage: my-awesome-service [OPTIONS] COMMAND [ARGS]...

  High performance analytics engine.

Options:
  -v, --version  Show version and exit.
  --help         Show this message and exit.

Commands:
  greet  Display a personalized greeting.
```

### Built-in Error Handling & Validation

When users pass unrecognized options or invalid arguments, Typer catches them and
formats a helpful error message:

```console
$ uv run my-awesome-service --unknown-flag
Error: No such option: --unknown-flag
Try 'my-awesome-service --help' for help.
```

## Automated CLI Testing

CLI commands in Zenith projects are verified using `typer.testing.CliRunner` in
`tests/test_cli.py`:

```python
from my_awesome_service.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_greet_default() -> None:
    result = runner.invoke(app, ["greet"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.stdout


def test_greet_custom_name() -> None:
    result = runner.invoke(app, ["greet", "Developer"])
    assert result.exit_code == 0
    assert "Hello, Developer!" in result.stdout
```

## Conditional Scaffolding

If a project is an internal library or data engine without a command-line interface,
setting `include_cli = false` in `cookiecutter.json`:

- Removes `src/<package_name>/cli.py`.
- Removes Typer and Rich from `dependencies`.
- Removes CLI unit tests from `tests/test_cli.py`.
- Strips Termynal stylesheets and interactive CLI demos from generated documentation.

## Key Invocations

```bash
uv run my-awesome-service --help       # Show auto-generated help
uv run my-awesome-service greet "Dev"  # Run greeting command
```

## Upstream Documentation

- [Typer Official Documentation](https://typer.tiangolo.com/)
- [Typer GitHub Repository](https://github.com/fastapi/typer)
