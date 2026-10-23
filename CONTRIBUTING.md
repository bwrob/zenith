# Contributing to Zenith

Thank you for helping improve the **Zenith** template repository!

## 1. Principles & Policies

- **AI Policy**: Read and adhere to [AI_POLICY.md](AI_POLICY.md). All AI-generated
  contributions require local verification, human accountability, and transparent
  disclosure.
- **Agent Instructions**: Coding assistants must follow [AGENTS.md](AGENTS.md).
- **Code of Conduct**: Treat all contributors respectfully in accordance with our
  [Code of Conduct](CODE_OF_CONDUCT.md).

## 2. Environment & Testing

Zenith uses `uv` and `poethepoet`:

```bash
# Clone and setup
git clone https://github.com/bwrob/zenith.git
cd zenith
uv sync

# Run tests validating template generation
uv run poe test

# Run code quality verification
uv run poe code-quality

# Auto-fix formatting and linting
uv run poe fix
```

## 3. Pull Requests

1. Create a dedicated branch (`feat/<name>`, `fix/<name>`, etc.).
2. Follow Conventional Commits (`feat(skills): add adr skill`).
3. Credit AI assistants using `Co-authored-by` trailers.
4. Ensure all unit and template generation tests pass locally before submitting.
