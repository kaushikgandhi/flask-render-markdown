"""The rendering functions — drop-in counterparts to ``flask.render_template``."""

from __future__ import annotations

import typing as t
from weakref import WeakKeyDictionary

from flask import Response, current_app, render_template

from .config import get_setting
from .conversion import render_markdown_page
from .negotiation import wants_markdown

if t.TYPE_CHECKING:
    from flask import Flask
    from jinja2 import Environment

# Per-app Jinja environments for string rendering with autoescaping off
# (Flask autoescapes nameless templates, which would corrupt Markdown).
_string_envs: "WeakKeyDictionary[Flask, Environment]" = WeakKeyDictionary()


def markdown_response(
    markdown_text: str,
    status: t.Optional[int] = None,
    headers: t.Optional[t.Mapping[str, str]] = None,
) -> Response:
    """Wrap already-rendered Markdown text in a ``text/markdown`` response.

    The mimetype comes from the ``MARKDOWN_MIMETYPE`` config key; the charset
    is always UTF-8. Handy when the Markdown is built dynamically rather than
    rendered from a template.
    """
    return Response(
        markdown_text,
        status=status,
        headers=dict(headers) if headers else None,
        mimetype=get_setting("MARKDOWN_MIMETYPE"),
    )


def render_markdown(
    template_name_or_list: t.Union[str, t.List[str]],
    **context: t.Any,
) -> Response:
    """Render a Markdown template and return it as a Markdown response.

    Use it exactly like :func:`flask.render_template`::

        @app.get("/guide")
        def guide():
            return render_markdown("guide.md", user=current_user)

    The template is looked up in the app's ``templates/`` folder and rendered
    with the full Jinja environment — ``{% extends %}``, ``{% include %}``,
    filters and context processors all work. Flask does not autoescape
    ``.md`` files, so rendered values are inserted verbatim (as Markdown
    should be).

    :param template_name_or_list: template name, or list of names to try in
        order (same semantics as ``render_template``).
    :param context: variables made available in the template.
    """
    markdown_text = render_template(template_name_or_list, **context)
    return markdown_response(markdown_text)


def render_markdown_string(source: str, **context: t.Any) -> Response:
    """Render a Markdown template from a string, like ``render_template_string``.

    Autoescaping is explicitly disabled (Flask would otherwise HTML-escape
    interpolated values in a nameless template, mangling characters like
    ``&`` and ``<`` in the Markdown output).
    """
    app = current_app._get_current_object()  # type: ignore[attr-defined]
    env = _string_envs.get(app)
    if env is None:
        env = app.jinja_env.overlay(autoescape=False)
        _string_envs[app] = env
    app.update_template_context(context)
    markdown_text = env.from_string(source).render(context)
    return markdown_response(markdown_text)


def render_adaptive(
    template_name_or_list: t.Union[str, t.List[str]],
    *,
    html_template: t.Optional[str] = None,
    **context: t.Any,
) -> Response:
    """Serve Markdown to AI agents and HTML to browsers, from one view.

    If :func:`~flask_render_markdown.wants_markdown` says the client prefers
    Markdown (Accept header, known AI User-Agent, or ``?format=md``), the
    Markdown template is rendered and returned as ``text/markdown``.

    Otherwise the client gets HTML:

    * with *html_template* given, that template is rendered with the same
      context (maintain two representations, share one view);
    * without it, the rendered Markdown is converted to HTML (requires the
      ``flask-render-markdown[html]`` extra) and wrapped in either the
      ``MARKDOWN_HTML_TEMPLATE`` template or a minimal built-in page — one
      ``.md`` file serves both audiences.

    A ``Vary`` header is added (configurable via ``MARKDOWN_VARY_HEADER``)
    so HTTP caches keep the two representations apart.
    """
    if wants_markdown():
        response: Response = render_markdown(template_name_or_list, **context)
    elif html_template is not None:
        response = current_app.make_response(render_template(html_template, **context))
    else:
        markdown_text = render_template(template_name_or_list, **context)
        response = current_app.make_response(render_markdown_page(markdown_text, context))

    if get_setting("MARKDOWN_VARY_HEADER"):
        response.vary.add("Accept")
        if get_setting("MARKDOWN_DETECT_AI_AGENTS"):
            response.vary.add("User-Agent")
    return response
