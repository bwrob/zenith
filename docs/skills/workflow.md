# Workflows

The **`workflow-*`** skill group codifies multi-step lifecycle operations, release
rituals, version control practices, quality checkpoints, and governance workflows.

These skills guide human developers and autonomous AI agents through structured,
deterministic procedures without skipping critical quality steps.

---

## Template Workflow Skills

### `workflow-git`

- **Directory**: `.agents/skills/workflow-git/`
- **Triggers**: `git commit`, `prepare commit`, `pull request`, `stage files`,
  `conventional commit`.
- **Purpose**: Enforces strict version control discipline:
  - **No Blanket Staging**: Prohibits indiscriminate `git add .` or `git add -A`.
    Requires precise staging of verified files (`git add <file>`).
  - **Conventional Commits**: Enforces structured commit types (`feat`, `fix`, `docs`,
    `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`).
  - **Pre-Commit Verification**: Mandates running `uv run poe test` and
    `uv run poe code-quality` before staging or committing.
  - **AI Disclosure Checklist**: Injects structured attribution and local verification
    checklists into pull request descriptions.

---

### `workflow-code-review`

- **Directory**: `.agents/skills/workflow-code-review/`
- **Triggers**: `review code`, `pre-PR audit`, `check compliance with AI_POLICY.md`,
  `code review`.
- **Purpose**: Provides a deterministic self-audit checklist that agents execute before
  submitting changes:
  - **AI Policy Compliance**: Verifies local verification, zero commented-out code, and
    honest tool disclosure.
  - **Architectural Integrity**: Verifies layer boundaries (`tach check`) and eliminates
    circular imports.
  - **Type Safety**: Inspects strict Pyrefly type annotations, structural protocols, and
    PEP 695 generics.
  - **Test Completeness**: Confirms that statement and branch test coverage remains at
    100% (`fail_under = 100`).

---

### `workflow-changelog`

- **Directory**: `.agents/skills/workflow-changelog/`
- **Triggers**: `changelog`, `release notes`, `update changelog`, `draft release`.
- **Purpose**: Directs the authoring and maintenance of `docs/changelog.md`:
  - Follows [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
    [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
  - Categorizes changes under standard subsections: `Added`, `Changed`, `Deprecated`,
    `Removed`, `Fixed`, `Security`.
  - **Source-Checked Invariant**: Prohibits guessing release notes from commit titles
    alone. Inspects actual code diffs, PR bodies, and deprecation notices.
  - Updates tag comparison links at the bottom of the changelog.

---

### `workflow-adr`

- **Directory**: `.agents/skills/workflow-adr/`
- **Triggers**: `adr`, `architecture decision record`, `record decision`, `create adr`.
- **Purpose**: Documents significant architectural choices using the
  [MADR 3.0.0](https://adr.github.io/madr/) format:
  - Formats records under `docs/adr/NNNN-title.md` with zero-padded 4-digit sequential
    numbering.
  - Tracks decision lifecycles (`proposed`, `accepted`, `rejected`, `deprecated`,
    `superseded`).
  - Records context, decision drivers, considered alternatives, and positive/negative
    trade-offs.
  - Updates `docs/adr/index.md` and registers pages in `zensical.toml`.

---

### `workflow-setup`

- **Directory**: `.agents/skills/workflow-setup/`
- **Triggers**: `setup project`, `bootstrap environment`, `fix venv`,
  `install dependencies`.
- **Purpose**: Bootstraps or repairs a local developer checkout:
  - Synchronizes dependencies with `uv sync`.
  - Installs git pre-commit hooks (`uv run prek install`).
  - Verifies the installation with `uv run poe test` and `uv run poe code-quality`.

---

### `workflow-skill-creator`

- **Directory**: `.agents/skills/workflow-skill-creator/`
- **Triggers**: `create skill`, `new skill`, `author skill`, `modular skill`.
- **Purpose**: Governs the creation of new agent skills in Zenith repositories:
  - Enforces the 4-prefix taxonomy (`workflow-*`, `tool-*`, `guide-*`, `domain-*`).
  - Implements **progressive disclosure**: lean `SKILL.md` with external `templates/`,
    `references/`, and `examples/`.
  - Enforces Simplified Technical English (ASD-STE100) writing standards.
  - Handles synchronization between template skills and repository symlinks.

---

## Maintainer Workflow Skills

These skills exist exclusively in the Zenith template repository (`bwrob/zenith`) to
assist template maintainers:

- **`workflow-inspect-repo`**: 9-pillar audit framework to benchmark external mature
  repositories (packaging, typing, testing, CI, agent skills) and extract best
  practices.
- **`workflow-update-tools`**: Maintenance protocol for upgrading tool versions in
  `pyproject.toml`, adapting to upstream breaking syntax, and updating matching `tool-*`
  skills.
- **`workflow-example-sync`**: Synchronization protocol and downstream canary CI
  verification for the live showcase repository `bwrob/zenith-example`.

---

## Custom Workflow Skills

When your project introduces specialized development processes, add them under the
`workflow-*` prefix:

```bash
mkdir -p .agents/skills/workflow-deploy/{templates,scripts,references}
```

Examples of custom workflows:

- `workflow-deploy`: Automated staging and production deployment checklist.
- `workflow-db-migration`: Safe database schema migration authoring and verification.
- `workflow-incident-triage`: On-call diagnostic and escalation runbook.
