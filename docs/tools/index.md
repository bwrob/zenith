---
diataxis: reference
purpose: Catalog the integrated developer tooling stack spanning workflow, code quality, testing, security, and documentation.
---

# Zenith Tooling Stack

Zenith replaces fragmented Python tooling with a pre-wired, predominantly Rust-native
toolchain configured through dedicated root files.

## Tool Architecture & Categories

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

## Daily Essentials Vs. Background Guardrails

You do not need to memorize CLI flags for twenty tools. Day-to-day commands go through
`uv` and `poe`, while the remaining tools run automatically inside `uv run poe fix`,
`uv run poe code-quality`, and `prek` Git hooks:

| Tier                             | Tools                                                                                                                  | How You Interact with Them                                      |
| :------------------------------- | :--------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| **Tier 1: Daily Commands**       | **`uv`**, **`poe`**, **`pytest`**, **`ruff`**, **`typer`**, **`zensical`**                                             | `uv add`, `uv run poe test`, `uv run poe fix`, `poe docs-serve` |
| **Tier 2: Automated Guardrails** | **`pyrefly`**, **`tach`**, **`deptry`**, **`complexipy`**, **`griffe`**, **`typos`**, **`zizmor`**, **`mutmut`**, etc. | Executed by `uv run poe code-quality`, `prek`, and CI workflows |

## Why Dedicated Configuration Files?

Although many Python tools support `[tool.*]` tables inside `pyproject.toml`, Zenith
places each tool's configuration in its own root file (`ruff.toml`, `pyrefly.toml`,
`tach.toml`, `complexipy.toml`, `poe_tasks.toml`, `pytest.ini`, `.coveragerc`,
`.taplo.toml`, `prek.toml`, `rumdl.toml`, `typos.toml`, `.zizmor.yml`,
`cosmic-ray.toml`):

- **Keep `pyproject.toml` focused on packaging**: Package metadata, dependencies, and
  PEP 517 build settings stay under 140 lines instead of scrolling past hundreds of
  lines of linter and type-checker rules.
- **Clean Git diffs and blame history**: Changing a Ruff rule or Tach module boundary
  touches only `ruff.toml` or `tach.toml`.
- **Direct editor schema binding**: Language servers (Taplo, YAML, INI) attach each
  tool's schema to its dedicated filename automatically.

> [!TIP]
> **Pruning or Consolidating Tools**: Every tool is decoupled. To remove a tool you do
> not need, delete its entry from `poe_tasks.toml` (`code-quality`), `prek.toml`, and
> `pyproject.toml` (`[dependency-groups]`), delete its config file, and run `uv sync`.
> Conversely, if your team prefers a single `pyproject.toml`, tools like Ruff, Coverage,
> and Taplo can be moved into `[tool.*]` sections.

## Tooling Matrix

| Tool                                | Group                      | Config File                       | Role in Zenith                                                            | Upstream Docs                                                                  |
| :---------------------------------- | :------------------------- | :-------------------------------- | :------------------------------------------------------------------------ | :----------------------------------------------------------------------------- |
| **[uv](uv.md)**                     | Build & Workflow           | `pyproject.toml`, `uv.lock`       | Package manager, virtual environments, lockfiles, and `uv_build` wheels   | [docs.astral.sh/uv](https://docs.astral.sh/uv/)                                |
| **[Poe the Poet](poethepoet.md)**   | Build & Workflow           | `poe_tasks.toml`                  | Hermetic task runner (`uv run poe <task>`)                                | [poethepoet.natn.io](https://poethepoet.natn.io/)                              |
| **[prek](prek.md)**                 | Build & Workflow           | `prek.toml`                       | Rust-native `pre-commit` and `pre-push` Git hook runner                   | [prek.j178.dev](https://prek.j178.dev/)                                        |
| **[Typer](typer.md)**               | Build & Workflow           | `src/<pkg>/cli.py`                | Type-safe CLI framework with Rich terminal output *(when CLI enabled)*    | [typer.tiangolo.com](https://typer.tiangolo.com/)                              |
| **[Cookiecutter](cookiecutter.md)** | Build & Workflow           | `cookiecutter.json`, `hooks/`     | Template engine used by `zenith-template` to scaffold projects            | [cookiecutter.readthedocs.io](https://cookiecutter.readthedocs.io/)            |
| **[Ruff](ruff.md)**                 | Code Quality               | `ruff.toml`                       | Python linter (`select = ["ALL"]`, `preview = true`) and code formatter   | [docs.astral.sh/ruff](https://docs.astral.sh/ruff/)                            |
| **[Pyrefly](pyrefly.md)**           | Code Quality               | `pyrefly.toml`                    | Strict static type checker and 100% type coverage verifier                | [github.com/facebook/pyrefly](https://github.com/facebook/pyrefly)             |
| **[Tach](tach.md)**                 | Code Quality               | `tach.toml`                       | Module layer boundary enforcer and circular import blocker                | [github.com/gauge-sh/tach](https://github.com/gauge-sh/tach)                   |
| **[Deptry](deptry.md)**             | Code Quality               | `pyproject.toml`                  | Checks for missing, unused, and transitive package imports                | [github.com/osprey-oss/deptry](https://github.com/osprey-oss/deptry)           |
| **[complexipy](complexipy.md)**     | Code Quality               | `complexipy.toml`                 | Cognitive complexity analyzer enforcing `<= 10` per function              | [github.com/rohaquinlop/complexipy](https://github.com/rohaquinlop/complexipy) |
| **[Griffe](griffe.md)**             | Code Quality               | `poe_tasks.toml`, `zensical.toml` | Static AST parser for API docs and breaking API change detection          | [mkdocstrings.github.io/griffe](https://mkdocstrings.github.io/griffe/)        |
| **[typos](typos.md)**               | Code Quality               | `typos.toml`                      | Code-aware spell checker for source code and documentation                | [github.com/crate-ci/typos](https://github.com/crate-ci/typos)                 |
| **[pytest](pytest.md)**             | Testing & Security         | `pytest.ini`                      | Test runner with `xdist`, `randomly`, `sugar`, `syrupy`, and `hypothesis` | [docs.pytest.org](https://docs.pytest.org/)                                    |
| **[Coverage.py](coverage.md)**      | Testing & Security         | `.coveragerc`                     | Enforces 100% statement and branch coverage across `src/` and `tests/`    | [coverage.readthedocs.io](https://coverage.readthedocs.io/)                    |
| **[mutmut](mutmut.md)**             | Testing & Security         | `pyproject.toml`                  | Fast AST mutation testing for local TDD loops on macOS and Linux          | [mutmut.readthedocs.io](https://mutmut.readthedocs.io/)                        |
| **[Cosmic Ray](cosmic-ray.md)**     | Testing & Security         | `cosmic-ray.toml`                 | SQLite-backed cross-platform AST mutation testing (Linux, macOS, Windows) | [cosmic-ray.readthedocs.io](https://cosmic-ray.readthedocs.io/)                |
| **[zizmor](zizmor.md)**             | Testing & Security         | `.zizmor.yml`                     | Static security analyzer for `.github/workflows/*.yaml`                   | [woodruffw.github.io/zizmor](https://woodruffw.github.io/zizmor/)              |
| **[Zensical](zensical.md)**         | Documentation & Formatting | `zensical.toml`                   | Static documentation site generator with `mkdocstrings` and `llmstxt`     | [github.com/zensical/zensical](https://github.com/zensical/zensical)           |
| **[rumdl](rumdl.md)**               | Documentation & Formatting | `rumdl.toml`                      | Rust Markdown linter/formatter and embedded Python code block checker     | [github.com/rvben/rumdl](https://github.com/rvben/rumdl)                       |
| **[Taplo](taplo.md)**               | Documentation & Formatting | `.taplo.toml`                     | TOML formatter and schema validator                                       | [taplo.tamasfe.dev](https://taplo.tamasfe.dev/)                                |
| **[Prettier](prettier.md)**         | Documentation & Formatting | `.prettierrc.yaml`, `prek.toml`   | YAML and CSS formatter executed via `prek`                                | [prettier.io](https://prettier.io/)                                            |
| **[Typst](typst.md)**               | Documentation & Formatting | `docs/assets/*.typ`               | Compiles `.typ` vector source files into SVG documentation banners/logos  | [typst.app/docs](https://typst.app/docs/)                                      |
| **[Termynal](termynal.md)**         | Documentation & Formatting | `zensical.toml`                   | Renders `<!-- termynal -->` console fences as animated terminal widgets   | [github.com/ines/termynal](https://github.com/ines/termynal)                   |
