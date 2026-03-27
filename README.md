# typermd

[![PyPI version](https://badge.fury.io/py/typermd.svg)](https://badge.fury.io/py/typermd)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tests](https://github.com/wronai/typermd/actions/workflows/tests.yml/badge.svg)](https://github.com/wronai/typermd/actions)

**Markdown rendering for Typer CLI applications with syntax highlighting.**

`typermd` is a drop-in replacement for [Typer](https://typer.tiangolo.com) that adds beautiful markdown rendering to your CLI output — with **zero code changes** beyond the import.

Like [clickmd](https://github.com/wronai/clickmd) is for Click, `typermd` is for Typer.

## Installation

```bash
pip install typermd
```

## Quick Start — Zero Code Changes

Just change your import:

```python
# Before
import typer

# After — that's it!
import typermd as typer
```

Everything works exactly as before, but now `typer.echo()` auto-detects markdown and renders it with colors, and you get a new `typer.md()` function for explicit markdown output.

### Minimal Example

```python
import typermd as typer

app = typer.Typer()

@app.command()
def hello(name: str = typer.Option("World", "--name", "-n")):
    typer.md(f"""
## 👋 Hello, {name}!

Welcome to **typermd** — making Typer CLIs beautiful.

```python
import typermd as typer
typer.md("# It's that easy!")
```
    """)

if __name__ == "__main__":
    app()
```

## Features

### Drop-in Typer Replacement

All Typer API is re-exported: `Typer`, `Option`, `Argument`, `Context`, `run`, `echo`, `style`, `colors`, `confirm`, `prompt`, `progressbar`, `launch`, `edit`, and more.

### Auto-detecting `echo()`

```python
# Plain text — works normally
typer.echo("Regular output, no formatting applied")

# Markdown detected — auto-rendered with colors
typer.echo("## Status: **running**")

# Force plain output
typer.echo("## Not rendered", auto_markdown=False)
```

### Explicit Markdown with `md()`

```python
typer.md("""
# Deploy Report

| Service | Status |
|---------|--------|
| API     | ✅ OK  |
| DB      | ✅ OK  |

```bash
kubectl get pods -n production
```
""")
```

### Syntax Highlighting

Supported languages:

| Language | Aliases | Highlights |
|----------|---------|-----------|
| Python | `python`, `py` | Keywords, strings, comments, decorators |
| JavaScript | `javascript`, `js` | Keywords, strings, template literals |
| TypeScript | `typescript`, `ts` | Same as JavaScript |
| Bash | `bash`, `sh`, `shell`, `zsh` | Commands, comments, variables |
| JSON | `json` | Keys, strings, numbers, booleans |
| YAML | `yaml`, `yml` | Keys, values, comments |
| TOML | `toml` | Sections, keys, strings |
| SQL | `sql` | Keywords, strings |
| Rust | `rust`, `rs` | Keywords, types, attributes |
| Go | `go` | Keywords, strings |
| Dockerfile | `dockerfile` | Instructions |
| Log | `log` | Errors (red), warnings (yellow), success (green) |

### Tables

```python
from typermd import table

table(
    headers=["Name", "Version", "Status"],
    rows=[
        ["typermd", "0.1.0", "✅ OK"],
        ["typer", "0.9.0", "✅ OK"],
    ],
)
```

### Panels

```python
from typermd import panel

panel("Deployment complete!", title="Success")
```

### Structured Logger

```python
from typermd.logger import get_logger

log = get_logger("deploy")
log.info("Starting deployment...")
log.step(1, 3, "Building artifacts")
log.step(2, 3, "Running tests")
log.step(3, 3, "Deploying")
log.success("Deployed to production!")
log.warning("Cache may need warming")
log.error("Rollback required")
log.action("Next", "Monitor dashboard")
```

### Themes

```python
from typermd.themes import set_theme, list_themes

list_themes()         # ['default', 'monokai', 'solarized', 'nord']
set_theme("monokai")  # Switch theme
```

Or via environment variable:

```bash
export TYPERMD_THEME=monokai
```

## Markdown Elements Supported

- **Headings** (`# H1` through `###### H6`) with colored underlines
- **Bold** (`**text**`) and **italic** (`*text*`)
- **Inline code** (`` `code` ``) with background highlight
- **Code blocks** with syntax highlighting
- **Bullet lists** (`- item`) with indentation
- **Numbered lists** (`1. item`)
- **Checklists** (`- [x] done`, `- [ ] todo`)
- **Links** (`[text](url)`)
- **Blockquotes** (`> text`)
- **Horizontal rules** (`---`)

## API Reference

### Core Functions

| Function | Description |
|----------|-------------|
| `md(text)` | Render markdown to stdout |
| `echo(msg, *, auto_markdown=True)` | Smart echo — auto-detects markdown |
| `render_markdown(text, stream, use_colors)` | Render to any stream |
| `render_to_string(text)` | Render and return as string |
| `get_renderer(stream, use_colors)` | Get a `MarkdownRenderer` instance |
| `table(headers, rows)` | Render a table |
| `panel(content, title)` | Render a bordered panel |
| `blockquote(content)` | Render a blockquote |

### All Typer Re-exports

`Typer`, `Argument`, `Option`, `Context`, `Exit`, `Abort`, `run`, `main`, `colors`, `style`, `unstyle`, `prompt`, `confirm`, `progressbar`, `get_text_stream`, `get_binary_stream`, `open_file`, `launch`, `edit`, `clear`, `pause`, `get_app_dir`

## Project Structure

```
typermd/
├── src/typermd/          # Package source (src layout)
│   ├── __init__.py       # Public API: md(), echo(), table(), panel()
│   ├── renderer.py       # Core markdown renderer & syntax highlighting
│   ├── help.py           # Markdown help formatter for Typer
│   ├── logger.py         # Structured logger
│   ├── themes.py         # Color themes & NO_COLOR support
│   └── py.typed          # PEP 561 type marker
├── tests/                # Test suite
├── examples/             # Demo scripts
├── pyproject.toml        # Project config (hatchling)
└── README.md
```

## Development

```bash
git clone https://github.com/wronai/typermd.git
cd typermd
pip install -e ".[dev]"
pytest
```

## Comparison: clickmd vs typermd

| Feature | clickmd | typermd |
|---------|---------|---------|
| Framework | Click | Typer |
| Import | `import clickmd as click` | `import typermd as typer` |
| Type hints | Click decorators | Native Python type hints |
| Markdown | `click.md()` | `typer.md()` |
| Auto-detect | `click.echo()` | `typer.echo()` |
| Code changes | Zero | Zero |

## Standards

- Respects [NO_COLOR](https://no-color.org) environment variable
- Supports `FORCE_COLOR` for CI/CD pipelines
- Supports `TYPERMD_THEME` for theme selection
- PEP 561 typed package

## License

Licensed under Apache-2.0.


Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Author

Tom Sapletta


Created by **Tom Sapletta** - [tom@sapletta.com](mailto:tom@sapletta.com)

## Related Projects

- [Typer](https://typer.tiangolo.com) — Python CLI framework with type hints
- [Click](https://click.palletsprojects.com) — Python CLI framework
- [clickmd](https://github.com/wronai/clickmd) — Markdown rendering for Click CLIs
- [Rich](https://github.com/Textualize/rich) — Rich text and formatting
