from __future__ import annotations

import pytest
from conftest import BROWSER_ACCEPT

import flask_render_markdown.conversion as conversion
from flask_render_markdown import render_adaptive

AGENT_UA = "Mozilla/5.0 (compatible; ClaudeBot/1.0; +claudebot@anthropic.com)"


def test_agent_gets_markdown(client):
    response = client.get("/adaptive", headers={"User-Agent": AGENT_UA})
    assert response.mimetype == "text/markdown"
    assert response.text.startswith("# Hello Ada")


def test_accept_header_gets_markdown(client):
    response = client.get("/adaptive-html", headers={"Accept": "text/markdown"})
    assert response.mimetype == "text/markdown"
    assert "# Hello Ada" in response.text


def test_browser_gets_html_template_when_given(client):
    response = client.get("/adaptive-html", headers={"Accept": BROWSER_ACCEPT})
    assert response.mimetype == "text/html"
    assert "<h1>HTML Ada</h1>" in response.text


def test_browser_gets_converted_markdown_without_html_template(client):
    response = client.get("/adaptive", headers={"Accept": BROWSER_ACCEPT})
    assert response.mimetype == "text/html"
    # Converted body, wrapped in the built-in page with the H1 as <title>.
    assert "<h1>Hello Ada</h1>" in response.text
    assert "<title>Hello Ada</title>" in response.text
    assert "Welcome, Ada!" in response.text


def test_conversion_uses_configured_wrapper_template(app, client):
    app.config["MARKDOWN_HTML_TEMPLATE"] = "shell.html"
    response = client.get("/adaptive", headers={"Accept": BROWSER_ACCEPT})
    assert '<main data-shell="1">' in response.text
    assert "<h1>Hello Ada</h1>" in response.text


def test_format_param_overrides_browser(client):
    response = client.get("/adaptive?format=md", headers={"Accept": BROWSER_ACCEPT})
    assert response.mimetype == "text/markdown"


def test_format_param_overrides_agent(client):
    response = client.get(
        "/adaptive-html?format=html", headers={"User-Agent": AGENT_UA}
    )
    assert response.mimetype == "text/html"


def test_vary_header_present_on_both_representations(client):
    for headers in ({"User-Agent": AGENT_UA}, {"Accept": BROWSER_ACCEPT}):
        vary = client.get("/adaptive-html", headers=headers).headers.get("Vary", "")
        assert "Accept" in vary
        assert "User-Agent" in vary


def test_vary_skips_user_agent_when_detection_off(app, client):
    app.config["MARKDOWN_DETECT_AI_AGENTS"] = False
    vary = client.get("/adaptive-html").headers.get("Vary", "")
    assert "Accept" in vary
    assert "User-Agent" not in vary


def test_vary_header_can_be_disabled(app, client):
    app.config["MARKDOWN_VARY_HEADER"] = False
    response = client.get("/adaptive-html")
    assert "Vary" not in response.headers


def test_helpful_error_when_markdown_package_missing(app, monkeypatch):
    monkeypatch.setattr(conversion, "_markdown", None)
    with app.test_request_context("/", headers={"Accept": BROWSER_ACCEPT}):
        with pytest.raises(RuntimeError, match=r"flask-render-markdown\[html\]"):
            render_adaptive("hello.md", name="Ada")


def test_title_falls_back_to_context_then_document(app):
    # Explicit title in context wins over the H1.
    with app.test_request_context("/", headers={"Accept": BROWSER_ACCEPT}):
        response = render_adaptive("hello.md", name="Ada", title="Custom <Title>")
    assert "<title>Custom &lt;Title&gt;</title>" in response.get_data(as_text=True)
