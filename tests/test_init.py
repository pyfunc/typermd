"""Tests for typermd main module — echo, table, panel, and Typer re-exports."""

from __future__ import annotations

from io import StringIO


class TestImports:
    """Verify all Typer re-exports are accessible."""

    def test_typer_class(self):
        import typermd

        assert typermd.Typer is not None

    def test_argument(self):
        import typermd

        assert typermd.Argument is not None

    def test_option(self):
        import typermd

        assert typermd.Option is not None

    def test_context(self):
        import typermd

        assert typermd.Context is not None

    def test_exit(self):
        import typermd

        assert typermd.Exit is not None

    def test_abort(self):
        import typermd

        assert typermd.Abort is not None

    def test_colors(self):
        import typermd

        assert typermd.colors is not None

    def test_style(self):
        import typermd

        assert callable(typermd.style)

    def test_run(self):
        import typermd

        assert callable(typermd.run)

    def test_md_function(self):
        import typermd

        assert callable(typermd.md)

    def test_echo_function(self):
        import typermd

        assert callable(typermd.echo)

    def test_version(self):
        import typermd

        assert typermd.__version__ == "0.1.2"


class TestEcho:
    """Test the enhanced echo function."""

    def test_plain_text(self):
        import typermd

        buf = StringIO()
        typermd.echo("hello world", file=buf)
        assert "hello world" in buf.getvalue()

    def test_markdown_heading(self):
        import typermd

        buf = StringIO()
        typermd.echo("# Hello", file=buf)
        assert "Hello" in buf.getvalue()

    def test_auto_markdown_disabled(self):
        import typermd

        buf = StringIO()
        typermd.echo("# Hello", file=buf, auto_markdown=False)
        out = buf.getvalue()
        assert "# Hello" in out

    def test_empty_message(self):
        import typermd

        buf = StringIO()
        typermd.echo("", file=buf)
        # Should not raise


class TestTable:
    """Test the table rendering function."""

    def test_basic_table(self):
        from typermd import table

        buf = StringIO()
        import typermd.renderer as renderer_mod
        from typermd.renderer import MarkdownRenderer

        old = renderer_mod._default_renderer
        renderer_mod._default_renderer = MarkdownRenderer(stream=buf, use_colors=False)
        try:
            table(
                headers=["Name", "Version"],
                rows=[["typermd", "0.1.0"], ["typer", "0.9.0"]],
            )
            out = buf.getvalue()
            assert "Name" in out
            assert "typermd" in out
            assert "0.1.0" in out
        finally:
            renderer_mod._default_renderer = old

    def test_empty_table(self):
        import typermd.renderer as renderer_mod
        from typermd import table
        from typermd.renderer import MarkdownRenderer

        buf = StringIO()
        old = renderer_mod._default_renderer
        renderer_mod._default_renderer = MarkdownRenderer(stream=buf, use_colors=False)
        try:
            table(headers=["A", "B"], rows=[])
            out = buf.getvalue()
            assert "A" in out
        finally:
            renderer_mod._default_renderer = old


class TestPanel:
    """Test the panel rendering function."""

    def test_basic_panel(self):
        import typermd.renderer as renderer_mod
        from typermd import panel
        from typermd.renderer import MarkdownRenderer

        buf = StringIO()
        old = renderer_mod._default_renderer
        renderer_mod._default_renderer = MarkdownRenderer(stream=buf, use_colors=False)
        try:
            panel("Hello World", title="Info")
            out = buf.getvalue()
            assert "Hello World" in out
            assert "Info" in out
            assert "╭" in out
            assert "╰" in out
        finally:
            renderer_mod._default_renderer = old


class TestDropInReplacement:
    """Test that typermd works as a drop-in for typer."""

    def test_create_app(self):
        import typermd as typer

        app = typer.Typer()
        assert app is not None

    def test_command_decorator(self):
        import typermd as typer

        app = typer.Typer()

        @app.command()
        def hello(name: str = "World"):
            typer.echo(f"Hello {name}")

    def test_option_annotation(self):
        import typermd as typer

        app = typer.Typer()

        @app.command()
        def greet(
            name: str = typer.Option("World", help="Name to greet"),
        ):
            pass
