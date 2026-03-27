"""Table rendering utilities for terminal output.

Provides table styling and rendering functions with support for multiple
border styles (unicode, ascii, minimal, none, markdown).
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .renderer import MarkdownRenderer


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


def _calculate_column_widths(headers: list[str], rows: list[list[str]]) -> list[int]:
    """Calculate the maximum width for each column."""
    from .renderer import strip_ansi
    
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(strip_ansi(str(cell))))
    return col_widths


def _render_markdown_table(
    renderer: "MarkdownRenderer",
    headers: list[str],
    rows: list[list[str]],
    col_widths: list[int],
) -> None:
    """Render a table in markdown format."""
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


def _render_table_border(
    renderer: "MarkdownRenderer",
    chars: dict[str, str],
    col_widths: list[int],
    border_type: str,
) -> None:
    """Render a table border (top, middle, or bottom)."""
    if border_type == "top":
        left, mid, right = chars["top_left"], chars["top_mid"], chars["top_right"]
    elif border_type == "middle":
        left, mid, right = chars["mid_left"], chars["mid_mid"], chars["mid_right"]
    else:  # bottom
        left, mid, right = chars["bottom_left"], chars["bottom_mid"], chars["bottom_right"]
    
    if left:  # Only render if the style has borders
        border = (
            left
            + mid.join(chars["horizontal"] * w for w in col_widths)
            + right
        )
        renderer._wln(renderer._c(border, "\033[2m"))


def _render_table_header(
    renderer: "MarkdownRenderer",
    headers: list[str],
    col_widths: list[int],
    chars: dict[str, str],
) -> None:
    """Render the table header row."""
    if not headers:
        return
        
    header_cells = []
    for i, h in enumerate(headers):
        w = col_widths[i] if i < len(col_widths) else 10
        colored = renderer._c(str(h), "\033[1m", "\033[36m")
        header_cells.append(colored.ljust(w))

    header_line = f"{chars['vertical']}{chars['vertical'].join(header_cells)}{chars['vertical']}"
    renderer._wln(header_line)


def _render_table_rows(
    renderer: "MarkdownRenderer",
    rows: list[list[str]],
    col_widths: list[int],
    chars: dict[str, str],
) -> None:
    """Render all data rows in the table."""
    for row in rows:
        row_cells = []
        for i in range(len(col_widths)):
            cell = str(row[i]) if i < len(row) else ""
            w = col_widths[i] if i < len(col_widths) else 10
            row_cells.append(cell.ljust(w))

        row_line = f"{chars['vertical']}{chars['vertical'].join(row_cells)}{chars['vertical']}"
        renderer._wln(row_line)


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
    from .renderer import get_renderer
    
    renderer = get_renderer()
    chars = _get_table_chars(style)
    col_widths = _calculate_column_widths(headers, rows)
    
    if style == "markdown":
        _render_markdown_table(renderer, headers, rows, col_widths)
        return
    
    # Top border
    _render_table_border(renderer, chars, col_widths, "top")
    
    # Header section
    _render_table_header(renderer, headers, col_widths, chars)
    
    # Header separator
    if headers:
        _render_table_border(renderer, chars, col_widths, "middle")
    
    # Data rows
    _render_table_rows(renderer, rows, col_widths, chars)
    
    # Bottom border
    _render_table_border(renderer, chars, col_widths, "bottom")
