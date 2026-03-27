"""Core markdown renderer with syntax highlighting for terminal output.

Provides MarkdownRenderer class and convenience functions for rendering
markdown text with ANSI color codes in the terminal.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from io import StringIO
from typing import IO, TextIO


# ── ANSI helpers ──────────────────────────────────────────────────────────

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

FG_RED = "\033[31m"
FG_GREEN = "\033[32m"
FG_YELLOW = "\033[33m"
FG_BLUE = "\033[34m"
FG_MAGENTA = "\033[35m"
FG_CYAN = "\033[36m"
FG_WHITE = "\033[37m"
FG_GRAY = "\033[90m"
FG_BRIGHT_RED = "\033[91m"
FG_BRIGHT_GREEN = "\033[92m"
FG_BRIGHT_YELLOW = "\033[93m"
FG_BRIGHT_BLUE = "\033[94m"
FG_BRIGHT_MAGENTA = "\033[95m"
FG_BRIGHT_CYAN = "\033[96m"

BG_GRAY = "\033[48;5;236m"

_ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    """Remove all ANSI escape codes from text."""
    return _ANSI_RE.sub("", text)


def _is_no_color() -> bool:
    """Check if NO_COLOR env is set (https://no-color.org)."""
    return "NO_COLOR" in os.environ


def _supports_color(stream: IO | None = None) -> bool:
    """Detect if the output stream supports color."""
    if _is_no_color():
        return False
    s = stream or sys.stdout
    if hasattr(s, "isatty") and s.isatty():
        return True
    if os.environ.get("FORCE_COLOR"):
        return True
    return False


# ── Markdown detection ────────────────────────────────────────────────────

_MD_PATTERNS = [
    re.compile(r"^#{1,6}\s"),          # headings
    re.compile(r"\*\*[^*]+\*\*"),      # bold
    re.compile(r"\*[^*]+\*"),          # italic
    re.compile(r"`[^`]+`"),            # inline code
    re.compile(r"^```"),               # code fences
    re.compile(r"^\s*[-*]\s"),         # list items
    re.compile(r"^\s*\d+\.\s"),        # numbered lists
    re.compile(r"\[.+\]\(.+\)"),       # links
    re.compile(r"^>\s"),               # blockquotes
    re.compile(r"^---\s*$"),           # horizontal rules
]


def looks_like_markdown(text: str) -> bool:
    """Heuristic: does the text contain markdown formatting?"""
    lines = text.strip().split("\n")
    score = 0
    for line in lines[:20]:
        for pat in _MD_PATTERNS:
            if pat.search(line):
                score += 1
    return score >= 1


# ── Syntax Highlighters ──────────────────────────────────────────────────

@dataclass
class _HL:
    """Highlighter rule: pattern + color."""
    pattern: re.Pattern
    color: str


def _make_highlighters() -> dict[str, list[_HL]]:
    """Build language-specific highlighter rules."""
    python_kw = (
        r"\b(def|class|if|elif|else|for|while|return|import|from|as|try|except|"
        r"finally|with|yield|raise|pass|break|continue|and|or|not|in|is|None|"
        r"True|False|self|async|await|lambda|global|nonlocal)\b"
    )
    return {
        "python": [
            _HL(re.compile(r"#.*$", re.M), FG_GRAY),
            _HL(re.compile(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\''), FG_GREEN),
            _HL(re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\''), FG_GREEN),
            _HL(re.compile(r"@\w+"), FG_YELLOW),
            _HL(re.compile(python_kw), FG_BLUE),
            _HL(re.compile(r"\b\d+\.?\d*\b"), FG_CYAN),
        ],
        "javascript": [
            _HL(re.compile(r"//.*$", re.M), FG_GRAY),
            _HL(re.compile(r"/\*[\s\S]*?\*/"), FG_GRAY),
            _HL(re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\'|`[^`]*`'), FG_GREEN),
            _HL(re.compile(
                r"\b(const|let|var|function|return|if|else|for|while|class|import|"
                r"export|from|async|await|try|catch|throw|new|this|typeof|null|"
                r"undefined|true|false)\b"
            ), FG_BLUE),
            _HL(re.compile(r"\b\d+\.?\d*\b"), FG_CYAN),
        ],
        "typescript": [],  # filled below
        "bash": [
            _HL(re.compile(r"#.*$", re.M), FG_GRAY),
            _HL(re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\']*\''), FG_GREEN),
            _HL(re.compile(
                r"\b(if|then|else|elif|fi|for|do|done|while|case|esac|function|"
                r"return|local|export|source|echo|exit|cd|ls|grep|awk|sed|cat|"
                r"mkdir|rm|cp|mv|chmod|sudo|apt|pip|npm|git|docker)\b"
            ), FG_BLUE),
            _HL(re.compile(r"\$\{?\w+\}?"), FG_CYAN),
        ],
        "json": [
            _HL(re.compile(r'"[^"]*"\s*(?=:)'), FG_CYAN),
            _HL(re.compile(r'"[^"]*"'), FG_GREEN),
            _HL(re.compile(r"\b(true|false|null)\b"), FG_BLUE),
            _HL(re.compile(r"-?\b\d+\.?\d*\b"), FG_MAGENTA),
        ],
        "yaml": [
            _HL(re.compile(r"#.*$", re.M), FG_GRAY),
            _HL(re.compile(r"^[\w._-]+(?=\s*:)", re.M), FG_CYAN),
            _HL(re.compile(r'"[^"]*"|\'[^\']*\''), FG_GREEN),
            _HL(re.compile(r"\b(true|false|null|yes|no)\b", re.I), FG_BLUE),
        ],
        "toml": [
            _HL(re.compile(r"#.*$", re.M), FG_GRAY),
            _HL(re.compile(r"^\[.*\]", re.M), FG_CYAN + BOLD),
            _HL(re.compile(r'^[\w._-]+(?=\s*=)', re.M), FG_CYAN),
            _HL(re.compile(r'"[^"]*"|\'[^\']*\''), FG_GREEN),
            _HL(re.compile(r"\b(true|false)\b"), FG_BLUE),
        ],
        "sql": [
            _HL(re.compile(r"--.*$", re.M), FG_GRAY),
            _HL(re.compile(
                r"\b(SELECT|FROM|WHERE|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|"
                r"TABLE|INDEX|JOIN|LEFT|RIGHT|INNER|OUTER|ON|AND|OR|NOT|IN|"
                r"ORDER|BY|GROUP|HAVING|LIMIT|AS|SET|VALUES|INTO|NULL|"
                r"PRIMARY|KEY|FOREIGN|REFERENCES|DISTINCT|COUNT|SUM|AVG)\b",
                re.I,
            ), FG_BLUE),
            _HL(re.compile(r"'[^']*'"), FG_GREEN),
        ],
        "rust": [
            _HL(re.compile(r"//.*$", re.M), FG_GRAY),
            _HL(re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"'), FG_GREEN),
            _HL(re.compile(
                r"\b(fn|let|mut|const|struct|enum|impl|trait|pub|use|mod|crate|"
                r"self|super|if|else|match|for|while|loop|return|break|continue|"
                r"async|await|move|ref|where|type|dyn|unsafe|extern)\b"
            ), FG_BLUE),
            _HL(re.compile(r"\b(i8|i16|i32|i64|u8|u16|u32|u64|f32|f64|bool|str|String|Vec|Option|Result|Self)\b"), FG_CYAN),
            _HL(re.compile(r"#\[.*?\]"), FG_YELLOW),
        ],
        "go": [
            _HL(re.compile(r"//.*$", re.M), FG_GRAY),
            _HL(re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"|`[^`]*`'), FG_GREEN),
            _HL(re.compile(
                r"\b(func|var|const|type|struct|interface|map|chan|go|select|"
                r"if|else|for|range|switch|case|default|return|break|continue|"
                r"defer|package|import|nil|true|false)\b"
            ), FG_BLUE),
        ],
        "dockerfile": [
            _HL(re.compile(r"#.*$", re.M), FG_GRAY),
            _HL(re.compile(r"^(FROM|RUN|CMD|COPY|ADD|EXPOSE|ENV|ARG|WORKDIR|ENTRYPOINT|VOLUME|USER|LABEL|HEALTHCHECK|SHELL)\b", re.M), FG_BLUE + BOLD),
            _HL(re.compile(r'"[^"]*"'), FG_GREEN),
        ],
        "log": [
            _HL(re.compile(r".*\b(error|fail|critical|fatal)\b.*", re.I), FG_RED),
            _HL(re.compile(r".*\b(warn|warning|⚠️)\b.*", re.I), FG_YELLOW),
            _HL(re.compile(r".*\b(success|ok|✅|done|complete)\b.*", re.I), FG_GREEN),
            _HL(re.compile(r".*\b(info|ℹ️|🚀|📦)\b.*", re.I), FG_BLUE),
        ],
    }


_HIGHLIGHTERS = _make_highlighters()
_HIGHLIGHTERS["typescript"] = _HIGHLIGHTERS["javascript"]
_HIGHLIGHTERS["js"] = _HIGHLIGHTERS["javascript"]
_HIGHLIGHTERS["ts"] = _HIGHLIGHTERS["typescript"]
_HIGHLIGHTERS["sh"] = _HIGHLIGHTERS["bash"]
_HIGHLIGHTERS["shell"] = _HIGHLIGHTERS["bash"]
_HIGHLIGHTERS["zsh"] = _HIGHLIGHTERS["bash"]
_HIGHLIGHTERS["py"] = _HIGHLIGHTERS["python"]
_HIGHLIGHTERS["yml"] = _HIGHLIGHTERS["yaml"]
_HIGHLIGHTERS["rs"] = _HIGHLIGHTERS["rust"]


def _highlight_code(code: str, lang: str) -> str:
    """Apply syntax highlighting to a code block."""
    rules = _HIGHLIGHTERS.get(lang.lower(), [])
    if not rules:
        return code

    # For log-style highlighting, apply line-by-line matching
    if lang.lower() == "log":
        lines = code.split("\n")
        result = []
        for line in lines:
            colored = line
            for rule in rules:
                if rule.pattern.search(line):
                    colored = f"{rule.color}{line}{RESET}"
                    break
            result.append(colored)
        return "\n".join(result)

    # For other languages, apply pattern-based highlighting
    # We track positions to avoid overlapping highlights
    highlights: list[tuple[int, int, str]] = []  # (start, end, color)
    for rule in rules:
        for m in rule.pattern.finditer(code):
            start, end = m.start(), m.end()
            # Skip if overlapping with existing highlight
            overlaps = any(
                not (end <= hs or start >= he) for hs, he, _ in highlights
            )
            if not overlaps:
                highlights.append((start, end, rule.color))

    if not highlights:
        return code

    # Sort by position and build result
    highlights.sort(key=lambda x: x[0])
    parts = []
    pos = 0
    for start, end, color in highlights:
        if start > pos:
            parts.append(code[pos:start])
        parts.append(f"{color}{code[start:end]}{RESET}")
        pos = end
    if pos < len(code):
        parts.append(code[pos:])

    return "".join(parts)


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
        self.use_colors = use_colors and _supports_color(self.stream)
        self._width = width

    @property
    def width(self) -> int:
        if self._width:
            return self._width
        try:
            return shutil.get_terminal_size().columns
        except Exception:
            return 80

    def _w(self, text: str) -> None:
        """Write text to stream."""
        self.stream.write(text)

    def _wln(self, text: str = "") -> None:
        """Write line to stream."""
        self.stream.write(text + "\n")

    def _c(self, text: str, *codes: str) -> str:
        """Colorize text if colors enabled."""
        if not self.use_colors or not codes:
            return text
        return "".join(codes) + text + RESET

    # ── Block renderers ───────────────────────────────────────────────

    def heading(self, level: int, text: str) -> None:
        colors = [FG_BRIGHT_CYAN, FG_BRIGHT_BLUE, FG_BRIGHT_MAGENTA, FG_CYAN, FG_BLUE, FG_MAGENTA]
        color = colors[min(level - 1, len(colors) - 1)]
        prefix = "━" * min(level, 3) + " " if level <= 2 else ""
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
            highlighted = _highlight_code(code, lang)
        else:
            highlighted = code
        for line in highlighted.split("\n"):
            self._wln(self._c("│ ", DIM) + line)
        self._wln(self._c(f"└{'─' * 42}┘", DIM))

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
    render_markdown(text, stream=buf, use_colors=_supports_color())
    return buf.getvalue()
