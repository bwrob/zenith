---
diataxis: reference
purpose: Document cognitive complexity measurement, threshold scoring, and function refactoring with complexipy.
---

# Complexipy: Cognitive Complexity

[![Tool: complexipy](https://img.shields.io/badge/complexity-complexipy-crimson.svg)](https://github.com/rohaquinlop/complexipy)

`complexipy` is an extremely fast cognitive complexity analyzer for Python code written
in Rust. It measures how difficult functions and methods are for a human or AI agent to
read and understand.

## What It Does

Cognitive complexity measures the mental effort required to understand the control flow
of code. Unlike Cyclomatic Complexity, which simply counts independent linear execution
paths, Cognitive Complexity penalizes nested control structures, recursion, cascading
conditional ladders, and convoluted boolean expressions.

`complexipy` performs this analysis in milliseconds, generating detailed terminal
reports that pinpoint exact lines where cognitive overhead spikes.

## Why It Is in Zenith

Deeply nested logic and tangled branching are the primary sources of regression bugs in
production software. AI coding assistants frequently write deeply nested code when
attempting to patch complex functionality.

Zenith enforces a hard ceiling of **cognitive complexity <= 10** per function or method.
Functions exceeding 10 points fail CI immediately. This requirement prompts developers
and agents to refactor logic into composable functions with early returns or dispatch
tables.

## Configuration in Zenith

Configured in `complexipy.toml` at the project root:

```python exec="1" result="toml"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/complexipy.toml")
if not path.exists():
    path = Path("complexipy.toml")
print(path.read_text().strip())
```

### Complexity Threshold Guidelines

Scores between 1 and 5 indicate simple, easily testable logic. Scores between 6 and 10
represent acceptable complexity for orchestration or algorithm dispatch. Any score above
10 is strictly prohibited in Zenith and must be refactored via helper extraction or
dispatch logic.

## Key Invocations

```bash
uv run complexipy src tests    # Run cognitive complexity analysis
uv run poe complexity          # Wired development task in Poe
```

## Upstream Documentation

- [complexipy GitHub Repository](https://github.com/rohaquinlop/complexipy)
- [Cognitive Complexity Whitepaper](https://www.sonarsource.com/resources/cognitive-complexity/)
