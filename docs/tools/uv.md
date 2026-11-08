---
diataxis: reference
purpose: Document package management, environment synchronization, and Python runtime pinning with uv.
---

# Uv: Packaging & Environments

[![Tool: uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

`uv` is Astral's Rust-based Python package, dependency, and environment manager. In
Zenith projects, `uv` manages Python interpreter downloads, `.venv/` creation,
cross-platform `uv.lock` resolution, isolated command execution (`uv run`), and PEP 517
wheel/sdist builds via the native `uv_build` backend.

## Configuration in Zenith

Configured in `pyproject.toml`:

```toml
[build-system]
    build-backend = "uv_build"
    requires      = ["uv_build>=0.12.7,<0.14.0"]

[dependency-groups]
    dev = [
        "poethepoet>=0.42.0",
        "prek>=0.5.5",
        { include-group = "test" },
        { include-group = "lint" },
        { include-group = "docs" },
        { include-group = "mutation" },
    ]
    docs = [
        "fontpkg-cinzel>=2.0",
        "griffe-warnings-deprecated>=1.1.0",
        "markdown-exec>=1.12.0",
        "mkdocstrings[python]>=1.0.7",
        "termynal>=0.14.0",
        "typst>=0.13.0",
        "zensical>=0.0.70",
    ]
    lint = [
        "complexipy>=8.0.0",
        "deptry>=0.25.1",
        "griffe>=1.5.0",
        "pyrefly>=1.3.0",
        "ruff>=0.17.0",
        "rumdl>=0.2.75",
        "tach>=0.35.0",
        "taplo>=0.9.3",
        "typos>=1.30.0",
        "zizmor>=1.23.0",
    ]
    mutation = [
        "cosmic-ray>=8.7.0",
        "mutmut>=3.8.0",
    ]
    test = [
        "hypothesis>=6.125.0",
        "pytest>=9.0.0",
        "pytest-cov>=7.0.0",
        "pytest-randomly>=3.16.0",
        "pytest-sugar>=1.1.1",
        "pytest-xdist>=3.8.0",
        "syrupy>=6.1.0",
    ]

[tool.uv]
    default-groups = ["dev", "test", "lint", "docs", "mutation"]
    package        = true

    [tool.uv.build-backend]
        source-include = [
            "tests/**",
            "poe_tasks.toml",
            "ruff.toml",
            "pytest.ini",
            ".coveragerc",
            "tach.toml",
            ".zizmor.yml",
            "cosmic-ray.toml",
        ]
```

### Supply-Chain Cooldown & Vulnerability Audits

- **Release cooldown (`UV_EXCLUDE_NEWER` / `exclude-newer`)**: In CI workflows
  (`python_tests.yaml` and `test_redistribute.yaml`), unpinned resolution steps set
  `UV_EXCLUDE_NEWER` to a 7-day rolling cutoff so newly published upstream releases
  have a 7-day window for community vetting before entering unpinned test jobs. You can
  also uncomment `exclude-newer = "7 days"` under `[tool.uv]` in `pyproject.toml` to
  apply the same buffer during local `uv lock` updates.
- **Lockfile CVE auditing (`uv audit`)**: Run `uv run poe audit` (`uv audit`) to scan
  all locked packages in `uv.lock` against advisory databases.

## Key Invocations

```bash
uv sync                                         # Sync .venv with uv.lock
uv sync --frozen --group test                   # Strict CI sync for one group
uv sync --group test --resolution lowest-direct # Resolve minimum bounds
uv add <package>                                # Add a runtime dependency
uv add --group lint <package>                   # Add to a dependency group
uv run poe test                                 # Run a Poe task inside .venv
uv run poe audit                                # Audit uv.lock for CVEs
uv build                                        # Build wheel and sdist
uv lock --upgrade                               # Upgrade locked versions
```

## Multi-Stage Docker Build

For containerized deployments, use `uv sync --frozen --no-dev --no-editable` with
BuildKit cache mounts:

```dockerfile
# syntax=docker/dockerfile:1.7
FROM python:3.12-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --no-editable

COPY src /app/src
COPY README.md LICENSE pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
USER nobody

ENTRYPOINT ["my-project"]
```

## Upstream Documentation

- [uv Official Documentation](https://docs.astral.sh/uv/)
- [uv GitHub Repository](https://github.com/astral-sh/uv)
