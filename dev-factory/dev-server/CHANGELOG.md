# Changelog — dev-server

The dev-factory runtime (FastAPI/uvicorn over the stdlib ops layer). Not a plugin — it ships in the dev-factory
marketplace and is versioned with the kernel it serves. Format: [Keep a Changelog](https://keepachangelog.com/).

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
