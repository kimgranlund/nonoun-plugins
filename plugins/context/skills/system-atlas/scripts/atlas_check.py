#!/usr/bin/env python3
"""atlas_check.py <page.html> - check an atlas page against the DESIGN contract.

Exits 1 and names every failure, or exits 0 with one "ok" line.
Python 3.9 stdlib only.
"""
import re
import json
import hashlib
from pathlib import Path
import sys

MAX_NODES = 14

EXACT_TOKENS = {
    "--hue": "235",
    "--r-control": "clamp(0.75rem,1.25rem,1.75rem)",
    "--r-container": "clamp(0.75rem,1.4vw,2.75rem)",
}

EXAMPLE_HEADING = "Example section: replace this whole block"

COLOR_FUNCS = r"\b(?:oklch|oklab|lch|lab|hwb|color|color-mix)\("

NAMED_COLORS = """aqua aquamarine azure beige bisque black blue brown chartreuse chocolate
coral crimson cyan darkblue darkgreen fuchsia gold goldenrod gray green grey indigo ivory
khaki lavender lime linen magenta maroon navy olive orange orchid pink plum purple red
salmon sienna silver snow tan teal thistle tomato turquoise violet wheat white yellow""".split()

MERMAID_KEYWORDS = set("""flowchart graph subgraph end direction stateDiagram stateDiagram-v2
sequenceDiagram classDiagram erDiagram journey gantt pie participant actor as Note note over
right left of autonumber state class classDef style linkStyle click call href accTitle accDescr
loop alt else opt par and rect activate deactivate LR RL TB BT TD v2 yes no""".split())


def strip_comments(css):
    return re.sub(r"/\*.*?\*/", " ", css, flags=re.S)


def strip_balanced(text, opener):
    """Remove every opener(...) span, honouring nested parens."""
    out = []
    i = 0
    while i < len(text):
        j = text.find(opener, i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j])
        k = j + len(opener)
        depth = 1
        while k < len(text) and depth:
            if text[k] == "(":
                depth += 1
            elif text[k] == ")":
                depth -= 1
            k += 1
        i = k
    return "".join(out)


def style_blocks(html):
    return re.findall(r"<style[^>]*>(.*?)</style>", html, flags=re.S | re.I)


def split_decls(body):
    out = []
    for decl in body.split(";"):
        if ":" not in decl:
            continue
        prop, value = decl.split(":", 1)
        out.append((prop.strip(), value.strip()))
    return out


def rules(css):
    """Yield (selector, body) for every rule block."""
    for sel, body in re.findall(r"([^{}]*)\{([^{}]*)\}", css):
        yield sel.strip(), body


def scrub_value(value):
    v = strip_balanced(value, "light-dark(")
    v = strip_balanced(v, "var(")
    v = re.sub(r"--[A-Za-z0-9_-]+", " ", v)
    return v


def check_decls(decls, fail, where):
    for prop, value in decls:
        v = scrub_value(value)
        hit = None
        if re.search(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})\b", v):
            hit = "a hex color"
        elif re.search(r"\brgba?\(", v):
            hit = "rgb()"
        elif re.search(r"\bhsla?\(", v):
            hit = "hsl()"
        elif re.search(r"\btransparent\b", v):
            hit = "bare transparent (use var(--none))"
        elif not prop.startswith("--") and re.search(COLOR_FUNCS, v, flags=re.I):
            hit = "a color function outside a token definition"
        elif not prop.startswith("--") and re.search(r"\bcurrentcolor\b", v, flags=re.I):
            hit = "currentColor outside a token definition"
        else:
            for name in NAMED_COLORS:
                if re.search(r"\b%s\b" % name, v):
                    hit = "the named color '%s'" % name
                    break
        if hit:
            fail("literal color in %s: %s in `%s: %s`" % (where, hit, prop, value))
        if prop.startswith("--") and re.search(COLOR_FUNCS + r"|#[0-9a-fA-F]{3}", value, flags=re.I):
            if "light-dark(" not in value:
                fail("color token `%s` does not use light-dark(): %s" % (prop, value))
        if prop == "border-radius" and not re.search(r"var\(--r-(?:control|container)\)", value):
            fail("border-radius in %s does not read var(--r-control) or var(--r-container): `%s`"
                 % (where, value))


def check_css(css, fail):
    seen = {}
    for sel, body in rules(css):
        decls = split_decls(body)
        check_decls(decls, fail, "the stylesheet")
        props = [p for p, _ in decls]
        if "border-radius" in props and not re.search(r"corner-shape\s*:\s*var\(--corner\)", body):
            fail("rule `%s` sets a border-radius without corner-shape:var(--corner)" % sel)
        themed = re.search(r"data-theme|data-scheme", sel)
        for prop, value in decls:
            if not prop.startswith("--"):
                continue
            if themed:
                fail("per-theme token redefinition in `%s`: `%s` must be defined once, with "
                     "light-dark()" % (sel, prop))
            seen.setdefault(prop, []).append(value)
            want = EXACT_TOKENS.get(prop)
            if want is not None and re.sub(r"\s+", "", value) != want:
                fail("token `%s` must be exactly `%s`, found `%s`" % (prop, want, value))
    for prop, values in seen.items():
        if len(values) > 1:
            fail("token `%s` is defined %d times; one definition per token" % (prop, len(values)))


def check_inline_styles(html, fail):
    for m in re.finditer(r"\bstyle=\"([^\"]*)\"", html):
        check_decls(split_decls(m.group(1)), fail, "an inline style attribute")


def mermaid_blocks(html):
    return re.findall(r"<pre[^>]*class=\"[^\"]*mermaid[^\"]*\"[^>]*>(.*?)</pre>", html, flags=re.S | re.I)


def count_nodes(block):
    text = re.sub(r"^\s*%%.*$", "", block, flags=re.M)
    text = re.sub(r"&[a-z]+;", " ", text)
    text = re.sub(r"<[^>]*>", " ", text)
    text = re.sub(r"\"[^\"]*\"", '""', text)
    if re.search(r"\bsequenceDiagram\b", text):
        return len(set(re.findall(r"^\s*(?:participant|actor)\s+([A-Za-z][A-Za-z0-9_]*)", text, flags=re.M)))
    if re.search(r"\bstateDiagram", text):
        ids = set()
        skip = False
        for raw in text.splitlines():
            line = raw.strip()
            if skip:
                skip = not re.match(r"end note\b", line)
                continue
            if re.match(r"note\b", line):
                skip = True
                continue
            line = line.split(":", 1)[0]
            if not re.search(r"-->", line):
                m = re.match(r"state\s+([A-Za-z][A-Za-z0-9_]*)", line)
                if m:
                    ids.add(m.group(1))
                continue
            for side in line.split("-->"):
                for tok in re.findall(r"[A-Za-z][A-Za-z0-9_]*", side):
                    if tok not in MERMAID_KEYWORDS:
                        ids.add(tok)
        return len(ids)
    ids = set()
    for m in re.finditer(r"([A-Za-z][A-Za-z0-9_]*)\s*(?:\[\[|\[\(|\(\(|\(\[|\{\{|\[|\(|\{|>)", text):
        if m.group(1) not in MERMAID_KEYWORDS:
            ids.add(m.group(1))
    for m in re.finditer(r"^\s*(?:participant|actor)\s+([A-Za-z][A-Za-z0-9_]*)", text, flags=re.M):
        ids.add(m.group(1))
    flat = re.sub(r"\[[^\]]*\]|\{[^}]*\}|\([^)]*\)", " ", text)
    flat = re.sub(r"[-=.<>|:~+]{1,}", " ", flat)
    for tok in re.findall(r"[A-Za-z][A-Za-z0-9_]*", flat):
        if tok not in MERMAID_KEYWORDS and not tok.startswith("accDescr"):
            ids.add(tok)
    for line in text.splitlines():
        m = re.match(r"\s*subgraph\s+([A-Za-z][A-Za-z0-9_]*)", line)
        if m:
            ids.discard(m.group(1))
    return len(ids)


def check_placeholders(html, fail):
    outside = re.sub(r"<pre[^>]*class=\"[^\"]*mermaid[^\"]*\"[^>]*>.*?</pre>", " ", html,
                     flags=re.S | re.I)
    left = sorted(set(re.findall(r"\{\{[A-Za-z][^}]*\}\}", outside)))
    for ph in left:
        fail("unfilled placeholder %s" % ph)
    if EXAMPLE_HEADING in html:
        fail("the template's example section is still in the page: %r" % EXAMPLE_HEADING)


def main(argv):
    if len(argv) != 2:
        print("usage: atlas_check.py <page.html>", file=sys.stderr)
        return 2
    path = argv[1]
    try:
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
    except OSError as exc:
        print("cannot read %s: %s" % (path, exc), file=sys.stderr)
        return 2

    failures = []

    def fail(msg):
        failures.append(msg)

    renderer = re.search(r'<script id="atlas-mermaid-renderer" data-sha256="([a-f0-9]+)">(.*?)</script>', html, flags=re.S)
    manifest = json.loads((Path(__file__).resolve().parent.parent / 'assets/vendor/manifest.json').read_text())
    if not renderer:
        fail("no bundled Mermaid renderer: local HTML must render without an artifact host")
    elif renderer.group(1) != manifest['sha256'] or hashlib.sha256(renderer.group(2).replace('<\\/script', '</script').encode()).hexdigest() != manifest['sha256']:
        fail("bundled Mermaid renderer hash does not match the pinned manifest")
    if 'id="atlas-render-diagrams"' not in html or 'await mermaid.run(' not in html:
        fail("no explicit Mermaid initialization and rendering lifecycle")
    # Vendor code is not page CSS, diagram source, or template placeholders.
    html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.S | re.I)

    css = strip_comments("\n".join(style_blocks(html)))
    if not css.strip():
        fail("no <style> block found")
    check_css(css, fail)
    check_inline_styles(html, fail)
    if re.search(r"@media[^{]*prefers-color-scheme", css, flags=re.I):
        fail("@media (prefers-color-scheme ...) present: switch through color-scheme only")
    if re.search(r"@import", css, flags=re.I):
        fail("@import in the stylesheet: no web fonts, no external CSS")
    if re.search(r"@font-face", css, flags=re.I):
        fail("@font-face in the stylesheet: system-ui and ui-monospace only")
    if re.search(r"<link[^>]*(?:stylesheet|font)", html, flags=re.I):
        fail("<link> to an external stylesheet or font: no web fonts")
    if re.search(r"fonts\.(?:googleapis|gstatic)\.com", html, flags=re.I):
        fail("a Google Fonts URL is present: no web fonts")

    blocks = mermaid_blocks(html)
    if not blocks:
        fail("no <pre class=\"mermaid\"> block found")
    for i, block in enumerate(blocks, 1):
        if "%%{init" in block:
            fail("mermaid block %d carries an %%%%{init directive: the host then prints the source as text" % i)
        n = count_nodes(block)
        if n > MAX_NODES:
            fail("mermaid block %d has about %d nodes, over the %d node limit: split the canvas" % (i, n, MAX_NODES))

    sections = re.findall(r"<section\b.*?</section>", html, flags=re.S | re.I)
    if not sections:
        fail("no <section> found")
    for i, sec in enumerate(sections, 1):
        eyebrows = re.findall(r"class=\"eyebrow\"[^>]*>(.*?)<", sec, flags=re.S | re.I)
        label = re.search(r"id=\"([^\"]+)\"", sec)
        who = label.group(1) if label else "#%d" % i
        if not eyebrows:
            fail("section %s has no eyebrow" % who)
        elif not any(re.search(r"outside-in|inside-out", e, flags=re.I) for e in eyebrows):
            fail("section %s eyebrow names no perspective (Outside-in or Inside-out): %r" % (who, eyebrows[0].strip()))

    footer = re.search(r"<footer\b(.*?)</footer>", html, flags=re.S | re.I)
    if not footer:
        fail("no <footer>: the footer must name the commit the atlas was drawn from")
    elif "{{COMMIT}}" not in footer.group(1) and not re.search(r"\b[0-9a-f]{7,40}\b", footer.group(1)):
        fail("footer names no commit sha")

    check_placeholders(html, fail)

    if re.search(chr(0x2014), html):
        line = html.count("\n", 0, html.index(chr(0x2014))) + 1
        fail("em dash (U+2014) on line %d" % line)

    if failures:
        print("%d failure(s) in %s" % (len(failures), path))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("ok %s: tokens, radii, fonts, diagrams, perspectives and footer all check out" % path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
