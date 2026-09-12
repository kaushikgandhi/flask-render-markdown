"""flask-render-markdown: Flask's ``render_template``, but for Markdown.

Serve Markdown templates to AI agents (which parse Markdown better and burn
fewer tokens on it than HTML) while still serving HTML to browsers.

Typical usage::

    from flask import Flask
    from flask_render_markdown import render_adaptive, render_markdown

    app = Flask(__name__)

    @app.get("/docs")
    def docs():
        # Markdown for AI agents, HTML for everyone else.
        return render_adaptive("docs.md", html_template="docs.html", title="API Docs")

    @app.get("/llms.txt")
    def llms():
        # Always Markdown.
        return render_markdown("llms.md")

Markdown templates are ordinary Jinja templates that live in your app's
``templates/`` folder, so ``{{ variables }}``, ``{% include %}``,
``{% extends %}`` and context processors all work exactly as they do with
``render_template``.
"""

from __future__ import annotations

from .config import DEFAULTS
from .conversion import markdown_to_html
from .core import (
    markdown_response,
    render_adaptive,
    render_markdown,
    render_markdown_string,
)
from .extension import RenderMarkdown
from .negotiation import DEFAULT_AI_USER_AGENTS, is_ai_agent, wants_markdown

__version__ = "0.1.2"

__all__ = [
    "DEFAULTS",
    "DEFAULT_AI_USER_AGENTS",
    "RenderMarkdown",
    "__version__",
    "is_ai_agent",
    "markdown_response",
    "markdown_to_html",
    "render_adaptive",
    "render_markdown",
    "render_markdown_string",
    "wants_markdown",
]
