---
diataxis: reference
purpose: Catalog developer tool skills, command syntax runbooks, and configuration mechanics across the Zenith stack.
---

# Tool Skills

Modern developer tools move fast. LLMs are notoriously prone to hallucinating outdated
command flags, inventing non-existent configuration options, or invoking commands
outside the hermetic project environment.

The **`tool-*`** skill suite provides **deterministic execution groundings**. It
gives AI assistants verified CLI syntax, configuration schemas, and step-by-step
runbooks for every compiler, linter, test runner, and utility in the Zenith stack.

Rather than letting models guess how a tool works, Zenith equips them with
verified, version-pinned knowledge.

## Package Management & Task Execution

These tools manage dependencies, repeatable project tasks, and command-line workflows.

### Fast Packaging & Environment Isolation (tool-uv)

**What it is**: The skill governing Astral's high-speed package installer and resolver.

**Why it is in Zenith**: Python dependency management historically suffered from
sluggish resolvers, broken environment isolation, and fragmentation between tools. `uv`
replaces this ecosystem with a single Rust binary that resolves packages in milliseconds
and guarantees reproducible environments via `uv.lock`.

The `tool-uv` skill grounds agents in hermetic execution: running commands via `uv run`,
managing dependency groups (`dev`, `docs`), and performing cross-platform lockfile
updates.

### Hermetic Task Automation (tool-poethepoet)

**What it is**: The runbook for Zenith's declarative task runner, Poe the Poet.

**Why it is in Zenith**: Development teams often rely on ad-hoc shell scripts or
obscure `Makefile` targets that fail across operating systems. Poe the Poet defines
development tasks directly inside `poe_tasks.toml` and runs them strictly within the
isolated `uv` virtual environment.

`tool-poethepoet` teaches agents standard repository tasks—such as `uv run poe test`,
`uv run poe code-quality`, and `uv run poe fix`—as well as argument forwarding and task
composition patterns.

### Rust-Native Git Pre-Commit Hooks (tool-prek)

**What it is**: The skill for running and configuring Git pre-commit lifecycle hooks
using `prek`.

**Why it is in Zenith**: Traditional Python `pre-commit` incurs noticeable startup
latency and requires isolated environments for every hook. `prek` is a fast,
Rust-native drop-in alternative that executes configured checks in parallel with minimal
overhead.

`tool-prek` guides agents through hook installations (`uv run prek install`), manual
workspace audits (`uv run prek run --all-files`), and `prek.toml` configuration syntax.

### Modern Type-Safe CLI Development (tool-typer)

**What it is**: The design guide and syntax reference for building modern command-line
interfaces using Typer and Rich.

**Why it is in Zenith**: Building CLIs with Python standard `argparse` requires
verbose boilerplate. Typer leverages modern Python type hints and PEP 593 `Annotated`
metadata to auto-generate help text, check arguments, and format output with Rich
terminal components.

`tool-typer` ensures agents build CLIs adhering to Zenith typing standards. It uses
lazy subcommand imports for fast startup and provides clean terminal panes.

### Template Instantiation & Scaffolding (tool-cookiecutter)

**What it is**: The skill for maintaining and testing Zenith's Cookiecutter template
engine, variables, and lifecycle hooks.

**Why it is in Zenith**: Zenith is itself a Cookiecutter template. Maintaining
`cookiecutter.json`, conditional file trees, and Jinja templating hooks requires strict
attention to variable scoping and post-generation scripts.

`tool-cookiecutter` provides maintainers and agents with syntax rules for conditional
blocks, prompt definitions (`__prompts__`), and multi-platform rendering tests.

## Code Quality, Static Typing & Architecture

These tools check source style, type correctness, module boundaries, and complexity.

### Unified Linting & Formatting (tool-ruff)

**What it is**: The operational guide for Astral Ruff, the unified Python linter and
code formatter.

**Why it is in Zenith**: In the past, Python projects combined multiple separate
formatters and linters. This caused slow CI builds and conflicting formatting rules.
Ruff replaces dozens of tools with a single Rust engine operating 10-100x faster than
legacy alternatives.

`tool-ruff` guides agents through Zenith's complete rule configuration (including
preview rules and type-checking imports), safe auto-fixing (`ruff check --fix`), and
formatting rules.

### Strict Static Type Checking (tool-pyrefly)

**What it is**: The reference guide for Meta's high-speed Pyrefly static type checker.

**Why it is in Zenith**: Static typing is the bedrock of agentic reliability. When types
are loose or unverified, AI assistants frequently introduce runtime `TypeError` or
`AttributeError` exceptions. Pyrefly provides near-instantaneous feedback, first-class
support for modern PEP 695 generic syntax, and strict structural subtyping.

`tool-pyrefly` teaches agents how to interpret Pyrefly diagnostics, write compliant type
aliases, and enforce 100% strict type coverage across domain packages.

### Modular Architecture & Boundary Enforcement (tool-tach)

**What it is**: The skill for defining and enforcing module layer boundaries with Tach.

**Why it is in Zenith**: As codebases expand, modular boundaries erode into circular
dependencies and improper layer coupling. Tach enforces explicit import rules directly
in AST.

`tool-tach` ensures agents respect defined layer hierarchies, update `tach.toml` when
adding new modules, and resolve circular dependencies using dependency injection or
protocols.

### Cognitive Complexity Ceiling (tool-complexipy)

**What it is**: The runbook for measuring cognitive complexity and refactoring dense
code.

**Why it is in Zenith**: Cyclomatic complexity measures linear code branches. In
contrast, cognitive complexity measures how difficult code is for a human mind and an
LLM to understand. Deeply nested loops and defensive branch conditions are magnets for
bugs.

Zenith sets a strict ceiling:
**no function may exceed a cognitive complexity score of 10**. `tool-complexipy`
provides agents with concrete refactoring recipes (guard clauses, functional extraction,
lookup tables) to reduce complexity scores.

### Public API Change Detection (tool-griffe)

**What it is**: The skill for static AST inspection of Python public API signatures
using Griffe.

**Why it is in Zenith**: Unintended breaking changes in public APIs break downstream
consumers. Griffe parses public docstrings and AST signatures without importing or
executing untrusted code.

In Zenith, `tool-griffe` powers automated API diff audits during Spec-Driven Development
reviews (`uv run poe sdd-check-api`). This ensures every new, modified, or removed
symbol is intentional.

### Source Code & Documentation Spelling Verification (tool-typos)

**What it is**: The guide for source code and documentation spell checking via `typos`.

**Why it is in Zenith**: Typos in code identifiers, configuration keys, or documentation
anchor links degrade project professionalism and cause subtle runtime bugs. `typos` is a
zero-dependency Rust tool that scans codebases in milliseconds with virtually zero false
positives.

`tool-typos` guides agents on running spell checks, maintaining `typos.toml` exclusion
lists for acronyms, and fixing documentation prose.

## Testing, Coverage & Security Assurance

These tools check behavior, coverage, dependency safety, and CI workflows.

### Test Suite Execution (tool-pytest)

**What it is**: The runbook for Zenith's pytest test suite and ecosystem plugins.

**Why it is in Zenith**: High-assurance engineering requires more than simple unit
tests. Zenith's test stack integrates `pytest-xdist` for multi-core parallel execution,
`pytest-randomly` for order-independent test isolation, `syrupy` for snapshot testing,
and `hypothesis` for property-based fuzz testing.

`tool-pytest` grounds agents in writing assertive tests, using fixtures, debugging test
failures, and managing test execution parameters.

### 100% Branch Coverage Enforcement (tool-coverage)

**What it is**: The configuration and enforcement guide for Coverage.py.

**Why it is in Zenith**: Statement coverage is deceptive: a test can execute a line
without testing both branches of an `if` condition. Zenith enforces **100% branch and
statement coverage** (`fail_under = 100`) as a mandatory quality gate.

`tool-coverage` helps agents inspect missed branches (`coverage report -m`), understand
`.coveragerc` exclusion patterns, and write targeted test scenarios to kill uncovered
branches.

### Local AST Mutation Testing (tool-mutmut)

**What it is**: The guide for high-speed AST mutation testing with `mutmut`.

**Why it is in Zenith**: 100% test coverage proves that tests executed the code.
However, it does not prove that assertions test meaningful logic. Mutation testing
modifies your AST (for example, flipping boolean operators) to check if tests fail.

`tool-mutmut` provides a fast mutation loop for local development. Developers and agents
discover surviving mutants and write deeper test assertions.

### Cross-Platform Mutation Testing (tool-cosmic-ray)

**What it is**: The skill for thorough, cross-platform mutation testing with Cosmic Ray.

**Why it is in Zenith**: `mutmut` excels at fast local loops. Cosmic Ray provides
mutation sweeps across all supported platforms, including Windows environments.

`tool-cosmic-ray` teaches agents how to initialize SQLite mutation databases, execute
distributed mutation workers, and analyze survivor summaries.

### GitHub Actions CI/CD Security Audit (tool-zizmor)

**What it is**: The static security analyzer for GitHub Actions workflows.

**Why it is in Zenith**: CI/CD workflows are frequent targets for supply-chain attacks,
script injections, unpinned third-party actions, and excessive token permissions.

`tool-zizmor` audits all `.github/workflows/*.yaml` files in pedantic mode. The audit
ensures workflows follow least-privilege permissions, pin actions to full commit SHAs,
and guard against script execution bugs.

## Documentation, Assets & Formatting

These tools build documentation and keep its source files and visual assets consistent.

### Modern TOML-Based Documentation (tool-zensical)

**What it is**: The operational guide for Zensical, Zenith's modern static documentation
generator.

**Why it is in Zenith**: Developers configure Zensical entirely via TOML
(`zensical.toml`). It features instant live-reloading, automatic `llms.txt` generation,
and clean theme switching.

`tool-zensical` guides agents in serving documentation locally
(`uv run poe docs-serve`), organizing navigation hierarchies, and configuring
`mkdocstrings` for automatic API docs.

### Rust-Native Markdown Linter & Formatter (tool-rumdl)

**What it is**: The skill for formatting and linting documentation with `rumdl`.

**Why it is in Zenith**: Markdown documentation easily drifts into inconsistent heading
styles, broken links, and irregular list formatting. `rumdl` formats markdown at Rust
speeds and features integrated code-block tools that format embedded Python blocks with
Ruff.

`tool-rumdl` guides agents in validating markdown documentation (`uv run poe lint-md`),
formatting prose, and resolving rule diagnostics.

### Declarative TOML Formatting & Linting (tool-taplo)

**What it is**: The formatting and schema validation guide for TOML configuration files.

**Why it is in Zenith**: Zenith organizes configurations into dedicated TOML files
(`pyproject.toml`, `tach.toml`, `zensical.toml`, `poe_tasks.toml`). Without automated
formatting, key-value pairs become disorganized and hard to read.

`tool-taplo` enforces aligned keys, 4-space indentation, and valid schemas across all
TOML manifests via `uv run poe format-check-toml`.

### Consistent YAML & CSS Formatting (tool-prettier)

**What it is**: The formatting guide for GitHub Actions YAML manifests and custom CSS
stylesheets using Prettier.

**Why it is in Zenith**: Ruff and Taplo format Python and TOML. Prettier formats GitHub
Actions YAML workflows and Zensical CSS stylesheets with consistent indentation.

`tool-prettier` formats all YAML and CSS files to prevent noisy Git diffs.

### Vector Logotypes & Asset Generation (tool-typst)

**What it is**: The guide for authoring vector SVG logotypes and diagrams using the
Typst typesetting engine.

**Why it is in Zenith**: Raster images (PNG, JPEG) blur on high-DPI displays and cannot
be edited in code. Typst compiles human-readable code into crisp, responsive vector SVG
assets (such as `docs/assets/python-logo.svg`).

`tool-typst` grounds agents in Typst layout markup, mathematical positioning, and SVG
export workflows.

### Animated Terminal Documentation Widgets (tool-termynal)

**What it is**: The skill for authoring interactive terminal animations in
documentation.

**Why it is in Zenith**: Static CLI output in documentation is dry and unengaging.
Termynal provides lightweight animated terminal widgets that simulate real CLI sessions
with interactive controls and custom progress delays.

`tool-termynal` teaches agents how to wrap shell sessions in `<div class="termy">` tags
with appropriate `data-ty` timing attributes.

## Adding Custom Tool Skills

When your project introduces major third-party libraries, databases, or cloud tools
(such as Docker, FastAPI, Alembic, or Playwright), create a matching `tool-*` skill:

```bash
mkdir -p .agents/skills/tool-docker/{templates,references}
```

Equipping your agents with dedicated tool skills prevents hallucinated flags, guarantees
idiomatic usage, and keeps your entire team operating on verified tool patterns.
