# Engineering & Prose Guides

While workflow skills define *what steps to take* and tool skills define *how to run
tools*, the **`guide-*`** skill suite establishes **normative qualitative standards**:
the core philosophy, architectural idioms, typing patterns, and prose rules that shape
every file in the repository.

AI coding assistants are trained on millions of public repositories, most of which
contain legacy Python (Python 3.8/3.9 idioms, mutable default arguments, deep
inheritance hierarchies, unconstrained `Any` types) and colloquial, ambiguous technical
writing. `guide-*` skills counteract this by grounding agents in Zenith's modern,
opinionated engineering philosophy.

## Core Template Guides

These guides define the default engineering and writing standards for generated
projects.

### Modern Python 3.12+ Engineering (guide-python)

**What it is**: The definitive engineering style guide for Python 3.12+ code in Zenith.
It codifies architectural invariants around type parameter syntax, structural subtyping,
immutability, and module purity.

**Why it's in Zenith**: Python has undergone a profound modernization with releases 3.12
and 3.13. Modern Python offers first-class generic parameter syntax, high-speed type
inference via Meta Pyrefly, and clean structural protocols. Without an explicit guide,
AI models routinely generate legacy code: defining old-style `TypeVar('T')`, nesting
deep object-oriented class hierarchies, importing `typing.List` or `typing.Dict`, or
using mutable dataclasses that introduce race conditions.

`guide-python` establishes five non-negotiable architectural pillars:

1. **PEP 695 Generics Syntax**: Replaces verbose `TypeVar` declarations and `Union`
   wrappers with clean modern syntax:

   ```python
   from collections.abc import Callable

   type JsonScalar = str | int | float | bool | None
   type Json = dict[str, Json] | list[Json] | JsonScalar


   # Modern Zenith idiom
   def transform[T](items: list[T], operation: Callable[[T], T]) -> list[T]: ...
   ```

2. **Composition Over Inheritance**: Avoids rigid inheritance hierarchies in favor of
   shallow composition and structural subtyping using `typing.Protocol`. Classes define
   what they do via behavioral interfaces rather than shared ancestry.
3. **Frozen Slots Dataclasses**: Mandates `@dataclass(frozen=True, slots=True)` for
   domain entities and value objects. This provides immutability by default, prevents
   accidental attribute assignment, and optimizes runtime memory layout.
4. **Absolute Imports Only**: Prohibits ambiguous relative imports
   (`from .core import x`). All module references use absolute package namespaces
   (`from my_package.core import x`), simplifying refactoring, layer verification in
   Tach, and AST static analysis.
5. **Strict Encoding Hygiene**: Eliminates subtle platform-specific encoding bugs by
   requiring explicit `encoding="utf-8"` in all file read/write operations and
   subprocess calls.

### Simplified Technical English (guide-ste100)

**What it is**: The writing guide and automated linter implementing the international
Simplified Technical English standard (ASD-STE100 Issue 8).

**Why it's in Zenith**: Ambiguity in technical documentation and agent prompts is the
number one cause of AI execution failures. When prompts or tool docstrings use modal
verbs ("you could check this") or words with multiple meanings ("address the bug", "run
the build"), LLMs often hallucinate alternate interpretations or skip verification steps
entirely.

ASD-STE100 solves this through controlled language principles:

- **One Meaning Per Word**: Restricts words to a single approved meaning per part of
  speech, eliminating polysemy and semantic confusion.
- **Active Voice & Imperative Verbs**: Replaces passive constructions ("the tests should
  be run") with direct, clear instructions ("Run the unit test suite with `poe test`").
- **Strict Sentence Length Limits**: Caps procedural instructions at 20 words and
  descriptive sentences at 25 words to prevent model attention degradation.
- **Automated Verification**: Zenith includes a standalone, standard-library Python
  linter and auto-fixer (`ste-lint.py`). Run `uv run poe lint-ste` to audit skills and
  documentation against STE-100 vocabulary and structure rules.

## Authoring Custom Guide Skills

As your project grows, your team will develop project-wide patterns for API design,
database queries, or error handling. Codify them under the `guide-*` prefix so agents
natively adhere to your team's architectural decisions:

```bash
mkdir -p .agents/skills/guide-api-design
```

Common examples created in Zenith projects:

- **`guide-api-design`**: RESTful resource conventions, pagination envelopes, and HTTP
  status code standards.
- **`guide-error-handling`**: Domain exception hierarchies, retry policies with jitter,
  and structured logging context schemas.
- **`guide-security`**: Cryptographic key rotation, input sanitization rules, and OWASP
  mitigation strategies.
