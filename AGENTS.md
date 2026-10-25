# AGENTS.md

Operational guidelines, architectural conventions, and workflows for AI coding
assistants working on the **Zenith** template repository.

## Project Stewardship

When working in this repository, your primary responsibility is to the long-term health
of the project, its users (both human and agent), and its maintainers—not merely
satisfying the immediate prompt with the shortest possible patch. Act as the first line
of defense against technical debt, architectural drift, and low-quality contributions by
enforcing end-to-end type safety, clean public abstractions, comprehensive test
coverage, and accurate documentation.

## Pre-Flight Checks

Before editing code or executing tasks, ensure an isolated, clean working environment:

1. Check repository status with `git status`. Do not make edits when uncommitted changes
   exist without explicit user consent.
2. Confirm remotes and branches before committing or pushing changes. Use git worktrees
   or dedicated feature branches for non-trivial tasks.
3. Run all commands inside the hermetic project environment using `uv run <command>`.
   Never use global or system Python environments directly.
4. When creating temporary or scratch files, always place them in the `.temp/`
   directory. Never pollute the workspace root or tracked directories with temporary
   files.

## Operational Workflows

- **Environment & Packages**: Always use **`uv`**.
  - Sync environment: `uv sync`
  - Add dependency: `uv add <package>` or `uv add --group dev <package>`
  - Run commands in environment: `uv run <command>`
- **Temporary Files**: When creating temporary files, scratch scripts, or intermediate
  test outputs, always store them in the `.temp/` directory.
- **Task Runner**: All development tasks are managed through **Poe the Poet**:
  - `uv run poe test` (run unit tests)
  - `uv run poe code-quality` (run static quality pipeline: lint, format, types,
    security, skills)
  - `uv run poe fix` (auto-fix linting and formatting)
- **Verification Gate**: Before proposing or finalizing changes, always verify your
  work:
  - `uv run poe test`
  - `uv run poe code-quality`
  - `uv run prek run --all-files`
  - Always re-read any files modified by formatters or `prek` hooks before making
    subsequent edits.
- **CI Monitoring on Push**: Never leave work unmonitored after `git push`. Track the
  triggered CI runs with `gh run watch` or `gh run list`. If a remote check fails,
  inspect the failure immediately (`gh run view <run-id> --log-failed`), reproduce,
  fix, and verify until all checks pass.
- **Downstream CI Monitoring on PR Merge**: When merging a pull request to `main`,
  monitor the automated sync workflow (`sync-example.yaml`) and verify that downstream
  canary runs pass in `bwrob/zenith-example` (`workflow-example-sync`).
- **Reproduce-First Bug Scoping**: When fixing a bug, first reproduce the failure with a
  minimal test, trace the root cause, and search the codebase for sibling occurrences of
  the same pattern before editing production code.
- **Complexity Reset Rule**: If a fix or implementation starts requiring layered hacks,
  defensive workarounds, or fighting the type checker, stop and re-evaluate the design
  from first principles rather than piling on patches.
- **AI Contribution Policy**: Consult and adhere to `AI_POLICY.md` for human review,
  local verification, and tool disclosure guidelines.

## Subagent Orchestration & Work-Sharing Policy

When work is decomposed across subagents (background or foreground), follow
these rules so that parallel work neither collides nor leaves orphaned
changes:

1. **Disjoint File Partitioning**: Assign each subagent an explicit, mutually
   exclusive set of file paths. Two agents must never write the same file in
   the same session. Shared "read any, write only yours" discipline: agents
   may read the whole repository, but write only partitioned paths.
2. **Canonical-Path Editing Behind Symlinks**: Root `.agents/skills/*`
   entries are symlinks into the git-tracked template directories
   (for example, `{{cookiecutter.project_slug}}/.agents/skills/tool-ruff/SKILL.md`).
   Instruct agents to edit the canonical template path, never the symlink
   target through the root link, and never to rewrite symlinked files in
   place (`Edit` through a symlink resolves to the target; writes to
   anything besides the canonical path are considered a policy violation).
   Run `uv run poe sync-skills-check` after skill edits.
3. **Per-Agent Context Package**: Do not hand each subagent only a one-line
   mission. Give every agent a package with:
   - the exact file list it may modify,
   - current tool state (config file paths, relevant ignore lists versions,
     failing-check counts),
   - the verification command set it must NOT run (or must run) locally,
   - the required format of its final report (files touched, decisions,
     open questions).
4. **Partial-Work Audit on Cancellation**: When a task is cancelled mid-run
   (by the user, supervisor, or failure), immediately audit the working tree
   with `git status` and `git diff --stat` for partial edits left by the
   cancelled agent. Either complete the work deliberately, or revert the
   half-done files with consent; never assume scattered partial changes are
   self-consistent.
5. **No Interdependent Edits in One Batch**: Do not dispatch multiple agents
   whose edits depend on each other's output within a single parallel batch.
   Sequence dependent edits (or perform them in one agent) so review is
   linearized.

## Strict-Lint Compliance Box

The repository enforces a fully strict ruff preset (`select = ["ALL"]`) with
these invariants:

- A bare `# noqa` comment (with or without codes) anywhere in tracked Python
  is forbidden. Use `# ruff: ignore[full-rule-name]` with a rationale
  comment. Details live in the `tool-ruff` skill, including the line-1
  placement rule for module-level diagnostics.
- Every pylint-style directive references a Ruff rulename, never a letter
  digit code.
- Generated projects must also be linted with their own config from inside
  the rendered directory: `uv run poe lint-rendered`.
- Root and template lint ignore lists must stay in exact lockstep;
  `tests/test_repo_conventions.py` fails on drift.

## Project Instructions Discovery & Compatibility

- **Multi-Agent Discovery & Settings**: Instruction files and configuration profiles are
  maintained in the repository root for seamless compatibility across modern AI coding
  tools:
  - **Claude Code**: `CLAUDE.md` symlink (`ln -s AGENTS.md CLAUDE.md`) and
    `.claude/settings.json` (pre-authorizing hermetic `uv run poe:*` commands).
  - **OpenAI Codex CLI**: `.codex/config.toml` (auto-discovering `AGENTS.md` and setting
    the `workspace-write` sandbox) and `.codex/agents/*.toml` (project subagents).
  - **Google Gemini CLI & Antigravity**: `.gemini/settings.json`
    (`contextFileName: "AGENTS.md"`).
  - **GitHub Copilot**: `.github/copilot-instructions.md` referencing `AGENTS.md`.
  - **Cursor & Windsurf**: `.cursorrules` and `.windsurfrules` symlinks
    (`ln -s AGENTS.md .cursorrules`) and `.cursor/rules/zenith.mdc`.
  - **Aider**: `.aider.conf.yml` (auto-loading `AGENTS.md`, wiring `lint-cmd` and
    `test-cmd` to Poe tasks).
- **Scope Hierarchy**: When exploring subdirectories, check for nested `AGENTS.md` or
  `CLAUDE.md` files; localized instructions take precedence within their scope.
- **Workflow & Tool Guidance**: Consult `.agents/skills/` for lifecycle workflow skills
  (`workflow-git`, `workflow-code-review`, `workflow-changelog`, `workflow-adr`,
  `workflow-setup`, `workflow-skill-creator`, `workflow-docs-authoring`,
  `workflow-docs-consumers`, `workflow-example-sync`), Spec-Driven
  Development suite (`sdd`, `sdd-spec`, `sdd-plan`, `sdd-implement`, `sdd-review`),
  engineering guides (`guide-python`, `guide-ste100`), and tool-specific guidance
  (`tool-*/SKILL.md`).

## Repository Architecture

- `cookiecutter.json`: Template configuration, prompts (`__prompts__`), and variable
  definitions.
- `hooks/`: Lifecycle hooks (`pre_gen_project.py`, `post_gen_project.py`).
  - `hooks/post_gen_project.py`: Strips educational comments, cleans conditional files
    (CLI, `.github`, LICENSE), and establishes AI agent compatibility symlinks and
    settings.
- `templates/`: Shared template partials (e.g. CI workflow components).
- `{{cookiecutter.project_slug}}/`: Root directory of the rendered project template.
- `tests/`: Automated tests validating template rendering, conditional branches, and
  generated asset structures.
