#!/usr/bin/env python3
"""gen-index.py — generate ./index.html documenting the plugins-forge catalog.

Reads .claude-plugin/marketplace.json and walks each plugin's real structure (skills, agents,
commands, hooks, bin gates, MCP, reference files) and emits one self-contained, dependency-free
index.html (inline CSS, no JS, no external assets). Re-run after changing any plugin to refresh.

Usage:  python3 gen-index.py            # writes ./index.html
        python3 gen-index.py --check    # exit 1 if index.html is missing or stale vs. a fresh render
Stdlib only (Python 3.8+).
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


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
        "<title>plugins-forge — catalog</title>",
        f"<style>{css}</style></head><body><div class='wrap'>",
        "<header><h1>plugins-forge</h1>",
        f"<p class='sub'>{e(market_desc)}</p>",
        f"<p class='sub'><b>{len(plugins)}</b> catalog plugins · "
        "<a href='https://github.com/kimgranlund/claude-plugins'>github.com/kimgranlund/claude-plugins</a></p></header>",
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


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
