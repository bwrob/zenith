---
diataxis: how-to
purpose: Provide operational procedures for version control, changelog curation, code review audits, ADR creation, and doc authoring.
---

# Workflow Skills

Modern software engineering with AI coding assistants is only as reliable as the
processes governing it. Without explicit procedural guardrails, agents cut corners.
They stage unverified files, guess changelog entries, skip pre-commit test runs, or
forget why teams chose an architecture.

The **`workflow-*`** skill suite codifies the operational rituals, version control
practices, quality checkpoints, and governance workflows of the repository into
predictable, repeatable procedures. Rather than providing a rigid script, each
workflow skill explains clear intent, rationale, and execution steps. Both human
developers and AI agents execute these steps with confidence.

## Core Template Workflows

Every project scaffolded from Zenith includes these skills to guide day-to-day
development.

### Git Hygiene & Commit Governance (workflow-git)

**What it is**: The version control protocol governing how developers inspect,
stage, commit, and submit code changes.

**Why it is in Zenith**: Unsupervised AI assistants frequently run `git add .` or
`git commit -am "fix"`. This sweeps intermediate scratch files, broken tests, or
unformatted files into Git history. `workflow-git` establishes a zero-tolerance policy
for indiscriminate staging. It requires:

- **Targeted Staging**: Staging verified files individually (`git add <file>`), never
  using blanket commands like `git add .` or `git add -A`.
- **Pre-Commit Gate Enforcement**: Verifying that `uv run poe test` (100% test coverage)
  and `uv run poe code-quality` pass before staging or committing any code.
- **Conventional Commits**: Structures commit messages using standard types (`feat`,
  `fix`, `docs`, `refactor`, `test`, `ci`, `chore`). Release automation and changelog
  generators remain fully deterministic.
- **AI Attribution & Disclosure**: Automatically injecting an AI disclosure checklist
  into pull request descriptions, documenting active AI tools and verifying local test
  execution.

### Pre-Flight Code Review (workflow-code-review)

**What it is**: An adversarial self-audit checklist that an agent or developer runs
before submitting changes or opening a pull request.

**Why it is in Zenith**: Passing tests can still hide architectural debt. Code can
contain unbounded type parameters, dead code, leaky module boundaries, or unplanned API
exports. `workflow-code-review` acts as an automated first line of defense for project
stewardship.

Before presenting work for human review, the workflow verifies:

1. **AI Policy Compliance**: Verifies zero dead code, zero suppressed type diagnostics
   without rationale, and honest disclosure of any AI assistance per `AI_POLICY.md`.
2. **Architectural Invariants**: Runs `uv run poe dependencies` to verify module
   boundaries and verify that circular dependencies do not exist.
3. **Type Precision**: Verifies that Meta Pyrefly reports zero type errors and that
   models leverage PEP 695 type parameter syntax and structural protocols.
4. **Coverage Invariants**: Asserts that 100% branch and statement coverage is intact.

### Source-Verified Changelog Curation (workflow-changelog)

**What it is**: A disciplined maintenance workflow for `docs/changelog.md` following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

**Why it is in Zenith**: LLMs typically generate changelogs by skimming commit messages.
Commit titles often miss edge cases or describe internal implementation details instead
of user impact. The resulting release notes become unreliable.

`workflow-changelog` enforces a **source-verified invariant**. The agent must inspect
Git diffs, pull request descriptions, and public API symbols before drafting entries.
It categorizes changes under standard subsections (`Added`, `Changed`, `Deprecated`,
`Removed`, `Fixed`, `Security`). The skill maintains tag comparison links at the bottom
of the document.

### Architecture Decision Records (workflow-adr)

**What it is**: A structured decision-logging workflow using the
[MADR 3.0.0](https://adr.github.io/madr/) (Markdown Architectural Decision Records)
format.

**Why it is in Zenith**: In active codebases, teams often ask why an architectural
choice exists. When teams change libraries or boundaries without recording context,
future contributors propose reversing choices. This repeats past debates.

`workflow-adr` creates sequential, zero-padded records in `docs/adr/` (for example,
`0001-record-architecture-decisions.md`). Each record captures decision status,
context, options, and outcomes. The skill updates `docs/adr/index.md` and registers
pages in `zensical.toml`.

### Environment Bootstrap & Recovery (workflow-setup)

**What it is**: A zero-friction runbook for bootstrapping a clean development
environment or recovering from a corrupted virtual environment.

**Why it is in Zenith**: Modern Python toolchains can become tangled when global Python
installations conflict with local virtual environments. `workflow-setup` leverages
Astral `uv` to establish hermetic, reproducible environments in seconds without
requiring manual virtualenv activation or global tool installation.

It executes the standard onboarding sequence:

```bash
uv sync                      # Hermetically installs all pinned dependencies
uv run prek install          # Installs Rust-native Git pre-commit hooks
uv run poe test              # Verifies the test suite passes locally
uv run poe code-quality      # Confirms linting, types, and formatting pass
```

### Skill Authoring & Standards (workflow-skill-creator)

**What it is**: The meta-skill that governs designing, structuring, and maintaining new
agent capabilities in Zenith repositories.

**Why it is in Zenith**: Ad-hoc agent skills degrade into bloated prompt dumps. These
dumps overwhelm LLM context windows and cause hallucinated tool flags.

`workflow-skill-creator` enforces the core architectural invariants of Zenith skills:

- **5-Prefix Taxonomy**: Restricts skill names to `sdd-*`, `workflow-*`, `tool-*`,
  `guide-*`, or `domain-*` to prevent naming collisions and guarantee predictable
  discovery.
- **Progressive Disclosure**: Keeps `SKILL.md` lean, placing detailed reference manuals,
  templates, and code recipes in dedicated subdirectories (`references/`, `templates/`,
  `examples/`, `scripts/`). The runner loads full text into context only when needed.
- **Simplified Technical English (ASD-STE100)**: Enforces clear, unambiguous language
  verified by an automated linter across agent skills and Python docstrings.
- **Template Synchronization**: Automatically handles symlink wiring between template
  sources and repository links via `uv run poe sync-skills`.

### Human-Centered Documentation Authoring (workflow-docs-authoring)

**What it is**: The operational authoring workflow and writing standard for creating
clear, human-centered technical documentation in `docs/`.

**Why it is in Zenith**: AI assistants frequently produce wordy, passive prose that
re-states the obvious without providing actionable value. Furthermore, documentation
degrades when multiple guides duplicate the same configuration. Instructions then drift
out of sync.

`workflow-docs-authoring` enforces core architectural and writing rules:

- **Human-First Prose Without Rigid STE Enforcement**: User documentation in `docs/`
  prioritizes natural, human-centered readability. While STE-100 principles serve as
  helpful suggestions for clarity, STE-100 is not enforced as a rigid rule in docs.
  Strict STE-100 compliance is reserved for agent skills and code docstrings.
- **Diátaxis Information Architecture**: Classifies every page into one of four intent
  quadrants (*Tutorials*, *How-To Guides*, *Reference*, *Explanation*). Enforces scope
  through a mandatory non-renderable YAML frontmatter preamble (`diataxis:` and
  `purpose:`). Guides page splitting when content drifts across boundaries.
- **Documentation-Driven Design (DDD)**: Drafts user guides and tutorials in lockstep
  with interface design. Friction in writing docs serves as an immediate design smell
  prompting public API simplification.
- **Golden Source of Truth ("Do Not Repeat, Link")**: Every option, architecture
  decision, and API behavior has a single canonical location. Documentation links
  directly to canonical sources (`docs/adr/`, `mkdocstrings`, `docs/tools/`)
  instead of duplicating text. Code snippets are complete, standalone runnable, and
  transcluded from continuous CI-tested files via `pymdownx.snippets` (`--8<--`).
- **Progressive Disclosure & Editor DX**: Focuses mainstream guides on the primary 80%
  use path, quarantining advanced complexity into dedicated reference pages. Ensures
  all Python examples carry explicit typing so developer editors autocomplete cleanly.
- **Anti-AI-Slop Writing Standards**: Eliminates hollow filler, circular definitions,
  and marketing buzzwords (`seamless`, `robust`, `delve`, `game-changer`, `empower`).
  Mandates direct, active-voice instructions, honest negative-space analysis
  (limitations and trade-offs), and structural verification with `uv run poe format-md`,
  `uv run poe lint-md`, and `uv run poe docs-build`.

---

> [!TIP]
> **Looking for Spec-Driven Development?**
> The `sdd-*` skills (`sdd`, `sdd-spec`, `sdd-plan`, `sdd-implement`, `sdd-review`)
> now form a dedicated group. See the [Spec-Driven Development Suite](sdd.md) guide.

## Maintainer Workflow Skills

These skills live in the Zenith template repository (`bwrob/zenith`) to support ongoing
maintenance, upstream tool tracking, and downstream showcase verification.

### External Repository Benchmarking (workflow-inspect-repo)

**What it is**: A 9-pillar audit framework for benchmarking mature open-source Python
projects to identify industry best practices.

**Why it is in Zenith**: Zenith tracks Python ecosystem trends by evaluating mature
repositories (such as projects from Astral, Meta, and Tiangolo). Rather than adopting
tools on hype, `workflow-inspect-repo` systematically evaluates external repositories
across 9 engineering pillars:

1. Packaging & Dependency Resolution (`uv`, PEP 621)
2. Linting & Formatting Standards (`ruff`, preview rules)
3. Static Typing Depth (`pyrefly`, `mypy`, PEP 695)
4. Testing Rigor & Mutation Testing (`pytest`, `mutmut`, `cosmic-ray`)
5. Architecture & Layer Enforcement (`tach`)
6. CI/CD Workflows & Security (`zizmor`, GitHub Actions)
7. Documentation Architecture (`zensical`, `termynal`)
8. Agentic Engineering & Discovery (`AGENTS.md`, modular skills)
9. Developer Ergonomics & Task Runners (`poethepoet`, `prek`)

Findings synthesize into actionable improvement proposals for Zenith.

### Dependency Upgrades & Skill Sync (workflow-update-tools)

**What it is**: The maintenance protocol for upgrading tool versions in `pyproject.toml`
and synchronizing matching agent skills.

**Why it is in Zenith**: Developer tools evolve rapidly. When Ruff introduces new
preview rule sets, Pyrefly updates type parameter rules, or `uv` changes CLI flags,
updating `pyproject.toml` alone is not enough. If the agent skills are not updated in
tandem, AI coding assistants will continue using obsolete flags or generate outdated
configurations.

`workflow-update-tools` pairs every dependency bump with:

1. Research into upstream release notes and breaking changes.
2. Configuration updates across `pyproject.toml`, `ruff.toml`, and `prek.toml`.
3. Synchronized updates to matching `tool-*` skills to reflect new flags and syntax.
4. Downstream verification in the showcase repository.

### Live Showcase Synchronization (workflow-example-sync)

**What it is**: The synchronization bridge and downstream canary verification protocol
between Zenith and the live showcase repository `bwrob/zenith-example`.

**Why it is in Zenith**: A Cookiecutter template cannot be proven by unit tests alone.
You need a real downstream repository. The canary workflow commits generated code,
locks dependencies, runs tests, builds docs, and verifies CI on real runners.

`workflow-example-sync` governs this lifecycle:

- Generates an instantiated project into `../zenith-example` using
  `scripts/sync_example.py`.
- Formats rendered files and locks dependencies with `uv lock`.
- Runs downstream test suites, type analysis, and pre-commit hooks.
- Monitors GitHub Actions CI workflow runs across Linux, macOS, and Windows to guarantee
  that template modifications never break downstream users.

## Authoring Custom Workflow Skills

When your project introduces specialized development processes—such as deployment
pipelines, database migrations, or incident triage—codify them as custom workflow
skills:

```bash
mkdir -p .agents/skills/workflow-deploy/{templates,scripts,references}
```

By adding a `SKILL.md` with clear triggers and instructions, you provide human teammates
and AI agents with an identical, verifiable operational playbook.
