---
description: >-
  Guide to maintain, test, and develop Cookiecutter templates with modern 2.x features.
  Use when editing template configurations, Jinja partials, lifecycle hooks, or running template tests.
  Triggers: cookiecutter, template, scaffold, hooks, cookiecutter.json.
name: tool-cookiecutter
version: 2.0.0
---

# Cookiecutter Template Engine (`tool-cookiecutter`)

`cookiecutter` is a command-line utility and Python library that scaffolds
projects from file templates with the Jinja templating engine.

In this repository, Cookiecutter defines the generation pipeline for the
**Zenith** Python template, targeting modern Cookiecutter 2.x (2.2+, 2.5+, 2.7+).

---

## 1. Repository Layout & Template Architecture

A modern Cookiecutter repository has five components:

```text
zenith/
├── cookiecutter.json               # Template configuration, variables, __prompts__, _jinja2_env_vars
├── hooks/                          # Lifecycle scripts (Python / Shell)
│   ├── pre_gen_project.py          # Runs after questions, before render; validates prerequisites and inputs
│   └── post_gen_project.py         # Runs after generation; cleans conditional files, formats configs
├── templates/                      # (2.2+) Shared template partials (via Jinja include / extends)
│   ├── _header.md
│   └── _base_ci.yaml
├── local_extensions.py             # (2.1+) Local Jinja filter/tag extensions defined within template
└── {{cookiecutter.project_slug}}/  # Project source root; renders directory names and files via Jinja
```

---

## 2. Core CLI, Replay & Testing Commands

Use these commands to test template generation and check rendered projects:

```bash
uv run cookiecutter .                                  # Interactive generation test
uv run cookiecutter . --no-input                       # Headless generation with default values
uv run cookiecutter . --no-input -o /tmp/test          # Render into specific output dir
uv run cookiecutter . --no-input -f                    # Overwrite output directory if it exists
uv run cookiecutter . --replay                         # Re-generate using cached replay values
uv run cookiecutter . --replay-file /path/to/replay.json # Generate from a specific replay file
uv run pytest                                          # Run template unit & validation test suite
```

### Programmatic Python Invocation

Use Cookiecutter's Python API to test templates programmatically:

```python
from pathlib import Path
from cookiecutter.exceptions import FailedHookException
from cookiecutter.main import cookiecutter

project_dir = Path(
    cookiecutter(
        template=".",
        no_input=True,
        output_dir="/tmp/output",
        extra_context={
            "project_name": "Demo App",
            "python_version": "3.13",
            "include_cli": True,
        },
    )
)
```

### End-to-End Smoke Test Workflow

Check that a generated project satisfies all quality gates:

```bash
# 1. Render template to a temporary directory
uv run cookiecutter . --no-input -o /tmp/smoke-test

# 2. Sync dependencies and run full quality and test suite
cd /tmp/smoke-test/zenith
uv sync
uv run poe code-quality
uv run poe test
uv run poe docs-build
```

---

## 3. Advanced `cookiecutter.json` Features

Cookiecutter provides built-in configuration directives in `cookiecutter.json`.

### A. Human-Readable Prompts (`__prompts__`)

Cookiecutter 2.2+ supports descriptive prompts through `__prompts__`.
The engine strips `__prompts__` from the rendered context:

```json
{
  "project_name": "Zenith",
  "license": ["MIT", "Apache-2.0", "BSD-3-Clause", "None"],
  "include_cli": true,
  "__prompts__": {
    "project_name": "Project Title (Human-readable):",
    "license": {
      "__prompt__": "Select an Open Source License:",
      "MIT": "MIT License (Permissive, widely adopted)",
      "Apache-2.0": "Apache 2.0 (Permissive with patent grant)",
      "BSD-3-Clause": "BSD 3-Clause (Permissive, attribution required)",
      "None": "Proprietary / No License (All Rights Reserved)"
    },
    "include_cli": "Scaffold Typer/Rich command-line interface?"
  }
}
```

### B. Native Boolean Variables

Cookiecutter 2.2.0+ supports native JSON booleans (`true` / `false`).
The interactive prompt checks user responses (`y/n/yes/no/true/false/1/0/on/off`).

- In `cookiecutter.json`:

  ```json
  {
    "include_cli": true,
    "include_ci_testing": true,
    "include_ci_publishing": true
  }
  ```

- In Jinja template files:

  ```jinja
  {% if cookiecutter.include_cli -%}
  dependencies = [ "rich>=14.0.0", "typer>=0.16.0" ]
  {%- endif %}
  ```

- In Python hooks (`hooks/post_gen_project.py`):

  ```python
  include_cli = "{{ cookiecutter.include_cli }}" in ("True", "true", "1")
  if not include_cli:
      remove_file("src", package_name, "cli.py")
  ```

### C. Private Variables (`_` unrendered vs `__` rendered)

- **Unrendered Private Variables (`_name`)**: Constants not prompted to the user and not rendered by Jinja. Useful for internal configurations, line endings, or copy lists:

  ```json
  {
    "_new_lines": "\n",
    "_copy_without_render": ["docs/assets/*", "*.svg", "*.png", "*.ico"]
  }
  ```

- **Rendered Private Variables (`__name`)**: Computed dynamically with Jinja from user inputs without prompting:

  ```json
  {
    "project_name": "Demo App",
    "__project_slug": "{{ cookiecutter.project_name | slugify }}",
    "__package_name": "{{ cookiecutter.__project_slug | replace('-', '_') }}"
  }
  ```

### D. Jinja2 Environment Tweaks (`_jinja2_env_vars`)

Configure whitespace trimming and template behavior directly:

```json
{
  "_jinja2_env_vars": {
    "lstrip_blocks": true,
    "trim_blocks": true
  }
}
```

- `lstrip_blocks`: Strips leading tabs and spaces from the start of a line to a block.
- `trim_blocks`: Strips the first newline after a block tag (`{% ... %}`).
  *Caveat*: `trim_blocks: true` also strips newlines after inline block tags at the end of a line (for example, `url: {% raw %}${{ ... }}{% endraw %}` in YAML workflows). This behavior collapses subsequent lines. In templates with inline raw blocks, use `lstrip_blocks: true` alone.

### E. Deterministic Line Endings (`_new_lines`)

Enforce POSIX LF line endings across all platforms to prevent git dirty working trees on Windows checkouts:

```json
{
  "_new_lines": "\n"
}
```

### F. Built-In & Custom Jinja Extensions (`_extensions`)

Cookiecutter includes five built-in extensions in `StrictEnvironment`:

1. `cookiecutter.extensions.SlugifyExtension`: `{{ cookiecutter.name | slugify }}` or `| slugify(separator='_')`
2. `cookiecutter.extensions.TimeExtension`: `{% now 'utc', '%Y' %}` (dynamic current year in `LICENSE` and docs)
3. `cookiecutter.extensions.UUIDExtension`: `{{ uuid4() }}`
4. `cookiecutter.extensions.RandomStringExtension`: `{{ random_ascii_string(16) }}`
5. `cookiecutter.extensions.JsonifyExtension`: `{{ cookiecutter.mapping | jsonify }}`

Register external Jinja extensions in `_extensions`:

```json
{
  "_extensions": [
    "jinja2.ext.do",
    "jinja2.ext.loopcontrols"
  ]
}
```

### G. Local Template Extensions (`local_extensions.py`)

Cookiecutter 2.1+ loads custom filters from `local_extensions.py` in the template root:

```python
# local_extensions.py
from cookiecutter.utils import simple_filter


@simple_filter
def sanitize_python_identifier(value: str) -> str:
    """Ensure value is a safe, valid Python identifier."""
    import re

    cleaned = re.sub(r"\W|^(?=\d)", "_", value.lower())
    return cleaned.strip("_")
```

Register it in `cookiecutter.json`:

```json
{
  "_extensions": ["local_extensions.sanitize_python_identifier"]
}
```

### H. Template Inheritance & Partials (`templates/` folder)

Cookiecutter 2.2+ adds `templates/` to Jinja's `FileSystemLoader`:

```text
cookiecutter-repo/
├── templates/
│   ├── _badge_ci.md
│   └── _base_license.txt
└── {{cookiecutter.project_slug}}/
    └── README.md   # Uses {% include "_badge_ci.md" %}
```

---

## 4. Hook Lifecycle Architecture & Execution Context

Cookiecutter supports three distinct lifecycle hooks:

| Hook | Timing | Working Directory | Context Available | Primary Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **`pre_gen_project.py`** | After questions, before files render | Generated project directory | Yes (rendered) | Check system prerequisites (`uv`, `git`, Python) and input variables |
| **`post_gen_project.py`** | After file rendering | Generated project directory | Yes (rendered) | File pruning, educational header stripping, git init |

> [!NOTE]
> Cookiecutter 2.4+ supports `pre_prompt.py`.
> However, it copies the full repository (including `.venv` and `.git`) before prompts.
> This copy creates high I/O overhead on local checkouts.
> Keep prerequisite checks in `pre_gen_project.py` instead.

### Hook Error Handling

If a hook exits with a non-zero code (`sys.exit(1)`), Cookiecutter halts generation and deletes the directory.

---

## 5. Best Practices & Zenith Rules

Follow these principles when developing the template:

- **Edit template, never rendered output**: Always make changes inside
  `{{cookiecutter.project_slug}}/` or `templates/`, not in temporary test output.
- **Escape Literal Jinja & Workflow Expressions**: When rendering GitHub Actions (`${{ github.sha }}`) or Jinja docs, wrap expressions in `{% raw %}...{% endraw %}`.
- **Maintain Formatting Resilience**: Expressions like `{{ cookiecutter.project_slug }}` vary in character length. Parenthesize lines in Python template code so `ruff format` does not fail on longer names.
- **Header Stripping Synchronization**: Zenith includes educational comments in config files that `hooks/post_gen_project.py` strips out. Keep `CONFIG_FILES_WITH_HEADERS` synchronized when adding new root configs.
- **Binary & Asset Protection**: Always register static binary and SVG assets in `_copy_without_render`.
- **Maintain Test Coverage**: Maintain test cases in `tests/test_template.py` covering boolean flags, Python versions, and licenses.
