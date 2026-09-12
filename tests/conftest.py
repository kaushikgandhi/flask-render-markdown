from __future__ import annotations

from pathlib import Path

import pytest
from flask import Flask

from flask_render_markdown import (
    render_adaptive,
    render_markdown,
    render_markdown_string,
)

TEMPLATES = Path(__file__).parent / "templates"

# A realistic desktop-browser Accept header.
BROWSER_ACCEPT = (
    "text/html,application/xhtml+xml,application/xml;q=0.9,"
    "image/avif,image/webp,*/*;q=0.8"
)


@pytest.fixture
def app() -> Flask:
    app = Flask(__name__, template_folder=str(TEMPLATES))
    app.config["TESTING"] = True

    @app.get("/doc")
    def doc():
        return render_markdown("hello.md", name="Ada")

    @app.get("/child")
    def child():
        return render_markdown("child.md", title="Guide", item="Tea")

    @app.get("/string")
    def string():
        return render_markdown_string("# Hi {{ name }}\n\nA & B <ok>", name="Ada")

    @app.get("/adaptive")
    def adaptive():
        return render_adaptive("hello.md", name="Ada")

    @app.get("/adaptive-html")
    def adaptive_html():
        return render_adaptive("hello.md", html_template="page.html", name="Ada")

    return app


@pytest.fixture
def client(app):
    return app.test_client()
