"""Syntax highlighting for code blocks in terminal output.

Provides language-specific syntax highlighting rules and functions
for applying ANSI color codes to code blocks.
"""

import re
from dataclasses import dataclass

from .ansi import (
    FG_BLUE,
    FG_CYAN,
    FG_GRAY,
    FG_GREEN,
    FG_MAGENTA,
    FG_RED,
    FG_YELLOW,
    RESET,
)

# ── Highlighter rule ─────────────────────────────────────────────────────


@dataclass
class HighlightRule:
    """Highlighter rule: pattern + color."""

    pattern: re.Pattern
    color: str


# ── Language highlighters builder ────────────────────────────────────────


def _make_highlighters() -> dict[str, list[HighlightRule]]:
    """Build language-specific highlighter rules."""
    python_kw = (
        r"\b(def|class|if|elif|else|for|while|return|import|from|as|try|except|"
        r"finally|with|yield|raise|pass|break|continue|and|or|not|in|is|None|"
        r"True|False|self|async|await|lambda|global|nonlocal)\b"
    )
    return {
        "python": [
            HighlightRule(re.compile(r"#.*$", re.M), FG_GRAY),
            HighlightRule(re.compile(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\''), FG_GREEN),
            HighlightRule(re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\''), FG_GREEN),
            HighlightRule(re.compile(r"@\w+"), FG_YELLOW),
            HighlightRule(re.compile(python_kw), FG_BLUE),
            HighlightRule(re.compile(r"\b\d+\.?\d*\b"), FG_CYAN),
        ],
        "javascript": [
            HighlightRule(re.compile(r"//.*$", re.M), FG_GRAY),
            HighlightRule(re.compile(r"/\*[\s\S]*?\*/"), FG_GRAY),
            HighlightRule(
                re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\'|`[^`]*`'),
                FG_GREEN,
            ),
            HighlightRule(
                re.compile(
                    r"\b(const|let|var|function|return|if|else|for|while|class|import|"
                    r"export|from|async|await|try|catch|throw|new|this|typeof|null|"
                    r"undefined|true|false)\b"
                ),
                FG_BLUE,
            ),
            HighlightRule(re.compile(r"\b\d+\.?\d*\b"), FG_CYAN),
        ],
        "typescript": [],  # filled below
        "bash": [
            HighlightRule(re.compile(r"#.*$", re.M), FG_GRAY),
            HighlightRule(re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\']*\''), FG_GREEN),
            HighlightRule(
                re.compile(
                    r"\b(if|then|else|elif|fi|for|do|done|while|case|esac|function|"
                    r"return|local|export|source|echo|exit|cd|ls|grep|awk|sed|cat|"
                    r"mkdir|rm|cp|mv|chmod|sudo|apt|pip|npm|git|docker)\b"
                ),
                FG_BLUE,
            ),
            HighlightRule(re.compile(r"\$\{?\w+\}?"), FG_CYAN),
        ],
        "json": [
            HighlightRule(re.compile(r'"[^"]*"\s*(?=: )'), FG_CYAN),
            HighlightRule(re.compile(r'"[^"]*"'), FG_GREEN),
            HighlightRule(re.compile(r"\b(true|false|null)\b"), FG_BLUE),
            HighlightRule(re.compile(r"-?\b\d+\.?\d*\b"), FG_MAGENTA),
        ],
        "yaml": [
            HighlightRule(re.compile(r"#.*$", re.M), FG_GRAY),
            HighlightRule(re.compile(r"^[\w._-]+(?=\s*:)", re.M), FG_CYAN),
            HighlightRule(re.compile(r'"[^"]*"|\'[^\']*\''), FG_GREEN),
            HighlightRule(re.compile(r"\b(true|false|null|yes|no)\b", re.I), FG_BLUE),
        ],
        "toml": [
            HighlightRule(re.compile(r"#.*$", re.M), FG_GRAY),
            HighlightRule(re.compile(r"^\[.*\]", re.M), f"{FG_CYAN}{FG_BLUE}"),
            HighlightRule(re.compile(r"^[\w._-]+(?=\s*=)", re.M), FG_CYAN),
            HighlightRule(re.compile(r'"[^"]*"|\'[^\']*\''), FG_GREEN),
            HighlightRule(re.compile(r"\b(true|false)\b"), FG_BLUE),
        ],
        "sql": [
            HighlightRule(re.compile(r"--.*$", re.M), FG_GRAY),
            HighlightRule(
                re.compile(
                    r"\b(SELECT|FROM|WHERE|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|"
                    r"TABLE|INDEX|JOIN|LEFT|RIGHT|INNER|OUTER|ON|AND|OR|NOT|IN|"
                    r"ORDER|BY|GROUP|HAVING|LIMIT|AS|SET|VALUES|INTO|NULL|"
                    r"PRIMARY|KEY|FOREIGN|REFERENCES|DISTINCT|COUNT|SUM|AVG)\b",
                    re.I,
                ),
                FG_BLUE,
            ),
            HighlightRule(re.compile(r"'[^']*'"), FG_GREEN),
        ],
        "rust": [
            HighlightRule(re.compile(r"//.*$", re.M), FG_GRAY),
            HighlightRule(re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"'), FG_GREEN),
            HighlightRule(
                re.compile(
                    r"\b(fn|let|mut|const|struct|enum|impl|trait|pub|use|mod|crate|"
                    r"self|super|if|else|match|for|while|loop|return|break|continue|"
                    r"async|await|move|ref|where|type|dyn|unsafe|extern)\b"
                ),
                FG_BLUE,
            ),
            HighlightRule(
                re.compile(
                    r"\b(i8|i16|i32|i64|u8|u16|u32|u64|f32|f64|bool|str|String|Vec|Option|Result|Self)\b"
                ),
                FG_CYAN,
            ),
            HighlightRule(re.compile(r"#\[.*?\]"), FG_YELLOW),
        ],
        "go": [
            HighlightRule(re.compile(r"//.*$", re.M), FG_GRAY),
            HighlightRule(re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"|`[^`]*`'), FG_GREEN),
            HighlightRule(
                re.compile(
                    r"\b(func|var|const|type|struct|interface|map|chan|go|select|"
                    r"if|else|for|range|switch|case|default|return|break|continue|"
                    r"defer|package|import|nil|true|false)\b"
                ),
                FG_BLUE,
            ),
        ],
        "dockerfile": [
            HighlightRule(re.compile(r"#.*$", re.M), FG_GRAY),
            HighlightRule(
                re.compile(
                    r"^(FROM|RUN|CMD|COPY|ADD|EXPOSE|ENV|ARG|WORKDIR|ENTRYPOINT|"
                    r"VOLUME|USER|LABEL|HEALTHCHECK|SHELL)\b",
                    re.M,
                ),
                f"{FG_BLUE}{FG_BLUE}",
            ),
            HighlightRule(re.compile(r'"[^"]*"'), FG_GREEN),
        ],
        "log": [
            HighlightRule(re.compile(r".*\b(error|fail|critical|fatal)\b.*", re.I), FG_RED),
            HighlightRule(re.compile(r".*\b(warn|warning|⚠️)\b.*", re.I), FG_YELLOW),
            HighlightRule(re.compile(r".*\b(success|ok|✅|done|complete)\b.*", re.I), FG_GREEN),
            HighlightRule(re.compile(r".*\b(info|ℹ️|🚀|📦)\b.*", re.I), FG_BLUE),
        ],
    }


# ── Highlighters registry ────────────────────────────────────────────────

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


# ── Public API ───────────────────────────────────────────────────────────


def highlight_code(code: str, lang: str) -> str:
    """Apply syntax highlighting to a code block.

    Args:
        code: The code string to highlight.
        lang: The programming language identifier.

    Returns:
        The code string with ANSI color codes applied.
    """
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
            overlaps = any(not (end <= hs or start >= he) for hs, he, _ in highlights)
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
