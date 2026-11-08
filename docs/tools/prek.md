---
diataxis: reference
purpose: Document Git pre-commit lifecycle hooks, automated fixers, and hook installation with prek.
---

# Prek: Git Hook Automation

[![Tool: prek](https://img.shields.io/badge/prek-enabled-brightgreen)](https://github.com/j178/prek)

`prek` is a Rust-native Git hook runner compatible with the `pre-commit` ecosystem. In
Zenith, `prek` installs both **`pre-commit`** and **`pre-push`** hooks
(`default_install_hook_types = ["pre-commit", "pre-push"]`) to keep individual commits
sub-second while running whole-project static checks before `git push`.

## Two-Stage Hook Architecture

`prek.toml` splits local hooks across `pre-commit` and `pre-push` stages.

### Stage 1: Pre-Commit (Staged Files Only)

Runs on `git commit` across staged files, scheduled by `[priorities]` so file-mutating
formatters never race on the same file:

- **Priority 0–2 (File hygiene)**: Fixes mixed line endings, trims trailing whitespace
  (excluding `.ambr` snapshots), and ensures newline at end of file.
- **Priority 3 (`uv-lock`)**: Ensures `uv.lock` stays synchronized with
  `pyproject.toml`.
- **Priority 4 (`independent_formatters`)**: Formats JSON (`pretty-format-json`), YAML
  (`prettier`), CSS (`prettier-css`), and TOML (`taplo-format`).
- **Priority 5–6 (`source_fix` & `python_format`)**: Formats Markdown and embedded code
  blocks (`rumdl-fmt`), auto-fixes Python lint issues (`ruff-check --fix`), and formats
  Python files (`ruff-format`).
- **Priority 7 (`checks`)**: Checks for merge/case conflicts, oversized files
  (`> 2000 KB`), valid YAML/JSON/XML/TOML syntax, `pyproject.toml` schema validity
  (`validate-pyproject`), hardcoded secrets (`gitleaks`), and spelling errors (`typos`).

### Stage 2: Pre-Push (Whole-Project Static Gates)

Runs on `git push` (`pass_filenames = false`) when Python or tool config files have
changed:

- **`pyrefly`**: Runs `uv run pyrefly check`.
- **`pyrefly-coverage`**: Runs
  `uv run pyrefly coverage check src --fail-under 100 --strict`.
- **`complexipy`**: Runs `uv run complexipy src tests`.
- **`tach`**: Runs `uv run tach check`.

> [!NOTE]
> **Why `uv run prek run --all-files` Only Runs `pre-commit` Stage Hooks by Default**:
> Because `default_stages = ["pre-commit"]`, `uv run prek run --all-files` executes the
> `pre-commit` hooks. To run the `pre-push` hooks manually on demand, pass
> `--hook-stage pre-push` (`uv run prek run --hook-stage pre-push --all-files`) or run
> `uv run poe code-quality`.

## Configuration in Zenith

Configured in `prek.toml` at the project root:

```python exec="1" result="toml"
import re
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/prek.toml")
if not path.exists():
    path = Path("prek.toml")
text = path.read_text(encoding="utf-8")
text = re.sub(r"^# =+[^\n]*\n(?:#[^\n]*\n)*# =+[^\n]*\n+", "", text)
print(text.strip())
```

## Key Invocations

```bash
# Install pre-commit and pre-push hooks into .git/hooks/
uv run prek install

# Run all pre-commit hooks across the repository
uv run prek run --all-files

# Run pre-push hooks (pyrefly, complexipy, tach)
uv run prek run --hook-stage pre-push --all-files

# Run a single hook by ID or alias (e.g. prettier-css)
uv run prek run <hook_id> --all-files

# Update external hook repositories and validate prek.toml
uv run prek autoupdate
uv run prek validate-config
```

## Upstream Documentation

- [prek Official Documentation](https://prek.j178.dev/)
- [prek GitHub Repository](https://github.com/j178/prek)
- [prek JSON Schema](https://www.schemastore.org/prek.json)
