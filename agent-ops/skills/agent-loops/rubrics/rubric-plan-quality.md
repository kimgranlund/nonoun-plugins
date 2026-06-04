# Rubric — Plan Quality

Score the **emitted orchestration blueprint itself** — the builder-seat output contract. Where `rubric-loop-selection` asks "did you pick the right loop?" and `rubric-loop-control` asks "is the loop safe and bounded?", this rubric asks the third cross-cutting question: **is the blueprint complete, concrete, and executable — or is it a topology name dressed up as a plan?** A blueprint that picks the right loop and wires a sound control plane still fails the skill's job if it hands the operator "use an orchestrator-workers pattern" instead of roles, parameters, a substrate, and a runnable sketch. The blueprint is the deliverable; this rubric is its acceptance bar.

**Band:** cross-cutting — load for EVERY plan, unconditionally (alongside `rubric-loop-selection` and `rubric-loop-control`). It scores the blueprint's _form and completeness_, which every plan must satisfy regardless of which family it composes.

Each dimension is labeled by how it is checked:

- **[gate]** — mechanically/structurally checkable. A failing gate blocks SHIP; it is not a matter of opinion. Q3 (control-plane-wired) overlaps with `${CLAUDE_PLUGIN_ROOT}/bin/check_blueprint.py`'s field-presence checks; Q1/Q2/Q7 are **[mech-partial]** — the criteria are structural but no automated script enforces the full check; agent judgment applies.
- **[mech-partial]** — mechanically checkable criterion, no automated script covers it fully — agent manually applies the check. Treated as a [gate] for SHIP purposes.
- **[review]** — requires judgment to score 1–5. The reviewer reads the blueprint and rates it against the anchor.

**Ship rule:** a plan ships when **every [gate] passes AND no [review] dimension is below 3**. Record evidence for every finding — cite the blueprint field number (the 14-field Orchestration Blueprint), the parameter, or the missing line. A finding without a citation is an opinion.

**Calibration caveat:** this rubric is **draft, 0 calibration samples**. Treat every score as **directional, not authoritative**, until the ROADMAP v0.2 calibration bar is met. The [gate] dimensions (Q1, Q2, Q3, Q7) are the only mechanically verifiable layer; the [review] anchors (Q4, Q5, Q6) are practitioner-folklore calibration points, not measured thresholds. `${CLAUDE_PLUGIN_ROOT}/bin/check_blueprint.py` mechanizes the gate layer (field presence + control-plane-gate instantiation); the review layer is human judgment.

---

## Dependency

This is a per-cycle cross-cutting rubric and, like every per-family rubric, it **depends on `rubric-loop-control`** (see the manifest `dependencies` array). `rubric-loop-control`'s gates also apply: a blueprint cannot pass Q3 (control-plane-wired) in isolation — Q3 checks that the control-plane fields are _present and instantiated_, while `rubric-loop-control` checks that what they instantiate is _sound_. Load and score both. The ship rule is the union: the plan must clear `rubric-plan-quality`'s gates **and** `rubric-loop-control`'s gates simultaneously.

---

## Gate dimensions

Run these first. They are the load-bearing structural checks; a blueprint that fails any of them is not executable, regardless of prose quality.

### Q1 [gate / mech-partial] — Runnable concreteness

The plan names the **carrier/harness, the roles, the model assignment per role, and the actual artifacts** (files, prompts, gate commands) — not an abstract pattern description. "Use an orchestrator-workers pattern" is advice; a runnable sketch on a named substrate is a blueprint.

**Test:** inspect blueprint field 11 (Execution Substrate + Runnable Sketch) and field 5 (Wiring / Control Flow). All four must be concretely present:

1. **Substrate named** — one of: Claude Code subagents · Workflow/orchestration tool · bash `while`-loop · Stop-hook session-internal · cron/scheduled · single-session. "An agent" or "the harness" unqualified fails.
2. **Roles named** — who calls whom (orchestrator / worker / generator / judge / writer), not "the agents."
3. **Model-per-role assigned** — field 6 maps each role to a model tier; "an LLM" unqualified fails.
4. **Runnable sketch present** — the actual bash loop, the subagent dispatch pseudocode, the workflow-graph nodes, or the prompt-file + gate command — specific enough to paste onto the substrate and run. A sketch that hand-waves the gate command ("then verify") fails.

Any one of the four missing or abstract → **fail**. (Anti-pattern: handing back a topology name with no substrate, no roles, no sketch.)

### Q2 [gate / mech-partial] — Parameter completeness

**Every key parameter the chosen family requires** (per that family's rubric's parameter list, and the blueprint's field-6 parameter slots) has a **concrete value** or an explicit **"operator decides + named default."** "Tune as needed" with no default is a hole, not a parameter.

**Test:** enumerate the parameters field 6 demands for the chosen topology — iteration/depth caps, fan-out width, per-step tool-call budget, advisory token budget, hard ceiling, model-per-role, and the topology-specific set (plan representation · replan cadence · vote threshold · memory window · …). For each:

- a concrete number/value present → pass that parameter;
- "operator decides, default = {value}" → pass (the default is the concrete fallback);
- "tune as needed" / "TBD" / silently absent → **fail** that parameter.

Any required parameter left as a bare hole → the gate fails. Cross-check against the per-family rubric: a parameter that rubric names as load-bearing (e.g. Ralph's `--max-iterations`, auto-research's four bounds, debate's N/R, evaluator-optimizer's iteration cap) must have a value here.

### Q3 [gate / mech-partial] — Control-plane wired

The plan **instantiates all of `rubric-loop-control`'s gates** — termination (C1), budget (C2), verification (C3), durability where applicable (C7) — as filled blueprint fields, rather than leaving them implicit. This is the structural-presence check; `rubric-loop-control` then scores whether what is wired is _sound_.

**Test:** confirm the four control-plane gates appear as concrete content in the blueprint:

- field 7 (Termination) carries a **layered** stop — goal-gate + no-progress detector + hard caps + STUCK/abort path — not just `max_iterations` and not just "model decides done";
- field 6 (Parameters) carries **both** an advisory pacing budget **and** a hard ceiling (C2);
- field 8 (Verification Gate) names a gate type, what it checks, and the trust note (C3);
- field 10 (Failure/Fallback) carries durability — checkpoint granularity + idempotency boundary — **for long/unattended/multi-agent runs** (C7; mark N/A for short attended loops).

Any of C1/C2/C3 absent or left implicit → **fail**. (This is the "no silent gaps" check `${CLAUDE_PLUGIN_ROOT}/bin/check_blueprint.py` mechanizes.) Note: presence here ≠ soundness there — a termination stack that is _present but unsound_ passes Q3 and fails `rubric-loop-control` C1.

### Q7 [gate / mech-partial] — Verify Target named

The plan ends with a **concrete real-world verify target** — "done against reality" for the whole run — not just internal green-CI, and not just "the plan reads well." The skill's own Verify Target discipline applied to its output: the blueprint must state the signal that proves the _run_ produced correct output.

**Test:** inspect field 1 (Success Criterion) and field 13 (Confidence/Unverified Note). A passing blueprint:

1. states an **objective success criterion** that the verification gate provably tests (field 1 ↔ field 8 are consistent — the gate checks the criterion, not a proxy);
2. names a **real-world** verify target for the whole run, distinct from the inner-loop CI gate (e.g. "the migrated app boots and the smoke flow passes," not only "tests are green");
3. carries an **honest verdict** — `READY-TO-RUN` only if the plan was dry-run/sanity-checked against the criterion, else `BLUEPRINT — UNVERIFIED`.

A blueprint whose success criterion is subjective with no objective verify target, or that claims `READY-TO-RUN` without exercising the plan, → **fail**. (Anti-pattern: green internal CI asserted as proof the _goal_ was met.)

---

## Review dimensions

Score 1–5 against the anchor. Cite the blueprint field for every score.

### Q4 [review] — Role / output contracts

Each agent/role has an **objective + output format + tool/source guidance + boundary**, and the **hand-off and aggregation contracts** are specified — so a worker doesn't duplicate, drift, or return an unparseable blob, and the orchestrator knows how results combine.

**Evidence to cite:** field 5 (Wiring) and field 6 (per-role parameters). Read each role's contract and the channels between roles.

| Score | Anchor |
| --- | --- |
| **5** | Every role has all four (objective · output format · tool/source guidance · boundary); hand-off (handoff vs delegation, what context passes) and aggregation (how results combine) are explicit; large outputs passed by reference. |
| **3** | Roles have objective + format but boundaries are loose or the aggregation contract is implied ("then combine"); one role under-specified. |
| **1** | "The agents research and write it up" — no per-role contract, no output format, no aggregation rule; workers will duplicate or return raw transcripts. |

### Q5 [review] — Failure-mode coverage

The plan **names the chosen family's top failure modes and a guard for each** — proxy-gaming → real-behavior gate; over-spawn → effort cap; parallel-write conflict → single-threaded synthesis; oracle-label illusion → deployment-reproducible stop. Not a generic "things might go wrong," but the _named_ dominant failure of this topology with its specific mitigation.

**Evidence to cite:** field 10 (Failure/Fallback) and field 4 (Rejected Alternatives, which should already reveal failure-awareness). Cross-check against the chosen family rubric's failure taxonomy.

| Score | Anchor |
| --- | --- |
| **5** | The topology's dominant failure mode is named by its specific name, each has a concrete guard, and a fallback path is specified (e.g. `git reset --hard` to last green / drop to single-agent / return best-of-N). |
| **3** | The dominant failure is named with a guard, but secondary failure modes or the fallback path are missing. |
| **1** | No named failure modes; "the loop should handle errors" or silence. The plan walks into the topology's known trap (over-spawn, shared-write conflict, overbaking) with no guard. |

### Q6 [review] — Operator-posture handoff

The plan states **what the human must do** (author the spec, build the gates, supervise, intervene) and **where the on-loop / in-loop boundary sits** — and cleanly **hands off to the sibling `agentic-ux` skill** for any evaluation of that experience, rather than re-doing it. This dimension checks the **handoff to the sibling** and the operator-action statement; it does **not** itself score the operator UX (trust, steerability, observability-as-experience). Scoring the human experience of the running workflow is the sibling skill's job — this rubric stays in the builder seat and only verifies the boundary is named and the baton is passed.

**Evidence to cite:** the blueprint's autonomy/handoff statement and field 13. Check that operator obligations are stated and that UX evaluation is _deferred to the sibling_, not duplicated.

| Score | Anchor |
| --- | --- |
| **5** | Operator obligations are explicit (what the human authors / builds / supervises); the on-loop vs in-loop boundary is stated; the plan explicitly hands UX evaluation to the sibling `agentic-ux` skill rather than scoring trust/steerability itself. |
| **3** | Operator obligations are stated but the on-loop/in-loop boundary is fuzzy, or the sibling handoff is implied rather than named. |
| **1** | No statement of what the human must do; **or** the plan drifts into scoring the workflow's human UX itself (rating trust/observability/steerability) — a boundary violation, since that is the sibling's seat. |

---

## Scoring summary template

```text
Blueprint: {goal short name}   Topology: {primary (+ nested)}   Mode: {PLAN | COMPOSE}

Dependency — also score rubric-loop-control (its gates apply):
  C1 termination-stack ......... PASS / FAIL
  C2 budget .................... PASS / FAIL
  C3 verification-gate ......... PASS / FAIL
  C7 durability-idempotency .... PASS / FAIL / N-A

Plan-quality gates:
  Q1 runnable-concreteness ..... PASS / FAIL   {field 11/5/6 evidence}
  Q2 parameter-completeness .... PASS / FAIL   {missing parameter, or all-present}
  Q3 control-plane-wired ....... PASS / FAIL   {which of C1/C2/C3/C7 fields filled}
  Q7 verify-target ............. PASS / FAIL   {field 1↔8 consistency; honest verdict}

Plan-quality review dimensions (1-5):
  Q4 role/output contracts ..... {n}   {field 5/6 evidence}
  Q5 failure-mode coverage ..... {n}   {field 10/4 evidence}
  Q6 operator-posture handoff .. {n}   {boundary + sibling handoff; builder-seat only}

Verdict:
  READY-TO-RUN            — all gates PASS (incl. rubric-loop-control's) AND no review < 3 AND plan dry-run against the success criterion
  BLUEPRINT — UNVERIFIED — all gates PASS but the plan was NOT exercised against its success criterion; name the dry-run as the remaining step
  BLOCK                  — any gate fails, or any review < 3
Top findings (severity-ranked, each citing a blueprint field):
  1. ...
```

A blueprint that fills every field but was **not dry-run / sanity-checked against the success criterion** is **BLUEPRINT — UNVERIFIED**, never **READY-TO-RUN** — the same honesty rule the skill applies to the loops it designs. A blueprint that names a topology but fails Q1/Q2/Q3/Q7 is **BLOCK** regardless of polish.
