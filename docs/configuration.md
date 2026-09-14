# Configuration

Every setting is a plain `app.config` key, read at request time — the extension is just a convenient way to set them.

**Precedence**, from strongest to weakest: values already in `app.config` (e.g. from `from_prefixed_env()` or a config file) → `RenderMarkdown(...)` keyword options → packaged defaults. Deployment configuration can always override what's written in code.

## With the extension

```python
from flask_render_markdown import RenderMarkdown

RenderMarkdown(
    app,
    extra_ai_user_agents=("MyCompanyAgent",),
    html_template="markdown_page.html",
)
```

Or with the application-factory pattern:

```python
md = RenderMarkdown(detect_ai_agents=False)

def create_app():
    app = Flask(__name__)
    md.init_app(app)
    return app
```

Accepted keyword options (each maps to the `MARKDOWN_*` config key of the same meaning): `mimetype`, `format_param`, `detect_ai_agents`, `ai_user_agents`, `extra_ai_user_agents`, `html_template`, `markdown_extensions`, `vary_header`. Unknown options raise `TypeError`.

## Without the extension

```python
app.config["MARKDOWN_MIMETYPE"] = "text/plain"
app.config["MARKDOWN_EXTRA_AI_USER_AGENTS"] = ("InternalCrawler",)
```

## All settings

| Config key | Default | Meaning |
| --- | --- | --- |
| `MARKDOWN_MIMETYPE` | `"text/markdown"` | Mimetype of Markdown responses. `text/markdown` is the [registered type (RFC 7763)](https://www.rfc-editor.org/rfc/rfc7763); switch to `"text/plain"` if a client renders the response as a download or you want it readable in any browser. |
| `MARKDOWN_FORMAT_PARAM` | `"format"` | Query parameter for manual overrides (`?format=md` / `?format=html`). `None` or `""` disables the override. |
| `MARKDOWN_DETECT_AI_AGENTS` | `True` | Enable User-Agent sniffing. When off, only the Accept header and the format parameter trigger Markdown. |
| `MARKDOWN_AI_USER_AGENTS` | `None` | *Replace* the built-in agent list with your own iterable of substrings. `None` means "use `DEFAULT_AI_USER_AGENTS`". |
| `MARKDOWN_EXTRA_AI_USER_AGENTS` | `()` | *Extend* the agent list without replacing it. |
| `MARKDOWN_HTML_TEMPLATE` | `None` | Template that wraps Markdown converted to HTML. It receives the converted HTML as `content` (already Markup-safe, so `{{ content }}` won't be escaped) plus the view's original context. `None` uses the built-in minimal page. |
| `MARKDOWN_EXTENSIONS` | `("extra",)` | [python-markdown extensions](https://python-markdown.github.io/extensions/) used by `markdown_to_html`, e.g. `("extra", "toc", "sane_lists")`. |
| `MARKDOWN_VARY_HEADER` | `True` | Add `Vary: Accept[, User-Agent]` to `render_adaptive` responses so shared caches don't mix representations. Only disable this if you handle `Vary` yourself. |
