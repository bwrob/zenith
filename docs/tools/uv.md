# uv: Packaging & Environments

[![Tool: uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

`uv` is an extremely fast Python package and project manager written in Rust by Astral.
It serves as a unified replacement for `pip`, `pip-tools`, `virtualenv`, `poetry`, and
`pyenv`.

---

## What It Does

`uv` handles the complete lifecycle of Python application and library development. Using
an advanced PubGrub resolution algorithm, it resolves cross-platform dependency graphs
up to a hundred times faster than legacy package managers. It produces deterministic
`uv.lock` manifests that lock exact wheels, cryptographic hashes, and platform markers,
guaranteeing reproducible environments across developer machines and continuous
integration runners.

Beyond dependency management, `uv` provisions isolated virtual environments
automatically, compiles production-ready wheels and source distributions through its
native `uv_build` backend, and executes ephemeral command-line tools via `uvx` without
polluting the global system.

---

## Why It's in Zenith

Zenith adopts `uv` as its foundational environment engine to eliminate latency from
developer and AI agent feedback loops. Sub-second environment synchronization
(`uv sync`) keeps automated refactoring and testing completely frictionless.

Executing all project tasks hermetically through `uv run <command>` guarantees that
tools run against pinned project dependencies rather than system Python, preventing host
environment contamination. Combined with declarative dependency groups (`dev`, `test`,
`docs`) and native PEP 517 packaging, `uv` provides a unified, zero-drift foundation for
modern Python engineering.

---

## Configuration in Zenith

`uv` is configured declaratively in `pyproject.toml`:

```toml
[build-system]
    build-backend = "uv_build"
    requires      = ["uv_build>=0.5.0"]

[tool.uv]
    package = true

[dependency-groups]
    dev = [
        "poethepoet>=0.42.0",
        "prek>=0.5.5",
        "pyrefly>=0.0.1",
        "ruff>=0.17.0",
        "tach>=0.28.0",
        "taplo>=0.9.3",
        "typos>=1.30.0",
        "complexipy>=0.5.0",
        "zizmor>=1.4.1",
        "rumdl>=0.0.8",
    ]
    test = [
        "pytest>=8.0.0",
        "pytest-cov>=6.0.0",
        "pytest-xdist>=3.6.0",
        "pytest-randomly>=3.16.0",
        "syrupy>=4.8.0",
        "hypothesis>=6.124.0",
        "cosmic-ray>=8.3.0",
    ]
    docs = [
        "zensical>=0.0.8",
        "mkdocstrings[python]>=0.28.0",
        "markdown-exec>=1.12.0",
        "pymdown-extensions>=10.14.0",
        "typst>=0.13.0",
    ]
```

### Supply-Chain Protection

In GitHub Actions workflows (`.github/workflows/python_tests.yaml`), Zenith configures:

```yaml
env:
    UV_EXCLUDE_NEWER: "2026-10-18T00:00:00Z"
```

This prevents newly released upstream dependencies or malicious zero-day supply-chain
packages from breaking continuous integration builds until maintainers intentionally
update locks.

---

## Key Invocations

```bash
uv sync                       # Synchronize project environment with uv.lock
uv sync --group test          # Sync with test dependency group
uv run poe test               # Run Poe tasks inside managed environment
uv build                      # Build sdist and wheel distributions
uv lock --upgrade             # Upgrade dependency pins in uv.lock
```

---

## Upstream Documentation

- [uv Official Documentation](https://docs.astral.sh/uv/)
- [uv GitHub Repository](https://github.com/astral-sh/uv)
