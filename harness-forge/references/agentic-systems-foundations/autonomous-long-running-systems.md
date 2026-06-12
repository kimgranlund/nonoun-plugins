# Autonomous Long-Running Systems

`Cell: methodology.fleet.autonomous-long-running-systems · Status: defined · Register: lab-empirical and practitioner-documented patterns; staging thresholds are convention`

## The Harness Is the Unit of Engineering

An agent is a model autonomously using tools in a loop; everything that makes it
reliable lives *around* the model. The harness comprises: the environment the agent
runs in, the tools it can call, the durable artifacts that carry state across context
windows, the orchestration deciding what runs next, and the gates that block progress
until checks pass. Engineering time goes to the harness; the prompt is one field
inside it.

## Durable State on Disk

Context windows forget; the repo remembers. Long-running work externalizes all state:
the lattice (or at minimum a feature list in JSON with per-item pass flags — JSON
because models are less likely to overwrite it than Markdown), progress logs, git
history with descriptive commits, and signal artifacts. Rationale is written into the
artifacts themselves — future iterations will not have this reasoning in context.

## Fresh-Context Iteration

The canonical discipline (the Ralph pattern): every iteration starts with a fresh
context window; state survives on disk, not in conversation history. Compaction and
context rot are the enemies of multi-hour coherence. One unit of work per dispatch —
one cell per worker agent — gets the same property by construction: clean context per
loop, structured handoff through the lattice and ledger.

## Agent Topology for Long Runs

The documented long-horizon shape is a three-role split:

- **Initializer** — first run only: writes the environment bootstrap, the progress
  log, the typed work inventory (feature list / lattice seed), and an initial commit.
- **Worker** — one unit at a time: pick the next item, implement, verify, commit with
  a descriptive message, update the progress state, exit.
- **Planner** (optional third) — re-prioritizes the inventory between worker passes;
  in lattice terms, the compass run as a step.

## Hook Control: Gates and Feedback

Two species of deterministic control, with distinct jobs:

- **Gates** block: a stop-gate runs the full suite and refuses completion on failure
  (guarding against infinite self-triggering with an active-flag check); pre-action
  gates deny writes to protected paths.
- **Feedback** injects: fast checks return their findings as additional context
  ("3 type errors in handler.ts at lines 42, 78, 103") so the next action
  self-corrects. Feedback improves the loop; gates merely stop it. Use both, in
  their places: feedback on the fast path, gates at the boundary.

## Hermetic Environments

Each parallel agent gets an isolated checkout or worktree — merge collisions are a
scheduling failure, not a model failure. Unattended loops run sandboxed (container or
VM): a long-running loop holds an unrestricted shell, and isolation is the only
defense that doesn't depend on the model's good behavior. Orphaned environments are
cleaned up as part of the loop's exit, not as quarterly hygiene.

## Budgets and Stop Conditions

Every loop carries: an iteration cap, a token/dollar budget, a wall-clock limit, a
no-progress detector (the same failure signature N times → halt and surface), and a
*separate* done-judge — the worker does not declare its own completion. Loop length,
not model choice, dominates cost; a 10-turn loop can spend ~50× the tokens of a
single call, and uncapped overnight loops are the canonical token-burn incident.

## Staged Autonomy

Autonomy is earned by measured verifier track record (full ladder in
`layer-policy.md`):

1. **Instrument before automating** — fast feedback hooks and a blocking stop gate on
   one real module; advance when the agent reliably reaches green unwatched.
2. **One closed verifier loop per domain, attended** — watch every run; tune the
   verifier whenever it gives a wrong signal; advance at false-pass under ~5%.
3. **Generator/critic split plus an eval harness** — calibrated skeptic, eval suite
   growing from observed failures, upstream fixes (spec/rubric, not output patches).
4. **Unattended, carefully** — only with hermetic sandbox, protected verifier assets,
   all caps active, a separate done-judge, and a tamper-evident audit trail. Demotion
   on any reward-hacking incident is automatic.

## Failure Modes of Long-Running Autonomy

**Reward hacking** — the dominant risk; defenses in `evals-and-verification.md`.
**Flaky verifiers** — noise in the gradient; quarantine before autonomy.
**Context rot** — fresh-context iteration and disk state are the mitigations;
compaction is a last resort, not a strategy.
**Comprehension debt** — the loop ships faster than you understand the output; if
you cannot explain merged work, drop back to attended mode. The loop amplifies
operator skill; it does not substitute for it.
**Token economics** — shorten loops and improve first-pass context before adding
iterations; spend per resolved unit is a ledger metric, watched like any other.
