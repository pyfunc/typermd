<!-- code2docs:start --># typermd

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.10-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-61-green)
> **61** functions | **5** classes | **10** files | CC̄ = 2.8

> Auto-generated project documentation from source code analysis.

**Author:** Tom Sapletta  
**License:** Apache-2.0[(LICENSE)](./LICENSE)  
**Repository:** [https://github.com/pyfunc/typermd](https://github.com/pyfunc/typermd)

## Installation

### From PyPI

```bash
pip install typermd
```

### From Source

```bash
git clone https://github.com/pyfunc/typermd
cd typermd
pip install -e .
```

### Optional Extras

```bash
pip install typermd[dev]    # development tools
```

## Quick Start

### CLI Usage

```bash
# Generate full documentation for your project
typermd ./my-project

# Only regenerate README
typermd ./my-project --readme-only

# Preview what would be generated (no file writes)
typermd ./my-project --dry-run

# Check documentation health
typermd check ./my-project

# Sync — regenerate only changed modules
typermd sync ./my-project
```

### Python API

```python
from typermd import generate_readme, generate_docs, Code2DocsConfig

# Quick: generate README
generate_readme("./my-project")

# Full: generate all documentation
config = Code2DocsConfig(project_name="mylib", verbose=True)
docs = generate_docs("./my-project", config=config)
```

## Generated Output

When you run `typermd`, the following files are produced:

```
<project>/
├── README.md                 # Main project README (auto-generated sections)
├── docs/
│   ├── api.md               # Consolidated API reference
│   ├── modules.md           # Module documentation with metrics
│   ├── architecture.md      # Architecture overview with diagrams
│   ├── dependency-graph.md  # Module dependency graphs
│   ├── coverage.md          # Docstring coverage report
│   ├── getting-started.md   # Getting started guide
│   ├── configuration.md    # Configuration reference
│   └── api-changelog.md    # API change tracking
├── examples/
│   ├── quickstart.py       # Basic usage examples
│   └── advanced_usage.py   # Advanced usage examples
├── CONTRIBUTING.md         # Contribution guidelines
└── mkdocs.yml             # MkDocs site configuration
```

## Configuration

Create `typermd.yaml` in your project root (or run `typermd init`):

```yaml
project:
  name: my-project
  source: ./
  output: ./docs/

readme:
  sections:
    - overview
    - install
    - quickstart
    - api
    - structure
  badges:
    - version
    - python
    - coverage
  sync_markers: true

docs:
  api_reference: true
  module_docs: true
  architecture: true
  changelog: true

examples:
  auto_generate: true
  from_entry_points: true

sync:
  strategy: markers    # markers | full | git-diff
  watch: false
  ignore:
    - "tests/"
    - "__pycache__"
```

## Sync Markers

typermd can update only specific sections of an existing README using HTML comment markers:

```markdown
<!-- typermd:start -->
# Project Title
... auto-generated content ...
<!-- typermd:end -->
```

Content outside the markers is preserved when regenerating. Enable this with `sync_markers: true` in your configuration.

## Architecture

```
typermd/
    ├── tables_panels    ├── table_styles_demo    ├── typermd/    ├── basic    ├── logger_usage        ├── logger├── project        ├── themes        ├── renderer        ├── help```

## API Overview

### Classes

- **`Logger`** — Markdown-aware structured logger.
- **`Theme`** — Color theme definition with named color slots.
- **`MarkdownRenderer`** — Renders markdown text to the terminal with ANSI colors.
- **`MarkdownHelpFormatter`** — Click HelpFormatter that renders markdown in help text.

### Functions

- `deps()` — Show project dependencies as a table.
- `info()` — Show app info in a panel.
- `demo()` — Demonstrate all table styles.
- `echo(message, file, nl, err)` — Enhanced echo that auto-detects and renders markdown.
- `table(headers, rows, style)` — Render a table to the terminal.
- `panel(content, title, style_color)` — Render a bordered panel.
- `blockquote(content)` — Render a blockquote.
- `hello(name, formal)` — Say hello with markdown formatting.
- `status()` — Show system status with styled output.
- `demo()` — Demonstrate all markdown features.
- `deploy(env, dry_run)` — Simulate a deployment with structured logging.
- `get_logger(name, verbose)` — Get or create the default logger.
- `set_logger(logger)` — Replace the default logger.
- `get_theme()` — Get the current active theme.
- `set_theme(name)` — Switch to a named theme.
- `register_theme(theme)` — Register a custom theme.
- `list_themes()` — Return list of available theme names.
- `is_no_color()` — Check if NO_COLOR env is set.
- `init_theme_from_env()` — Initialize theme from TYPERMD_THEME env variable.
- `strip_ansi(text)` — Remove all ANSI escape codes from text.
- `looks_like_markdown(text)` — Heuristic: does the text contain markdown formatting?
- `get_renderer(stream, use_colors)` — Get or create the default MarkdownRenderer.
- `render_markdown(text, stream, use_colors)` — Render markdown text to a stream.
- `md(text)` — Render markdown text to stdout. Primary convenience function.
- `render_to_string(text)` — Render markdown and return as string.
- `install_help_formatter(app)` — Install the markdown help formatter on a Typer app.


## Project Structure

📄 `examples.basic` (3 functions)
📄 `examples.logger_usage` (1 functions)
📄 `examples.table_styles_demo` (1 functions)
📄 `examples.tables_panels` (2 functions)
📄 `project`
📦 `src.typermd` (5 functions)
📄 `src.typermd.help` (6 functions, 1 classes)
📄 `src.typermd.logger` (12 functions, 1 classes)
📄 `src.typermd.renderer` (24 functions, 2 classes)
📄 `src.typermd.themes` (7 functions, 1 classes)

## Requirements

- Python >= >=3.10
- typer >=0.9.0

## Contributing

**Contributors:**
- Tom Sapletta <tom-sapletta-com@users.noreply.github.com>
- Tom Softreck <tom@sapletta.com>

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/pyfunc/typermd
cd typermd

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Documentation

- 📖 [Full Documentation](https://github.com/pyfunc/typermd/tree/main/docs) — API reference, module docs, architecture
- 🚀 [Getting Started](https://github.com/pyfunc/typermd/blob/main/docs/getting-started.md) — Quick start guide
- 📚 [API Reference](https://github.com/pyfunc/typermd/blob/main/docs/api.md) — Complete API documentation
- 🔧 [Configuration](https://github.com/pyfunc/typermd/blob/main/docs/configuration.md) — Configuration options
- 💡 [Examples](./examples) — Usage examples and code samples

### Generated Files

| Output | Description | Link |
|--------|-------------|------|
| `README.md` | Project overview (this file) | — |
| `docs/api.md` | Consolidated API reference | [View](./docs/api.md) |
| `docs/modules.md` | Module reference with metrics | [View](./docs/modules.md) |
| `docs/architecture.md` | Architecture with diagrams | [View](./docs/architecture.md) |
| `docs/dependency-graph.md` | Dependency graphs | [View](./docs/dependency-graph.md) |
| `docs/coverage.md` | Docstring coverage report | [View](./docs/coverage.md) |
| `docs/getting-started.md` | Getting started guide | [View](./docs/getting-started.md) |
| `docs/configuration.md` | Configuration reference | [View](./docs/configuration.md) |
| `docs/api-changelog.md` | API change tracking | [View](./docs/api-changelog.md) |
| `CONTRIBUTING.md` | Contribution guidelines | [View](./CONTRIBUTING.md) |
| `examples/` | Usage examples | [Browse](./examples) |
| `mkdocs.yml` | MkDocs configuration | — |

<!-- code2docs:end -->