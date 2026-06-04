#!/usr/bin/env python3
"""Structural + targeted-semantic gate over a PLAN/COMPOSE Orchestration Blueprint.

What this DOES check (against the 14-field contract in SKILL.md Output Contract):
every numbered section 1..14 is present and non-empty; the TERMINATION section
names more than one stop layer AND none of those layers is self-reported by the
model (First Principle 5 — enforced OUTSIDE the model); the VERIFICATION GATE
names a gate type AND is not a same-model self-grade on irreversible/correctness-
critical work; a concrete BUDGET ceiling is present; an execution SUBSTRATE +
runnable sketch are named, with no unbounded `while :;` / skip-permissions on
high-stakes work; REJECTED ALTERNATIVES is non-empty; the verdict is honest
(READY-TO-RUN only with a stated dry-run); durability is present for long runs;
and — when the loop ingests untrusted content AND can take external action — the
TRUST BOUNDARY field names a containment/split (the lethal-trifecta gate, C9).

What this does NOT do: it remains NECESSARY, NOT SUFFICIENT. It checks structure
and a handful of *named* anti-patterns mechanically; it cannot prove a gate truly
tests the success criterion, that a stop would actually converge, or that the
budget is right. Those stay [review] judgments with a human/agent reviewer. A
structurally-PASSing blueprint that has not been dry-run against its success
criterion is still BLUEPRINT — UNVERIFIED, never READY-TO-RUN.

Usage:
  check_blueprint.py path/to/blueprint.md
  check_blueprint.py --help
Exit 0 = all gates pass; 1 = one or more gaps; 2 = bad invocation.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys

# The 14 numbered blueprint fields, in contract order (SKILL.md Output Contract).
SECTIONS = [
    (1, "GOAL & SUCCESS CRITERION", ["GOAL", "SUCCESS"]),
    (2, "TASK CLASSIFICATION", ["TASK CLASSIFICATION", "CLASSIFICATION"]),
    (3, "CHOSEN LOOP TOPOLOGY", ["TOPOLOGY", "CHOSEN LOOP"]),
    (4, "REJECTED ALTERNATIVES", ["REJECTED ALTERNATIVE", "REJECTED"]),
    (5, "WIRING / CONTROL FLOW", ["WIRING", "CONTROL FLOW"]),
    (6, "PARAMETERS", ["PARAMETER"]),
    (7, "TERMINATION CONDITIONS", ["TERMINATION"]),
    (8, "VERIFICATION GATE", ["VERIFICATION"]),
    (9, "CONTEXT / MEMORY STRATEGY", ["CONTEXT", "MEMORY"]),
    (10, "FAILURE / FALLBACK HANDLING", ["FAILURE", "FALLBACK"]),
    (11, "EXECUTION SUBSTRATE + RUNNABLE SKETCH", ["SUBSTRATE", "RUNNABLE"]),
    (12, "SCORING", ["SCORING"]),
    (13, "CONFIDENCE / UNVERIFIED NOTE", ["CONFIDENCE", "UNVERIFIED NOTE"]),
    (14, "TRUST BOUNDARY & BLAST RADIUS", ["TRUST BOUNDARY", "BLAST RADIUS", "PRIVILEGE"]),
]
_MAXN = 14

# A numbered-heading line looks like "7. TERMINATION ..." / "7) ..." / "## 7. ...".
_NUM_HEAD = re.compile(r"^\s*#{0,6}\s*(\d{1,2})\s*[.)\]:\-]\s*(.*\S)\s*$")

# Gate-type vocabulary for the VERIFICATION section (C3).
_GATE_TYPES = [
    "executable oracle", "oracle", "ground-truth", "ground truth",
    "llm-judge", "llm judge", "llm-as-judge", "judge", "panel",
    "self-grade", "self grade", "self-judge", "test", "compiler",
    "schema", "lint", "citation", "corroborat", "adversarial",
]

# Stop-layer vocabulary for TERMINATION (C1): we want > 1 *kind* of layer.
_TERM_GOAL = ["goal-gate", "goal gate", "oracle passes", "complete marker",
              "explicit complete", "success criterion met", "tests pass",
              "tests green", "done marker", "completion sentinel", "coverage gate",
              "coverage-complete", "ledger"]
_TERM_NOPROGRESS = ["no-progress", "no progress", "flat round", "flat rounds",
                    "tool-repetition", "tool repetition", "state similarity",
                    "no-improvement", "no improvement", "stall", "plateau",
                    "k rounds", "k flat", "oscillat", "no new", "adds no new"]
_TERM_HARDCAP = ["hard cap", "hard caps", "max-iteration", "max iteration",
                 "max_iteration", "max-iter", "iteration cap", "budget exhaust",
                 "token budget", "cost ceiling", "wall-clock", "wall clock",
                 "timeout", "time box", "time-box", "max-files", "re-dispatch cap",
                 "redispatch cap", "round cap", "token ceiling", "token-budget"]
_TERM_ABORT = ["stuck", "abort", "escalate", "bail", "force synthesis", "needs_manual"]

# Anti-pattern: termination signal computed/declared BY the model (First Principle 5).
# This now fires whenever a self-reported signal appears in TERMINATION, regardless
# of how many layer keywords are also present (the keyword-costume false-PASS fix).
_SELF_REPORTED = ["model decides", "agent decides", "model declares", "agent declares",
                  "decides it's done", "decides its done", "decides it is done",
                  "self-declar", "knows when it", "agent notices", "model notices",
                  "agent determines it", "model determines it", "agent thinks it",
                  "model thinks it", "agent believes", "model believes",
                  "when it feels", "agent considers it done", "agent decides its budget",
                  "agent decides it has", "loop decides it", "the model judges it"]

# Budget detection (C2).
_BUDGET_VAGUE = ["tune as needed", "as needed", "tune later", "tbd", "to be determined",
                 "reasonable", "appropriate budget", "some budget"]
_NUM = re.compile(r"\d")

# Durability (C7) — only required for long/unattended/multi runs.
_DURABLE = ["checkpoint", "idempoten", "resumable", "resume", "durable",
            "crash-safe", "crash safe", "snapshot", "restart-safe"]
_LONG_RUN = ["unattended", "overnight", "scheduled", "cron", "background",
             "async", "long-horizon", "long horizon", "long-running",
             "long running", "fan-out", "fan out", "multi-agent", "fleet",
             "workflow tool", "durable"]

# Substrate (field 11).
_SUBSTRATE = ["subagent", "sub-agent", "task tool", "taskcreate", "workflow tool", "workflow",
              "bash", "while loop", "while :", "while true", "stop-hook",
              "stop hook", "cron", "scheduled", "single-session", "single session",
              "deep-research"]

# Unbounded / unsafe substrate (field 11) — bare loop or skip-permissions.
_UNBOUNDED = ["while :;", "while:;", "while true", "while :", "for(;;)", "for (;;)"]
_SKIP_PERMS = ["--dangerously-skip-permissions", "dangerously-skip-permissions",
               "skip-permissions", "--yolo", "yolo mode"]

# Verdict (field 13).
_VERDICT_READY = ["ready-to-run", "ready to run"]
_VERDICT_UNVERIFIED = ["blueprint — unverified", "blueprint - unverified",
                       "blueprint unverified", "unverified", "block"]
_DRYRUN = ["dry-run", "dry run", "exercised against", "executed against", "ran against",
           "sanity-check", "sanity check", "test run", "pilot run", "executed and passed",
           "has been run", "ran and passed", "dry-ran"]

# Irreversible / correctness-critical signals (sections 1+2) — raise the bar on the gate.
_IRREVERSIBLE = ["irreversible", "correctness-critical", "correctness critical",
                 "production", "payments", "payment", "refund", "destructive",
                 "high-stakes", "high stakes", "deletes", "drop table", "irreversibly"]

# Same-model self-grade (section 8) and its mitigations.
_SELF_GRADE = ["self-grade", "self grade", "self-judge", "self judge", "same agent",
               "same model", "reviews its own", "self-review", "grades itself",
               "judges its own", "self-assess"]
_GRADE_MITIGATION = ["separate judge", "separate agent", "different model", "different family",
                     "executable oracle", "ground-truth", "human review", "human-in-the-loop",
                     "not same-model", "not a self-grade", "independent verifier",
                     "tests", "compiler", "skeptic", "external"]

# Oracle-label illusion (sections 1+8): stop/gate may depend on a label absent at deploy.
_ORACLE_LABEL = ["golden", "expected ledger", "expected output", "ground-truth label",
                 "ground truth label", "reference answer", "reference label", "gold label",
                 "known-good output", "expected answer label"]

# Trust-boundary / lethal-trifecta detection (C9, field 14).
_UNTRUSTED_INGEST = ["untrusted", "open web", "open-web", "web page", "web_search",
                     "web search", "fetch", "arbitrary url", "transcript", "issue content",
                     "channel content", "external content", "scrape", "crawl",
                     "user-provided", "third-party content", "repo content",
                     "ingested content", "attacker-control", "attacker control"]
_EXTERNAL_ACTION = ["git push", "pr merge", "execute_sql", "deploy", "self-modif",
                    "writes to", "production credential", "api write", "post to",
                    "delete", "merge to main", "push to", "--dangerously-skip-permissions"]
_CONTAINMENT = ["content/action split", "content-action split", "dual-llm", "dual llm",
                "read-only", "read only", "no credential", "no credentials",
                "no external-action", "no external action", "sealed egress",
                "allowlist", "sandbox", "least-privilege", "least privilege",
                "no tool-write", "quarantin", "isolat", "privilege scope",
                "blast radius", "no irreversible", "no action capability"]


def _split_sections(text: str) -> dict:
    lines = text.splitlines()
    heads = []  # (section_number, line_index)
    for i, ln in enumerate(lines):
        m = _NUM_HEAD.match(ln)
        if not m:
            continue
        n = int(m.group(1))
        if 1 <= n <= _MAXN:
            heads.append((n, i))
    bodies = {}
    for idx, (n, li) in enumerate(heads):
        end = heads[idx + 1][1] if idx + 1 < len(heads) else len(lines)
        chunk = "\n".join(lines[li:end])
        bodies.setdefault(n, []).append(chunk)
    return {n: "\n".join(parts) for n, parts in bodies.items()}


def _contains_any(haystack: str, needles: list) -> bool:
    low = haystack.lower()
    return any(nd in low for nd in needles)


def _nonempty_body(chunk: str) -> bool:
    body_lines = chunk.splitlines()[1:]
    stripped = []
    for ln in body_lines:
        s = ln.strip().lstrip("-*•").strip()
        if not s:
            continue
        if re.fullmatch(r"\{[^{}]*\}", s):
            continue
        if s in {"...", "—", "-", "TODO", "TBD"}:
            continue
        stripped.append(s)
    return len(stripped) > 0


def check(path: str):
    notes = []
    ok = True
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as e:
        return False, [f"[FAIL] cannot read {path}: {e}"]

    sections = _split_sections(text)

    # --- Check 1: all 14 numbered sections present and non-empty ---------------
    missing, empty = [], []
    for num, name, _kw in SECTIONS:
        if num not in sections:
            missing.append(f"{num}. {name}")
        elif not _nonempty_body(sections[num]):
            empty.append(f"{num}. {name}")
    if missing:
        ok = False
        notes.append(f"[FAIL] sections-present: missing {', '.join(missing)}")
    if empty:
        ok = False
        notes.append(f"[FAIL] sections-nonempty: heading present but empty -> {', '.join(empty)}")
    if not missing and not empty:
        notes.append(f"[PASS] sections-complete: all {_MAXN} numbered fields present and non-empty")

    goal = sections.get(1, "")
    klass = sections.get(2, "")
    rejected = sections.get(4, "")
    params = sections.get(6, "")
    term = sections.get(7, "")
    verify = sections.get(8, "")
    failure = sections.get(10, "")
    substrate = sections.get(11, "")
    confidence = sections.get(13, "")
    trust = sections.get(14, "")

    irreversible = _contains_any(goal + "\n" + klass, _IRREVERSIBLE)

    # --- Check 2 (C1 termination): > 1 stop layer AND not self-reported --------
    layers = []
    if _contains_any(term, _TERM_GOAL):
        layers.append("goal-gate")
    if _contains_any(term, _TERM_NOPROGRESS):
        layers.append("no-progress")
    if _contains_any(term, _TERM_HARDCAP):
        layers.append("hard-cap")
    self_reported = _contains_any(term, _SELF_REPORTED)
    if self_reported:
        ok = False
        notes.append("[FAIL] C1-termination: a stop signal is SELF-REPORTED by the model "
                     "(e.g. 'the agent decides/notices…') — termination must be computed/enforced "
                     "OUTSIDE the model (First Principle 5), not in keyword costume")
    elif len(layers) > 1:
        notes.append(f"[PASS] C1-termination: {len(layers)} stop layers named ({', '.join(layers)}), externally enforced")
        if not _contains_any(term, _TERM_ABORT):
            notes.append("[WARN] C1-termination: no STUCK/abort/escalate path named (impossible tasks may iterate into damage)")
    elif layers == ["hard-cap"]:
        ok = False
        notes.append("[FAIL] C1-termination: max-iterations / hard-cap is the ONLY stop layer — add a goal-gate and a no-progress detector")
    elif layers:
        ok = False
        notes.append(f"[FAIL] C1-termination: only one stop layer named ({layers[0]}); a real stop stacks goal-gate + no-progress + hard caps")
    else:
        ok = False
        notes.append("[FAIL] C1-termination: no recognizable stop layer named in section 7")

    # --- Check 3 (C3 verification): a gate type, and no self-grade on stakes ----
    if not _contains_any(verify, _GATE_TYPES):
        ok = False
        notes.append("[FAIL] C3-verification: no gate type named (expected oracle / ground-truth / "
                     "LLM-judge / panel / citation / self-grade) in section 8")
    else:
        self_grade = _contains_any(verify, _SELF_GRADE)
        mitigated = _contains_any(verify, _GRADE_MITIGATION)
        if irreversible and self_grade and not mitigated:
            ok = False
            notes.append("[FAIL] C3-verification: a same-model SELF-GRADE gate on irreversible / "
                         "correctness-critical work (section 2) — separate the judge or use an "
                         "executable oracle; self-preference bias makes this the weakest rung")
        else:
            notes.append("[PASS] C3-verification: a gate type is named in section 8"
                         + (" (self-grade present but mitigated/low-stakes)" if self_grade else ""))

    # --- Check 4 (C2 budget): a concrete ceiling/number ------------------------
    budget_blob = (params + "\n" + term).strip()
    has_num = bool(_NUM.search(budget_blob))
    vague = _contains_any(budget_blob, _BUDGET_VAGUE)
    if has_num and not vague:
        notes.append("[PASS] C2-budget: a concrete numeric budget/ceiling is present")
    elif has_num and vague:
        ok = False
        notes.append("[FAIL] C2-budget: budget reads as 'tune as needed' alongside numbers — name a concrete hard ceiling")
    else:
        ok = False
        notes.append("[FAIL] C2-budget: no concrete number/ceiling in PARAMETERS or TERMINATION")

    # --- Check 5 (field 11): substrate named, and not an unbounded/unsafe one ---
    if _contains_any(substrate, _SUBSTRATE):
        notes.append("[PASS] substrate: a runnable substrate is named in section 11")
    else:
        ok = False
        notes.append("[FAIL] substrate: no execution substrate named in section 11")
    if _contains_any(substrate, _SKIP_PERMS) and irreversible:
        ok = False
        notes.append("[FAIL] substrate: skip-permissions / YOLO substrate on irreversible / high-stakes "
                     "work (section 2) with no containment — opt-in execution + a gate are required, not a skip flag")
    if _contains_any(substrate, _UNBOUNDED):
        if "hard-cap" not in layers:
            ok = False
            notes.append("[FAIL] substrate: an unbounded `while :;` loop with no hard cap in TERMINATION — "
                         "the canonical overbake/cost-runaway shape; add a `--max-iterations` / budget ceiling")
        else:
            notes.append("[WARN] substrate: a bare `while :;` loop is named — ensure the hard cap is actually "
                         "enforced by the driver, not just stated")

    # --- Check 6 (field 4): REJECTED ALTERNATIVES non-empty --------------------
    if 4 in sections and _nonempty_body(rejected):
        notes.append("[PASS] rejected-alternatives: section 4 is non-empty")
        if not _contains_any(rejected, ["single", "one strong pass", "one pass",
                                        "augmented llm", "single pass", "ralph", "minimal"]):
            notes.append("[WARN] rejected-alternatives: does not visibly rule out a single strong pass / minimal Ralph loop")
    else:
        ok = False
        notes.append("[FAIL] rejected-alternatives: section 4 missing or empty")

    # --- Check 7 (field 13): honest verdict — READY only with a dry-run --------
    ready = _contains_any(confidence, _VERDICT_READY)
    unverified = _contains_any(confidence, _VERDICT_UNVERIFIED)
    if ready and not _contains_any(confidence, _DRYRUN):
        ok = False
        notes.append("[FAIL] verdict: READY-TO-RUN asserted with no stated dry-run / exercise against the "
                     "success criterion (section 13) — the honest default for an un-exercised plan is "
                     "BLUEPRINT — UNVERIFIED")
    elif ready or unverified:
        notes.append("[PASS] verdict: an explicit, honest READY-TO-RUN / BLUEPRINT-UNVERIFIED verdict line exists")
    else:
        ok = False
        notes.append("[FAIL] verdict: no explicit READY-TO-RUN vs BLUEPRINT-UNVERIFIED verdict line in section 13")

    # --- Check 8 (C9 trust boundary / lethal trifecta, field 14) ---------------
    untrusted = _contains_any(text, _UNTRUSTED_INGEST)
    action = _contains_any(text, _EXTERNAL_ACTION)
    contained = _contains_any(trust, _CONTAINMENT)
    if 14 in sections and _nonempty_body(trust):
        if untrusted and action and not contained:
            ok = False
            notes.append("[FAIL] C9-trust-boundary: the loop ingests untrusted content AND can take an "
                         "external/irreversible action (lethal trifecta) but field 14 names no containment "
                         "(content/action split / read-only-reader / sealed egress / allowlist / least-privilege)")
        else:
            notes.append("[PASS] C9-trust-boundary: field 14 addresses trust boundary / blast radius"
                         + (" with containment for the trifecta exposure" if (untrusted and action) else ""))
    # (a missing/empty field 14 is already reported by Check 1.)

    # --- Oracle-label illusion (WARN) ------------------------------------------
    if _contains_any(goal + "\n" + verify, _ORACLE_LABEL):
        notes.append("[WARN] oracle-label illusion risk: the success criterion / gate may depend on a "
                     "golden/expected/ground-truth label absent at deployment (control-plane.md §3.4) — "
                     "confirm the stop signal exists at run time, or the loop won't reproduce")

    # --- C7 durability (conditional WARN) --------------------------------------
    long_run = _contains_any(text, _LONG_RUN)
    durable_named = _contains_any(failure + "\n" + sections.get(9, ""), _DURABLE)
    if long_run and not durable_named:
        notes.append("[WARN] C7-durability: long/unattended/multi-agent run names no checkpoint/idempotency boundary (section 10)")
    elif long_run and durable_named:
        notes.append("[PASS] C7-durability: durability (checkpoint/idempotency) named for the long/unattended run")

    # --- Check 9 (C8 observability) [gate/mech-partial]: iteration counter + budget signal + kill path ---
    # C8 blocks SHIP but is not fully automated — this check mechanizes the minimum structural bar.
    # A loop with none of these signals is a black box: it cannot be safely observed or stopped.
    _ITER_COUNT = ["iteration count", "current iteration", "step counter", "loop counter",
                   "num_iterations", "iter_count", "progress signal", "steps completed",
                   "turn count", "attempts made", "attempt count", "current step",
                   "step_num", "iteration:", "iter:", "step:", "round:"]
    _OBS_BUDGET = ["remaining budget", "tokens remaining", "cost remaining", "budget remaining",
                   "token count", "cost so far", "budget countdown", "cost signal",
                   "budget signal", "spent tokens", "remaining tokens", "budget_remaining",
                   "cost_remaining", "tokens_used", "cost_used"]
    _KILL_PATH   = ["kill path", "kill signal", "force-terminate", "force terminate",
                    "force-stop", "hard-stop", "hard stop", "externally stop",
                    "external stop", "interrupt path", "sigint", "sigterm", "watchdog",
                    "abort path", "escape hatch", "emergency stop"]

    substrate11 = substrate + "\n" + sections.get(9, "")
    obs_iter   = _contains_any(substrate11, _ITER_COUNT)
    obs_budget = _contains_any(substrate11, _OBS_BUDGET)
    obs_kill   = _contains_any(term + "\n" + substrate, _KILL_PATH) or _contains_any(term, _TERM_ABORT)

    if obs_iter and obs_budget and obs_kill:
        notes.append("[PASS] C8-observability [mech-partial]: iteration counter + budget signal + kill path named")
    else:
        if not obs_iter:
            ok = False
            notes.append("[FAIL] C8-observability [mech-partial]: no iteration counter / progress signal in "
                         "substrate (section 11) — the loop cannot be observed or interrupted without knowing "
                         "where it is; name the specific counter variable or signal")
        if not obs_budget:
            notes.append("[WARN] C8-observability [mech-partial]: no real-time budget/cost signal surfaced in "
                         "substrate — operator cannot detect runaway spend mid-run; surface remaining tokens/cost")
        if not obs_kill:
            notes.append("[WARN] C8-observability [mech-partial]: no external kill path named — add how the loop "
                         "is forcibly stopped from outside (SIGINT, watchdog flag, external abort sentinel)")

    # --- Operability gauges (WARN) -------------------------------------------------
    _COST_PER_SUCCESS = ["cost-per-success", "cost per success", "cost/success",
                         "success cost", "cost per completion", "efficiency metric"]
    _RETRY_TREND = ["retry trend", "retry-trend", "retry rate", "failure trend",
                    "convergence rate", "attempt trend", "retry_count", "fail_count"]
    _WORKER_TRACE = ["trace id", "trace-id", "traceid", "worker id", "worker-id",
                     "span id", "correlation id", "per-worker", "per worker",
                     "subagent id", "task_id", "worker_id", "job_id"]
    if not _contains_any(text, _COST_PER_SUCCESS):
        notes.append("[WARN] operability: no cost-per-success metric named — consider how "
                     "efficiency (success rate / token spend) will be measured post-run")
    if long_run and not _contains_any(text, _WORKER_TRACE):
        notes.append("[WARN] operability: long/multi-agent run with no per-worker trace ID — "
                     "add a correlation ID per subagent so failures can be attributed to a specific worker")
    if not _contains_any(text, _RETRY_TREND):
        notes.append("[WARN] operability: no retry-trend / failure-rate signal — "
                     "consider logging consecutive failures to detect non-convergence before the hard cap fires")

    notes.append("[NOTE] NECESSARY, NOT SUFFICIENT — structural + named-anti-pattern checks only. A PASS does "
                 "not prove the gate tests the success criterion or that the loop converges; an un-exercised "
                 "blueprint is BLUEPRINT — UNVERIFIED, never READY-TO-RUN.")
    return ok, notes


_VG_TYPES = ["oracle", "ground-truth", "llm-judge", "panel", "adversarial-panel", "self-grade"]
_ROUTES = ["R0", "R1", "R2", "R3", "R3-lite", "R4", "R5", "R6", "R7", "R8", "R9"]
_VERDICTS = ["READY-TO-RUN", "BLUEPRINT-UNVERIFIED", "BLOCK"]
_LAYERS = ["goal-gate", "no-progress", "hard-cap", "abort"]
_CONTAINMENT = ["content-action-split", "read-only-reader", "sealed-egress", "allowlist", "least-privilege", "sandboxed"]


def validate_sidecar(sidecar_path: str) -> list[str]:
    """Validate a blueprint JSON sidecar against schemas/blueprint.json's load-bearing rules — the
    structural layer that makes Wlaschin-class illegal states actually unrepresentable (not just
    written down). Hand-implements THIS schema's required fields, enums, consts, and the four allOf
    illegal-state bans + the verifier-stronger rule; no jsonschema dependency. Returns errors (empty=valid).
    """
    errs: list[str] = []
    try:
        obj = json.load(open(sidecar_path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return [f"cannot read/parse sidecar {sidecar_path}: {e}"]
    if not isinstance(obj, dict):
        return ["sidecar is not a JSON object"]

    for f in ("goal", "successCriterion", "topologyRoute", "taskClassification",
              "verificationGate", "termination", "verdict", "trustBoundary"):
        if f not in obj:
            errs.append(f"missing required field '{f}'")

    if obj.get("topologyRoute") not in _ROUTES and "topologyRoute" in obj:
        errs.append(f"topologyRoute '{obj.get('topologyRoute')}' not in {_ROUTES}")
    if obj.get("verdict") not in _VERDICTS and "verdict" in obj:
        errs.append(f"verdict '{obj.get('verdict')}' not in {_VERDICTS}")

    vg = obj.get("verificationGate") if isinstance(obj.get("verificationGate"), dict) else {}
    if vg.get("type") and vg["type"] not in _VG_TYPES:
        errs.append(f"verificationGate.type '{vg['type']}' not in {_VG_TYPES}")
    tc = obj.get("taskClassification") if isinstance(obj.get("taskClassification"), dict) else {}
    term = obj.get("termination") if isinstance(obj.get("termination"), dict) else {}
    tb = obj.get("trustBoundary") if isinstance(obj.get("trustBoundary"), dict) else {}

    layers = term.get("layers") if isinstance(term.get("layers"), list) else []
    if term:
        if term.get("selfReported") is not False:
            errs.append("termination.selfReported MUST be false (model-decided termination is prohibited — First Principle 5)")
        if len(layers) < 2:
            errs.append("termination.layers requires >= 2 stacked stop layers")
        for l in layers:
            if l not in _LAYERS:
                errs.append(f"termination.layers has invalid layer '{l}' (not in {_LAYERS})")
    if tb.get("containmentType") and tb["containmentType"] not in _CONTAINMENT:
        errs.append(f"trustBoundary.containmentType '{tb['containmentType']}' not in {_CONTAINMENT}")

    # --- the four allOf illegal-state bans (+ the verifier-stronger rule) ---
    if vg.get("type") == "self-grade" and tc.get("irreversible") is True:
        if not (isinstance(vg.get("mitigations"), list) and len(vg["mitigations"]) >= 1):
            errs.append("ILLEGAL STATE 1: self-grade gate on irreversible work requires >= 1 mitigation "
                        "(separate-judge, return-best-not-last, anti-oscillation, iteration-cap)")
        if vg.get("verifierStrongerThanGenerator") is not True:
            errs.append("ILLEGAL STATE 1b: self-grade on irreversible work requires "
                        "verifierStrongerThanGenerator: true (a weak verifier hurts — control-plane §3.2)")
    if obj.get("verdict") == "READY-TO-RUN" and obj.get("dryRunExecuted") is not True:
        errs.append("ILLEGAL STATE 2: READY-TO-RUN verdict requires dryRunExecuted: true")
    if tb.get("untrustedContentIngested") is True and tb.get("externalActionsCapable") is True:
        if tb.get("containmentNamed") is not True or not tb.get("containmentType"):
            errs.append("ILLEGAL STATE 3: lethal trifecta (untrusted content + external actions) requires "
                        "containmentNamed: true and a containmentType")
    if len(layers) == 1 and layers[0] == "hard-cap":
        errs.append("ILLEGAL STATE 4: hard-cap alone is not a real stop; layer it with goal-gate + no-progress")
    return errs


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="check_blueprint.py",
        description=(
            "Structural + targeted-semantic gate over a PLAN/COMPOSE Orchestration "
            "Blueprint (the 14-field contract in SKILL.md). Checks field presence + "
            "control-plane gates C1 (termination, incl. self-reported-stop), C2 "
            "(budget), C3 (verification, incl. self-grade-on-irreversible), C7 "
            "(durability), C9 (trust boundary / lethal trifecta), verdict honesty, "
            "and unsafe substrate. NECESSARY, NOT SUFFICIENT — not semantic proof."
        ),
        epilog="Exit 0 = all gates pass; 1 = one or more gaps; 2 = bad invocation.",
    )
    parser.add_argument("blueprint", nargs="?", help="path to the Orchestration Blueprint markdown/text file")
    parser.add_argument("--sidecar", metavar="FILE",
                        help="path to a JSON blueprint sidecar to validate against schemas/blueprint.json "
                             "(the structural layer: enforces the four illegal-state bans). May be used with "
                             "or without the prose blueprint.")
    args = parser.parse_args(argv)
    if not args.blueprint and not args.sidecar:
        parser.error("give a blueprint file and/or --sidecar FILE")

    ok = True
    if args.blueprint:
        bp_ok, notes = check(args.blueprint)
        ok = ok and bp_ok
        print(f"== {args.blueprint} ==")
        for n in notes:
            print("  " + n)
        fails = sum(1 for n in notes if n.startswith("[FAIL]"))
        warns = sum(1 for n in notes if n.startswith("[WARN]"))
        print(f"\nSUMMARY: {fails} fail, {warns} warn")

    if args.sidecar:
        errs = validate_sidecar(args.sidecar)
        ok = ok and not errs
        print(f"== sidecar: {args.sidecar} ==")
        if errs:
            for e in errs:
                print("  [FAIL] " + e)
        else:
            print("  [PASS] sidecar valid — no illegal states representable")
        print(f"\nSIDECAR: {len(errs)} fail")

    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
