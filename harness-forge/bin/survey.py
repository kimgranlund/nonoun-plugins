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


def survey(root):
    root = os.path.abspath(root)
    found = {}          # signal key → sorted list of relpaths (evidence)
    lang_counts = {}
    manifests = []
    walked = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in NOISE_DIRS and not (d.startswith(".") and d not in {".github", ".circleci", ".git"})]
        depth = os.path.relpath(dirpath, root).count(os.sep)
        # match directory signals at this level
        for d in list(dirnames) + ([".git"] if os.path.isdir(os.path.join(root, ".git")) and dirpath == root else []):
            rel = os.path.relpath(os.path.join(dirpath, d), root)
            bl = d.lower()
            for key, matcher, _layers, _note in SIGNALS:
                if matcher(bl, rel.lower(), True):
                    found.setdefault(key, set()).add(rel.replace(os.sep, "/"))
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, "/")
            bl = fn.lower()
            ext = os.path.splitext(bl)[1]
            if ext in EXT_LANG and walked < 50000:
                lang_counts[EXT_LANG[ext]] = lang_counts.get(EXT_LANG[ext], 0) + 1
                walked += 1
            if bl in MANIFESTS or any(bl.endswith(m[1:]) for m in MANIFESTS if m.startswith("*")):
                manifests.append(rel)
            for key, matcher, _layers, _note in SIGNALS:
                if matcher(bl, rel.lower(), False):
                    found.setdefault(key, set()).add(rel)
    found = {k: sorted(v)[:4] for k, v in found.items()}   # cap evidence per signal

    # capability presence: any source files OR a manifest
    has_source = bool(lang_counts) or bool(manifests)
    layers = {}
    for layer in LAYER_ORDER:
        if layer == "capability":
            ev = (manifests[:3] + [f"{n} {l} files" for l, n in sorted(lang_counts.items(), key=lambda kv: -kv[1])[:2]])
            layers[layer] = ("PRESENT" if has_source else "ABSENT", ev)
            continue
        feeds = LAYER_FEEDS[layer]
        present_keys = [k for k in feeds if k in found]
        ev = sorted({p for k in present_keys for p in found[k]})[:4]
        # PRESENT if a *strong/explicit* signal is there; PARTIAL if only an incidental one (architecture/docs/git);
        weak = {"architecture", "docs_dir", "git", "adr"}
        strong = [k for k in present_keys if k not in weak]
        if strong:
            status = "PRESENT"
        elif present_keys:
            status = "PARTIAL"
        else:
            status = "ABSENT"
        layers[layer] = (status, ev)
    return {
        "root": root,
        "stack": {"languages": dict(sorted(lang_counts.items(), key=lambda kv: -kv[1])), "manifests": sorted(set(manifests))[:6]},
        "docs": found,
        "layers": layers,
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
    out.append("Lattice-layer signal — where the project ALREADY carries knowledge (seed those cells mature)")
    out.append("vs ABSENT (the frontier the harness should work). Evidence in parens:")
    for layer in LAYER_ORDER:
        status, ev = s["layers"][layer]
        mark = {"PRESENT": "●", "PARTIAL": "◐", "ABSENT": "○"}[status]
        ev_s = f"  ← {', '.join(ev)}" if ev else ""
        out.append(f"  {mark} {layer:<11} {status:<8}{ev_s}")
    out.append("")
    absent = [l for l in LAYER_ORDER if s["layers"][l][0] == "ABSENT"]
    out.append(f"Frontier (ABSENT layers): {', '.join(absent) or 'none — a mature project; the frontier is the new agentic capability'}.")
    out.append("→ Now /harness-assess: read the ✓ docs, map them to the ontology + first spec slice, and recommend the seed")
    out.append("  (which absent layer is highest-risk, the smallest scope that yields signal, and whether to wire the gates).")
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
        expect(L["ontology"][0] == "PRESENT", f"ontology should be PRESENT (README+ARCH): {L['ontology']}")
        expect(L["rubric"][0] == "PRESENT", f"rubric should be PRESENT (tests+CI): {L['rubric']}")
        expect(L["capability"][0] == "PRESENT", f"capability should be PRESENT (src+manifest): {L['capability']}")
        expect(L["ledger"][0] in ("PRESENT", "PARTIAL"), f"ledger should be present-ish (CHANGELOG): {L['ledger']}")
        expect(L["methodology"][0] == "ABSENT", f"methodology should be ABSENT (no AGENTS.md): {L['methodology']}")
        expect(L["spec"][0] in ("PARTIAL", "ABSENT"), f"spec should be partial/absent (only ARCH, no specs/): {L['spec']}")
        expect(L["policy"][0] == "ABSENT", f"policy should be ABSENT (no SECURITY/CONTRIBUTING): {L['policy']}")
        report = render(s)
        expect("PROJECT SURVEY" in report and "Lattice-layer signal" in report and "Frontier" in report, "report missing sections")

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
        expect(L["spec"][0] == "PRESENT", f"a -spec.md / probes doc should make spec PRESENT: {L['spec']}")
        expect(L["protocol"][0] == "PRESENT", f"a .d.ts / types/ should make protocol PRESENT (library API contract): {L['protocol']}")
        expect(L["pattern"][0] == "PRESENT", f"a case-study should make pattern PRESENT: {L['pattern']}")

    # a greenfield project (empty dir) → mostly ABSENT, never crashes
    with tempfile.TemporaryDirectory() as tmp:
        s = survey(tmp)
        expect(s["layers"]["capability"][0] == "ABSENT", "empty project should have ABSENT capability")
        expect(all(s["layers"][l][0] == "ABSENT" for l in ("rubric", "methodology", "pattern")), "empty project layers should be ABSENT")
        render(s)  # must not raise

    if fails:
        sys.stderr.write("survey selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("survey selftest: OK (finds README/ARCH/tests/CI/CHANGELOG/manifest, prunes node_modules, counts languages, "
          "maps present/partial/absent across all nine layers, flags the ABSENT frontier; detects library forms — a "
          "probe/-spec doc → spec, .d.ts/types/ → protocol, a case-study → pattern; greenfield + brownfield + library all render)")
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
