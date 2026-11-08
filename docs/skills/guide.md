---
diataxis: reference
purpose: Prescribe Python 3.12+ engineering invariants, strict typing paradigms, and ASD-STE100 technical writing standards.
---

# Engineering & Prose Guides

While `workflow-*` skills define operational steps and `tool-*` skills document CLI
mechanics, the **`guide-*`** skills set the code and prose standards that apply across
the repository. Both `guide-python` and `guide-ste100` are **mandatory** skills that
agents load automatically whenever they edit Python code, docstrings, or agent skills.

## Modern Python 3.12+ Engineering (guide-python)

Defines the Python style, typing, and architecture conventions enforced in Zenith
projects:

1. **PEP 695 Generic Syntax**: Uses native `def func[T](...)` and `type Alias = ...`
   declarations instead of legacy `typing.TypeVar` or `typing.TypeAlias`:

   ```python
   from __future__ import annotations

   from typing import TYPE_CHECKING

   if TYPE_CHECKING:
       from collections.abc import Callable

   type JsonScalar = str | int | float | bool | None
   type Json = dict[str, Json] | list[Json] | JsonScalar


   def transform[T](items: list[T], operation: Callable[[T], T]) -> list[T]:
       """Apply *operation* to each element in *items*."""
       return [operation(item) for item in items]
   ```

2. **Composition Over Inheritance**: Uses `typing.Protocol` for structural subtyping and
   shallow composition instead of deep class inheritance hierarchies.
3. **Frozen Slotted Dataclasses**: Models domain entities and value objects with
   `@dataclass(frozen=True, slots=True)` for immutability and compact memory layout.
4. **Absolute Imports & Deferred Annotations**: Requires
   `from __future__ import annotations` at the top of every module, imports collection
   ABCs from `collections.abc`, and bans relative imports
   (`ban-relative-imports = "all"`).
5. **Explicit UTF-8 Encoding & Rule-Scoped Suppressions**: Requires explicit
   `encoding="utf-8"` on file and subprocess I/O, forbids bare `# noqa` comments in
   favor of `# ruff: ignore[full-rule-name]` with a rationale comment, and requires 100%
   Pyrefly strict type coverage.

## Simplified Technical English (guide-ste100)

Enforces Simplified Technical English (ASD-STE100 Issue 8) across **agent skills**
(`.agents/skills/`) and **Python docstrings** so autonomous agents can parse procedural
rules without ambiguity:

- **One meaning per word**: Avoids ambiguous modal verbs ("might", "should", "may") and
  polysemous words in procedural instructions.
- **Active voice and imperative mood**: Uses direct imperatives ("Run
  `uv run poe test`") instead of passive constructions ("The test suite can be executed
  by...").
- **Sentence length limits**: Caps procedural sentences at 20 words and descriptive
  sentences at 25 words in skill files.
- **Automated linter (`poe lint-ste`)**: Runs
  `.agents/skills/guide-ste100/scripts/ste-lint.py .agents/skills` as part of skill
  verification.

> [!NOTE]
> **Scope of ASD-STE100**: `poe lint-ste` enforces ASD-STE100 strictly on
> `.agents/skills/` and Python docstrings. User-facing documentation in `docs/` is
> governed by
> [`workflow-docs-authoring`](workflow.md#documentation-authoring-workflow-docs-authoring)
> and prioritizes natural human readability rather than rigid STE-100 rules.

## Creating Custom Guide Skills

To codify team-wide engineering standards (such as REST API conventions, error-handling
hierarchies, or SQL query rules), create a `guide-<name>` skill:

```bash
mkdir -p .agents/skills/guide-api-design/{references,examples}
```

Register the new skill in `AGENTS.md` and validate it with `uv run poe lint-ste` and
`uv run poe check-skills`.
