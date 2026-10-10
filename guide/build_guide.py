#!/usr/bin/env python3
"""Build the BurrTools user guide page from userGuide.t2t (txt2tags source).

Usage (run inside this directory):
    pip install txt2tags          # once; modern txt2tags 3.x on Python 3
    python3 build_guide.py        # regenerates index.html from userGuide.t2t

The .t2t source uses a few legacy macros from the 2010 toolchain that are
expanded here before conversion, because modern txt2tags would otherwise
misinterpret them:

    @F@label|img1 img2|caption@F@   -> figure with anchor, images, caption
    @A@text@A@ / @B@text@B@         -> italic / bold-italic
    [text Label]                    -> [text #Label] internal links

Images are served from img/ next to the generated index.html.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / 'userGuide.t2t'
OUT = HERE / 'index.html'
TMP_T2T = HERE / '.guide_build.t2t'
TMP_HTML = HERE / '.guide_build.html'

TITLE = 'BurrTools User Guide'
VERSION = '0.8.0'

TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BurrTools User Guide</title>
<meta name="description" content="The BurrTools user guide: creating shapes, defining puzzles, solving, and exporting.">
<link rel="shortcut icon" href="../images/burricons.ico">
<style>
  :root {
    --bg: #16130f;
    --bg2: #1e1a14;
    --card: #241f17;
    --card2: #2b2419;
    --ink: #f2ead9;
    --dim: #b3a78e;
    --faint: #7d7461;
    --accent: #f0a832;
    --accent2: #e2682a;
    --line: #3a3226;
    --good: #9ccc65;
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0; background: var(--bg); color: var(--ink);
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
    line-height: 1.65;
  }
  a { color: var(--accent); }
  a:hover { color: #ffd080; }
  nav.top {
    display: flex; align-items: center; gap: 22px;
    padding: 14px 28px; max-width: 1000px; margin: 0 auto;
  }
  .brand { display: flex; align-items: center; gap: 12px; text-decoration: none; color: var(--ink); }
  .brand img { width: 34px; height: 34px; }
  .brand b { font-size: 20px; letter-spacing: 0.5px; }
  nav.top .links { margin-left: auto; display: flex; gap: 4px; flex-wrap: wrap; }
  nav.top .links a {
    color: var(--dim); text-decoration: none; font-size: 15px;
    padding: 8px 12px; border-radius: 8px;
  }
  nav.top .links a:hover { color: var(--ink); background: var(--card); }
  main { max-width: 1000px; margin: 0 auto; padding: 10px 28px 60px; }
  h1 { font-size: clamp(30px, 4vw, 44px); line-height: 1.1; letter-spacing: -0.5px; margin: 18px 0 8px; }
  h1 .em { color: var(--accent); }
  section h1 { font-size: 30px; margin-top: 44px; border-bottom: 1px solid var(--line); padding-bottom: 8px; }
  section section h1 { font-size: 24px; margin-top: 30px; }
  section section section h1 { font-size: 20px; margin-top: 22px; }
  section section section section h1 { font-size: 17px; margin-top: 18px; }
  .byline { color: var(--faint); font-size: 14px; margin: 0 0 18px; }
  .note {
    background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--accent);
    border-radius: 10px; padding: 12px 16px; color: var(--dim); font-size: 14.5px; margin: 0 0 22px;
  }
  nav.toc { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 16px 22px; margin: 0 0 30px; }
  nav.toc h2 { margin: 0 0 8px; font-size: 18px; }
  nav.toc ol, nav.toc ul { margin: 6px 0; padding-left: 22px; color: var(--dim); font-size: 14.5px; }
  nav.toc li { margin: 2px 0; }
  figure {
    background: var(--card); border: 1px solid var(--line); border-radius: 14px;
    padding: 16px; margin: 20px 0; text-align: center;
  }
  figure img { max-width: 100%; height: auto; margin: 6px auto; border-radius: 6px; }
  figcaption { color: var(--dim); font-size: 14px; margin-top: 8px; }
  p img, li img { vertical-align: middle; max-width: 100%; }
  code {
    background: #100d09; border: 1px solid var(--line); border-radius: 6px;
    padding: 1px 7px; font-size: 0.88em; color: #ffd9a0;
  }
  pre {
    background: #100d09; border: 1px solid var(--line); border-radius: 10px;
    padding: 12px 16px; overflow-x: auto; font-size: 14px; color: #ffd9a0;
  }
  table { border-collapse: collapse; margin: 14px 0; font-size: 14.5px; }
  table th, table td { border: 1px solid var(--line); padding: 6px 12px; text-align: left; }
  table th { background: var(--card2); }
  dl { margin: 12px 0; }
  dt { font-weight: 650; color: var(--ink); margin-top: 10px; }
  dd { margin: 2px 0 6px 22px; color: var(--dim); }
  dd p { margin: 4px 0; }
  blockquote { margin: 1em 0; border-left: 3px solid var(--accent); padding: 4px 16px; color: var(--dim); background: var(--card); border-radius: 0 10px 10px 0; }
  footer.site { max-width: 1000px; margin: 0 auto; padding: 26px 28px 60px; color: var(--faint); font-size: 14px; }
</style>
</head>
<body>

<nav class="top">
  <a class="brand" href="../">
    <img src="../images/burrtools-32.png" alt="" onerror="this.style.display='none'">
    <span><b>BurrTools</b></span>
  </a>
  <div class="links">
    <a href="../">Home</a>
    <a href="#toc">Contents</a>
    <a href="https://burr-tools.github.io/burr-tools/">API reference</a>
    <a href="https://github.com/burr-tools/burr-tools">GitHub</a>
  </div>
</nav>

<main>
  <h1>BurrTools <span class="em">User Guide</span></h1>
  <p class="byline">VERSION_LINE · AUTHOR_LINE</p>
  <div class="note">NOTE_LINE</div>
  <nav class="toc" id="toc"><h2>Contents</h2>
TOC_LINE
  </nav>
BODY_LINE
</main>

<footer class="site">
  BurrTools is free software under the GPL — free as in beer and as in speech.
  Sources: <a href="https://github.com/burr-tools/burr-tools">code</a> ·
  <a href="https://github.com/burr-tools/burr-tools.github.io">this site</a>
</footer>

</body>
</html>
'''

VERSION_LINE = f'For BurrTools {VERSION}. Originally written 2008–2010, revised for {VERSION} in 2026.'
AUTHOR_LINE = 'Andreas Röver, Ronald Kint-Bruynseels and contributors'
NOTE_LINE = ('This guide was revised for BurrTools 0.8 in 2026: installation, settings, '
             'solver and STL-export chapters were rewritten and new features documented. '
             'Some screenshots still show earlier versions of the interface.')


def find_txt2tags():
    exe = shutil.which('txt2tags')
    if exe:
        return [exe]
    return [sys.executable, '-m', 'txt2tags']


def main():
    text = SRC.read_text(encoding='utf8')

    # legacy toolchain directives: we expand the macros ourselves
    text = '\n'.join(l for l in text.splitlines()
                     if not l.startswith('%!postproc') and l.strip() != '@Hyp@')

    # --- figures ---------------------------------------------------------
    fig_labels = []

    def fig_sub(m):
        label, imgs, cap = m.group(1).strip(), m.group(2), m.group(3).strip()
        files = [p for p in re.split(r'\s+', imgs)
                 if p.strip().lower().endswith('.png')]
        fig_labels.append(label)
        return '@@FIGURE:%s|%s|%s@@' % (label, cap, ','.join(files))

    text = re.sub(r'@F@(.*?)\|(.*?)\|(.*?)@F@', fig_sub, text, flags=re.S)

    # --- header (title/author/date must be the first three lines) --------
    text = (f'{TITLE} for BurrTools {VERSION}\n{AUTHOR_LINE}\n'
            f'2008-2010, revised 2026\n' + text)
    TMP_T2T.write_text(text, encoding='utf8')

    # --- convert ----------------------------------------------------------
    cmd = find_txt2tags()
    r = subprocess.run(cmd + ['-t', 'html', '--toc', '-n',
                              '-o', str(TMP_HTML), str(TMP_T2T)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:], file=sys.stderr)
        sys.exit(f'{" ".join(cmd)} failed (need: pip install txt2tags)')

    h = TMP_HTML.read_text(encoding='utf8')

    labels = (set(re.findall(r'^=+.*?=\[([A-Za-z0-9_]+)\]', text, flags=re.M))
              | set(fig_labels))

    def fig_html(m):
        label, cap, files = m.group(1), m.group(2), m.group(3).split(',')
        imgs = ''.join(f'\n<img src="img/{f}" alt="">' for f in files)
        return (f'<figure id="{label}">{imgs}\n'
                f'<figcaption>Figure: {cap}</figcaption>\n</figure>')

    def img_sub(m):
        tag = m.group(0)
        return re.sub(r'src="([A-Za-z0-9_]+\.png)"', r'src="img/\1"', tag)

    h = re.sub(r'(?:<p>\s*)?@@FIGURE:([^|]+)\|([^|]+)\|([^@]+)@@(?:\s*</p>)?',
                 fig_html, h)
    h = re.sub(r'<img\b[^>]*>', img_sub, h)
    h = re.sub(r'@B@(.*?)@B@', r'<b><i>\1</i></b>', h)
    h = re.sub(r'@A@(.*?)@A@', r'<i>\1</i>', h)

    def link_sub(m):
        if m.group(2) in labels:
            return f'{m.group(1)}#{m.group(2)}{m.group(3)}'
        return m.group(0)

    h = re.sub(r'(<a href=")([A-Za-z0-9_]+)(")', link_sub, h)

    # --- typography & cleanup (outside pre/code) -----------------------------
    parts = re.split(r'(<pre>.*?</pre>|<code>.*?</code>)', h, flags=re.S)
    for i in range(0, len(parts), 2):
        parts[i] = parts[i].replace('---', '\u2014').replace('--/', '\u2192')
    h = ''.join(parts)
    h = re.sub(r'<p>\s*</p>', '', h)

    # --- diagnostics -------------------------------------------------------
    problems = []
    n_left = len(re.findall(r'@[ABFLx]@', h))
    if n_left:
        problems.append(f'{n_left} unexpanded @ macros')
    n_bare = len(re.findall(r'<a href="[A-Za-z][A-Za-z0-9_]*">', h))
    if n_bare:
        problems.append(f'{n_bare} internal links without # target')
    for src in sorted(set(re.findall(r'<img[^>]+src="([^"]+)"', h))):
        if not (HERE / src).exists():
            problems.append(f'missing image file: {src}')
    if problems:
        sys.exit('guide build problems:\n- ' + '\n- '.join(problems))

    # --- template ------------------------------------------------------------
    toc = re.search(r'<nav>(.*?)</nav>', h, flags=re.S).group(1)
    body = re.search(r'</nav>\s*<div class="body">(.*)</div>\s*</body>',
                     h, flags=re.S).group(1)
    # txt2tags numbers every header; drop the top-level duplicate title header
    body = re.sub(r'<section id="toc1">\s*<h1>[^<]*</h1>', '<section>', body,
                  count=1)

    page = (TEMPLATE
            .replace('VERSION_LINE', VERSION_LINE)
            .replace('AUTHOR_LINE', AUTHOR_LINE)
            .replace('NOTE_LINE', NOTE_LINE)
            .replace('TOC_LINE', toc)
            .replace('BODY_LINE', body))
    OUT.write_text(page, encoding='utf8')

    n_fig = len(re.findall(r'<figure', page))
    n_img = len(re.findall(r'<img', page))
    print(f'wrote {OUT} ({OUT.stat().st_size // 1024} KB, '
          f'{n_fig} figures, {n_img} images)')
    TMP_T2T.unlink()
    TMP_HTML.unlink()


if __name__ == '__main__':
    main()
