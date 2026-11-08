---
diataxis: reference
purpose: Document 100% statement and branch coverage enforcement and report analysis with Coverage.py.
---

# Coverage.py: Code Coverage

[![Tool: Coverage.py](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://coverage.readthedocs.io/)

`Coverage.py` measures statement and conditional branch coverage across both
`src/<package_name>` and `tests`. Zenith sets `branch = true` and `fail_under = 100` in
`.coveragerc`, and enables subprocess and `_exit` patching (`patch = subprocess _exit`)
so child-process CLI calls are tracked accurately.

## Configuration in Zenith

Configured in `.coveragerc` at the project root:

```python exec="1" result="ini"
import re
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/.coveragerc")
if not path.exists():
    path = Path(".coveragerc")
text = path.read_text(encoding="utf-8")
text = re.sub(r"^# =+[^\n]*\n(?:#[^\n]*\n)*# =+[^\n]*\n+", "", text)
text = text.replace("{{ cookiecutter.package_name }}", "my_project")
print(text.strip())
```

## Built-in Exclusions & Pragmatic Overrides

- **Pre-configured `exclude_also` patterns**: Non-executable typing constructs
  (`if TYPE_CHECKING:`, `Protocol` classes, `@abstractmethod`, `@overload`),
  unreachable exhaustiveness checks (`assert_never`, `raise NotImplementedError`,
  `return NotImplemented`), and `if __name__ == "__main__":` guards are excluded
  automatically.
- **Targeted exclusions (`# pragma: no cover` / `# pragma: no branch`)**: For
  OS-specific branches (such as `if sys.platform == "win32":`) that only execute on one
  platform, add `# pragma: no cover` or `# pragma: no branch`.
- **Adjusting the coverage threshold**: For hardware-interfacing or early prototype
  projects where 100% coverage is impractical, adjust `fail_under` under `[report]` in
  `.coveragerc`.

## Key Invocations

```bash
uv run poe test              # Run pytest with terminal missing-line and XML coverage reports
uv run poe coverage          # Generate interactive HTML report in htmlcov/index.html
uv run coverage report -m    # Print missing lines and partial branches from last run
```

## Upstream Documentation

- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Coverage.py GitHub Repository](https://github.com/nedbat/coveragepy)
