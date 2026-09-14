# flask-render-markdown

**Flask's `render_template`, but for Markdown.** Serve Markdown to AI agents and HTML to browsers — from the same view, with the same Jinja templates you already know.

```python
from flask import Flask
from flask_render_markdown import render_adaptive

app = Flask(__name__)

@app.get("/docs")
def docs():
    # AI agents get docs.md as text/markdown; browsers get docs.html.
    return render_adaptive("docs.md", html_template="docs.html", title="API Docs")
```

```bash
curl -A "ClaudeBot/1.0" https://example.com/docs   # -> text/markdown
curl -A "Mozilla/5.0 …" https://example.com/docs   # -> text/html
```

## Why serve Markdown to AI agents?

More and more of your traffic isn't a person with a browser — it's an AI assistant fetching a page on a user's behalf (ChatGPT, Claude, Perplexity), or a crawler feeding a model. For those clients, HTML is a bad fit:

- **Tokens.** A typical HTML page is dominated by markup, scripts, and styling. The same content as Markdown is often 5–10× smaller in tokens — cheaper calls, faster answers, and more of your content fitting in the model's context window.
- **Fidelity.** LLMs are trained on enormous amounts of Markdown. Headings, lists, tables, and code blocks survive as structure instead of being reverse-engineered from a DOM.
- **You control the story.** Instead of hoping an agent's HTML-to-text scraper does your page justice, you decide exactly what the Markdown representation says — the same idea that drives the [`llms.txt` convention](https://llmstxt.org/).

`flask-render-markdown` makes this a one-line change per route. It is deliberately small: no new template language, no middleware magic, no lock-in — just Flask responses built from Jinja templates.

## Installation

```bash
pip install flask-render-markdown
```

If you want browsers to receive your Markdown *converted to HTML* (used by `render_adaptive` when you don't maintain a separate HTML template), add the `html` extra, which pulls in [python-markdown](https://python-markdown.github.io/):

```bash
pip install "flask-render-markdown[html]"
```

Requires **Python ≥ 3.9** and **Flask ≥ 2.0**. The PyPI package is `flask-render-markdown`; the import name is `flask_render_markdown`.

## Where to go next

- [Quickstart](quickstart.md) — a working app in two minutes.
- [How detection works](detection.md) — the exact rules deciding Markdown vs HTML.
- [Configuration](configuration.md) — every `MARKDOWN_*` setting.
- [Recipes](recipes.md) — `llms.txt`, docs sections, CDNs, testing.
- [API reference](api.md) — generated from the source docstrings.

## Used in production

`flask-render-markdown` powers the Markdown responses behind millions of AI-agent requests in production. Using it in your project? [Open an issue or PR](https://github.com/kaushikgandhi/flask-render-markdown/issues) to get listed in the README.
