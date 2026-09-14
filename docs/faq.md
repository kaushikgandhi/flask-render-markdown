# FAQ

**Do I replace `render_template` everywhere?**
No. Keep `render_template` for your normal HTML pages — this library is a *companion*, not a replacement. Use `render_markdown`/`render_adaptive` only on routes that should speak Markdown to agents. HTML templates are still first-class citizens via `render_adaptive(..., html_template=...)`, which calls `render_template` under the hood.

**How is this different from Flask-Markdown or a `markdown` Jinja filter?**
Those render Markdown *into your HTML pages* for humans. `flask-render-markdown` goes the other direction: it serves the Markdown itself as the HTTP response for clients that prefer it, with HTML as the fallback for people.

**Does this hurt SEO?**
No. Googlebot/Bingbot aren't in the agent list, so search crawlers see your normal HTML, and the `Vary` header tells caches not to mix things up. Only AI-specific fetchers get Markdown.

**Why default to `text/markdown` and not `text/plain`?**
`text/markdown` is the registered mimetype for Markdown (RFC 7763) and tells capable clients exactly what they're getting. Browsers hitting a Markdown URL directly may offer to download it, though — if your Markdown routes are also meant for humans-with-browsers, either use `render_adaptive` (browsers then get HTML) or set `MARKDOWN_MIMETYPE = "text/plain"`.

**A plain `curl` gets HTML — isn't curl "not a browser"?**
curl sends `Accept: */*`, which is a preference for *anything*, not a request for Markdown. Guessing Markdown from wildcards would change behavior for every HTTP client in existence. `curl -H "Accept: text/markdown"` or `?format=md` gets you Markdown explicitly.

**Do I need the `Markdown` package?**
Only for automatic Markdown→HTML conversion (`render_adaptive` without `html_template`, or calling `markdown_to_html`). Pure-Markdown deployments — agent endpoints, `llms.txt`, APIs — need no extra dependency.

**Can I use it in blueprints?**
Yes. The functions behave exactly like `render_template`, including blueprint template folders and the normal template search order.

**What about async views?**
Fine too — the functions are synchronous and cheap, and Flask runs them inside your async view just as it does `render_template`.

**Can I use it with Django or FastAPI?**
Not this package — it's built on Flask's request context and Jinja setup. The negotiation logic ports easily, though; open an issue if you'd use a Django or Starlette version.
