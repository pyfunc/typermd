"""Color theme support for typermd.

Provides switchable color themes and respects the NO_COLOR standard.

Usage:
    from typermd.themes import set_theme, list_themes

    list_themes()
    set_theme("monokai")
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Theme:
    """Color theme definition with named color slots."""

    name: str
    keyword: str = "\033[34m"  # blue
    string: str = "\033[32m"  # green
    comment: str = "\033[90m"  # gray
    number: str = "\033[36m"  # cyan
    decorator: str = "\033[33m"  # yellow
    heading: str = "\033[96m"  # bright cyan
    bold: str = "\033[1m"
    dim: str = "\033[2m"
    error: str = "\033[31m"
    warning: str = "\033[33m"
    success: str = "\033[32m"
    info: str = "\033[34m"

    def get_color(self, name: str) -> str:
        return getattr(self, name, "")


# ── Built-in themes ──────────────────────────────────────────────────────

_THEMES: dict[str, Theme] = {
    "default": Theme(name="default"),
    "monokai": Theme(
        name="monokai",
        keyword="\033[38;5;197m",
        string="\033[38;5;186m",
        comment="\033[38;5;242m",
        number="\033[38;5;141m",
        decorator="\033[38;5;81m",
        heading="\033[38;5;81m",
    ),
    "solarized": Theme(
        name="solarized",
        keyword="\033[38;5;136m",
        string="\033[38;5;37m",
        comment="\033[38;5;246m",
        number="\033[38;5;33m",
        decorator="\033[38;5;166m",
        heading="\033[38;5;33m",
    ),
    "nord": Theme(
        name="nord",
        keyword="\033[38;5;110m",
        string="\033[38;5;108m",
        comment="\033[38;5;60m",
        number="\033[38;5;175m",
        decorator="\033[38;5;222m",
        heading="\033[38;5;110m",
    ),
}

_current_theme: str = "default"


def get_theme() -> Theme:
    """Get the current active theme."""
    return _THEMES.get(_current_theme, _THEMES["default"])


def set_theme(name: str) -> None:
    """Switch to a named theme."""
    global _current_theme
    if name not in _THEMES:
        available = ", ".join(_THEMES.keys())
        raise ValueError(f"Unknown theme '{name}'. Available: {available}")
    _current_theme = name


def register_theme(theme: Theme) -> None:
    """Register a custom theme."""
    _THEMES[theme.name] = theme


def list_themes() -> list[str]:
    """Return list of available theme names."""
    return list(_THEMES.keys())


def is_no_color() -> bool:
    """Check if NO_COLOR env is set."""
    return "NO_COLOR" in os.environ


def init_theme_from_env() -> None:
    """Initialize theme from TYPERMD_THEME env variable."""
    theme_name = os.environ.get("TYPERMD_THEME", "default")
    if theme_name in _THEMES:
        set_theme(theme_name)
