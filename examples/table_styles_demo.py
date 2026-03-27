#!/usr/bin/env python3
"""Demonstrate table styles feature."""

import typermd as typer

app = typer.Typer()

@app.command()
def demo() -> None:
    """Demonstrate all table styles."""
    
    headers = ["Package", "Version", "Status"]
    rows = [
        ["typer", "0.24.1", "✅ OK"],
        ["typermd", "0.1.2", "✅ OK"],
        ["click", "8.3.1", "✅ OK"],
        ["rich", "14.3.3", "⚠️ optional"],
    ]
    
    styles = ["unicode", "ascii", "minimal", "none", "markdown"]
    
    for style in styles:
        typer.md(f"\n## Table Style: {style}\n")
        typer.table(headers, rows, style=style)

if __name__ == "__main__":
    typer.Typer()
