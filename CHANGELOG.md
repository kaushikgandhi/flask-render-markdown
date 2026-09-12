# Changelog

## 0.1.2 (2026-09-12)

- Project moved to GitHub: https://github.com/kaushikgandhi/flask-render-markdown
  (`[project.urls]` now populates the PyPI sidebar links).
- CI: GitHub Actions test matrix on Python 3.9–3.13; release workflow for
  PyPI Trusted Publishing.
- README: badges and repository links.

## 0.1.1 (2026-09-12)

Documentation-only release.

- README: prominent `html_template=` usage in the lead example, plus a
  production-usage section (prisonassist.com).

## 0.1.0 (2026-09-12)

Initial release.

- `render_markdown()` — `render_template` drop-in that renders `.md` Jinja
  templates and returns them as `text/markdown`.
- `render_adaptive()` — content negotiation: Markdown for AI agents, HTML for
  browsers (via a separate template or automatic Markdown→HTML conversion),
  with correct `Vary` headers.
- `render_markdown_string()`, `markdown_response()`, `markdown_to_html()`.
- `wants_markdown()` / `is_ai_agent()` — detection via `?format=` override,
  explicit `Accept: text/markdown`, and a curated AI User-Agent list.
- Optional `RenderMarkdown` extension; all `MARKDOWN_*` settings also work as
  plain `app.config` keys.
- Optional `[html]` extra (python-markdown) for browser-facing conversion.
