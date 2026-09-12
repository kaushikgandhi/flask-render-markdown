"""Markdown-to-HTML conversion for browser fallbacks.

Conversion needs the optional ``Markdown`` package::

    pip install "flask-render-markdown[html]"

It is only imported when a browser actually needs HTML and no
``html_template`` was provided, so Markdown-only deployments (AI-agent
endpoints, ``llms.txt`` style routes) don't need the dependency at all.
"""

from __future__ import annotations

import re
import string
import typing as t

from flask import render_template
from markupsafe import Markup, escape

from .config import get_setting

try:
    import markdown as _markdown
except ImportError:  # pragma: no cover - exercised via monkeypatching in tests
    _markdown = None  # type: ignore[assignment]

_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)

# Minimal readable shell used when no MARKDOWN_HTML_TEMPLATE is configured.
_PAGE = string.Template(
    """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$title</title>
<style>
  body { margin: 2rem auto; max-width: 46rem; padding: 0 1rem; color: #1f2328;
         font: 16px/1.6 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
  pre { background: #f6f8fa; padding: 1rem; overflow-x: auto; border-radius: 6px; }
  code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: .95em; }
  a { color: #0969da; }
  img { max-width: 100%; }
  blockquote { border-left: .25rem solid #d1d9e0; margin-left: 0; padding-left: 1rem; color: #59636e; }
  table { border-collapse: collapse; } th, td { border: 1px solid #d1d9e0; padding: .4rem .8rem; }
</style>
</head>
<body>
$content
</body>
</html>
"""
)


def markdown_to_html(markdown_text: str) -> str:
    """Convert Markdown source to an HTML fragment.

    Uses `python-markdown <https://python-markdown.github.io/>`_ with the
    extensions listed in ``MARKDOWN_EXTENSIONS`` (default: ``extra``, which
    covers tables, fenced code blocks, footnotes and more).

    .. warning::
       Markdown may contain raw HTML and python-markdown does not sanitize
       it. If your template context includes untrusted user input, sanitize
       the output (e.g. with ``nh3`` or ``bleach``) before serving it to
       browsers.
    """
    if _markdown is None:
        raise RuntimeError(
            "Converting Markdown to HTML requires the 'Markdown' package. "
            "Install it with: pip install 'flask-render-markdown[html]' "
            "(or pass html_template= to render_adaptive to skip conversion)."
        )
    extensions = list(get_setting("MARKDOWN_EXTENSIONS") or ())
    return _markdown.markdown(markdown_text, extensions=extensions, output_format="html5")


def render_markdown_page(markdown_text: str, context: t.Mapping[str, t.Any]) -> str:
    """Return a full HTML page for *markdown_text*, for browser fallbacks.

    If ``MARKDOWN_HTML_TEMPLATE`` is configured, that template is rendered
    with the converted HTML available as ``content`` (Markup-safe) plus the
    view's original context. Otherwise a small built-in page is used, titled
    from ``context["title"]`` or the first ``# heading`` in the document.
    """
    html_body = markdown_to_html(markdown_text)
    template_name = get_setting("MARKDOWN_HTML_TEMPLATE")
    if template_name:
        template_context = dict(context)
        template_context["content"] = Markup(html_body)
        return render_template(template_name, **template_context)

    title = context.get("title")
    if not title:
        match = _H1_RE.search(markdown_text)
        title = match.group(1) if match else "Document"
    return _PAGE.substitute(title=escape(str(title)), content=html_body)
