"""Tables, panels, and structured output with typermd."""

import typermd as typer
from typermd import table, panel

app = typer.Typer()


@app.command()
def deps():
    """Show project dependencies as a table."""
    typer.md("## 📦 Dependencies\n")
    table(
        headers=["Package", "Version", "Status"],
        rows=[
            ["typer", "0.9.0", "✅ OK"],
            ["typermd", "0.1.0", "✅ OK"],
            ["click", "8.1.7", "✅ OK"],
            ["rich", "13.7.0", "⚠️ optional"],
        ],
    )


@app.command()
def info():
    """Show app info in a panel."""
    panel(
        "typermd v0.1.0\nMarkdown rendering for Typer CLIs\nLicense: Apache-2.0",
        title="About",
    )


if __name__ == "__main__":
    app()
