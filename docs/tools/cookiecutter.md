---
diataxis: reference
purpose: Document template variables, lifecycle hooks, and project generation mechanics with Cookiecutter.
---

# Cookiecutter: Templating Engine

[![Tool: Cookiecutter](https://img.shields.io/badge/template-cookiecutter-D4B830.svg)](https://github.com/cookiecutter/cookiecutter)

`Cookiecutter` is the Jinja2-based project templating engine underneath Zenith. You can
scaffold a Zenith project either through the interactive Textual wizard
(`uvx zenith-template`, which wraps Cookiecutter's Python API) or directly via the
`cookiecutter` CLI.

## Lifecycle Hooks in Zenith

Zenith uses two lifecycle hooks in `hooks/`:

- **`hooks/pre_gen_project.py`**: Validates `project_slug`, `package_name` (PEP 8 Python
  identifier), `version` (PEP 440 / SemVer), and `python_version` before any files are
  written.
- **`hooks/post_gen_project.py`**: Strips `# ====` template header comments from
  generated config files, removes disabled optional components (`include_cli`,
  `include_docs`, `include_mutation_testing`, `include_ci_testing`,
  `include_ci_publishing`, `include_agent_skills`), and wires AI assistant symlinks and
  permission files based on `ai_tools`.

## Configuration in Zenith

Configured in `cookiecutter.json` at the repository root:

```python exec="1" result="json"
from pathlib import Path

print(Path("cookiecutter.json").read_text(encoding="utf-8").strip())
```

## Key Invocations

```bash
# Launch the interactive Textual wizard (recommended)
uvx zenith-template

# Run non-interactively with flags
uvx zenith-template --no-input --name "My Project" --sync

# Or render directly with Cookiecutter from GitHub
uvx cookiecutter https://github.com/bwrob/zenith.git
```

## Upstream Documentation

- [Cookiecutter Documentation](https://cookiecutter.readthedocs.io/)
- [Cookiecutter GitHub Repository](https://github.com/cookiecutter/cookiecutter)
