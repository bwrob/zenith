---
diataxis: tutorial
purpose: Teach newcomers modern Python concepts, tooling rationale, and end-to-end scaffolding workflows from commit zero.
---

# First Steps & Core Concepts

Zenith is a **project starter generator** (powered by Cookiecutter), not a runtime
library that you `import zenith` into your code. Running the generator creates a
standalone Python repository on your machine with directory layouts, test runners, and
static checks already wired up.

This tutorial walks through installing `uv`, generating your first project, running the
CLI and test suite, and fixing common quality gate errors.

## Step 0: Install Uv

Zenith projects use **[uv](tools/uv.md)** to manage Python interpreters, virtual
environments, and packages. Before generating a project, install `uv`:

=== "macOS & Linux"

    ```shell
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

> [!TIP]
> **You do not need to install Python or Rust manually.** `uv` downloads and manages
> the requested Python version automatically, and every Rust-based tool in Zenith ships
> as a pre-compiled binary wheel.

## Your First 5 Minutes: Zero to Running Code

Follow these four steps to generate a project and run its first commands.

### 1. Scaffold Your Project

Launch the interactive **Zenith Project Initializer** wizard with `uvx` (which runs CLI
tools in an ephemeral environment without global installation):

```shell
uvx zenith-template
```

The two-screen terminal wizard prompts for project metadata, optional features,
post-generation hooks, and AI assistant integrations:

| Screen / Field            | Meaning & Purpose                                                                                                                 | Default Value                    |
| :------------------------ | :-------------------------------------------------------------------------------------------------------------------------------- | :------------------------------- |
| **Root Directory**        | Parent directory where the project folder is created                                                                              | Current working directory (`.`)  |
| **Project Name**          | Human-readable title of your project                                                                                              | `My Project`                     |
| **Project Slug**          | Directory and distribution package name                                                                                           | Auto-derived (`my-project`)      |
| **Python Package Name**   | Import identifier in `src/`                                                                                                       | Auto-derived (`my_project`)      |
| **Short Description**     | Summary for `README.md` and `pyproject.toml`                                                                                      | `A modern Python project.`       |
| **Author Name / Email**   | Packaging metadata (auto-detected from `git config`)                                                                              | Git `user.name` and `user.email` |
| **GitHub Username**       | GitHub user or organization handle                                                                                                | `author`                         |
| **Target Python Version** | Minimum Python runtime (`3.12`–`3.15`)                                                                                            | `3.12`                           |
| **Open Source License**   | License file and metadata (`MIT`, `Apache-2.0`, etc.)                                                                             | `MIT`                            |
| **Core Features**         | Toggle CLI (`--no-cli`), Docs (`--no-docs`), Mutation testing (`--no-mutation`), CI (`--no-ci`), and Agent Skills (`--no-skills`) | All enabled (`true`)             |
| **Setup & Automation**    | Toggle `git init` (`--no-git`), `uv sync` (`--sync`), and `prek install` (`--hooks`)                                              | `git init` enabled (`true`)      |
| **AI Assistant Presets**  | Multi-select checkbox list with presets (`recommended`, `all`, `ide-only`, `cli-only`, `none`)                                    | `recommended`                    |

For non-interactive scripting or CI usage, pass `--no-input` (every wizard run also
prints the exact CLI command to reproduce your selections):

```shell
uvx zenith-template --no-input --name "My Project" --ai-tools recommended --sync
```

You can also render the template directly via Cookiecutter
(`uvx cookiecutter https://github.com/bwrob/zenith.git`).

> [!NOTE]
> **AI Tooling Is Elective**: If you prefer a repository without AI agent configs, set
> `ai_tools` to `none` and `include_agent_skills` to `false` (or pass
> `--ai-tools none --no-skills`). The generator strips all agent instruction files,
> `.agents/` skills, and tool dot-directories while keeping the Python toolchain and
> quality gates intact.

### 2. Enter and Sync Your Project

Move into the generated folder and synchronize its virtual environment:

```shell
cd my-project
uv sync
```

`uv sync` creates a local `.venv/` directory and installs all locked dependencies from
`uv.lock`.

### 3. Run Your Application

When scaffolded with `include_cli` enabled (the default), your project includes a
working Typer CLI:

```console
$ uv run my-project --help
Usage: my-project [OPTIONS] COMMAND [ARGS]...

  A modern Python project.

Options:
  -v, --version  Show version and exit.
  --help         Show this message and exit.

Commands:
  greet  Display a personalized greeting.
```

Run the `greet` command:

```console
$ uv run my-project greet "Developer"
✨ Hello, Developer!
```

### 4. Preview Live Documentation

Start the local **[Zensical](tools/zensical.md)** documentation server:

```console
$ uv run poe docs-serve
Serving documentation at http://127.0.0.1:8000
```

Open `http://127.0.0.1:8000` in your browser. Edits to Markdown files in `docs/` reload
automatically.

## Project Layout & Everyday Workflows

Your day-to-day work happens inside `src/`, `tests/`, and `docs/`, while the `.toml`
files in the repository root configure the background toolchain:

```tree
my-project/
    src/my_project/     # Application source code
    tests/              # Unit and property-based test suite
    docs/               # Markdown documentation and ADRs
    pyproject.toml      # Package metadata and dependencies
    poe_tasks.toml      # Task runner shortcuts (uv run poe <task>)
    ruff.toml           # Linter and formatter configuration
    pyrefly.toml        # Static type checker configuration
    tach.toml           # Module layer boundary rules
```

### How the CLI Entry Point Is Wired

When `include_cli` is enabled, `pyproject.toml` registers a console script under
`[project.scripts]`:

```toml
[project.scripts]
my-project = "my_project.__main__:main"
```

Running `uv run my-project` calls `main()` in `src/my_project/__main__.py`, which
dispatches to the Typer `app` defined in `src/my_project/cli.py`.

### Translating Classic Python Commands to Zenith

| Classic Command                   | Zenith Equivalent                 | Why                                                                                      |
| :-------------------------------- | :-------------------------------- | :--------------------------------------------------------------------------------------- |
| `pip install <pkg>`               | `uv add <pkg>`                    | Installs the package into `.venv` and records the version constraint in `pyproject.toml` |
| `pip install -r requirements.txt` | `uv sync`                         | Installs exact pinned wheels and hashes from `uv.lock`                                   |
| `source .venv/bin/activate`       | `uv run <command>`                | Runs commands inside `.venv` without manual shell activation                             |
| `python script.py`                | `uv run python -m my_project.cli` | Executes with `src/` on `sys.path` inside the project environment                        |
| `pytest`                          | `uv run poe test`                 | Runs `pytest` with 100% statement and branch coverage enforcement                        |
| Manual linter / formatter runs    | `uv run poe fix`                  | Formats Python, TOML, Markdown, YAML, and CSS and auto-fixes lint issues                 |
| Pre-PR static checks              | `uv run poe code-quality`         | Runs Ruff, Taplo, Prettier, rumdl, typos, Pyrefly, complexipy, zizmor, Tach, and Deptry  |

### Connecting Your Editor

If your editor highlights imports like `import typer` as unresolved, point it at the
project's `.venv` interpreter:

=== "VS Code & Cursor"

    1. Open the Command Palette (`Cmd+Shift+P` on macOS, `Ctrl+Shift+P` on Linux/Windows).
    2. Run **Python: Select Interpreter**.
    3. Select `./.venv/bin/python` (or `.\.venv\Scripts\python.exe` on Windows).

=== "PyCharm"

    1. Open **Settings** -> **Project** -> **Python Interpreter**.
    2. Click **Add Interpreter** -> **Add Local Interpreter**.
    3. Choose **Existing Environment** and select `./.venv/bin/python` (or `.\.venv\Scripts\python.exe`).

## Working with Quality Gates

Zenith projects enforce test coverage, complexity limits, and static types on every
run.

### 100% Statement and Branch Coverage

`uv run poe test` enforces **100% statement and branch coverage** across `src/` and
`tests/`. If you add a function without tests, coverage reports the exact missed lines.

**1. Add an untested function** in `src/my_project/calculator.py`:

```python
from __future__ import annotations


def divide(a: int, b: int) -> int:
    """Divide *a* by *b* using integer division."""
    if b == 0:
        msg = "Cannot divide by zero"
        raise ValueError(msg)
    return a // b
```

**2. Run `uv run poe test`**:

If your test only checks `divide(10, 2)`, lines 7–8 (`if b == 0`) are never executed
and Coverage.py flags both missed statements and a partial branch (`BrPart`).

**3. Cover both branches** in `tests/test_calculator.py`:

```python
from __future__ import annotations

import pytest
from my_project.calculator import divide


def test_divide_success() -> None:
    assert divide(10, 2) == 5


def test_divide_zero_raises() -> None:
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
```

Re-running `uv run poe test` now reaches 100% statement and branch coverage.

### Running a Single Test During Development

Because `uv run poe test` checks coverage across the entire package, running it against
a single test file while drafting code will fail coverage on untouched modules. Run
`pytest` directly while iterating, then run `uv run poe test` when ready:

```shell
# Run one test file without failing on global coverage
uv run pytest tests/test_calculator.py --no-cov

# Run a single test function by name
uv run pytest tests/test_calculator.py -k test_divide_zero_raises --no-cov

# Drop into the Python debugger (pdb) on failure
uv run pytest tests/test_calculator.py --pdb
```

### Cognitive Complexity Limit

**[complexipy](tools/complexipy.md)** scores how deeply nested a function's control flow
is (`if`, `for`, `while`, `try/except`). When a function exceeds a score of **10**,
extract nested blocks into small helper functions or replace conditional chains with
early returns.

### Troubleshooting Quality Gate Failures

When `uv run poe code-quality` or `prek` flags an issue, use these steps to resolve it:

#### 1. Formatting or Lint Errors (Ruff, Taplo, Rumdl, Prettier)

- **Symptom**: `uv run poe code-quality` reports unformatted files, unsorted imports, or
  lint violations.
- **Root Cause**: Files were edited without running the project formatters.
- **Resolution**: Run `uv run poe fix` to format all code, configuration, and Markdown
  files in place.

#### 2. Static Type Errors or Missing Coverage (Pyrefly)

- **Symptom**: `pyrefly check` reports `Expected int, got str | None`, or
  `pyrefly coverage` reports untyped symbols.
- **Root Cause**: A variable can be `None` at runtime without a narrowing check, or a
  parameter/return/module attribute lacks an explicit type annotation.
- **Resolution**: Narrow optional values before use (`if value is None: raise ...`) and
  add explicit type annotations instead of `Any`.

#### 3. Git Hook Rejects a Commit or Push (Prek)

- **Symptom**: `git commit` or `git push` exits non-zero and prints `Failed` on a hook.
- **Root Cause**: Staged files violate a `pre-commit` formatter/linter check, or the
  branch fails a `pre-push` check (`pyrefly`, `complexipy`, `tach`).
- **Resolution**:
  1. Run `uv run poe fix` to auto-format files.
  2. Re-read any modified files, stage them (`git add <file>`), and re-run `git commit`.

## Where to Go Next

- Browse the **[Tooling Stack](tools/index.md)** for configuration details and CLI
  commands for every tool in Zenith.
- Read the **[Zenith Philosophy](philosophy.md)** for the trade-offs behind strict
  guardrails and brownfield adoption strategies.
- See **[CI/CD Actions](ci-actions.md)** for the GitHub Actions workflows and PyPI
  Trusted Publishing setup.
