# Typst: Vector Layout Engine

[![Tool: Typst](https://img.shields.io/badge/typesetting-typst-239dad.svg)](https://typst.app)

`Typst` is a modern markup-based typesetting and document layout engine written in Rust. In Zenith projects, Typst is used to programmatically generate clean, resolution-independent vector SVG logotypes for documentation.

---

## What It Does

Typst pairs the document layout power of LaTeX with a modern, ergonomic scripting language. It compiles text-based `.typ` files into resolution-independent `.svg` vector graphics or `.pdf` outputs in milliseconds.

In Zenith projects, visual emblems, icons, and logotypes are constructed programmatically with Typst's canvas shapes, gradients, and typography engines—treating design assets as version-controlled code rather than binary image blobs.

---

## Why It's in Zenith

Zenith enforces a "code-as-asset" philosophy: all project assets, including branding and documentation imagery, should be plain text files that can be edited by humans or AI agents, diffed in Git, and built deterministically.

The Typst logotype source directly defines the celestial Python hues (`#387eb8` blue and `#ffc331` gold) used throughout documentation stylesheets, eliminating binary media tracking from the repository.

---

## Configuration in Zenith

Source file located at `docs/assets/python-logo.typ` (or `assets/zenith-star.svg`):

```typst
#set page(width: auto, height: auto, margin: 0pt, fill: none)

#let python-blue = rgb("#387eb8")
#let python-gold = rgb("#ffc331")

// Vector geometry rendering of the logotype
#rect(width: 120pt, height: 120pt, radius: 16pt, fill: python-blue)
```

Wired into `poe_tasks.toml` through the `docs-logo` task:

```toml
[tasks.docs-logo]
cmd = "typst compile docs/assets/python-logo.typ docs/assets/python-logo.svg"
help = "Compile documentation logotype SVG with Typst."
```

---

## Key Invocations

```bash
uv run poe docs-logo         # Re-compile SVG logotype from Typst source
uv run typst compile file.typ file.svg
```

---

## Upstream Documentation

- [Typst Official Documentation](https://typst.app/docs/)
- [Typst GitHub Repository](https://github.com/typst/typst)
