# mutmut: Fast Mutation Testing

[![Tool: mutmut](https://img.shields.io/badge/mutation-mutmut-orange.svg)](https://mutmut.readthedocs.io/)

`mutmut` is a fast mutation testing framework for Python. It introduces deliberate modifications into the Abstract Syntax Tree (AST) of source code and executes the test suite against each mutation to verify whether existing tests actively catch the introduced defects.

---

## What It Does

Traditional code coverage only measures which lines of code were executed during a test run; it cannot determine whether tests contain meaningful assertions. A test suite can reach 100% line coverage while asserting nothing.

`mutmut` modifies Python AST trees directly in memory and source files, applying microscopic mutations such as swapping relational operators (`<` to `<=`), replacing boolean constants, mutating numbers, or removing function calls. It then runs targeted `pytest` executions against each mutant. When a mutant causes a test failure, it is marked as killed; when all tests pass despite the mutation, the mutant is flagged as surviving, revealing an untested boundary condition.

---

## Why It's in Zenith

Zenith integrates mutation testing to prevent test suites from becoming superficial coverage checklists. Autonomous AI coding agents frequently generate tests that achieve high line coverage while failing to assert critical invariants. Mutation testing acts as a mechanical verification gate that ensures tests assert behavior rather than merely execute paths.

Zenith provides `mutmut` as the primary mutation testing tool for rapid, day-to-day developer and AI agent iteration loops. Running `uv run poe test-mutation` evaluates code in seconds, allowing developers to inspect surviving mutants immediately and strengthen assertions before opening a pull request.

> [!WARNING] Platform Compatibility: Windows Limitation
> `mutmut` relies on POSIX process mechanics and filesystem assumptions that cause it to fail or behave unreliably on Windows environments.
>
> On Windows workstations and cross-platform continuous integration matrix runners, use **[Cosmic Ray](cosmic-ray.md)** via `uv run poe test-mutation-cosmic`. On macOS and Linux, `mutmut` provides the fastest local mutation feedback loop.

---

## Dual Mutation Strategy: mutmut vs Cosmic Ray

Zenith includes both `mutmut` and `cosmic-ray` because they serve complementary roles across developer workflows and platforms:

| Capability | `mutmut` | `cosmic-ray` |
|---|---|---|
| **Primary Role** | Fast local developer TDD loops | Exhaustive distributed CI campaigns |
| **Execution Model** | Direct AST mutation with local cache | SQLite-backed task distribution |
| **Windows Support** | ❌ Not supported (fails on Windows) | ✅ Fully supported across all OS platforms |
| **Execution Speed** | Sub-second to minutes | Minutes to hours (deep matrix runs) |
| **Task Runner Command** | `uv run poe test-mutation` | `uv run poe test-mutation-cosmic` |
| **Best Used By** | Developers & AI agents pre-commit (macOS/Linux) | Scheduled CI governance & Windows developers |

---

## Configuration in Zenith

Configured in `pyproject.toml` under the `[tool.mutmut]` table:

```python exec="1" result="toml"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/pyproject.toml")
if not path.exists():
    path = Path("pyproject.toml")
content = path.read_text()
if "[tool.mutmut]" in content:
    start = content.index("[tool.mutmut]")
    end = content.find("\n[", start + 1)
    print(content[start : end if end != -1 else len(content)].strip())
```

---

## Key Invocations

```bash
# Run fast mutation analysis across package source
uv run poe test-mutation

# Inspect surviving mutants with diff view
uv run mutmut show <mutant_id>

# Generate interactive HTML report of mutation coverage
uv run mutmut html
```

---

## Upstream Documentation

For extended configuration options and mutant survival analysis, consult the [mutmut documentation](https://mutmut.readthedocs.io/) and the [mutmut GitHub repository](https://github.com/boxed/mutmut).
