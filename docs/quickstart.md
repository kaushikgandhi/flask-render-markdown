# Quickstart

Project layout — Markdown templates live in your normal `templates/` folder:

```
myapp/
├── app.py
└── templates/
    ├── docs.md
    └── docs.html      (optional)
```

`app.py`:

```python
from flask import Flask
from flask_render_markdown import render_adaptive, render_markdown

app = Flask(__name__)

@app.get("/docs")
def docs():
    # One .md source for everyone: agents get it raw, browsers get it
    # converted to HTML (requires the [html] extra).
    return render_adaptive("docs.md", title="Coffee API")

@app.get("/llms.txt")
def llms():
    # Always Markdown, no negotiation.
    return render_markdown("docs.md", title="Coffee API")
```

`templates/docs.md` — an ordinary Jinja template that happens to be Markdown:

```markdown
# {{ title }}

All endpoints return JSON.

| Method | Path        | Description       |
| ------ | ----------- | ----------------- |
| GET    | /brews      | List all brews.   |
| POST   | /brews      | Start a new brew. |
```

Now compare what different clients receive:

```bash
curl -A "ClaudeBot/1.0" http://127.0.0.1:5000/docs         # Markdown (AI agent UA)
curl -H "Accept: text/markdown" http://127.0.0.1:5000/docs  # Markdown (explicit Accept)
curl "http://127.0.0.1:5000/docs?format=md"                 # Markdown (manual override)
curl http://127.0.0.1:5000/docs                             # HTML (everyone else)
```

A complete runnable example, including a route that maintains separate `.md` and `.html` templates, is in [`examples/quickstart/`](https://github.com/kaushikgandhi/flask-render-markdown/tree/main/examples/quickstart).

## Writing Markdown templates

Markdown templates are **regular Jinja templates**. Everything you use with `render_template` works unchanged, because rendering goes through your app's normal Jinja environment:

- `{{ variables }}`, filters, and tests
- `{% include %}`, `{% import %}`, and macros
- `{% extends %}` / `{% block %}` inheritance
- context processors, `g`, `request`, `session`, `url_for`, `config`

Inheritance example:

```markdown
{# templates/base.md #}
# {{ title }}

{% block body %}{% endblock %}

---
*{{ config.SITE_NAME }} — generated {{ now.date() }}*
```

```markdown
{# templates/guide.md #}
{% extends "base.md" %}
{% block body %}
Follow these steps: {{ steps | join(", ") }}.
{% endblock %}
```

!!! note "No autoescaping"
    Flask only autoescapes `.html`/`.htm`/`.xml`/`.xhtml`/`.svg` templates, so values interpolated into `.md` templates are inserted verbatim — `&`, `<`, and `>` stay intact, which is what Markdown needs. (`render_markdown_string` explicitly disables autoescaping for the same reason.) See the [security notes](recipes.md#security-notes) for what this means when context contains untrusted input.
