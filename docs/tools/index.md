---
diataxis: reference
purpose: Catalog the integrated developer tooling stack spanning workflow, code quality, testing, security, and documentation.
---

# Zenith Tooling Stack

Zenith replaces fragmented Python tooling with a fast, Rust-based toolchain
configured with automated quality checks.

## Tool Architecture & Categories

The diagram below maps the complete Zenith tool ecosystem across four operational
pillars:

```mermaid
flowchart TB
    subgraph Build["🛠️ Build & Workflow"]
        direction TB
        uv["uv<br/><i>Package Manager & Builds</i>"]
        poe["Poe the Poet<br/><i>Hermetic Task Runner</i>"]
        prek["prek<br/><i>Git Hook Automation</i>"]
        typer["Typer<br/><i>Type-Safe CLI Framework</i>"]
        cc["Cookiecutter<br/><i>Template Scaffolding</i>"]
    end

    subgraph Quality["🛡️ Code Quality & Architecture"]
        direction TB
        ruff["Ruff<br/><i>Linter & Formatter</i>"]
        pyrefly["Pyrefly<br/><i>Strict Type Checker</i>"]
        tach["Tach<br/><i>Boundary Enforcer</i>"]
        deptry["Deptry<br/><i>Dependency Checker</i>"]
        complex["complexipy<br/><i>Complexity Ceiling</i>"]
        griffe["Griffe<br/><i>API Change Detector</i>"]
        typos["typos<br/><i>Source Spell Checker</i>"]
    end

    subgraph Test["🧪 Testing & Security"]
        direction TB
        pytest["pytest<br/><i>Parallel Test Engine</i>"]
        cov["Coverage.py<br/><i>100% Branch Coverage</i>"]
        mutmut["mutmut<br/><i>Fast Local Mutation</i>"]
        cosmic["Cosmic Ray<br/><i>Deep AST Mutation</i>"]
        zizmor["zizmor<br/><i>CI Security Analyzer</i>"]
    end

    subgraph Docs["📚 Documentation & Formatting"]
        direction TB
        zensical["Zensical<br/><i>Fast Docs Generator</i>"]
        rumdl["rumdl<br/><i>Markdown Linter</i>"]
        taplo["Taplo<br/><i>TOML Formatter</i>"]
        prettier["Prettier<br/><i>YAML & CSS Formatter</i>"]
        typst["Typst<br/><i>SVG Layout Engine</i>"]
        termy["Termynal<br/><i>Animated Terminal</i>"]
    end

    click uv "uv/" "Explore uv documentation"
    click poe "poethepoet/" "Explore Poe the Poet documentation"
    click prek "prek/" "Explore prek documentation"
    click typer "typer/" "Explore Typer documentation"
    click cc "cookiecutter/" "Explore Cookiecutter documentation"
    click ruff "ruff/" "Explore Ruff documentation"
    click pyrefly "pyrefly/" "Explore Pyrefly documentation"
    click tach "tach/" "Explore Tach documentation"
    click deptry "deptry/" "Explore Deptry documentation"
    click complex "complexipy/" "Explore complexipy documentation"
    click griffe "griffe/" "Explore Griffe documentation"
    click typos "typos/" "Explore typos documentation"
    click pytest "pytest/" "Explore pytest documentation"
    click cov "coverage/" "Explore Coverage.py documentation"
    click mutmut "mutmut/" "Explore mutmut documentation"
    click cosmic "cosmic-ray/" "Explore Cosmic Ray documentation"
    click zizmor "zizmor/" "Explore zizmor documentation"
    click zensical "zensical/" "Explore Zensical documentation"
    click rumdl "rumdl/" "Explore rumdl documentation"
    click taplo "taplo/" "Explore Taplo documentation"
    click prettier "prettier/" "Explore Prettier documentation"
    click typst "typst/" "Explore Typst documentation"
    click termy "termynal/" "Explore Termynal documentation"
```

Click any tool above to view its technical specifications, architectural rationale in
Zenith, configuration showcases, and upstream references.

## Dedicated Configuration Files

Most modern Python tools support defining configuration inside `pyproject.toml` with
`[tool.*]` tables. Consolidating settings into one file seems convenient. However,
Zenith standardizes on dedicated configuration files for each tool. Examples include
`ruff.toml`, `pyrefly.toml`, `complexipy.toml`, `tach.toml`, `poe_tasks.toml`,
`pytest.ini`, `.coveragerc`, `.taplo.toml`, and `prek.toml`.

- **Focused Code Reviews**: Updating a linter rule, adjusting type checks, or
  revising task scripts creates a clean Git diff in that tool's file. Pull requests
  remain easy to review without noise in the core packaging manifest.
- **Prevents Monolithic File Bloat**: Storing configuration for 15+ developer tools
  in `pyproject.toml` creates a file stretching hundreds of lines. This bloat obscures
  essential package metadata, dependencies, and build specifications.
- **Granular Git Blame & History**: Each tool configuration retains an independent
  commit history. Inspecting `git log ruff.toml` or `git blame tach.toml` surfaces the
  exact context, author, and pull request for architectural decisions over time.
- **Tool-Native Schema Support**: Dedicated files allow language servers and editors
  to attach schemas directly without schema interference.

## Tooling Matrix

| Tool                                | Group                      | Primary Role                                                               | Upstream Documentation                                                         |
| ----------------------------------- | -------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **[uv](uv.md)**                     | Build & Workflow           | Package manager, virtual environments, lockfiles, and PEP 517 builds       | [docs.astral.sh/uv](https://docs.astral.sh/uv/)                                |
| **[Poe the Poet](poethepoet.md)**   | Build & Workflow           | Declarative development task runner integrated with uv                     | [poethepoet.natn.io](https://poethepoet.natn.io/)                              |
| **[prek](prek.md)**                 | Build & Workflow           | Rust Git hook runner and local quality gate automation                     | [prek.j178.dev](https://prek.j178.dev/)                                        |
| **[Typer](typer.md)**               | Build & Workflow           | Type-safe CLI framework with Rich terminal rendering                       | [typer.tiangolo.com](https://typer.tiangolo.com/)                              |
| **[Cookiecutter](cookiecutter.md)** | Build & Workflow           | Project templating engine powering Zenith generation                       | [cookiecutter.readthedocs.io](https://cookiecutter.readthedocs.io/)            |
| **[Ruff](ruff.md)**                 | Code Quality               | Fast Python linter and formatter with preview rules                        | [docs.astral.sh/ruff](https://docs.astral.sh/ruff/)                            |
| **[Pyrefly](pyrefly.md)**           | Code Quality               | Meta's strict type checker and 100% type coverage engine                   | [github.com/facebook/pyrefly](https://github.com/facebook/pyrefly)             |
| **[Tach](tach.md)**                 | Code Quality               | Modular boundary enforcement, circular dependency blocker                  | [github.com/gauge-sh/tach](https://github.com/gauge-sh/tach)                   |
| **[Deptry](deptry.md)**             | Code Quality               | Detect missing, unused, and transitive package dependencies                | [github.com/osprey-oss/deptry](https://github.com/osprey-oss/deptry)           |
| **[complexipy](complexipy.md)**     | Code Quality               | Fast cognitive complexity analyzer enforcing max <= 10                     | [github.com/rohaquinlop/complexipy](https://github.com/rohaquinlop/complexipy) |
| **[Griffe](griffe.md)**             | Code Quality               | Static AST analysis and breaking public API change detector                | [mkdocstrings.github.io/griffe](https://mkdocstrings.github.io/griffe/)        |
| **[typos](typos.md)**               | Code Quality               | High-performance source code and doc spell checker                         | [github.com/crate-ci/typos](https://github.com/crate-ci/typos)                 |
| **[pytest](pytest.md)**             | Testing & Security         | Fixture-based test framework with parallel, property, and snapshot plugins | [docs.pytest.org](https://docs.pytest.org/)                                    |
| **[Coverage.py](coverage.md)**      | Testing & Security         | 100% statement and branch test coverage engine                             | [coverage.readthedocs.io](https://coverage.readthedocs.io/)                    |
| **[mutmut](mutmut.md)**             | Testing & Security         | Fast AST mutation testing for local TDD loops (macOS/Linux)                | [mutmut.readthedocs.io](https://mutmut.readthedocs.io/)                        |
| **[Cosmic Ray](cosmic-ray.md)**     | Testing & Security         | AST mutation testing evaluating test suite assertiveness                   | [cosmic-ray.readthedocs.io](https://cosmic-ray.readthedocs.io/)                |
| **[zizmor](zizmor.md)**             | Testing & Security         | Static security analysis tool for GitHub Actions workflows                 | [woodruffw.github.io/zizmor](https://woodruffw.github.io/zizmor/)              |
| **[Zensical](zensical.md)**         | Documentation & Formatting | Fast TOML-based static documentation generator                             | [github.com/zensical/zensical](https://github.com/zensical/zensical)           |
| **[rumdl](rumdl.md)**               | Documentation & Formatting | Rust-native Markdown linter and embedded code checker                      | [github.com/rvben/rumdl](https://github.com/rvben/rumdl)                       |
| **[Taplo](taplo.md)**               | Documentation & Formatting | Consistent TOML formatting and schema validation                           | [taplo.tamasfe.dev](https://taplo.tamasfe.dev/)                                |
| **[Prettier](prettier.md)**         | Documentation & Formatting | Opinionated formatter for YAML workflows and CSS stylesheets               | [prettier.io](https://prettier.io/)                                            |
| **[Typst](typst.md)**               | Documentation & Formatting | Markup-based layout engine for compiling SVG documentation assets          | [typst.app/docs](https://typst.app/docs/)                                      |
| **[Termynal](termynal.md)**         | Documentation & Formatting | Lightweight terminal animation widget for documentation                    | [github.com/ines/termynal](https://github.com/ines/termynal)                   |
