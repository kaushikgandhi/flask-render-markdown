from __future__ import annotations

import pytest
from jinja2 import TemplateNotFound

from flask_render_markdown import render_markdown


def test_renders_template_with_context(client):
    response = client.get("/doc")
    assert response.status_code == 200
    assert response.text == "# Hello Ada\n\nWelcome, Ada! Math works: 5 > 3 & 2 < 4."


def test_markdown_mimetype_and_charset(client):
    response = client.get("/doc")
    assert response.mimetype == "text/markdown"
    assert response.content_type == "text/markdown; charset=utf-8"


def test_no_autoescaping_in_md_templates(client):
    # '&', '>' and '<' must come through verbatim — they are Markdown text,
    # not HTML.
    body = client.get("/doc").text
    assert "&amp;" not in body
    assert "5 > 3 & 2 < 4" in body


def test_template_inheritance_works(client):
    response = client.get("/child")
    assert response.mimetype == "text/markdown"
    assert "# Guide" in response.text
    assert "From child: Tea" in response.text


def test_template_list_falls_back(app):
    with app.test_request_context("/"):
        response = render_markdown(["missing.md", "hello.md"], name="Ada")
    assert "# Hello Ada" in response.get_data(as_text=True)


def test_missing_template_raises(app):
    with app.test_request_context("/"):
        with pytest.raises(TemplateNotFound):
            render_markdown("nope.md")


def test_render_markdown_string_disables_autoescape(client):
    response = client.get("/string")
    assert response.mimetype == "text/markdown"
    assert response.text == "# Hi Ada\n\nA & B <ok>"


def test_custom_mimetype(app, client):
    app.config["MARKDOWN_MIMETYPE"] = "text/plain"
    response = client.get("/doc")
    assert response.content_type == "text/plain; charset=utf-8"


def test_markdown_response_helper(app):
    from flask_render_markdown import markdown_response

    with app.app_context():
        response = markdown_response("# Direct", status=201, headers={"X-Extra": "1"})
    assert response.status_code == 201
    assert response.mimetype == "text/markdown"
    assert response.headers["X-Extra"] == "1"
    assert response.get_data(as_text=True) == "# Direct"
