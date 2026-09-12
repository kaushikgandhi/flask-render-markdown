"""Optional Flask extension for configuring flask-render-markdown.

The rendering functions work without this class — it exists so configuration
can be done in one obvious, discoverable place::

    from flask_render_markdown import RenderMarkdown

    md = RenderMarkdown(
        app,
        mimetype="text/markdown",
        extra_ai_user_agents=("MyCompanyAgent",),
        html_template="markdown_page.html",
    )

or with the application-factory pattern::

    md = RenderMarkdown()

    def create_app():
        app = Flask(__name__)
        md.init_app(app)
        return app
"""

from __future__ import annotations

import typing as t

from .config import DEFAULTS

if t.TYPE_CHECKING:
    from flask import Flask

#: Keyword argument -> app.config key.
_OPTION_TO_CONFIG_KEY = {
    "mimetype": "MARKDOWN_MIMETYPE",
    "format_param": "MARKDOWN_FORMAT_PARAM",
    "detect_ai_agents": "MARKDOWN_DETECT_AI_AGENTS",
    "ai_user_agents": "MARKDOWN_AI_USER_AGENTS",
    "extra_ai_user_agents": "MARKDOWN_EXTRA_AI_USER_AGENTS",
    "html_template": "MARKDOWN_HTML_TEMPLATE",
    "markdown_extensions": "MARKDOWN_EXTENSIONS",
    "vary_header": "MARKDOWN_VARY_HEADER",
}


class RenderMarkdown:
    """Registers flask-render-markdown's configuration on a Flask app.

    Accepted keyword options (each maps to a ``MARKDOWN_*`` config key):
    ``mimetype``, ``format_param``, ``detect_ai_agents``, ``ai_user_agents``,
    ``extra_ai_user_agents``, ``html_template``, ``markdown_extensions``,
    ``vary_header``.

    Precedence: values already present in ``app.config`` win over keyword
    options, which win over the packaged defaults — so deployment config
    (e.g. ``app.config.from_prefixed_env()``) can always override code.
    """

    def __init__(self, app: t.Optional["Flask"] = None, **options: t.Any) -> None:
        unknown = set(options) - set(_OPTION_TO_CONFIG_KEY)
        if unknown:
            raise TypeError(
                f"Unknown RenderMarkdown option(s): {', '.join(sorted(unknown))}. "
                f"Valid options: {', '.join(sorted(_OPTION_TO_CONFIG_KEY))}."
            )
        self._options = options
        if app is not None:
            self.init_app(app)

    def init_app(self, app: "Flask") -> None:
        for option, value in self._options.items():
            app.config.setdefault(_OPTION_TO_CONFIG_KEY[option], value)
        for key, default in DEFAULTS.items():
            app.config.setdefault(key, default)
        app.extensions["render_markdown"] = self
