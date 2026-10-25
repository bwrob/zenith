---
diataxis: tutorial
purpose: Teach newcomers modern Python concepts, tooling rationale, and end-to-end scaffolding workflows from commit zero.
---

# First Steps & Core Concepts

If you are comfortable writing Python scripts but feel intimidated by modern
tooling, virtual environments, or quality gates, you are in the right place.

Zenith produces production-grade Python projects. While it uses modern
standards, you do not need to be an expert in compiler design or DevOps to use it.
This guide introduces the core concepts and workflows in plain English.

## What Zenith Actually Is

Zenith is a **project starter generator** (powered by Cookiecutter).

- **What it is NOT**: A library that you `import zenith` into your code.
- **What it IS**: A command-line wizard that builds a clean project folder on your
  computer. It configures standard directory layouts, automated test runners, and code
  checkers.

Instead of spending days setting up configuration files, Zenith gives you a
production-grade foundation in seconds.

## Step 0: Installing Uv

Modern Python projects use **`uv`** as an all-in-one package and environment manager.

Before scaffolding a Zenith project, install `uv` on your machine:

=== "macOS & Linux"

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

=== "Windows"

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

> [!TIP]
> **You do not need to install Python 3.13 manually.** `uv` automatically downloads and
> manages the correct Python version for your project. Several Zenith tools use Rust for
> speed. You do **not** need to install Rust or Cargo. Everything runs as pre-compiled
> packages managed by `uv`.

## Your First 5 Minutes: Zero to Running Code

Follow these steps to create a project and run its first commands.

### 1. Scaffold Your Project

Run Cookiecutter directly through `uvx` (which runs tools without permanent
installation):

```shell
uvx cookiecutter https://github.com/bwrob/zenith.git
```

Follow the prompts. If you are unsure, press `Enter` to accept the defaults.

### 2. Enter and Sync Your Project

Move into your new folder and initialize your environment:

```shell
cd my-awesome-service
uv sync
```

`uv sync` creates a private project sandbox (a virtual environment) and downloads
all necessary tools.

### 3. Run Your Application

If you enabled the command-line interface (CLI) during setup, your project is
already an executable application:

```console
$ uv run my-awesome-service --help
Usage: my-awesome-service [OPTIONS] COMMAND [ARGS]...

  High performance analytics engine

Options:
  -v, --version  Show version and exit.
  --help         Show this message and exit.

Commands:
  greet  Display a personalized greeting.
```

Run the built-in `greet` command:

```console
$ uv run my-awesome-service greet "Developer"
✨ Hello, Developer!
```

### 4. Check Your Live Documentation

Every project includes a live-reloading documentation website powered by Zensical:

```console
$ uv run poe docs-serve
Serving documentation at http://127.0.0.1:8000
```

Open `http://127.0.0.1:8000` in your browser. Any edits you make to markdown files in
`docs/` will update live automatically in your browser.

## Where Do I Actually Write Code

A scaffolded Zenith repository has many files, but your daily work happens in only
a few places:

```tree
my-awesome-service/
    src/my_awesome_service/     # 🟢 YOUR WORKSPACE: All application code lives here!
    tests/                      # 🟢 YOUR TESTS: Automated tests for your code
    docs/                       # 🟢 YOUR DOCS: Markdown documentation files
    pyproject.toml              # 🟡 PROJECT SETTINGS: Dependencies and metadata
    poe_tasks.toml              # 🔒 TASK RUNNER: Pre-tuned task shortcuts
    ruff.toml                   # 🔒 GUARDRAILS: Pre-tuned linter rules
    pyrefly.toml                # 🔒 GUARDRAILS: Pre-tuned type checker settings
    tach.toml                   # 🔒 GUARDRAILS: Pre-tuned module boundaries
```

> [!NOTE]
> **The "Engine Room" Rule**
> The files ending in `.toml` in the project root are pre-configured background
> settings—like the pre-tuned engine in a car. You can safely ignore them. You do not
> need to open or configure them to write your application.

## Everyday Workflows

Use these tasks for common development work after setup.

### How to Add a New Package

Whenever a tutorial says `pip install <package>`, use `uv add` instead:

```shell
uv add httpx
```

This installs the package into your private sandbox and records it in `pyproject.toml`
automatically.

### How to Run a Python Script

Instead of running global `python my_script.py`, prefix your commands with `uv run`:

```shell
uv run python -m my_awesome_service.cli
```

`uv run` ensures your script runs inside your isolated project sandbox where all
installed packages are available.

### How to Run Project Tasks

Zenith uses **Poe the Poet** as a task shortcut runner. Instead of memorizing long
terminal flags, use these four commands:

- `uv run poe test`: Runs your automated test suite.
- `uv run poe fix`: Automatically formats your code and resolves style issues.
- `uv run poe code-quality`: Runs static checks (types, linters, complexity).
- `uv run poe docs-serve`: Launches your documentation website locally at
  `http://localhost:8000`.

## Understanding Quality Gates (Why Are Tests Failing?)

When you run `uv run poe test`, Zenith checks test coverage.

Zenith has a strict rule: **100% test coverage**. This means every line of code you
write in `src/` must have a corresponding test in `tests/`.

If you write a new function without a test, `uv run poe test` stops and highlights
the un-tested line in red. **Nothing is broken.** The tool is simply reminding you
to write a test.

### A Hands-on Experiment: Breaking and Satisfying the Guardrail

Let's see what happens when you write code without a test:

**Step 1: Write an un-tested function** in `src/my_awesome_service/calculator.py`:

```python
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
```

**Step 2: Run `uv run poe test` to see the guardrail in action**:

```console
$ uv run poe test
================================ tests coverage ================================
Name                                  Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------------------------
src/my_awesome_service/calculator.py      2      1      0      0    50%   3
---------------------------------------------------------------------------------
TOTAL                                    35      1      4      0    97%

FAIL Required test coverage of 100% not reached. Total coverage: 97.14%
```

The test runner shows exactly which line is missing test coverage (line 3 in
`calculator.py`).

**Step 3: Add the matching test** in `tests/test_calculator.py`:

```python
from my_awesome_service.calculator import add


def test_add() -> None:
    assert add(2, 3) == 5
```

**Step 4: Re-run `uv run poe test`**:

```console
$ uv run poe test
================================ tests coverage ================================
TOTAL                                    35      0      4      0   100%

Required test coverage of 100.0% reached. Total coverage: 100.00%
======================== 3 passed in 0.45s ========================
```

The gate turns green. Tests now cover all statements and branches.

## Step-by-Step Recap: What Just Happened

Here is the mental model to remember as you build:

1. **`uv` is your engine**: It manages your Python versions and packages inside an
   isolated sandbox. You never need to worry about broken system Python installs.
2. **Your code lives in `src/`**: Focus your energy on `src/` and `tests/`. The `.toml`
   files in the root directory are background guardrails that stay out of your way.
3. **`uv add` is your `pip install`**: When you need a library, type `uv add <package>`.
4. **`uv run poe ...` are your project controls**: Run `poe test` to check your code,
   `poe fix` to auto-format, and `poe code-quality` to check types and boundaries.
5. **Red tests are safety nets**: Quality gate errors indicate an un-tested branch or
   type mismatch before code reaches production.

## Plain-English Tool Glossary

Zenith includes several tools that run quietly in the background. Here is what each
tool does for you:

| Tool             | What It Does for You     | Why It Is Helpful                                                                   |
| ---------------- | ------------------------ | ----------------------------------------------------------------------------------- |
| **`uv`**         | Package & Python Manager | Installs libraries fast and manages Python versions without breaking your computer. |
| **`ruff`**       | Code Cleaner & Formatter | Formats code styling and catches syntax bugs in milliseconds.                       |
| **`pyrefly`**    | Type Safety Inspector    | Analyzes type hints so you do not accidentally pass incompatible data to functions. |
| **`poe`**        | Shortcut Command Runner  | Provides easy commands like `uv run poe test` instead of long commands.             |
| **`prek`**       | Git Commit Guard         | Checks your code automatically when you run `git commit` to block invalid commits.  |
| **`tach`**       | Architecture Protector   | Prevents circular imports and keeps modules separated cleanly.                      |
| **`complexipy`** | Simplicity Checker       | Warns you if a function has too many nested loops or branches.                      |
| **`zensical`**   | Documentation Engine     | Turns markdown files in `docs/` into a searchable website.                          |
| **`typos`**      | Spell Checker            | Catches spelling mistakes in your code and documentation.                           |

## Where to Go Next

Now that you understand the basic workflow:

- Explore [The Tooling Stack](tools/index.md) to learn more about each individual tool.
- Read [The Zenith Philosophy](philosophy.md) for the design principles behind the
  guardrails.
