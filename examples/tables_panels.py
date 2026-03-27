"""Tables, panels, and structured output with typermd."""

import typermd as typer
from typermd import table, panel

app = typer.Typer()


@app.command()
def deps() -> None:
    """Show project dependencies as a table."""
    typer.md("## 📦 Dependencies\n")
    table(
        headers=["Package", "Version", "Status"],
        rows=[
            ["typer", "0.9.0", "✅ OK"],
            ["typermd", "0.1.2", "✅ OK"],
            ["click", "8.1.7", "✅ OK"],
            ["rich", "13.7.0", "⚠️ optional"],
        ],
        style="markdown",
    )


@app.command()
def info() -> None:
    """Show app info in a panel."""
    panel(
        "typermd v0.1.2\nMarkdown rendering for Typer CLIs\nLicense: Apache-2.0",
        title="About",
    )


if __name__ == "__main__":
    app()
