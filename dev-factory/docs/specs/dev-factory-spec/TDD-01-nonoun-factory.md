# The nonoun Factory — Specification & Architecture

**Document:** TDD-01-nonoun-factory
**Version:** 0.1.0 (Draft)
**Date:** June 2026
**Status:** Draft — first complete pass; unvalidated (corpus maturity `defined`)
**Audience:** factory engineers, platform architects, substrate-engineering practitioners

---

## How to Read This Document

This document serves two purposes. Read it front-to-back as a **brief** to understand the intent, reasoning, and design philosophy behind the nonoun Factory. Or use the table of contents to jump to a specific **specification section** for schemas, interfaces, the state machine, the server, or the agent roster.

Sections marked **📐** are specification detail. Sections marked **💡** are design reasoning. Sections marked **⚠️** are open decisions. The vocabulary throughout draws from the project corpus — see `agentic-systems-ontology.md` for every controlled term used here.

---

## Table of Contents

1. What This Is
2. Why It Exists
3. First Principles (the disciplines this spec obeys)
4. The Central Reconciliation: Two Lifecycles, One Link
5. Core Architecture: Kernel / Kit / Instance / Server
6. The Coordination Corpus (the ticket substrate)
7. The Ticket Lifecycle State Machine
8. The Outer Loop (the 30-second heartbeat)
9. The Server (Python) and Live UI
10. The Agent Roster (workers, orchestrators, architects)
11. The Compound Skills (folders that carry their own substrate)
12. Naming Conventions (namespaced to `nonoun`)
13. Canonical Schemas
14. Safety, Autonomy, and Reward-Hacking Defenses
15. Failure, Crash, and Recovery Semantics
16. What Differentiates This System
17. Anti-Patterns
18. Open Decisions
19. Bootstrapping Arc & Current Status
20. Requirements Index

---

## 1 · What This Is

The **nonoun Factory** is a self-hosting, lights-out agentic system that advances a knowledge **lattice** by running an autonomous outer loop: it reads a coordination corpus of work tickets, dispatches agent workers to advance cells against validated verifiers, records everything to an append-only ledger, and improves its own definitional knowledge from that ledger — all while a human governs the boundary of what it may rewrite rather than performing the work.

It is, in category terms, a **dark factory** (Phase D of the substrate-engineering arc): the outer regeneration loop running unattended at instance-and-fleet scale. It is *not* an agent framework, a CI bot, or a project-management tool, though it has organs resembling each. It is the harness factory described in `agentic-systems-ontology.md`, made operational.

At its most fundamental level the Factory does four things:

- **Selects** — scans the lattice and the coordination corpus, ranks what to advance next (deterministic; the compass).
- **Dispatches** — claims a ticket, provisions a hermetic environment, runs a worker against one cell (the engine).
- **Verifies** — a separate critic validates the work and emits a signal; the cell's maturity advances only on signal (the generator/critic split).
- **Regenerates** — distills the ledger into patterns and upstream revision proposals, improving the definitions the next loop runs against.

> The name is deliberate. Work in this system is named by **verbs** — operations that advance cells — not by a static product noun. There is no "the product" sitting at the center; there is the substrate and the operations that move it. "nonoun" is that stance compressed into a namespace.

---

## 2 · Why It Exists

**Failure 1: the loop converges the output, nothing converges the definition.** Loop engineering reliably converges a single task against a fixed verifier, but the verifier, spec, knowledge, and permissions are authored by hand and frozen. A team accumulates outputs, not a sharpening substrate. *(Root: the definitional layer is treated as static setup.)*

**Failure 2: coordination lives in tools that don't share the work's ontology.** Tickets in a generic tracker are nouns with ad-hoc statuses, disconnected from the knowledge state they're supposed to change. "Done" in the tracker and "validated" in the system are unrelated facts, so drift between *what was claimed* and *what is true* is undetectable. *(Root: the coordination object has no typed link to the knowledge asset it advances.)*

**Failure 3: autonomy is granted by enthusiasm and revoked by incident.** Without a measured trust ladder and mechanical gates, unattended operation is either forbidden (no leverage) or reckless (reward-hacking ships). *(Root: standing intent expressed as prose, not enforcement.)*

**Failure 4: long-running loops burn without stop conditions.** Uncapped overnight loops are the canonical token-burn incident; loop length, not model choice, dominates cost. *(Root: budgets treated as ops afterthoughts rather than policy primitives.)*

The root cause across all four is one architectural mismatch: **the artifacts that define the work are not in the loop, and the coordination layer is not typed to the knowledge layer.** The nonoun Factory exists to put the definitions in the loop under mechanical protection, and to make the coordination corpus a typed projection of the lattice — so that selecting work, doing it, verifying it, and improving the definition of it are one closed system.

---

## 3 · First Principles

Four disciplines from the corpus govern every decision below. Each is falsifiable — you can look at a design choice and tell whether it complies.

**📐 Signal is the only currency.** No cell advances and no scope widens without a signal artifact written by the validation path. *If* a ticket reaches `done` without a `signals/` reference produced by a critic the worker could not write, the design is wrong (`evals-and-verification.md`).

**📐 The routing law places every behavior.** Deterministic → a script. One-pass judgment → the main thread with a skill. Multi-step judgment needing isolated context → an agent. *If* the heartbeat poll, the compass scan/rank, or staleness propagation is implemented as an agent, the design is wrong (`layer-methodology.md`). *If* triage, decomposition, or cell advancement is implemented as a hard-coded script, the design is also wrong.

**📐 A rule that matters is a gate, not a sentence.** Standing intent is deterministic enforcement (PreToolUse denies, transition validators, protected paths) or it is advisory. *If* verifier assets, the ledger, or hooks are writable by a worker, the design is wrong (`layer-policy.md`, `the-dawn-of-substrate-engineering.md`).

**📐 Identity excludes state; revision is a tracked transition.** Cell and ticket identities never encode maturity/lifecycle; every state change is a ledgered event, never a silent edit. *If* a cell is renamed when it advances, the design is wrong (`naming-conventions.md`, `layer-spec.md`).

---

## 4 · The Central Reconciliation: Two Lifecycles, One Link

💡 The request names ticket states (draft, active, claimed, in-review, completed, stuck/paused) and asks them to "match our actual lifecycles." The actual lifecycle in the corpus is the **maturity state machine** (`absent → defined → instantiated → validated → operating → regenerating → stale → deprecated`). These are not the same machine, and fusing them is the category error the whole system exists to prevent.

They are two ontological kinds (`agentic-systems-ontology.md`):

| | Ticket | Cell |
|---|---|---|
| **Kind** | Activity (occurrent — a piece of coordination work that *happens*) | Entity + maturity Property (a knowledge asset and its *state*) |
| **Lifecycle** | `draft → active → claimed → in-progress → in-review → done` (+ `blocked`, `paused`, `cancelled`) | the eight maturity states |
| **Lives in** | the coordination corpus (Kanban) | the lattice (`lattice.json`, the grid) |
| **Answers** | "what work is in flight and who holds it" | "what is known, and how well" |

**📐 The link.** Every ticket declares a **target cell** and a **target transition** (`from_maturity → to_maturity`). A ticket's entire purpose is to drive that one maturity transition. The binding rule:

> Ticket `done` ⟹ the target cell's maturity advances to `to_maturity` — **and that advance is itself gated by `gate-signal`.** A ticket cannot reach `done` unless the critic has emitted the signal the maturity transition requires.

This makes the two boards consistent by construction. The Kanban shows *coordination state*; the lattice grid shows *knowledge state*; the ticket is the typed morphism between them. Drift between "claimed done" and "actually validated" becomes structurally impossible: there is one gate, and both transitions pass through it.

---

## 5 · Core Architecture: Kernel / Kit / Instance / Server

📐 The Factory is a three-tier substrate (per `the-dawn-of-substrate-engineering.md`) plus a runtime. Flow of authority is one-way; value flows back the other way.

```
┌─────────────────────────────────────────────────────────────────────┐
│  nonoun-kernel  (plugin · invariant machinery · stateless)            │
│  schemas · maturity state machine · engine · compass · gates · roster │
└───────────────▲───────────────────────────────────────────┬─────────┘
       defines contracts                                implements
┌───────────────┴───────────────┐                  ┌────────▼──────────┐
│  nonoun-kit-corpus             │   …more kits…    │  nonoun-kit-app   │
│  ontology · rubric manifests · │                  │  (test/CI harness)│
│  harness adapters · seed       │                  │                   │
│  patterns  (stateless)         │                  │                   │
└───────────────▲────────────────┘                  └────────▲──────────┘
        binds + accretes                                 binds + accretes
┌───────────────┴───────────────────────────────────────────┴──────────┐
│  Instance repo  (the ONLY tier that holds state)                       │
│  lattice.json · coordination/ · spec/ rubric/ … · signals/ · ledger/   │
└───────────────▲────────────────────────────────────────────┬─────────┘
        reads/writes (single-writer)                     dispatches workers
┌───────────────┴────────────────────────────────────────────▼─────────┐
│  nonoun-server  (Python · the runtime · the dark-factory heartbeat)    │
│  scheduler · dispatcher · store+index · API · SSE/WS · web UI          │
└────────────────────────────────────────────────────────────────────────┘
```

| Tier | Owns | Consumes | Produces | Fails how |
|---|---|---|---|---|
| **Kernel** | cell/ticket/ledger schemas, the two state machines, engine + compass scripts, gate hooks, the base agent roster | nothing project-specific | contracts kits and the server bind to | a kernel that needs editing for a new family has leaked — boundary defect |
| **Kit** | family ontology, rubric manifests, validation **harness adapters**, seed patterns | kernel contracts (`kit.schema.json`, `adapter.schema.json`) | a stamped family capability | adapter that violates the contract → `kit-conform` gate rejects it |
| **Instance** | `lattice.json`, the coordination corpus, all layer artifacts, `signals/`, `ledger/` | kernel + one kit | accreted, validated substrate | state corruption → ledger replay (§15) |
| **Server** | the loop, dispatch, the read-index, the API/UI, worktrees | the instance (as single-writer) + a dispatch adapter | dispatched workers, live views, ledger events | crash → lease expiry + idempotent re-dispatch (§15) |

💡 **Why the server is separate from the kernel.** The kernel is invariant *capability* (it could be vendored into many runtimes). The server is the *operational* tier — the thing that actually polls, holds leases, serves a socket, and supervises subprocesses. Keeping them apart means the same kernel/kit substrate can be driven by this server, by a CI trigger, or by a human running one cell by hand, without change.

---

## 6 · The Coordination Corpus (the ticket substrate)

💡 The coordination corpus is **itself substrate** — a cell (`methodology.system.coordination`) with a schema, a maturity, and the capacity to go stale. It is not a database bolted to the side; it is typed knowledge the Factory maintains about its own work, and therefore git-native and ledgerable like everything else. This is the "central orchestration and coordination corpus" the requirements call for.

### 6.1 📐 Storage model (source of truth + derived index)

- **Source of truth:** files on disk, git-versioned. One file per coordination object under `coordination/`:
  - `coordination/tickets/{ticket-id}.json`
  - `coordination/roadmap/{epic-id}.json`
  - `coordination/issues/{issue-id}.json`
  - `coordination/index.jsonl` — append-only event log of all coordination state changes (a slice of the ledger).
- **Derived read-index:** a SQLite database (`.factory/index.db`) the server rebuilds from the files on boot and updates on every write. **Derived, never authoritative** — deletable and reconstructible, exactly as `lattice.json` is canonical and all grid views are derived (`agentic-systems-ontology.md`, core nouns).
- **Live channel:** the server pushes diffs to connected UIs over SSE/WebSocket on every committed write.

> ⚠️ **OD-001** — File-of-record + SQLite index vs. a single embedded transactional DB as source of truth. Files win on git-nativity, diff-ability, and model-friendliness (JSON is harder for a model to clobber than prose — `autonomous-long-running-systems.md`); a DB wins on concurrent-write integrity. Current resolution: files-of-record with the **server as sole writer** (§6.2), which removes the multi-writer pressure that would otherwise favor a DB.

### 6.2 📐 Single-writer discipline

**REQ-CORPUS-003:** All mutations to coordination state MUST pass through the server. Workers and agents never write ticket state directly. The dispatcher sets `claimed`; the validation path drives `in-review → done`. This eliminates the claim race entirely (no two workers can claim one ticket because workers do not claim — the server assigns) and gives every write a single ordering authority that also appends the ledger event.

### 6.3 📐 Coordination object types

| Type | ID prefix | Purpose | Targets |
|---|---|---|---|
| `feature` | `tkt-` | a unit of advancement delivering user-visible capability | a cell + transition |
| `task` | `tkt-` | a sub-unit of a feature | a cell + transition |
| `bug` | `tkt-` | a correction to an operating/validated cell | a cell, target `regenerating → validated` |
| `chore` | `tkt-` | infra/maintenance work | a factory-infra cell |
| `spike` | `tkt-` | a time-boxed probe to reduce risk (sized to the assumption) | usually `defined`-only, may produce a pattern |
| `epic` | `epic-` | a roadmap container decomposing into tickets | a workflow/system-scope cell |
| `issue` | `iss-` | an observation/anomaly not yet triaged into work | none until triaged |

---

## 7 · The Ticket Lifecycle State Machine

📐 The Kanban columns *are* these states. Every transition is a ledger event; each is guarded by a gate.

```
            ┌─────────┐  triage gate   ┌────────┐   dispatch gate   ┌─────────┐
            │  draft  ├───────────────▶│ active ├──────────────────▶│ claimed │
            └────┬────┘                └───┬────┘                   └────┬────┘
                 │                         │                            │ worker starts
                 │ cancel                  │ (returns on               ▼
                 ▼                         │  unblock)            ┌──────────────┐
            ┌────────────┐                 │                     │ in-progress  │
            │ cancelled  │◀────────────────┴──────┐              └──────┬───────┘
            └────────────┘                        │ cancel              │ artifact ready
                 ▲                                 │                     ▼
                 │                  ┌──────────────┴───┐           ┌────────────┐
   any active ───┘                  │     blocked      │◀──────────│ in-review  │
   state can be                     │ (budget / no-    │  critic   └─────┬──────┘
   cancelled by human               │  progress / dep  │  fails &        │ critic passes
                                     │  regressed)      │  budget gone    │ + signal emitted
   pause/resume is orthogonal ──────│                  │                 ▼
   (sets paused flag, freezes lease)└──────────────────┘           ┌──────────┐
                                                                    │   done   │  ⟹ cell advances
                                                                    └──────────┘
```

### 7.1 📐 Transition table

| From → To | Trigger | Gate (must pass) |
|---|---|---|
| `draft → active` | `ticket-triager` approves, or human | **gate-ticket-ready**: schema valid; `target_cell` exists; `target_transition` legal in maturity machine; `acceptance` bound to a **validated** rubric cell; `budget` set; `dependencies` declared |
| `active → claimed` | server dispatcher (single-writer) | **gate-dispatch**: dependencies validated; budget available this window; concurrency slot free; **autonomy tier permits unattended dispatch of this transition** (§14); worktree provisioned |
| `claimed → in-progress` | worker process started & heartbeating | lease acquired with expiry |
| `in-progress → in-review` | worker reports artifact ready | artifact written to instance; worker exited 0 |
| `in-review → done` | validation path | **gate-signal**: a `signals/{cell}/…` artifact exists, written by the **critic, not the worker**; cell maturity transition recorded atomically with ticket close |
| `in-review → in-progress` | critic fails, budget remains | feedback injected as additional context; attempt counter ++ |
| `* → blocked` | budget exhausted / no-progress signature / dependency regressed / gate denied | reason + diagnostic written; cell **not** advanced; surfaced to compass |
| `blocked → active` | dependency validated, budget extended, or human unblock | the original ready-gate re-checked |
| `* → paused` | human | lease frozen; worker signalled to checkpoint and exit |
| `* → cancelled` | human or superseded-by | worktree torn down; ledgered with rationale |

### 7.2 💡 Why `claimed` is server-set, not worker-claimed

The classic distributed-claim race (two workers grab one ticket) is designed out, not mitigated: the **server is the only writer of `claimed`**, so assignment is serialized by construction. A worker that crashes after assignment is recovered by lease expiry (§15), not by reconciling competing claims. This is the single-writer principle doing safety work.

---

## 8 · The Outer Loop (the 30-second heartbeat)

💡 This is the dark factory's pulse. By the routing law it is **deterministic and lives in the server** — scanning, dependency-filtering, ranking, and dispatching are graph/arithmetic operations over `lattice.json` and the coordination index, never inference. Agents enter only *inside* a dispatched unit.

### 8.1 📐 One tick (default period 30 s, configurable; **REQ-LOOP-001**)

```
on_tick():
  if global_pause: return                               # human kill-switch
  reconcile_leases()                                     # expire dead workers → blocked/active (§15)
  active = store.tickets(state="active")                 # the queue the request names
  ready  = [t for t in active if deps_validated(t)       # partial-order readiness
                              and budget_available(t)
                              and tier_allows(t)]         # trust trajectory (§14)
  ranked = compass.rank(ready)                            # (risk × unlock) / probe_cost  — script
  slots  = max_concurrency - count_running()
  for t in ranked[:slots]:
      worktree = provision_worktree(t.target_cell)        # hermetic git worktree
      store.transition(t, "claimed", writer="dispatcher") # single-writer + ledger event
      dispatch_worker(t, worktree)                        # subprocess via DispatchAdapter
  emit_metrics()                                          # spend/window, queue depth → ledger + UI
```

### 8.2 📐 Compass ranking (deterministic)

`priority(t) = (risk_concentration(t) × unlock_value(t)) / probe_cost(t)`, subject to dependency readiness.

- `risk_concentration` and `unlock_value`: read from ticket fields set at triage; `unlock_value` is computed from the dependency graph (how many cells/tickets this one unblocks) — pure graph traversal.
- `probe_cost`: **measured from the ledger** once history exists (tokens & iterations per prior signal for this cell type), estimated only on cold start (`layer-ledger.md`). The value function goes empirical the moment the ledger has data.

> ⚠️ **OD-002** — Cold-start risk estimation. Before the ledger has history, `risk_concentration` is a human/triage estimate. Options: (a) a one-shot `risk-assessor` agent at triage; (b) fixed priors per ticket type; (c) seed from the kit's pattern corpus. Leaning (c)+(a): kit priors, refined by triage judgment, replaced by ledger evidence as soon as it exists.

### 8.3 📐 Concurrency, backpressure, idempotency

- **REQ-LOOP-004:** max concurrent workers is a policy field; the loop never dispatches beyond it.
- **REQ-LOOP-005:** per-window spend ceilings (tokens/$) halt dispatch when exceeded — the loop *surfaces* the ceiling, it does not burn through it.
- **REQ-LOOP-006:** dispatch is idempotent — re-dispatching a ticket whose worktree/lease already exists is a no-op, so a server restart mid-tick cannot double-launch.

---

## 9 · The Server (Python) and Live UI

### 9.1 📐 Components

| Component | Responsibility | Tech (recommended; **REQ-SRV-001**) |
|---|---|---|
| **API + app** | REST CRUD, lattice status, control surface | FastAPI (async) on uvicorn |
| **Scheduler** | the 30 s heartbeat (§8) | APScheduler interval job or an asyncio task |
| **Dispatcher** | claim, provision worktree, launch/monitor worker subprocess, collect artifacts, invoke critic | asyncio subprocess supervision + a `DispatchAdapter` |
| **Store** | canonical file I/O + SQLite read-index + ledger append | SQLite (`aiosqlite`) over the file-of-record |
| **Stream** | push diffs to UIs | Server-Sent Events (default) or WebSocket |
| **Web UI** | Kanban, lattice grid, ledger feed, agent monitor, roadmap | server-rendered + a thin JS client subscribing to the stream |

### 9.2 📐 The dispatch boundary (integration seam)

> ⚠️ **OD-003 / integration assumption** — The dispatcher launches each worker through a `DispatchAdapter` whose concrete binding targets a **headless agent runtime** (the Claude Agent SDK / headless Claude Code). Exact invocation (flags, session handling, streaming of tool events) is a *kit/instance-level binding pinned against current product docs at build time* — the kernel defines only the contract below. This keeps the architecture correct without hard-coding an interface that may change; verify specifics via the product documentation before implementation.

**📐 `DispatchAdapter` contract:**
```
dispatch(unit) -> WorkerHandle
  inputs : { ticket, target_cell, from→to transition, worktree_path,
             skill_surface (kit skills+agents available),
             budget (iters/tokens/wallclock), hooks_active=true }
  runtime guarantees:
    - runs in the provided hermetic worktree
    - PreToolUse/PostToolUse gates are active (protected paths enforced)
    - emits tool/loop events to a stream the dispatcher tees into the ledger
    - terminates on stop condition (signal | budget | no-progress)
  outputs: exit status, artifact refs, ledger event stream
WorkerHandle: { pid, lease, heartbeat, cancel(), checkpoint() }
```

### 9.3 📐 API surface (representative)

| Method · Path | Purpose |
|---|---|
| `GET /api/tickets?state=` | list/filter (from index) |
| `POST /api/tickets` | create (draft) |
| `PATCH /api/tickets/{id}` | edit fields (draft only for free edits; state changes go through `/transition`) |
| `POST /api/tickets/{id}/transition` | request a lifecycle transition (server applies gate; rejects illegal) |
| `DELETE /api/tickets/{id}` | cancel (soft; ledgered) |
| `GET /api/roadmap` · `GET /api/issues` | roadmap & backlog views |
| `GET /api/lattice` | the grid: cells with `(layer, scope, maturity, signal_refs, staleness)` |
| `GET /api/ledger?cell=&since=` | provenance query |
| `GET /api/agents/running` | live workers, worktrees, budgets burning |
| `POST /api/control/pause` · `/resume` · `/demote/{family}` | the human governance surface |
| `GET /api/stream` | SSE subscription (board diffs, lattice diffs, ledger tail, agent telemetry) |

### 9.4 📐 UI views (**REQ-UI-001..005**)

1. **Kanban board — two lenses over the same work.** Because the factory defaults to maximal decomposition (teams, sub-agents, parallel/orchestrated shapes), one ticket typically spawns a *tree* of activities, so the board renders two switchable lenses:
   - **Ticket lens** — columns = the ticket states (§7); cards are tickets, draggable (a drag is a transition request, gate-checked server-side, refused with a reason if illegal); CRUD modals create/edit the underlying JSON documents. This is the coordination view.
   - **Agent / activity lens** — **swimlanes per agent (or per team)**; cards are **Activities** (`activity.schema.json`) in their live status columns (`queued → running → handed-off → completed`, with `blocked`/`failed`). Each card shows the operation `kind`, the target cell, the `orchestration_shape`/`loop_strategy` badge (so a parallel fan-out worker reads as one), and a live burning-budget indicator. Activities nest by `parent_activity` into a **delegation tree** the lens can expand — the lead, its sub-agents, team peers, and the critic — so progress is visible at *both* the agent level (who is doing what, how deep) and the activity level (each span's status and budget). `team.role` distinguishes lead/worker/critic/specialist; `handed-off` marks a typed handoff between peers.
2. **Lattice grid** — rows = the nine layers, columns = the five scopes; each cell colored by maturity, badged with signal presence and a staleness flag; click → cell detail (artifact, signals, `validated_against` hashes, the tickets and activities targeting it).
3. **Activity / ledger feed** — live append-only stream: dispatches, claims, transitions, signals, blocks, demotions, and activity lifecycle events (`activity-start`, `handoff`, `activity-complete`).
4. **Agent monitor** — the running slice of the agent/activity lens: live workers and team members, their target cells, worktrees, delegation depth, and iteration/token/wall-clock budgets consuming in real time, with cancel/checkpoint controls.
5. **Roadmap & backlog** — epics decomposing into tickets; issues awaiting triage; dependency view.

💡 The UI is a *window onto substrate*, not a separate database. Every card and every grid cell is a rendering of a git-tracked file; every CRUD action is a server-mediated, ledgered write. The board cannot disagree with the repo because the board is the repo, projected.

---

## 10 · The Agent Roster

💡 Each agent is justified by **multi-step judgment needing isolated context** (`layer-capability.md`). Anything deterministic is a script or hook and is listed in §10.4 explicitly as *not* an agent, so the roster cannot quietly accrete actors that should be code. Files live at `{plugin}/agents/*` per modern patterns; each carries a mission, a tool posture (reads / may-write), a model tier, and the reason it is an agent.

💡 **Default topology is maximal decomposition.** Workers are dispatched as **teams** (role-specialized peers — lead, worker, critic, specialist, with typed handoffs) and **sub-agents** (a lead's dispatched children, one cell each) wherever the unit admits real seams — the `collapse-to-justify` posture of `execution-strategy.md`. The roster below lists the *roles*; the execution plan (`dispatch-policy.schema.json`) decides how many of each are instantiated per unit, at maximal width and bounded depth. Each running role is an Activity (§9.4) visible on the agent/activity lens.

### 10.1 📐 Architects (high-stakes definitional judgment)

| Agent | Mission | May write | Tier |
|---|---|---|---|
| `lattice-architect` | design a new instance's lattice; decompose layer×scope; seed cells with honest maturity | `lattice.json` draft, cell stubs | deep |
| `spec-architect` | author/decompose specs (the highest-value cells); check decomposition entailment | `spec/` | deep |
| `rubric-architect` | author **and calibrate** rubric cells (the verifiers); build few-shot exemplar sets | `rubric/` (never `signals/`) | deep |
| `kit-architect` | author/extend a family kit: ontology, rubric manifests, harness adapters, seed patterns | a kit plugin (never the kernel, never instance state) | deep |

### 10.2 📐 Orchestrators (coordination judgment)

| Agent | Mission | May write | Tier |
|---|---|---|---|
| `roadmap-planner` | decompose an epic into a dependency-ordered ticket set; place on the roadmap | `coordination/roadmap/`, draft tickets | deep |
| `ticket-triager` | turn a draft/issue into a well-formed `active` ticket: bind target cell+transition, acceptance→rubric, budget, deps, risk/unlock estimates | draft→active proposals (gate-applied by server) | fast |
| `dependency-arbiter` | resolve contested dependencies / detect cycles the partial-order filter surfaces | annotations on tickets | fast |

### 10.3 📐 Workers (one unit per dispatch, fresh context)

| Agent | Mission | May write | Tier |
|---|---|---|---|
| `cell-advancer` | the engine on **one** cell: `define → create → validate`-readiness; produce the artifact | only the target cell's layer dir + its worktree | fast |
| `cell-validator` (critic) | the **separate skeptic**: run the bound rubric/harness adapter against the artifact; emit the signal | `signals/` (and ONLY the validation path may) | fast/deep |
| `pattern-distiller` | read ledger windows; propose pattern candidates with provenance | `pattern/` drafts | deep |
| `spec-regenerator` | turn ledger deltas + patterns into upstream revision proposals (PRs against spec/rubric) | proposals only; merge is policy-gated | deep |
| `incident-responder` | on a reward-hack/false-pass alarm, perform RCA, propose corrective; the **demotion itself is mechanical** (§14) | incident records, `stale` flags via the proper path | deep |

### 10.4 📐 Explicitly NOT agents (deterministic → scripts/hooks)

The heartbeat poll; the compass **scan** and **rank**; **staleness propagation** (`propagate-staleness` hook); worktree **garbage collection**; lease reconciliation; the ledger append; schema/naming validation. Implementing any of these as an agent violates the routing law and the corpus's "computation by inference is a hallucination surface" rule.

---

## 11 · The Compound Skills

💡 These are the "advanced skills as folders that carry their own agents, rubrics, policies, methodologies." Each is a self-contained capability bundle. A skill folder MAY contain `agents/`, `rubric/`, `policy/`, `methodologies/`, `scripts/`, and `references/` of its own — the unit of reuse is the bundle, not a lone `SKILL.md`. Triggering is model-invoked by description (no commands).

| Skill (folder) | What it manages | Carries its own… |
|---|---|---|
| `lattice-management` | seed/scan/rank/query/visualize a lattice; staleness as graph computation | scripts (scan, rank, propagate-staleness, query); a lattice-health rubric; the lattice-model reference |
| `ticket-orchestration` | the coordination corpus: create/triage/transition; roadmap & backlog; the lifecycle machine | `agents/` (triager, roadmap-planner); the ticket lifecycle **policy**; a decomposition **methodology**; the ticket schema |
| `cell-engine` | the `define→create→validate` engine; dispatch contract | `agents/` (cell-advancer, cell-validator); the engine **methodology**; the signal contract |
| `verification` | rubric authoring, calibration, eval-harness management, reward-hack defenses | `agents/` (rubric-architect, critic); **rubric** manifests; calibration **methodology**; exploit-scan **policy** |
| `regeneration` | ledger distillation → patterns → upstream revision | `agents/` (pattern-distiller, spec-regenerator); the regeneration **methodology**; provenance rules |
| `autonomy-governance` | the trust trajectory; budgets; gate definitions; tier promotion/demotion | the autonomy-tier **policy**; gate scripts; the incident-responder agent |
| `factory-ops` | server/infra maintenance, worktree lifecycle, health, heartbeat config | ops scripts; monitoring **methodology**; the crash/recovery runbook |
| `kit-authoring` | author/extend family kits; conformance to kernel contracts | the kit-architect agent; the kit/adapter schemas; the `kit-conform` checker |

📐 **Folder shape (example, `ticket-orchestration`):**
```
ticket-orchestration/
├── SKILL.md
├── scripts/{lifecycle.py, _validate_ticket.py}
├── agents/{ticket-triager.md, roadmap-planner.md}
├── policy/ticket-lifecycle.policy.json
├── methodologies/decomposition.md
├── rubric/ticket-wellformedness.rubric.json
└── references/coordination-model.md
```

---

## 12 · Naming Conventions (namespaced to `nonoun`)

📐 The typed naming system from `naming-conventions.md`, with `ns = nonoun`. The convention ships as `naming.schema.json` and is enforced by `gate-naming` on every write — it is itself the cell `ontology.fleet.naming`.

| Artifact | Grammar | Example |
|---|---|---|
| Plugin | `nonoun-{tier}[-{family}]` | `nonoun-kernel`, `nonoun-kit-corpus` |
| Skill folder | `{block}-{operation}` | `lattice-management`, `cell-engine` |
| Agent file | `{object}-{actor}.md` | `cell-advancer.md`, `ticket-triager.md` |
| Hook script | `{gateverb}-{invariant}.py` | `gate-signal.py`, `propagate-staleness.py`, `gate-dispatch.py` |
| Cell ID | `{layer}.{scope}.{slug}` | `rubric.workflow.citation-integrity` |
| Ticket ID | `tkt-{ulid}` (epics `epic-`, issues `iss-`) | `tkt-01J9Z…`; references a target cell |
| Signal path | `signals/{cell-id}/{ISO-ts}--{harness}.json` | `…/2026-06-14T09-14--link-check.json` |
| Layer dir | `== layer enum, singular` | `spec/`, never `specs/` |

**Rules carried over:** directories mirror enums byte-for-byte; the namespace never repeats inside members (`nonoun-kernel` ships `cell-advance`, not `nonoun-cell-advance`); `_`-prefixed scripts are private; identity excludes state; casing by class; gateverbs (`gate-`/`emit-`/`propagate-`) carry control semantics. New vocabulary atoms enter only by a ledgered `regenerating` transition on the naming cell.

---

## 13 · Canonical Schemas

📐 The load-bearing contracts. Shipped as files under `nonoun-kernel/schemas/` (the three most central are bundled alongside this spec). `Purpose` columns state *why* each field exists.

### 13.1 Cell (`cell.schema.json` → `$id: Cell`)

| Field | Type | Req | Purpose |
|---|---|---|---|
| `id` | string `{layer}.{scope}.{slug}` | yes | identity; excludes maturity by rule |
| `layer` | enum(9) | yes | modality axis position |
| `scope` | enum(5) | yes | grain axis position |
| `maturity` | enum(8) | yes | the knowledge-state Property |
| `blocked` | bool | yes | condition flag (budget/no-progress) — distinct from maturity |
| `asset_ref` | path | no | the artifact this cell points at |
| `signal_refs` | path[] | no | evidence artifacts; gate-signal checks presence |
| `validated_against` | {cell_id: hash}[] | no | upstream hashes; drives staleness propagation |
| `budget` | Budget | yes | iteration/token/$/wallclock caps for advancing it |
| `attempts` | int | yes | no-progress detection input |

### 13.2 Ticket (`ticket.schema.json` → `$id: Ticket`)

| Field | Type | Req | Purpose |
|---|---|---|---|
| `id` | string `tkt-{ulid}` | yes | coordination identity |
| `type` | enum(feature,task,bug,chore,spike,epic,issue) | yes | routes triage & gating |
| `title` / `body` | string | yes | human-readable intent |
| `state` | enum(draft,active,claimed,in-progress,in-review,done,blocked,paused,cancelled) | yes | lifecycle position (Kanban column) |
| `target_cell` | Cell.id | yes* | the cell this ticket advances (*not for untriaged issues) |
| `target_transition` | {from: maturity, to: maturity} | yes* | the maturity morphism this ticket performs |
| `acceptance` | {rubric_cell: Cell.id} | yes* | doneness bound to a **validated** rubric — not prose |
| `budget` | Budget | yes | the loop enforces it |
| `dependencies` | {tickets: id[], cells_ready: Cell.id[]} | no | partial-order readiness inputs |
| `priority` | {risk: 0-1, unlock: int, probe_cost: number?} | no | compass inputs; probe_cost from ledger |
| `claim` | {worker_id, worktree, lease_expiry} \| null | no | set by dispatcher only (single-writer) |
| `signal_refs` | path[] | no | populated by the critic at in-review→done |
| `provenance` | {created_by, ledger_refs[]} | yes | who/why; every transition appended |
| `timestamps` | {created, updated, …per-state} | yes | flow metrics |

### 13.3 Ledger entry (`ledger-entry.schema.json` → `$id: LedgerEntry`)

| Field | Type | Req | Purpose |
|---|---|---|---|
| `ts` | ISO-8601 | yes | tensed ordering |
| `event` | enum(dispatch,claim,transition,signal,block,demote,regenerate,…) | yes | event-sourced replay |
| `actor` | {kind: human\|server\|agent, id} | yes | accountability; tool-output is never an actor |
| `subject` | {ticket?: id, cell?: id} | yes | what it touched |
| `from`/`to` | state/maturity | no | the change, if a transition |
| `rationale` | string | yes | the *why* — useless-for-regeneration without it |
| `hashes` | {artifact?, validated_against?} | no | staleness + tamper-evidence |

Append-only (`gate-ledger` denies mutation). The `event` enum also carries activity-lifecycle events (`activity-start`, `handoff`, `activity-complete`, `activity-fail`) so the agent/activity lens and monitor materialize from the ledger like everything else. Other kernel schemas: `lattice.json`, `activity.schema.json` (the live agent-work span, §9.4), `roadmap.schema.json`, `Budget`, `kit.schema.json`, `adapter.schema.json`, `naming.schema.json`.

---

## 14 · Safety, Autonomy, and Reward-Hacking Defenses

💡 This is the keystone (`the-dawn-of-substrate-engineering.md`, Part VII): **the line between what the Factory may rewrite and what it may never touch, enforced mechanically.** Everything else is a projection of where that line sits.

### 14.1 📐 The immutable/rewritable boundary

| Side | Members | Enforcement |
|---|---|---|
| **Immutable** (workers deny-on-write; change only via deliberate, ledgered, human-gated transition) | verifier assets (`rubric/`, eval harnesses), `signals/`, `ledger/`, the hooks themselves, `naming.schema.json`, kernel schemas | `gate-verifier`, `gate-ledger`, filesystem perms in the sandbox |
| **Rewritable** (free to improve under protection) | `spec/`, `pattern/`, knowledge corpus, drafts, instance artifacts | normal write, but every change is a ledgered transition |

**REQ-SAFE-001:** A worker process MUST be mechanically unable to write any immutable-side path. A clean scoreboard a worker produced by editing its own verifier is the canonical reward-hack and is designed out, not detected after the fact.

### 14.2 📐 The trust trajectory gates the loop

The loop's `tier_allows(t)` check (§8.1) reads the policy autonomy ladder (`layer-policy.md`). A loop family runs unattended only at the tier its **ledger-measured** track record has earned:

| Tier | What the loop may dispatch unattended | Precondition (from ledger) |
|---|---|---|
| 0 Attended | nothing unattended; every run human-watched | default for a new family |
| 1 Gated | dispatch, but human reviews at `in-review` | verifier validated; false-pass trending down |
| 2 Unattended-in-budget | full `active→done` within budget | false-pass < ~5%; zero reward-hack incidents; caps active |
| 3 Scheduled/long-running | the 30 s heartbeat runs the family lights-out | Tier 2 sustained across a window; hermetic sandbox; tamper-evident audit trail |

**REQ-SAFE-004:** Demotion is mechanical — a reward-hack incident or false-pass spike drops the family a tier and flags its verifier cells `stale`, with no human in the demotion path (humans investigate via `incident-responder`; the demotion already happened).

### 14.3 📐 Defense stack (in force order)

1. **Protected verifier assets** — §14.1, mechanical.
2. **Pristine reference scoring** — each rubric carries ≥1 `[gate]` check computed from reference material the worker cannot reach.
3. **Higher-order/isomorphic checks** — verify properties, not just the extensional pass/fail a worker can game.
4. **Exploit scans** — adversarial review of *passing* runs (a clean board is what a hack produces).
5. **Comprehension-debt guard** — if humans cannot explain merged work, the family drops to attended (`autonomous-long-running-systems.md`).

---

## 15 · Failure, Crash, and Recovery Semantics

📐 Long-running autonomy needs explicit crash semantics, not hope.

| Failure | Detection | Recovery |
|---|---|---|
| Worker crash / hang | lease heartbeat stops | `reconcile_leases()` next tick expires the lease; ticket → `active` (retry, attempts++) or `blocked` if attempts exhausted; worktree GC'd |
| Server crash mid-tick | restart | idempotent dispatch (§8.3) — existing leases/worktrees are adopted, not duplicated; SQLite index rebuilt from files; ledger replayed for in-memory state |
| Budget exhaustion | counters vs. caps | ticket → `blocked` with reason; cell **not** advanced; surfaced to compass and UI |
| No-progress (same failure signature ×N) | attempt diff | ticket → `blocked`; flagged for triage/regeneration |
| Reward-hack / false-pass | exploit scan / independent check disagreeing with critic | incident logged; **family auto-demoted** (§14.2); verifier cells `stale` |
| Upstream cell changed | `propagate-staleness` (hook, deterministic) | every dependent flips to `stale`; tickets targeting them gated until re-validated |
| Merge collision (parallel worktrees) | integration check | scheduling failure, not model failure — the dispatcher serializes merges to one cell; concurrent tickets on the *same* cell are not co-dispatched |

> ⚠️ **OD-004** — Parallel-cell merge strategy at scale. Current rule: never co-dispatch two tickets targeting the same cell; independent cells merge freely in isolated worktrees. Open question is cross-cell consistency when two validated cells were validated against each other's pre-merge hashes — staleness propagation catches it, but the *re-validation ordering* under heavy parallelism needs a policy.

---

## 16 · What Differentiates This System

📐 The architectural argument, not marketing.

| Dimension | Generic agent framework | CI/CD bot | Issue tracker (Jira-like) | **nonoun Factory** |
|---|---|---|---|---|
| Unit of work | a prompt/chain | a pipeline run | a noun-ticket with ad-hoc status | a **cell** advanced by a typed **ticket→maturity morphism** |
| "Done" | model says so | tests green | column moved | **signal** written by a separate critic; maturity advanced through a gate |
| Coordination ↔ knowledge | none | none | none (status ≠ truth) | **typed link**; board cannot disagree with the lattice |
| Self-improvement | none | none | none | **outer loop** regenerates specs/rubrics from the ledger |
| Autonomy | all-or-nothing | scheduled | n/a | **earned, measured, revocable** per family |
| Reward-hacking | unaddressed | n/a | n/a | **mechanical protected-verifier boundary** + exploit scans |
| Source of truth | framework state | pipeline config | a database | **git-native substrate**; UI and DB are derived |

---

## 17 · Anti-Patterns

| Anti-Pattern | Why It Fails |
|---|---|
| Fusing ticket-state with cell-maturity | category error (Activity vs. Property); destroys the drift-detection the typed link provides (§4) |
| Heartbeat/scan/rank as an agent | computation by inference — a hallucination surface; violates the routing law (§10.4) |
| Worker writes its own signal/verifier | the canonical reward-hack; a clean board produced by editing the scorer (§14) |
| Tickets `done` without a signal | "validated by assertion"; the lattice fills with confident claims that don't hold |
| Prose budgets / prose policy | advisory under pressure; uncapped overnight loops are the canonical burn incident |
| Database as source of truth | breaks git-nativity, diff-ability, ledger replay; the model can't reason over opaque rows like it can over JSON |
| Multi-writer ticket claims | reintroduces the claim race the single-writer server design eliminates (§7.2) |
| Renaming cells/tickets on state change | identity-encodes-state; a drift generator; breaks `validated_against` hashes |
| Grid-filling the meta-system | building dashboards/kits before one cell reaches `validated` is grid-filling the factory itself (§19) |

---

## 18 · Open Decisions

| OD | Title | Status | Affects |
|---|---|---|---|
| OD-001 | File-of-record + index vs. transactional DB as source of truth | DECIDED (files + single-writer) | §6 |
| OD-002 | Cold-start risk estimation before ledger history | EXPLORING | §8.2 compass |
| OD-003 | Concrete `DispatchAdapter` binding to the headless runtime | OPEN (verify against current product docs) | §9.2 |
| OD-004 | Cross-cell re-validation ordering under heavy parallelism | OPEN | §15 |
| OD-005 | Fleet scope: one server per instance vs. one server orchestrating many instances | OPEN | §5, scaling |
| OD-006 | Human approval granularity for `spec-regenerator` merges (per-PR vs. policy-class auto-merge at high tiers) | OPEN | §10.3, §14 |

---

## 19 · Bootstrapping Arc & Current Status

📐 The Factory is built along the substrate-engineering arc; **each phase earns the next — skipping ahead is the canonical way self-improving systems fail.**

- **Crawl — Instrumentation.** Kernel schemas (`cell`, `ticket`, `ledger`), `gate-transition`/`gate-signal`/`gate-naming`/`gate-verifier`, the compass scan/rank scripts, the server skeleton with the heartbeat **disabled**, and the `cell-advancer` + `cell-validator` pair. **Milestone:** one corpus-family cell driven `absent → validated` *by hand through the API*, every gate firing, a real signal on disk. No UI beyond a list, no second kit, no auto-dispatch.
- **Walk — Delegation.** Enable the heartbeat at Tier 1 (dispatch, human reviews at `in-review`); add the Kanban + lattice-grid UI and the live stream; budgets and no-progress binding. **Milestone:** a full vertical slice reaches `done` unattended within budget, false-pass under threshold, zero reward-hack incidents.
- **Run — Regeneration.** Turn on `pattern-distiller` + `spec-regenerator`; the outer loop proposes upstream revisions; promote the corpus family toward Tier 2. **Milestone:** a ledger-driven revision to a spec/rubric cell lands through a deliberate transition and the next run is measurably better.
- **Fly — Dark Factory.** Tier 3 lights-out at fleet scale; the second kit (`nonoun-kit-app`) proves the kernel/kit boundary (adding it must require **zero kernel edits** — the boundary's falsification test). **Milestone:** the Factory improves its own definitional knowledge across a window with substrate-accretion as the watched metric and reward-hack incidents held at zero.

**Status — what is complete:** nothing is `validated`; this document is itself a `defined` cell (`spec.system.nonoun-factory`). **In progress:** this spec. **Not yet addressed:** OD-002..006; the concrete dispatch binding; the kit-app harness; multi-instance fleet topology.

---

## 20 · Requirements Index

| ID | §  | Summary |
|---|---|---|
| REQ-CORPUS-003 | 6.2 | All coordination mutations pass through the single-writer server |
| REQ-LOOP-001 | 8.1 | Configurable heartbeat (default 30 s) scans `active` tickets and dispatches |
| REQ-LOOP-004 | 8.3 | Never dispatch beyond max-concurrency policy |
| REQ-LOOP-005 | 8.3 | Per-window spend ceilings halt (not burn through) dispatch |
| REQ-LOOP-006 | 8.3 | Dispatch is idempotent across server restarts |
| REQ-SRV-001 | 9.1 | Python async server (FastAPI/uvicorn) hosting API + UI + stream |
| REQ-UI-001..005 | 9.4 | Kanban, lattice grid, ledger feed, agent monitor, roadmap views, live-streamed |
| REQ-SAFE-001 | 14.1 | Workers mechanically unable to write immutable-side paths |
| REQ-SAFE-004 | 14.2 | Autonomy demotion is mechanical and ledger-driven |
| GATE-* | 7.1,14 | gate-ticket-ready, gate-dispatch, gate-signal, gate-verifier, gate-ledger, gate-naming |

> *The board shows coordination state; the grid shows knowledge state; the ticket is the typed morphism between them. The loop selects and dispatches; the critic alone validates; the ledger remembers; the outer loop improves the definitions — and a human decides only what the factory is allowed to rewrite.*
