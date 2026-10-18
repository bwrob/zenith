# Pyrefly: Static Type Checking

[![Tool: Pyrefly](https://img.shields.io/badge/types-pyrefly%20strict-blueviolet.svg)](https://github.com/facebook/pyrefly)

`Pyrefly` is Meta's next-generation static type checker for Python written in Rust. It provides high-speed type inference, strict sound type validation, and native support for modern Python 3.12+ type system syntax.

---

## What It Does

Pyrefly validates type soundness across Python codebases by evaluating Abstract Syntax Trees in Rust. It natively supports modern Python 3.12+ features—including PEP 695 generic syntax (`def get_item[T](items: list[T]) -> T:`), type aliases, and structural subtyping through `typing.Protocol` without requiring inheritance.

By validating function boundaries at compile time, Pyrefly catches missing type annotations, implicit dynamic conversions, and unsafe coercions with instant feedback.

---

## Why It's in Zenith

Zenith runs Pyrefly in its highest-assurance configuration (`preset = "strict"`). This eliminates implicit `Any` and ensures that every public interface, parameter, and return value is explicitly typed and sound.

Autonomous AI agents frequently introduce loose type annotations or unconstrained generics when generating code. Operating Pyrefly in strict mode acts as an automated anti-hallucination guardrail, blocking untyped code from passing quality gates before human review.

---

## Configuration in Zenith

Configured in `pyrefly.toml` at the project root:

```python exec="1" result="toml"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/pyrefly.toml")
if not path.exists():
    path = Path("pyrefly.toml")
print(path.read_text().strip())
```

### Strict Mode Invariants

Under strict mode, all function parameters and return types must be fully annotated. Implicit `Any` inference is strictly prohibited, structural protocols are validated at call sites, and any untyped third-party libraries require explicit stub declarations or typed wrappers.

---

## Key Invocations

```bash
uv run pyrefly check           # Run static type analysis across project
uv run poe type-check          # Wired task in Poe development pipeline
```

---

## Upstream Documentation

- [Pyrefly GitHub Repository](https://github.com/facebook/pyrefly)
- [Python Typing Documentation](https://docs.python.org/3/library/typing.html)
