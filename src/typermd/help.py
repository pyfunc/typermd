"""Markdown-aware help formatter for Typer/Click commands.

Renders help text with markdown formatting (bold, code, headers, lists)
in the terminal when colors are supported.

Usage:
    import typermd as typer

    app = typer.Typer(rich_markup_mode=None)

    # Then install the formatter:
    from typermd.help import install_help_formatter
    install_help_formatter(app)
"""


import re
import sys
from typing import Any

import click

from typermd.renderer import (
    BOLD,
    FG_CYAN,
    FG_YELLOW,
    ITALIC,
    RESET,
    _supports_color,
)


class MarkdownHelpFormatter(click.HelpFormatter):
    """Click HelpFormatter that renders markdown in help text."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._use_colors = _supports_color(sys.stdout)

    def _colorize(self, text: str) -> str:
        """Apply inline markdown rendering to help text."""
        if not self._use_colors:
            return text

        # Bold
        text = re.sub(
            r"\*\*(.+?)\*\*",
            lambda m: f"{BOLD}{m.group(1)}{RESET}",
            text,
        )
        # Italic
        text = re.sub(
            r"\*(.+?)\*",
            lambda m: f"{ITALIC}{m.group(1)}{RESET}",
            text,
        )
        # Inline code
        text = re.sub(
            r"`(.+?)`",
            lambda m: f"{FG_YELLOW}{m.group(1)}{RESET}",
            text,
        )
        return text

    def write(self, string: str) -> str:  # type: ignore[override]
        """Override write to apply markdown formatting."""
        return super().write(self._colorize(string)) or ""

    def write_heading(self, heading: str) -> None:
        """Write a heading with color."""
        if self._use_colors:
            self.write(f"{BOLD}{FG_CYAN}{heading}:{RESET}\n")
        else:
            super().write_heading(heading)

    def write_usage(self, prog: str, args: str = "", prefix: str | None = None) -> None:
        """Write usage line with color."""
        if self._use_colors and prefix is None:
            prefix = f"{BOLD}Usage:{RESET} "
        super().write_usage(prog, args, prefix=prefix)


def install_help_formatter(app: Any) -> None:
    """Install the markdown help formatter on a Typer app.

    This patches the underlying Click group's format_help to use
    MarkdownHelpFormatter.

    Args:
        app: A typer.Typer instance.
    """

    class _MarkdownGroup(click.Group):
        def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
            md_formatter = MarkdownHelpFormatter(
                width=formatter.width,
                max_width=formatter.width,
            )
            super().format_help(ctx, md_formatter)
            formatter.write(md_formatter.getvalue())

    # Patch the Typer app's underlying Click group class
    if hasattr(app, "info") and hasattr(app.info, "cls"):
        app.info.cls = _MarkdownGroup
