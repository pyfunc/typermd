"""Markdown-aware structured logger for CLI applications.

Provides a Logger class that emits output using markdown code blocks,
automatically colorizing log levels.

Usage:
    from typermd.logger import get_logger

    log = get_logger("myapp")
    log.info("Starting process...")
    log.success("Build complete!")
    log.warning("Deprecated API")
    log.error("Connection failed")
"""


import sys
from typing import TextIO

from typermd.ansi import (
    BOLD,
    DIM,
    FG_BLUE,
    FG_CYAN,
    FG_GRAY,
    FG_GREEN,
    FG_RED,
    FG_YELLOW,
    RESET,
    supports_color,
)


class Logger:
    """Markdown-aware structured logger.

    All output is emitted as styled text to the specified stream.
    """

    def __init__(
        self,
        name: str = "app",
        verbose: bool = False,
        stream: TextIO | None = None,
        use_colors: bool = True,
    ) -> None:
        self.name = name
        self.verbose = verbose
        self.stream = stream or sys.stderr
        self.use_colors = use_colors and supports_color(self.stream)

    def _c(self, text: str, *codes: str) -> str:
        if not self.use_colors or not codes:
            return text
        return f"{''.join(codes)}{text}{RESET}"

    def _emit(self, icon: str, level: str, message: str, color: str) -> None:
        tag = self._c(f"[{level:>7}]", color, BOLD)
        name = self._c(f"({self.name})", DIM)
        self.stream.write(f"{icon} {tag} {name} {message}\n")

    def debug(self, message: str) -> None:
        """Log a debug message (only in verbose mode)."""
        if self.verbose:
            self._emit("🔍", "DEBUG", message, FG_GRAY)

    def info(self, message: str) -> None:
        """Log an info message."""
        self._emit("ℹ️ ", "INFO", message, FG_BLUE)

    def success(self, message: str) -> None:
        """Log a success message."""
        self._emit("✅", "SUCCESS", message, FG_GREEN)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self._emit("⚠️ ", "WARN", message, FG_YELLOW)

    def error(self, message: str) -> None:
        """Log an error message."""
        self._emit("❌", "ERROR", message, FG_RED)

    def action(self, action: str, detail: str = "") -> None:
        """Log an action step."""
        act = self._c(action, FG_CYAN, BOLD)
        self.stream.write(f"  → {act} {detail}\n")

    def step(self, num: int, total: int, message: str) -> None:
        """Log a numbered step."""
        counter = self._c(f"[{num}/{total}]", FG_CYAN)
        self.stream.write(f"  {counter} {message}\n")


# ── Module-level convenience ──────────────────────────────────────────────

_logger: Logger | None = None


def get_logger(name: str = "app", verbose: bool = False) -> Logger:
    """Get or create the default logger."""
    global _logger
    if _logger is None or _logger.name != name:
        _logger = Logger(name=name, verbose=verbose)
    return _logger


def set_logger(logger: Logger) -> None:
    """Replace the default logger."""
    global _logger
    _logger = logger
