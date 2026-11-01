---
diataxis: reference
purpose: Document interactive animated terminal widgets and console session wrapping with Termynal.
---

# Termynal: Terminal Animations

[![Tool: Termynal](https://img.shields.io/badge/docs-termynal-00c853.svg)](https://github.com/ines/termynal)

`Termynal` is a lightweight, animated terminal emulation widget written in JavaScript
and CSS by Ines Montani. It renders typing animations and interactive CLI outputs
directly in documentation pages without requiring video recordings or animated GIFs.

## What It Does

`Termynal` simulates an authentic interactive shell session directly inside
documentation pages. It animates command input keystroke by keystroke with realistic
cursor delays, simulates progress indicators and loaders, and distinguishes command
prompts, user input, and console outputs.

Unlike video recordings or animated GIFs, Termynal renders text as pure, accessible HTML
and CSS without heavy media assets.

## Why It's in Zenith

First impressions matter. Displaying an interactive, animated terminal demonstration of
the CLI on the landing page immediately conveys project ergonomics without requiring
visitors to download large media files.

Unlike recorded videos, visitors can pause animations, select text, and copy commands
directly from the terminal widget. Zenith integrates Termynal so any standard
markdown ` ```console ` block preceded by `<!-- termynal -->` automatically
animates.

## Configuration in Zenith

Managed as a declared dependency (`termynal>=0.14.0`) in `pyproject.toml` and
registered in `zensical.toml`:

```toml
[project.markdown_extensions]
    termynal.include_assets = true
    termynal.prompt_literal_start = ["$", ">>>"]
```

### Usage in Markdown

Place `<!-- termynal -->` directly before any fenced `console` code block:

````markdown
<!-- termynal -->
```console
$ uv run my-app greet "World"

✨ Hello, World!

# View help and options
$ uv run my-app --help
```
````

## Upstream Documentation

- [Termynal PyPI Package](https://pypi.org/project/termynal/)
- [Termynal GitHub Repository](https://github.com/ines/termynal)
