#!/usr/bin/env python3
"""One-shot migration: userGuide.t2t (txt2tags) -> guide-md/*.md (Markdown).

Run once from the website repo root:
    python3 guide/t2t_to_md.py

Reads guide/userGuide.t2t, splits the 10 top-level '=...=' chapters into
guide-md/<slug>.md files with YAML front matter (title, nav order).

Deliberately small on purpose: figures (@F@) become raw-HTML <figure> blocks
(which Markdown passes through), GUI macros @A@/@B@ become *...* / ***...***,
': **Term**' definition lists become PHP-extra style 'Term\\n:   def' blocks
(Python-Markdown 'def_list' / Kramdown understand them), and '[text Label]'
internal links become '[text](#Label)'.
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
SRC = ROOT / 'guide' / 'userGuide.t2t'
DST = ROOT / 'guide-md'

TOP_CHAPTERS = [
    ('Prologue', 'prologue'),
    ('Getting Started', 'getting-started'),
    ('The BurrTools Interface', 'interface'),
    ('Shapes', 'shapes'),
    ('Defining Puzzles', 'puzzles'),
    ('Solving Puzzles', 'solving'),
    ('Reporting with BurrTools', 'reporting'),
    ('Scripting with Python', 'scripting'),
    ('What Came Next', 'what-came-next'),
    ('Appendix', 'appendix'),
]


def slug_for(title):
    for t, s in TOP_CHAPTERS:
        if t.lower() in title.lower() or title.lower() in t.lower():
            return s
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')


def inline_md(s):
    # code first so its contents are not touched by other rules
    s = re.sub(r'``(.*?)``', r'`\1`', s, flags=re.S)
    s = re.sub(r'@B@(.*?)@B@', r'***\1***', s, flags=re.S)
    s = re.sub(r'@A@(.*?)@A@', r'*\1*', s, flags=re.S)
    s = re.sub(r'\*\*(.*?)\*\*', r'**\1**', s, flags=re.S)
    s = re.sub(r'//(.*?)//', r'*\1*', s, flags=re.S)
    s = s.replace('--/', '\u2192').replace('---', '\u2014')
    return s


def convert_figure(m):
    label, imgs, cap = m.group(1).strip(), m.group(2), m.group(3).strip()
    files = [p for p in re.split(r'\s+', imgs)
             if p.strip().lower().endswith('.png')]
    tags = ''.join(f'\n<img src="../guide/img/{f}" alt="">' for f in files)
    return (f'<figure id="{label}">{tags}\n'
            f'<figcaption>Figure: {inline_md(cap)}</figcaption>\n</figure>')


def main():
    text = SRC.read_text(encoding='utf8', errors='replace')
    text = '\n'.join(l for l in text.splitlines()
                     if not l.startswith('%!postproc') and l.strip() != '@Hyp@')
    text = re.sub(r'@F@(.*?)\|(.*?)\|(.*?)@F@', convert_figure, text, flags=re.S)

    labels = set(re.findall(r'^=+\s*.*\[([A-Za-z0-9_]+)\]\s*$', text, flags=re.M))
    labels |= set(re.findall(r'<figure id="([A-Za-z0-9_]+)">', text))

    def link_sub(m):
        inner = m.group(1)
        if re.fullmatch(r'[A-Za-z0-9_]+\.png', inner):
            # toolbar-icon term, e.g. ': [Button_Toolbar_Draw_Brush.png]:'
            return f'![](../guide/img/{inner})'
        parts = inner.rsplit(' ', 1)
        if len(parts) == 2 and re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*', parts[1]):
            if parts[1] in labels:
                return f'[{parts[0]}](#{parts[1]})'
            if parts[1].startswith(('http://', 'https://', '#')):
                return f'[{parts[0]}]({parts[1]})'
            return f'[{parts[0]}]({parts[1]})'
        if inner.startswith(('http://', 'https://')):
            return f'<{inner}>'
        return m.group(0)

    text = re.sub(r'\[([^\[\]\n]+)\]', link_sub, text)

    # split into chapters on single-= headers (==, === ... are sub-headers).
    # Top-level headers may carry a trailing [Label] anchor (=Shapes=[ChShapes]).
    parts = re.split(r'(?m)^=(?!=)\s*(.+?)\s*=\s*(\[[A-Za-z0-9_]+\])?\s*$', text)
    # parts[0] is preamble (encoding line etc, empty); then title/label/body triples
    chapters = []
    for i in range(1, len(parts), 3):
        title = parts[i].strip()
        label = (parts[i + 1] or '').strip('[]')
        chapters.append((title, label, parts[i + 2]))

    DST.mkdir(exist_ok=True)
    order = {s: n for n, (_, s) in enumerate(TOP_CHAPTERS)}
    for title, label, body in chapters:
        slug = slug_for(title)
        anchor_suffix = f' {{#{label}}}' if label else ''
        lines = [f'# {inline_md(title)}{anchor_suffix}', '']
        in_def = False
        for line in body.splitlines():
            if line.strip() == '%%toc':
                in_def = False
                continue
            mh = re.match(r'^(={2,})\s*(.*?)\s*={2,}\s*(\[[A-Za-z0-9_]+\])?\s*$', line)
            if mh and len(mh.group(1)) >= 2:
                in_def = False
                level = len(mh.group(1))  # == -> h2 (h1 is page title)
                htitle = inline_md(mh.group(2).strip())
                anchor = (mh.group(3) or '').strip('[]')
                suffix = f' {{#{anchor}}}' if anchor else ''
                lines.append(f'{"#" * level} {htitle}{suffix}')
                lines.append('')
                continue
            md = re.match(r'^: +(.*)$', line)
            if md:
                if in_def:
                    lines.append('')
                lines.append(inline_md(md.group(1).strip()))
                lines.append(':   ')
                in_def = True
                continue
            if line.strip() == '':
                in_def = False
                lines.append('')
                continue
            if in_def and not re.match(r'^([-*] |\d+\. |<figure|```)', line):
                # continuation of a definition-list definition
                if lines and lines[-1] == ':   ':
                    lines[-1] = ':   ' + inline_md(line.strip())
                else:
                    lines.append(inline_md(line.strip()))
                continue
            in_def = False
            if re.match(r'^- ', line):
                lines.append('- ' + inline_md(line[2:]))
            elif line.startswith('<figure') or line.startswith('<img') \
                    or line.startswith('<figcaption') or line.startswith('</figure'):
                lines.append(line)
            else:
                lines.append(inline_md(line))
        md_text = ('---\n'
                   f'title: "{title}"\n'
                   f'nav_order: {order.get(slug, 99)}\n'
                   '---\n\n'
                   + '\n'.join(lines).strip() + '\n')
        (DST / f'{slug}.md').write_text(md_text, encoding='utf8')
        print(f'wrote {slug}.md ({len(md_text) // 1024} KB)')
    print(f'{len(chapters)} chapters, {len(labels)} anchors preserved')


if __name__ == '__main__':
    sys.exit(main())
