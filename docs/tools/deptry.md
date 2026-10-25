---
diataxis: reference
purpose: Document dependency health checks, unused package detection, and transitive import audits with Deptry.
---

# Deptry: Dependency Hygiene

Deptry checks Python imports against the dependencies declared in `pyproject.toml`. It
detects missing runtime dependencies, unused declared dependencies, and imports that
are available only through another package.

## Usage in Zenith

Run the dependency check through Poe:

```bash
uv run poe dependencies
```

In the template repository, the task scans `hooks/` and `scripts/`. In a generated
project, it runs `tach check` for internal module boundaries and `deptry src` for
package dependencies.

Run Deptry directly when you need to inspect its findings:

```bash
uv run deptry hooks scripts  # Template repository
uv run deptry src            # Generated project
```

Deptry reads project metadata and its configuration from `pyproject.toml`. Use
`[tool.deptry]` there only when the project needs exclusions or import-name mappings.

## Upstream Documentation

- [Deptry usage](https://github.com/osprey-oss/deptry/blob/main/docs/usage.md)
- [Deptry configuration](https://github.com/osprey-oss/deptry/blob/main/docs/configuration.md)
