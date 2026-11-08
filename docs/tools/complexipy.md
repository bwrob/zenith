---
diataxis: reference
purpose: Document cognitive complexity measurement, threshold scoring, and function refactoring with complexipy.
---

# Complexipy: Cognitive Complexity

[![Tool: complexipy](https://img.shields.io/badge/complexity-complexipy-crimson.svg)](https://github.com/rohaquinlop/complexipy)

`complexipy` is a Rust-based cognitive complexity analyzer for Python. Unlike cyclomatic
complexity (which counts linear branches equally), cognitive complexity penalizes deeply
nested control structures (`if`, `for`, `while`, `try/except`), recursion, and mixed
boolean operator chains.

Zenith enforces a strict ceiling of **`max-complexity-allowed = 10`** per function or
method across both `src/` and `tests/`.

## Configuration in Zenith

Configured in `complexipy.toml` at the project root:

```python exec="1" result="toml"
import re
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/complexipy.toml")
if not path.exists():
    path = Path("complexipy.toml")
text = path.read_text(encoding="utf-8")
text = re.sub(r"^# =+[^\n]*\n(?:#[^\n]*\n)*# =+[^\n]*\n+", "", text)
print(text.strip())
```

## Reducing Complexity Above 10

When a function exceeds a score of 10:

1. **Replace nested `if/else` blocks with guard clauses** (early `return` or `raise`).
2. **Extract inner loop bodies** into small, pure helper functions.
3. **Replace long `if/elif` chains** with a dictionary dispatch table or `match/case`.

## Key Invocations

```bash
uv run poe complexity          # Run complexipy src tests (fails if any function > 10)
uv run complexipy src tests    # Direct CLI invocation
```

## Upstream Documentation

- [complexipy GitHub Repository](https://github.com/rohaquinlop/complexipy)
- [Cognitive Complexity Whitepaper](https://www.sonarsource.com/resources/cognitive-complexity/)
