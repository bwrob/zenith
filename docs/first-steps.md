# First Steps & Core Concepts

If you are comfortable writing Python scripts but feel intimidated by modern
tooling, virtual environments, or quality gates, you are in the right place.

Zenith produces production-grade Python projects. While it uses modern
standards, you do not need to be an expert in compiler design or DevOps to use it.
This guide introduces the core concepts and workflows in plain English.

---

## What Zenith Actually Is

Zenith is a **project starter generator** (powered by Cookiecutter).

- **What it is NOT**: A library that you `import zenith` into your code.
- **What it IS**: A command-line wizard that builds a brand-new, clean project folder
  on your computer with professional directory layouts, automated test runners, and
  code checkers already wired up.

Instead of spending days setting up configuration files, Zenith gives you a
production-grade foundation in seconds.

---

## Step 0: Installing uv

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
> **You do not need to install Python 3.13 manually!**
> `uv` automatically downloads and manages the correct Python version for your project.
> Furthermore, while Zenith tools are written in Rust for blazing speed, you do **not**
> need to install Rust or Cargo—everything runs as pre-compiled Python tools managed
> by `uv`.

---

## Your First 5 Minutes: Zero to Running Code

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

```shell
uv run my-awesome-service --help
```

You can also run commands directly with:

```shell
uv run my-awesome-service hello "World"
```

---

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

---

## Everyday Workflows

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
- `uv run poe fix`: Automatically formats your code and fixes style issues.
- `uv run poe code-quality`: Runs static checks (types, linters, complexity).
- `uv run poe docs-serve`: Launches your documentation website locally at
  `http://localhost:8000`.

---

## Understanding Quality Gates (Why Are Tests Failing?)

When you run `uv run poe test`, Zenith checks test coverage.

Zenith has a strict rule: **100% test coverage**. This means every line of code you
write in `src/` must have a corresponding test in `tests/`.

If you write a new function without a test, `uv run poe test` stops and highlights
the un-tested line in red. **Nothing is broken.** The tool is simply reminding you
to write a test.

### Quick Example: Adding a Function and a Test

1. Add a function in `src/my_awesome_service/calculator.py`:

```python
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
```

2. Add a matching test in `tests/test_calculator.py`:

```python
from my_awesome_service.calculator import add


def test_add() -> None:
    assert add(2, 3) == 5
```

3. Run the test suite:

```shell
uv run poe test
```

The test runner passes and reports 100% coverage.

---

## Plain-English Tool Glossary

Zenith includes several tools that run quietly in the background. Here is what each
tool does for you:

| Tool | What It Does for You | Why It Is Helpful |
| --- | --- | --- |
| **`uv`** | Package & Python Manager | Installs libraries fast and manages Python versions without breaking your computer. |
| **`ruff`** | Code Cleaner & Formatter | Formats code styling and catches syntax bugs in milliseconds. |
| **`pyrefly`** | Type Safety Inspector | Analyzes type hints so you do not accidentally pass incompatible data to functions. |
| **`poe`** | Shortcut Command Runner | Provides easy commands like `uv run poe test` instead of long commands. |
| **`prek`** | Git Commit Guard | Checks your code automatically when you run `git commit` to keep bad code from being saved. |
| **`tach`** | Architecture Protector | Prevents circular imports and keeps modules separated cleanly. |
| **`complexipy`** | Simplicity Checker | Warns you if a function has too many nested loops or branches. |
| **`zensical`** | Documentation Engine | Turns markdown files in `docs/` into a searchable website. |
| **`typos`** | Spell Checker | Catches spelling mistakes in your code and documentation. |

---

## Where to Go Next

Now that you understand the basic workflow:

- Explore [The Tooling Stack](tools/index.md) to learn more about each individual tool.
- Read [The Zenith Philosophy](philosophy.md) for the design principles behind the
  guardrails.
