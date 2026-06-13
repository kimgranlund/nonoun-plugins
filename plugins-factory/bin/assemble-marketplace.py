#!/usr/bin/env python3
"""assemble-marketplace.py — assemble + validate a `.claude-plugin/marketplace.json` for a carved library.

The **publish** step of the carve workflow (`carve-method.md` step 4 → publish; plugins-factory ROADMAP).
A carve turns one library into N plugins, some depending on others (a *foundation plugin* others
`dependencies`-declare). This assembles the multi-plugin `marketplace.json` from the plugins on disk and
validates the wiring a carve must get right:

  - every plugin's manifest is legal (delegates to `validate_plugin.validate_plugin_manifest`);
  - the assembled marketplace is legal (`validate_plugin.validate_marketplace_manifest` + the cross-plugin
    agent-collision check — so a carved library can't ship two councils that silently drop a critic, D-13);
  - every `dependencies` edge RESOLVES — to a plugin in the library, or a marketplace named in
    `allowCrossMarketplaceDependenciesOn`;
  - the dependency graph is ACYCLIC and foundation plugins are sinks (carve-quality D4).

It does NOT publish anywhere — it produces + validates the manifest; pushing the repo is yours (the D8
"example-only" gap is the missing *assembler*, not a deploy step). A plugin entry's `tags` come from each
plugin.json's `keywords`; `category` from a `category` field if present, else `"general"` (curate the
assembled file). `source` is `./<dir-relative-to-library>`.

Usage:
  assemble-marketplace.py assemble <library-dir> --name <kebab> --owner <name> [--owner-email <e>]
                          [--metadata-description <text>] [--allow-external <marketplace> ...] [--out <path>]
  assemble-marketplace.py selftest

Exit 0 = assembled + valid (written to --out or stdout); 1 = invalid (bad manifest / unresolved or cyclic
dependency); 2 = usage error. Stdlib only; Python 3.8+.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate_plugin as _vp  # co-located; reuse its manifest + collision validators (DRY, intra-plugin)


def _load(plugin_dir):
    cand = os.path.join(plugin_dir, ".claude-plugin", "plugin.json")
    if not os.path.isfile(cand):
        return None
    try:
        return json.load(open(cand, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def discover(library_dir):
    """Every immediate subdirectory of library_dir that carries a .claude-plugin/plugin.json."""
    out = []
    for entry in sorted(os.listdir(library_dir)):
        pdir = os.path.join(library_dir, entry)
        if not os.path.isdir(pdir):
            continue
        data = _load(pdir)
        if data is not None:
            out.append((entry, pdir, data))
    return out


def _dep_names(plugin_json):
    """Names a plugin depends on. `dependencies` is a list of {name, version} (carve-method step 4)."""
    deps = plugin_json.get("dependencies", [])
    names = []
    if isinstance(deps, list):
        for d in deps:
            if isinstance(d, dict) and isinstance(d.get("name"), str):
                names.append(d["name"])
            elif isinstance(d, str):
                names.append(d)
    return names


def check_dependencies(found, allow_external):
    """Resolve + acyclicity over the library's `dependencies` graph. Returns a list of error strings."""
    errors = []
    in_library = {data.get("name") or slug for slug, _, data in found}
    graph = {}
    for slug, _, data in found:
        name = data.get("name") or slug
        deps = _dep_names(data)
        graph[name] = deps
        for dep in deps:
            if dep not in in_library and dep not in allow_external:
                errors.append(f"plugin `{name}` declares dependency `{dep}` that is neither in the library "
                              f"nor in allowCrossMarketplaceDependenciesOn {sorted(allow_external)} — it would "
                              f"break on install (carve-method: declare it, co-locate it, or allow its marketplace)")
    # cycle detection (DFS with a recursion stack); foundation plugins must be sinks
    WHITE, GREY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}

    def visit(n, stack):
        color[n] = GREY
        for m in graph.get(n, []):
            if m not in graph:
                continue  # external/unresolved already reported
            if color[m] == GREY:
                cyc = " → ".join(stack[stack.index(m):] + [m]) if m in stack else f"{n} → {m}"
                errors.append(f"dependency cycle: {cyc} — the graph must be acyclic (foundation plugins are sinks, carve-quality D4)")
                return
            if color[m] == WHITE:
                visit(m, stack + [m])
        color[n] = BLACK

    for n in graph:
        if color[n] == WHITE:
            visit(n, [n])
    return errors


def assemble(library_dir, name, owner, owner_email=None, metadata_description=None, allow_external=None):
    """Return (marketplace dict, errors). errors empty == valid + ready to write."""
    allow_external = set(allow_external or [])
    errors = []
    found = discover(library_dir)
    if not found:
        return None, [f"no plugins found under {library_dir} (each needs a .claude-plugin/plugin.json)"]

    plugins = []
    for slug, pdir, data in found:
        perrs, _ = _vp.validate_plugin_manifest(data, pdir)
        for e in perrs:
            errors.append(f"{slug}: {e}")
        entry = {
            "name": data.get("name") or slug,
            "source": f"./{slug}",
            "description": data.get("description", "").strip(),
            "category": data.get("category", "general"),
            "tags": data.get("keywords", []) if isinstance(data.get("keywords"), list) else [],
        }
        plugins.append(entry)

    market = {"name": name, "owner": {"name": owner}, "plugins": plugins}
    if owner_email:
        market["owner"]["email"] = owner_email
    if metadata_description:
        market["metadata"] = {"description": metadata_description}
    if allow_external:
        market["allowCrossMarketplaceDependenciesOn"] = sorted(allow_external)

    merrs, _ = _vp.validate_marketplace_manifest(market)
    errors += merrs
    cerr, _ = _vp.check_cross_plugin_agents(market, library_dir)
    errors += cerr  # known reuse is a warning there → not returned as an error; a NEW collision is
    errors += check_dependencies(found, allow_external)
    return market, errors


def cmd_assemble(argv):
    if not argv:
        print("usage: assemble-marketplace.py assemble <library-dir> --name <kebab> --owner <name> [...]", file=sys.stderr)
        return 2

    def flag(name, default=None):
        return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default

    def flag_multi(name):
        vals = []
        i = 0
        while i < len(argv):
            if argv[i] == name and i + 1 < len(argv):
                vals.append(argv[i + 1])
            i += 1
        return vals

    library_dir = argv[0]
    name, owner = flag("--name"), flag("--owner")
    if not os.path.isdir(library_dir) or not name or not owner:
        print("assemble requires <library-dir> --name <kebab> --owner <name>", file=sys.stderr)
        return 2
    market, errors = assemble(library_dir, name, owner, flag("--owner-email"),
                              flag("--metadata-description"), flag_multi("--allow-external"))
    if errors:
        print("RESULT: INVALID — the carved library does not assemble into a legal marketplace:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    text = json.dumps(market, indent=2) + "\n"
    out = flag("--out")
    if out:
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"RESULT: WROTE {out} ({len(market['plugins'])} plugin(s); manifest + dependency graph valid)")
    else:
        sys.stdout.write(text)
        print(f"RESULT: VALID ({len(market['plugins'])} plugin(s); manifest + dependency graph valid)", file=sys.stderr)
    return 0


def cmd_selftest():
    import tempfile
    fails = []

    def expect(cond, msg):
        if not cond:
            fails.append(msg)

    def mk(root, slug, data, agent=None):
        d = os.path.join(root, slug)
        os.makedirs(os.path.join(d, ".claude-plugin"))
        json.dump(data, open(os.path.join(d, ".claude-plugin", "plugin.json"), "w"))
        if agent:
            os.makedirs(os.path.join(d, "agents"))
            open(os.path.join(d, "agents", f"{agent}.md"), "w").write(f"---\nname: {agent}\n---\nbody\n")
        return d

    # a clean 2-plugin library: a domain plugin depending on a foundation plugin (a sink)
    with tempfile.TemporaryDirectory() as tmp:
        mk(tmp, "core-types", {"name": "core-types", "version": "1.0.0", "description": "Shared types.", "keywords": ["types"]})
        mk(tmp, "ui-build", {"name": "ui-build", "version": "0.1.0", "description": "Build UI.",
                             "keywords": ["ui"], "category": "developer-tools",
                             "dependencies": [{"name": "core-types", "version": "~1.0.0"}]})
        market, errors = assemble(tmp, "ui-lib", "Owner")
        expect(errors == [], f"a clean library did not assemble: {errors}")
        expect(market and len(market["plugins"]) == 2, "did not discover both plugins")
        expect(any(p["name"] == "ui-build" and p["tags"] == ["ui"] for p in market["plugins"]), "tags not derived from keywords")
        expect(any(p["category"] == "developer-tools" for p in market["plugins"]), "category not carried from plugin.json")

    # an UNRESOLVED dependency must fail — unless explicitly allowed external, or added to the library
    with tempfile.TemporaryDirectory() as tmp:
        mk(tmp, "ui-build", {"name": "ui-build", "version": "0.1.0", "description": "Build UI.",
                             "dependencies": [{"name": "ghost-types", "version": "~1.0.0"}]})
        _, errors = assemble(tmp, "ui-lib", "Owner")
        expect(any("ghost-types" in e and "neither in the library" in e for e in errors), "unresolved dependency not caught")
        # --allow-external vouches for the name → resolves and is recorded in allowCrossMarketplaceDependenciesOn
        market_a, errors_a = assemble(tmp, "ui-lib", "Owner", allow_external=["ghost-types"])
        expect(not any("ghost-types" in e for e in errors_a), "allow-external did not resolve the external dependency")
        expect(market_a and market_a.get("allowCrossMarketplaceDependenciesOn") == ["ghost-types"], "allow-external not recorded in the manifest")
        # ...or adding the missing plugin to the library resolves it
        mk(tmp, "ghost-types", {"name": "ghost-types", "version": "1.0.0", "description": "Shared types."})
        _, errors_b = assemble(tmp, "ui-lib", "Owner")
        expect(not any("ghost-types" in e for e in errors_b), "adding the missing plugin did not resolve the dependency")

    # a CYCLE must fail
    with tempfile.TemporaryDirectory() as tmp:
        mk(tmp, "a", {"name": "a", "version": "1.0.0", "description": "A.", "dependencies": [{"name": "b", "version": "~1.0.0"}]})
        mk(tmp, "b", {"name": "b", "version": "1.0.0", "description": "B.", "dependencies": [{"name": "a", "version": "~1.0.0"}]})
        _, errors = assemble(tmp, "cyc", "Owner")
        expect(any("cycle" in e for e in errors), "dependency cycle not caught")

    # a NEW cross-plugin agent collision must fail (D-13 wiring carried into publish)
    with tempfile.TemporaryDirectory() as tmp:
        mk(tmp, "p1", {"name": "p1", "version": "1.0.0", "description": "P1."}, agent="critic-zz-new")
        mk(tmp, "p2", {"name": "p2", "version": "1.0.0", "description": "P2."}, agent="critic-zz-new")
        _, errors = assemble(tmp, "lib", "Owner")
        expect(any("collides across" in e for e in errors), "a new cross-plugin agent collision not caught at publish")

    if fails:
        sys.stderr.write("assemble-marketplace selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("assemble-marketplace selftest: OK (assembles a clean 2-plugin library w/ a foundation dependency; "
          "catches an unresolved dep, a cycle, and a new cross-plugin agent collision; derives tags/category)")
    return 0


def main(argv):
    if len(argv) == 1 and argv[0] == "selftest":
        return cmd_selftest()
    if argv and argv[0] == "assemble":
        return cmd_assemble(argv[1:])
    print(__doc__.split("Usage:")[1].split("Exit 0")[0].strip() if "Usage:" in __doc__ else "usage error", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
