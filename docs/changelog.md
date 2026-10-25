---
diataxis: reference
purpose: Record historical releases, breaking changes, and user-facing modifications across versions following Keep a Changelog.
---

# Changelog

All notable changes to the **Zenith** project will be documented in this file.

The format is based on [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New `workflow-docs-authoring` agent skill enforcing human-first technical writing,
  Documentation-Driven Design, the golden source of truth rule ("do not repeat, link"),
  and tested snippet transclusion in CI, alongside progressive disclosure, editor
  ergonomics, the Diátaxis architecture, and Troubleshooting Triads.
- Standardized non-renderable Diátaxis YAML frontmatter preambles across all
  documentation pages in the repository and template.
- Dedicated Zenith documentation website configured with Zensical, Catppuccin hue-based
  theming, MathJax, and Termynal terminal animations.
- Tooling guides for all 22 integrated tools.
- Detailed agent skill architecture guides for lifecycle workflows in `.agents/skills/`.
- Deep-dive philosophy guide outlining Modern Rust Tooling, AI-Ready Engineering,
  Ruthless Guardrails, and Project Sizing.
- GitHub Pages automated deployment workflow (`.github/workflows/docs.yaml`).

## [0.1.0] - 2026-10-18

### Added

- **Modern Rust Toolchain**:
  - Full integration of **uv** for fast package resolution, deterministic `uv.lock`, and
    PEP 517 builds.
  - Linting and formatting with **Ruff** (preview rules enabled, docstring formatting,
    and import organization).
  - Strict static type analysis with **Pyrefly** (`preset = "strict"` with PEP 695
    generics).
  - Cognitive complexity enforcement with **complexipy** (ceiling of <= 10 per
    function/method).
  - Modular boundary enforcement via **Tach** and declared dependency checks via
    **Deptry**.
  - Declarative task runner integration with **Poe the Poet** (`uv run poe <task>`).
  - High-performance Markdown linting and embedded code verification with **rumdl**.
  - Source code and documentation spell checking with **typos**.
  - Consistent TOML and YAML/CSS formatting with **Taplo** and **Prettier**.
- **Rigorous Test Stack**:
  - **100% Mandatory Test Coverage**: Configured with `.coveragerc` enforcing statement
    and branch coverage (`fail_under = 100`).
  - Multi-core parallel execution with **pytest-xdist** (`-n auto`).
  - Flakiness and state-leakage detection with **pytest-randomly**.
  - Declarative snapshot assertions with **syrupy**.
  - Generative property-based testing with **hypothesis**.
  - Deep AST mutation testing with **Cosmic Ray**.
  - Zero-warning tolerance via `filterwarnings = "error"` in `pytest.ini`.
- **First-Class AI Agent Readiness**:
  - Unified agent entry point via root `AGENTS.md`, symlinked to `CLAUDE.md`,
    `.cursorrules`, and `.windsurfrules`.
  - Machine-readable context discovery configs for OpenAI Codex CLI
    (`.codex/config.toml`), Aider (`.aider.conf.yml`), and Google Gemini CLI
    (`.gemini/settings.json`).
  - Repository `.agents/skills/` directory with 26 agent skills covering architecture
    decisions (ADRs), code reviews, git hygiene, benchmark inspections, and tool syntax.
  - ASD-STE100 Simplified Technical English linting and auto-fixing (`asd-ste100` skill
    and `ste-lint.py`).
  - Clear AI governance policies and disclosure checklist in `AI_POLICY.md` and PR
    templates.
  - Automated compilation of `site/llms.txt` and `site/llms-full.txt` by Zensical.
- **Modern Documentation**:
  - Fast TOML-based static documentation generator with **Zensical**.
  - Two-file CSS design token architecture (`palette.css` and `custom.css`) harmonizing
    Catppuccin Latte/Mocha with Typst logo colors.
  - Client-side LaTeX math rendering with MathJax.
  - Dynamic code execution and directory tree rendering via `markdown-exec`.
  - Interactive terminal animation widgets powered by **Termynal**.
  - Programmatic vector SVG logotypes compiled via **Typst**.
- **CI/CD & Security Pipelines**:
  - GitHub Actions test matrix across Python 3.12, 3.13, 3.14, and 3.15.
  - Lowest-direct dependency resolution gate (`--resolution lowest-direct`).
  - Distribution wheel smoke testing in clean, isolated virtual environments
    (`test-dist`).
  - Supply-chain security cutoff buffer via `UV_EXCLUDE_NEWER`.
  - CI workflow security static analysis via **zizmor**.
  - Automated showcase synchronization to `bwrob/zenith-example` via
    `sync-example.yaml`.
  - Automated dependency pull request merging via Dependabot and Renovate.

[unreleased]: https://github.com/bwrob/zenith/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/bwrob/zenith/releases/tag/v0.1.0
