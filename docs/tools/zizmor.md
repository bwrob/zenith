---
diataxis: reference
purpose: Document GitHub Actions static security auditing and pipeline risk analysis with zizmor.
---

# Zizmor: CI Security Static Analysis

[![Tool: zizmor](https://img.shields.io/badge/security-zizmor-red.svg)](https://woodruffw.github.io/zizmor/)

`zizmor` is a Rust-based static security analyzer for GitHub Actions workflows
(`.github/workflows/*.yaml`). It detects script injection vulnerabilities (unquoted
`${{ github.event.* }}` interpolations inside `run:` blocks), overly broad
`permissions:` scopes, dangerous `pull_request_target` checkouts, and cache poisoning
vectors.

Zenith runs `zizmor` in `--pedantic` mode (`--min-severity informational`) as part of
`uv run poe code-quality` and CI quality gates.

## Configuration in Zenith

Configured in `.zizmor.yml` at the project root:

```python exec="1" result="yaml"
import re
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/.zizmor.yml")
if not path.exists():
    path = Path(".zizmor.yml")
text = path.read_text(encoding="utf-8")
text = re.sub(r"^# =+[^\n]*\n(?:#[^\n]*\n)*# =+[^\n]*\n+", "", text)
print(text.strip())
```

And wired in `poe_tasks.toml`:

```toml
[tasks.zizmor]
    cmd  = "zizmor --config .zizmor.yml --pedantic --min-severity informational .github/workflows"
    help = "Audit GitHub Actions workflows for security vulnerabilities with zizmor."
```

> [!NOTE]
> **Why `unpinned-uses` Is Disabled by Default**: Scaffolded workflows pin actions to
> version tags (such as `actions/checkout@v6`) so Dependabot can update them cleanly. If
> your organization mandates full 40-character commit SHA pinning for third-party
> actions, remove the `unpinned-uses` block from `.zizmor.yml`.

## Key Invocations

```bash
# Run pedantic audit via Poe
uv run poe zizmor

# Direct CLI invocation
uv run zizmor --config .zizmor.yml --pedantic --min-severity informational .github/workflows
```

## Upstream Documentation

- [zizmor Official Documentation](https://woodruffw.github.io/zizmor/)
- [zizmor GitHub Repository](https://github.com/woodruffw/zizmor)
- [GitHub Actions Security Hardening Guide](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
