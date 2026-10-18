# Guides

The **`guide-*`** skill group establishes engineering conventions, architectural invariants, coding paradigms, and prose standards that dictate **how** code and technical text must be authored in the repository.

Unlike `workflow-*` skills (which define sequential operational procedures) or `tool-*` skills (which define tool syntax), `guide-*` skills establish **normative qualitative standards**.

---

## Template Guide Skills

### `guide-python`
- **Directory**: `.agents/skills/guide-python/`
- **Triggers**: `python style`, `pep 695`, `protocols`, `dataclasses`, `typing`, `refactor`.
- **Purpose**: Establishes modern, high-assurance Python coding standards across the codebase:
  - **PEP 695 Type Parameter Syntax**: Mandates modern generic syntax (`def func[T](val: T) -> T:` and `type Vector = list[float]`) over legacy `TypeVar` and `Union`.
  - **Composition Over Inheritance**: Favors shallow composition, structural subtyping (`typing.Protocol`), and pure function pipelines over deep object-oriented inheritance trees.
  - **Frozen Slots Dataclasses**: Requires `@dataclass(frozen=True, slots=True)` for domain models and immutable value objects.
  - **Absolute Imports Mandate**: Prohibits ambiguous relative imports (`from .core import x`), enforcing absolute package imports across all modules.
  - **Strict Encoding Hygiene**: Requires explicit UTF-8 encoding in all file operations (`open("file.txt", "r", encoding="utf-8")`).

---

### `guide-ste100`
- **Directory**: `.agents/skills/guide-ste100/`
- **Triggers**: `disambiguate`, `STE100 rewrite`, `apply Simplified Technical English`, `controlled-language rewrite`.
- **Purpose**: Enforces the international Simplified Technical English standard (ASD-STE100 Issue 8) on technical text, tool descriptions, and agent-to-agent prompts:
  - **Restricts Vocabulary**: Restricts words to one approved meaning per part of speech to eliminate semantic ambiguity.
  - **Active Voice & Imperative Mood**: Replaces passive voice constructions with direct, unambiguous instructions.
  - **Sentence Length Limits**: Caps procedural instructions at 20 words and descriptive sentences at 25 words.
  - **Automated Mechanical Verification**: Includes a standard-library Python linter and auto-fixer (`ste-lint.py`) wired into `uv run poe lint-ste`.

---

## Custom Guide Skills

As projects scale, development teams naturally introduce domain-wide engineering conventions, architectural contracts, or security rules. Codify them under the `guide-*` prefix:

```bash
mkdir -p .agents/skills/guide-api-design
```

Common guide skills added to Zenith projects:
- **`guide-api-design`**: RESTful resource naming, pagination envelopes, error response models, and HTTP status codes.
- **`guide-error-handling`**: Custom domain exception hierarchies, retry policies, and logging context standards.
- **`guide-security`**: Cryptographic key handling, input sanitization, OWASP top 10 prevention, and authentication middleware.
- **`guide-database-patterns`**: Query optimization rules, transaction isolation boundaries, and connection pooling conventions.
