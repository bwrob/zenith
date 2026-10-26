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
  computer with standard directory layouts, automated test runners, and code checkers
  already wired up.

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
> manages the correct Python version for your project. Furthermore, while several Zenith
> tools are written in Rust for performance, you do **not** need to install Rust or
> Cargo—everything runs as pre-compiled packages managed by `uv`.

## Your First 5 Minutes: Zero to Running Code

Follow these steps to create a project and run its first commands.

### 1. Scaffold Your Project

Run Cookiecutter directly through `uvx` (which runs tools without permanent
installation):

```shell
uvx cookiecutter https://github.com/bwrob/zenith.git
```

Cookiecutter will prompt you for a few project settings:

| Prompt                  | Meaning & Purpose                                      | Recommended Choice / Default       |
| :---------------------- | :----------------------------------------------------- | :--------------------------------- |
| `project_name`          | Human-readable title of your project                   | `My Awesome Service`               |
| `project_slug`          | Directory and distribution package name                | `my_awesome_service`               |
| `package_name`          | Import identifier in `src/`                            | Auto-derived from `project_slug`   |
| `description`           | Short summary for README & package metadata            | Press `Enter` to customize         |
| `author_name` / `email` | Your details for packaging metadata                    | Your name and email                |
| `github_username`       | GitHub user or organization name                       | Your GitHub handle                 |
| `python_version`        | Target Python runtime                                  | `3.13` (current stable)            |
| `license`               | Open-source or proprietary license                     | `MIT`, `Apache-2.0`, `None`        |
| `include_cli`           | Scaffold a ready-to-run Typer command-line application | `true` (recommended for CLIs/apps) |
| `include_ci_testing`    | Generate GitHub Actions CI test & quality workflows    | `true`                             |
| `include_ci_publishing` | Generate GitHub Actions PyPI & docs deploy workflow    | `true`                             |
| `include_agent_skills`  | Include Zenith agent skills suite and SDD subagents    | `true` (or `false` for pure-human) |
| `ai_tools`              | AI assistant configs to scaffold (presets or custom)   | `all`, `recommended`, or `none`    |

> [!NOTE]
> **AI Tooling Is 100% Elective**
>
> Zenith does not force AI tooling onto your repository. If you develop without AI
> assistants or prefer a traditional Python project, set `ai_tools` to `none` and
> `include_agent_skills` to `false`. The generator completely removes all agent
> configuration files, skills, and context symlinks.
>
> The strict quality gates (100% test coverage, strict typing, complexity limits) remain
> identical—accelerating human developers just as effectively as autonomous agents.

If you are unsure about any prompt, simply press `Enter` to accept the default. You can
adjust these settings at any time in `pyproject.toml`.

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
> **The "Engine Room" Rule: Zero Configuration by Default, Full Control When Needed**
> The files ending in `.toml` in the project root are pre-configured guardrails. For
> everyday feature development, you do not need to edit or configure them—they work out
> of the box like a pre-tuned engine. When senior engineers or platform teams need to
> customize linting rules, type boundaries, or tasks, every setting lives in an
> explicit, decoupled file rather than an opaque global environment.

### How Does the Project CLI Script Work?

When you scaffold a project with `include_cli: true`, Cookiecutter registers a
command-line script in `pyproject.toml` under `[project.scripts]`:

```toml
[project.scripts]
my-awesome-service = "my_awesome_service.cli:app"
```

This tells `uv` to look inside `src/my_awesome_service/cli.py` and run the Typer `app`
function whenever you invoke `uv run my-awesome-service`. If you build new modules or
functions in `src/my_awesome_service/`, you can call them from `cli.py` or import them
into other modules.

### The Quick Translation Guide: from Tutorial Python to Zenith

If you learned Python through courses or tutorials, you likely used traditional tools.
Here is how your existing habits translate directly into Zenith:

| Traditional Pattern               | Zenith Modern Pattern         | Why Zenith Uses It                                                                                                                   |
| :-------------------------------- | :---------------------------- | :----------------------------------------------------------------------------------------------------------------------------------- |
| `pip install <package>`           | `uv add <package>`            | `uv add` installs packages in milliseconds and records them in `pyproject.toml`.                                                     |
| `pip install -r requirements.txt` | `uv sync`                     | `uv sync` reads `uv.lock` for 100% deterministic, reproducible environments.                                                         |
| `source .venv/bin/activate`       | `uv run <command>`            | `uv run` executes within `.venv` automatically without manual activation (though `.venv` remains there if you prefer activating it). |
| `python script.py`                | `uv run python -m pkg.module` | Prevents import resolution errors and ensures `src/` is correctly mapped on `sys.path`.                                              |
| `pytest`                          | `uv run poe test`             | Executes pytest with parallel multi-core execution (`-n auto`), 100% coverage gating, and zero-warning tolerance.                    |

### Connecting Your Editor or IDE

When you open a scaffolded project in an editor (such as VS Code, Cursor, or PyCharm),
the editor may default to your system Python. This causes false red or yellow squiggly
lines under imports like `import typer`.

To connect your editor to the project virtual environment:

=== "VS Code & Cursor"

```text
1. Open the Command Palette using `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux).
2. Type and select **Python: Select Interpreter**.
3. Choose the interpreter located in your project directory: `./.venv/bin/python`
   (or `.\.venv\Scripts\python.exe` on Windows).
```

=== "PyCharm"

```text
1. Open **Settings** (or **Preferences** on macOS) and navigate to **Project > Python Interpreter**.
2. Click **Add Interpreter** and choose **Add Local Interpreter**.
3. Select **Existing Environment** and browse to `./.venv/bin/python` (or `.\.venv\Scripts\python.exe`).
```

Once connected, your editor will auto-complete functions, resolve all imports, and
provide instant type feedback while you write code.

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
- `uv run poe fix`: Automatically formats your code and fixes style issues.
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

The gate turns green, confirming that all statements and branches are tested.

### What About Branch Coverage and Missing Branches?

Zenith measures both **line coverage** and **branch coverage** (`branch = true`). A
branch occurs whenever code makes a decision (`if/else`, `try/except`, `while`).

For example, imagine you write an integer division function:

```python
def divide(a: int, b: int) -> int:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a // b
```

If your test only calls `divide(10, 2)`, line 3 is never executed, and `coverage`
flags a `BrPart 1 Missing` violation. Even if you don't miss lines, failing to test both
sides of a conditional path fails the build.

To satisfy the branch coverage gate, test the exception path using `pytest.raises`:

```python
import pytest
from my_awesome_service.calculator import divide


def test_divide_success() -> None:
    assert divide(10, 2) == 5


def test_divide_zero_raises() -> None:
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
```

### What Does "Cognitive Complexity <= 10" Mean?

`complexipy` checks how difficult a function is for human working memory to read and
maintain. Unlike raw line counts, cognitive complexity measures nested logic: `for`
loops inside `if` statements inside `while` blocks increment the complexity score.

**The Fix**: When a function exceeds a score of 10, simply extract the inner loop or
conditional body into a small, descriptive helper function. This keeps functions
bite-sized, easy to read, and painless to unit test.

### How to Run and Debug an Individual Test

`uv run poe test` enforces 100% statement and branch coverage across the **entire**
codebase. When you are drafting a new feature, running whole-suite coverage on a single
test file will fail because untouched files are also measured.

During active development, run individual tests directly through `pytest`:

```shell
# Run a specific test file
uv run pytest tests/test_calculator.py

# Run a specific test by function name
uv run pytest tests/test_calculator.py -k test_divide_zero_raises

# Drop into the interactive Python debugger (PDB) on failure
uv run pytest tests/test_calculator.py --pdb
```

You can also place `breakpoint()` anywhere in your code or tests to pause execution and
inspect variables interactively. Once your isolated test passes, run `uv run poe test`
to verify project-wide coverage before committing.

### When Quality Gates Fail: Troubleshooting Triads

When `uv run poe code-quality` or `prek` flags an issue, follow these steps:

#### 1. Formatting or Style Errors (Ruff)

- **Symptom**: `ruff:check` or `ruff:format` reports missing whitespace, unused imports,
  or formatting violations.
- **Root Cause**: Code was written or edited without running the automated formatter.
- **Resolution**: Run `uv run poe fix`. Poe formats code and auto-fixes auto-resolvable
  lint rules immediately.

#### 2. Static Type Violations (Pyrefly)

- **Symptom**: `pyrefly check` reports `Expected int, got str | None`.
- **Root Cause**: A function receives or returns an optional value that may be `None` at
  runtime.
- **Resolution**: Add an explicit check before using the variable:

  ```python
  value: str | None = None
  if value is None:
      raise ValueError("Value cannot be None")
  ```

  Avoid using `# type: ignore` or untyped `Any`—explicit guards preserve runtime safety
  and satisfy the type checker.

#### 3. Pre-Commit Hook Blocks Your Commit (Prek)

- **Symptom**: Running `git commit -m "..."` stops and prints `Failed` on a hook.
- **Root Cause**: Code in your staging area violates a linting, formatting, or security
  rule.
- **Resolution**: Your code is **completely safe**—Git hooks never delete or lose your
  edits.
  1. Inspect the terminal output to see which hook failed.
  2. Run `uv run poe fix` to resolve formatting and linting.
  3. Re-stage the modified files (`git add <file>`) and run `git commit` again.

## Step-by-Step Recap: What Just Happened

Here is the mental model to remember as you build:

1. **`uv` is your engine**: It manages your Python versions and packages inside an
   isolated sandbox. You never need to worry about broken system Python installs.
2. **Your code lives in `src/`**: Focus your energy on `src/` and `tests/`. The `.toml`
   files in the root directory are background guardrails that stay out of your way.
3. **`uv add` is your `pip install`**: When you need a library, type `uv add <package>`.
4. **`uv run poe ...` are your project controls**: Run `poe test` to verify your code,
   `poe fix` to auto-format, and `poe code-quality` to check types and boundaries.
5. **Red tests are safety nets**: When a quality gate flags an error, it is pointing out
   an un-tested branch or type mismatch before code reaches production.

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
