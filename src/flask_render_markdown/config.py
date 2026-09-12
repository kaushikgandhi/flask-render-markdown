"""Configuration keys and defaults.

Every setting is read from ``app.config`` at request time, so the library
works with or without the :class:`~flask_render_markdown.RenderMarkdown` extension:
set the keys directly on ``app.config``, or let the extension set them for
you. Missing keys fall back to the values below.
"""

from __future__ import annotations

import typing as t

from flask import current_app

#: Default value for every supported ``app.config`` key.
DEFAULTS: dict[str, t.Any] = {
    # Mimetype used for Markdown responses. Some clients interoperate better
    # with "text/plain"; both are valid choices for Markdown payloads.
    "MARKDOWN_MIMETYPE": "text/markdown",
    # Query-string parameter that forces the representation, e.g.
    # ``?format=md`` or ``?format=html``. Set to None/"" to disable.
    "MARKDOWN_FORMAT_PARAM": "format",
    # Whether User-Agent sniffing for known AI agents/crawlers is enabled.
    "MARKDOWN_DETECT_AI_AGENTS": True,
    # Replace the built-in list of AI User-Agent substrings entirely.
    # None means "use flask_render_markdown.DEFAULT_AI_USER_AGENTS".
    "MARKDOWN_AI_USER_AGENTS": None,
    # Additional User-Agent substrings, merged with the list above.
    "MARKDOWN_EXTRA_AI_USER_AGENTS": (),
    # Template used by render_adaptive() to wrap Markdown converted to HTML.
    # It receives the converted HTML as ``content`` (already Markup-safe)
    # plus the view's original context. None means "use the built-in page".
    "MARKDOWN_HTML_TEMPLATE": None,
    # python-markdown extensions used when converting Markdown to HTML.
    "MARKDOWN_EXTENSIONS": ("extra",),
    # Whether render_adaptive() adds a "Vary" header (Accept, and User-Agent
    # when agent detection is on) so caches don't mix representations.
    "MARKDOWN_VARY_HEADER": True,
}


def get_setting(key: str) -> t.Any:
    """Return ``app.config[key]``, falling back to the packaged default."""
    return current_app.config.get(key, DEFAULTS[key])
