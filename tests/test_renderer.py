"""Tests for typermd.renderer module."""

from __future__ import annotations

from io import StringIO

from typermd.renderer import (
    MarkdownRenderer,
    _highlight_code,
    get_renderer,
    looks_like_markdown,
    render_markdown,
    render_to_string,
    strip_ansi,
)


class TestStripAnsi:
    def test_removes_color_codes(self):
        assert strip_ansi("\033[31mred\033[0m") == "red"

    def test_plain_text_unchanged(self):
        assert strip_ansi("hello") == "hello"

    def test_multiple_codes(self):
        assert strip_ansi("\033[1m\033[34mbold blue\033[0m") == "bold blue"


class TestLooksLikeMarkdown:
    def test_heading(self):
        assert looks_like_markdown("# Hello")

    def test_bold(self):
        assert looks_like_markdown("This is **bold** text")

    def test_code_fence(self):
        assert looks_like_markdown("```python\nprint('hi')\n```")

    def test_bullet_list(self):
        assert looks_like_markdown("- item one\n- item two")

    def test_link(self):
        assert looks_like_markdown("[click](https://example.com)")

    def test_plain_text(self):
        assert not looks_like_markdown("just regular text")

    def test_empty(self):
        assert not looks_like_markdown("")

    def test_inline_code(self):
        assert looks_like_markdown("Use `pip install typermd`")


class TestHighlightCode:
    def test_python_keywords(self):
        result = _highlight_code("def hello():", "python")
        assert "\033[" in result  # has color codes

    def test_unknown_lang(self):
        code = "some random code"
        assert _highlight_code(code, "unknown_lang") == code

    def test_json(self):
        result = _highlight_code('{"key": "value", "num": 42}', "json")
        assert "\033[" in result

    def test_yaml(self):
        result = _highlight_code("key: value\n# comment", "yaml")
        assert "\033[" in result

    def test_bash(self):
        result = _highlight_code("echo $HOME", "bash")
        assert "\033[" in result

    def test_log_error(self):
        result = _highlight_code("ERROR: something failed", "log")
        assert "\033[31m" in result or "\033[" in result

    def test_log_success(self):
        result = _highlight_code("✅ Build success", "log")
        assert "\033[" in result


class TestMarkdownRenderer:
    def setup_method(self):
        self.buf = StringIO()
        self.r = MarkdownRenderer(stream=self.buf, use_colors=False)

    def test_heading_level1(self):
        self.r.heading(1, "Title")
        out = self.buf.getvalue()
        assert "Title" in out

    def test_heading_level2(self):
        self.r.heading(2, "Subtitle")
        out = self.buf.getvalue()
        assert "Subtitle" in out

    def test_codeblock(self):
        self.r.codeblock("python", 'print("hi")')
        out = self.buf.getvalue()
        assert 'print("hi")' in out
        assert "python" in out

    def test_blockquote(self):
        self.r.blockquote("quoted text")
        out = self.buf.getvalue()
        assert "quoted text" in out

    def test_horizontal_rule(self):
        self.r.horizontal_rule()
        out = self.buf.getvalue()
        assert "─" in out

    def test_list_item(self):
        self.r.list_item("item one")
        out = self.buf.getvalue()
        assert "item one" in out

    def test_numbered_item(self):
        self.r.numbered_item(1, "first")
        out = self.buf.getvalue()
        assert "first" in out

    def test_paragraph(self):
        self.r.paragraph("A simple paragraph.")
        out = self.buf.getvalue()
        assert "A simple paragraph." in out

    def test_checklist_checked(self):
        self.r.checklist_item(True, "Done task")
        out = self.buf.getvalue()
        assert "Done task" in out

    def test_checklist_unchecked(self):
        self.r.checklist_item(False, "Todo task")
        out = self.buf.getvalue()
        assert "Todo task" in out


class TestRenderFull:
    def test_full_document(self):
        buf = StringIO()
        r = MarkdownRenderer(stream=buf, use_colors=False)
        r.render("""# Title

Some **bold** text.

```python
print("hello")
```

- item 1
- item 2

> A quote

---
""")
        out = buf.getvalue()
        assert "Title" in out
        assert "bold" in out
        assert "print" in out
        assert "item 1" in out
        assert "quote" in out

    def test_numbered_list(self):
        buf = StringIO()
        r = MarkdownRenderer(stream=buf, use_colors=False)
        r.render("1. First\n2. Second\n3. Third\n")
        out = buf.getvalue()
        assert "First" in out
        assert "Second" in out
        assert "Third" in out

    def test_nested_code_block(self):
        buf = StringIO()
        r = MarkdownRenderer(stream=buf, use_colors=False)
        r.render("```bash\necho hello\n```")
        out = buf.getvalue()
        assert "echo hello" in out

    def test_empty_input(self):
        buf = StringIO()
        r = MarkdownRenderer(stream=buf, use_colors=False)
        r.render("")
        # Should not raise


class TestConvenienceFunctions:
    def test_render_markdown(self):
        buf = StringIO()
        render_markdown("# Hello", stream=buf, use_colors=False)
        assert "Hello" in buf.getvalue()

    def test_render_to_string(self):
        result = render_to_string("**bold** text")
        assert "bold" in result

    def test_get_renderer_default(self):
        r = get_renderer()
        assert isinstance(r, MarkdownRenderer)

    def test_get_renderer_custom_stream(self):
        buf = StringIO()
        r = get_renderer(stream=buf)
        assert r.stream is buf


class TestInlineFormatting:
    def setup_method(self):
        self.buf = StringIO()
        self.r = MarkdownRenderer(stream=self.buf, use_colors=True)

    def test_bold(self):
        result = self.r._inline("**bold** text")
        plain = strip_ansi(result)
        assert "bold" in plain

    def test_italic(self):
        result = self.r._inline("*italic* text")
        plain = strip_ansi(result)
        assert "italic" in plain

    def test_inline_code(self):
        result = self.r._inline("Use `pip install`")
        plain = strip_ansi(result)
        assert "pip install" in plain

    def test_link(self):
        result = self.r._inline("[Click](https://example.com)")
        plain = strip_ansi(result)
        assert "Click" in plain
        assert "example.com" in plain

    def test_no_colors(self):
        r = MarkdownRenderer(stream=StringIO(), use_colors=False)
        result = r._inline("**bold** and *italic*")
        assert "\033[" not in result
        assert "bold" in result
