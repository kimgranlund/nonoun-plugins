#!/usr/bin/env python3
"""lattice.py — the canonical lattice operations: scan, rank, advance-validity, staleness.

The lattice is layers × scopes; a cell is one layer at one scope with a maturity state. "What should we
work on next?" is a SELECTION FUNCTION over this grid, not a planning meeting — and selection, ranking,
readiness, and staleness are deterministic graph computations, so they live in code, never in inference
(the routing law: computation routes to code, a model-predicted computation is a hallucination surface).
This script is that code. Canonical state is `.agents/harness/lattice.json`; every other view is derived.

Operations:
  - scan      — sweep the modality axis at the frontier scope → the open/stale gap set (detects gaps; does not rank)
  - rank      — order the gaps by priority ≈ (risk × unlock) ÷ probe-cost, subject to dependency readiness
  - validity  — may this cell advance? (deps validated · verifier-rubric validated · layer partial-order · not blocked)
  - stale     — propagate staleness: an upstream content-hash change flips every dependent to `stale`

The partial order it enforces (a rubric before its spec scores vibes):
  ontology + spec → rubric, policy, capability → methodology, protocol → ledger → pattern

See references/agentic-systems-foundations/lattice-model.md and layer-*.md.

Usage:
  lattice.py init <project> [--dir DIR]          # seed a lattice.json (an ontology+spec slice at task scope)
  lattice.py scan [--dir DIR]                    # the gap set at the frontier scope
  lattice.py rank [--dir DIR]                    # ranked, dependency-ready gaps
  lattice.py validity <cell-id> [--dir DIR]      # can this cell advance? exit 0 = yes
  lattice.py stale <cell-id> <hash> [--dir DIR]  # flip dependents of <cell-id> to stale; print + persist
  lattice.py block <cell-id> [--reason R] [--dir DIR]    # flip the budget/no-progress stop flag (out of rank until unblocked)
  lattice.py unblock <cell-id> [--dir DIR]               # clear it; the cell returns to the ready set
  lattice.py selftest
Exit codes are operation-specific (see each). Stdlib only; Python 3.8+.
"""
import hashlib
import json
import datetime
import os
import shutil
import sys

_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The kernel contract version. Bump it whenever this module's on-disk contract or graph behavior changes
# (a new check, a transition-relation edit, a lattice.json field). `wire.py` stamps it beside the copied
# `_lattice.py` so `wire.py check` can fail a project whose wired kernel has drifted from the installed one
# (CV1 — the vendored-copy-drift the council caught: the staleness plugin must not ship a stale kernel).
KERNEL_VERSION = "0.5.2"

# The controlled vocabularies. cell.schema.json is the SINGLE SOURCE (CV5 — the schemas were inert and
# hand-reimplemented here, a second copy that can drift); these module constants are the portable fallback
# for the wired `_lattice.py` copy, which ships without a schema sibling. `check()` reads the schema when it
# can, and `selftest` asserts these constants still equal the schema's enums — so a drift between the two
# copies is a mechanical failure, not a silent divergence.
LAYERS = ["ontology", "spec", "rubric", "policy", "capability", "methodology", "protocol", "ledger", "pattern"]
SCOPES = ["call", "task", "workflow", "system", "fleet"]
MATURITIES = ["absent", "defined", "instantiated", "validated", "operating", "regenerating", "stale", "deprecated"]
ADVANCEABLE = {"absent", "defined", "instantiated", "regenerating", "stale"}   # maturities an engine pass may act on
SETTLED = {"validated", "operating"}                                          # maturities that count as a foothold


def _cell_schema():
    """Load cell.schema.json (the single source for the cell contract), or None if unavailable (wired copy)."""
    for p in (os.path.join(_ROOT, "schemas", "cell.schema.json"),
              os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "schemas", "cell.schema.json")):
        try:
            return json.load(open(p, encoding="utf-8"))
        except (OSError, ValueError):
            continue
    return None

# The maturity state machine: which states may legally follow which (the transition relation the prose claimed
# but did not encode). `deprecated` is terminal. An engine pass routes through `transition_ok` before mutating.
TRANSITIONS = {
    "absent": {"defined", "deprecated"},
    "defined": {"instantiated", "deprecated"},
    "instantiated": {"validated", "defined", "deprecated"},
    "validated": {"operating", "regenerating", "stale", "deprecated"},
    "operating": {"regenerating", "stale", "deprecated"},
    "regenerating": {"instantiated", "validated", "deprecated"},
    "stale": {"regenerating", "defined", "deprecated"},
    "deprecated": set(),
}

# The layer partial order: which upstream layers (at the same scope) a layer requires a validated foothold in.
# Ledger sits early (schema cannot be retrofitted) so it has no upstream layer dep; pattern sits last (needs operation).
LAYER_DEPS = {
    "ontology": [], "spec": ["ontology"],
    "rubric": ["spec"], "policy": ["spec"], "capability": ["spec", "ontology"],
    "methodology": ["spec", "rubric"], "protocol": ["capability"],
    "ledger": ["ontology"], "pattern": ["ledger"],
}
LAYER_RANK = {l: i for i, (l, _) in enumerate(
    [("ontology", 0), ("spec", 0), ("rubric", 1), ("policy", 1), ("capability", 1),
     ("methodology", 2), ("protocol", 2), ("ledger", 2), ("pattern", 3)])}


def cid(c):
    return f"{c['layer']}.{c['scope']}.{c['slug']}"


def load(d):
    return json.load(open(os.path.join(d, "lattice.json"), encoding="utf-8"))


def kernel_compat(lat):
    """The run-time half of the vendoring contract: `save()` stamps the writing `KERNEL_VERSION` into the
    instance; this reads it back and compares to the running kernel. Returns (ok, message). An UNSTAMPED
    instance (written before the stamp existed, or hand-authored) is treated as compatible — only a
    present-and-different stamp is a skew worth surfacing. Never raises; the caller decides warn vs refuse.
    A vendoring host (e.g. dev-factory) calls this on boot so a future breaking bump becomes a detected
    migration, not a silent corruption."""
    ver = (lat or {}).get("kernel_version")
    if ver and ver != KERNEL_VERSION:
        return False, f"instance was written by kernel {ver} but the running kernel is {KERNEL_VERSION} — migrate or re-validate before operating"
    return True, None


def save(d, lat):
    # Atomic write (CV1/Simon): the staleness cascade rewrites lattice.json on every PostToolUse edit; a
    # plain truncating dump that is interrupted mid-write corrupts the canonical state. Write a temp file in
    # the same dir, then os.replace — the same discipline wire.py already uses for the user's settings.json.
    lat["kernel_version"] = KERNEL_VERSION   # stamp the writing kernel — the migration anchor kernel_compat() reads back
    path = os.path.join(d, "lattice.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(lat, f, indent=2)
    os.replace(tmp, path)


def find(lat, cell_id):
    return next((c for c in lat["cells"] if cid(c) == cell_id), None)


def content_hash(path):
    """The canonical 16-hex content hash signals and staleness compare (the same shape validate.py mints)."""
    try:
        return "sha256:" + hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    except OSError:
        return ""


def _validated_at(lat, layer, scope):
    """Is there a validated/operating cell of `layer` at `scope`? (a same-scope upstream foothold)."""
    return any(c["layer"] == layer and c["scope"] == scope and c["maturity"] in SETTLED for c in lat["cells"])


def ready(lat, c):
    """A cell is dependency-ready iff its explicit depends_on are all validated, its verifier rubric (if any) is
    validated, and every upstream LAYER it requires has a validated foothold at its scope. Returns (bool, reasons)."""
    reasons = []
    for dep in c.get("depends_on", []):
        d = find(lat, dep)
        if d is None or d["maturity"] not in SETTLED:
            reasons.append(f"depends_on {dep} is {'absent' if d is None else d['maturity']}, not validated")
    v = c.get("verifier")
    if v:
        vc = find(lat, v)
        if vc is None or vc["maturity"] != "validated":
            reasons.append(f"verifier {v} is {'absent' if vc is None else vc['maturity']}, not validated (a cell advances only against a validated rubric)")
    for up in LAYER_DEPS.get(c["layer"], []):
        if not _validated_at(lat, up, c["scope"]):
            reasons.append(f"no validated {up} cell at scope {c['scope']} (partial order: {c['layer']} requires {up} upstream)")
    return (not reasons, reasons)


def scan(lat):
    """The gap set: cells at the frontier scope whose maturity is open (absent/defined/instantiated) or stale."""
    fs = lat.get("frontier_scope", "task")
    return [c for c in lat["cells"] if c["scope"] == fs and c["maturity"] in (ADVANCEABLE | {"stale"})]


def _probe_cost(lat, c):
    """Probe cost ≈ prior iterations for this layer/scope, read from the ledger when history exists, else 1."""
    led = lat.get("_ledger_cost", {})            # injected by the CLI from ledger.py; default-free in pure use
    return led.get(c["layer"], {}).get(c["scope"], 1) or 1


def rank(lat):
    """Order the dependency-ready gaps by priority ≈ (risk × unlock) ÷ probe-cost. Returns [(priority, cell, reasons)]."""
    gaps = scan(lat)
    # unlock = how many other cells declare this one as a dependency (out-degree of being depended-on).
    depended = {}
    for c in lat["cells"]:
        for dep in c.get("depends_on", []):
            depended[dep] = depended.get(dep, 0) + 1
    out = []
    for c in gaps:
        if c.get("blocked"):
            continue                              # a blocked cell (budget cap / no-progress) is out of the ready set
        ok, reasons = ready(lat, c)
        if not ok:
            continue                              # not yet selectable — dependency filter
        risk = 4 - LAYER_RANK[c["layer"]]         # upstream layers concentrate risk (block more downstream)
        unlock = 1 + depended.get(cid(c), 0)
        priority = (risk * unlock) / _probe_cost(lat, c)
        out.append((round(priority, 3), c, reasons))
    out.sort(key=lambda t: -t[0])
    return out


def set_blocked(lat, cell_id, blocked=True, reason=""):
    """Flip a cell's `blocked` condition flag (the budget/no-progress stop). The flag is a Property, not a
    maturity; a blocked cell falls out of `rank` and `advance_validity` until unblocked. This is a PROTECTED
    write (lattice.json) — the orchestrator/harness sets it, never the worker (the worker is deny-on-write to
    the lattice). Returns the cell, or None if absent."""
    c = find(lat, cell_id)
    if c is None:
        return None
    if blocked:
        c["blocked"] = True
        if reason:
            c["blocked_reason"] = reason
    else:
        c.pop("blocked", None)
        c.pop("blocked_reason", None)
    return c


# ── The global run bound, in code (the council's convergent v0.4.0 Critical fix). The orchestrator no longer
# "ticks" caps in its own context; the run's budget is persisted and the exhaustion verdict is COMPUTED here
# (wall-clock from an absolute deadline — no counter; iterations/cells counted from the ledger). gate-budget
# reads run_budget_exhausted() and denies every worker write once the run is spent — the hard global floor. ──
def _run_path(d):
    return os.path.join(d, "run", "budget.json")


def _append_ledger_event(d, event):
    """Append one event to ledger/events.jsonl inline (no ledger.py import — wired _lattice.py stays self-contained).
    Best-effort: a ledger-write failure must never break the operation that triggered it."""
    try:
        os.makedirs(os.path.join(d, "ledger"), exist_ok=True)
        with open(os.path.join(d, "ledger", "events.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(event, separators=(",", ":")) + "\n")
        return True
    except OSError:
        return False


def _read_ledger_events(d):
    """Read .agents/harness/ledger/events.jsonl inline (no ledger.py import — keeps the wired _lattice.py self-contained)."""
    p = os.path.join(d, "ledger", "events.jsonl")
    out = []
    try:
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    except OSError:
        pass
    return out


def run_budget_load(d):
    try:
        return json.load(open(_run_path(d), encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _parse_ts(s):
    """Parse an ISO-8601 timestamp into a datetime for ROBUST comparison (offset-aware, not string-lexicographic —
    a DST shift or a UTC-vs-offset stamp would mis-order a raw string compare). Returns None if unparseable."""
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _ts_ge(a, b):
    """a >= b as instants when both parse; falls back to string compare only if a side is unparseable."""
    pa, pb = _parse_ts(a), _parse_ts(b)
    if pa is not None and pb is not None:
        return pa >= pb
    return (a or "") >= (b or "")


def run_budget_start(d, now_iso, max_iterations=None, max_cells=None, deadline_iso=None):
    """Persist the run's budget. Rejects a VACUOUS budget (no cap is no budget) and ill-typed caps — the bound that
    bounds nothing is the illegal state the council flagged. `now_iso`/`deadline_iso` are passed in (pure paths take
    no clock). If an unexhausted budget is already active, ledgers a `budget-reset` event so a self-extending loop is
    tamper-evident in the append-only trail (Simon M1). Raises ValueError on a bad/vacuous budget."""
    for name, v in (("max_iterations", max_iterations), ("max_cells", max_cells)):
        if v is not None and (not isinstance(v, int) or isinstance(v, bool) or v < 1):
            raise ValueError(f"{name} must be a positive integer or None, got {v!r}")
    if max_iterations is None and max_cells is None and not deadline_iso:
        raise ValueError("a vacuous run budget (no max-iterations, no max-cells, no wall-clock) bounds nothing — refused")
    prior = run_budget_load(d)
    if prior is not None and not run_budget_exhausted(d, now_iso)[0]:   # overwriting a live run → tamper-evident
        _append_ledger_event(d, {"operation": "record", "actor": "orchestrator", "result": "budget-reset", "ts": now_iso,
                                 "rationale": f"a new run budget replaced an active one (was start {prior.get('start_ts')})"})
    budget = {"start_ts": now_iso, "deadline_ts": deadline_iso,
              "max_iterations": max_iterations, "max_cells": max_cells}
    os.makedirs(os.path.join(d, "run"), exist_ok=True)
    tmp = _run_path(d) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(budget, f, indent=2)
    os.replace(tmp, _run_path(d))
    return budget


def run_budget_clear(d):
    try:
        os.remove(_run_path(d))
        return True
    except OSError:
        return False


def _marker_path(d):
    return os.path.join(d, "run", "loop-active.json")


# A marked-but-unbudgeted marker older than this is treated as STALE — a crashed run that left a corpse marker,
# NOT a live forgotten-start. The legitimate arming-gap window (step 0a `mark` → step 0b `start`) is sub-second;
# this backstop means a crash can't wedge the project deny-closed forever (Charity M., 0.5.3). `stop`/`seed` clear
# it; `/harness-status` surfaces it. The arming gap is still enforced for a *live* forgotten-start (caught at once).
LOOP_TTL_S = 900


def loop_marker_set(d, now_iso, label=None):
    """Mark that an AUTONOMOUS loop (`/harness-run`) is active — the I-9 arming-gap fix. This is the mechanical
    signal, written by the loop driver as its FIRST step (step 0a, before the orchestrator arms the budget at
    step 0b), that makes the budget gap fail-CLOSED: `gate-budget` denies every write while the marker is set but
    no budget is armed. Attended single-cell work (`/harness-advance`) and manual editing never set the marker, so
    the gate leaves them free — the marker is precisely what distinguishes 'the autonomous loop is running' from
    'a human is editing'. `now_iso` is passed in (pure paths take no clock). Stamps `pid` for diagnostics."""
    os.makedirs(os.path.join(d, "run"), exist_ok=True)
    marker = {"active": True, "started_ts": now_iso, "label": label or "harness-run", "pid": os.getpid()}
    tmp = _marker_path(d) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f, indent=2)
    os.replace(tmp, _marker_path(d))
    return marker


def loop_marker_active(d):
    """True iff an autonomous loop is marked active (the marker exists and is well-formed)."""
    try:
        return bool(json.load(open(_marker_path(d), encoding="utf-8")).get("active"))
    except (OSError, ValueError):
        return False


def loop_marker_load(d):
    try:
        return json.load(open(_marker_path(d), encoding="utf-8"))
    except (OSError, ValueError):
        return None


def loop_marker_clear(d):
    try:
        os.remove(_marker_path(d))
        return True
    except OSError:
        return False


def loop_marker_age_s(d, now_iso):
    """Seconds since the marker was set, or None if no/unparseable marker or now."""
    m = loop_marker_load(d)
    if not m:
        return None
    started, now = _parse_ts(m.get("started_ts")), _parse_ts(now_iso)
    if started is None or now is None:
        return None
    return (now - started).total_seconds()


def loop_marker_stale(d, now_iso):
    """A marked loop whose marker is older than LOOP_TTL_S — a crashed run that left a corpse marker, not a live gap."""
    age = loop_marker_age_s(d, now_iso)
    return age is not None and age > LOOP_TTL_S


def loop_marker_check(d):
    """Validate `.agents/harness/run/loop-active.json`'s shape when present (mirrors run_budget_check — Scott W., 0.5.3).
    Returns a list of findings; an absent marker is fine (no loop)."""
    m = loop_marker_load(d)
    if m is None:
        return []
    if not isinstance(m, dict):
        return ["run/loop-active.json: not a JSON object"]
    findings = []
    if m.get("active") is not True:
        findings.append("run/loop-active.json: `active` must be `true` — the marker's presence means a loop is active")
    if not isinstance(m.get("started_ts"), str) or _parse_ts(m.get("started_ts")) is None:
        findings.append("run/loop-active.json: `started_ts` must be an ISO-8601 timestamp")
    for k in m:
        if k not in ("active", "started_ts", "label", "pid"):
            findings.append(f"run/loop-active.json: unknown field `{k}`")
    return findings


def loop_unbudgeted(d, now_iso=None):
    """(True, detail) iff a LIVE autonomous loop is marked active but NO run budget is armed — the arming gap, a
    denial condition rather than a silent unbounded run. A marker older than LOOP_TTL_S (given `now_iso`) is STALE
    — a crashed run's corpse, not a live loop — so it returns False and the gate stops wedging the project. The
    gate-budget enforcement reads exactly this (and passes `now_iso` so staleness applies)."""
    if loop_marker_active(d) and run_budget_load(d) is None:
        if now_iso is not None and loop_marker_stale(d, now_iso):
            return False, None
        m = loop_marker_load(d) or {}
        return True, f"loop marked active at {m.get('started_ts', '?')} ({m.get('label', 'harness-run')}) with no run budget armed"
    return False, None


def run_budget_exhausted(d, now_iso):
    """(exhausted: bool, reason|None, detail). Computed from code — no agent counting. No active run ⇒ not exhausted.
    `detail` carries the caps (max_iterations/max_cells) so an operator can see X/Y, not just the numerator (Charity)."""
    b = run_budget_load(d)
    if b is None:
        return False, None, {"active": False}
    detail = {"active": True, "start_ts": b.get("start_ts"),
              "max_iterations": b.get("max_iterations"), "max_cells": b.get("max_cells")}
    if b.get("deadline_ts"):
        detail["deadline_ts"] = b["deadline_ts"]
        if _ts_ge(now_iso, b["deadline_ts"]):                 # an absolute deadline needs no counter (offset-robust)
            return True, f"wall-clock deadline reached ({b['deadline_ts']})", detail
    evs = [e for e in _read_ledger_events(d) if e.get("ts") and _ts_ge(e["ts"], b.get("start_ts"))]
    iters = sum(1 for e in evs if e.get("operation") == "validate")
    detail["iterations"] = iters
    if b.get("max_iterations") is not None and iters >= b["max_iterations"]:
        return True, f"max-iterations reached ({iters}/{b['max_iterations']})", detail
    cells = len({e.get("cell_id") for e in evs if e.get("operation") == "validate" and e.get("result") == "pass"})
    detail["cells"] = cells
    if b.get("max_cells") is not None and cells >= b["max_cells"]:
        return True, f"max-cells reached ({cells}/{b['max_cells']})", detail
    return False, None, detail


def run_budget_check(d):
    """Validate .agents/harness/run/budget.json against run-budget.schema.json when present. Returns a list of findings."""
    b = run_budget_load(d)
    if b is None:
        return []
    findings = []
    sch = _run_budget_schema()
    props = (sch or {}).get("properties", {})
    if sch and "start_ts" not in b:
        findings.append("run/budget.json: missing required `start_ts`")
    if sch:
        for k in b:
            if k not in props:
                findings.append(f"run/budget.json: unknown field `{k}`")
    for k in ("max_iterations", "max_cells"):
        v = b.get(k)
        if v is not None and (not isinstance(v, int) or isinstance(v, bool) or v < 1):
            findings.append(f"run/budget.json: `{k}` must be a positive integer or null, got {v!r}")
    if b.get("deadline_ts") and b.get("start_ts") and _parse_ts(b["deadline_ts"]) and _parse_ts(b["start_ts"]):
        if _parse_ts(b["deadline_ts"]) < _parse_ts(b["start_ts"]):
            findings.append("run/budget.json: `deadline_ts` is before `start_ts` (the run is born exhausted)")
    if b.get("max_iterations") is None and b.get("max_cells") is None and not b.get("deadline_ts"):
        findings.append("run/budget.json: vacuous budget — no cap of any kind (bounds nothing)")
    return findings


def _run_budget_schema():
    for p in (os.path.join(_ROOT, "schemas", "run-budget.schema.json"),
              os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "schemas", "run-budget.schema.json")):
        try:
            return json.load(open(p, encoding="utf-8"))
        except (OSError, ValueError):
            continue
    return None


def advance_validity(lat, cell_id):
    """Return (ok, reasons) — may an engine pass advance this cell right now?"""
    c = find(lat, cell_id)
    if c is None:
        return False, [f"no such cell: {cell_id}"]
    reasons = []
    if c.get("blocked"):
        reasons.append("cell is blocked (budget cap or no-progress signature) — surface to the compass, do not burn tokens")
    if c["maturity"] not in ADVANCEABLE:
        reasons.append(f"maturity {c['maturity']} is not advanceable (advanceable: {sorted(ADVANCEABLE)})")
    ok, dep_reasons = ready(lat, c)
    reasons += dep_reasons
    return (not reasons, reasons)


def propagate_staleness(lat, changed_cell_id, new_hash):
    """Flip every cell that was validated against an old hash of `changed_cell_id` to `stale`. Returns flipped ids."""
    flipped = []
    for c in lat["cells"]:
        va = c.get("validated_against", {})
        if changed_cell_id in va and va[changed_cell_id] != new_hash and c["maturity"] in SETTLED:
            c["maturity"] = "stale"
            flipped.append(cid(c))
    return flipped


def transition_ok(frm, to):
    """Is the maturity transition frm→to legal (the state machine)? Same-state is a no-op (always ok)."""
    return frm == to or to in TRANSITIONS.get(frm, set())


def scaffold(d):
    """Lay the full durable tree: the nine layer dirs + signals/ + ledger/, and copy the naming schema in so the
    naming gate is self-hosting in the project. Idempotent (exist_ok). Returns the list of created/ensured paths."""
    made = []
    for sub in LAYERS + ["signals", "ledger"]:
        p = os.path.join(d, sub)
        os.makedirs(p, exist_ok=True)
        made.append(sub)
    src = os.path.join(_ROOT, "schemas", "naming.schema.json")
    dst = os.path.join(d, "naming.schema.json")
    if os.path.isfile(src):
        shutil.copyfile(src, dst)
        made.append("naming.schema.json")
    # commit-vs-ignore hygiene: the run budget + loop marker under run/ are EPHEMERAL per-run state,
    # regenerated each /harness-run — a stale committed run/budget.json or run/loop-active.json would
    # wedge a fresh clone's wired gate. The durable knowledge (lattice.json, the layer assets, signals/,
    # ledger/) IS committed. Written once; a user-customized .gitignore is left untouched.
    gi = os.path.join(d, ".gitignore")
    if not os.path.isfile(gi):
        with open(gi, "w", encoding="utf-8") as f:
            f.write("# Ephemeral per-run state (run budget + loop marker) — regenerated each /harness-run.\n"
                    "# Never commit it: a stale run/ would wedge a fresh clone's budget gate. The durable\n"
                    "# lattice (lattice.json, layer assets, signals/, ledger/) IS committed.\n"
                    "run/\n"
                    "\n"
                    "# OS / editor cruft — never belongs in committed lattice state (a `git add .agents/` magnet).\n"
                    ".DS_Store\n")
        made.append(".gitignore")
    return made


def check(lat, d=None):
    """Lightweight structural + state-machine + integrity validation of a lattice (stdlib; the full JSON-Schema
    gate is roadmap). Returns a list of findings (empty = sound). Catches the ill-typed cells raw json.load would
    let through, plus two RETROACTIVE integrity violations: a settled cell whose dependency never validated (the
    partial order violated after the fact), and — when `d` is given so assets can be resolved — a settled cell
    trusting a dependency whose on-disk content no longer matches the recorded hash (stale-but-trusted)."""
    findings = []
    seen = set()
    by_id = {cid(c): c for c in lat.get("cells", []) if all(k in c for k in ("layer", "scope", "slug"))}
    # the harness dir is `<project-root>/.agents/harness` by convention, so the project root that
    # asset_refs resolve against is its GRANDPARENT (two dirnames up), not its parent.
    root = (os.path.dirname(os.path.dirname(d.rstrip("/"))) or ".") if d else None
    # cell.schema.json is the single source when present; the module constants are the portable fallback.
    schema = _cell_schema()
    props = (schema or {}).get("properties", {})
    layers = props.get("layer", {}).get("enum", LAYERS)
    scopes = props.get("scope", {}).get("enum", SCOPES)
    maturities = props.get("maturity", {}).get("enum", MATURITIES)
    required = (schema or {}).get("required", ["layer", "scope", "slug", "maturity"])
    known_keys = set(props) if (schema and schema.get("additionalProperties") is False) else None
    for i, c in enumerate(lat.get("cells", [])):
        where = f"cell[{i}]"
        for k in required:
            if k not in c:
                findings.append(f"{where}: missing required field `{k}`")
        if known_keys is not None:                          # additionalProperties:false — a typo'd key silently loses data
            for k in c:
                if k not in known_keys:
                    findings.append(f"{where}: unknown field `{k}` (not in the cell schema — typo, or data that will be ignored)")
        # blocked_reason without blocked is a representable illegal state (Scott/CV4 band-aid; the discriminated-union
        # refactor that makes it unconstructable is ROADMAP). The reason describes a stop that isn't in effect.
        if c.get("blocked_reason") and not c.get("blocked"):
            findings.append(f"{where}: `blocked_reason` set but `blocked` is false — a stop reason on a cell that isn't stopped")
        if c.get("layer") not in layers:
            findings.append(f"{where}: layer `{c.get('layer')}` not in the closed enum")
        if c.get("scope") not in scopes:
            findings.append(f"{where}: scope `{c.get('scope')}` not in the closed enum")
        if c.get("maturity") not in maturities:
            findings.append(f"{where}: maturity `{c.get('maturity')}` not a valid state")
        slug = c.get("slug", "")
        if not slug or not all(ch.isalnum() or ch == "-" for ch in slug) or slug != slug.lower():
            findings.append(f"{where}: slug `{slug}` is not kebab-case")
        cell_id = cid(c) if all(k in c for k in ("layer", "scope", "slug")) else where
        if cell_id in seen:
            findings.append(f"{where}: duplicate cell id `{cell_id}`")
        seen.add(cell_id)
        if c.get("maturity") in SETTLED:
            # the validated-with-no-signal contradiction the signal-currency design forbids
            if not c.get("signal_refs"):
                findings.append(f"{cell_id}: maturity `{c['maturity']}` but no signal_refs — validated against nothing")
            # phantom signals: a cited signal that does not exist on disk is asserted, not earned
            # (found by the live council run against the unearned-autonomy fixture — 0.3.0)
            elif d:
                for ref in c["signal_refs"]:
                    if not os.path.isfile(ref if os.path.isabs(ref) else os.path.join(d, ref)):
                        findings.append(f"{cell_id}: cites signal `{ref}` that does not exist on disk — asserted, not earned")
            # the partial order, violated retroactively: settled atop a dependency that never validated
            for dep in c.get("depends_on", []):
                dc = by_id.get(dep)
                if dc is None:
                    findings.append(f"{cell_id}: depends on unknown cell `{dep}`")
                elif dc.get("maturity") not in SETTLED:
                    findings.append(f"{cell_id}: `{c['maturity']}` while dependency `{dep}` is `{dc.get('maturity')}` — "
                                    f"the partial order was violated retroactively (a rubric before its spec scores vibes)")
            # stale-but-trusted: the recorded validation hash no longer matches the asset on disk
            if root:
                for dep, recorded in (c.get("validated_against") or {}).items():
                    ref = (by_id.get(dep) or {}).get("asset_ref")
                    if not (recorded and ref):
                        continue
                    now = content_hash(ref if os.path.isabs(ref) else os.path.join(root, ref))
                    if now and now != recorded:
                        findings.append(f"{cell_id}: trusts `{dep}` at {recorded} but its asset now hashes {now} — "
                                        f"stale-but-trusted (the evidence predates the content; re-validate)")
    if d:                                                    # the run/ files are durable .agents/harness/ state — type-check them too
        findings += run_budget_check(d)
        findings += loop_marker_check(d)
    return findings


def seed_lattice(project):
    """A first slice: an ontology + spec foothold at task scope, plus the rubric that will verify the slice's WORK.
    Bootstrap order matters: the spec validates FIRST (against a spec-quality predicate check, not the rubric — a
    spec whose verifier is the rubric that depends on it is a circular wait, and the seed must never deadlock);
    the rubric is then authored against the validated spec, and downstream work cells bind their `verifier` to it."""
    return {
        "version": "1", "project": project, "created": "", "frontier_scope": "task",
        "cells": [
            {"layer": "ontology", "scope": "task", "slug": "domain", "maturity": "defined", "depends_on": []},
            {"layer": "spec", "scope": "task", "slug": "first-slice", "maturity": "defined",
             "depends_on": ["ontology.task.domain"]},
            {"layer": "rubric", "scope": "task", "slug": "first-slice", "maturity": "defined",
             "depends_on": ["spec.task.first-slice"]},
            {"layer": "ledger", "scope": "task", "slug": "events", "maturity": "defined",
             "depends_on": ["ontology.task.domain"]},
        ],
    }


def _demo():
    """A synthetic lattice exercising the partial order + staleness, for the selftest."""
    return {
        "version": "1", "project": "demo", "frontier_scope": "task",
        "cells": [
            {"layer": "ontology", "scope": "task", "slug": "domain", "maturity": "validated", "depends_on": []},
            {"layer": "spec", "scope": "task", "slug": "x", "maturity": "validated",
             "depends_on": ["ontology.task.domain"], "validated_against": {"ontology.task.domain": "h1"}},
            {"layer": "rubric", "scope": "task", "slug": "x", "maturity": "defined", "depends_on": ["spec.task.x"]},
            {"layer": "spec", "scope": "task", "slug": "y", "maturity": "defined", "depends_on": []},
            {"layer": "rubric", "scope": "task", "slug": "y", "maturity": "defined", "depends_on": ["spec.task.y"]},
            {"layer": "methodology", "scope": "task", "slug": "loop", "maturity": "defined",
             "depends_on": [], "verifier": "rubric.task.x"},
        ],
    }


def selftest():
    fails = []
    def expect(cond, label):
        if not cond:
            fails.append(label)
    lat = _demo()

    gaps = {cid(c) for c in scan(lat)}
    expect("rubric.task.x" in gaps and "spec.task.y" in gaps, f"scan missed open cells: {gaps}")
    expect("ontology.task.domain" not in gaps, "scan returned a validated cell as a gap")

    # rubric.task.x is ready (its spec is validated); rubric.task.y is NOT (its spec is only defined) — the partial order.
    expect(ready(lat, find(lat, "rubric.task.x"))[0], "rubric.task.x should be ready (validated spec upstream)")
    expect(not ready(lat, find(lat, "rubric.task.y"))[0], "rubric.task.y should NOT be ready (rubric-before-validated-spec)")

    # advance against an unvalidated verifier is blocked (verifier-maturity precondition).
    ok, reasons = advance_validity(lat, "methodology.task.loop")
    expect(not ok and any("verifier" in r for r in reasons), f"advance should fail on unvalidated verifier: {reasons}")

    # rank yields the ready gaps only, ordered; the rubric-before-spec cell is filtered out.
    ranked = [cid(c) for _, c, _ in rank(lat)]
    expect("rubric.task.x" in ranked, "rank dropped a ready gap")
    expect("rubric.task.y" not in ranked, "rank included a not-ready cell (dependency filter failed)")

    # block/unblock (the budget stop flag): a blocked cell falls out of rank; advance_validity refuses it; unblock restores it.
    set_blocked(lat, "rubric.task.x", True, reason="no-progress: 3 consecutive fails")
    expect("rubric.task.x" not in [cid(c) for _, c, _ in rank(lat)], "a blocked cell was still ranked")
    expect(not advance_validity(lat, "rubric.task.x")[0], "advance_validity allowed a blocked cell")
    expect(find(lat, "rubric.task.x").get("blocked_reason"), "block did not record a reason")
    set_blocked(lat, "rubric.task.x", False)
    expect("rubric.task.x" in [cid(c) for _, c, _ in rank(lat)], "unblock did not restore the cell to the ready set")
    expect("blocked_reason" not in find(lat, "rubric.task.x"), "unblock did not clear the reason")
    expect(set_blocked(lat, "no.such.cell", True) is None, "set_blocked did not return None for a missing cell")

    # the GLOBAL run bound (the council's convergent fix): exhaustion is computed from code, no agent counter.
    import tempfile
    with tempfile.TemporaryDirectory() as rb:
        rd = os.path.join(rb, ".agents/harness")
        scaffold(rd)
        nowi = "2026-06-13T12:00:00-07:00"
        expect(run_budget_exhausted(rd, nowi) == (False, None, {"active": False}), "no-run was treated as exhausted")
        run_budget_start(rd, nowi, max_iterations=2, deadline_iso="2026-06-13T12:30:00-07:00")
        expect(not run_budget_exhausted(rd, nowi)[0], "fresh run exhausted")
        with open(os.path.join(rd, "ledger", "events.jsonl"), "w") as f:   # 2 validate events since start → max-iterations
            f.write('{"operation":"validate","actor":"a","cell_id":"spec.task.x","result":"fail","ts":"2026-06-13T12:05:00-07:00"}\n')
            f.write('{"operation":"validate","actor":"a","cell_id":"spec.task.y","result":"fail","ts":"2026-06-13T12:06:00-07:00"}\n')
        ex, why, _ = run_budget_exhausted(rd, nowi)
        expect(ex and "max-iterations" in why, f"max-iterations not enforced from the ledger: {why}")
        expect(run_budget_exhausted(rd, "2026-06-13T13:00:00-07:00")[0], "past the deadline not exhausted")  # wall-clock
        expect(run_budget_exhausted(rd, nowi)[2].get("max_iterations") == 2, "detail must carry the caps for the X/Y dashboard")
        run_budget_clear(rd)
        expect(not run_budget_exhausted(rd, nowi)[0], "clear did not end the run")
        # the writer rejects the illegal states (vacuous / non-positive / non-int caps) — they can't be constructed.
        for bad in (lambda: run_budget_start(rd, nowi),                                   # vacuous
                    lambda: run_budget_start(rd, nowi, max_iterations=0),                 # < 1
                    lambda: run_budget_start(rd, nowi, max_cells=-3),
                    lambda: run_budget_start(rd, nowi, max_iterations="5")):              # not an int
            try:
                bad(); expect(False, "run_budget_start accepted an illegal budget")
            except ValueError:
                pass
        # run_budget_check catches a hand-edited illegal budget.json (deadline before start, vacuous).
        run_budget_start(rd, "2026-06-13T12:00:00-07:00", max_iterations=2)
        import json as _json
        _json.dump({"start_ts": "2026-06-13T12:00:00-07:00", "deadline_ts": "2026-06-13T11:00:00-07:00",
                    "max_iterations": 2, "max_cells": None}, open(_run_path(rd), "w"))
        expect(any("before `start_ts`" in f for f in run_budget_check(rd)), "check missed deadline-before-start")
        _json.dump({"start_ts": "2026-06-13T12:00:00-07:00", "deadline_ts": None,
                    "max_iterations": None, "max_cells": None}, open(_run_path(rd), "w"))
        expect(any("vacuous" in f for f in run_budget_check(rd)), "check missed a vacuous budget.json")
        # the budget round-trips its own schema cleanly when well-formed
        run_budget_clear(rd); run_budget_start(rd, nowi, max_iterations=3, deadline_iso="2026-06-13T13:00:00-07:00")
        expect(run_budget_check(rd) == [], f"check flagged a well-formed budget: {run_budget_check(rd)}")
        # the loop-active marker (I-9 arming gap): un-marked = not an unbudgeted loop; marked + no budget = the gap
        run_budget_clear(rd)
        expect(not loop_unbudgeted(rd)[0] and not loop_marker_active(rd), "a fresh project was treated as a marked/unbudgeted loop")
        loop_marker_set(rd, nowi, label="harness-run")
        expect(loop_marker_active(rd) and loop_unbudgeted(rd)[0], "a marked loop with no budget was not flagged unbudgeted")
        run_budget_start(rd, nowi, max_cells=8)
        expect(not loop_unbudgeted(rd)[0], "arming a budget did not clear the arming-gap state")
        run_budget_clear(rd); loop_marker_clear(rd)
        expect(not loop_marker_active(rd) and not loop_unbudgeted(rd)[0], "clearing the marker did not end the loop state")

    # staleness propagation: change ontology's hash → spec.task.x (validated against h1) flips to stale.
    flipped = propagate_staleness(lat, "ontology.task.domain", "h2")
    expect("spec.task.x" in flipped and find(lat, "spec.task.x")["maturity"] == "stale", f"staleness did not propagate: {flipped}")

    # the seed lattice is structurally sound (every cell well-typed); check() passes it and catches ill-typed cells.
    seed = seed_lattice("p")
    expect(all(c["layer"] in LAYERS and c["scope"] in SCOPES for c in seed["cells"]), "seed lattice has an ill-typed cell")
    expect(check(seed) == [], f"check() flagged a sound seed lattice: {check(seed)}")
    bad = {"cells": [{"layer": "rubrics", "scope": "task", "slug": "X", "maturity": "done"},
                     {"layer": "spec", "scope": "task", "slug": "y", "maturity": "validated"}]}  # validated, no signal
    bf = check(bad)
    expect(any("not in the closed enum" in f for f in bf), "check() missed a bad layer enum")
    expect(any("not a valid state" in f for f in bf), "check() missed a bad maturity")
    expect(any("not kebab-case" in f for f in bf), "check() missed a non-kebab slug")
    expect(any("validated against nothing" in f for f in bf), "check() missed validated-with-no-signal")

    # THE SEED MUST NEVER DEADLOCK: driving it in dependency order reaches full validation (the circular
    # spec⟲rubric verifier wait the walkthrough surfaced — spec validates first, the rubric is authored against it).
    boot = seed_lattice("boot")
    for _ in range(len(boot["cells"]) + 1):
        for c in boot["cells"]:
            if c["maturity"] in ADVANCEABLE and advance_validity(boot, cid(c))[0]:
                c["maturity"] = "validated"
                c["signal_refs"] = ["signals/x.json"]
    stuck = [cid(c) for c in boot["cells"] if c["maturity"] not in SETTLED]
    expect(not stuck, f"the seeded first slice deadlocks — permanently stuck: {stuck}")

    # retroactive partial-order violation: a settled cell atop a dependency that never validated.
    retro = {"cells": [{"layer": "spec", "scope": "task", "slug": "s", "maturity": "defined"},
                       {"layer": "rubric", "scope": "task", "slug": "s", "maturity": "validated",
                        "signal_refs": ["x"], "depends_on": ["spec.task.s"]}]}
    expect(any("violated retroactively" in f for f in check(retro)), "check() missed a retro partial-order violation")

    # stale-but-trusted: the recorded validation hash no longer matches the asset on disk (needs d to resolve).
    import tempfile
    with tempfile.TemporaryDirectory() as td2:
        hd = os.path.join(td2, ".agents/harness")
        os.makedirs(hd)
        asset = os.path.join(td2, "spec-asset.md")
        open(asset, "w").write("v2 — moved on")
        stale_lat = {"cells": [
            {"layer": "spec", "scope": "task", "slug": "s", "maturity": "validated", "signal_refs": ["x"],
             "depends_on": [], "asset_ref": "spec-asset.md"},
            {"layer": "rubric", "scope": "task", "slug": "s", "maturity": "validated", "signal_refs": ["x"],
             "depends_on": ["spec.task.s"], "validated_against": {"spec.task.s": "sha256:0ld0ld0ld0ld0ld0"}}]}
        sbf = check(stale_lat, d=hd)
        expect(any("stale-but-trusted" in f for f in sbf), f"check() missed stale-but-trusted: {sbf}")
        expect(not any("stale-but-trusted" in f for f in check(stale_lat)),
               "check() ran hash checks without d (cannot resolve assets)")
        # phantom signals (the live council's emergent find): a cited signal file must exist on disk.
        expect(any("does not exist on disk" in f for f in sbf), f"check() missed a phantom signal ref: {sbf}")
        os.makedirs(os.path.join(hd, "signals"), exist_ok=True)
        open(os.path.join(hd, "x"), "w").write("{}")          # the refs above are literally "x" — make it real
        real = check(stale_lat, d=hd)
        expect(not any("does not exist on disk" in f for f in real), f"check() flagged a real signal file: {real}")

    # CV5 — the module enums must equal cell.schema.json's (the single source); drift between the two copies is a failure.
    sch = _cell_schema()
    if sch is not None:                                       # absent only in the wired _lattice.py copy
        sp = sch["properties"]
        expect(sp["layer"]["enum"] == LAYERS, "LAYERS drifted from cell.schema.json (single-source violation)")
        expect(sp["scope"]["enum"] == SCOPES, "SCOPES drifted from cell.schema.json")
        expect(sp["maturity"]["enum"] == MATURITIES, "MATURITIES drifted from cell.schema.json")
    # the additionalProperties:false catch — a typo'd key is a finding, not silent data loss.
    typo = {"cells": [{"layer": "spec", "scope": "task", "slug": "s", "maturity": "validated",
                       "signal_refs": ["x"], "depends_on": [], "signl_refs": ["typo"]}]}
    expect(any("unknown field `signl_refs`" in f for f in check(typo)), "check() missed an off-schema (typo'd) key")
    # blocked_reason without blocked is the illegal state Scott flagged.
    orphan = {"cells": [{"layer": "spec", "scope": "task", "slug": "s", "maturity": "defined",
                         "depends_on": [], "blocked_reason": "no-progress"}]}
    expect(any("`blocked` is false" in f for f in check(orphan)), "check() missed blocked_reason-without-blocked")

    # the state machine: legal vs. illegal transitions.
    expect(transition_ok("validated", "regenerating") and transition_ok("defined", "instantiated"), "rejected a legal transition")
    expect(not transition_ok("absent", "operating") and not transition_ok("deprecated", "validated"), "accepted an illegal transition")
    # the maturity partition is total: every schema state is advanceable, settled, or explicitly terminal.
    expect(set(MATURITIES) == ADVANCEABLE | SETTLED | {"deprecated"}, "maturity enum not partitioned by the engine sets")

    # scaffold() lays the full durable tree (the CC1 fix — init was writing only lattice.json).
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        made = scaffold(td)
        for layer in LAYERS:
            expect(os.path.isdir(os.path.join(td, layer)), f"scaffold did not create layer dir {layer}/")
        expect(os.path.isdir(os.path.join(td, "signals")) and os.path.isdir(os.path.join(td, "ledger")), "scaffold missed signals/ or ledger/")
        expect("naming.schema.json" in made and os.path.isfile(os.path.join(td, "naming.schema.json")), "scaffold did not copy the naming schema")
        gi = os.path.join(td, ".gitignore")                # commit-vs-ignore hygiene: run/ + OS cruft ignored, the rest committed
        _gic = open(gi, encoding="utf-8").read() if os.path.isfile(gi) else ""
        expect("run/" in _gic and ".DS_Store" in _gic, "scaffold did not write a run/ + .DS_Store ignoring .gitignore")

    if fails:
        sys.stderr.write("lattice selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("lattice selftest: OK (scan/partial-order/verifier-maturity/rank/staleness; the state machine rejects illegal "
          "transitions; check() catches ill-typed, validated-without-signal, retro-order-violated, and "
          "stale-but-trusted cells; block/unblock drops a cell from rank; the run budget rejects vacuous/ill-typed caps "
          "+ check() validates budget.json; the I-9 loop-active marker makes a marked-but-unbudgeted loop detectable "
          "(the arming gap, fail-closed); the seed bootstraps without deadlock; scaffold lays the full tree)")
    return 0


def _dir(argv):
    return argv[argv.index("--dir") + 1] if "--dir" in argv else ".agents/harness"


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    d = _dir(argv)
    pos = [a for a in argv if not a.startswith("--") and a != d]
    if pos and pos[0] == "init":
        if os.path.isfile(os.path.join(d, "lattice.json")) and "--force" not in argv:
            print(f"{os.path.join(d, 'lattice.json')} already exists — refusing to clobber durable state. Pass --force to reseed.", file=sys.stderr)
            return 2
        os.makedirs(d, exist_ok=True)
        made = scaffold(d)                                  # the nine layer dirs + signals/ + ledger/ + the naming schema
        lat = seed_lattice(pos[1] if len(pos) > 1 else os.path.basename(os.getcwd()))
        lat["created"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
        lat["produced_by"] = os.environ.get("LATTICE_PRODUCED_BY", "harness-forge")  # producing plugin (migration anchor); a vendoring host sets LATTICE_PRODUCED_BY (e.g. dev-factory)
        save(d, lat)
        print(f"seeded {os.path.join(d, 'lattice.json')} — {len(lat['cells'])} cells + scaffold ({', '.join(made)})")
        return 0
    if pos and pos[0] == "check":
        try:
            lat = load(d)
        except OSError:
            print(f"no lattice at {d}/lattice.json", file=sys.stderr)
            return 2
        findings = check(lat, d=d)
        for f in findings:
            print(f"  [INVALID] {f}")
        print(f"\nRESULT: {'PASS' if not findings else 'FAIL'} (lattice structural check) — {len(findings)} finding(s)")
        return 0 if not findings else 1
    try:
        lat = load(d)
    except OSError:
        print(f"no lattice at {d}/lattice.json — run `lattice.py init <project> --dir {d}` first", file=sys.stderr)
        return 2
    if pos and pos[0] == "scan":
        for c in scan(lat):
            print(f"  {c['maturity']:12} {cid(c)}")
        print(f"\n{len(scan(lat))} open/stale cell(s) at frontier scope {lat.get('frontier_scope','task')}")
        return 0
    if pos and pos[0] == "rank":
        ranked = rank(lat)
        for p, c, _ in ranked:
            print(f"  {p:7.3f}  {cid(c)}  ({c['maturity']})")
        print(f"\n{len(ranked)} ready, ranked cell(s) — priority ≈ (risk × unlock) ÷ probe-cost")
        return 0
    if len(pos) >= 2 and pos[0] == "validity":
        ok, reasons = advance_validity(lat, pos[1])
        print(f"{'CAN ADVANCE' if ok else 'BLOCKED'}: {pos[1]}")
        for r in reasons:
            print(f"  - {r}")
        return 0 if ok else 1
    if len(pos) >= 3 and pos[0] == "stale":
        flipped = propagate_staleness(lat, pos[1], pos[2])
        save(d, lat)
        print(f"propagate-staleness from {pos[1]}: flipped {len(flipped)} cell(s) → stale: {flipped}")
        return 0
    if len(pos) >= 2 and pos[0] in ("block", "unblock"):
        reason = argv[argv.index("--reason") + 1] if "--reason" in argv else (pos[2] if len(pos) >= 3 else "")
        c = set_blocked(lat, pos[1], blocked=(pos[0] == "block"), reason=reason)
        if c is None:
            print(f"no such cell: {pos[1]}", file=sys.stderr)
            return 2
        save(d, lat)
        # ledger the decision (Charity/CV2): a block/unblock is the loop's most consequential act and must leave a
        # trace — it is a Bash subprocess, so neither ledger.append nor the Write-only emit-ledger hook would see it.
        _append_ledger_event(d, {"operation": "record", "actor": "orchestrator", "cell_id": pos[1],
                                 "result": pos[0] + "ed", "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                                 "rationale": (f"blocked: {reason}" if pos[0] == "block" else "unblocked — back in the ready set")})
        if pos[0] == "block":
            print(f"blocked {pos[1]}" + (f" — {reason}" if reason else "") + " (falls out of rank/advance until unblocked; ledgered)")
        else:
            print(f"unblocked {pos[1]} — back in the ready set (ledgered)")
        return 0
    print(__doc__.split("Usage:")[1].split("Stdlib")[0].strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
