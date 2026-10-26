#!/usr/bin/env python3
"""atlas_build.py <atlas.json> <out.html> - assemble an atlas page from one JSON file.

Fills assets/page-template.html: drops the example section, builds the nav, emits one
section per concept and the three table sections (inventory, enforcement matrix,
findings), and replaces every placeholder. Then runs scripts/atlas_check.py on the
result and exits with the checker's code.

Refuses, before writing anything, a section whose perspective is not Outside-in or
Inside-out, a section without exactly 3 rules, and a sections count that disagrees with
scope.size. Every refusal names the field and the section.

Python 3.9 stdlib only. See assets/atlas.example.json for the input shape.
"""
import html
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
TEMPLATE = os.path.join(SKILL, "assets", "page-template.html")
CHECKER = os.path.join(HERE, "atlas_check.py")

PERSPECTIVES = ("Outside-in", "Inside-out")
RULES_PER_SECTION = 3
TABLES = (
    ("inventory", "Inventory", ["Kind", "Count", "Items", "Evidence"]),
    ("matrix", "Enforcement matrix", ["Rule", "Stated in", "Rung", "Enforcer", "State"]),
    ("findings", "Findings", ["State", "Finding", "Detail"]),
)
TABLE_TITLES = {
    "inventory": "What the scan found, by kind",
    "matrix": "Every rule against its rung and enforcer",
    "findings": "Where the two drawings disagree",
}
TABLE_LEDES = {
    "inventory": "One row per machinery kind, with the evidence path the count came from.",
    "matrix": "Rung 1 could be read, rung 2 prose says must, rung 3 a procedure or tool list "
              "does it right, rung 4 a machine or an independent grader refuses the wrong way.",
    "findings": "Each row is a finding, not a fix.",
}


class AtlasBuildError(Exception):
    """A refusal: the atlas.json breaks the contract, so no page is written."""


def need(data, key, where):
    if key not in data:
        raise AtlasBuildError("%s: missing field %r" % (where, key))
    return data[key]


def validate(atlas):
    scope = need(atlas, "scope", "atlas.json")
    sections = need(atlas, "sections", "atlas.json")
    if not isinstance(sections, list) or not sections:
        raise AtlasBuildError("atlas.json: sections must be a non-empty list")

    size = need(scope, "size", "scope")
    try:
        size = int(size)
    except (TypeError, ValueError):
        raise AtlasBuildError("scope.size is not a number: %r" % (size,))
    if len(sections) != size:
        raise AtlasBuildError(
            "size mismatch: scope.size is %d but sections has %d entries. The scope line and "
            "the page must agree." % (size, len(sections)))

    for i, sec in enumerate(sections, 1):
        who = "section %d (%s)" % (i, sec.get("slug", "no slug"))
        for key in ("slug", "perspective", "nav", "title", "lede", "rules", "mermaid"):
            need(sec, key, who)
        if sec["perspective"] not in PERSPECTIVES:
            raise AtlasBuildError(
                "%s: perspective is %r, must be one of %s. Every eyebrow names its perspective; "
                "atlas_check.py fails a page where one does not."
                % (who, sec["perspective"], " or ".join(PERSPECTIVES)))
        rules = sec["rules"]
        if not isinstance(rules, list) or len(rules) != RULES_PER_SECTION:
            raise AtlasBuildError(
                "%s: rules has %d entries, must have exactly %d."
                % (who, len(rules) if isinstance(rules, list) else 0, RULES_PER_SECTION))

    for key, label, head in TABLES:
        rows = need(atlas, key, "atlas.json")
        if not isinstance(rows, list) or not rows:
            raise AtlasBuildError("%s: must be a non-empty list of rows (%s)" % (key, label))
        for n, row in enumerate(rows, 1):
            if not isinstance(row, list) or len(row) != len(head):
                raise AtlasBuildError(
                    "%s row %d has %d cells, must have %d: %s"
                    % (key, n, len(row) if isinstance(row, list) else 0, len(head), ", ".join(head)))


def section_html(i, sec):
    lis = "".join("        <li>%s</li>\n" % r for r in sec["rules"])
    return (
        '<section id="%s">\n  <div class="head">\n'
        '    <div><p class="eyebrow">%s &middot; Concept %d</p><h2>%s</h2></div>\n'
        "    <div>\n      <p>%s</p>\n"
        '      <ul class="rules">\n%s      </ul>\n    </div>\n  </div>\n'
        '  <div class="canvas"><pre class="mermaid">\n%s\n</pre></div>\n</section>\n'
    ) % (sec["slug"], sec["perspective"], i, sec["title"], sec["lede"], lis,
         html.escape(sec["mermaid"], quote=False))


def table_html(rows, head):
    th = "".join("<th>%s</th>" % h for h in head)
    body = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in row) for row in rows)
    return ('<div class="tablewrap"><table>\n    <thead><tr>%s</tr></thead>\n'
            "    <tbody>%s</tbody>\n  </table></div>" % (th, body))


def table_section_html(atlas, key, label, head):
    titles = atlas.get("table_titles", {})
    ledes = atlas.get("table_ledes", {})
    return (
        '<section id="%s">\n  <div class="head">\n'
        '    <div><p class="eyebrow">Inside-out &middot; %s</p><h2>%s</h2></div>\n'
        "    <div><p>%s</p></div>\n  </div>\n  %s\n</section>\n"
    ) % (key, label, titles.get(key, TABLE_TITLES[key]), ledes.get(key, TABLE_LEDES[key]),
         table_html(atlas[key], head))


def drop_example(page):
    start = page.find('<section id="c1">')
    if start < 0:
        raise AtlasBuildError("page-template.html has no example section id=\"c1\" to drop")
    end = page.index("</section>", start) + len("</section>")
    return page[:start] + page[end:]


def build(atlas):
    validate(atlas)
    with open(TEMPLATE, encoding="utf-8") as fh:
        page = drop_example(fh.read())

    vendor = os.path.join(SKILL, "assets", "vendor")
    with open(os.path.join(vendor, "manifest.json"), encoding="utf-8") as fh:
        renderer = json.load(fh)
    with open(os.path.join(vendor, renderer["file"]), "rb") as fh:
        renderer_bytes = fh.read()
    if hashlib.sha256(renderer_bytes).hexdigest() != renderer["sha256"]:
        raise AtlasBuildError("bundled Mermaid renderer hash differs from vendor manifest")
    renderer_js = renderer_bytes.decode("utf-8").replace("</script", "<\\/script")
    page = page.replace("<!-- ATLAS RENDERER -->", '<script id="atlas-mermaid-renderer" data-sha256="%s">%s</script>' % (renderer["sha256"], renderer_js))

    sections = atlas["sections"]
    body = "".join(section_html(i, s) for i, s in enumerate(sections, 1))
    body += "".join(table_section_html(atlas, k, label, head) for k, label, head in TABLES)

    nav = "".join('<a href="#%s">%d %s</a>' % (s["slug"], i, s["nav"])
                  for i, s in enumerate(sections, 1))
    nav += "".join('<a href="#%s">%s</a>' % (k, k) for k, _, _ in TABLES)
    page = re.sub(r'<a href="#c1">.*?</a><!-- NAV LINKS -->', lambda m: nav, page)
    page = page.replace("<!-- SECTIONS -->", body)

    scope = atlas["scope"]
    paths = atlas["source_paths"]
    if isinstance(paths, list):
        paths = ", ".join(paths)
    for token, value in (
        ("{{SYSTEM}}", atlas["system"]),
        ("{{Harness}}", scope["subject"]),
        ("{{The Harness, Overview lens}}", scope["playbook"]),
        ("{{a new contributor}}", scope["reader"]),
        ("{{size 9 diagrams}}", "%d diagrams" % int(scope["size"])),
        ("{{what is out of scope and why}}", scope.get("skipped", "nothing")),
        ("{{SOURCE PATHS}}", paths),
        ("{{BRANCH}}", atlas["branch"]),
        ("{{COMMIT}}", atlas["commit"]),
        ("{{DATE}}", atlas["date"]),
    ):
        page = page.replace(token, str(value))

    outside = re.sub(r'<pre[^>]*class="[^"]*mermaid[^"]*"[^>]*>.*?</pre>', " ", page,
                     flags=re.S | re.I)
    outside = re.sub(r'<script\b[^>]*>.*?</script>', '', outside, flags=re.S | re.I)
    left = sorted(set(re.findall(r"\{\{[A-Za-z][^}]*\}\}", outside)))
    if left:
        raise AtlasBuildError("placeholders the template carries but atlas.json does not fill: %s"
                              % ", ".join(left))
    return page


def main(argv):
    if len(argv) != 3:
        print("usage: atlas_build.py <atlas.json> <out.html>", file=sys.stderr)
        return 2
    src, out = argv[1], argv[2]
    try:
        with open(src, encoding="utf-8") as fh:
            atlas = json.load(fh)
    except OSError as exc:
        print("cannot read %s: %s" % (src, exc), file=sys.stderr)
        return 2
    except ValueError as exc:
        print("%s is not valid JSON: %s" % (src, exc), file=sys.stderr)
        return 2

    try:
        page = build(atlas)
    except AtlasBuildError as exc:
        print("AtlasBuildError: %s" % exc, file=sys.stderr)
        return 2

    with open(out, "w", encoding="utf-8") as fh:
        fh.write(page)
    print("wrote %s: %d sections, %d bytes" % (out, len(atlas["sections"]), len(page)))
    return subprocess.call([sys.executable, CHECKER, out])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
