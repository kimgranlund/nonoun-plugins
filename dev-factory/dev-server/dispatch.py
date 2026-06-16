#!/usr/bin/env python3
"""dispatch.py — the dispatcher: provision, launch, supervise, validate (the engine's outer mechanics).

The heartbeat selects (compass) and this dispatches: it provisions a hermetic git worktree, sets
`claimed` (single-writer, so the classic claim race is designed out, not mitigated — §7.2), launches a
worker through a `DispatchAdapter`, supervises its lease, then runs the critic (the validation path) and
drives the ticket to `done`. A dead worker is recovered by lease expiry, not by reconciling competing
claims (§15).

The `DispatchAdapter` is the integration seam (§9.2, OD-003): the kernel defines the contract; the
concrete binding to a headless agent runtime is pinned against current product docs. This module ships
the deterministic **MockAdapter** (a real subprocess, no live model) so the whole loop is CI-verifiable;
the live `headless-claude` binding lands as a sibling adapter once its invocation is confirmed.

Stdlib only; Python 3.8+. (Part of dev-server; not a plugin.)
"""
import datetime
import json
import os
import shutil
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import api as _api          # noqa: E402  (single-writer ops)
sys.path.insert(0, _api._store._KERNEL_BIN)
import lattice as _lat      # noqa: E402
import lifecycle as _lc     # noqa: E402
import ledger as _led       # noqa: E402
import execplan as _ep      # noqa: E402  (the deterministic execution-plan assembly)

LEASE_TTL_S = 900           # a worker lease; exceeded → the worker is presumed dead (reconcile_leases)
MAX_WORKER_ATTEMPTS = 3     # consecutive worker failures on one cell before it blocks (a transient hiccup retries)


def _consecutive_fails(d, tid):
    """The current failure STREAK for a ticket — count `activity-fail` events since its last `activity-complete`
    (any success resets the streak). The retry budget: a transient failure retries; a persistently-stuck cell
    blocks. Read from the append-only ledger, so it survives a crash + needs no schema change to the ticket."""
    n = 0
    for e in _led.read(d):
        if (e.get("subject") or {}).get("ticket") != tid:
            continue
        ev = e.get("event")
        if ev == "activity-fail":
            n += 1
        elif ev == "activity-complete":
            n = 0
    return n

# Roster mapping: which worker role advances a cell of a given layer (the critic is always cell-validator —
# the separate skeptic). The execution plan decides HOW the unit runs; this decides WHO. A regenerating cell
# is advanced by the spec-regenerator. Defaults to the generic cell-advancer.
ROSTER = {
    "ontology": "lattice-architect", "spec": "spec-architect", "rubric": "rubric-architect",
    "pattern": "pattern-distiller", "policy": "cell-advancer", "capability": "cell-advancer",
    "methodology": "cell-advancer", "protocol": "cell-advancer", "ledger": "cell-advancer",
}
# A single-pass plan for instances with no kit policy bound (the irreducible default).
DEFAULT_PLAN = {"orchestration_shape": "single-pass", "loop_strategy": "single",
                "context_plan": {"retrieval": "minimal"}, "effort": {"model_tier": "small", "reasoning_effort": "low", "max_iterations": 2},
                "delegation": {"mode": "none", "max_depth": 0}}


def agent_for(cell, to_mat):
    if to_mat == "regenerating":
        return "spec-regenerator"
    return ROSTER.get((cell or {}).get("layer"), "cell-advancer")


def resolve_policy(d, kit_dir=None):
    """The kit's DispatchPolicy (the family bound to this instance). Resolved from DEV_FACTORY_KIT or a passed
    kit dir; a permissive single-pass default if none is bound."""
    kit_dir = kit_dir or os.environ.get("DEV_FACTORY_KIT")
    if kit_dir:
        try:
            kit = json.load(open(os.path.join(kit_dir, "kit.json"), encoding="utf-8"))
            return _ep.load_policy(os.path.join(kit_dir, kit.get("dispatch_policy", "dispatch-policy.json")))
        except (OSError, ValueError, KeyError):
            pass
    return {"family": "default", "rules": [], "default": DEFAULT_PLAN}


def _now():
    return datetime.datetime.now().astimezone()


def _iso(dt):
    return dt.isoformat(timespec="seconds")


# ─────────────────────────────────── hermetic worktrees ───────────────────────────────────

def provision_worktree(d, cell_id, worker_id, repo_root=None):
    """A hermetic workspace for one unit. A real git worktree when the instance lives in a repo (so
    parallel workers on different cells never collide); a plain isolated dir otherwise. Returns the path."""
    wt = os.path.join(d, "run", "worktrees", f"{cell_id}--{worker_id}")
    os.makedirs(os.path.dirname(wt), exist_ok=True)
    repo = repo_root or os.path.dirname(os.path.dirname(d.rstrip("/")))  # the .agents/<plugin> grandparent
    if os.path.isdir(os.path.join(repo, ".git")):
        try:
            subprocess.run(["git", "-C", repo, "worktree", "add", "--detach", wt, "HEAD"],
                           capture_output=True, check=True)
            return wt, True
        except (subprocess.CalledProcessError, OSError):
            pass
    os.makedirs(wt, exist_ok=True)   # fallback: a plain isolated dir
    return wt, False


def teardown_worktree(d, wt, repo_root=None):
    repo = repo_root or os.path.dirname(os.path.dirname(d.rstrip("/")))
    if os.path.isdir(os.path.join(repo, ".git")):
        subprocess.run(["git", "-C", repo, "worktree", "remove", "--force", wt], capture_output=True)
    shutil.rmtree(wt, ignore_errors=True)


# ─────────────────────────────────── the DispatchAdapter contract ───────────────────────────────────

class DispatchAdapter:
    """dispatch(unit) -> result. Runtime guarantees (§9.2): runs in the hermetic worktree, gates active,
    emits events the dispatcher tees into the ledger, terminates on a stop condition. Subclasses bind a
    concrete runtime."""
    name = "abstract"

    def dispatch(self, d, unit):
        raise NotImplementedError


def _authoring_for(cell, kit_dir=None):
    """The bound kit's AUTHORING declaration for this cell's layer, or None (→ single-`.md` authoring). A kit
    declares multi-file CODE authoring per layer via a top-level `authoring` list, so dev-kit-corpus (doc cells)
    stays single-file while dev-kit-app (capability code) opts into a multi-file directory. The kernel/dispatch
    stay generic — the kit names the shape; check-kit-conform ignores the (kit-local) `authoring` field."""
    kit_dir = kit_dir or os.environ.get("DEV_FACTORY_KIT")
    if not kit_dir:
        return None
    try:
        kit = json.load(open(os.path.join(kit_dir, "kit.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return None
    for a in kit.get("authoring", []):
        if a.get("layer") == cell["layer"]:
            return a
    return None


def _asset_rel(layer, slug, authoring):
    """A cell's asset path relative to the instance: a DIRECTORY for multi-file authoring, else {layer}/{slug}.md."""
    if authoring and authoring.get("mode") == "multi-file":
        return os.path.join(layer, slug)
    return os.path.join(layer, f"{slug}.md")


class MockAdapter(DispatchAdapter):
    """Deterministic runtime for CI/Crawl→Walk: a real subprocess that plays the worker role — it authors
    (or refines) the target cell's asset, writes nothing to a protected path, and reports metrics. No live
    model, so the whole dispatch loop is reproducible and gate-bounded."""
    name = "mock"

    def dispatch(self, d, unit):
        layer, slug = unit["layer"], unit["slug"]
        authoring = _authoring_for({"layer": layer, "slug": slug})
        if authoring and authoring.get("mode") == "multi-file":
            # multi-file CODE authoring (the worker's GENERATOR side): author source files into the cell's dir.
            # The per-cell verify.mjs is the CRITIC's gate — authored by the planner, write-protected from the
            # worker — so the mock never writes it (a real cold-start seeds the real harness; a trivial stub here).
            asset_rel = os.path.join(layer, slug)
            asset_abs = os.path.join(d, asset_rel)
            os.makedirs(asset_abs, exist_ok=True)
            src = os.path.join(asset_abs, "index.mjs")
            if not os.path.exists(src):
                open(src, "w", encoding="utf-8").write(
                    f"// {layer}.{unit['scope']}.{slug} — authored by the {self.name} worker for {unit['ticket']}\n"
                    "export const ready = true;\n")
            return {"ok": True, "asset_ref": asset_rel, "metrics": {"tokens": 9000, "iterations": 1}}
        asset_dir = os.path.join(d, layer)
        os.makedirs(asset_dir, exist_ok=True)
        asset_rel = os.path.join(layer, f"{slug}.md")
        asset_abs = os.path.join(d, asset_rel)
        existing = open(asset_abs, encoding="utf-8", errors="replace").read() if os.path.exists(asset_abs) else ""
        # a STRUCTURED asset (JSON / a ```json block) is already authored — confirm it, don't clobber it
        # (so a kit's structured-asset verifier still validates after the worker runs).
        if existing.lstrip()[:1] == "{" or "```json" in existing:
            return {"ok": True, "asset_ref": asset_rel, "metrics": {"tokens": 3000, "iterations": 1}}
        # else the worker authors prose (rewritable side — gate-verifier permits spec/ etc.)
        body = f"# {layer}.{unit['scope']}.{slug}\n\nAuthored by the {self.name} worker for {unit['ticket']}.\n"
        with open(asset_abs, "a" if existing else "w", encoding="utf-8") as f:
            f.write(body)
        return {"ok": True, "asset_ref": asset_rel, "metrics": {"tokens": 8000, "iterations": 1}}


def wire_gates(worktree, kernel_bin):
    """Make the immutable boundary ACTIVE inside the worker's worktree: write a .claude/settings.json that
    runs the dev-kernel gates as PreToolUse(Write|Edit) hooks. A worker that tries to forge a signal or
    rewrite the lattice/ledger is denied in-process (gate-verifier emits permissionDecision: deny). This is
    the §9.2 'gates active inside the worktree' guarantee — wired per dispatch, never bundled."""
    cfg_dir = os.path.join(worktree, ".claude")
    os.makedirs(cfg_dir, exist_ok=True)
    settings = {"hooks": {"PreToolUse": [
        {"matcher": "Write|Edit|MultiEdit", "hooks": [
            {"type": "command", "command": f"{os.path.join(kernel_bin, 'gate-verifier')} --hook"},
            {"type": "command", "command": f"{os.path.join(kernel_bin, 'gate-ledger')} --hook"},
            {"type": "command", "command": f"{os.path.join(kernel_bin, 'gate-naming')} --hook"},
        ]},
    ]}}
    json.dump(settings, open(os.path.join(cfg_dir, "settings.json"), "w"), indent=2)
    return os.path.join(cfg_dir, "settings.json")


class HeadlessClaudeAdapter(DispatchAdapter):
    """The live OD-003 binding: launches headless Claude Code (`claude -p`) as a subprocess in the hermetic
    worktree, gates wired active, streaming tool events into the ledger, bounded by the unit's budget.

    Pinned against the June-2026 Claude Code docs (cli-reference / headless): `-p` headless; `--add-dir`
    the worktree; `--allowedTools`; `--permission-mode acceptEdits`; `--max-turns` (iterations) and
    `--max-budget-usd` (dollars) as hard stops; `--output-format stream-json` for the teeable event log;
    `--settings` to load the gate hooks. Not exercised in CI (it spends real tokens); the MockAdapter is
    the deterministic stand-in. Requires the `claude` CLI on PATH.
    """
    name = "headless-claude"

    def __init__(self, model=None, allowed_tools="Read,Edit,Write,Bash,Glob,Grep"):
        self.model = model
        self.allowed_tools = allowed_tools

    def _allowed_tools(self, unit):
        """The worker's tool scope. A `team` delegation plan adds Task so the orchestrator can SPAWN the planned
        sub-agent team (orchestrator-workers, to max_depth); a non-delegating plan keeps the single-worker scope."""
        if ((unit.get("plan") or {}).get("delegation") or {}).get("mode") == "team":
            return self.allowed_tools + ",Task"
        return self.allowed_tools

    def _prompt(self, d, unit, project_root):
        tt = unit.get("transition") or {}
        # Fold the operator's recent steering guidance (the 5s channel) into THIS dispatch. A running one-shot
        # `claude -p` worker cannot receive mid-flight input, so guidance reaches the NEXT worker dispatched —
        # which is this one. Latest-last; advisory context, never a substitute for the cell's acceptance.
        guide = _api.recent_guidance(d, n=5)
        gtxt = ("\n\nRecent operator guidance (advisory context, fold in where relevant; latest last):\n"
                + "\n".join(f"- {g}" for g in guide)) if guide else ""

        # multi-file CODE authoring (a kit's capability/code layer): author N source files to a directory, graded
        # by the cell's per-cell critic harness verify.mjs — the worker may READ its contract but CANNOT write it.
        authoring = _authoring_for({"layer": unit["layer"], "slug": unit["slug"]})
        if authoring and authoring.get("mode") == "multi-file":
            dir_rel = os.path.relpath(os.path.join(d, unit["layer"], unit["slug"]), project_root)
            plan = unit.get("plan") or {}
            dele = plan.get("delegation") or {}
            # the INTEGRATOR (the SHIP cell) depends on sibling capability cells — it must compose them into a
            # RUNNABLE app (a real UI), not just an API barrel. Detect it and steer the worker accordingly.
            _cell = _lat.find(_lat.load(d), f"{unit['layer']}.{unit['scope']}.{unit['slug']}") or {}
            is_integrator = unit["layer"] == "capability" and any(
                str(dep).startswith("capability.") for dep in (_cell.get("depends_on") or []))
            integ = ""
            if is_integrator:
                integ = (" You are the INTEGRATOR — compose the sibling capabilities into a RUNNABLE web app that "
                         "actually PLAYS in a browser, not just an API barrel. Author (a) `index.mjs` re-exporting "
                         "every capability's API; (b) `main.mjs` that imports the capabilities and EXPORTS "
                         "`mount(root)` — building an INTERACTIVE UI into `root` (render the state to the DOM, wire "
                         "up user input/clicks, update on change); (c) `index.html` with a `<div id=\"app\">` and a "
                         "`<script type=\"module\" src=\"./main.mjs\">` that calls `mount(document.getElementById('app'))`. "
                         "Include the CSS (inline or a styles.css linked from index.html) so it looks like a real app.")
            team = ""
            if dele.get("mode") == "team":   # the planned orchestrator-workers team (execplan) — execute it, don't just record it
                par = (plan.get("effort") or {}).get("parallelism", 1)
                team = (f" You are the ORCHESTRATOR ({plan.get('orchestration_shape', 'orchestrator-workers')} / "
                        f"{plan.get('loop_strategy', 'tracer-bullet')}): decompose this capability into independent sub-tasks "
                        f"and DELEGATE each to a sub-agent via the Task tool — to a maximum delegation depth of "
                        f"{dele.get('max_depth', 1)}, up to {par} in parallel. Each sub-agent authors part of the source; you "
                        f"integrate them and ensure the harness passes. Use the team only where it earns its keep.")
            return (f"You are a dev-factory worker building ONE capability of a shippable app: "
                    f"{unit['layer']}.{unit['scope']}.{unit['slug']}. Author its source as multiple files under "
                    f"`{dir_rel}/` to INDUSTRIAL standards: clear module boundaries, named exports, descriptive "
                    f"naming, proper levels of abstraction, no dead code. Put the testable LOGIC in pure ES modules "
                    f"the harness can import headlessly; keep rendering/DOM/canvas in a thin shell. "
                    f"REQUIRED: author an `{dir_rel}/index.mjs` ENTRY POINT that re-exports the capability's full "
                    f"public API (a barrel, e.g. `export * from './foo.mjs';`) — the critic harness imports the API "
                    f"from `./index.mjs`, so that file MUST exist and surface every declared export no matter how you "
                    f"split the internals. It MUST pass its critic harness `{dir_rel}/verify.mjs` — READ it for the "
                    f"exact contract, but you CANNOT write it (it is the critic's gate; your write is denied).{integ}{team} "
                    f"Do NOT touch .agents/dev-factory/signals/, the ledger, rubric/, lattice.json, or any verify.mjs. "
                    f"Produce the source files INCLUDING index.mjs.{gtxt}")

        asset_abs = os.path.join(d, unit["layer"], f"{unit['slug']}.md")
        rel = os.path.relpath(asset_abs, project_root)             # the asset's path FROM the worker's cwd (project root)
        cur = ("\n\nCurrent asset:\n" + open(asset_abs, encoding="utf-8").read()[:4000]) if os.path.exists(asset_abs) else ""
        fmt = ""
        if unit["layer"] == "spec":
            fmt = (f' Author it as a fenced ```json block declaring: "title", "cell" ("{unit["layer"]}.{unit["scope"]}.{unit["slug"]}"), '
                   '"acceptance_criteria" (a list of {"id", and EITHER "check": an executable assertion OR "rubric_cell"}), '
                   '"non_goals" (a non-empty list), and "binds_rubric" (the bound rubric cell id). Zero prose-only criteria.')
        return (f"You are a dev-factory worker advancing exactly one lattice cell: "
                f"{unit['layer']}.{unit['scope']}.{unit['slug']} (transition {tt.get('from')} -> {tt.get('to')}). "
                f"Write its asset to the file `{rel}` (relative to your working directory).{fmt} "
                f"Do NOT touch .agents/dev-factory/signals/, the ledger, rubric/, or lattice.json — those are "
                f"protected and your write will be denied. Produce ONLY the asset.{cur}{gtxt}")

    def dispatch(self, d, unit):
        if shutil.which("claude") is None:
            return {"ok": False, "error": "the `claude` CLI is not on PATH", "metrics": {}}
        # the worker runs from the PROJECT ROOT so the asset lands in the instance the critic validates,
        # and the gates' project-relative protected globs (.agents/dev-factory/…) match the worker's writes.
        project_root = os.path.dirname(os.path.dirname(d.rstrip("/")))
        settings = wire_gates(unit["worktree"], _api._store._KERNEL_BIN)
        budget = unit.get("budget") or {}
        effort = (unit.get("plan") or {}).get("effort") or {}          # the assembled execution plan's effort ladder
        max_turns = effort.get("max_iterations") or budget.get("iterations", 10)
        model = self.model or {"small": "haiku", "mid": "sonnet", "large": "opus"}.get(effort.get("model_tier"))
        # DF-4: the kit's bin/ holds the real meta-verifiers (rubric-check / spec-quality-check / doc-check) the
        # worker must RUN, not eyeball — but it lives in the plugin source, outside project_root. Grant read
        # access so an agent can locate + execute its gate instead of self-attesting (the generator/critic split
        # the kernel exists to enforce). The worker reads `${DEV_FACTORY_KIT}/bin/…`; project writes still land
        # in the instance (only the asset dir is writable; the kit is read-only here).
        kit_dir = os.environ.get("DEV_FACTORY_KIT")
        kit_add = ["--add-dir", os.path.abspath(kit_dir)] if kit_dir and os.path.isdir(kit_dir) else []
        cmd = ["claude", "-p", self._prompt(d, unit, project_root),
               "--add-dir", project_root,                        # the project (incl. the instance) the worker reads/writes
               *kit_add,                                         # the bound kit (its bin/ verifiers), read-only — DF-4
               "--allowedTools", self._allowed_tools(unit),
               "--permission-mode", "acceptEdits",
               "--max-turns", str(max_turns),
               "--output-format", "stream-json", "--verbose",
               "--settings", settings]
        if budget.get("dollars"):
            cmd += ["--max-budget-usd", str(budget["dollars"])]
        if model:
            cmd += ["--model", model]
        try:
            proc = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True,
                                  timeout=budget.get("wallclock_seconds", 600))
        except (OSError, subprocess.SubprocessError) as e:
            return {"ok": False, "error": str(e), "metrics": {}}
        cost, tokens = None, None
        for line in (proc.stdout or "").splitlines():       # tee the stream-json events into the ledger
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            et = ev.get("type")
            if et in ("tool_use", "tool_result", "assistant"):
                _led.append(d, "activity-start" if et == "tool_use" else "handoff",
                            {"kind": "agent", "id": "headless-claude"}, {"ticket": unit["ticket"], "cell": unit["target_cell"]},
                            f"{et}: {ev.get('tool_name', '')}".strip()[:200] or et)
            if et == "result":
                cost = ev.get("cost_usd")
        # Success is "the worker PRODUCED an artifact", NOT "claude exited 0". A real authoring run very often
        # exits non-zero (it hits --max-turns, or errors late AFTER writing a valid asset) — gating on the exit
        # code wrongly marks that a failure and blocks the cell, even though the artifact is on disk and the REAL
        # gate (validate.py running the cell's verifier) would pass it. The verdict belongs to the external critic,
        # not the worker's process code — so `ok` means "an asset exists to validate"; the exit code is advisory
        # metrics. (A crash that writes nothing → no asset → correctly failed.) Authoring-aware: a multi-file
        # capability produces a DIRECTORY of source (anything but its critic harness), a doc/spec a single `.md`.
        authoring = _authoring_for({"layer": unit["layer"], "slug": unit["slug"]})
        if authoring and authoring.get("mode") == "multi-file":
            asset_rel = os.path.join(unit["layer"], unit["slug"])                       # a source DIRECTORY
            asset_abs = os.path.join(d, asset_rel)
            produced = os.path.isdir(asset_abs) and any(
                f != "verify.mjs" and not f.startswith(".") for f in os.listdir(asset_abs))
        else:
            asset_rel = os.path.join(unit["layer"], f"{unit['slug']}.md")
            asset_abs = os.path.join(d, asset_rel)
            produced = os.path.exists(asset_abs) and os.path.getsize(asset_abs) > 0
        err = None if produced else f"no artifact (claude exited {proc.returncode}, asset {asset_rel} absent/empty)"
        return {"ok": produced, "asset_ref": asset_rel, "error": err,
                "metrics": {"cost_usd": cost, "tokens": tokens, "exit": proc.returncode}}


def resolve_adapter(name=None, model=None):
    """Select the dispatch adapter the server's heartbeat runs. `DEV_FACTORY_ADAPTER=headless` picks the LIVE
    `claude -p` worker (real tokens, gated on the armed run budget + the per-cell gates); the default `mock` is
    deterministic + free. Default mock so a Walk loop NEVER spends tokens unless the operator explicitly opts in."""
    name = (name or os.environ.get("DEV_FACTORY_ADAPTER") or "mock").lower()
    if name == "headless":
        return HeadlessClaudeAdapter(model=model)
    return MockAdapter()


def adapter_name():
    """The adapter the server would dispatch with — surfaced to the dashboard so the operator knows whether a run
    spends real tokens (`headless`) or is the free mock loop (`mock`)."""
    return "headless" if (os.environ.get("DEV_FACTORY_ADAPTER") or "mock").lower() == "headless" else "mock"


def _verifier_for(unit):
    """The asset-exists default verifier (exit 0 iff the worker produced the artifact) — used when no kit is
    bound. A kit's validation adapter supplies the real verifier; see _kit_verifier."""
    if unit.get("verifier"):
        return unit["verifier"]
    asset_abs = os.path.join(unit["dir"], unit["layer"], f"{unit['slug']}.md")
    return ["python3", "-c", f"import os,sys; sys.exit(0 if os.path.exists({asset_abs!r}) else 1)"]


def _kit_verifier(d, cell, unit, kit_dir=None):
    """Resolve the bound kit's validation-adapter verifier for this cell's layer, with {asset}/{worktree}/
    {cell}/${CLAUDE_PLUGIN_ROOT} substituted. None when no kit is bound (DEV_FACTORY_KIT unset) or no
    adapter matches the layer — the dispatcher then falls back to the asset-exists default. This is what
    makes 'validated' MEAN the family's real rubric (e.g. spec-quality-check), not just 'a file exists'."""
    kit_dir = kit_dir or os.environ.get("DEV_FACTORY_KIT")
    if not kit_dir:
        return None
    try:
        kit = json.load(open(os.path.join(kit_dir, "kit.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return None
    asset = os.path.join(d, cell.get("asset_ref") or os.path.join(cell["layer"], f"{cell['slug']}.md"))
    for a in kit.get("adapters", []):
        if a.get("kind") == "validation" and (a.get("target") or {}).get("layer") == cell["layer"]:
            return [tok.replace("${CLAUDE_PLUGIN_ROOT}", kit_dir).replace("{asset}", asset)
                    .replace("{worktree}", unit.get("worktree", "")).replace("{cell}", _lat.cid(cell))
                    for tok in a.get("verifier", [])]
    return None


# ─────────────────────────────────── the dispatch loop ───────────────────────────────────

def _activity_kind(to_mat):
    return {"defined": "define", "instantiated": "create", "validated": "validate",
            "regenerating": "regenerate", "operating": "author"}.get(to_mat, "author")


def dispatch_unit(d, ticket, adapter, actor, tier=1, repo_root=None, auto_validate=True, policy=None):
    """Drive one ticket active→done. ASSEMBLE the execution plan from the kit's dispatch policy (execplan),
    pick the worker by roster, provision a worktree, claim (single-writer), run the worker, emit the activity
    span (the agent/activity lens), then let the critic validate. Returns (ok, ticket, msg). At Tier 1 a human
    reviews at in-review; Tier 2+ runs to done unattended."""
    tid = ticket["id"]
    cell = _lat.find(_lat.load(d), ticket["target_cell"])
    if cell is None:
        return False, ticket, f"target_cell {ticket['target_cell']} missing"
    to_mat = ticket.get("target_transition", {}).get("to")
    policy = policy if policy is not None else resolve_policy(d)
    plan, plan_src = _ep.plan_for(policy, ticket, cell, tier)     # HOW the unit runs — deterministic policy
    agent = agent_for(cell, to_mat)                              # WHO advances it — roster
    worker_id = _led.ulid("wrk-")
    act_id = _led.ulid("act-")
    wt, hermetic = provision_worktree(d, ticket["target_cell"], worker_id, repo_root)
    unit = {"ticket": tid, "target_cell": ticket["target_cell"], "layer": cell["layer"],
            "scope": cell["scope"], "slug": cell["slug"], "worktree": wt, "dir": d,
            "transition": ticket.get("target_transition"), "budget": ticket.get("budget"),
            "plan": plan, "agent": agent, "activity": act_id}

    # claimed (single-writer) + the lease
    ok, ticket, msg = _api.transition_ticket(d, tid, "claimed", actor)
    if not ok:
        teardown_worktree(d, wt, repo_root)
        return False, ticket, f"dispatch: {msg}"
    ticket["claim"] = {"worker_id": worker_id, "worktree": wt, "claimed_at": _iso(_now()),
                       "lease_expiry": _iso(_now() + datetime.timedelta(seconds=LEASE_TTL_S))}
    _lc.save_ticket(d, ticket)
    _eff = plan.get("effort") or {}
    _dele = plan.get("delegation") or {}
    _led.append(d, "dispatch", {"kind": "server", "id": "dispatcher"}, {"ticket": tid, "cell": ticket["target_cell"]},
                f"dispatched {agent} as {plan['orchestration_shape']}/{plan['loop_strategy']} "
                f"({plan_src}) in {'hermetic worktree' if hermetic else 'isolated dir'}",
                metrics={"hermetic": hermetic, "plan_source": plan_src})
    # the activity span begins — the agent/activity lens + the monitor materialize from these ledger events. The
    # delegation DEPTH is the plan's (the planned orchestrator-workers team), and the model tier + effort travel
    # with the span so token spend can be attributed per model + effort downstream.
    _led.append(d, "activity-start", {"kind": "agent", "id": agent}, {"ticket": tid, "cell": ticket["target_cell"]},
                f"{agent} {_activity_kind(to_mat)} {ticket['target_cell']}",
                metrics={"activity": act_id, "agent": agent, "kind": _activity_kind(to_mat),
                         "orchestration_shape": plan["orchestration_shape"], "loop_strategy": plan["loop_strategy"],
                         "delegation_mode": _dele.get("mode", "none"), "depth": _dele.get("max_depth", 0),
                         "parallelism": _eff.get("parallelism", 1), "model_tier": _eff.get("model_tier"),
                         "reasoning_effort": _eff.get("reasoning_effort"), "worktree": wt})

    # worker starts → authors the asset
    _api.transition_ticket(d, tid, "in-progress", actor)
    result = adapter.dispatch(d, unit)
    if not result.get("ok"):
        _led.append(d, "activity-fail", {"kind": "agent", "id": agent}, {"ticket": tid, "cell": ticket["target_cell"]},
                    f"{agent} failed: {result.get('error', 'no artifact')}", metrics={"activity": act_id})
        # RETRY, don't dead-end: most worker failures are transient (a flaky tool call, a `claude` that errored
        # late, an operator interruption). Returning the ticket to `active` lets the next tick re-dispatch it; only
        # after MAX_WORKER_ATTEMPTS consecutive failures (a genuinely stuck cell) does it `block` and drop out of
        # rank. Without this a single hiccup wedged the whole build behind one cell, needing a manual reopen — the
        # opposite of an autonomous loop. The streak resets on any success; the global run budget still bounds total
        # dispatches, so retries can't run away.
        teardown_worktree(d, wt, repo_root)
        fails = _consecutive_fails(d, tid)
        if fails < MAX_WORKER_ATTEMPTS:
            _api.transition_ticket(d, tid, "active", actor,
                                   reason=f"worker failed (attempt {fails}/{MAX_WORKER_ATTEMPTS}) — retrying next tick")
            _api._store.rebuild(d)
            return False, _api.get_ticket(d, tid), f"worker failed; retrying ({fails}/{MAX_WORKER_ATTEMPTS})"
        _api.transition_ticket(d, tid, "blocked", actor,
                               reason=f"worker failed {fails}× consecutively — blocked (retries exhausted)")
        _api._store.rebuild(d)
        return False, _api.get_ticket(d, tid), "worker did not complete — blocked after retries"
    # the server records the authored asset on the cell (workers cannot write lattice.json)
    _api.seed_cell(d, cell["layer"], cell["scope"], cell["slug"], maturity=cell["maturity"],
                   asset_ref=result.get("asset_ref"), depends_on=cell.get("depends_on", []),
                   signal_refs=cell.get("signal_refs", []))
    _api.transition_ticket(d, tid, "in-review", actor)
    # carry the model tier + effort with the spend metrics so token burn can be charted per model + effort
    _spend = {"model_tier": _eff.get("model_tier"), "reasoning_effort": _eff.get("reasoning_effort"),
              **(result.get("metrics") or {})}
    _led.append(d, "activity-complete", {"kind": "agent", "id": agent}, {"ticket": tid, "cell": ticket["target_cell"]},
                f"{agent} produced the artifact", metrics={"activity": act_id, "budget_fraction": 1.0, **_spend})

    if not auto_validate:
        teardown_worktree(d, wt, repo_root)
        _api._store.rebuild(d)
        return True, _api.get_ticket(d, tid), f"in-review (Tier {tier}: awaiting human review)"

    # critic validates (or authoring advance) → done. The kit's validation adapter supplies the verifier;
    # the asset-exists default applies when no kit is bound.
    verifier = (_kit_verifier(d, cell, unit) or _verifier_for(unit)) if to_mat in _lc.SIGNAL_BEARING else None
    ok, ticket, msg = _api.transition_ticket(d, tid, "done", actor, verifier=verifier)
    teardown_worktree(d, wt, repo_root)
    if ok:
        t = _api.get_ticket(d, tid)
        t["claim"] = None
        _lc.save_ticket(d, t)
        _led.append(d, "signal", {"kind": "server", "id": "dispatcher"}, {"ticket": tid, "cell": ticket["target_cell"]},
                    "probe cost recorded", metrics=result.get("metrics", {}))
    _api._store.rebuild(d)
    return ok, ticket, msg


# ─────────────────────────────────── crash recovery (lease reconciliation) ───────────────────────────────────

def reconcile_leases(d, now=None):
    """Expire dead workers: a claimed/in-progress ticket whose lease has passed returns to `active`
    (retry, attempts++) or `blocked` if attempts are exhausted. Idempotent — runs each tick (§8.1, §15)."""
    now = now or _now()
    reclaimed = []
    for t in _api.list_tickets(d):
        if t.get("state") not in ("claimed", "in-progress"):
            continue
        full = _api.get_ticket(d, t["id"])
        claim = full.get("claim") or {}
        exp = claim.get("lease_expiry")
        if not exp:
            continue
        try:
            dead = datetime.datetime.fromisoformat(exp) < now
        except ValueError:
            dead = False
        if dead:
            full["claim"] = None
            _lc.save_ticket(d, full)
            _api.transition_ticket(d, t["id"], "active", {"kind": "server", "id": "lease-reconciler"},
                                   reason=f"lease expired ({exp}); worker presumed dead — returned to active")
            reclaimed.append(t["id"])
    return reclaimed


def selftest():
    import tempfile
    fails = []
    def expect(c, m):
        if not c:
            fails.append(m)
    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        _api.init_instance(d)
        srv = {"kind": "server", "id": "dev-server"}
        _api.seed_cell(d, "rubric", "task", "r", maturity="validated", signal_refs=["signals/rubric.task.r/seed.json"])
        _api.seed_cell(d, "spec", "task", "slice", maturity="instantiated", asset_ref="spec/slice.md")
        os.makedirs(os.path.join(d, "spec"), exist_ok=True)
        open(os.path.join(d, "spec", "slice.md"), "w").write("# slice\n")

        t = _api.create_ticket(d, "feature", "the vertical slice", target_cell="spec.task.slice",
                               target_transition={"from": "instantiated", "to": "validated"},
                               acceptance={"rubric_cell": "rubric.task.r"}, budget={"iterations": 2, "tokens": 50000})
        _api.transition_ticket(d, t["id"], "active", srv)

        # the dispatcher drives the slice to done UNATTENDED via the mock adapter
        ok, ticket, msg = dispatch_unit(d, _api.get_ticket(d, t["id"]), MockAdapter(), srv, tier=1, repo_root=root)
        expect(ok and ticket["state"] == "done", f"unattended dispatch did not reach done: {msg}")
        cell = _lat.find(_lat.load(d), "spec.task.slice")
        expect(cell["maturity"] == "validated", "dispatched slice cell not validated")
        expect(cell.get("signal_refs"), "no signal minted by the dispatched critic")
        expect(_api.get_ticket(d, t["id"]).get("claim") is None, "claim not cleared after done")
        # the worktree was torn down
        expect(not os.path.isdir(os.path.join(d, "run", "worktrees")) or
               not os.listdir(os.path.join(d, "run", "worktrees")), "worktree not torn down")

        # lease reconciliation: a claimed ticket with an EXPIRED lease returns to active
        t2 = _api.create_ticket(d, "task", "stuck", target_cell="spec.task.slice",
                                target_transition={"from": "validated", "to": "operating"},
                                acceptance={"rubric_cell": "rubric.task.r"}, budget={"iterations": 1, "tokens": 1000})
        _api.transition_ticket(d, t2["id"], "active", srv)
        _api.transition_ticket(d, t2["id"], "claimed", srv)
        stuck = _api.get_ticket(d, t2["id"])
        stuck["claim"] = {"worker_id": "wrk-dead", "worktree": "x",
                          "lease_expiry": _iso(_now() - datetime.timedelta(seconds=10))}
        _lc.save_ticket(d, stuck)
        reclaimed = reconcile_leases(d)
        expect(t2["id"] in reclaimed, "expired-lease ticket not reclaimed")
        expect(_api.get_ticket(d, t2["id"])["state"] == "active", "reclaimed ticket not returned to active")

        # retry-then-block: a worker failure RETRIES up to MAX_WORKER_ATTEMPTS (a transient hiccup self-recovers
        # instead of wedging the build); only a persistently-stuck cell blocks and drops from dispatch.
        class _AlwaysFail(DispatchAdapter):
            name = "always-fail"
            def dispatch(self, d, unit):
                return {"ok": False, "error": "boom (test)", "metrics": {}}
        _api.seed_cell(d, "spec", "task", "flaky", maturity="instantiated", asset_ref="spec/flaky.md")
        open(os.path.join(d, "spec", "flaky.md"), "w").write("# flaky\n")
        tf = _api.create_ticket(d, "task", "flaky", target_cell="spec.task.flaky",
                                target_transition={"from": "instantiated", "to": "validated"},
                                acceptance={"rubric_cell": "rubric.task.r"}, budget={"iterations": 1, "tokens": 1000})
        _api.transition_ticket(d, tf["id"], "active", srv)
        seen = []
        for _ in range(MAX_WORKER_ATTEMPTS):
            dispatch_unit(d, _api.get_ticket(d, tf["id"]), _AlwaysFail(), srv, tier=1, repo_root=root)
            seen.append(_api.get_ticket(d, tf["id"])["state"])
        expect(seen[:-1] == ["active"] * (MAX_WORKER_ATTEMPTS - 1),
               f"a transient worker failure must RETRY (return to active), got {seen[:-1]}")
        expect(seen[-1] == "blocked",
               f"a cell stuck for {MAX_WORKER_ATTEMPTS} consecutive failures must block, got {seen[-1]}")

        # Feature A: the HeadlessClaudeAdapter folds the operator's recent guidance into a NEWLY dispatched
        # worker's prompt (a running one-shot worker can't be steered mid-flight; the NEXT dispatch is).
        unit = {"layer": "spec", "scope": "task", "slug": "slice", "transition": {"from": "instantiated", "to": "validated"}}
        hca = HeadlessClaudeAdapter()
        expect("Recent operator guidance" not in hca._prompt(d, unit, root), "guidance clause must be absent on an empty buffer")
        _api.enqueue_input(d, "make the leaderboard top-10 only", source="operator")
        _api.drain_input(d)
        expect("make the leaderboard top-10 only" in hca._prompt(d, unit, root),
               "a newly dispatched worker's prompt must fold the latest operator guidance")

        # DF-9 (Phase 1): a kit that DECLARES multi-file authoring makes a code cell author a DIRECTORY of
        # source (not one {slug}.md), and the worker prompt demands industrial multi-file code graded by the
        # cell's per-cell verify.mjs critic harness. Hermetic: a temp kit, no env, no node.
        kitdir = os.path.join(root, "kitx"); os.makedirs(kitdir, exist_ok=True)
        json.dump({"name": "dev-kit-x", "family": "x", "authoring": [{"layer": "capability", "mode": "multi-file"}]},
                  open(os.path.join(kitdir, "kit.json"), "w"))
        capcell = {"layer": "capability", "slug": "deck"}
        auth = _authoring_for(capcell, kit_dir=kitdir)
        expect(auth and auth.get("mode") == "multi-file", "kit-declared multi-file authoring not detected")
        expect(_asset_rel("capability", "deck", auth) == os.path.join("capability", "deck"),
               "a multi-file capability's asset must be a DIRECTORY, not {slug}.md")
        expect(_asset_rel("spec", "s", None) == os.path.join("spec", "s.md"), "doc cells must stay single-file")
        capunit = {"layer": "capability", "scope": "system", "slug": "deck", "transition": {"from": "instantiated", "to": "validated"}}
        os.environ["DEV_FACTORY_KIT"] = kitdir
        try:
            p = hca._prompt(d, capunit, root)
        finally:
            del os.environ["DEV_FACTORY_KIT"]
        expect("multiple files under" in p and "verify.mjs" in p and "CANNOT write it" in p,
               "the multi-file worker prompt must demand source files + name the worker-protected verify.mjs gate")

        # team EXECUTION: a delegation=team plan makes the worker an ORCHESTRATOR that spawns the planned sub-agent
        # team (the Task tool is added; the prompt names the depth) — so 'team, depth 2' is executed, not just ledgered.
        team_unit = dict(capunit, plan={"orchestration_shape": "orchestrator-workers", "loop_strategy": "tracer-bullet",
                                        "effort": {"parallelism": 2, "model_tier": "mid"},
                                        "delegation": {"mode": "team", "max_depth": 2}})
        os.environ["DEV_FACTORY_KIT"] = kitdir
        try:
            tp = hca._prompt(d, team_unit, root)
        finally:
            del os.environ["DEV_FACTORY_KIT"]
        expect("ORCHESTRATOR" in tp and "Task tool" in tp and "depth of 2" in tp,
               "a team-delegation plan must produce an orchestrator prompt that delegates to the planned depth")
        expect("Task" in hca._allowed_tools(team_unit), "delegation=team must add the Task tool to the worker scope")
        expect("Task" not in hca._allowed_tools(capunit), "a non-delegating plan must NOT add the Task tool")

        # adapter selection: DEV_FACTORY_ADAPTER=headless picks the LIVE worker; default is the free mock loop
        expect(isinstance(resolve_adapter("mock"), MockAdapter) and isinstance(resolve_adapter("headless"), HeadlessClaudeAdapter),
               "resolve_adapter must select mock|headless by name")
        expect(adapter_name() == "mock", "adapter_name defaults to mock (free) when DEV_FACTORY_ADAPTER is unset")
        os.environ["DEV_FACTORY_ADAPTER"] = "headless"
        try:
            expect(adapter_name() == "headless" and isinstance(resolve_adapter(), HeadlessClaudeAdapter),
                   "DEV_FACTORY_ADAPTER=headless selects the live adapter (real workers, opt-in)")
        finally:
            del os.environ["DEV_FACTORY_ADAPTER"]
    if fails:
        sys.stderr.write("dispatch selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("dispatch selftest: OK (provision worktree -> claimed(single-writer)+lease -> worker authors -> "
          "critic validates -> done, UNATTENDED, with the worktree torn down and the claim cleared; an expired "
          "lease returns a stuck ticket to active — crash recovery without reconciling competing claims; a newly "
          "dispatched worker's prompt folds the operator's recent 5s guidance; a kit that declares multi-file "
          "authoring routes a code cell to a source DIRECTORY graded by its worker-protected verify.mjs [DF-9])")
    return 0


def main(argv):
    if not argv or argv[0] == "selftest":
        return selftest()
    sys.stderr.write("dispatch.py is a library (use selftest; the heartbeat drives it)\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
