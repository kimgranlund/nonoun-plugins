# Changelog — dev-server

The dev-factory runtime (FastAPI/uvicorn over the stdlib ops layer). Not a plugin — it ships in the dev-factory
marketplace and is versioned with the kernel it serves. Format: [Keep a Changelog](https://keepachangelog.com/).

## 2026-06-15 — orchestration + observability: real teams, token-burn graph, roadmap, elapsed/effort

- **The planned sub-agent team now EXECUTES, not just records.** `HeadlessClaudeAdapter`: a `team` delegation
  plan makes the worker an ORCHESTRATOR — the prompt instructs decompose + delegate to sub-agents via the Task
  tool to the planned `max_depth` at `parallelism`, and `_allowed_tools` adds `Task` so it can spawn them. The
  activity ledger records the REAL `depth` (the plan's, not `0`) + `parallelism` + `model_tier` + `reasoning_effort`
  (dev-kit-app plans `orchestrator-workers` / depth 2 / parallelism 2 for capabilities). Cross-cell parallelism was
  already real (the heartbeat's concurrency); now the within-cell team is wired.
- **Token-burn graph.** Dispatch stamps `model_tier` + `reasoning_effort` onto the spend metrics; a **15s poll**
  (`_wire_token_poll`) snapshots cumulative tokens (+ USD) to `run/token-snapshots.jsonl`, attributed **per model
  tier + per reasoning effort**, and streams a `tokens` SSE. `GET /api/tokens` serves the series; a new **Tokens**
  view draws a realtime SVG area chart (cumulative total + per-model lines) with per-model / per-effort breakdown bars.
- **The roadmap is hydrated.** The cold-start planner now creates one **epic per milestone** (SPEC · CAPABILITY ·
  SHIP) with its tickets nested, so the Roadmap view fills in.
- **Elapsed time + estimated effort.** The claim stamps `claimed_at` (materialized); the Agents view shows a **live
  per-worker elapsed timer** (a 1s clock, no round-trip) + a **probe-cost token ETA** on each worker. `app.js?v=7`.
- api/app/store/dispatch selftests + the `debug-coldstart` replay assert the team ledger, the token attribution,
  the roadmap epics, and `claimed_at`; server-smoke covers `/api/tokens`.

## 2026-06-15 — dashboard richness: a milestone/ship progress strip

- **`api.milestones(d)` + `/api/status.milestones`** — a build-progress rollup the dashboard renders: the
  SPEC · CAPABILITY · SHIP stages (each `done/total`), whether the `capability.system.app` integrator has
  validated (`shipped`), and `spec_revisions` — the count of ledgered spec regenerations (the visible trace of
  the bi-directional loop). Generic over any lattice (a per-layer rollup), surfacing the app-building milestones
  when present. The UI header gains a colour-coded strip beside the work-state chip — `SPEC 1/1 › CAPABILITY
  2/3 › SHIP` with a `⟲ n` spec-revision badge — so the cockpit answers "where is the build, and has it shipped?"
  at a glance. `app.js?v=5`. api/app selftests + server-smoke cover the new field.

## 2026-06-15 — the code-authoring adapter (shippable software, DF-9)

- **`dispatch.py` authors real multi-file source.** `_authoring_for(cell)` reads the bound kit's `authoring`
  declaration; for a multi-file layer (dev-kit-app `capability`) the `MockAdapter` + `HeadlessClaudeAdapter._prompt`
  author source files into the cell's **directory** (industrial module boundaries, pure-logic ES modules + a thin
  shell) graded by the cell's per-cell `verify.mjs` — the worker is gate-denied from writing that harness
  (dev-kernel 0.2.4). Doc cells (dev-kit-corpus) stay single-`.md` (back-compat). This is the DF-9 fix that turns
  a "markdown lattice" into shippable software; the `/debug/` harness drives it through milestone rubrics to a
  shipped integrator. dispatch selftest covers the multi-file routing + the worker-protected harness.

## 2026-06-15 — two operator surfaces (the ralph-loop debugging system)

Two shipped features that make the autonomous loop watchable and steerable in real time, exercised by the new
`/debug/` ralph-loop harness (repo-root `debug/`).

### Added

- **5-second operator-input channel, folded into the loop's reasoning.** `POST /api/input` enqueues a steering
  message to `run/input.jsonl` (append-only intake); a **separate 5s asyncio poll** (`_wire_input_poll`,
  independent of the 30s dispatch heartbeat and of `HEARTBEAT_ENABLED`, so steering works even in Crawl) drains
  new intake into `run/guidance.json` and streams a `guidance` SSE event. `HeadlessClaudeAdapter._prompt` folds
  the latest guidance into each **newly dispatched** worker's prompt. **Security:** both files sit under `run/`,
  which `_gates.VERIFIER` already denies to gate-wired workers — so guidance is operator→loop only, by
  construction (a worker cannot forge it; proven in the `debug-coldstart` replay). **Honest limit:** a running
  one-shot `claude -p` worker can't be steered mid-flight — guidance reaches the *next* dispatch + the
  orchestrator. UI: a persistent **Steer dock** (`df-steer`) with a streaming guidance feed; its input survives
  the 5s updates (static template + a separate feed effect + direct-DOM toggle).
- **Two-mode ticket creator (tabs: Structured · Prompt · Instruction).** The create-ticket modal (`df-modal`)
  gains an intake-mode tab control. **Prompt** = a free-form brief that parks for the cold-start planner to
  triage into structured tickets; **Instruction** = literal steps that the server also folds into the guidance
  buffer (so the next worker sees it) and shows on the board. Backed by the dev-kernel `prompt`/`instruction`
  ticket kinds (schema + `gate_ticket_ready`, dev-kernel 0.2.3). `app.js?v=4`.

### Notes

- The `/debug/` harness (`debug/bin/{scaffold,coldstart,ralph,verdict}.py`) drives the whole arc — brief → spec
  → hydrated lattice → built app — bounded by construction. `debug-coldstart/replay.py` proves it CI-safe with
  the MockAdapter (no model, no server, no tokens); a live run (`DEBUG_RALPH_LIVE=1`) dispatches real workers.
