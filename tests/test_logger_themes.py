"""Tests for typermd.logger and typermd.themes."""

from __future__ import annotations

from io import StringIO

import pytest

from typermd.logger import Logger, get_logger, set_logger
from typermd.themes import (
    Theme,
    get_theme,
    list_themes,
    register_theme,
    set_theme,
)


class TestLogger:
    def test_info(self):
        buf = StringIO()
        log = Logger(name="test", stream=buf, use_colors=False)
        log.info("hello")
        assert "INFO" in buf.getvalue()
        assert "hello" in buf.getvalue()

    def test_success(self):
        buf = StringIO()
        log = Logger(name="test", stream=buf, use_colors=False)
        log.success("done")
        assert "SUCCESS" in buf.getvalue()

    def test_warning(self):
        buf = StringIO()
        log = Logger(name="test", stream=buf, use_colors=False)
        log.warning("careful")
        assert "WARN" in buf.getvalue()

    def test_error(self):
        buf = StringIO()
        log = Logger(name="test", stream=buf, use_colors=False)
        log.error("fail")
        assert "ERROR" in buf.getvalue()

    def test_debug_verbose(self):
        buf = StringIO()
        log = Logger(name="test", verbose=True, stream=buf, use_colors=False)
        log.debug("trace")
        assert "DEBUG" in buf.getvalue()

    def test_debug_silent(self):
        buf = StringIO()
        log = Logger(name="test", verbose=False, stream=buf, use_colors=False)
        log.debug("trace")
        assert buf.getvalue() == ""

    def test_action(self):
        buf = StringIO()
        log = Logger(name="test", stream=buf, use_colors=False)
        log.action("Installing", "dependencies")
        assert "Installing" in buf.getvalue()

    def test_step(self):
        buf = StringIO()
        log = Logger(name="test", stream=buf, use_colors=False)
        log.step(1, 3, "First step")
        assert "[1/3]" in buf.getvalue()

    def test_get_logger(self):
        log = get_logger("myapp")
        assert isinstance(log, Logger)
        assert log.name == "myapp"

    def test_set_logger(self):
        custom = Logger(name="custom")
        set_logger(custom)
        assert get_logger("custom") is custom


class TestThemes:
    def test_default_theme(self):
        theme = get_theme()
        assert theme.name == "default"

    def test_set_theme(self):
        set_theme("monokai")
        assert get_theme().name == "monokai"
        set_theme("default")  # reset

    def test_invalid_theme(self):
        with pytest.raises(ValueError, match="Unknown theme"):
            set_theme("nonexistent")

    def test_list_themes(self):
        themes = list_themes()
        assert "default" in themes
        assert "monokai" in themes
        assert "solarized" in themes
        assert "nord" in themes

    def test_register_custom(self):
        custom = Theme(name="custom_test", keyword="\033[35m")
        register_theme(custom)
        assert "custom_test" in list_themes()
        set_theme("custom_test")
        assert get_theme().name == "custom_test"
        set_theme("default")  # reset

    def test_get_color(self):
        theme = get_theme()
        assert theme.get_color("keyword") != ""
        assert theme.get_color("nonexistent") == ""
