---
diataxis: reference
purpose: Document GitHub Actions static security auditing and pipeline risk analysis with zizmor.
---

# Zizmor: CI Security Static Analysis

[![Tool: zizmor](https://img.shields.io/badge/security-zizmor-red.svg)](https://woodruffw.github.io/zizmor/)

`zizmor` is a static security analysis tool for GitHub Actions CI/CD workflows written
in Rust by William Woodruff.

## What It Does

`zizmor` parses GitHub Actions YAML workflow manifests to detect security
vulnerabilities, insecure patterns, and potential attack vectors. It identifies
unescaped context interpolations that expose steps to script injection. It flags
missing permission blocks and warns against unpinned third-party actions.

zizmor detects patterns where fork pull requests or untrusted triggers could
exfiltrate secrets. This secures CI pipelines before deployment.

## Why It Is in Zenith

Continuous integration pipelines represent high-value attack surfaces because they hold
deployment credentials, PyPI release tokens, and code signing keys. AI coding assistants
frequently introduce insecure CI patterns, such as unquoted GitHub event contexts in run
steps.

Zenith runs zizmor as an automated security quality gate in prek hooks and CI
pipelines. This keeps infrastructure-as-code hardened against supply-chain and
injection attacks.

## Configuration in Zenith

Configured in `.zizmor.yml` at the project root:

```python exec="1" result="yaml"
from pathlib import Path

path = Path("{{cookiecutter.project_slug}}/.zizmor.yml")
if not path.exists():
    path = Path(".zizmor.yml")
print(path.read_text().strip())
```

And integrated into `prek.toml`:

```toml
[[repos]]
repo = "https://github.com/woodruffw/zizmor-pre-commit"
rev = "v1.4.1"
hooks = [
    { id = "zizmor", name = "🛡️ zizmor · Audit GitHub Actions workflows" },
]
```

## Key Invocations

```bash
uv run zizmor .github/workflows/   # Run static security audit on CI workflows
uv run prek run zizmor -a          # Run zizmor via prek
```

## Upstream Documentation

- [zizmor Official Documentation](https://woodruffw.github.io/zizmor/)
- [zizmor GitHub Repository](https://github.com/woodruffw/zizmor)
- [GitHub Actions Security Hardening Guide](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
