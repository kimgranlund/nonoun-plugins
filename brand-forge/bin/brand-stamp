#!/usr/bin/env python3
"""brand-stamp — stamp a finished brand corpus into a distributable artifact.

Three forms, by destination — each emitted into its OWN folder under <out>, kept pure and separate
(see skills/brand-corpus/references/stamping.md):

  plugin  <out>/plugin/<brand>-brand/      installable plugin (corpus + stdio MCP + skill) — Claude Code / Cowork
  skill   <out>/skill/<brand>-brand/       a standard Agent Skill (corpus bundled in references/) — Claude chat
  mcp     <out>/mcp/<brand>-brand-mcp/     a standalone deployable MCP (server + corpus + wiring) — claude mcp add / self-host

Usage:
  brand-stamp plugin <corpus_dir> --name <brand> -o <out_dir> [--linked] [--version V]
  brand-stamp skill  <corpus_dir> --name <brand> -o <out_dir>
  brand-stamp mcp    <corpus_dir> --name <brand> -o <out_dir> [--linked]
      --linked   (plugin/mcp) point the MCP at a live corpus_dir instead of bundling a snapshot
      --version  (plugin) plugin.json version — bump on each re-stamp; baking a corpus is a release action

A bundled corpus is a baked SNAPSHOT — the editable source-of-truth lives in the consumer's workspace,
never here. Mechanical scaffolding only; readiness/quality judgment lives in /brand-stamp + the
brand-corpus skill. Stdlib only (Python 3.8+). The plugin form is built to pass plugins-factory's
validate_plugin.py.
"""
import argparse
import json
import os
import re
import shutil
import sys

LAYER_DIR = re.compile(r"^\d\d-[a-z][a-z0-9-]*$")
FLAT_DOC = re.compile(r"^(\d\d-[a-z][a-z0-9-]*)--(.+)\.md$")
KEBAB = re.compile(r"[^a-z0-9]+")


def _kebab(s):
    return KEBAB.sub("-", s.strip().lower()).strip("-")


def read_corpus(corpus):
    """Return (docs, extras): docs = [(layer, name, text)] from either convention; extras = [(rel, abs)]
    for token files carried verbatim."""
    if not os.path.isdir(corpus):
        sys.exit(f"brand-stamp: corpus dir not found: {corpus}")
    docs, extras = [], []
    for entry in sorted(os.listdir(corpus)):
        full = os.path.join(corpus, entry)
        if os.path.isdir(full) and LAYER_DIR.match(entry):                # folder convention
            for f in sorted(os.listdir(full)):
                if f.endswith(".md"):
                    docs.append((entry, f[:-3], open(os.path.join(full, f), encoding="utf-8").read()))
        elif os.path.isfile(full):
            m = FLAT_DOC.match(entry)                                     # flat convention
            if m:
                docs.append((m.group(1), m.group(2), open(full, encoding="utf-8").read()))
            elif "token" in entry.lower() and entry.lower().endswith((".json", ".css")):
                extras.append((entry, full))
    if not docs:
        sys.exit(f"brand-stamp: no brand-corpus documents found in {corpus} "
                 f"(expected NN-layer/ dirs or NN-layer--name.md files)")
    return docs, extras


def _write_folder_corpus(dest, docs, extras, brand):
    """Write docs in folder convention (path = layer) under dest/, plus token files and an INDEX.md manifest."""
    by_layer = {}
    for layer, nm, text in docs:
        os.makedirs(os.path.join(dest, layer), exist_ok=True)
        open(os.path.join(dest, layer, f"{nm}.md"), "w", encoding="utf-8").write(text)
        by_layer.setdefault(layer, []).append(nm)
    for rel, src in extras:
        shutil.copy2(src, os.path.join(dest, rel))
    lines = [f"# {brand} — brand corpus index", "",
             f"{len(docs)} document(s) across {len(by_layer)} layer(s). Read by layer; 01-foundation is load-bearing."]
    for layer in sorted(by_layer):
        lines += ["", f"## {layer}"] + [f"- `{layer}/{nm}.md`" for nm in sorted(by_layer[layer])]
    if extras:
        lines += ["", "## tokens"] + [f"- `{rel}`" for rel, _ in extras]
    open(os.path.join(dest, "INDEX.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")


def _ref_mcp():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "brand-corpus-mcp.py")


def _copy_mcp(dst):
    shutil.copy2(_ref_mcp(), dst)
    os.chmod(dst, 0o755)


def _write_json(path, obj):
    open(path, "w", encoding="utf-8").write(json.dumps(obj, indent=2) + "\n")


def _thin_skill(brand, docs, retrieval):
    name = f"{_kebab(brand)}-brand"
    layers = ", ".join(sorted({l for l, _, _ in docs})) or "(none yet)"
    return (
        f"---\nname: {name}\ndescription: >\n"
        f"  The {brand} brand — its cultural foundation, positioning, identity, voice, and tokens. Use when\n"
        f"  working on, referencing, or extending the {brand} brand: its position, point of view, voice, or guidelines.\n"
        f"---\n\n"
        f"# {brand} — brand\n\n"
        f"This skill carries the **{brand}** brand corpus — the layered foundation → expression → stewardship\n"
        f"documents. {retrieval}\n\n"
        f"**Layers present:** {layers}\n\n"
        f"The corpus follows the canonical brand layers (01-foundation … 08-evaluation). **01-foundation is\n"
        f"load-bearing** — everything else descends from it; don't contradict it. When the brand evolves, record\n"
        f"the change in 08-evaluation rather than silently overwriting a decision.\n"
    )


def emit_plugin(corpus, out, brand, linked, version):
    name = f"{_kebab(brand)}-brand"
    root = os.path.join(out, "plugin", name)
    docs, extras = read_corpus(corpus)
    os.makedirs(os.path.join(root, ".claude-plugin"), exist_ok=True)
    os.makedirs(os.path.join(root, "bin"), exist_ok=True)
    os.makedirs(os.path.join(root, "skills", name), exist_ok=True)
    _copy_mcp(os.path.join(root, "bin", "brand-corpus-mcp.py"))

    if linked:
        corpus_env = "${user_config.corpus_dir}"
    else:
        _write_folder_corpus(os.path.join(root, "corpus"), docs, extras, brand)
        corpus_env = "${CLAUDE_PLUGIN_ROOT}/corpus"

    pj = {
        "name": name,
        "version": version,
        "description": (f"The {brand} brand corpus — foundation, positioning, identity, voice, tokens — "
                        f"with a read-only brand-corpus MCP for retrieval."),
        "keywords": ["brand", _kebab(brand), "brand-corpus", "design"],
    }
    if linked:
        pj["userConfig"] = {"corpus_dir": {
            "type": "directory",
            "description": f"Path to the {brand} brand corpus directory.",
            "sensitive": False}}
    _write_json(os.path.join(root, ".claude-plugin", "plugin.json"), pj)
    _write_json(os.path.join(root, ".mcp.json"), {"mcpServers": {"brand-corpus": {
        "command": "python3",
        "args": ["${CLAUDE_PLUGIN_ROOT}/bin/brand-corpus-mcp.py"],
        "env": {"BRAND_CORPUS_DIR": corpus_env}}}})
    open(os.path.join(root, "skills", name, "SKILL.md"), "w", encoding="utf-8").write(_thin_skill(
        brand, docs,
        "Query the bundled `brand-corpus` MCP (`list_brand_documents` / `search_brand` / "
        "`fetch_brand_section` / `outline_brand_document` / `get_brand_tokens`) to read the documents."))
    return root, len(docs)


def emit_skill(corpus, out, brand):
    name = f"{_kebab(brand)}-brand"
    root = os.path.join(out, "skill", name)
    docs, extras = read_corpus(corpus)
    os.makedirs(os.path.join(root, "references"), exist_ok=True)
    _write_folder_corpus(os.path.join(root, "references"), docs, extras, brand)   # corpus bundled INSIDE the skill
    open(os.path.join(root, "SKILL.md"), "w", encoding="utf-8").write(_thin_skill(
        brand, docs,
        "The brand's documents are bundled in this skill's `references/` (one folder per layer; start from "
        "`references/INDEX.md`) — read them directly, by layer. (The cloud form ships no MCP or scripts; the "
        "corpus travels with the skill.)"))
    return root, len(docs)


def emit_mcp(corpus, out, brand, linked):
    name = f"{_kebab(brand)}-brand-mcp"
    root = os.path.join(out, "mcp", name)
    docs, extras = read_corpus(corpus)
    os.makedirs(root, exist_ok=True)
    _copy_mcp(os.path.join(root, "brand-corpus-mcp.py"))
    if linked:
        corpus_env, corpus_note = "/path/to/<corpus>", "Point `BRAND_CORPUS_DIR` at your **live** corpus directory:"
    else:
        _write_folder_corpus(os.path.join(root, "corpus"), docs, extras, brand)
        corpus_env, corpus_note = "$(pwd)/corpus", "A **snapshot** of the corpus is bundled in `corpus/`:"
    readme = f"""# {brand} — brand-corpus MCP (standalone)

A read-only **stdio** MCP over the {brand} brand corpus, exposing five task-level tools:
`list_brand_documents`, `search_brand`, `fetch_brand_section`, `outline_brand_document`, `get_brand_tokens`.

## Wire it locally (Claude Code / Cowork / any stdio host)

{corpus_note}

```bash
claude mcp add {name} -s user -e BRAND_CORPUS_DIR="{corpus_env}" -- python3 "$(pwd)/brand-corpus-mcp.py"
```

Canonical env var is `BRAND_CORPUS_DIR` (alias `BRAND_CORPUS_ROOT`).

## Cloud connector (Claude chat)

This is a **stdio** server; Claude chat needs a **remote (HTTP/SSE)** MCP connector. A cloud deployment means
hosting an HTTP transport in front of these same five tools and adding it as a connector — the tool contract is
identical, only the transport differs.
"""
    open(os.path.join(root, "README.md"), "w", encoding="utf-8").write(readme)
    return root, len(docs)


# --- verification (the S9/S10 gate: a stamped artifact is structurally valid, per form) -----------------

def _frontmatter_keys(path):
    """Top-level keys in a doc's YAML frontmatter (no yaml dep)."""
    try:
        head = open(path, encoding="utf-8", errors="replace").read(4000)
    except OSError:
        return set()
    if not head.startswith("---"):
        return set()
    end = head.find("\n---", 3)
    fm = head[3:end] if end != -1 else ""
    return set(re.findall(r'^\s*([A-Za-z_]+):', fm, re.M))


def verify(root, form):
    """Assert a stamped artifact has the structure its form requires; return a list of problems ([] = ok).
    Mechanizes 'the stamp produced a valid artifact' for ALL THREE forms — the plugin form is additionally
    deep-validated by plugins-factory's validate_plugin in CI; here we cover the skill + mcp forms it can't,
    and assert the bundled MCP copy has not drifted from the canonical server."""
    import filecmp
    p = []
    if not os.path.isdir(root):
        return [f"not a directory: {root}"]

    def has(rel):
        return os.path.exists(os.path.join(root, rel))

    def need(rel, why):
        if not has(rel):
            p.append(f"missing {rel} ({why})")

    def good_json(rel):
        try:
            return json.load(open(os.path.join(root, rel), encoding="utf-8"))
        except (OSError, ValueError) as e:
            p.append(f"{rel} is not valid JSON: {e}")
            return None

    if form == "plugin":
        need(".claude-plugin/plugin.json", "plugin manifest")
        if has(".claude-plugin/plugin.json"):
            pj = good_json(".claude-plugin/plugin.json")
            for k in ("name", "version", "description"):
                if pj is not None and not pj.get(k):
                    p.append(f"plugin.json missing '{k}'")
        need(".mcp.json", "MCP wiring")
        if has(".mcp.json"):
            good_json(".mcp.json")
        need("bin/brand-corpus-mcp.py", "bundled MCP server")
        sk = os.path.join(root, "skills")
        found = [os.path.join("skills", d, "SKILL.md") for d in (sorted(os.listdir(sk)) if os.path.isdir(sk) else [])
                 if os.path.isfile(os.path.join(sk, d, "SKILL.md"))]
        if not found:
            p.append("missing skills/<name>/SKILL.md")
        elif "name" not in _frontmatter_keys(os.path.join(root, found[0])):
            p.append(f"{found[0]} has no `name` frontmatter")
    elif form == "skill":
        need("SKILL.md", "cloud skill entry")
        if has("SKILL.md"):
            keys = _frontmatter_keys(os.path.join(root, "SKILL.md"))
            for k in ("name", "description"):
                if k not in keys:
                    p.append(f"SKILL.md has no `{k}` frontmatter")
        need("references", "bundled corpus")
        if os.path.isdir(os.path.join(root, "references")) and not os.listdir(os.path.join(root, "references")):
            p.append("references/ is empty (no corpus bundled)")
        for leak in (".mcp.json", "bin"):  # the cloud form must ship NO MCP/scripts
            if has(leak):
                p.append(f"cloud skill form must ship no MCP/scripts, found {leak}")
    elif form == "mcp":
        need("brand-corpus-mcp.py", "standalone server")
        need("README.md", "wiring recipe")
        if has("README.md") and "claude mcp add" not in open(os.path.join(root, "README.md"), encoding="utf-8", errors="replace").read():
            p.append("README.md has no `claude mcp add` wiring recipe")
    else:
        return [f"unknown form: {form}"]

    if form in ("plugin", "mcp"):  # the bundled server must match the canonical one (no silent drift)
        shipped = "bin/brand-corpus-mcp.py" if form == "plugin" else "brand-corpus-mcp.py"
        if has(shipped) and not filecmp.cmp(os.path.join(root, shipped), _ref_mcp(), shallow=False):
            p.append("the bundled brand-corpus-mcp.py has drifted from the canonical server")
    return p


def selftest():
    """Stamp the stamp-smoke corpus in all three forms, verify each is clean, and confirm verify catches a
    representative defect per form (an MCP leak in the cloud form, a broken plugin.json, a drifted MCP copy)."""
    import shutil
    import tempfile
    fails = []

    def expect(c, m):
        if not c:
            fails.append(m)

    here = os.path.dirname(os.path.abspath(__file__))
    corpus = os.path.normpath(os.path.join(here, "..", "evals", "stamp-smoke", "corpus"))
    d = tempfile.mkdtemp(prefix="brand-stamp-selftest-")
    try:
        pr, _ = emit_plugin(corpus, d, "smoke", False, "0.1.0")
        expect(verify(pr, "plugin") == [], f"a freshly stamped plugin failed verify: {verify(pr, 'plugin')}")
        sr, _ = emit_skill(corpus, d, "smoke")
        expect(verify(sr, "skill") == [], f"a freshly stamped skill failed verify: {verify(sr, 'skill')}")
        mr, _ = emit_mcp(corpus, d, "smoke", False)
        expect(verify(mr, "mcp") == [], f"a freshly stamped mcp failed verify: {verify(mr, 'mcp')}")
        os.makedirs(os.path.join(sr, "bin"))  # the cloud form must stay pure
        expect(any("ship no MCP" in x for x in verify(sr, "skill")), "verify missed an MCP/script leak in the cloud skill form")
        open(os.path.join(pr, ".claude-plugin", "plugin.json"), "w").write("{ not json")
        expect(any("not valid JSON" in x for x in verify(pr, "plugin")), "verify missed a broken plugin.json")
        open(os.path.join(mr, "brand-corpus-mcp.py"), "a").write("\n# tampered\n")
        expect(any("drifted" in x for x in verify(mr, "mcp")), "verify missed a drifted bundled MCP server")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    if fails:
        sys.stderr.write("brand-stamp selftest: FAIL\n")
        for m in fails:
            sys.stderr.write(f"  - {m}\n")
        return 1
    print("brand-stamp selftest: OK (all three forms stamp + verify clean; an MCP leak in the cloud form, a "
          "broken plugin.json, and a drifted bundled MCP are each caught)")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(prog="brand-stamp", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for form in ("plugin", "skill", "mcp"):
        p = sub.add_parser(form)
        p.add_argument("corpus")
        p.add_argument("--name", required=True)
        p.add_argument("-o", "--out", required=True)
        if form in ("plugin", "mcp"):
            p.add_argument("--linked", action="store_true",
                           help="point the MCP at a live corpus_dir instead of bundling a snapshot")
        if form == "plugin":
            p.add_argument("--version", default="0.1.0",
                           help="plugin.json version — bump on each re-stamp (baking a corpus is a release)")
    sub.add_parser("selftest")
    pv = sub.add_parser("verify")
    pv.add_argument("root", help="a stamped artifact's root dir (e.g. <out>/plugin/<brand>-brand)")
    pv.add_argument("--form", required=True, choices=("plugin", "skill", "mcp"))
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "verify":
        probs = verify(args.root, args.form)
        if probs:
            sys.stderr.write(f"brand-stamp verify ({args.form}): FAIL — {args.root}\n")
            for x in probs:
                sys.stderr.write(f"  - {x}\n")
            return 1
        print(f"brand-stamp verify ({args.form}): OK — {args.root}")
        return 0
    if args.cmd == "plugin":
        root, n = emit_plugin(args.corpus, args.out, args.name, args.linked, args.version)
        print(f"brand-stamp: plugin → {root} (v{args.version}, {n} doc(s), "
              f"{'linked' if args.linked else 'bundled'} corpus)")
        print(f"  → validate:  python3 <plugins-factory>/bin/validate_plugin.py plugin {root}")
    elif args.cmd == "skill":
        root, n = emit_skill(args.corpus, args.out, args.name)
        print(f"brand-stamp: skill → {root} ({n} doc(s) bundled in references/, + INDEX.md)")
        print("  → upload the skill folder to Claude chat (it carries its own corpus; no MCP/scripts).")
    else:
        root, n = emit_mcp(args.corpus, args.out, args.name, args.linked)
        print(f"brand-stamp: mcp → {root} ({n} doc(s), {'linked' if args.linked else 'bundled'} corpus) — see README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
