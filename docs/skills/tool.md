# Tools

The **`tool-*`** skill group provides autonomous AI coding agents with verified syntax, concrete CLI flags, configuration specifications, and operational runbooks for specific external developer tools, compilers, formatters, and libraries.

---

## Why AI Agents Need Tool Skills

While modern LLMs have general knowledge of popular Python libraries, they frequently hallucinate non-existent flags, use obsolete configuration syntax, or guess incorrect subcommands when working on modern tooling stacks.

`tool-*` skills act as **deterministic execution groundings**:
- They provide the exact syntax used in the current version of the tool.
- They show concrete `uv run poe <task>` invocations.
- They document configuration files (`*.toml`, `*.yaml`) and specific rule overrides.
- They include troubleshooting steps for common edge cases.

---

## Catalog of Template Tool Skills

| Skill | Target Tool | Core Purpose & Agent Guidance |
|---|---|---|
| **`tool-uv`** | [uv](../tools/uv.md) | Package management, virtual environment isolation, lockfile synchronization, and PEP 517 builds. |
| **`tool-ruff`** | [Ruff](../tools/ruff.md) | High-speed linting, code formatting, docstring compliance, and safe auto-fixing with preview rules (`ALL`). |
| **`tool-pyrefly`** | [Pyrefly](../tools/pyrefly.md) | Meta's strict static type checker, PEP 695 type parameter syntax, and structural Protocol verification. |
| **`tool-complexipy`** | [complexipy](../tools/complexipy.md) | Cognitive complexity measurement, ceiling enforcement (max <= 10), and refactoring recipes. |
| **`tool-tach`** | [Tach](../tools/tach.md) | Modular architectural boundary enforcement, circular dependency elimination, and external dependency validation. |
| **`tool-griffe`** | [Griffe](../tools/griffe.md) | Static AST analysis, docstring signature inspection, and breaking public API change detection. |
| **`tool-poethepoet`** | [Poe the Poet](../tools/poethepoet.md) | Declarative task automation, hermetic subprocesses, task composition, and argument forwarding. |
| **`tool-zensical`** | [Zensical](../tools/zensical.md) | TOML-based documentation, live watchdog server (`zensical serve`), MathJax LaTeX, and `llms.txt` generation. |
| **`tool-rumdl`** | [rumdl](../tools/rumdl.md) | Rust-native Markdown linting, formatting, and embedded Python code block verification. |
| **`tool-typos`** | [typos](../tools/typos.md) | Blazing-fast source code, docstring, and documentation spell checking with automated fixing. |
| **`tool-pytest`** | [pytest](../tools/pytest.md) | Fixture-based test framework, parallel execution, random order shuffling, snapshots, and property testing. |
| **`tool-coverage`** | [Coverage.py](../tools/coverage.md) | 100% statement and branch coverage enforcement, missed line inspection, and `.coveragerc` configuration. |
| **`tool-mutmut`** | [mutmut](../tools/mutmut.md) | Fast AST mutation testing for local developer TDD loops and surviving mutant inspection on macOS and Linux. |
| **`tool-cosmic-ray`** | [Cosmic Ray](../tools/cosmic-ray.md) | Cross-platform AST mutation testing evaluating test suite assertiveness and detecting survivor mutants. |
| **`tool-prettier`** | [Prettier](../tools/prettier.md) | Consistent 4-space formatting across GitHub Actions YAML workflows and custom CSS stylesheets. |
| **`tool-taplo`** | [Taplo](../tools/taplo.md) | TOML toolkit, formatter, and schema validation with aligned key-values and 4-space indentation. |
| **`tool-zizmor`** | [zizmor](../tools/zizmor.md) | Static security analysis auditing GitHub Actions workflows for script injection and excessive permissions. |
| **`tool-termynal`** | [Termynal](../tools/termynal.md) | Lightweight animated terminal widget for documentation pages wrapped in `<div class="termy">`. |
| **`tool-typer`** | [Typer](../tools/typer.md) | Modern type-safe command-line interfaces with PEP 593 `Annotated` parameters and Rich formatting. |
| **`tool-cookiecutter`** | [Cookiecutter](../tools/cookiecutter.md) | Template generation engine, prompt matrices in `cookiecutter.json`, and lifecycle hooks. |
| **`tool-typst`** | [Typst](../tools/typst.md) | Markup-based layout engine for compiling vector SVG logotypes from plain text `.typ` source files. |

---

## Custom Tool Skills

When your project adds major external dependencies or infrastructure tools, create matching `tool-*` skills so AI agents understand how to use them correctly:

```bash
mkdir -p .agents/skills/tool-docker
```

Common tool skills added to Zenith projects:
- **`tool-docker`**: Multi-stage Dockerfile patterns, buildx caches, and non-root container user hygiene.
- **`tool-fastapi`**: Pydantic v2 schemas, dependency injection, and OpenAPI response documentation.
- **`tool-alembic`**: Database migration generation, revision branches, and autocommit transactions.
- **`tool-playwright`**: End-to-end browser testing, locators, and headless CI verification.
- **`tool-kubernetes`**: Helm chart templates, pod resource limits, and probe definitions.
