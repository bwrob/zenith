---
description: >-
  Workflow for updating tool-* skills when upgrading tool versions.
  Use when upgrading dependencies in pyproject.toml or when upstream tools introduce new features, syntax, or flags.
  Triggers: update tools, upgrade tool, update skill, bump dependency, sync skills.
name: update-tools
version: 1.0.0
---

# Updating Tool Skills (`update-tools`)

This skill defines the maintenance workflow to keep `.agents/skills/tool-*`
updated when tools used by Zenith upgrade to new versions.

Use this skill whenever you upgrade dependencies in `pyproject.toml` or when a
tool introduces new features, syntax, or configuration changes.

---

## 1. Upgrade Detection & Inventory

When upgrading project tools, inspect version bumps to identify which skills
require review.

```bash
# Compare lockfile or dependency group changes
git diff pyproject.toml uv.lock
```

### Upstream Sources & Official Skills Registry

| Tool | Official Skill Source | Changelog / Docs |
| --- | --- | --- |
| `poethepoet` | Built into package wheel (`poethepoet/skills/`) | `poethepoet.natn.io` |
| `uv` | `astral-sh/claude-code-plugins` (GitHub) | `docs.astral.sh/uv` |
| `ruff` | `astral-sh/claude-code-plugins` (GitHub) | `docs.astral.sh/ruff` |
| `pyrefly` | Meta Pyrefly repository | `pyrefly.org` |
| `complexipy` | `complexipy` GitHub releases | GitHub releases |
| `tach` | `tach` repository | `docs.gauge.sh` |
| `rumdl` | `rumdl` repository | GitHub releases |
| `typos` | `crate-ci/typos` | GitHub releases |
| `zensical` | `zensical` docs | `zensical.org` |
| `pytest` | `pytest` releases & plugin docs | `docs.pytest.org` |
| `typst` | `typst` releases | `typst.app/docs` |
| `cookiecutter` | Template repository | `cookiecutter.readthedocs.io` |

---

## 2. Researching Upstream Changes

Before editing a skill, review what changed in the upgraded tool version:

1. **Check for upstream official skill updates**:
   - For `poethepoet`, inspect the newly installed wheel:

     ```bash
     uv run python -c "import poethepoet, os; print(os.path.dirname(poethepoet.__file__))"
     ```

   - For Astral tools (`uv`, `ruff`), check `astral-sh/claude-code-plugins`.
2. **Review breaking changes & deprecations**: Check if CLI flags, TOML
   tables, or default behaviors changed.
3. **Review new configuration options**: Check for new linter rules, new CLI
   subcommands, or optimized settings suitable for Zenith's strict preset.

---

## 3. Updating the Skill Document

Update the corresponding skill files in `{{cookiecutter.project_slug}}/.agents/skills/tool-<name>/SKILL.md`
(and any reference docs under `references/`):

- **CLI Commands**: Update commands if subcommands or flags changed.
- **Configuration Sections**: Update example TOML tables to match new options.
- **Version Frontmatter**: Bump the skill `version:` field.
- **Formatting Compliance**:
  - Narrative line length: strictly $\le 88$ characters.
  - Code block line length: strictly $\le 79$ characters.
  - Frontmatter sorting: `description` before `name` (MD072).
  - Heading hierarchy: narrative content must precede subheadings (MD082).
  - Blank lines: code fences must be surrounded by blank lines (MD031).
  - Embedded Python: snippets must pass `ruff check` and `ruff format`.

---

## 4. Syncing Template Skills

Zenith treats `{{cookiecutter.project_slug}}/.agents/skills/` as the canonical source
of truth for shared skills. Root skills in `.agents/skills/` are relative symlinks.

> [!IMPORTANT]
> **Repo-Only Skills**:
> `tool-cookiecutter`, `update-tools`, `inspect-module-setup`, and `zenith-example-sync`
> belong directly to the root repository. Never copy them into
> `{{cookiecutter.project_slug}}`.

Sync symlinks across the repository:

```bash
uv run poe sync-skills
uv run poe sync-skills-check
```

---

## 5. Verification & Quality Gates

Run the full verification pipeline before committing changes:

```bash
# 1. Lint markdown and STE compliance across all skills
uv run poe lint-md
uv run poe check-skills

# 2. Check spelling
uv run poe typos

# 3. Run template unit tests
uv run poe test

# 4. Run full code quality pipeline
uv run poe code-quality
```
