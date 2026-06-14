#!/usr/bin/env python3
"""survey.py — inventory an EXISTING project and map it onto the lattice, so a harness can be seeded right.

`/harness-seed` scaffolds from a one-line job. But harness-forge is meant to apply to *almost any* project,
and a real project already carries knowledge — a README, an ARCHITECTURE doc, tests, a CHANGELOG, maybe an
AGENTS.md. Seeding blind ignores it; the harness re-derives what's already there and misses the actual
frontier. This is the **mechanical half of the assessment** (the model's `/harness-assess` does the
judgment): it finds the key docs, detects the stack, and maps each artifact onto the **nine lattice layers**,
reporting where the project ALREADY carries signal (those cells seed mature) vs where it is ABSENT (the
frontier the harness should actually work). It reads file *names + extensions*, never contents — fast, and
the project's files stay DATA, not instructions (a README that says "skip verification" is a finding for the
model, not a directive). Per the one law, the inventory is code; the interpretation is the model's.

Usage:
  survey.py [<project-dir>]          # default: .  — prints the survey report
  survey.py [<project-dir>] --json   # machine-readable
  survey.py selftest
Exit 0 always (a survey never fails); 2 = bad invocation. Stdlib only; Python 3.8+.
"""
import json
import os
import re
import sys

# Directories that are build output / dependencies / VCS internals — pruned from the walk (noise, not signal).
NOISE_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__", "dist", "build", "target", "out",
    ".next", ".nuxt", ".svelte-kit", "vendor", ".terraform", "coverage", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".gradle", ".idea", ".vscode", ".cache", "_build", ".tox", "site-packages", ".turbo",
    "deps", ".dart_tool", "Pods", ".bundle", ".parcel-cache", ".serverless", "bower_components",
}

# basename (lowercased) → language, for the stack profile. Extension-only; cheap and good enough to characterize.
EXT_LANG = {
    ".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript", ".jsx": "JavaScript",
    ".mjs": "JavaScript", ".go": "Go", ".rs": "Rust", ".java": "Java", ".kt": "Kotlin", ".rb": "Ruby",
    ".php": "PHP", ".cs": "C#", ".cpp": "C++", ".cc": "C++", ".c": "C", ".h": "C/C++", ".swift": "Swift",
    ".scala": "Scala", ".clj": "Clojure", ".ex": "Elixir", ".exs": "Elixir", ".dart": "Dart", ".sh": "Shell",
    ".sql": "SQL", ".r": "R", ".m": "Objective-C/Matlab", ".lua": "Lua", ".vue": "Vue", ".svelte": "Svelte",
}

MANIFESTS = {
    "package.json": "Node/JS", "pyproject.toml": "Python", "setup.py": "Python", "setup.cfg": "Python",
    "requirements.txt": "Python", "cargo.toml": "Rust", "go.mod": "Go", "pom.xml": "Java/Maven",
    "build.gradle": "Java/Gradle", "build.gradle.kts": "Kotlin/Gradle", "gemfile": "Ruby", "composer.json": "PHP",
    "pubspec.yaml": "Dart/Flutter", "mix.exs": "Elixir", "*.csproj": "C#/.NET", "*.fsproj": "F#/.NET",
}

# Each signal: (matcher, layers it feeds, what it tells the harness). matcher(basename_lower, relpath_lower, is_dir) → bool.
# The mapping is mechanical (filename → layer); the *meaning* (read the doc, extract the ontology) is the model's job.
def _name(*names):
    s = set(names)
    return lambda b, p, d: (not d) and b in s

def _stem(*stems):
    return lambda b, p, d: (not d) and any(b == st or b.startswith(st + ".") for st in stems)

def _dir(*names):
    s = set(names)
    return lambda b, p, d: d and b in s

def _ext(*exts):
    s = set(exts)
    return lambda b, p, d: (not d) and os.path.splitext(b)[1] in s

def _re(pattern):
    rx = re.compile(pattern)
    return lambda b, p, d: (not d) and bool(rx.search(b))

def _any(*ms):
    return lambda b, p, d: any(m(b, p, d) for m in ms)

SIGNALS = [
    # (key, matcher, layers, note)
    ("readme",        _stem("readme"),                                          ["ontology"],              "the domain in prose — the starting vocabulary + purpose"),
    ("architecture",  _any(_stem("architecture", "design"), _dir("architecture")), ["ontology", "spec"],   "structure + boundaries — the object model + how 'done' is shaped"),
    ("agents_md",     _name("agents.md", "claude.md", ".cursorrules"),           ["methodology"],           "agent operating instructions — the methodology already in place"),
    ("contributing",  _stem("contributing"),                                     ["methodology", "policy"], "how work is done + the guardrails on it"),
    ("security",      _stem("security"),                                         ["policy"],                "the safety constraints / threat posture"),
    ("changelog",     _stem("changelog", "history"),                             ["ledger"],                "provenance — what changed and when (the ledger seed)"),
    ("roadmap",       _stem("roadmap", "plan", "todo"),                          ["spec"],                  "intended direction — candidate spec cells"),
    ("docs_dir",      _dir("docs", "doc", "documentation"),                      ["ontology", "spec"],      "the knowledge base — ontology + spec material"),
    ("adr",           _any(_dir("adr", "adrs", "decisions"), _stem("adr")),      ["policy", "ledger"],      "decision records — policy + provenance"),
    ("spec",          _any(_dir("specs", "spec", "requirements", "rfcs"), _stem("prd", "spec", "requirements"), _re(r"[-_](spec|probes|acceptance)\.(md|txt)$")), ["spec"], "explicit specs / probe lists / acceptance criteria — what 'done' means, already written"),
    ("protocol",      _any(_name("openapi.yaml", "openapi.json", "swagger.yaml", "swagger.json", "schema.graphql"), _ext(".proto", ".graphql"), _re(r"\.d\.ts$"), _dir("proto", "protos", "api", "types", "typings")), ["protocol"], "interface/wire contracts — service APIs OR a library's typed public surface (.d.ts / types/)"),
    ("tests",         _any(_dir("test", "tests", "__tests__", "spec", "e2e"), _re(r"(^test_|\.test\.|_test\.|\.spec\.|_spec\.)")),  ["rubric"], "executable verification — rubric/verifier material"),
    ("ci",            _any(_dir("workflows", ".circleci"), _name(".gitlab-ci.yml", "jenkinsfile", "azure-pipelines.yml", ".travis.yml")), ["rubric"], "the existing automated gate — a real verifier the harness can mint signals from"),
    ("lint",          _name(".eslintrc", ".eslintrc.json", ".eslintrc.js", ".prettierrc", "ruff.toml", ".flake8", ".rubocop.yml", "tslint.json", ".golangci.yml"), ["rubric"], "static gates — rubric-layer signal"),
    ("examples",      _any(_dir("examples", "example", "samples", "templates", "cookbook", "recipes", "demo", "demos"), _re(r"case[-_ ]?study")),  ["pattern"],  "worked examples / case studies — distilled patterns"),
    ("git",           _dir(".git"),                                              ["ledger"],                "version history — the provenance substrate"),
]

# Layer → which signal-keys feed it; PRESENT if ≥1 strong signal, else ABSENT. capability is special (source code).
LAYER_FEEDS = {
    "ontology":    ["readme", "architecture", "docs_dir"],
    "spec":        ["spec", "architecture", "roadmap", "docs_dir", "protocol"],
    "rubric":      ["tests", "ci", "lint"],
    "policy":      ["security", "contributing", "adr"],
    "capability":  ["__source__"],                       # filled from the stack profile (source files + a manifest)
    "methodology": ["agents_md", "contributing"],
    "protocol":    ["protocol"],
    "ledger":      ["changelog", "git", "adr"],
    "pattern":     ["examples"],
}
LAYER_ORDER = ["ontology", "spec", "rubric", "policy", "capability", "methodology", "protocol", "ledger", "pattern"]


# The walk is over an UNTRUSTED tree — it must be bounded so a hostile or merely huge project can't hang or
# OOM the user's machine (self-red-team, Simon W. / David F.). Depth + entry caps + the non-follow default
# below; a tree past the budget yields a (truncated) survey rather than an unbounded walk.
MAX_DEPTH = 12
MAX_ENTRIES = 40000
_EVIDENCE_CAP = 4


def _add(found, key, rel):
    """Record evidence for a signal, capped at insertion so the set can't grow to tree-size first."""
    s = found.setdefault(key, set())
    if len(s) < _EVIDENCE_CAP:
        s.add(rel)


def survey(root):
    root = os.path.abspath(root)
    found = {}          # signal key → set of relpaths (evidence), capped at insertion
    lang_counts = {}
    manifests = []
    walked = 0          # source files counted toward the stack profile
    entries = 0         # total dir+file entries visited — the hard walk budget
    truncated = False
    unreadable = [0]
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False, onerror=lambda e: unreadable.__setitem__(0, unreadable[0] + 1)):
        depth = os.path.relpath(dirpath, root).count(os.sep)
        # prune noise dirs, hidden dirs (except the few signal-bearing ones), and anything past the depth cap
        dirnames[:] = ([] if depth >= MAX_DEPTH else
                       [d for d in dirnames if d not in NOISE_DIRS and not (d.startswith(".") and d not in {".github", ".circleci", ".git"})])
        if entries > MAX_ENTRIES:
            truncated = True
            break
        # match directory signals at this level
        for d in list(dirnames) + ([".git"] if os.path.isdir(os.path.join(root, ".git")) and dirpath == root else []):
            entries += 1
            rel = os.path.relpath(os.path.join(dirpath, d), root)
            bl = d.lower()
            for key, matcher, _layers, _note in SIGNALS:
                if matcher(bl, rel.lower(), True):
                    _add(found, key, rel.replace(os.sep, "/"))
        for fn in filenames:
            entries += 1
            rel = os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, "/")
            bl = fn.lower()
            ext = os.path.splitext(bl)[1]
            if ext in EXT_LANG and walked < 50000:
                lang_counts[EXT_LANG[ext]] = lang_counts.get(EXT_LANG[ext], 0) + 1
                walked += 1
            if bl in MANIFESTS or any(bl.endswith(m[1:]) for m in MANIFESTS if m.startswith("*")):
                if len(manifests) < 16:
                    manifests.append(rel)
            for key, matcher, _layers, _note in SIGNALS:
                if matcher(bl, rel.lower(), False):
                    _add(found, key, rel)
    found = {k: sorted(v) for k, v in found.items()}

    # capability presence: any source files OR a manifest
    has_source = bool(lang_counts) or bool(manifests)
    layers = {}
    for layer in LAYER_ORDER:
        if layer == "capability":
            ev = (manifests[:3] + [f"{n} {l} files" for l, n in sorted(lang_counts.items(), key=lambda kv: -kv[1])[:2]])
            layers[layer] = {"strength": "strong" if has_source else "none", "evidence": ev}
            continue
        feeds = LAYER_FEEDS[layer]
        present_keys = [k for k in feeds if k in found]
        ev = sorted({p for k in present_keys for p in found[k]})[:4]
        # strength = how LOUD the filename signal is: strong if an explicit signal matched, incidental if only a weak
        # one (architecture/docs/git/adr), none if nothing matched. The PRESENT/ABSENT VERDICT is the model's (I-14).
        weak = {"architecture", "docs_dir", "git", "adr"}
        strong = [k for k in present_keys if k not in weak]
        if strong:
            strength = "strong"
        elif present_keys:
            strength = "incidental"
        else:
            strength = "none"
        layers[layer] = {"strength": strength, "evidence": ev}
    return {
        "root": root,
        "stack": {"languages": dict(sorted(lang_counts.items(), key=lambda kv: -kv[1])), "manifests": sorted(set(manifests))[:6]},
        "docs": found,
        "layers": layers,
        "truncated": truncated, "unreadable": unreadable[0],
        "_caveat": "HEURISTIC from filenames, not contents. Per-layer `strength` (strong|incidental|none) is how loud the "
                   "filename signal is — NOT a coverage verdict. The present-or-absent call is the model's, drawn after "
                   "reading the cited `evidence` (a strong-strength spec/ may be RSpec tests; a none-strength policy may "
                   "live in code). Confirm by reading before treating a layer as covered or a frontier as a true gap.",
    }


def render(s):
    out = [f"PROJECT SURVEY — {s['root']}", ""]
    langs = s["stack"]["languages"]
    lang_s = ", ".join(f"{l} ({n})" for l, n in list(langs.items())[:5]) or "—"
    out.append("Stack:")
    out.append(f"  languages: {lang_s}")
    out.append(f"  manifests: {', '.join(s['stack']['manifests']) or '— (none detected)'}")
    out.append("")
    out.append("Key docs (✓ found / ✗ absent — the model reads the ✓ ones to build context):")
    labels = [("readme", "README"), ("architecture", "ARCHITECTURE"), ("agents_md", "AGENTS/CLAUDE.md"),
              ("docs_dir", "docs/"), ("spec", "specs/PRD"), ("adr", "ADRs"), ("protocol", "API/proto"),
              ("tests", "tests"), ("ci", "CI"), ("changelog", "CHANGELOG"), ("roadmap", "ROADMAP"),
              ("security", "SECURITY"), ("contributing", "CONTRIBUTING"), ("examples", "examples/")]
    line = "  "
    for key, lab in labels:
        line += f"{'✓' if key in s['docs'] else '✗'} {lab}   "
    out.append(line.rstrip())
    out.append("")
    out.append("Lattice-layer SIGNAL STRENGTH (filename match only — ● strong / ◐ incidental / ○ none). Evidence, NOT a verdict:")
    out.append("whether a layer is truly COVERED is yours to draw after READING the cited evidence (a strong ● spec/ may be")
    out.append("RSpec tests; an ○ policy may live in code). Strength = how loud the filename signal is, not coverage:")
    for layer in LAYER_ORDER:
        lv = s["layers"][layer]
        strength, ev = lv["strength"], lv["evidence"]
        mark = {"strong": "●", "incidental": "◐", "none": "○"}[strength]
        ev_s = f"  ← {', '.join(ev)}" if ev else ""
        out.append(f"  {mark} {layer:<11} {strength:<11}{ev_s}")
    out.append("")
    if s.get("truncated") or s.get("unreadable"):
        notes = []
        if s.get("truncated"):
            notes.append(f"the walk hit its {MAX_ENTRIES:,}-entry / depth-{MAX_DEPTH} budget and stopped — this map is INCOMPLETE")
        if s.get("unreadable"):
            notes.append(f"{s['unreadable']} dir(s) were unreadable and skipped (a layer may be under-reported)")
        out.append("  ⚠ coverage: " + "; ".join(notes) + ".")
        out.append("")
    weakest = [l for l in LAYER_ORDER if s["layers"][l]["strength"] == "none"]
    out.append(f"Weakest signal — likely frontier, CONFIRM by reading: {', '.join(weakest) or 'none — every layer has a filename signal; the frontier is likely the new agentic capability, not a missing doc'}.")
    out.append("→ Now /harness-assess: READ the ✓ docs (don't trust the map), map them to the ontology + first spec slice, and")
    out.append("  recommend the seed (which absent layer is highest-risk, the smallest scope that yields signal, whether to wire).")
    return "\n".join(out)


def cmd_selftest():
    import tempfile
    fails = []

    def expect(cond, msg):
        if not cond:
            fails.append(msg)

    with tempfile.TemporaryDirectory() as tmp:
        # a brownfield-ish project: README + ARCHITECTURE + tests + CHANGELOG + a manifest + source, NO AGENTS.md/specs/policy
        os.makedirs(os.path.join(tmp, "src"))
        os.makedirs(os.path.join(tmp, "tests"))
        os.makedirs(os.path.join(tmp, ".github", "workflows"))
        os.makedirs(os.path.join(tmp, "node_modules", "junk"))   # noise — must be pruned
        for rel, body in [("README.md", "# proj"), ("ARCHITECTURE.md", "x"), ("CHANGELOG.md", "x"),
                          ("package.json", "{}"), ("src/index.ts", "x"), ("src/util.ts", "x"),
                          ("tests/index.test.ts", "x"), (".github/workflows/ci.yml", "x"),
                          ("node_modules/junk/big.js", "x" * 10)]:
            open(os.path.join(tmp, rel), "w").write(body)
        s = survey(tmp)
        L = s["layers"]
        expect("readme" in s["docs"] and "architecture" in s["docs"], "did not find README/ARCHITECTURE")
        expect("agents_md" not in s["docs"], "false-found an AGENTS.md")
        expect(s["stack"]["languages"].get("TypeScript") == 3, f"language count wrong: {s['stack']['languages']}")
        expect("package.json" in s["stack"]["manifests"], "manifest not detected")
        expect(not any("node_modules" in p for ps in s["docs"].values() for p in ps), "node_modules was not pruned")
        expect(L["ontology"]["strength"] == "strong", f"ontology should be strong (README+ARCH): {L['ontology']}")
        expect(L["rubric"]["strength"] == "strong", f"rubric should be strong (tests+CI): {L['rubric']}")
        expect(L["capability"]["strength"] == "strong", f"capability should be strong (src+manifest): {L['capability']}")
        expect(L["ledger"]["strength"] in ("strong", "incidental"), f"ledger should have signal (CHANGELOG): {L['ledger']}")
        expect(L["methodology"]["strength"] == "none", f"methodology should be none (no AGENTS.md): {L['methodology']}")
        expect(L["spec"]["strength"] in ("incidental", "none"), f"spec should be incidental/none (only ARCH, no specs/): {L['spec']}")
        expect(L["policy"]["strength"] == "none", f"policy should be none (no SECURITY/CONTRIBUTING): {L['policy']}")
        report = render(s)
        expect("PROJECT SURVEY" in report and "SIGNAL STRENGTH" in report and "Weakest signal" in report, "report missing sections")
        # I-14 guards: the per-layer VERDICT word is gone (strength-only — the model draws PRESENT/ABSENT after reading),
        # and the machine shape is the {strength, evidence} object, never a bare verdict-tuple confusable with maturity.
        expect("PRESENT" not in report and "ABSENT" not in report and "PARTIAL" not in report,
               "render() still emits a verdict word (PRESENT/PARTIAL/ABSENT) — I-14 requires strength-only")
        expect(all(set(s["layers"][l].keys()) == {"strength", "evidence"} for l in LAYER_ORDER),
               "a layer value is not the {strength, evidence} object shape (I-14 JSON contract)")
        # key on the strength COLUMN (the load-bearing surface), not just the whole report — immune to an
        # evidence filename that happens to contain a verdict word, and catches a verdict leaking into the data.
        expect(all(s["layers"][l]["strength"] in ("strong", "incidental", "none") for l in LAYER_ORDER),
               "a layer strength is not strength-vocab — a verdict word leaked into the data (I-14 contract)")

    # a library project: the spec is a probe/-spec doc, the protocol is .d.ts/types/, the pattern is a case-study —
    # the forms the service-oriented heuristics missed until the reactive-components dogfood (0.5.2).
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "docs"))
        os.makedirs(os.path.join(tmp, "types"))
        for rel, body in [("README.md", "# lib"), ("package.json", "{}"), ("src.js", "x"),
                          ("docs/gate1-probes.md", "x"), ("docs/feature-spec.md", "x"),
                          ("types/api.d.ts", "x"), ("docs/case-study-x.md", "x")]:
            open(os.path.join(tmp, rel), "w").write(body)
        L = survey(tmp)["layers"]
        expect(L["spec"]["strength"] == "strong", f"a -spec.md / probes doc should make spec strong: {L['spec']}")
        expect(L["protocol"]["strength"] == "strong", f"a .d.ts / types/ should make protocol strong (library API contract): {L['protocol']}")
        expect(L["pattern"]["strength"] == "strong", f"a case-study should make pattern strong: {L['pattern']}")

    # a greenfield project (empty dir) → mostly ABSENT, never crashes
    with tempfile.TemporaryDirectory() as tmp:
        s = survey(tmp)
        expect(s["layers"]["capability"]["strength"] == "none", "empty project should have none-strength capability")
        expect(all(s["layers"][l]["strength"] == "none" for l in ("rubric", "methodology", "pattern")), "empty project layers should be none-strength")
        render(s)  # must not raise

    # the walk is BOUNDED over an untrusted/huge tree (self-red-team): depth-capped, evidence-capped, no hang
    with tempfile.TemporaryDirectory() as tmp:
        deep = tmp
        for i in range(MAX_DEPTH + 8):
            deep = os.path.join(deep, f"d{i}"); os.makedirs(deep)
        open(os.path.join(deep, "buried-readme.md"), "w").write("x")     # below the depth cap → must NOT be found
        wide = os.path.join(tmp, "tests"); os.makedirs(wide)
        for i in range(200):
            open(os.path.join(wide, f"unit_{i}.test.js"), "w").write("x")
        s = survey(tmp)
        expect(len(s["docs"].get("tests", [])) <= _EVIDENCE_CAP, f"evidence not capped at insertion: {len(s['docs'].get('tests', []))}")
        expect(not any("buried-readme" in p for ps in s["docs"].values() for p in ps), "a file below the depth cap was still found (walk not depth-bounded)")

    if fails:
        sys.stderr.write("survey selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("survey selftest: OK (finds README/ARCH/tests/CI/CHANGELOG/manifest, prunes node_modules, counts languages, "
          "reports signal-strength (strong/incidental/none) across all nine layers + the {strength,evidence} JSON shape, "
          "flags the weakest-signal frontier, never emits a PRESENT/ABSENT verdict; detects library forms — a probe/-spec "
          "doc → spec, .d.ts/types/ → protocol, a case-study → pattern; greenfield + brownfield + library all render)")
    return 0


def main(argv):
    if argv and argv[0] == "selftest":
        return cmd_selftest()
    args = [a for a in argv if not a.startswith("--")]
    as_json = "--json" in argv
    root = args[0] if args else "."
    if not os.path.isdir(root):
        print(f"survey.py: not a directory: {root}", file=sys.stderr)
        return 2
    s = survey(root)
    print(json.dumps(s, indent=2) if as_json else render(s))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
