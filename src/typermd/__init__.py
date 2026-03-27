"""typermd — Markdown rendering for Typer CLI applications.

Drop-in replacement: `import typermd as typer` gives you the full Typer API
plus automatic markdown rendering in terminal output.

Usage:
    import typermd as typer

    app = typer.Typer()

    @app.command()
    def hello(name: str = "World"):
        typer.md(f"## Hello, {name}!")
        typer.echo("Regular text works too")

    if __name__ == "__main__":
        typer.Typer()
"""


__version__ = "0.1.3"
__all__ = [
    # typermd extras
    "md",
    "echo",
    "render_markdown",
    "get_renderer",
    "MarkdownRenderer",
    "looks_like_markdown",
    "strip_ansi",
    # re-exported from typer
    "Typer",
    "Argument",
    "Option",
    "Context",
    "CallbackType",
    "Exit",
    "Abort",
    "run",
    "colors",
    "style",
    "unstyle",
    "prompt",
    "confirm",
    "progressbar",
    "get_text_stream",
    "get_binary_stream",
    "open_file",
    "launch",
    "edit",
    "clear",
    "pause",
    "get_app_dir",
    "main",
]

# ── Re-export the full Typer API ──────────────────────────────────────────

import typer as _typer

# Core classes & types
Typer = _typer.Typer
Argument = _typer.Argument
Option = _typer.Option
Context = _typer.Context
Exit = _typer.Exit
Abort = _typer.Abort

# Typer callable helpers
run = _typer.run
main = _typer.main

# Color / style
colors = _typer.colors
style = _typer.style
unstyle = _typer.unstyle

# Interactive
prompt = _typer.prompt
confirm = _typer.confirm

# Progress
progressbar = _typer.progressbar

# Streams / files
get_text_stream = _typer.get_text_stream
get_binary_stream = _typer.get_binary_stream
open_file = _typer.open_file

# OS integration
launch = _typer.launch
edit = _typer.edit
clear = _typer.clear
pause = _typer.pause
get_app_dir = _typer.get_app_dir

# If Typer exposes CallbackType (version-dependent)
try:
    CallbackType = _typer.CallbackType  # type: ignore[attr-defined]
except AttributeError:
    pass

# ── Import typermd rendering ─────────────────────────────────────────────

from typermd.renderer import (  # noqa: E402
    MarkdownRenderer,
    get_renderer,
    looks_like_markdown,
    md,
    render_markdown,
    strip_ansi,
)

# ── Enhanced echo ─────────────────────────────────────────────────────────

_original_echo = _typer.echo


def echo(
    message: object = "",
    file: object | None = None,
    nl: bool = True,
    err: bool = False,
    color: bool | None = None,
    *,
    auto_markdown: bool = True,
) -> None:
    """Enhanced echo that auto-detects and renders markdown.

    Drop-in replacement for ``typer.echo()`` with one extra feature:
    if the message looks like markdown, it is rendered with colors and
    formatting. Set ``auto_markdown=False`` to force plain output.

    Args:
        message: Text to print.
        file: Output stream (default: stdout, or stderr when ``err=True``).
        nl: Print trailing newline.
        err: Print to stderr.
        color: Force color on/off (None = auto-detect).
        auto_markdown: Auto-render markdown when detected.
    """
    text = str(message) if message is not None else ""

    if auto_markdown and text and looks_like_markdown(text):
        import sys

        stream = file if file is not None else (sys.stderr if err else sys.stdout)
        use_colors = color if color is not None else True
        render_markdown(text, stream=stream, use_colors=use_colors)  # type: ignore[arg-type]
        if nl and not text.endswith("\n"):
            (stream if hasattr(stream, "write") else sys.stdout).write("\n")
    else:
        _original_echo(message, file=file, nl=nl, err=err, color=color)  # type: ignore[arg-type]


# ── Convenience: table / panel / blockquote ───────────────────────────────


def _get_table_chars(style: str) -> dict[str, str]:
    """Get table border characters for style."""
    if style == "markdown":
        return {
            "horizontal": "-",
            "vertical": "|",
            "top_left": "",
            "top_right": "",
            "top_mid": "",
            "mid_left": "|",
            "mid_right": "|",
            "mid_mid": "|",
            "bottom_left": "",
            "bottom_right": "",
            "bottom_mid": "",
        }
    elif style == "unicode":
        return {
            "horizontal": "─",
            "vertical": "│",
            "top_left": "┌",
            "top_right": "┐",
            "top_mid": "┬",
            "mid_left": "├",
            "mid_right": "┤",
            "mid_mid": "┼",
            "bottom_left": "└",
            "bottom_right": "┘",
            "bottom_mid": "┴",
        }
    elif style == "ascii":
        return {
            "horizontal": "-",
            "vertical": "|",
            "top_left": "+",
            "top_right": "+",
            "top_mid": "+",
            "mid_left": "+",
            "mid_right": "+",
            "mid_mid": "+",
            "bottom_left": "+",
            "bottom_right": "+",
            "bottom_mid": "+",
        }
    elif style == "minimal":
        return {
            "horizontal": "─",
            "vertical": " ",
            "top_left": "",
            "top_right": "",
            "top_mid": " ",
            "mid_left": "",
            "mid_right": "",
            "mid_mid": " ",
            "bottom_left": "",
            "bottom_right": "",
            "bottom_mid": " ",
        }
    else:  # none
        return {
            "horizontal": "",
            "vertical": " ",
            "top_left": "",
            "top_right": "",
            "top_mid": "",
            "mid_left": "",
            "mid_right": "",
            "mid_mid": "",
            "bottom_left": "",
            "bottom_right": "",
            "bottom_mid": "",
        }


def table(
    headers: list[str],
    rows: list[list[str]],
    style: str = "unicode",
) -> None:
    """Render a table to the terminal.

    Args:
        headers: Column header labels.
        rows: List of rows (each row is a list of cell strings).
        style: Table border style - "unicode", "ascii", "minimal", "none", or "markdown".
    """
    renderer = get_renderer()

    # Get table border characters based on style
    chars = _get_table_chars(style)

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(strip_ansi(str(cell))))

    if style == "markdown":
        # Generate markdown table
        # Header row
        header_row = f"| {' | '.join(h.ljust(w) for h, w in zip(headers, col_widths))} |"
        renderer._wln(header_row)
        
        # Separator row
        separator_row = f"| {' | '.join('-' * w for w in col_widths)} |"
        renderer._wln(separator_row)
        
        # Data rows
        for row in rows:
            row_cells = []
            for i in range(len(col_widths)):
                cell = str(row[i]) if i < len(row) else ""
                w = col_widths[i] if i < len(col_widths) else 10
                row_cells.append(cell.ljust(w))
            row_line = f"| {' | '.join(row_cells)} |"
            renderer._wln(row_line)
        return

    # Top border
    if chars["top_left"]:
        top = (
            chars["top_left"]
            + chars["top_mid"].join(chars["horizontal"] * w for w in col_widths)
            + chars["top_right"]
        )
        renderer._wln(renderer._c(top, "\033[2m"))

    # Header
    if headers:
        header_cells = []
        for i, h in enumerate(headers):
            w = col_widths[i] if i < len(col_widths) else 10
            colored = renderer._c(str(h), "\033[1m", "\033[36m")
            header_cells.append(colored.ljust(w))

        header_line = f"{chars['vertical']}{chars['vertical'].join(header_cells)}{chars['vertical']}"
        renderer._wln(header_line)

        # Header separator
        sep = (
            chars["mid_left"]
            + chars["mid_mid"].join(chars["horizontal"] * w for w in col_widths)
            + chars["mid_right"]
        )
        renderer._wln(renderer._c(sep, "\033[2m"))

    # Rows
    for row in rows:
        row_cells = []
        for i in range(len(col_widths)):
            cell = str(row[i]) if i < len(row) else ""
            w = col_widths[i] if i < len(col_widths) else 10
            row_cells.append(cell.ljust(w))

        row_line = f"{chars['vertical']}{chars['vertical'].join(row_cells)}{chars['vertical']}"
        renderer._wln(row_line)

    # Bottom border
    if chars["bottom_left"]:
        bottom = (
            chars["bottom_left"]
            + chars["bottom_mid"].join(chars["horizontal"] * w for w in col_widths)
            + chars["bottom_right"]
        )
        renderer._wln(renderer._c(bottom, "\033[2m"))


def panel(
    content: str,
    title: str = "",
    style_color: str = "\033[36m",
) -> None:
    """Render a bordered panel."""
    renderer = get_renderer()
    lines = content.split("\n")
    max_len = max((len(strip_ansi(line)) for line in lines), default=0)
    if title:
        max_len = max(max_len, len(title) + 2)
    box_w = max_len + 4

    title_str = f" {title} " if title else ""
    top = f"╭{'─' * 2}{title_str}{'─' * max(0, box_w - len(title_str) - 2)}╮"
    bot = f"╰{'─' * box_w}╯"

    renderer._wln(renderer._c(top, style_color))
    for line in lines:
        pad = max_len - len(strip_ansi(line))
        renderer._wln(
            renderer._c("│ ", style_color)
            + renderer._inline(line)
            + " " * pad
            + renderer._c(" │", style_color)
        )
    renderer._wln(renderer._c(bot, style_color))


def blockquote(content: str) -> None:
    """Render a blockquote."""
    get_renderer().blockquote(content)
