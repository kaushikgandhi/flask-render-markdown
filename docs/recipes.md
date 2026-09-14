# Recipes

## An `llms.txt` route

The [`llms.txt` convention](https://llmstxt.org/) gives agents a well-known Markdown entry point to your site:

```python
@app.get("/llms.txt")
def llms():
    return render_markdown("llms.md", sections=SECTIONS)
```

## A whole Markdown docs section from files

```python
from jinja2 import TemplateNotFound
from flask import abort

@app.get("/docs/<path:page>")
def doc_page(page):
    try:
        return render_adaptive(f"docs/{page}.md")
    except TemplateNotFound:
        abort(404)
```

## Styling the browser version with your site layout

Point `MARKDOWN_HTML_TEMPLATE` at a template that extends your base layout; converted Markdown arrives as `content`:

```html
{# templates/markdown_page.html #}
{% extends "base.html" %}
{% block main %}
  <article class="prose">{{ content }}</article>
{% endblock %}
```

```python
RenderMarkdown(app, html_template="markdown_page.html")
```

## Markdown built at runtime (no template file)

```python
@app.get("/status.md")
def status():
    lines = ["# Service status", ""]
    lines += [f"- **{s.name}**: {s.state}" for s in check_services()]
    return markdown_response("\n".join(lines))
```

## Behind a CDN

Nothing to do beyond the defaults: `render_adaptive` sends `Vary: Accept, User-Agent`, so compliant caches key the two representations separately. Note that varying on `User-Agent` fragments the cache heavily; if that matters, disable sniffing (`MARKDOWN_DETECT_AI_AGENTS = False`) and rely on Accept headers and `?format=md` (different URL → different cache entry) instead.

## Logging which routes agents actually hit

```python
@app.after_request
def log_agent_hits(response):
    if is_ai_agent():
        app.logger.info("agent hit: %s %s", request.user_agent, request.path)
    return response
```

## Testing your app

Simulate the different clients with Flask's test client:

```python
def test_docs_markdown_for_agents(client):
    response = client.get("/docs", headers={"User-Agent": "ClaudeBot/1.0"})
    assert response.mimetype == "text/markdown"
    assert response.text.startswith("# ")

def test_docs_html_for_browsers(client):
    browser_accept = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    response = client.get("/docs", headers={"Accept": browser_accept})
    assert response.mimetype == "text/html"

def test_manual_override(client):
    assert client.get("/docs?format=md").mimetype == "text/markdown"
```

## Security notes

- **Untrusted input in templates.** `.md` templates are rendered *without* autoescaping (correct for Markdown), and Markdown may itself contain raw HTML which python-markdown passes through untouched. The Markdown representation is plain text to the client, but the **converted HTML** served to browsers is not — if your template context includes user-supplied strings, sanitize the conversion output (e.g. with [`nh3`](https://nh3.readthedocs.io/) or `bleach`) or stick to `html_template` with normal autoescaped HTML for the browser path.
- **Detection is advisory, not authentication.** User-Agent strings and Accept headers are trivially spoofed. Serving Markdown to anyone who asks is harmless by design — but never use `is_ai_agent()`/`wants_markdown()` for access control, rate limiting, or anything security-relevant.
- **Same content, different clothes.** Serve agents the same substantive content as humans, formatted differently. Feeding crawlers different *information* than visitors (cloaking) can get a site penalized by search engines.
