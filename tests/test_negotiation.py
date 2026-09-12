from __future__ import annotations

from conftest import BROWSER_ACCEPT

from flask_render_markdown import is_ai_agent, wants_markdown


def wants(app, path="/", **kwargs) -> bool:
    with app.test_request_context(path, **kwargs):
        return wants_markdown()


def test_browser_accept_header_gets_html(app):
    assert wants(app, headers={"Accept": BROWSER_ACCEPT}) is False


def test_explicit_markdown_accept_gets_markdown(app):
    assert wants(app, headers={"Accept": "text/markdown"}) is True
    assert wants(app, headers={"Accept": "text/x-markdown"}) is True


def test_markdown_accept_beats_html_on_equal_quality(app):
    assert wants(app, headers={"Accept": "text/markdown, text/html"}) is True


def test_html_preferred_over_low_quality_markdown(app):
    assert wants(app, headers={"Accept": "text/html, text/markdown;q=0.5"}) is False


def test_wildcard_accept_does_not_mean_markdown(app):
    # curl and many HTTP clients send */* — that alone shouldn't flip to md.
    assert wants(app, headers={"Accept": "*/*"}) is False


def test_no_headers_defaults_to_html(app):
    assert wants(app) is False


def test_known_ai_user_agents_get_markdown(app):
    for ua in (
        "Mozilla/5.0 AppleWebKit/537.36; compatible; GPTBot/1.2; +https://openai.com/gptbot",
        "Mozilla/5.0 (compatible; ClaudeBot/1.0; +claudebot@anthropic.com)",
        "Mozilla/5.0 (compatible; Claude-User/1.0; +Claude-User@anthropic.com)",
        "Mozilla/5.0 (compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
    ):
        assert wants(app, headers={"Accept": BROWSER_ACCEPT, "User-Agent": ua}) is True, ua


def test_ua_matching_is_case_insensitive(app):
    assert wants(app, headers={"User-Agent": "something GPTBOT here"}) is True


def test_regular_browser_ua_not_detected(app):
    ua = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"
    )
    assert wants(app, headers={"Accept": BROWSER_ACCEPT, "User-Agent": ua}) is False


def test_detection_can_be_disabled(app):
    app.config["MARKDOWN_DETECT_AI_AGENTS"] = False
    assert wants(app, headers={"User-Agent": "GPTBot/1.0"}) is False
    # Explicit Accept still wins even with detection off.
    assert wants(app, headers={"Accept": "text/markdown", "User-Agent": "GPTBot"}) is True


def test_custom_agent_list_replaces_default(app):
    app.config["MARKDOWN_AI_USER_AGENTS"] = ("MyBot",)
    assert wants(app, headers={"User-Agent": "GPTBot/1.0"}) is False
    assert wants(app, headers={"User-Agent": "MyBot/2.0"}) is True


def test_extra_agents_extend_default(app):
    app.config["MARKDOWN_EXTRA_AI_USER_AGENTS"] = ("InternalCrawler",)
    assert wants(app, headers={"User-Agent": "InternalCrawler/0.1"}) is True
    assert wants(app, headers={"User-Agent": "GPTBot/1.0"}) is True


def test_format_param_forces_markdown(app):
    assert wants(app, "/?format=md", headers={"Accept": BROWSER_ACCEPT}) is True
    assert wants(app, "/?format=markdown", headers={"Accept": BROWSER_ACCEPT}) is True


def test_format_param_forces_html(app):
    assert wants(app, "/?format=html", headers={"User-Agent": "GPTBot/1.0"}) is False


def test_format_param_name_is_configurable(app):
    app.config["MARKDOWN_FORMAT_PARAM"] = "as"
    assert wants(app, "/?as=md") is True
    assert wants(app, "/?format=md") is False


def test_format_param_can_be_disabled(app):
    app.config["MARKDOWN_FORMAT_PARAM"] = None
    assert wants(app, "/?format=md") is False


def test_is_ai_agent_with_explicit_argument(app):
    with app.app_context():
        assert is_ai_agent("Mozilla/5.0 (compatible; Bytespider)") is True
        assert is_ai_agent("Mozilla/5.0 Chrome/128.0") is False
        assert is_ai_agent("") is False
