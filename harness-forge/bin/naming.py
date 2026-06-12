#!/usr/bin/env python3
"""naming.py — the self-hosting typed-name validator.

Names carry type. Every composed name in an agentic-systems lattice decomposes into atoms drawn from
closed, declared vocabularies (`schemas/naming.schema.json`); a name that cannot be parsed against the
grammar is a defect, caught mechanically rather than by review. This script is the gate's engine: it
compiles each composition grammar into a regex from the vocab + slug patterns and tests a candidate
name of a given class. The naming system is itself a cell in the ontology — extending a vocabulary is
an ontology revision (edit the schema), never an ad-hoc coinage.

See references/agentic-systems-foundations/naming-conventions.md.

Usage:
  naming.py check <class> <name>     # classes: cell_id agent_file skill_folder hook_script layer_dir plugin
  naming.py classes                  # list the validatable name classes
  naming.py selftest                 # prove the validator (accepts the spec's examples, rejects malformations)
Exit 0 = the name conforms (or selftest passed); 1 = it does not; 2 = bad invocation.
Stdlib only; Python 3.8+.
"""
import json
import os
import re
import sys

_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCHEMA = os.path.join(_ROOT, "schemas", "naming.schema.json")


def load_grammar(path=_SCHEMA):
    g = json.load(open(path, encoding="utf-8"))
    vocab = dict(g["vocab"])
    # `block` is the closed set unioned with every layer value (the schema notes this; we compute it).
    vocab["block"] = list(g.get("block_extra", [])) + list(vocab["layer"])
    return g, vocab


def _token_pattern(token, g, vocab):
    """The regex fragment a grammar placeholder expands to."""
    if token in vocab:                       # a controlled vocabulary → alternation of its values
        return "(?:" + "|".join(re.escape(v) for v in vocab[token]) + ")"
    if token in ("slug", "invariant", "object", "ns"):   # free kebab atoms
        return g.get("slug", "[a-z0-9]+(?:-[a-z0-9]+)*")
    if token == "harness":
        return r"[a-z0-9]+(?:[-_][a-z0-9]+)*"
    if token == "ts":
        return r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}(?:-\d{2})?"
    if token == "cell_id":
        return _compile(g, vocab, "cell_id")[1]   # nested grammar
    raise KeyError(f"unknown grammar token: {{{token}}}")


_PLACEHOLDER = re.compile(r"\{([a-z_]+)\}")


def _expand(template, g, vocab):
    """Expand a grammar template string into a regex fragment (placeholders → patterns, literals escaped)."""
    out, last = [], 0
    for m in _PLACEHOLDER.finditer(template):
        out.append(re.escape(template[last:m.start()]))     # literal separators, escaped
        out.append(_token_pattern(m.group(1), g, vocab))
        last = m.end()
    out.append(re.escape(template[last:]))
    return "".join(out)


def _compile(g, vocab, cls):
    """Return (regex, inner) for a name class — `inner` is the body without ^$ anchors (for nesting)."""
    spec = g["grammars"].get(cls)
    if spec is None:
        raise KeyError(f"unknown name class: {cls}")
    inner = _expand(spec["template"], g, vocab)
    if spec.get("optional_suffix"):                          # e.g. plugin's `-{family}` tail
        inner += "(?:" + _expand(spec["optional_suffix"], g, vocab) + ")?"
    return re.compile("^" + inner + "$"), inner


def validate(name, cls, path=_SCHEMA):
    """Return (ok: bool, reason: str)."""
    g, vocab = load_grammar(path)
    try:
        rx, _ = _compile(g, vocab, cls)
    except KeyError as e:
        return False, str(e)
    if rx.match(name):
        return True, f"{name} conforms to {cls} ({g['grammars'][cls]['template']})"
    return False, f"{name} does not conform to {cls} grammar `{g['grammars'][cls]['template']}` — atoms must be drawn from the declared vocabularies"


def name_classes(path=_SCHEMA):
    return sorted(load_grammar(path)[0]["grammars"].keys())


# (class, name, should_pass) — the spec's own examples plus malformations.
_CASES = [
    ("cell_id", "rubric.workflow.citation-integrity", True),
    ("cell_id", "spec.task.parse-invoice", True),
    ("cell_id", "rubrics.workflow.x", False),       # plural layer — directory drift
    ("cell_id", "rubric.epic.x", False),            # `epic` not a scope
    ("cell_id", "rubric.workflow", False),          # missing slug
    ("agent_file", "cell-advancer.md", True),
    ("agent_file", "pattern-distiller.md", True),
    ("agent_file", "cell-helper.md", False),        # `helper` not an actor
    ("agent_file", "cell-advancer.py", False),      # wrong extension
    ("skill_folder", "frontier-rank", True),
    ("skill_folder", "cell-validate", True),
    ("skill_folder", "cell-frobnicate", False),     # `frobnicate` not an operation
    ("hook_script", "gate-signal", True),
    ("hook_script", "propagate-staleness", True),
    ("hook_script", "emit-ledger", True),
    ("hook_script", "block-signal", False),         # `block` not a gateverb
    ("layer_dir", "spec", True),
    ("layer_dir", "specs", False),                  # plural drift
    ("plugin", "frontier-kernel", True),
    ("plugin", "frontier-kit-corpus", True),
    ("plugin", "harness-forge", True),              # the catalog family axis (forge) — must parse its own grammar
    ("plugin", "frontier-foundry", False),          # `foundry` still not a tier
]


def _dogfood():
    """Run the grammar over the plugin's OWN real artifacts — agents/*.md, the layer dirs, this plugin's name —
    so the self-hosting claim is a mechanical fact, not a coincidence. Returns a list of failures."""
    out = []
    plugin = os.path.basename(_ROOT)
    ok, reason = validate(plugin, "plugin")
    if not ok:
        out.append(f"the plugin's own name `{plugin}` fails its own grammar: {reason}")
    agents_dir = os.path.join(_ROOT, "agents")
    if os.path.isdir(agents_dir):
        for f in sorted(os.listdir(agents_dir)):
            if f.endswith(".md"):
                ok, reason = validate(f, "agent_file")
                if not ok:
                    out.append(f"agent file `{f}`: {reason}")
    return out


def selftest():
    fails = []
    for cls, name, should in _CASES:
        ok, reason = validate(name, cls)
        if ok != should:
            fails.append(f"{cls} `{name}`: expected {'PASS' if should else 'REJECT'}, got {'PASS' if ok else 'REJECT'} ({reason})")
    fails += _dogfood()
    if fails:
        sys.stderr.write("naming selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print(f"naming selftest: OK ({len(_CASES)} cases across {len(name_classes())} name classes — accepts the spec examples, rejects vocab/casing/plural drift)")
    return 0


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    if argv and argv[0] == "classes":
        print(" ".join(name_classes()))
        return 0
    if len(argv) == 3 and argv[0] == "check":
        ok, reason = validate(argv[2], argv[1])
        print(("OK   " if ok else "FAIL ") + reason)
        return 0 if ok else 1
    print(__doc__.split("Usage:")[1].split("Stdlib")[0].strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
