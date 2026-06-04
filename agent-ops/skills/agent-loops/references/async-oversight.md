# Async / Background / Scheduled Agents & the Oversight Model

**One-liner.** Dispatch agent work to run _detached_ — backgrounded, cloud-sandboxed, or cron-scheduled — so the human is freed from the turn, then keep it safe with an **oversight plane**: a monitorable task list, a permission/network containment policy, and an **inbox** where paused or completed runs are triaged, approved, edited, or killed. Fire-and-**monitor**, never fire-and-forget.

**Where it sits in the taxonomy.** This is **not a loop body — it is an orthogonal wrapper on the control plane.** Per `composition.md`, the loop families (Ralph, plan-execute, ReAct/Reflexion, evaluator-optimizer, orchestrator-workers, auto-research, debate, self-improving, spec-driven) answer _what the loop does each iteration_. Async/oversight answers an orthogonal question: **WHEN, WHERE, and HOW-SUPERVISED a loop runs** — synchronously in the foreground attached to a human, or detached and reviewed at a boundary. Any loop body can be wrapped by this layer; wrapping it changes neither the iteration logic nor the gate's _content_, only **when** verification happens (deferred, out-of-band) and **who** is watching (nobody, mid-run). It composes _over_ a topology the way `control-plane.md` composes _into_ one. Because the human leaves the turn, this family is where the **builder/operator boundary is most load-bearing**: the mechanism (dispatch, isolation, containment, kill) is the builder's seat — but the _experience_ of supervising a fleet (trust calibration, triage cognitive load, steerability of a paused run) is scored by the sibling `agentic-ux` skill. Build the oversight plane here; hand the supervision UX there.

---

## Mechanism — the control flow

Two coupled control loops run concurrently: a **DISPATCH/EXECUTION** loop (per task, detached) and an **OVERSIGHT** loop (human-driven, over the fleet).

### DISPATCH / EXECUTION (per task)

1. **Create + scope + isolate.** A task is created with a scoped prompt and an **isolation boundary**. Granularity spans: in-process (a daemon thread running a subprocess — Claude Code `BackgroundManager.run()` returns immediately with a `task_id`) → git **worktree** (Cursor/Codex local, isolated files on a shared machine) → full isolated **VM/sandbox** with its own terminal, browser, shell, and test runner (Cursor cloud, Devin managed session, Codex cloud).
2. **Dispatch non-blocking.** Control returns to the caller (human or orchestrator) immediately. The agent loop itself stays single-threaded — _"the model thinks while the harness waits"_; only subprocess I/O is parallelized. The agent runs to a **natural stopping point** or to a configured **interrupt/breakpoint**.
3. **Trigger surface is pluggable.** Interactive (`Ctrl+B` to background a running subagent) · API/CLI · chat-ops (`@cursor` / `@codex` mention in Slack/Linear/GitHub) · event (CI failure, new bug in a triage channel) · **schedule** (cron / "scheduled agent" / routine). A scheduled agent is the _same dispatch primitive_ with a time/event trigger instead of a human one.
4. **Containment runs throughout.** Because no human is attached to answer prompts, backgrounded Claude Code agents run on **already-granted session permissions** and **auto-deny** any tool call that would otherwise prompt. Cloud sandboxes **cut network egress during the task phase** (allowing it only in a setup phase) so a detached agent cannot exfiltrate or call out mid-run.
5. **Materialize a reviewable artifact.** On completion the result is surfaced asynchronously: an injected notification into the parent conversation (`[bg:task_id]` snippet, capped ~500 chars in Claude Code, full output retained for inspection); a **pull request** with diff + conversation log + auto-generated demo/screenshot/video (Cursor cloud, Codex, Faire's Playground); or a **session link** the human opens later.

### OVERSIGHT (concurrent, human-driven)

| Stage | What it does |
| --- | --- |
| **A — Monitor** | A unified surface lists all in-flight tasks with status, token/ACU burn, and progress (Claude Code `/tasks`, Cursor unified sidebar local+cloud, Devin session list, Codex queue). This is fire-and-**monitor**. |
| **B — Interrupt/Control (while running)** | Inspect a live task, message it directly (Devin per-session link), sleep/pause it, or terminate/kill it (Devin sleep-or-terminate, `KillShell` for a backgrounded bash). |
| **C — Human-IN-the-loop gate (pause-and-ask)** | For sensitive actions the agent issues an **interrupt BEFORE acting**; state is **checkpointed** (LangGraph persistence / durable runtime) so the run can sit paused indefinitely and resume _at the exact node_. The human picks from a small fixed action set — **accept / edit** (modify tool args) **/ reject** (explanation injected back) **/ respond** (skip the call; human text becomes the tool result) — via `Command(resume={decisions:[...]})` keyed to a `thread_id`. This is the _only_ pattern that pauses an autonomous run safely **without** a human watching continuously. |
| **D — Agent inbox** | The triage UI over a _fleet_ of such interrupts. It connects to the deployment (URL + API key + graph/assistant id), **fetches** the queue of paused runs, renders each `HumanInterrupt` (`action_request{name,args}` + `config{allow_accept,allow_edit,allow_respond,allow_ignore}` + markdown description), lets the human pick, and **posts** the `HumanResponse` to resume. **One human triages many agents** — the inverse of one agent, many tools. |
| **E — Post-hoc review (human-ON-the-loop)** | For _completed_ detached work, review is the PR/diff/demo gate **at merge time, not at action time**. The human supervises outcomes and intervenes **by exception** (request changes, re-dispatch, revert) rather than approving each step. |

### ORCHESTRATION OVER A FLEET (the "manage-the-managers" variant)

A coordinator decomposes a job into scoped pieces, spins up **N isolated sessions** (Devin "~10 at a time"; Cursor up to 8 agents on one problem, then auto-pick best; Faire's "Swarm" scrapes targets to S3 and **fires the next agent as the previous merges**), tracks per-child resource burn, can **sleep/kill divergent children**, compiles results, and can **read child trajectories to learn**. Self-messaging / scheduled follow-ups let a coordinator wake itself to re-check progress. _(This is orchestrator-workers wrapped by async; nest per the Composition section.)_

---

## When it fits / When it fails

| WHEN IT FITS | WHEN IT FAILS |
| --- | --- |
| Long-running (minutes–hours), read-heavy or independently verifiable work — code review, test/security/dependency scanning, doc audits, large mechanical migrations, bug triage — where the human shouldn't be blocked watching | Tasks with tight mutual dependencies or **shared mutable state** — detached agents step on each other unless rigorously isolated; naive backgrounding corrupts state |
| High-volume repetitive work that benefits from parallelism: thousands of small autonomous runs/week (CI-failure fixes, PR routing, channel-driven bug triage) where each result is a small reviewable PR | Results that are **not cheaply verifiable** — if reviewing the output costs as much as doing the work, async is a _net loss_; the review queue becomes the new bottleneck |
| Throughput-bound orgs where the bottleneck is **human attention, not agent capability** — one engineer supervising a fleet (Faire: 18-month migration → 1 engineer; 2000+ runs/week) | Work needing **mid-run approvals** fired into the background — with no human attached, Claude Code **auto-denies** and the agent silently fails/degrades |
| Recurring/maintenance work with a natural schedule (nightly dependency bumps, scheduled flaky-test triage, daily digest agents) — the cron/routine variant | **Fire-and-forget** (skipping the monitor + review plane) — silent failures, runaway token/ACU burn, drifted PRs nobody catches, unbounded blast radius |
| Sensitive/irreversible actions present, so an explicit **pause-and-approve** gate (HITL interrupt + inbox) must wrap the autonomy | **Over-parallelization past the human triage ceiling** — 50 agents finishing at once with no inbox/prioritization → humans rubber-stamp, defeating the safety model |
| Tasks decompose cleanly into independent, isolatable units (one worktree/VM per unit) | Network-dependent tasks under strict egress rules — if the agent must install/fetch mid-task but egress is sealed, it stalls (needs staging into setup) |
| You want **ensemble/best-of-N** — run the same problem in several parallel sandboxes, pick the best | Interactive, fast back-and-forth work — detachment adds latency and loses the tight loop; keep foreground. Scheduled/cron agents firing on **stale assumptions** (branch moved, API changed) with no liveness check |

**The decisive test:** async pays off **only when the review gate is cheaper than the work.** If verifying the detached output is as expensive as producing it, do not detach.

---

## Key parameters (the knobs a builder sets)

The highest-value section. Each knob has a default and a rationale. Defaults assume the common case — a code-touching, independently-verifiable task supervised by one engineer; deviate with a reason.

| Knob | Default | Rationale |
| --- | --- | --- |
| **Isolation boundary granularity** | **git worktree** for code tasks; **full VM/sandbox** if the task runs untrusted code, needs its own browser/test-runner, or fans out wide; in-process thread _only_ for short read-only side-quests | Sets blast radius and _true_ parallelism. In-process shares fs+permissions (can collide); worktree isolates files on a shared machine; VM isolates fs+net+tools (safe to run many). Wrong choice corrupts shared state or wastes resources. |
| **Parallelism ceiling (concurrent tasks)** | **≤ what one human can actually triage** — start at **~5–10** detached tasks/operator; cap fleets at the real-system numbers (Devin ~10, Cursor ~8 on one problem) | The binding limit is **review bandwidth, not compute**. Past the triage ceiling the inbox saturates and the gate erodes to rubber-stamping. Size to sustainable triage, not to available cores. |
| **Permission / containment policy** | **Minimal pre-granted allowlist** scoped to the task; **default-deny** on would-prompt calls; _never_ background work that needs a mid-run approval | The core safety knob. A backgrounded agent has no human to answer; too tight → silent auto-deny stall, too loose → unsafe autonomy. If the task _needs_ a prompt mid-run, it belongs in the foreground or behind a HITL interrupt — not the background. |
| **Network egress policy** | **Sealed during the task phase; all network needs staged into a setup phase** | Cutting egress mid-run prevents exfiltration/uncontrolled calls by a detached agent (Codex/cloud model). The cost: no mid-task installs/fetches — stage every dependency into setup and accept a sealed task phase. |
| **Oversight mode: human-IN vs human-ON the loop** | **ON-the-loop** (outcome review by exception at PR/merge) for _reversible_ work; **IN-the-loop** (pause-and-approve each sensitive action) for _irreversible/sensitive_ work | IN = max control, low throughput, requires checkpointing + inbox. ON = max throughput, requires strong verification + reversibility. Picking wrong either throttles a safe task or under-guards a dangerous one. Default to the cheaper ON mode _only_ when the action is reversible and the artifact is cheap to review. |
| **Interrupt policy (which actions gate, allowed decisions)** | Gate **writes / irreversible / external-effect** tool calls (`write_file=true`, `execute_sql={allowed:[approve,reject]}`); leave **reads ungated** (`read=false`); offer **accept/edit/reject/respond** on gated calls | Defines exactly where autonomy stops and the human starts. Gating reads wastes human attention; not gating writes is the blast-radius hole. Map tool → approval requirement explicitly. |
| **Checkpoint / persistence backend** | **Durable store** (Postgres saver / durable runtime), _never_ in-memory, whenever HITL or an inbox is in play | Determines whether a paused run survives long enough for a human to reach it. In-memory loses state on restart → the human's eventual response can't resume → **HITL silently broken in prod**. Durable lets a run sit paused for hours/days and rehydrate at the exact node. |
| **Result artifact + review gate** | **PR + diff + full conversation log**, plus an **auto-generated demo/screenshot/video** for any UI change; agent must **run its own tests in-sandbox first** | The richer the artifact, the cheaper the review — and review cost decides whether async is a net win. Surface a _tested candidate_, not raw output. The auto-demo and tested-in-sandbox pattern exist precisely to lower review cost. |
| **Trigger surface** | **Chat-ops `@mention` + event (CI/bug)** for on-demand; **cron/routine** for maintenance | Determines who/what can launch work and how it integrates into existing workflows. Scheduled triggers turn the same primitive into always-on maintenance. |
| **Termination / kill & resource budget** | **Per-task timeout** (~300s default in Claude Code, raise for long migrations) · **output cap** (~50k chars) · **token/ACU ceiling** · an **operator kill/sleep** control | Detached runs can diverge or burn unbounded. A per-task budget + a kill/sleep path lets a runaway be stopped _without taking down the fleet_ (Devin sleep-or-terminate, `KillShell`, `/tasks`). |
| **Schedule / liveness check (cron agents)** | A **pre-flight precondition/liveness check** every run (branch is current, API contract unchanged, target still exists); **sane cadence** (no tighter than the work's natural rhythm) | Scheduled agents run unattended against a _moving_ codebase. Without a liveness guard they act confidently on stale assumptions on a schedule — the worst kind of silent failure. |

---

## Termination · Context · Verification (this family)

Defined cross-cuttingly in `control-plane.md`; this section names how those substrates **specialize** for detached execution. Do not re-derive them here.

### Termination

Per `control-plane.md`'s layered stop, but the layers are **distributed across two loops**. A detached task halts when **any** of:

- **Natural completion** — emits report / commits branch / opens PR + surfaces its artifact.
- **Interrupt/breakpoint** — agent hits a gated action and **PAUSES** awaiting a human decision (state checkpointed, _not_ terminated). This is the async-specific stop the other families don't have.
- **Hard caps** — per-task timeout (~300s), output cap (~50k chars), or token/ACU ceiling exhausted.
- **Operator stop** — explicit sleep or kill (Devin sleep-or-terminate, `KillShell`, `/tasks`).
- **Auto-deny dead-end** — backgrounded agent needs a would-prompt permission, is auto-denied, stops/degrades. _(A degenerate stop — guard against it, don't rely on it.)_
- **Coordinator boundary** — all decomposed children complete and compile, or pipelining fires the next as the previous merges.
- **Schedule boundary** — cron agent completes its run and sleeps to the next tick (or a self-scheduled follow-up wakes it).

### Context strategy

**Isolated per detached task, not accumulated into the dispatcher** — the subagent context-isolation rationale (`control-plane.md` context axis) applied to _detached_ execution. Each background/cloud/managed session gets a **clean, narrow slate**: its own scoped prompt, shell, fs, and (VM mode) browser/test-runner — preventing cross-task pollution and keeping the parent's window from bloating with sub-task transcripts. Only a **compact result** re-enters the parent (the ~500-char injected snippet, or a PR + log + diff pulled up by reference). The **full trajectory is preserved out-of-band** and addressable by session link — inspectable/replayable without ever loading it into the live loop. For HITL/inbox flows the **durable checkpoint is the carried state**: the entire graph state is serialized at the interrupt and rehydrated on resume, so context survives an arbitrarily long human-review gap. A coordinator may deliberately **pull** child trajectories post-hoc to learn — pull-on-demand, never always-resident.

### Verification gate

**Deferred and out-of-band — the defining trait.** Because no human watches the run, correctness is checked **at the boundary, not during** (`control-plane.md` verification axis: the gate's _trust ranking_ is unchanged — oracle > ground-truth > judge/panel > self-grade — only its _timing_ moves). Two gate types:

1. **Pre-action gate (human-IN-the-loop):** the interrupt _is_ the gate — sensitive calls are checkpointed and an accept/edit/reject/respond decision is required before execution; nothing risky runs unverified.
2. **Post-hoc artifact gate (human-ON-the-loop):** the run must self-package into a reviewable artifact — PR + diff + full conversation log + (ideally) auto-demo/screenshot/video — approved at merge by a human, a downstream review agent, or CI.

The agent is expected to **verify its own work in-sandbox first** (write code, run tests, capture a demo) so the human reviews a _tested candidate_. **Hard rule:** async only pays off when this gate is **cheaper than the work** — the auto-demo and tested-in-sandbox patterns exist to lower review cost. Ensemble-pick (run N, auto-select best) layers on top. **Standing risk: gate erosion** — when the review queue outruns human bandwidth, the gate degrades to rubber-stamping and the safety model collapses.

---

## Failure modes (each with its guard)

| Failure mode | Guard |
| --- | --- |
| **Fire-and-forget** — no monitor/review plane → silent failures, runaway token/ACU burn, drifted/abandoned PRs | Mandate the monitor surface (`/tasks` / unified sidebar) + a closing review gate; _no detached dispatch without both_. |
| **Auto-deny silent stall** — backgrounded agent needs a would-prompt permission, auto-denied (no human), quietly fails/degrades | Pre-grant a _minimal-yet-sufficient_ allowlist; if a mid-run approval is genuinely needed, route through a HITL interrupt or keep the task foreground. Surface auto-deny events in the monitor, don't swallow them. |
| **Review-queue saturation / oversight debt** — more completed runs than humans can triage → rubber-stamping → gate erodes, unsafe changes ship | Cap the parallelism ceiling **at or below** sustainable triage bandwidth; add **SLA/prioritization** to the inbox; make artifacts cheap to review (auto-demo, tested-in-sandbox). |
| **Parallel state collision** — under-isolated agents (in-process / shared worktree) clobber each other's files/state | Match the isolation boundary to concurrency — worktree or VM per unit; never run shared-mutable-state tasks in-process. Bug surfaces only under concurrency, so test concurrently. |
| **Blast-radius blowout** — detached agent with too-broad permissions or live egress does damage with no human to stop it mid-run | Minimal pre-granted allowlist + **sealed task-phase egress**; gate writes/irreversible calls behind an interrupt; keep a kill/sleep control live. |
| **Sandbox-egress stall** — task needs a mid-run install/fetch but egress is sealed | Stage _all_ network needs into the **setup phase**; accept a sealed task phase. Surface the stall in the monitor rather than hanging silently. |
| **Lost/expired checkpoint** — non-durable persistence loses paused state on restart → human's response can't resume → HITL silently broken | Use a **durable** checkpoint store (Postgres saver / durable runtime) whenever HITL or an inbox is in play; never in-memory in prod. |
| **Stale scheduled run** — cron agent fires against a moved branch / changed API with no liveness check, confidently does the wrong thing on a schedule | A **pre-flight precondition/liveness check** every run; abort (don't proceed) if preconditions fail. |
| **Orphaned interrupts** — paused runs pile up in the inbox with no SLA/prioritization → agent blocked indefinitely, work never completes | Assign each interrupt an **SLA + priority**; alert on aging interrupts; treat the inbox as a queue with backpressure, not a dead-letter box. |
| **Coordinator runaway** — fleet orchestrator spawns past the ceiling, exhausts resources, no sleep/kill control | Hard parallelism cap + per-child budget + an operator sleep/kill path to reel in divergent children (Devin sleep-or-terminate). |
| **Notification truncation blind spot** — parent acts on a ~500-char snippet, missing a failure buried in the body | Treat the snippet as a _pointer_, not the result; require inspecting the full retained trajectory before any consequential decision; never auto-merge off the snippet alone. |
| **Latency tax misapplied** — interactive/fast-iteration work pushed to background, adding round-trips, losing the tight loop | Apply the async-fit test up front: detach _only_ long-running, independent, verifiable work; keep interactive work foreground. |

---

## Composition — how it nests / wraps other layers

This family is an **orthogonal wrapper**, so it composes by _enclosing_ a loop body rather than sitting inside one (see `composition.md`):

- **Wraps any loop body.** A Ralph loop, a plan-execute run, an evaluator-optimizer cycle, or a ReAct agent can each be dispatched detached. The wrapper supplies dispatch + isolation + containment + monitor + review; the inner topology is unchanged. _Inheritance:_ the wrapped loop still instantiates all of `rubric-loop-control` (termination, context, verification, budget, durability) — async just relocates verification to the boundary and _requires_ the durability gate (durable checkpoint) that foreground loops can sometimes omit.
- **Wraps orchestrator-workers (the fleet/coordinator variant).** "Manage-the-managers" = orchestrator-workers (`orchestrator-workers.md`) where each worker is a _detached_ isolated session and the coordinator gains async controls (per-child budget, sleep/kill, read-trajectory-to-learn, self-scheduled follow-ups). Name the nesting: _outer = async/oversight, inner = orchestrator-workers; the worker dispatch is the detached primitive._
- **Wraps auto-research fan-out.** Breadth-first research subagents (`auto-research.md`) dispatched detached, each in its own context, results compiled into a cited report at the boundary — the canonical isolated-context fan-out _plus_ an async oversight plane.
- **Hosts an ensemble/best-of-N gate.** Run the same task in several parallel sandboxes and auto-select the best (ties to `debate-ensemble.md`'s aggregation) — a verification strategy layered on top of detached dispatch.
- **The cron/scheduled variant** is the same primitive with a time/event trigger; it adds exactly one obligation over the on-demand variant — the **schedule liveness check** — and otherwise inherits this whole control flow.

**Where it does NOT belong:** it is not itself a loop you'd pick from the router's body column. The router selects the _topology_; this wrapper is chosen _separately_ when the answer to "should the human stay on the turn?" is **no** (long-running, independent, verifiable, throughput-bound). A request that is purely "which loop body" never resolves to this file alone.

### Scoring & the builder/operator hand-off

This family has **no own family rubric.** Score it with the cross-cutting **`rubrics/rubric-loop-control.md`** — every detached run must still pass `C1 termination-stack` (the layered + kill/sleep stop), `C2 budget` (per-task caps), `C3 verification-gate` (now boundary-deferred), and especially **`C7 durability-idempotency`** (the durable checkpoint that makes HITL/inbox work) and `C8 observability` (the monitor surface). The wrapped _inner_ topology additionally loads its own family rubric per `rubrics/rubric-manifest.json`.

**Everything about the _supervision experience_ hands off to the sibling `agentic-ux` skill.** This file builds the oversight _mechanism_ — dispatch, isolation, containment policy, interrupt map, kill control, durable checkpoint. It deliberately does **not** score: whether the operator _trusts_ the fleet, whether triage cognitive load is sustainable, whether a paused run is _steerable/interruptible_ in a way that feels safe, whether the inbox is _observable_ as a human experience, whether reversibility is legible to the person at the merge gate. Those are the sibling's `agentic-ux` dimensions (trust, control, observability, steerability, reversibility, cognitive load). **Rule of thumb:** if the question is "_does this oversight plane exist and is it mechanically sound?_" → here (`rubric-loop-control`). If it is "_what is it like to supervise this fleet, and will a human stay calibrated?_" → hand to the sibling `agentic-ux` skill. Build the plane; let the sibling judge the seat.

---

## Primary sources

| Title | URL |
| --- | --- |
| Claude Code — Background tasks (BackgroundManager, `/tasks`, notification injection, timeout/output caps, single-threaded harness) | <https://github.com/shareAI-lab/learn-claude-code/blob/main/docs/en/s08-background-tasks.md> |
| Claude Code Async: Background Agents & Parallel Tasks (claudefast) | <https://claudefa.st/blog/guide/agents/async-workflows> |
| LangChain — Human-in-the-Loop middleware (docs) | <https://docs.langchain.com/oss/python/langchain/human-in-the-loop> |
| LangChain — Agent Inbox (open-source README) | <https://github.com/langchain-ai/agent-inbox/blob/main/README.md> |
| Cursor — Faire doubles PR throughput with Cloud Agents | <https://cursor.com/blog/faire> |
| Cognition — Devin can now manage Devins | <https://cognition.ai/blog/devin-can-now-manage-devins> |
| OpenAI — Codex cloud (developer docs) | <https://developers.openai.com/codex/cloud> |

**Confidence note.** The _mechanisms_ (in-process background dispatch, the HITL interrupt/resume control flow, the agent-inbox schema, sandbox egress sealing) are **empirically-supported** — documented in the primary sources above. The fleet-scale economics (Faire's 2000+ runs/week, 18-month → 1-engineer migration; Cursor's >30% agent-authored merged PRs) are **vendor-reported single-org outcomes** — directionally strong, not independently benchmarked; treat the specific multipliers as practitioner-folklore until reproduced. The parallelism-ceiling defaults (~5–10/operator) are **practitioner-folklore** calibrated to the cited caps, not a measured optimum.
