"""Basic typermd usage — drop-in replacement for typer."""

import typermd as typer

app = typer.Typer(help="Example CLI with markdown rendering")


@app.command()
def hello(
    name: str = typer.Option("World", "--name", "-n", help="Name to greet"),
    formal: bool = typer.Option(False, "--formal", "-f", help="Use formal greeting"),
):
    """Say hello with markdown formatting."""
    if formal:
        typer.md(f"""
## 🎩 Greetings, {name}!

It is a **pleasure** to make your acquaintance.

Features available:
- Syntax highlighting
- Markdown rendering
- Drop-in Typer replacement
        """)
    else:
        typer.md(f"""
## 👋 Hey, {name}!

Welcome to **typermd** — beautiful CLI output with *zero effort*.
        """)


@app.command()
def status():
    """Show system status with styled output."""
    typer.md("""
## 📊 System Status

```log
✅ API server: running
✅ Database: connected
⚠️ Cache: warming up
✅ Queue: 0 pending jobs
```

All systems **operational**.
    """)


@app.command()
def demo():
    """Demonstrate all markdown features."""
    typer.md("""
# typermd Feature Demo

## Code Blocks

```python
from typermd import md

md("# Hello from typermd!")
```

```bash
pip install typermd
typermd --help
```

## Text Formatting

This is **bold**, this is *italic*, and this is `inline code`.

## Lists

- First item
- Second item
- Third item

1. Ordered one
2. Ordered two
3. Ordered three

## Links

Check out [Typer](https://typer.tiangolo.com) for more info.

> Blockquotes are also supported and rendered with style.

---

*That's all!*
    """)


if __name__ == "__main__":
    app()
