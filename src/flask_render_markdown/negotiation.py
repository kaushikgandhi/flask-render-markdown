"""Deciding whether a request should receive Markdown or HTML."""

from __future__ import annotations

import typing as t

from flask import request

from .config import get_setting

#: Mimetypes treated as "the client explicitly asked for Markdown".
MARKDOWN_MIMETYPES = frozenset({"text/markdown", "text/x-markdown"})

#: Case-insensitive User-Agent substrings of known AI agents, assistants and
#: AI crawlers. Used by :func:`is_ai_agent` unless overridden with the
#: ``MARKDOWN_AI_USER_AGENTS`` config key; extend it (without replacing it)
#: via ``MARKDOWN_EXTRA_AI_USER_AGENTS``.
DEFAULT_AI_USER_AGENTS: tuple[str, ...] = (
    # OpenAI
    "GPTBot",
    "ChatGPT-User",
    "OAI-SearchBot",
    # Anthropic
    "ClaudeBot",
    "Claude-User",
    "Claude-SearchBot",
    "claude-web",
    "anthropic-ai",
    # Perplexity
    "PerplexityBot",
    "Perplexity-User",
    # Google AI (beyond regular search indexing)
    "Google-Extended",
    "Google-CloudVertexBot",
    # Meta
    "meta-externalagent",
    "meta-externalfetcher",
    # Others
    "Amazonbot",
    "Applebot-Extended",
    "Bytespider",
    "CCBot",
    "cohere-ai",
    "cohere-training-data-crawler",
    "DuckAssistBot",
    "MistralAI-User",
    "YouBot",
)

_FORCE_MARKDOWN_VALUES = frozenset({"md", "markdown"})
_FORCE_HTML_VALUES = frozenset({"html", "htm"})


def _agent_patterns() -> t.Iterable[str]:
    patterns = get_setting("MARKDOWN_AI_USER_AGENTS")
    if patterns is None:
        patterns = DEFAULT_AI_USER_AGENTS
    extra = get_setting("MARKDOWN_EXTRA_AI_USER_AGENTS") or ()
    return (*patterns, *extra)


def is_ai_agent(user_agent: t.Optional[str] = None) -> bool:
    """Return True if the User-Agent looks like a known AI agent or crawler.

    Matching is a case-insensitive substring test against the configured
    pattern list. When *user_agent* is omitted, the current request's
    ``User-Agent`` header is used (which requires a request context).
    """
    if user_agent is None:
        user_agent = request.headers.get("User-Agent", "")
    ua = user_agent.lower()
    if not ua:
        return False
    return any(pattern.lower() in ua for pattern in _agent_patterns())


def wants_markdown() -> bool:
    """Return True if the current request should receive Markdown.

    The decision is made in order:

    1. **Explicit override** — the query parameter named by
       ``MARKDOWN_FORMAT_PARAM`` (default ``format``): ``?format=md`` or
       ``?format=markdown`` forces Markdown, ``?format=html`` forces HTML.
    2. **Accept header** — the client explicitly lists ``text/markdown``
       (or ``text/x-markdown``) with a quality at least as high as
       ``text/html``. Wildcards like ``*/*`` do NOT count as asking for
       Markdown, so browsers and plain ``curl`` keep getting HTML.
    3. **User-Agent detection** — the User-Agent matches a known AI agent
       (see :func:`is_ai_agent`), unless ``MARKDOWN_DETECT_AI_AGENTS`` is
       disabled.

    Anything else gets HTML. Requires a request context.
    """
    param = get_setting("MARKDOWN_FORMAT_PARAM")
    if param:
        forced = (request.args.get(param) or "").strip().lower()
        if forced in _FORCE_MARKDOWN_VALUES:
            return True
        if forced in _FORCE_HTML_VALUES:
            return False

    accept = request.accept_mimetypes
    markdown_quality = max(
        (quality for value, quality in accept if value.lower() in MARKDOWN_MIMETYPES),
        default=0.0,
    )
    if markdown_quality > 0 and markdown_quality >= accept.quality("text/html"):
        return True

    if get_setting("MARKDOWN_DETECT_AI_AGENTS") and is_ai_agent():
        return True

    return False
