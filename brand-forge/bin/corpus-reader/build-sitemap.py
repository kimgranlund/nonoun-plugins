#!/usr/bin/env python3
"""Build lib/sitemap.json for the corpus-reader from a directory of Markdown files.

Scans CORPUS_DIR for `.md` files, groups them by their top-level section folder,
extracts a title + one-line summary for each, and writes the sitemap the static
reader (index.html) loads. Works for any generated corpus, not just the bundled
example.

    python3 build-sitemap.py [CORPUS_DIR] [--out lib/sitemap.json] [--title TITLE]

CORPUS_DIR defaults to the single sibling directory that contains `.md` files
(e.g. the bundled `brand-corpus`). Page paths are written relative to this
script's directory — where index.html lives — so the reader can fetch them
directly. Pass `..` to generate for a viewer that lives in a SUBFOLDER of the
corpus (the `<corpus>/site/` export layout): paths come out `../<section>/…`,
and this script's own directory is excluded from the scan. Re-run after the
corpus changes. Python 3.8+, stdlib only.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {"lib", ".git", "node_modules"}


def find_corpus(root):
    """Sibling directories that contain at least one .md file."""
    found = []
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if not os.path.isdir(path) or name in SKIP_DIRS or name.startswith("."):
            continue
        for _dirpath, _dirnames, files in os.walk(path):
            if any(f.endswith(".md") for f in files):
                found.append(name)
                break
    return found


def split_frontmatter(text):
    """Return (meta_dict, body) splitting a leading `--- ... ---` YAML block.

    Only flat `key: value` pairs are read — enough for the meta bar; this is not
    a full YAML parser.
    """
    meta = {}
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.DOTALL)
    if not match:
        return meta, text
    for line in match.group(1).splitlines():
        pair = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if pair:
            meta[pair.group(1).strip()] = pair.group(2).strip().strip('"').strip("'")
    return meta, text[match.end():]


def first_heading(body):
    for line in body.splitlines():
        m = re.match(r"^#\s+(.*)$", line)
        if m:
            return m.group(1).strip()
    return None


def first_paragraph(body):
    """The first real prose paragraph, flattened to a short plain-text summary."""
    buf = []
    in_fence = started = False
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not started:
            if s == "" or s[:1] in ("#", ">", "|", "-", "*") or s.startswith("---"):
                continue
            started = True
            buf.append(s)
        elif s == "":
            break
        else:
            buf.append(s)
    text = " ".join(buf)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)  # [label](url) -> label
    text = re.sub(r"[*_`#>]", "", text).strip()
    return (text[:197].rstrip() + "…") if len(text) > 198 else text


def prettify(name):
    name = re.sub(r"\.md$", "", name)
    name = re.sub(r"^\d+[-_]+", "", name)
    name = name.replace("-", " ").replace("_", " ").strip()
    return (name[:1].upper() + name[1:]) if name else name


def section_order(folder):
    m = re.match(r"^(\d+)", folder)
    return int(m.group(1)) if m else 9999


def main():
    ap = argparse.ArgumentParser(description="Generate lib/sitemap.json for the corpus-reader.")
    ap.add_argument("corpus", nargs="?", default=None, help="corpus directory (default: auto-detect)")
    ap.add_argument("--out", default=os.path.join("lib", "sitemap.json"), help="output path (default: lib/sitemap.json)")
    ap.add_argument("--title", default=None, help="corpus title (default: root README H1, else dir name)")
    args = ap.parse_args()

    corpus = args.corpus
    if not corpus:
        candidates = find_corpus(ROOT)
        if len(candidates) == 1:
            corpus = candidates[0]
        elif not candidates:
            sys.exit("error: no corpus directory with .md files found — pass one explicitly")
        else:
            sys.exit("error: multiple corpus dirs found (%s) — pass one explicitly" % ", ".join(candidates))

    corpus = corpus.rstrip("/")
    corpus_abs = os.path.join(ROOT, corpus)
    if not os.path.isdir(corpus_abs):
        sys.exit("error: not a directory: %s" % corpus)

    entries = []
    for dirpath, dirnames, filenames in os.walk(corpus_abs):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and os.path.join(dirpath, d) != ROOT]
        for fname in filenames:
            if not fname.endswith(".md") or fname.startswith("."):
                continue
            full = os.path.join(dirpath, fname)
            rel_index = os.path.relpath(full, ROOT).replace(os.sep, "/")
            rel_corpus = os.path.relpath(full, corpus_abs).replace(os.sep, "/")
            entries.append((rel_index, rel_corpus, full))

    if not entries:
        sys.exit("error: no .md files under %s" % corpus)

    sections = {}
    root_pages = []
    for rel_index, rel_corpus, full in sorted(entries, key=lambda t: t[1].lower()):
        with open(full, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        meta, body = split_frontmatter(text)
        page = {
            "path": rel_index,
            "title": meta.get("title") or first_heading(body) or prettify(os.path.basename(rel_corpus)),
        }
        summary = first_paragraph(body)
        if summary:
            page["summary"] = summary
        if meta.get("status"):
            page["status"] = meta["status"]

        parts = rel_corpus.split("/")
        if len(parts) == 1:
            root_pages.append(page)
        else:
            folder = parts[0]
            section = sections.setdefault(
                folder,
                {"id": folder, "title": prettify(folder), "order": section_order(folder), "pages": []},
            )
            section["pages"].append(page)

    section_list = sorted(sections.values(), key=lambda s: (s["order"], s["title"].lower()))
    for section in section_list:
        del section["order"]  # ordering is now positional

    title = args.title or (root_pages[0]["title"] if root_pages else prettify(corpus))

    sitemap = {"title": title, "base": corpus, "rootPages": root_pages, "sections": section_list}

    out_path = os.path.join(ROOT, args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(sitemap, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    pages = len(root_pages) + sum(len(s["pages"]) for s in section_list)
    print("wrote %s — %d page(s), %d section(s), title=%r" % (args.out, pages, len(section_list), title))


if __name__ == "__main__":
    main()
