# Zenith

<p align="center">
  <img src="assets/zenith-star.svg" alt="Zenith Emblem" width="140">
</p>

<p align="center" style="font-size: 1.15rem; font-weight: 500;">
  An opinionated template for modern Python projects.
</p>

---

## Quick Start

Scaffold a production-grade repository in seconds using `uvx`:

<div class="termy">

```console
$ uvx cookiecutter https://github.com/bwrob/zenith.git

// Answer configuration prompts
project_name [Zenith]: My Awesome Service
project_slug [my-awesome-service]:
package_name [my_awesome_service]:
description [An opinionated, strict Python project]: High performance analytics engine
author_name [bwrob]: Jane Developer
author_email [contact@bwrob.dev]: jane@example.com
github_username [bwrob]: janedev
version [0.1.0]: 0.1.0
Target Python Version: 3.13
Select Open Source License: MIT
Scaffold Typer/Rich command-line interface? [True]: True
Generate GitHub Actions workflows for CI testing and code quality? [True]: True
Generate GitHub Actions workflow for PyPI Trusted Publishing and documentation deployment? [True]: True

// Initialize and verify newly generated project
$ cd my-awesome-service
$ uv sync
$ uv run poe test
100% test coverage reached (statements and branches).
$ uv run poe code-quality
All quality gates passed!
$ uv run poe docs-serve
Serving documentation at http://127.0.0.1:8000
```

</div>

---

## The Zenith Philosophy

Zenith eliminates **scaffolding debt** and **quality decay**. Instead of spending days
configuring linters, type checkers, and test harnesses—or fighting architectural drift
down the road—Zenith establishes a non-negotiable standard of excellence from commit
zero across four foundational pillars:

<div class="grid cards" markdown>

-   **Modern Rust-Native Tooling**

    ---

    Sub-second developer loops powered by **[uv](tools/uv.md)**,
    **[Ruff](tools/ruff.md)**, **[Pyrefly](tools/pyrefly.md)**,
    **[Tach](tools/tach.md)**, **[complexipy](tools/complexipy.md)**, and
    **[Zensical](tools/zensical.md)**. All tasks run through
    **[Poe the Poet](tools/poethepoet.md)** for identical local and CI execution.

-   **First-Class AI Agent Readiness**

    ---

    Built for autonomous pair-programming with Claude Code, Gemini CLI, Antigravity, and
    Codex. Canonical `AGENTS.md` context, modular skills in
    [`.agents/skills/`](skills/index.md), transparent review standards, and automated
    `llms.txt`.

-   **Ruthless Quality Guardrails**

    ---

    Zero compromises: **100% mandatory test coverage** (`fail_under = 100`), strict
    static typing with Pyrefly, cognitive complexity <= 10 per function, module boundary
    enforcement, and CI security auditing with **[zizmor](tools/zizmor.md)**.

-   **Hermetic Delivery & CI/CD**

    ---

    Zero-drift automation: multi-version matrix testing across Python 3.12–3.15,
    isolated wheel package smoke tests, automated documentation publishing, and PyPI
    Trusted Publishing with supply-chain safeguards.

</div>

> [!IMPORTANT]
> **Built for Long-Term Production, Not Throwaway Scripts**
>
> Zenith is engineered for **production libraries, services, and frameworks** intended
> to be maintained over years by teams of humans and AI agents.
>
> **Zenith is probably not suited for:**
>
> - Quick two-script throwaway automations or web scrapers.
> - 24-hour hackathon prototypes where dirty hacks precede design.
> - Beginners learning fundamental Python syntax for the first time.
>
> If you only need a single script, use `uv run script.py`. When your codebase must
> remain robust, typed, and tested across hundreds of commits, Zenith is your
> foundation.
>
> [Read the full philosophy & project sizing rubric →](philosophy.md)

---

## Project Structure

Every project scaffolded from Zenith matches the production architecture of the
**[zenith-example](https://github.com/bwrob/zenith-example)** showcase repository:

```tree
zenith-example/
    pyproject.toml              # Dependencies & tool configurations (PEP 621)
    poe_tasks.toml              # Unified Poe task runner definitions
    AGENTS.md                   # Canonical AI agent instructions & boundaries
    AI_POLICY.md                # AI contribution standards & verification rules
    zensical.toml               # Fast documentation site configuration
    ruff.toml                   # Ruff linting & formatting settings
    pyrefly.toml                # Pyrefly strict static typing configuration
    complexipy.toml             # Cognitive complexity ceiling (complexity <= 10)
    tach.toml                   # Modular architectural boundary rules
    .agents/skills/             # Modular agent skills
        workflow-*/             # Lifecycle workflows (git, code reviews, changelogs)
        tool-*/                 # Tool-specific guides (uv, ruff, pytest, etc.)
        guide-*/                # Style & language guides (guide-python, guide-ste100)
        domain-*/               # (Reserved for your domain-specific skills)
    src/zenith_example/         # Production package source
        __init__.py             # Public package exports
        cli.py                  # Optional Typer + Rich command-line interface
        py.typed                # PEP 561 typing marker
    tests/                      # Comprehensive test suite with 100% coverage gate
        test_cli.py
    docs/                       # Markdown documentation site with live preview
```

> [!TIP]
> **Explore the Live Showcase Repository**
>
> Browse the real instantiated code, commit history, and GitHub Actions CI runs in
> **[bwrob/zenith-example on GitHub](https://github.com/bwrob/zenith-example)**.

---

## Documentation Guide

<div class="grid cards" markdown>

-   **[Philosophy & Sizing](philosophy.md)**

    ---

    In-depth rationale, tool comparisons against legacy stacks, and sizing rubric.

-   **[Tooling Stack](tools/index.md)**

    ---

    Comprehensive guides for the integrated tool stack, including Typer CLI, uv, and
    Pyrefly.

-   **[Agent Skills](skills/index.md)**

    ---

    Four-prefix taxonomy (`workflow-*`, `tool-*`, `guide-*`, `domain-*`) for AI agents.

-   **[CI/CD Pipelines](ci-actions.md)**

    ---

    GitHub Actions matrix builds, wheel smoke testing, and security scanning.

</div>

Review the version history and release notes in the **[Changelog](changelog.md)**.
