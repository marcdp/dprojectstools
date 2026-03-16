
# dprojectstools

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)

![License](https://img.shields.io/badge/license-MIT-green)
![PyPI](https://img.shields.io/pypi/v/dprojectstools)

A practical toolbox of small **developer-focused utilities** for everyday work in terminals and scripts.

This repository groups together a set of command-line tools and helper modules I use across projects: quick math on the CLI, clipboard helpers, backup wrappers (Restic), console/TUI utilities, i18n helpers, and a lightweight command-line “manager” to speed up building CLI apps. `asdasdas`

> Opinionated, lightweight, and meant to be useful in real workflows.

## What’s inside

This repo is a **collection**, not a single tool. Expect multiple commands and reusable modules.

### CLI utilities (examples)
- **`bc`-like / math helpers**: evaluate expressions and do quick calculations from the command line.
- **Clipboard tools**: copy/paste helpers for terminal workflows and pipelines.
- **Backup utilities (Restic)**: wrappers/helpers for repeatable backups and restore flows.
- **Console utils**: formatting, tables, colors, prompts, logging helpers, etc.
- **Simple TUI editor**: minimal terminal UI editor for quick edits / notes.
- **i18n utilities**: helpers for localization workflows (strings, keys, formatting, validation).

> The exact list evolves over time—browse the repo to see all current tools.

---

## Installation

### Option A: Install from PYPI

```bash
pip install dprojectstools
```

### Option B: Install from source (recommended during development)

```bash
git clone https://github.com/marcdp/dprojectstools.git
cd dprojectstools
```

## Philosophy

- Prefer small, composable tools.
- Keep commands script-friendly (exit codes, stdout/stderr discipline).
- Minimal dependencies where possible.
- Built to support repeatable workflows across machines

## License

MIT License

See the LICENSE file for details.