# AGENTS.md — burr-tools.github.io

Static site, plain GitHub Pages (no Jekyll, no CI). `index.html` is the
homepage (dark theme, inline CSS, three.js 3D viewer under `assets/`).
`guide/` is the user guide; `images/shots/` holds homepage screenshots.

## User guide workflow

- Source of truth: `guide/*.md` (one chapter per file, `title`/`nav_order`
  front matter). Images live in `guide/img/`, referenced as `img/...`.
- Rebuild after any `.md` edit with `uv run guide/build.py` (PEP 723
  deps in the script header, no manual installs) → `guide/index.html`
  (all-in-one, keeps the `guide/` URL) + `guide/<chapter>/` (multi-page,
  contents nav, prev/next, cross-page `#Label` links). Theme and token
  colours live in `guide/style.css`, linked from every page.
- Commit the `.md` sources **and** the generated HTML together.
- Markdown limits, handled by convention: definition lists need the
  `def_list` extension (already on); GUI-element emphasis is `**_x_**`;
  code blocks use fenced ``` with a language tag (```python) for
  Pygments highlighting via `codehilite`.
- After rebuilding, check for stray `**` outside `<pre>/<code>` and run a
  link pass: every `#anchor`, `<page>/#anchor` and `<img src>` must resolve.

## Conventions

- Homepage screenshots: 860px PNGs in `images/shots/`, shot from the
  running 0.8 editor (Xvfb + xdotool + scrot), puzzle zoomed to fill the
  3D view, click-through to full size.
- Verify visual changes with headless Chromium screenshots before
  committing (`chromium --headless=new --screenshot=...`; use
  `.../index.html` file URLs directly — directory URLs render a listing).
- Local preview over HTTP, not `file://`:
  `python3 -m http.server` from the repo root.
