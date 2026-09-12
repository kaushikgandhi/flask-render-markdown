from __future__ import annotations

import pytest
from flask import Flask

from flask_render_markdown import RenderMarkdown
from flask_render_markdown.config import DEFAULTS


def test_init_app_fills_defaults():
    app = Flask(__name__)
    RenderMarkdown(app)
    for key, default in DEFAULTS.items():
        assert app.config[key] == default
    assert isinstance(app.extensions["render_markdown"], RenderMarkdown)


def test_keyword_options_map_to_config():
    app = Flask(__name__)
    RenderMarkdown(
        app,
        mimetype="text/plain",
        detect_ai_agents=False,
        extra_ai_user_agents=("MyBot",),
        html_template="shell.html",
    )
    assert app.config["MARKDOWN_MIMETYPE"] == "text/plain"
    assert app.config["MARKDOWN_DETECT_AI_AGENTS"] is False
    assert app.config["MARKDOWN_EXTRA_AI_USER_AGENTS"] == ("MyBot",)
    assert app.config["MARKDOWN_HTML_TEMPLATE"] == "shell.html"


def test_existing_config_beats_keyword_options():
    app = Flask(__name__)
    app.config["MARKDOWN_MIMETYPE"] = "text/x-markdown"
    RenderMarkdown(app, mimetype="text/plain")
    assert app.config["MARKDOWN_MIMETYPE"] == "text/x-markdown"


def test_unknown_option_raises():
    with pytest.raises(TypeError, match="Unknown RenderMarkdown option"):
        RenderMarkdown(mimetipe="text/plain")  # typo on purpose


def test_app_factory_pattern():
    md = RenderMarkdown(detect_ai_agents=False)
    app = Flask(__name__)
    md.init_app(app)
    assert app.config["MARKDOWN_DETECT_AI_AGENTS"] is False
    assert app.extensions["render_markdown"] is md
