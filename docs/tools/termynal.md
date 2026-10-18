# Termynal: Terminal Animations

[![Tool: Termynal](https://img.shields.io/badge/docs-termynal-00c853.svg)](https://github.com/ines/termynal)

`Termynal` is a lightweight, animated terminal emulation widget written in JavaScript and CSS by Ines Montani. It renders typing animations and interactive CLI outputs directly in documentation pages without requiring video recordings or animated GIFs.

---

## What It Does

`Termynal` simulates an authentic interactive shell session directly inside documentation pages. It animates command input keystroke by keystroke with realistic cursor delays, simulates progress indicators and loaders, and distinguishes command prompts, user input, and console outputs.

Unlike video recordings or animated GIFs, Termynal renders text as pure, accessible HTML and CSS without heavy media assets.

---

## Why It's in Zenith

First impressions matter. Displaying an interactive, animated terminal demonstration of the CLI on the landing page immediately conveys project ergonomics without requiring visitors to download large media files.

Unlike recorded videos, visitors can pause animations, select text, and copy commands directly from the terminal widget. Zenith wraps this functionality so any standard markdown ` ```console ` block contained within `<div class="termy">` automatically animates.

---

## Configuration in Zenith

Configured in `docs/stylesheets/termynal.css` and `docs/javascripts/termynal.js`, registered in `zensical.toml`:

```toml
extra_css = [
    "stylesheets/termynal.css",
]

extra_javascript = [
    "javascripts/termynal.js",
]
```

### Usage in Markdown:

```markdown
<div class="termy">

```console
$ uv run my-app greet "World"

✨ Hello, World!
```

</div>
```

---

## Upstream Documentation

- [Termynal GitHub Repository](https://github.com/ines/termynal)
