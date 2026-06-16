#!/usr/bin/env python3
"""gen-index.py — generate ./index.html documenting the nonoun-plugins catalog.

Reads .claude-plugin/marketplace.json and walks each plugin's real structure (skills, agents,
commands, hooks, bin gates, MCP, reference files) and emits one self-contained, dependency-free
index.html (inline CSS, no JS, no external assets). Re-run after changing any plugin to refresh.

Usage:  python3 gen-index.py            # writes ./index.html
        python3 gen-index.py --check    # exit 1 if index.html is missing or stale vs. a fresh render
        python3 gen-index.py selftest   # unit-prove the tracked-only walk (R-1 regression guard) + --check staleness
Stdlib only (Python 3.8+).
"""
import html
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def _tracked():
    """Git-tracked paths (relative, '/'-separated) — the shipped catalog. None when git is unavailable."""
    try:
        out = subprocess.run(["git", "-C", ROOT, "ls-files", "-z"],
                             capture_output=True, check=True)
        return set(out.stdout.decode("utf-8", "replace").split("\0")) - {""}
    except (OSError, subprocess.CalledProcessError):
        return None


TRACKED = _tracked()


def _shipped(path):
    """True if `path` is part of the shipped catalog.

    The index documents what a fresh checkout contains, so only git-tracked content
    counts — gitignored local files (example corpora, generated sitemaps, the
    git-ignored critic name-maps) must not skew the render, or `--check` diverges
    between a working tree and CI. Without git (tarball), fall back to skipping
    dotfiles — which covers the known ignored-file classes.
    """
    if TRACKED is None:
        return not os.path.basename(path).startswith(".")
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    if rel in TRACKED:
        return True
    prefix = rel + "/"
    return any(t.startswith(prefix) for t in TRACKED)  # directories: shipped iff they contain tracked files


def _frontmatter(path):
    """Best-effort parse of a markdown file's YAML frontmatter -> {name, description}."""
    try:
        t = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return {}
    if not t.startswith("---"):
        return {}
    end = t.find("\n---", 3)
    fm = t[3:end] if end != -1 else ""
    out = {}
    m = re.search(r"(?m)^name:\s*(.+?)\s*$", fm)
    if m:
        out["name"] = m.group(1).strip().strip("\"'")
    m = re.search(r"(?m)^description:\s*(.*)$", fm)
    if m:
        first = m.group(1).strip()
        if first in (">", ">-", "|", "|-", ""):  # folded/block scalar — collect indented lines
            buf = []
            for ln in fm[m.end():].split("\n"):
                if ln.strip() == "":
                    continue
                if re.match(r"^\s+\S", ln):
                    buf.append(ln.strip())
                else:
                    break
            out["description"] = " ".join(buf).strip()
        else:
            out["description"] = first.strip("\"'")
    return out


def _first_sentences(text, limit=240):
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    dot = cut.rfind(". ")
    return (cut[:dot + 1] if dot > 80 else cut.rstrip() + "…")


def _ls(path, suffix=None):
    if not os.path.isdir(path):
        return []
    out = []
    for fn in sorted(os.listdir(path)):
        if suffix and not fn.endswith(suffix):
            continue
        if not _shipped(os.path.join(path, fn)):
            continue
        out.append(fn)
    return out


def collect(plugin_dir):
    p = os.path.join(ROOT, plugin_dir)
    data = {"skills": [], "critics": [], "orchestrators": [], "commands": [],
            "hooks": [], "bins": [], "mcp": [], "ref_count": 0, "version": None, "keywords": []}
    pj = os.path.join(p, ".claude-plugin", "plugin.json")
    if os.path.isfile(pj):
        try:
            j = json.load(open(pj, encoding="utf-8"))
            data["version"] = j.get("version")
            data["keywords"] = j.get("keywords", [])
        except (OSError, ValueError):
            pass
    # skills
    sk = os.path.join(p, "skills")
    for d in _ls(sk):
        sm = os.path.join(sk, d, "SKILL.md")
        if os.path.isfile(sm):
            fm = _frontmatter(sm)
            data["skills"].append((fm.get("name", d), _first_sentences(fm.get("description", ""))))
        data["ref_count"] += sum(len(_ls(dp, ".md")) for dp, _, _ in os.walk(os.path.join(sk, d, "references")))
    # agents
    for fn in _ls(os.path.join(p, "agents"), ".md"):
        name = fn[:-3]
        if name.startswith("critic-"):
            data["critics"].append(name)
        else:
            data["orchestrators"].append(name)
    # commands
    for fn in _ls(os.path.join(p, "commands"), ".md"):
        fm = _frontmatter(os.path.join(p, "commands", fn))
        data["commands"].append(("/" + fn[:-3], _first_sentences(fm.get("description", ""), 140)))
    # hooks
    hj = os.path.join(p, "hooks", "hooks.json")
    if os.path.isfile(hj):
        try:
            hooks = json.load(open(hj, encoding="utf-8")).get("hooks", {})
            for event, entries in hooks.items():
                for e in entries:
                    cmds = [h.get("command", "") for h in e.get("hooks", [])]
                    cmd = os.path.basename(cmds[0].split('"')[-2]) if cmds and '"' in cmds[0] else (cmds[0] if cmds else "")
                    data["hooks"].append(f"{event} ({e.get('matcher', '*')}) → {cmd}")
        except (OSError, ValueError):
            pass
    # bin
    for fn in _ls(os.path.join(p, "bin")):
        if not fn.startswith("."):
            data["bins"].append(fn)
    # mcp
    mj = os.path.join(p, ".mcp.json")
    if os.path.isfile(mj):
        try:
            data["mcp"] = list(json.load(open(mj, encoding="utf-8")).get("mcpServers", {}).keys())
        except (OSError, ValueError):
            data["mcp"] = ["(mcp)"]
    return data


def render(market):
    e = html.escape
    plugins = market.get("plugins", [])
    market_desc = market.get("metadata", {}).get("description", "")
    market_name = market.get("name", "catalog")           # read the marketplace name — survives a rename, no code change
    css = """
:root{--bg:#0d1117;--card:#161b22;--bd:#30363d;--fg:#e6edf3;--mut:#9da7b3;--acc:#58a6ff;--chip:#21262d}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1040px;margin:0 auto;padding:32px 20px 64px}
header h1{margin:0 0 6px;font-size:30px;letter-spacing:-.02em}
header .sub{color:var(--mut);margin:0 0 18px}
nav{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 28px}
nav a{background:var(--chip);border:1px solid var(--bd);border-radius:20px;padding:5px 13px;font-size:13px;color:var(--fg)}
nav a:hover{border-color:var(--acc);text-decoration:none}
.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:22px 24px;margin:0 0 22px;scroll-margin-top:16px}
.card h2{margin:0 0 4px;font-size:22px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.ver{font:12px/1 ui-monospace,monospace;color:var(--mut);border:1px solid var(--bd);border-radius:6px;padding:3px 7px}
.cat{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:#3fb950;border:1px solid #2ea04344;background:#2ea04318;border-radius:6px;padding:3px 8px}
.desc{color:var(--fg);margin:6px 0 14px}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 16px}
.chip{background:var(--chip);border:1px solid var(--bd);border-radius:5px;padding:2px 8px;font-size:12px;color:var(--mut)}
.sec{border-top:1px solid var(--bd);padding:13px 0 3px}
.sec h3{margin:0 0 8px;font-size:12px;text-transform:uppercase;letter-spacing:.07em;color:var(--mut)}
.sec h3 .n{color:var(--acc)}
code,.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px}
.skill{margin:0 0 7px}
.skill b{color:var(--fg)}.skill .d{color:var(--mut)}
.list{display:flex;flex-wrap:wrap;gap:6px}
.list .it{background:var(--chip);border:1px solid var(--bd);border-radius:5px;padding:2px 8px;font-size:12.5px}
.cmd{margin:0 0 5px}.cmd code{color:var(--acc)}.cmd .d{color:var(--mut)}
.muted{color:var(--mut)}
footer{color:var(--mut);font-size:13px;border-top:1px solid var(--bd);margin-top:28px;padding-top:16px}
"""
    parts = [
        "<!doctype html>", '<html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f"<title>{e(market_name)} — catalog</title>",
        f"<style>{css}</style></head><body><div class='wrap'>",
        f"<header><h1>{e(market_name)}</h1>",
        f"<p class='sub'>{e(market_desc)}</p>",
        f"<p class='sub'><b>{len(plugins)}</b> catalog plugins · "
        "<a href='https://github.com/kimgranlund/nonoun-plugins'>github.com/kimgranlund/nonoun-plugins</a></p></header>",
        "<nav>" + "".join(f"<a href='#{e(p['name'])}'>{e(p['name'])}</a>" for p in plugins) + "</nav>",
    ]
    for p in plugins:
        d = collect(p["name"])
        parts.append(f"<section class='card' id='{e(p['name'])}'>")
        ver = f"<span class='ver'>v{e(d['version'])}</span>" if d["version"] else ""
        cat = f"<span class='cat'>{e(p.get('category', ''))}</span>" if p.get("category") else ""
        parts.append(f"<h2><code>{e(p['name'])}</code> {ver} {cat}</h2>")
        parts.append(f"<p class='desc'>{e(p.get('description', ''))}</p>")
        tags = p.get("tags") or d["keywords"]
        if tags:
            parts.append("<div class='chips'>" + "".join(f"<span class='chip'>{e(t)}</span>" for t in tags) + "</div>")
        # Skills
        if d["skills"]:
            parts.append(f"<div class='sec'><h3>Skills <span class='n'>{len(d['skills'])}</span></h3>")
            for nm, ds in d["skills"]:
                parts.append(f"<div class='skill'><b><code>{e(nm)}</code></b> <span class='d'>— {e(ds)}</span></div>")
            parts.append("</div>")
        # Agents
        if d["critics"] or d["orchestrators"]:
            n = len(d["critics"]) + len(d["orchestrators"])
            parts.append(f"<div class='sec'><h3>Agents <span class='n'>{n}</span></h3>")
            if d["orchestrators"]:
                parts.append("<div class='list' style='margin-bottom:7px'>" +
                             "".join(f"<span class='it'><code>{e(o)}</code></span>" for o in d["orchestrators"]) + "</div>")
            if d["critics"]:
                parts.append(f"<div class='muted' style='font-size:12.5px;margin-bottom:5px'>{len(d['critics'])} critics</div>")
                parts.append("<div class='list'>" +
                             "".join(f"<span class='it'>{e(c)}</span>" for c in d["critics"]) + "</div>")
            parts.append("</div>")
        # Commands
        if d["commands"]:
            parts.append(f"<div class='sec'><h3>Commands <span class='n'>{len(d['commands'])}</span></h3>")
            for nm, ds in d["commands"]:
                parts.append(f"<div class='cmd'><code>{e(nm)}</code> <span class='d'>— {e(ds)}</span></div>")
            parts.append("</div>")
        # Resources
        res = []
        if d["hooks"]:
            res.append("<b>Hook:</b> " + "; ".join(f"<code>{e(h)}</code>" for h in d["hooks"]))
        if d["bins"]:
            res.append("<b>Gates / bin:</b> " + " · ".join(f"<code>{e(b)}</code>" for b in d["bins"]))
        res.append("<b>MCP:</b> " + (", ".join(f"<code>{e(m)}</code>" for m in d["mcp"]) if d["mcp"] else "<span class='muted'>none (or planned)</span>"))
        if d["ref_count"]:
            res.append(f"<b>Reference files:</b> {d['ref_count']}")
        parts.append("<div class='sec'><h3>Resources</h3>" +
                     "".join(f"<div style='margin-bottom:4px'>{r}</div>" for r in res) + "</div>")
        parts.append("</section>")
    parts.append("<footer>Generated from <code>.claude-plugin/marketplace.json</code> + each plugin's "
                 "structure by <code>gen-index.py</code> — re-run to refresh. "
                 "Each plugin is self-contained and red-teamed with <code>plugins-factory</code>.</footer>")
    parts.append("</div></body></html>")
    return "\n".join(parts) + "\n"


def main(argv):
    market = json.load(open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8"))
    out = render(market)
    target = os.path.join(ROOT, "index.html")
    if "--check" in argv:
        cur = open(target, encoding="utf-8").read() if os.path.isfile(target) else ""
        if cur != out:
            print("index.html is missing or stale — run: python3 gen-index.py", file=sys.stderr)
            return 1
        print("index.html: up to date")
        return 0
    open(target, "w", encoding="utf-8").write(out)
    print(f"wrote index.html ({len(market.get('plugins', []))} plugins, {len(out)} bytes)")
    return 0


def selftest():
    """Unit-prove the load-bearing behavior, anchored on R-1 (the 5-day outage, ISSUES.md R-1):
    gen-index walked untracked files and leaked the gitignored `.name-map.md` into the committed
    index.html as 4 phantom "orchestrators". This asserts the tracked-only walk (`_shipped`) excludes
    untracked content — at the unit level AND through `collect()` (the actual leak path) — plus the
    `--check` staleness contract and render determinism. No real catalog needed. Exit 0 = pass, 1 = fail.
    """
    import tempfile
    import shutil
    global ROOT, TRACKED
    saved_root, saved_tracked = ROOT, TRACKED
    fails = []
    def check(cond, label):
        if not cond:
            fails.append(label)
    tmp = tempfile.mkdtemp(prefix="gen-index-selftest-")
    try:
        def w(rel, content):
            full = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            open(full, "w", encoding="utf-8").write(content)
        # a minimal fixture catalog: one plugin with a TRACKED critic + an UNTRACKED .name-map (the R-1 leak file)
        w(".claude-plugin/marketplace.json", json.dumps({
            "metadata": {"description": "fixture"},
            "plugins": [{"name": "demo-plugin", "description": "a demo", "category": "x", "tags": ["t"]}]}))
        w("demo-plugin/.claude-plugin/plugin.json", json.dumps({"version": "9.9.9", "keywords": ["k"]}))
        w("demo-plugin/agents/critic-foo.md", "---\nname: critic-foo\ndescription: a critic.\n---\n")
        w("demo-plugin/agents/.name-map.md", "---\nname: SECRET\n---\nreal names here\n")  # gitignored, untracked
        w("demo-plugin/skills/demo/SKILL.md", "---\nname: demo\ndescription: a skill.\n---\n")

        ROOT = tmp
        # TRACKED = what `git ls-files` would return — everything EXCEPT the untracked .name-map
        TRACKED = {".claude-plugin/marketplace.json", "demo-plugin/.claude-plugin/plugin.json",
                   "demo-plugin/agents/critic-foo.md", "demo-plugin/skills/demo/SKILL.md"}

        # --- R-1 unit: the tracked-only guard ---
        check(_shipped(os.path.join(tmp, "demo-plugin/agents/critic-foo.md")) is True, "tracked file rejected by _shipped")
        check(_shipped(os.path.join(tmp, "demo-plugin/agents/.name-map.md")) is False, "R-1: untracked .name-map counted as shipped")
        check(_shipped(os.path.join(tmp, "demo-plugin/agents")) is True, "dir with tracked children rejected")
        # --- R-1 leak path: collect() must NOT surface the untracked .name-map as an orchestrator ---
        d = collect("demo-plugin")
        check("critic-foo" in d["critics"], "tracked critic not collected")
        check(not any("name-map" in o for o in d["orchestrators"]), "R-1 REGRESSION: untracked .name-map leaked as an orchestrator")
        check(d["version"] == "9.9.9" and [s[0] for s in d["skills"]] == ["demo"], "collect() basics wrong")
        # --- determinism ---
        market = json.load(open(os.path.join(tmp, ".claude-plugin", "marketplace.json"), encoding="utf-8"))
        check(render(market) == render(market), "render is not idempotent")
        # --- --check staleness contract ---
        open(os.path.join(tmp, "index.html"), "w", encoding="utf-8").write("STALE")
        check(main(["--check"]) == 1, "--check did not reject a stale index.html")
        open(os.path.join(tmp, "index.html"), "w", encoding="utf-8").write(render(market))
        check(main(["--check"]) == 0, "--check rejected a freshly-rendered index.html")
        # --- tarball fallback (no git): TRACKED is None → dotfiles skipped, so .name-map still excluded ---
        TRACKED = None
        check(_shipped(os.path.join(tmp, "demo-plugin/agents/critic-foo.md")) is True
              and _shipped(os.path.join(tmp, "demo-plugin/agents/.name-map.md")) is False,
              "tarball fallback: dotfile leak not prevented")
    finally:
        ROOT, TRACKED = saved_root, saved_tracked
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        sys.stderr.write("gen-index selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("gen-index selftest: OK (tracked-only walk / R-1 guard, --check staleness, determinism)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    sys.exit(main(sys.argv[1:]))
