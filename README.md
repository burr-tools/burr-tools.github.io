# burr-tools.github.io
Burr puzzle creation and solving engine by Andreas Röver

Static site (plain GitHub Pages, no Jekyll). To edit the user guide,
change the Markdown chapters in `guide/*.md` and rebuild the HTML:

    pip install markdown   # once
    python3 guide/build.py # writes guide/index.html + guide/<chapter>/

Commit both the `.md` sources and the generated HTML. Images for the
guide live in `guide/img/`; homepage grid screenshots in `images/shots/`.
