---
diataxis: reference
purpose: Document interactive animated terminal widgets and console session wrapping with Termynal.
---

# Termynal: Terminal Animations

[![Tool: Termynal](https://img.shields.io/badge/docs-termynal-00c853.svg)](https://github.com/ines/termynal)

`Termynal` renders fenced `console` code blocks preceded by `<!-- termynal -->` as
interactive, copyable HTML/CSS terminal animations in **[Zensical](zensical.md)**
documentation pages.

## Configuration in Zenith

Declared in the `docs` dependency group (`termynal>=0.14.0` when `include_cli` is
enabled) and configured under `[project.markdown_extensions]` in `zensical.toml`:

```toml
[project.markdown_extensions]
    termynal.include_assets       = true
    termynal.prompt_literal_start = ["$", ">>>"]
```

## Usage in Markdown

Place `<!-- termynal -->` immediately before a fenced `console` block:

````markdown
<!-- termynal -->
```console
$ uv run my-project greet "World"

✨ Hello, World!

# Inspect CLI help
$ uv run my-project --help
```
````

## Upstream Documentation

- [Termynal PyPI Package](https://pypi.org/project/termynal/)
- [Termynal GitHub Repository](https://github.com/ines/termynal)
