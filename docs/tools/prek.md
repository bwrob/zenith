---
diataxis: reference
purpose: Document Git pre-commit lifecycle hooks, automated fixers, and hook installation with prek.
---

# Prek: Git Hook Automation

[![Tool: prek](https://img.shields.io/badge/prek-enabled-brightgreen)](https://github.com/j178/prek)

`prek` is a fast Git hook runner written in Rust. In Zenith, it validates
code hygiene, detects secrets, verifies schemas, and enforces formatting before
you create commits.

## What It Does

`prek` manages Git hook lifecycles. It intercepts `git commit` commands to run
automated inspections across staged files.

Zenith configures `prek` through `prek.toml` with multiple validation layers:

- **File Sanitization**: Trims trailing whitespace, fixes end-of-file newlines,
  validates merge and case conflicts, and blocks oversized files.
- **Secret Detection**: Runs `gitleaks` to detect hardcoded credentials, API keys,
  and sensitive tokens.
- **Manifest Validation**: Runs `validate-pyproject` to ensure `pyproject.toml`
  schema integrity.
- **Code Formatters**: Runs `ruff`, `taplo`, `rumdl`, and `prettier` directly on
  staged files.
- **Local Quality Gates**: Runs `pyrefly`, `complexipy`, and `tach`. This ensures
  code meets strict typing, cognitive complexity, and layer boundary standards before
  leaving the workstation.

## Why It Is in Zenith

Zenith standardizes on modern, fast, Rust-native developer tooling. Unlike
traditional Python hook runners, `prek` executes hooks in milliseconds without
Python interpreter startup latency or global virtual environment overhead.

`prek` establishes an automated local barrier that prevents defective code,
unformatted files, and accidental secret disclosures from ever entering the Git
commit history.

## Configuration in Zenith

Configured in `prek.toml` at the project root:

```python exec="1" result="toml"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/prek.toml")
if not path.exists():
    path = Path("prek.toml")
print(path.read_text().strip())
```

## Architectural Rationale

Local hooks call tools directly so they can process staged file paths and return
reliable exit codes.

### Direct Invocations Vs. Poe Tasks

In Zenith, local hooks in `prek.toml` invoke tools directly using `uv run <tool>`
(for example, `uv run pyrefly check` or `uv run tach check`) rather than delegating
to task aliases (`uv run poe type-check`):

1. **Staged File Argument Passing**: `prek` passes the list of staged filenames
   directly to hook commands. Direct tool invocations receive and process these file
   arguments natively. In contrast, wrapping calls in task runners can misroute or
   drop path arguments.
2. **Subprocess Overhead Elimination**: Direct `uv run <tool>` invocations avoid
   nested subprocess wrappers. This keeps local Git commit operations instantaneous.
3. **Deterministic Exit Codes**: Direct commands propagate exit codes straight to
   Git without an intermediate task runner layer.

## Key Invocations

```bash
uv run prek install             # Install Git commit hooks into .git/hooks/
uv run prek run --all-files     # Execute all hooks across the entire repository
uv run prek run <hook_id> -a    # Execute a specific hook across all files
uv run prek update              # Update hook repositories to their latest revs
uv run prek validate-config     # Validate configuration syntax
```

## Upstream Documentation

- [prek Official Documentation](https://prek.j178.dev/)
- [prek GitHub Repository](https://github.com/j178/prek)
- [prek Schema Documentation](https://www.schemastore.org/prek.json)
