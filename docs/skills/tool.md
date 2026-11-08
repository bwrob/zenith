---
diataxis: reference
purpose: Catalog developer tool skills, command syntax runbooks, and configuration mechanics across the Zenith stack.
---

# Tool Skills

The **`tool-*`** skills in `.agents/skills/tool-*/SKILL.md` give AI coding agents
verified CLI flags, configuration file paths, and Poe task aliases for the tools in the
Zenith stack. Loading a `tool-*` skill on demand prevents agents from inventing
non-existent flags, writing `[tool.*]` blocks into the wrong config file, or invoking
tools outside `uv run`.

For detailed human documentation on how each tool is configured in Zenith, follow the
links in the **Tool Reference** column below.

## Build & Workflow Tool Skills

| Skill               | Target Config File                | Primary Grounded Commands & Poe Tasks                                      | Tool Reference                           |
| :------------------ | :-------------------------------- | :------------------------------------------------------------------------- | :--------------------------------------- |
| `tool-uv`           | `pyproject.toml`, `uv.lock`       | `uv sync`, `uv add`, `uv lock`, `uv run`, `uv build`, `uv run poe audit`   | [uv](../tools/uv.md)                     |
| `tool-poethepoet`   | `poe_tasks.toml`                  | `uv run poe test`, `uv run poe code-quality`, `uv run poe fix`             | [Poe the Poet](../tools/poethepoet.md)   |
| `tool-prek`         | `prek.toml`                       | `uv run prek install`, `uv run prek run --all-files`, `uv run prek update` | [prek](../tools/prek.md)                 |
| `tool-typer`        | `src/<pkg>/cli.py`                | `uv run <project-slug> --help`, `CliRunner` testing patterns               | [Typer](../tools/typer.md)               |
| `tool-cookiecutter` | `cookiecutter.json`, `hooks/*.py` | `uvx zenith-template`, `cookiecutter .` *(upstream template repo only)*    | [Cookiecutter](../tools/cookiecutter.md) |

## Code Quality, Typing & Architecture Tool Skills

| Skill             | Target Config File                | Primary Grounded Commands & Poe Tasks                                         | Tool Reference                       |
| :---------------- | :-------------------------------- | :---------------------------------------------------------------------------- | :----------------------------------- |
| `tool-ruff`       | `ruff.toml`                       | `uv run poe lint`, `uv run poe format`, `# ruff: ignore[rule-name]` rules     | [Ruff](../tools/ruff.md)             |
| `tool-pyrefly`    | `pyrefly.toml`                    | `uv run poe type-check`, `uv run poe type-coverage`                           | [Pyrefly](../tools/pyrefly.md)       |
| `tool-tach`       | `tach.toml`                       | `uv run tach check`, `uv run poe dependencies`, `uv run poe dependency-graph` | [Tach](../tools/tach.md)             |
| `tool-complexipy` | `complexipy.toml`                 | `uv run poe complexity` (`max-complexity-allowed = 10`)                       | [complexipy](../tools/complexipy.md) |
| `tool-griffe`     | `poe_tasks.toml`, `zensical.toml` | `uv run poe check-api`, `uv run poe sdd-check-api <feature-id>`               | [Griffe](../tools/griffe.md)         |
| `tool-typos`      | `typos.toml`                      | `uv run poe typos`, `uv run poe typos-fix`                                    | [typos](../tools/typos.md)           |

## Testing, Coverage & Security Tool Skills

| Skill             | Target Config File                 | Primary Grounded Commands & Poe Tasks                                 | Tool Reference                       |
| :---------------- | :--------------------------------- | :-------------------------------------------------------------------- | :----------------------------------- |
| `tool-pytest`     | `pytest.ini`                       | `uv run poe test`, `uv run poe test-fast`, `uv run poe test-lowest`   | [pytest](../tools/pytest.md)         |
| `tool-coverage`   | `.coveragerc`                      | `uv run poe test`, `uv run poe coverage`, `uv run coverage report -m` | [Coverage.py](../tools/coverage.md)  |
| `tool-mutmut`     | `pyproject.toml` (`[tool.mutmut]`) | `uv run poe test-mutation`, `uv run mutmut show <id>` *(macOS/Linux)* | [mutmut](../tools/mutmut.md)         |
| `tool-cosmic-ray` | `cosmic-ray.toml`                  | `uv run poe test-mutation-cosmic`, `uv run cr-report session.sqlite`  | [Cosmic Ray](../tools/cosmic-ray.md) |
| `tool-zizmor`     | `.zizmor.yml`                      | `uv run poe zizmor` (pedantic audit of `.github/workflows`)           | [zizmor](../tools/zizmor.md)         |

## Documentation & Formatting Tool Skills

| Skill           | Target Config File              | Primary Grounded Commands & Poe Tasks                    | Tool Reference                   |
| :-------------- | :------------------------------ | :------------------------------------------------------- | :------------------------------- |
| `tool-zensical` | `zensical.toml`                 | `uv run poe docs-serve`, `uv run poe docs-build`         | [Zensical](../tools/zensical.md) |
| `tool-rumdl`    | `rumdl.toml`                    | `uv run poe lint-md`, `uv run poe format-md`             | [rumdl](../tools/rumdl.md)       |
| `tool-taplo`    | `.taplo.toml`                   | `uv run poe format-toml`, `uv run poe format-check-toml` | [Taplo](../tools/taplo.md)       |
| `tool-prettier` | `.prettierrc.yaml`, `prek.toml` | `uv run poe format-yaml`, `uv run poe format-css`        | [Prettier](../tools/prettier.md) |
| `tool-typst`    | `docs/assets/*.typ`             | `uv run poe docs-logo`, `uv run typst compile`           | [Typst](../tools/typst.md)       |
| `tool-termynal` | `zensical.toml`                 | `<!-- termynal -->` fenced `console` blocks              | [Termynal](../tools/termynal.md) |

## Syncing & Adding Custom Tool Skills

To pull pre-built agent skills from installed third-party Python libraries into
`.agents/skills/`, run:

```bash
uv run poe sync-skills
```

When your project adopts an external tool or framework that does not ship its own skill
(for example, Docker, Alembic, or Playwright), scaffold a custom `tool-<name>` skill
following
[`workflow-skill-creator`](workflow.md#skill-authoring-workflow-skill-creator):

```bash
mkdir -p .agents/skills/tool-docker/{templates,references}
```
