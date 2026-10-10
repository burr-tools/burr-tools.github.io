#!/usr/bin/env python3
"""Prototype Markdown guide builder: guide-md/*.md -> single + multi-page HTML.

Usage (website repo root):
    pip install markdown            # once (pure python)
    python3 guide-md/build_md.py    # writes guide-md/site/index.html (all-in-one)
                                    #   and guide-md/site/<slug>/index.html (multi-page)

Shares the dark theme of guide/build_guide.py (CSS copied, not imported, so
the prototype stands alone). Internal '#Label' links are rewritten to
'<page>.html#Label' when the label lives on another chapter page.
"""
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
SRC = ROOT
OUT = ROOT / 'site'

MD_EXT = ['def_list', 'attr_list', 'toc', 'sane_lists', 'smarty']

CSS = '''
  :root{--bg:#16130f;--bg2:#1e1a14;--card:#241f17;--card2:#2b2419;--ink:#f2ead9;
  --dim:#b3a78e;--faint:#7d7461;--accent:#f0a832;--line:#3a3226}
  *{box-sizing:border-box}html{scroll-behavior:smooth}
  body{margin:0;background:var(--bg);color:var(--ink);
  font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.65}
  a{color:var(--accent)}a:hover{color:#ffd080}
  nav.top{display:flex;align-items:center;gap:22px;padding:14px 28px;max-width:1000px;margin:0 auto}
  .brand{color:var(--ink);text-decoration:none;font-size:20px;font-weight:650}
  nav.top .links{margin-left:auto;display:flex;gap:4px;flex-wrap:wrap}
  nav.top .links a{color:var(--dim);text-decoration:none;font-size:15px;padding:8px 12px;border-radius:8px}
  nav.top .links a:hover{color:var(--ink);background:var(--card)}
  main{max-width:1000px;margin:0 auto;padding:10px 28px 60px}
  nav.chapters{background:var(--card);border:1px solid var(--line);border-radius:14px;
  padding:12px 22px;margin:0 0 24px;font-size:14.5px;color:var(--dim)}
  nav.chapters ol{margin:6px 0;padding-left:22px}
  nav.pager{display:flex;justify-content:space-between;gap:12px;margin-top:36px;font-size:15px}
  figure{background:var(--card);border:1px solid var(--line);border-radius:14px;
  padding:16px;margin:20px 0;text-align:center}
  figure img{max-width:100%;height:auto;margin:6px auto;border-radius:6px}
  figcaption{color:var(--dim);font-size:14px;margin-top:8px}
  code{background:#100d09;border:1px solid var(--line);border-radius:6px;
  padding:1px 7px;font-size:.88em;color:#ffd9a0}
  pre{background:#100d09;border:1px solid var(--line);border-radius:10px;
  padding:12px 16px;overflow-x:auto;font-size:14px;color:#ffd9a0}
  dl{margin:12px 0}dt{font-weight:650;margin-top:10px}dd{margin:2px 0 6px 22px;color:var(--dim)}
  footer.site{max-width:1000px;margin:0 auto;padding:26px 28px 60px;color:var(--faint);font-size:14px}
'''

TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — BurrTools User Guide</title>
<style>{css}</style>
</head>
<body>
<nav class="top">
  <a class="brand" href="../../">BurrTools</a>
  <div class="links">
    <a href="../../">Home</a>
    <a href="../">Guide contents</a>
    <a href="https://burr-tools.github.io/burr-tools/">API reference</a>
    <a href="https://github.com/burr-tools/burr-tools">GitHub</a>
  </div>
</nav>
<main>
{chapters_nav}
{body}
{pager}
</main>
<footer class="site">
  BurrTools user guide (Markdown prototype) — sources: <a href="https://github.com/burr-tools/burr-tools.github.io">this site</a>
</footer>
</body>
</html>
'''


def load_chapters():
    chapters = []
    for md in sorted(SRC.glob('*.md')):
        text = md.read_text(encoding='utf8')
        m = re.match(r'---\ntitle: "(.*?)"\nnav_order: (\d+)\n---\n\n(.*)$',
                     text, flags=re.S)
        title, order, body = m.group(1), int(m.group(2)), m.group(3)
        chapters.append({'slug': md.stem, 'title': title,
                         'order': order, 'body': body})
    return sorted(chapters, key=lambda c: c['order'])


def render(chapters):
    for ch in chapters:
        ch['html'] = markdown.markdown(ch['body'], extensions=MD_EXT)
        ch['labels'] = set(re.findall(r'id="([A-Za-z0-9_]+)"', ch['html']))
        ch['labels'] |= set(re.findall(r'<h[1-4][^>]* id="([A-Za-z0-9_]+)"',
                                        ch['html']))
    label_page = {}
    for ch in chapters:
        for lab in ch['labels']:
            label_page[lab] = ch['slug']
    return label_page


def fix_links(html, own_slug, label_page, depth):
    def sub(m):
        lab = m.group(1)
        page = label_page.get(lab)
        if page is None or page == own_slug:
            return f'href="#{lab}"'
        prefix = '../' * depth
        return f'href="{prefix}{page}/#{lab}"'
    html = re.sub(r'href="#([A-Za-z0-9_]+)"', sub, html)
    # images point at the existing guide/img/ store; keep them relative
    html = re.sub(r'src="\.\./guide/img/',
                  'src="' + '../' * depth + '../guide/img/', html)
    return html


def main():
    chapters = load_chapters()
    label_page = render(chapters)
    OUT.mkdir(exist_ok=True)

    nav = ('<nav class="chapters"><b>Guide contents</b><ol>' +
           ''.join(f'<li><a href="{c["slug"]}/">{c["title"]}</a></li>'
                   for c in chapters) + '</ol></nav>')

    # multi-page
    for i, ch in enumerate(chapters):
        prev = (f'<a href="../{chapters[i-1]["slug"]}/">← {chapters[i-1]["title"]}</a>'
                if i > 0 else '<span></span>')
        nxt = (f'<a href="../{chapters[i+1]["slug"]}/">{chapters[i+1]["title"]} →</a>'
               if i + 1 < len(chapters) else '<span></span>')
        body = fix_links(ch['html'], ch['slug'], label_page, depth=1)
        page = TEMPLATE.format(title=ch['title'], css=CSS, chapters_nav=nav,
                               body=body,
                               pager=f'<nav class="pager">{prev}{nxt}</nav>')
        d = OUT / ch['slug']
        d.mkdir(exist_ok=True)
        (d / 'index.html').write_text(page, encoding='utf8')

    # all-in-one page (parity check against guide/index.html)
    (OUT / 'contents.html').write_text(
        TEMPLATE.format(title='Contents', css=CSS, chapters_nav='',
                        body=nav, pager=''), encoding='utf8')
    all_body = ''.join(
        f'<section id="page-{c["slug"]}">'
        + fix_links(c['html'], c['slug'], label_page, depth=0)
        + '</section>' for c in chapters)
    (OUT / 'index.html').write_text(
        TEMPLATE.format(title='User Guide', css=CSS, chapters_nav=nav,
                        body=all_body, pager=''), encoding='utf8')

    n_fig = sum(c['html'].count('<figure') for c in chapters)
    n_img = sum(c['html'].count('<img') for c in chapters)
    print(f'{len(chapters)} chapters, {len(label_page)} anchors, '
          f'{n_fig} figures, {n_img} images -> {OUT}')


if __name__ == '__main__':
    sys.exit(main())
