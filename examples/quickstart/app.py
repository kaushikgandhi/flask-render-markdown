"""Quickstart for flask-render-markdown.

Run:

    pip install "flask-render-markdown[html]"
    python app.py

Then compare what different clients receive:

    curl http://127.0.0.1:5001/                          # browser-ish -> HTML
    curl -A "ClaudeBot/1.0" http://127.0.0.1:5001/       # AI agent    -> Markdown
    curl -H "Accept: text/markdown" http://127.0.0.1:5001/docs
    curl "http://127.0.0.1:5001/docs?format=md"
    curl http://127.0.0.1:5001/llms.txt                  # always Markdown
"""

from flask import Flask
from flask_render_markdown import RenderMarkdown, render_adaptive, render_markdown

app = Flask(__name__)
RenderMarkdown(app)  # optional; sets config defaults in one place

ENDPOINTS = [
    {"method": "GET", "path": "/brews", "description": "List all coffee brews."},
    {"method": "POST", "path": "/brews", "description": "Start a new brew."},
    {"method": "GET", "path": "/brews/<id>", "description": "Inspect one brew."},
]


@app.get("/")
def home():
    # Markdown for agents; browsers get home.html rendered with the same context.
    return render_adaptive("home.md", html_template="home.html", name="Coffee API")


@app.get("/docs")
def docs():
    # Single .md source: agents get it raw, browsers get it converted to HTML.
    return render_adaptive("docs.md", title="Coffee API Docs", endpoints=ENDPOINTS)


@app.get("/llms.txt")
def llms():
    # Always Markdown, for clients that fetch llms.txt by convention.
    return render_markdown("docs.md", title="Coffee API Docs", endpoints=ENDPOINTS)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
