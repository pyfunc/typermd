"""Core markdown renderer with syntax highlighting for terminal output.

Provides MarkdownRenderer class and convenience functions for rendering
markdown text with ANSI color codes in the terminal.
"""

import re
import shutil
import sys
from io import StringIO
from typing import TextIO

from .ansi import (
    BG_GRAY,
    BOLD,
    DEFAULT_PANEL_WIDTH,
    DEFAULT_TERMINAL_WIDTH,
    DIM,
    FG_BLUE,
    FG_BRIGHT_BLUE,
    FG_BRIGHT_CYAN,
    FG_BRIGHT_MAGENTA,
    FG_BRIGHT_YELLOW,
    FG_CYAN,
    FG_GRAY,
    FG_GREEN,
    FG_MAGENTA,
    FG_YELLOW,
    ITALIC,
    MAX_LINES_TO_CHECK,
    RESET,
    UNDERLINE,
    strip_ansi,
    supports_color,
)
from .highlighting import highlight_code


# ── Markdown detection ────────────────────────────────────────────────────

_MD_PATTERNS = [
    re.compile(r"^#{1,6}\s"),  # headings
    re.compile(r"\*\*[^*]+\*\*"),  # bold
    re.compile(r"\*[^*]+\*"),  # italic
    re.compile(r"`[^`]+`"),  # inline code
    re.compile(r"^```"),  # code fences
    re.compile(r"^\s*[-*]\s"),  # list items
    re.compile(r"^\s*\d+\.\s"),  # numbered lists
    re.compile(r"\[.+\]\(.+\)"),  # links
    re.compile(r"^>\s"),  # blockquotes
    re.compile(r"^---\s*$"),  # horizontal rules
]


def looks_like_markdown(text: str) -> bool:
    """Heuristic: does the text contain markdown formatting?"""
    lines = text.strip().split("\n")
    score = 0
    for line in lines[:MAX_LINES_TO_CHECK]:
        for pat in _MD_PATTERNS:
            if pat.search(line):
                score += 1
    return score >= 1


# ── MarkdownRenderer ─────────────────────────────────────────────────────


class MarkdownRenderer:
    """Renders markdown text to the terminal with ANSI colors."""

    def __init__(
        self,
        stream: TextIO | None = None,
        use_colors: bool = True,
        width: int | None = None,
    ):
        self.stream = stream or sys.stdout
        self.use_colors = use_colors and supports_color(self.stream)
        self._width = width

    @property
    def width(self) -> int:
        if self._width:
            return self._width
        try:
            return shutil.get_terminal_size().columns
        except Exception:
            return DEFAULT_TERMINAL_WIDTH

    def _w(self, text: str) -> None:
        """Write text to stream."""
        self.stream.write(text)

    def _wln(self, text: str = "") -> None:
        """Write line to stream."""
        self.stream.write(f"{text}\n")

    def _c(self, text: str, *codes: str) -> str:
        """Colorize text if colors enabled."""
        if not self.use_colors or not codes:
            return text
        return f"{''.join(codes)}{text}{RESET}"

    # ── Block renderers ───────────────────────────────────────────────

    def heading(self, level: int, text: str) -> None:
        colors = [FG_BRIGHT_CYAN, FG_BRIGHT_BLUE, FG_BRIGHT_MAGENTA, FG_CYAN, FG_BLUE, FG_MAGENTA]
        color = colors[min(level - 1, len(colors) - 1)]
        prefix = f"{'━' * min(level, 3)}{' ' if level <= 2 else ''}"
        self._wln()
        self._wln(self._c(f"{prefix}{text}", BOLD, color))
        if level <= 2:
            bar_char = "━" if level == 1 else "─"
            bar_len = min(len(strip_ansi(text)) + len(prefix) + 4, self.width - 2)
            self._wln(self._c(bar_char * bar_len, DIM, color))

    def codeblock(self, lang: str, code: str) -> None:
        label = f" {lang} " if lang else ""
        border = self._c(f"┌{'─' * 2}{label}{'─' * max(0, 40 - len(label))}┐", DIM)
        self._wln(border)
        if self.use_colors:
            highlighted = highlight_code(code, lang)
        else:
            highlighted = code
        for line in highlighted.split("\n"):
            self._wln(self._c("│ ", DIM) + line)
        self._wln(self._c(f"└{'─' * DEFAULT_PANEL_WIDTH}┘", DIM))

    def blockquote(self, text: str) -> None:
        for line in text.split("\n"):
            self._wln(self._c("  ▎ ", FG_GRAY) + self._c(line, ITALIC, FG_GRAY))

    def horizontal_rule(self) -> None:
        self._wln(self._c("─" * min(60, self.width - 2), DIM))

    def list_item(self, text: str, indent: int = 0) -> None:
        bullet = self._c("  •", FG_CYAN)
        pad = "  " * indent
        self._wln(f"{pad}{bullet} {self._inline(text)}")

    def numbered_item(self, num: int, text: str, indent: int = 0) -> None:
        marker = self._c(f"  {num}.", FG_CYAN)
        pad = "  " * indent
        self._wln(f"{pad}{marker} {self._inline(text)}")

    def paragraph(self, text: str) -> None:
        self._wln(self._inline(text))

    def checklist_item(self, checked: bool, text: str) -> None:
        mark = self._c("✓", FG_GREEN, BOLD) if checked else self._c("○", DIM)
        self._wln(f"  {mark} {self._inline(text)}")

    # ── Inline formatting ─────────────────────────────────────────────

    def _inline(self, text: str) -> str:
        """Apply inline markdown formatting."""
        if not self.use_colors:
            # Strip markdown markers when no color
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
            text = re.sub(r"\*(.+?)\*", r"\1", text)
            text = re.sub(r"`(.+?)`", r"\1", text)
            text = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1 (\2)", text)
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
            lambda m: f"{BG_GRAY}{FG_BRIGHT_YELLOW} {m.group(1)} {RESET}",
            text,
        )
        # Links
        text = re.sub(
            r"\[(.+?)\]\((.+?)\)",
            lambda m: f"{UNDERLINE}{FG_BLUE}{m.group(1)}{RESET}{DIM} ({m.group(2)}){RESET}",
            text,
        )
        return text

    # ── Full render ───────────────────────────────────────────────────

    def render(self, text: str) -> None:
        """Render a complete markdown document."""
        lines = text.split("\n")
        in_code = False
        code_lang = ""
        code_lines: list[str] = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Code fence toggle
            if line.strip().startswith("```"):
                if not in_code:
                    in_code = True
                    code_lang = line.strip()[3:].strip()
                    code_lines = []
                else:
                    self.codeblock(code_lang, "\n".join(code_lines))
                    in_code = False
                    code_lang = ""
                    code_lines = []
                i += 1
                continue

            if in_code:
                code_lines.append(line)
                i += 1
                continue

            stripped = line.strip()

            # Empty line
            if not stripped:
                self._wln()
                i += 1
                continue

            # Headings
            m = re.match(r"^(#{1,6})\s+(.+)$", stripped)
            if m:
                self.heading(len(m.group(1)), m.group(2))
                i += 1
                continue

            # Horizontal rule
            if re.match(r"^[-*_]{3,}\s*$", stripped):
                self.horizontal_rule()
                i += 1
                continue

            # Checklist items
            m = re.match(r"^\s*[-*]\s+\[([ xX])\]\s+(.+)$", stripped)
            if m:
                checked = m.group(1).lower() == "x"
                self.checklist_item(checked, m.group(2))
                i += 1
                continue

            # Bullet list items
            m = re.match(r"^(\s*)[-*]\s+(.+)$", line)
            if m:
                indent = len(m.group(1)) // 2
                self.list_item(m.group(2), indent)
                i += 1
                continue

            # Numbered list items
            m = re.match(r"^(\s*)\d+\.\s+(.+)$", line)
            if m:
                indent = len(m.group(1)) // 2
                num_m = re.match(r"\s*(\d+)\.", line)
                num = int(num_m.group(1)) if num_m else 1
                self.numbered_item(num, m.group(2), indent)
                i += 1
                continue

            # Blockquote
            if stripped.startswith("> "):
                bq_lines = []
                while i < len(lines) and lines[i].strip().startswith("> "):
                    bq_lines.append(lines[i].strip()[2:])
                    i += 1
                self.blockquote("\n".join(bq_lines))
                continue

            # Regular paragraph
            self.paragraph(stripped)
            i += 1


# ── Convenience functions ─────────────────────────────────────────────────

_default_renderer: MarkdownRenderer | None = None


def get_renderer(
    stream: TextIO | None = None,
    use_colors: bool = True,
) -> MarkdownRenderer:
    """Get or create the default MarkdownRenderer."""
    global _default_renderer
    if stream is None and _default_renderer is not None:
        return _default_renderer
    renderer = MarkdownRenderer(stream=stream, use_colors=use_colors)
    if stream is None:
        _default_renderer = renderer
    return renderer


def render_markdown(
    text: str,
    stream: TextIO | None = None,
    use_colors: bool = True,
) -> None:
    """Render markdown text to a stream."""
    renderer = get_renderer(stream=stream, use_colors=use_colors)
    renderer.render(text)


def md(text: str) -> None:
    """Render markdown text to stdout. Primary convenience function."""
    render_markdown(text)


def render_to_string(text: str) -> str:
    """Render markdown and return as string."""
    buf = StringIO()
    render_markdown(text, stream=buf, use_colors=supports_color())
    return buf.getvalue()
