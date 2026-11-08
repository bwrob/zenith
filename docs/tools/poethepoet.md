---
diataxis: reference
purpose: Document hermetic task definitions, command orchestration, and developer shortcuts with Poe the Poet.
---

# Poe the Poet: Task Automation

[![Tool: poethepoet](https://img.shields.io/badge/tasks-poethepoet-blue.svg)](https://poethepoet.natn.io/)

`Poe the Poet` (`poe`) is the declarative task runner used in Zenith projects. Tasks are
defined in `poe_tasks.toml` (included from `pyproject.toml` via
`[tool.poe] include = "poe_tasks.toml"`) and run inside the `uv` virtual environment
with `PYTHONUTF8=1` and `PYTHONWARNDEFAULTENCODING=1`. Both local development and GitHub
Actions workflows invoke the exact same `uv run poe <task>` commands.

## Task Reference

The tables below group all Poe tasks configured in `poe_tasks.toml`.

### Testing & Packaging Tasks

| Task                              | Underlying Command / Sequence                                                  | Purpose                                                                          |
| :-------------------------------- | :----------------------------------------------------------------------------- | :------------------------------------------------------------------------------- |
| `uv run poe test`                 | `pytest --cov --cov-report=term-missing --cov-report=xml`                      | Run test suite and enforce 100% statement and branch coverage                    |
| `uv run poe test-fast`            | `pytest -n auto --dist=worksteal --max-worker-restart=0 --cov ...`             | Run tests in parallel across CPU cores via `pytest-xdist`                        |
| `uv run poe test-lowest`          | `uv sync --resolution lowest-direct` → `pytest --cov` → `uv sync`              | Test against minimum declared dependency bounds                                  |
| `uv run poe test-dist`            | `python scripts/verify_wheel.py --run-tests`                                   | Build wheel, install into an isolated venv, and run `pytest` against it          |
| `uv run poe test-sdist`           | `uv build --sdist` → extract `.tar.gz` → `uv run poe test` → `verify_wheel.py` | Build source distribution, run tests inside extracted archive, and build a wheel |
| `uv run poe verify-wheel`         | `python scripts/verify_wheel.py`                                               | Build wheel and verify package import and CLI `--help` in an isolated venv       |
| `uv run poe test-snapshot-update` | `pytest --snapshot-update`                                                     | Update Syrupy `.ambr` snapshot files                                             |
| `uv run poe coverage`             | `pytest --cov --cov-report=html ...`                                           | Generate interactive HTML coverage report in `htmlcov/`                          |
| `uv run poe test-mutation`        | `mutmut run`                                                                   | Run fast local AST mutation testing (`mutmut`, macOS/Linux)                      |
| `uv run poe test-mutation-cosmic` | `cosmic-ray init` → `cosmic-ray exec` → `cr-report`                            | Run cross-platform SQLite-backed mutation testing (`cosmic-ray`)                 |

### Code Quality & Formatting Tasks

| Task                                           | Underlying Command / Sequence                                                                                                                                                       | Purpose                                                                         |
| :--------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------ |
| `uv run poe code-quality`                      | `lint`, `format-check`, `format-check-toml`, `format-yaml`, `format-css`, `lint-md`, `typos`, `type-check`, `type-coverage`, `complexity`, `zizmor`, `dependencies`, `check-skills` | Run the full static quality pipeline                                            |
| `uv run poe fix`                               | `ruff check --fix`, `ruff format`, `taplo format`, `rumdl fmt`, `prettier`, `prettier-css`, `typos -w`                                                                              | Auto-fix lint issues and format all project files                               |
| `uv run poe lint`                              | `ruff check --config ruff.toml`                                                                                                                                                     | Lint Python code with Ruff                                                      |
| `uv run poe format` / `format-check`           | `ruff format` / `ruff format --check`                                                                                                                                               | Format or verify Python formatting with Ruff                                    |
| `uv run poe format-toml` / `format-check-toml` | `taplo format` / `taplo format --check`                                                                                                                                             | Format or verify TOML files with Taplo                                          |
| `uv run poe format-yaml` / `format-css`        | `prek run prettier --all-files` / `prek run prettier-css --all-files`                                                                                                               | Format YAML or CSS files with Prettier via `prek`                               |
| `uv run poe format-md` / `lint-md`             | `rumdl fmt` / `rumdl check`                                                                                                                                                         | Format or lint Markdown and embedded code blocks with `rumdl`                   |
| `uv run poe typos` / `typos-fix`               | `typos` / `typos -w`                                                                                                                                                                | Check or auto-fix spelling across code and docs                                 |
| `uv run poe type-check`                        | `pyrefly check`                                                                                                                                                                     | Run strict static type checking with Pyrefly                                    |
| `uv run poe type-coverage`                     | `pyrefly coverage check src --fail-under 100 --strict`                                                                                                                              | Enforce 100% strict type annotation completeness across `src/`                  |
| `uv run poe complexity`                        | `complexipy src tests`                                                                                                                                                              | Enforce cognitive complexity `<= 10` per function                               |
| `uv run poe dependencies`                      | `tach check`, `deptry src`                                                                                                                                                          | Verify internal module boundaries (`tach`) and declared dependencies (`deptry`) |
| `uv run poe check-api`                         | `griffe check <package_name> --search src`                                                                                                                                          | Detect breaking public API changes against the previous Git tag                 |
| `uv run poe zizmor`                            | `zizmor --config .zizmor.yml --pedantic --min-severity informational .github/workflows`                                                                                             | Audit GitHub Actions workflows for security vulnerabilities                     |
| `uv run poe audit`                             | `uv audit`                                                                                                                                                                          | Audit locked dependencies in `uv.lock` for known CVEs                           |

### Documentation, Maintenance & Agent Tasks

| Task                      | Underlying Command / Sequence                                                                               | Purpose                                                                    |
| :------------------------ | :---------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------- |
| `uv run poe docs-serve`   | `zensical serve`                                                                                            | Start live-reloading local documentation server at `http://127.0.0.1:8000` |
| `uv run poe docs-build`   | `zensical build --strict --clean`                                                                           | Build static documentation into `site/` with strict link/anchor validation |
| `uv run poe docs-logo`    | Compiles `docs/assets/*.typ` with `typst` and `fontpkg`                                                     | Recompile SVG banner assets from Typst sources                             |
| `uv run poe repl`         | `python -i -c "import <pkg> as pkg; ..."`                                                                   | Launch interactive Python REPL with the package pre-imported as `pkg`      |
| `uv run poe clean`        | Removes `dist/`, `build/`, `site/`, `htmlcov/`, `.pytest_cache/`, `.ruff_cache/`, `.temp/`, mutation caches | Clean build artifacts and caches                                           |
| `uv run poe lint-ste`     | `python .agents/skills/guide-ste100/scripts/ste-lint.py .agents/skills`                                     | Lint agent skills against ASD-STE100 rules                                 |
| `uv run poe check-skills` | `python scripts/check_skills.py .agents/skills`                                                             | Validate frontmatter and structure of `.agents/skills/`                    |
| `uv run poe sync-skills`  | `uvx library-skills --all -y`                                                                               | Pull agent skills from installed library dependencies                      |

## Configuration Excerpt

Representative task definitions in `poe_tasks.toml`:

```toml
[executor]
    type = "uv"

[env]
    PYTHONUTF8                = "1"
    PYTHONWARNDEFAULTENCODING = "1"

[tasks.test]
    cmd  = "pytest --cov --cov-report=term-missing --cov-report=xml"
    help = "Run tests with coverage measurement (pytest + pytest-cov)."

[tasks.fix]
    default_item_type = "cmd"
    help = "Auto-fix linting and formatting issues."
    ignore_fail = "return_zero"
    sequence = [
        "ruff check --fix",
        "ruff format",
        "taplo format",
        "rumdl fmt",
        "prek run prettier --all-files",
        "prek run prettier-css --all-files",
        "typos -w",
    ]

[tasks.code-quality]
    help = "Execute the full code quality verification pipeline."
    ignore_fail = "return_non_zero"
    sequence = [
        "lint",
        "format-check",
        "format-check-toml",
        "format-yaml",
        "format-css",
        "lint-md",
        "typos",
        "type-check",
        "type-coverage",
        "complexity",
        "zizmor",
        "dependencies",
        "check-skills",
    ]
```

## Forwarding Extra Arguments

Pass `--` after a single-command Poe task to forward extra flags to the underlying tool:

```bash
uv run poe test -- -k "test_greeting" -v
uv run poe lint -- --statistics
```

## Upstream Documentation

- [Poe the Poet Documentation](https://poethepoet.natn.io/)
- [Poe the Poet GitHub Repository](https://github.com/nat-n/poethepoet)
