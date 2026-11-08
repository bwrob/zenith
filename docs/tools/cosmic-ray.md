---
diataxis: reference
purpose: Document mutation testing and database-backed test suite verification with Cosmic Ray.
---

# Cosmic Ray: Mutation Testing

[![Tool: Cosmic Ray](https://img.shields.io/badge/testing-cosmic--ray-darkred.svg)](https://cosmic-ray.readthedocs.io/)

`Cosmic Ray` is a cross-platform AST mutation testing engine that records mutant
campaigns in an SQLite session database (`session.sqlite`). Unlike
**[mutmut](mutmut.md)** (which requires POSIX `fork` on macOS/Linux), Cosmic Ray runs on
Linux, macOS, and Windows, and allows large mutation sessions to be paused, resumed, and
inspected with `cr-report`.

See
[Dual Mutation Strategy (`mutmut` vs. `cosmic-ray`)](mutmut.md#dual-mutation-strategy-mutmut-vs-cosmic-ray)
for when to use each tool.

## Configuration in Zenith

Configured in `cosmic-ray.toml` at the project root:

```python exec="1" result="toml"
import re
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/cosmic-ray.toml")
if not path.exists():
    path = Path("cosmic-ray.toml")
text = path.read_text(encoding="utf-8")
text = re.sub(r"^# =+[^\n]*\n(?:#[^\n]*\n)*# =+[^\n]*\n+", "", text)
text = text.replace("{{ cookiecutter.package_name }}", "my_project")
print(text.strip())
```

## Key Invocations

```bash
# Run full init -> exec -> report sequence via Poe
uv run poe test-mutation-cosmic

# Or run individual Cosmic Ray steps manually
uv run cosmic-ray init cosmic-ray.toml session.sqlite
uv run cosmic-ray exec session.sqlite
uv run cr-report session.sqlite
```

## Upstream Documentation

- [Cosmic Ray Documentation](https://cosmic-ray.readthedocs.io/)
- [Cosmic Ray GitHub Repository](https://github.com/sixty-north/cosmic-ray)
