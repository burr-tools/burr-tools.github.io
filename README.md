# burr-tools.github.io
Burr puzzle creation and solving engine by Andreas Röver

Static site (plain GitHub Pages, no Jekyll). To edit the user guide,
change the Markdown chapters in `guide/*.md` and rebuild the HTML:

    uv run guide/build.py  # writes guide/index.html + guide/<chapter>/

Commit both the `.md` sources and the generated HTML. Images for the
guide live in `guide/img/`; homepage grid screenshots in `images/shots/`.

To preview locally (needed: `file://` has no directory-index fallback,
so per-chapter `index.html` pages only resolve over HTTP):

    python3 -m http.server -d /path/to/burr-tools.github.io 8000
    # homepage:  http://localhost:8000/
    # guide:     http://localhost:8000/guide/
    # a chapter: http://localhost:8000/guide/shapes/
