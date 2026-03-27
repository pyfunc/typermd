"""ANSI color codes and terminal utility functions.

Provides ANSI escape codes for terminal colors and text formatting,
along with utility functions for detecting color support and stripping
ANSI codes from text.
"""

import os
import re
import sys
from typing import IO

# ── Constants ───────────────────────────────────────────────────────────

MAX_LINES_TO_CHECK = 20
DEFAULT_TERMINAL_WIDTH = 80
DEFAULT_PANEL_WIDTH = 42

# ── ANSI color codes ────────────────────────────────────────────────────

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

# Foreground colors
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

# Background colors
BG_GRAY = "\033[48;5;236m"

# ── ANSI regex pattern ───────────────────────────────────────────────────

_ANSI_RE = re.compile(r"\033\[[0-9;]*m")

# ── Utility functions ────────────────────────────────────────────────────


def strip_ansi(text: str) -> str:
    """Remove all ANSI escape codes from text."""
    return _ANSI_RE.sub("", text)


def is_no_color() -> bool:
    """Check if NO_COLOR env is set (https://no-color.org)."""
    return "NO_COLOR" in os.environ


def supports_color(stream: IO | None = None) -> bool:
    """Detect if the output stream supports color."""
    if is_no_color():
        return False
    s = stream or sys.stdout
    if hasattr(s, "isatty") and s.isatty():
        return True
    if os.environ.get("FORCE_COLOR"):
        return True
    return False
