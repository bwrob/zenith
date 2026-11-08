---
diataxis: how-to
purpose: Provide operational procedures for version control, changelog curation, code review audits, ADR creation, and doc authoring.
---

# Workflow Skills

The **`workflow-*`** skills define repeatable procedures for Git operations, pre-PR code
reviews, changelog maintenance, architecture decision records, documentation authoring,
and environment setup.

> [!TIP]
> **Looking for Spec-Driven Development?** The `sdd-*` skills (`sdd`, `sdd-spec`,
> `sdd-plan`, `sdd-implement`, `sdd-review`) are documented in the
> **[Spec-Driven Development Suite](sdd.md)** guide.

## Template Workflow Skills

These eight workflow skills ship in every generated Zenith project (when
`include_agent_skills` is enabled):

| Skill                                                                               | Activation  | Trigger Domain                                     | Verification Gate                                                |
| :---------------------------------------------------------------------------------- | :---------- | :------------------------------------------------- | :--------------------------------------------------------------- |
| [`workflow-git`](#git-hygiene-workflow-git)                                         | Mandatory   | Branches, staging, commits, and pull requests      | `poe code-quality`, `poe test`, `prek run --all-files`           |
| [`workflow-code-review`](#pre-flight-code-review-workflow-code-review)              | Mandatory   | Pre-PR audits and code review requests             | `poe code-quality`, `poe test`, `poe verify-wheel`, `prek`       |
| [`workflow-changelog`](#changelog-curation-workflow-changelog)                      | Mandatory   | Editing `docs/changelog.md` or preparing a release | `rumdl check docs/changelog.md`, `poe docs-build`                |
| [`workflow-adr`](#architecture-decision-records-workflow-adr)                       | Mandatory   | Creating or updating records in `docs/adr/`        | `rumdl check docs/adr/`, `poe docs-build`                        |
| [`workflow-docs-authoring`](#documentation-authoring-workflow-docs-authoring)       | Mandatory   | Authoring or editing documentation in `docs/`      | `poe format-md`, `poe lint-md`, `poe test`, `poe docs-build`     |
| [`workflow-skill-creator`](#skill-authoring-workflow-skill-creator)                 | Mandatory   | Creating or modifying skills in `.agents/skills/`  | `poe lint-ste`, `poe check-skills`                               |
| [`workflow-setup`](#environment-bootstrap-workflow-setup)                           | Manual only | Bootstrapping or repairing the local `.venv`       | `uv sync`, `prek install`, `poe test`, `poe code-quality`        |
| [`workflow-docs-consumers`](#documentation-consumer-review-workflow-docs-consumers) | Manual only | Stress-testing docs with simulated reader personas | Persona reports written to `.temp/docs-review/<persona-slug>.md` |

### Git Hygiene (workflow-git)

Governs how branches are named, how files are staged and committed, and how pull
requests are opened and monitored:

- **Explicit path staging**: Requires `git add <file1> <file2>` and forbids blanket
  staging (`git add .`, `git add -A`, `git commit -am`) so scratch or untracked files
  are never swept into commits.
- **Reason-focused Conventional Commits**: Formats commit headers as
  `<type>(<scope>): <imperative summary>` stating *why* the change was made, plus
  `Co-authored-by` trailers when AI assistants contributed.
- **Shell-safe outbound CLI calls**: Uses single-quoted heredocs
  (`--body-file - <<'EOF'`) when calling `gh pr create` so Markdown backticks are never
  expanded by the shell.
- **Post-push CI monitoring**: Requires watching triggered GitHub Actions runs via
  `gh run list` and `gh run watch` until all remote jobs pass.

### Pre-Flight Code Review (workflow-code-review)

Runs a 6-point audit before opening a pull request or when asked to review a diff:

- **Read-only review contract**: When asked to review a working tree or PR diff, the
  agent reports grounded findings (`file:line` + concrete failing input or violated
  rule) and stops without making unrequested edits.
- **6-Point Review Matrix**: Checks `AI_POLICY.md` compliance (no diff-narrative
  comments), Tach layer boundaries and Griffe public API compatibility
  (`poe check-api`), Python 3.12+ typing and the no-`# noqa` rule, cognitive complexity
  (`<= 10`), 100% branch coverage, and wheel packaging (`poe verify-wheel`).

### Changelog Curation (workflow-changelog)

Maintains `docs/changelog.md` following
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html):

- **Source-checked entries**: Inspects actual Git diffs (`git diff vX.Y.Z..HEAD`), pull
  request bodies (`gh pr view`), and public API changes rather than guessing release
  notes from commit subjects alone.
- **Standard categories**: Groups changes under `Added`, `Changed`, `Deprecated`,
  `Removed`, `Fixed`, and `Security`, and updates tag comparison links at the bottom of
  the file.

### Architecture Decision Records (workflow-adr)

Logs architectural choices in `docs/adr/` using the
[MADR 3.0.0](https://adr.github.io/madr/) format:

- Creates sequential, zero-padded files (`docs/adr/0002-<kebab-case-title>.md`) from
  `docs/adr/template.md`.
- Records status (`Proposed`, `Accepted`, `Rejected`, `Superseded`, `Deprecated`),
  context, evaluated options, and trade-offs.
- Updates the index table in `docs/adr/index.md` and registers new records in
  `zensical.toml`.

### Documentation Authoring (workflow-docs-authoring)

Enforces structural and writing standards across `docs/`:

- **Golden Source of Truth ("Do Not Repeat, Link")**: Every concept, CLI flag, and API
  signature has one canonical home. Public Python APIs are rendered with `mkdocstrings`
  (`::: package.module`), and runnable examples are transcluded via `pymdownx.snippets`
  (`--8<--`).
- **Diátaxis frontmatter preamble**: Every Markdown page in `docs/` begins with
  non-renderable `diataxis:` (`tutorial | how-to | reference | explanation`) and
  `purpose:` YAML frontmatter.
- **Human-first anti-slop prose**: Bans throat-clearing intros, circular definitions,
  and hollow marketing buzzwords (`seamless`, `robust`, `delve`, `game-changer`,
  `empower`). Note that ASD-STE100 is strictly enforced on `.agents/skills/` and Python
  docstrings, not on user-facing prose in `docs/`.

### Skill Authoring (workflow-skill-creator)

Governs how new skills in `.agents/skills/` are structured and validated:

- **5-prefix taxonomy**: Restricts skill directory names to `sdd-*`, `workflow-*`,
  `tool-*`, `guide-*`, or `domain-*`.
- **Progressive disclosure layout**: Keeps `SKILL.md` concise and places reusable
  artifacts in `templates/`, `references/`, `examples/`, and `scripts/`.
- **Automated verification**: Validates ASD-STE100 compliance with `uv run poe lint-ste`
  and structural frontmatter rules with `uv run poe check-skills`. (To pull skills from
  installed third-party packages, generated projects also provide
  `uv run poe sync-skills` via `library-skills`.)

### Environment Bootstrap (workflow-setup)

Manual-only runbook (`disable-model-invocation: true`) for initializing or repairing the
local development environment:

```bash
uv sync                      # Install locked dependencies into .venv
uv run prek install          # Install pre-commit and pre-push Git hooks
uv run poe test              # Verify unit tests and 100% coverage locally
uv run poe code-quality      # Verify linters, formatters, types, and boundaries
```

### Documentation Consumer Review (workflow-docs-consumers)

Manual-only workflow (`disable-model-invocation: true`) that dispatches read-only
subagents representing five reader personas (*Junior Developer*, *Opinionated Senior
Pythonista*, *Tech Lead & Engineering Manager*, *DevOps Engineer*, *Solo Prototyper*).
Each persona writes a review artifact to `.temp/docs-review/<persona-slug>.md`, which
the lead agent compacts into concrete file-by-file edit proposals.

## Upstream Maintainer Skills (Template Repository Only)

These three skills exist only in the upstream Zenith template repository and are omitted
from generated projects:

| Skill                   | Activation  | Purpose in `bwrob/zenith`                                                                                                            |
| :---------------------- | :---------- | :----------------------------------------------------------------------------------------------------------------------------------- |
| `workflow-update-tools` | On demand   | Upgrades tool versions in root and template `pyproject.toml` and updates matching `tool-*` skills in lockstep                        |
| `workflow-inspect-repo` | Manual only | Audits external open-source Python repositories across 9 engineering pillars to benchmark practices for Zenith                       |
| `workflow-example-sync` | Manual only | Renders Zenith into `bwrob/zenith-example` via `scripts/sync_example.py` and verifies downstream CI across Linux, macOS, and Windows |

## Creating a Custom Workflow Skill

To codify a team-specific operational process (such as database migrations or release
deployments), scaffold a `workflow-<name>` directory:

```bash
mkdir -p .agents/skills/workflow-deploy/{templates,scripts,references}
```

Author `.agents/skills/workflow-deploy/SKILL.md` and validate it with
`uv run poe lint-ste` and `uv run poe check-skills`.
