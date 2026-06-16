#!/usr/bin/env python3
"""coldstart.py — the privileged planner: a brief becomes a spec + a hydrated lattice + build tickets.

    python3 debug/bin/coldstart.py <name> [--mock] [--model opus]

This realises "prompt = triaged": it reads the scaffolded PROMPT ticket (the brief), produces a PLAN (the spec
asset + the lattice cells + the build tickets), and APPLIES it through the single-writer ops layer (api.seed_cell
/ create_ticket). It runs as a PRIVILEGED operator process — NOT a gate-wired cell-worker — because seeding
lattice.json + tickets is denied to gate-wired workers; the privilege split is the design, not a hole. It must
run BEFORE the dev-server boots (so it is the single writer); ralph.py sequences it that way.

  --mock : use a deterministic CANNED plan (no model) — the CI plumbing proof. Default when DEBUG_RALPH_LIVE
           is unset and `claude` is absent.
  live   : run a `claude -p` planner that emits the plan as JSON, then apply it (spends tokens).

Stdlib only; Python 3.8+.
"""
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C   # noqa: E402

SLUG = "app"          # the system-scope slug the plan builds under (spec.system.app, capability.system.app)
ACTOR = {"kind": "agent", "id": "cold-start-planner"}

# The MILESTONE rubrics the planner authors/seeds (dynamic rubric generation — "make as many as we need").
# PRD = the product from the OUTSIDE-IN (jobs · UX · user-facing acceptance); SPEC = the architecture from the
# INSIDE-OUT (modules · contracts · decomposition) that realizes it.
R_PRD, R_SPEC, R_CAP, R_SHIP = ("rubric.system.prd-quality", "rubric.system.spec-quality",
                                "rubric.system.test-suite", "rubric.system.ship")


def _mock_cap_verify():
    """A per-cell CRITIC harness (mock) — authored by the planner, gate-denied to the worker. It imports the
    worker's code and gates on it; a live planner authors real checkable predicates + a pristine reference."""
    return ("// per-cell critic harness (mock). The planner authors this; the worker is gate-denied from writing it.\n"
            "import { ready } from './index.mjs';\n"
            "if (ready !== true) { console.error('FAIL: index.mjs must export ready=true'); process.exit(1); }\n"
            "console.log('pass'); process.exit(0);\n")


def _mock_ship_verify(features):
    """The SHIP gate (mock): the app integrator composes EVERY capability. A live planner also runs the build +
    the acceptance criteria + (with DEV_FACTORY_BROWSER_SMOKE=1) a real-browser smoke."""
    imports = "\n".join(f"import {{ ready as r_{f} }} from '../{f}/index.mjs';" for f in features)
    checks = " && ".join(f"r_{f} === true" for f in features) or "true"
    return ("// SHIP gate (mock) — the app integrator composes every capability. The planner authors it.\n"
            + imports + "\n"
            + f"if (!({checks})) {{ console.error('FAIL: not every capability composed'); process.exit(1); }}\n"
            "console.log('pass: all capabilities composed'); process.exit(0);\n")


def _slugify(s):
    return re.sub(r"[^a-z0-9-]", "-", str(s).lower()).strip("-") or "feature"


def _gen_cap_verify(exports, acceptance=None):
    """A REAL critic harness from the planner's contract: the worker's code must (1) export the declared API,
    (2) load without throwing, and (3) pass the planner's BEHAVIORAL acceptance — executable boolean expressions
    over the exports that EXERCISE the logic ("createDeck().length === 52"), not just check its shape. The worker
    reads this gate but cannot write it, and cannot forge the pass (validate.py mints the signal from the exit
    status). Representative, not exhaustive: passing them should imply general correctness; a stub can't."""
    req = ", ".join(json.dumps(e) for e in exports)
    accept = [a for a in (acceptance or []) if isinstance(a, str) and a.strip()]
    acc_arr = ", ".join(json.dumps(a) for a in accept)
    return (
        "// per-cell critic harness (live) — API surface + BEHAVIORAL acceptance. The planner declares the\n"
        "// contract; the worker authors code that satisfies it and is gate-denied from writing this file.\n"
        "import * as m from './index.mjs';\n"
        f"const required = [{req}];\n"
        "const missing = required.filter((e) => !(e in m));\n"
        "if (missing.length) { console.error('FAIL: index.mjs missing exports: ' + missing.join(', ')); process.exit(1); }\n"
        "const notDefined = required.filter((e) => typeof m[e] === 'undefined');\n"
        "if (notDefined.length) { console.error('FAIL: undefined exports: ' + notDefined.join(', ')); process.exit(1); }\n"
        f"const ACCEPT = [{acc_arr}];\n"
        "const names = Object.keys(m);\n"
        "const failed = [];\n"
        "for (const a of ACCEPT) {\n"
        "  try {\n"
        "    const fn = new Function(...names, 'return (' + a + ');');\n"
        "    if (!fn(...names.map((n) => m[n]))) failed.push(a);\n"
        "  } catch (e) { failed.push(a + '  (threw: ' + (e && e.message) + ')'); }\n"
        "}\n"
        "if (failed.length) { console.error('FAIL: behavioral acceptance not met:\\n  ' + failed.join('\\n  ')); process.exit(1); }\n"
        "console.log('pass: API surface (' + required.length + ') + ' + ACCEPT.length + ' behavioral assertion(s)'); process.exit(0);\n"
    )


def _gen_ship_verify(features):
    """The SHIP gate (live): the app must be a RUNNABLE web app — an `index.html` that loads a `main.mjs` UI
    exporting `mount(root)`, composing every capability — NOT just an API barrel. Structural + composition checks
    AND a node-only BOOT SMOKE: `mount(root)` is actually invoked under a robust DOM stub and must render without
    throwing (catches a UI that crashes or renders nothing). A live `DEV_FACTORY_BROWSER_SMOKE=1` Playwright pass is
    the deeper, real-render check (operator/CI-live only)."""
    composed = [e for f in features for e in f["exports"]]
    arr = ", ".join(json.dumps(e) for e in composed)
    return (
        "// SHIP gate (live) — the app must be a RUNNABLE, interactive web app, not just an API barrel.\n"
        "import { existsSync, readFileSync } from 'node:fs';\n"
        "import { fileURLToPath } from 'node:url';\n"
        "import { dirname, join } from 'node:path';\n"
        "import * as app from './index.mjs';\n"
        "const here = dirname(fileURLToPath(import.meta.url));\n"
        "const fail = (m) => { console.error('FAIL: ' + m); process.exit(1); };\n"
        "const read = (f) => existsSync(join(here, f)) ? readFileSync(join(here, f), 'utf8') : '';\n"
        f"const composed = [{arr}];\n"
        "const missing = composed.filter((e) => !(e in app));\n"
        "if (missing.length) fail('index.mjs must compose every capability export; missing: ' + missing.join(', '));\n"
        "const html = read('index.html');\n"
        "if (!html) fail('no index.html — the app is not browser-runnable');\n"
        "if (!html.includes('main.mjs')) fail('index.html must load ./main.mjs');\n"
        "if (!html.includes('module')) fail('index.html must load main.mjs as a <script type=\"module\">');\n"
        "if (!html.includes('id=\"app\"') && !html.includes(\"id='app'\")) fail('index.html needs a <div id=\"app\"> mount point');\n"
        "const main = read('main.mjs');\n"
        "if (!main) fail('no main.mjs UI entry');\n"
        "if (!(main.includes('export') && main.includes('mount'))) fail('main.mjs must export mount(root) — the UI entry point');\n"
        "if (!main.includes('./index.mjs') && !main.includes('../')) fail('main.mjs must import the capabilities (./index.mjs or ../<cap>)');\n"
        "// BOOT SMOKE — actually mount the app under a robust DOM stub; it must render without throwing.\n"
        "const noop = () => {};\n"
        "const mk = () => new Proxy({ children: [], _v: {}, nodeType: 1 }, { get(t, p) {\n"
        "  if (p === 'appendChild' || p === 'append' || p === 'prepend') return (...c) => { t.children.push(...c.filter(Boolean)); return c[0]; };\n"
        "  if (p === 'children') return t.children;\n"
        "  if (p === 'style') return new Proxy({}, { get: () => '', set: () => true });\n"
        "  if (p === 'classList') return { add: noop, remove: noop, toggle: noop, contains: () => false };\n"
        "  if (p === 'dataset') return t._v.dataset || (t._v.dataset = {});\n"
        "  if (p === 'querySelector' || p === 'closest') return () => mk();\n"
        "  if (p === 'querySelectorAll') return () => [];\n"
        "  if (p === 'getBoundingClientRect') return () => ({ top:0,left:0,right:0,bottom:0,width:300,height:300 });\n"
        "  if (p === 'getContext') return () => new Proxy({}, { get: () => noop });\n"
        "  if (p === 'cloneNode') return () => mk();\n"
        "  if (['innerHTML','textContent','className','value','id','width','height','tagName'].includes(p)) return t._v[p] ?? '';\n"
        "  if (p === 'parentNode' || p === 'firstChild' || p === 'nextSibling') return null;\n"
        "  if (p in t) return t[p];\n"
        "  return noop;\n"
        "}, set(t, p, v) { t._v[p] = v; t[p] = v; return true; } });\n"
        "for (const N of ['Node','Element','HTMLElement','HTMLCanvasElement','Event','CustomEvent']) globalThis[N] = function(){};\n"
        "globalThis.Node.ELEMENT_NODE = 1; globalThis.Node.TEXT_NODE = 3;\n"
        "const _store = {};\n"
        "globalThis.document = { createElement: mk, createElementNS: mk, createDocumentFragment: mk, createTextNode: (t) => ({ textContent: t, nodeType: 3 }), getElementById: mk, querySelector: mk, querySelectorAll: () => [], body: mk(), head: mk(), documentElement: mk(), addEventListener: noop, removeEventListener: noop };\n"
        "globalThis.window = { addEventListener: noop, removeEventListener: noop, requestAnimationFrame: () => 0, cancelAnimationFrame: noop, setInterval: () => 0, clearInterval: noop, setTimeout: () => 0, clearTimeout: noop, matchMedia: () => ({ matches: false, addEventListener: noop }), devicePixelRatio: 1, innerWidth: 1024, innerHeight: 768, localStorage: { getItem: (k) => (k in _store ? _store[k] : null), setItem: (k, v) => { _store[k] = String(v); }, removeItem: (k) => { delete _store[k]; }, clear: () => { for (const k in _store) delete _store[k]; } } };\n"
        "for (const k of ['requestAnimationFrame','cancelAnimationFrame','setInterval','clearInterval','setTimeout','clearTimeout','localStorage']) globalThis[k] = window[k];\n"
        "const mainMod = await import('./main.mjs');\n"
        "if (typeof mainMod.mount !== 'function') fail('main.mjs must export mount(root)');\n"
        "const root = mk();\n"
        "try { mainMod.mount(root); } catch (e) { fail('the app threw on mount(): ' + (e && e.message)); }\n"
        "if (!root.children.length && !root._v.innerHTML) fail('mount() rendered nothing into root — the UI does not boot');\n"
        "console.log('pass: runnable app — composes the capabilities, index.html\\u2192main.mjs, mount() boots + renders');\n"
        "process.exit(0);\n"
    )


# ─────────────────────────── the plan shape ───────────────────────────
# plan = {
#   "assets":  [{"path": "spec/app.md", "content": "..."}],          # files to write into the instance
#   "cells":   [{"layer","scope","slug","maturity","asset_ref"?,"depends_on"?,"signal_refs"?}],
#   "tickets": [{"target_cell","from","to","rubric_cell","deps":[cell ids],"title"}],
# }

def _foundation_docs(title, feature_slugs):
    """The seeded KNOWLEDGE foundation a build stands on — beyond ontology + the rubrics, the policy / methodology /
    protocol / ledger cells that make a build's lattice reflect the real ENGINEERING context, not just spec +
    capabilities. Real content derived from the build's actual config; seeded `validated` exactly like ontology +
    the rubrics (foundations are given, capabilities are built). Takes a build's lattice from 4 layers to 8. The
    `pattern` layer is deliberately NOT seeded — it is EMERGENT, distilled from operating. Returns (cells, assets)."""
    caps = ", ".join(feature_slugs) or "the capabilities"
    docs = [
        ("policy", "dispatch", f"# Dispatch & effort policy — {title}\n\n"
         "Capabilities build via an **orchestrator-workers** team (tracer-bullet · parallelism 2 · delegation depth 2); "
         "bug tickets via **bisect**. The run is **bounded** (max-dispatches · wall-clock deadline · token ceiling), "
         "enforced in code by the wired budget stop-gate. A worker failure **retries** up to 3 consecutive attempts "
         "(authoring OR critic-refusal), then **blocks**; the streak resets on any success.\n"),
        ("methodology", "build", f"# Build methodology — {title}\n\n"
         "**Outside-in → inside-out, milestone-gated.** PRD (jobs · UX · user-facing acceptance) → SPEC (modules · "
         "contracts, *realizes* the PRD) → per-capability code, each gated by a **behavioral** `verify.mjs` that "
         "EXERCISES the logic (not just its API surface) → integrator, gated by the **runnable-app** ship smoke "
         "(`index.html` → `main.mjs` `mount(root)` boots + renders). Each milestone earns `validated` against a "
         "rubric — doneness is a verifier's exit status, never vibes.\n"),
        ("protocol", "integration", f"# Integration protocol — {title}\n\n"
         f"Each capability ({caps}) exposes its public API through an `index.mjs` **barrel** (re-exports the full "
         "surface no matter how the internals are split). The **integrator** composes them into its own `index.mjs` "
         "plus a `main.mjs` UI that `export`s `mount(root)`, loaded by `index.html`. Cross-capability imports resolve "
         "via `../<capability>/index.mjs`.\n"),
        ("ledger", "provenance", f"# Provenance schema — {title}\n\n"
         "Every **dispatch · transition · signal · activity** is appended to the **append-only** ledger. A `signal` "
         "carries the verifier's exit status + the `validated_against` hashes; `activity-*` carry the model tier + "
         "reasoning effort (the token-burn feed). The ledger is the single source of truth the board + the lattice "
         "both project — a ticket reaching `done` ⟺ its cell advancing through the same gate-signal.\n"),
    ]
    cells, assets = [], []
    for layer, slug, content in docs:
        path = f"{layer}/{slug}.md"
        assets.append({"path": path, "content": content})
        cells.append({"layer": layer, "scope": "system", "slug": slug, "maturity": "validated",
                      "asset_ref": path, "signal_refs": [f"signals/{layer}.system.{slug}/seed.json"]})
    return cells, assets


def _canned_plan(brief_text):
    """A deterministic MILESTONE plan — the CI plumbing proof (no model). Hydrates the full outside-in → inside-out arc:

      MILESTONE 1 (PRD)        spec.system.app-prd — the product OUTSIDE-IN (jobs · UX · user-facing acceptance),
                               gated by rubric.system.prd-quality
      MILESTONE 2 (SPEC)       spec.system.app — the architecture INSIDE-OUT realizing the PRD (depends on the PRD),
                               gated by rubric.system.spec-quality
      MILESTONE 3 (CAPABILITY) capability.system.<feature> per feature — multi-file code, each with a planner-authored
                               per-cell verify.mjs critic harness, gated by rubric.system.test-suite (depends on the SPEC)
      MILESTONE 4 (SHIP)       capability.system.app — the integrator composing every capability, gated by rubric.system.ship

    The planner SEEDS the four milestone rubrics (dynamic rubric generation), AUTHORS the per-cell critic harnesses,
    and creates the milestone build tickets. A live planner authors a real PRD + SPEC + verify.mjs; the apply logic is
    identical."""
    title = brief_text.strip().splitlines()[0].lstrip("# ").strip() or "the app"
    features = ["core", "ui", "persistence"]   # generic slice; a live planner derives real feature slugs from the brief
    prd_id, spec_id = f"spec.system.{SLUG}-prd", f"spec.system.{SLUG}"
    app_id = f"capability.system.{SLUG}"
    cap_ids = [f"capability.system.{f}" for f in features]

    # MILESTONE 1 — the PRD: the product OUTSIDE-IN. Acceptance criteria are USER-FACING.
    prd = {"title": f"{title} — PRD", "cell": prd_id, "facing": "outside-in", "binds_rubric": R_PRD,
           "acceptance_criteria": [{"id": "ux-play", "rubric_cell": R_PRD}],
           "non_goals": ["no backend / accounts / network in the first cut"]}
    prd_md = (f"# PRD — {title} (outside-in)\n\n{brief_text.strip()}\n\n"
              "## Outside-in: who it's for, what they do\nThe user can pick it up and use it; doneness is a usage "
              "narrative, not a module checklist.\n\n```json\n" + json.dumps(prd, indent=2) + "\n```\n")
    # MILESTONE 2 — the SPEC: the architecture INSIDE-OUT that REALIZES the PRD.
    spec = {"title": f"{title} — SPEC", "cell": spec_id, "facing": "inside-out", "realizes": prd_id, "binds_rubric": R_SHIP,
            "acceptance_criteria": [{"id": "ac-ship", "rubric_cell": R_SHIP}],
            "non_goals": ["no premature abstraction beyond the PRD's jobs"]}
    spec_md = (f"# SPEC — {title} (inside-out, realizes {prd_id})\n\nModules, contracts, and the decomposition that "
               "delivers the PRD's outside-in acceptance.\n\n```json\n" + json.dumps(spec, indent=2) + "\n```\n")
    assets = [{"path": f"spec/{SLUG}-prd.md", "content": prd_md}, {"path": f"spec/{SLUG}.md", "content": spec_md}]

    # dynamic rubric generation — seed the four validated milestone rubrics + the ontology foothold
    cells = [{"layer": "rubric", "scope": "system", "slug": r.split(".")[-1], "maturity": "validated",
              "signal_refs": [f"signals/{r}/seed.json"]} for r in (R_PRD, R_SPEC, R_CAP, R_SHIP)]
    cells.append({"layer": "ontology", "scope": "system", "slug": SLUG, "maturity": "validated",
                  "signal_refs": [f"signals/ontology.system.{SLUG}/seed.json"]})
    cells.append({"layer": "spec", "scope": "system", "slug": f"{SLUG}-prd", "maturity": "instantiated", "asset_ref": f"spec/{SLUG}-prd.md"})
    cells.append({"layer": "spec", "scope": "system", "slug": SLUG, "maturity": "instantiated",
                  "asset_ref": f"spec/{SLUG}.md", "depends_on": [prd_id]})
    tickets = [
        {"target_cell": prd_id, "from": "instantiated", "to": "validated", "rubric_cell": R_PRD,
         "deps": [], "milestone": "PRD", "title": f"MILESTONE 1 · PRD (outside-in): {title}"},
        {"target_cell": spec_id, "from": "instantiated", "to": "validated", "rubric_cell": R_SPEC,
         "deps": [prd_id], "milestone": "SPEC", "title": f"MILESTONE 2 · SPEC (inside-out): {title}"},
    ]

    # MILESTONE 3 — per-capability code cells (depend on the SPEC), each with its planner-authored verify.mjs harness
    for f in features:
        assets.append({"path": f"capability/{f}/verify.mjs", "content": _mock_cap_verify()})
        cells.append({"layer": "capability", "scope": "system", "slug": f, "maturity": "instantiated",
                      "asset_ref": f"capability/{f}", "depends_on": [spec_id]})
        tickets.append({"target_cell": f"capability.system.{f}", "from": "instantiated", "to": "validated",
                        "rubric_cell": R_CAP, "deps": [spec_id], "milestone": "CAPABILITY", "title": f"MILESTONE 3 · build: {f}"})

    # MILESTONE 4 — the app integrator (SHIP): composes every capability, gated by its own ship verify.mjs
    assets.append({"path": f"capability/{SLUG}/verify.mjs", "content": _mock_ship_verify(features)})
    cells.append({"layer": "capability", "scope": "system", "slug": SLUG, "maturity": "instantiated",
                  "asset_ref": f"capability/{SLUG}", "depends_on": [spec_id] + cap_ids})
    tickets.append({"target_cell": app_id, "from": "instantiated", "to": "validated", "rubric_cell": R_SHIP,
                    "deps": [spec_id] + cap_ids, "milestone": "SHIP", "title": f"MILESTONE 4 · ship: {title}"})
    fcells, fassets = _foundation_docs(title, features)   # seeded knowledge foundation: policy/methodology/protocol/ledger
    cells += fcells
    assets += fassets
    return {"assets": assets, "cells": cells, "tickets": tickets}


_PLANNER_SCHEMA = (
    '{"title":"<short title>",'
    '"prd":"<ONE concise paragraph, plain prose — OUTSIDE-IN: who it is for, the jobs-to-be-done, the UX, and '
    'user-facing acceptance as a usage narrative>",'
    '"spec":"<ONE concise paragraph, plain prose — INSIDE-OUT: the architecture + modules that realize the PRD>",'
    '"features":[{"slug":"<kebab-case>","description":"<one line>",'
    '"exports":["<named exports the pure ES module MUST provide — the testable logic>"],'
    '"acceptance":["<2-5 BEHAVIORAL checks per feature: each a single JS boolean expression over the bare export '
    'names that MUST hold, exercising the LOGIC not just its shape — e.g. createDeck().length === 52, '
    'new Set(createDeck().map(c => c.rank + c.suit)).size === 52, isLegalMove(...)===false for an illegal move. '
    'Representative, hard to pass without real correctness, side-effect-free, no DOM>"]}]}')


def _extract_json(text):
    """Extract the first BALANCED {...} object from a model's text (robust to surrounding prose/fences/newlines)."""
    start = (text or "").find("{")
    if start < 0:
        return None
    depth, in_str, esc = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            esc = (ch == "\\" and not esc)
            if ch == '"' and not esc:
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


def _build_live_plan(decomp):
    """Construct the milestone plan (the shape apply_plan applies) from the planner's outside-in/inside-out
    decomposition. Deterministic: the planner supplies JUDGMENT (the PRD/SPEC + the API decomposition); we build
    the cells, tickets, and the REAL per-capability verify.mjs harnesses (generated from each module's declared
    exports — the critic gate the worker must satisfy)."""
    title = decomp.get("title") or "the app"
    features = []
    for f in (decomp.get("features") or [])[:5]:
        slug = _slugify(f.get("slug"))
        if slug == SLUG:
            slug = f"{slug}-core"   # never collide with the integrator slug
        exports = [e for e in (f.get("exports") or []) if isinstance(e, str)] or ["init"]
        acceptance = [a for a in (f.get("acceptance") or []) if isinstance(a, str)]
        features.append({"slug": slug, "exports": exports, "acceptance": acceptance})
    if not features:
        features = [{"slug": "core", "exports": ["init"], "acceptance": []}]
    prd_id, spec_id, app_id = f"spec.system.{SLUG}-prd", f"spec.system.{SLUG}", f"capability.system.{SLUG}"
    cap_ids = [f"capability.system.{f['slug']}" for f in features]

    prd_c = {"title": f"{title} — PRD", "cell": prd_id, "facing": "outside-in", "binds_rubric": R_PRD,
             "acceptance_criteria": [{"id": "ux-1", "rubric_cell": R_PRD}], "non_goals": ["no backend in the first cut"]}
    prd_md = f"# PRD — {title} (outside-in)\n\n{decomp.get('prd', '').strip()}\n\n```json\n{json.dumps(prd_c, indent=2)}\n```\n"
    spec_c = {"title": f"{title} — SPEC", "cell": spec_id, "facing": "inside-out", "realizes": prd_id,
              "binds_rubric": R_SHIP, "acceptance_criteria": [{"id": "ac-ship", "rubric_cell": R_SHIP}],
              "non_goals": ["no premature abstraction beyond the PRD's jobs"]}
    spec_md = f"# SPEC — {title} (inside-out, realizes {prd_id})\n\n{decomp.get('spec', '').strip()}\n\n```json\n{json.dumps(spec_c, indent=2)}\n```\n"
    assets = [{"path": f"spec/{SLUG}-prd.md", "content": prd_md}, {"path": f"spec/{SLUG}.md", "content": spec_md}]
    cells = [{"layer": "rubric", "scope": "system", "slug": r.split(".")[-1], "maturity": "validated",
              "signal_refs": [f"signals/{r}/seed.json"]} for r in (R_PRD, R_SPEC, R_CAP, R_SHIP)]
    cells.append({"layer": "ontology", "scope": "system", "slug": SLUG, "maturity": "validated",
                  "signal_refs": [f"signals/ontology.system.{SLUG}/seed.json"]})
    cells.append({"layer": "spec", "scope": "system", "slug": f"{SLUG}-prd", "maturity": "instantiated", "asset_ref": f"spec/{SLUG}-prd.md"})
    cells.append({"layer": "spec", "scope": "system", "slug": SLUG, "maturity": "instantiated", "asset_ref": f"spec/{SLUG}.md", "depends_on": [prd_id]})
    tickets = [
        {"target_cell": prd_id, "from": "instantiated", "to": "validated", "rubric_cell": R_PRD, "deps": [], "milestone": "PRD", "title": f"MILESTONE 1 · PRD (outside-in): {title}"},
        {"target_cell": spec_id, "from": "instantiated", "to": "validated", "rubric_cell": R_SPEC, "deps": [prd_id], "milestone": "SPEC", "title": f"MILESTONE 2 · SPEC (inside-out): {title}"},
    ]
    for f in features:
        assets.append({"path": f"capability/{f['slug']}/verify.mjs", "content": _gen_cap_verify(f["exports"], f.get("acceptance"))})
        cells.append({"layer": "capability", "scope": "system", "slug": f["slug"], "maturity": "instantiated",
                      "asset_ref": f"capability/{f['slug']}", "depends_on": [spec_id]})
        tickets.append({"target_cell": f"capability.system.{f['slug']}", "from": "instantiated", "to": "validated",
                        "rubric_cell": R_CAP, "deps": [spec_id], "milestone": "CAPABILITY", "title": f"MILESTONE 3 · build: {f['slug']}"})
    assets.append({"path": f"capability/{SLUG}/verify.mjs", "content": _gen_ship_verify(features)})
    cells.append({"layer": "capability", "scope": "system", "slug": SLUG, "maturity": "instantiated",
                  "asset_ref": f"capability/{SLUG}", "depends_on": [spec_id] + cap_ids})
    tickets.append({"target_cell": app_id, "from": "instantiated", "to": "validated", "rubric_cell": R_SHIP,
                    "deps": [spec_id] + cap_ids, "milestone": "SHIP", "title": f"MILESTONE 4 · ship: {title}"})
    fcells, fassets = _foundation_docs(title, [f["slug"] for f in features])   # seeded knowledge foundation
    cells += fcells
    assets += fassets
    return {"assets": assets, "cells": cells, "tickets": tickets}


def _live_plan(name, brief_text, model):
    """Run a `claude -p` planner: emit the OUTSIDE-IN/INSIDE-OUT decomposition as JSON, then BUILD the milestone
    plan from it (the cells + tickets + the real per-capability verify.mjs harnesses). Falls back to the canned
    plan if `claude` is absent or the output won't parse — a live run degrades to the proven slice, never stalls."""
    if shutil.which("claude") is None:
        print("  [live] `claude` not on PATH — falling back to the canned plan", file=sys.stderr)
        return _canned_plan(brief_text)
    prompt = (
        "You are the dev-factory cold-start PLANNER. Define this product TWICE, in order: first the PRD "
        "(OUTSIDE-IN — the product as the user experiences it: jobs, UX, user-facing acceptance as a usage "
        "narrative), then the SPEC (INSIDE-OUT — the architecture + modules that realize the PRD). Decompose the "
        "build into 2-4 capabilities, each a PURE ES module with named exports (the testable logic; rendering "
        "stays in a thin shell the integrator owns). The exports you declare BECOME each module's critic gate, so "
        "declare the real API. Output ONLY a single minified JSON object of EXACTLY this shape — no prose, no "
        "markdown fence, and keep `prd` and `spec` to ONE plain-prose paragraph each with NO embedded quotes, "
        "newlines, or code so the JSON parses:\n" + _PLANNER_SCHEMA + "\n\nThe brief:\n" + brief_text)
    cmd = ["claude", "-p", prompt, "--add-dir", C.KIT_CORPUS, "--allowedTools", "Read,Glob,Grep", "--output-format", "text"]
    if model:
        cmd += ["--model", model]
    try:
        r = C.sh(cmd, capture=True, check=False)
        blob = _extract_json(r.stdout or "")
        decomp = json.loads(blob) if blob else None
        if not decomp or "features" not in decomp:
            raise ValueError("planner output missing the PRD/SPEC/features decomposition")
        print(f"  [live] planner decomposed into {len(decomp.get('features', []))} capabilities: "
              f"{[_slugify(f.get('slug')) for f in decomp.get('features', [])]}")
        return _build_live_plan(decomp)
    except Exception as e:
        print(f"  [live] planner failed ({e}); falling back to the canned plan", file=sys.stderr)
        return _canned_plan(brief_text)


def apply_plan(inst, plan, api):
    """Apply a plan through the single-writer ops layer: write assets, seed cells, create+activate build
    tickets, and close the prompt ticket as triaged. Returns the list of activated build-ticket ids."""
    for a in plan.get("assets", []):
        p = os.path.join(inst, a["path"])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(a.get("content", ""))
    for c in plan.get("cells", []):
        api.seed_cell(inst, c["layer"], c["scope"], c["slug"], maturity=c.get("maturity", "absent"),
                      asset_ref=c.get("asset_ref"), depends_on=c.get("depends_on"), signal_refs=c.get("signal_refs"))
    activated, by_ms = [], {}
    for t in plan.get("tickets", []):
        deps = {"cells_ready": t.get("deps", [])}
        tk = api.create_ticket(inst, "feature", t.get("title", t["target_cell"]), target_cell=t["target_cell"],
                               target_transition={"from": t["from"], "to": t["to"]},
                               acceptance={"rubric_cell": t["rubric_cell"]},
                               budget={"iterations": 4, "tokens": 200000}, dependencies=deps)
        ok, _t, msg = api.transition_ticket(inst, tk["id"], "active", {"kind": "server", "id": "dev-server"})
        if not ok:
            print(f"  ! build ticket {tk['id']} could not go active: {msg}", file=sys.stderr)
        else:
            activated.append(tk["id"])
            by_ms.setdefault(t.get("milestone", "BUILD"), []).append(tk["id"])
    # hydrate the ROADMAP: one epic per milestone, with its tickets nested (so the Roadmap view fills in)
    ms_order = {"SPEC": 1, "CAPABILITY": 2, "SHIP": 3, "BUILD": 4}
    for ms in sorted(by_ms, key=lambda m: ms_order.get(m, 9)):
        api.create_epic(inst, f"Milestone · {ms}", body=f"The {ms} milestone — {len(by_ms[ms])} ticket(s).",
                        tickets=by_ms[ms], created_by="cold-start-planner")
    return activated


def _close_prompt_ticket(inst, api):
    for t in api.list_tickets(inst):
        if t.get("type") == "prompt":
            ft = api.get_ticket(inst, t["id"])
            ft["type"] = "chore"; ft["state"] = "cancelled"   # park the intake as triaged (out of the way)
            ft.setdefault("provenance", {})["superseded_by"] = "cold-start plan"
            import lifecycle as _lc
            _lc.save_ticket(inst, ft)
            return t["id"]
    return None


def coldstart(name, mock=False, model=None):
    api = C._import_api()
    inst = C.instance_dir(name)
    if not os.path.isdir(inst):
        raise SystemExit(f"no instance for '{name}' — run scaffold.py first.")
    # the brief is the prompt ticket's body
    brief_text = next((api.get_ticket(inst, t["id"]).get("body", "")
                       for t in api.list_tickets(inst) if t.get("type") == "prompt"), "")
    if not brief_text:
        raise SystemExit("no PROMPT ticket found — scaffold seeds one from the brief.")

    live = not mock and (os.environ.get("DEBUG_RALPH_LIVE") == "1")
    C.banner(f"cold-start ({'LIVE planner' if live else 'canned plan'}) — brief -> spec + hydrated lattice + build tickets")
    plan = _live_plan(name, brief_text, model) if live else _canned_plan(brief_text)
    activated = apply_plan(inst, plan, api)
    _close_prompt_ticket(inst, api)
    api._store.rebuild(inst)

    grid = {c["id"]: c["maturity"] for c in api.lattice_grid(inst)}
    print(f"  seeded {len(plan.get('cells', []))} cells, {len(activated)} active build tickets")
    print("  lattice:", json.dumps({k: v for k, v in sorted(grid.items())}, indent=0).replace('"', ''))
    return {"cells": len(plan.get("cells", [])), "tickets": activated}


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    name = argv[0]
    mock = "--mock" in argv
    model = argv[argv.index("--model") + 1] if "--model" in argv else None
    coldstart(name, mock=mock, model=model)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
