# `/debug/` — the dev-factory ralph-loop harness

A reproducible harness that **runs the whole Software Dark Factory end to end from a one-paragraph brief** —
*brief → spec → **milestone lattice** → real multi-file code → integrated app → **SHIPPED*** — and a verdict
that says whether it actually shipped. The point is to *ralph-loop* across briefs until we can confidently say
dev-factory reliably turns "almost any idea" into a solid spec and then **shippable, fully-functional software**,
watched live on the web dashboard. The factory works **bi-directionally**: build learnings flow back upstream to
revise the spec, and spec work is first-class — as valuable as the build.

> **Ralph** = brute-force the same loop until it converges. Here the loop is **bounded by construction**: the
> factory's own armed run-budget (deadline / max-dispatches / token-ceiling) *and* the harness's outer caps
> (`--max-iters`, `--deadline-s`) both apply. It can stall and stop; it cannot run away.

## The milestones (each gated by a rubric)

| Milestone | Cell | Gated by | Verifier |
| --- | --- | --- | --- |
| **1 · SPEC** | `spec.system.app` | `rubric.system.spec-quality` | the spec declares a real acceptance contract |
| **2 · CAPABILITY** (per feature) | `capability.system.<feature>` | `rubric.system.test-suite` | `node {cell}/verify.mjs` — a per-cell **critic harness** the worker's real code must pass (and is gate-denied from writing) |
| **3 · SHIP** | `capability.system.app` (depends on every capability) | `rubric.system.ship` | the integrator's `verify.mjs` composes every capability + (live) the build + the spec's acceptance + a browser smoke |

The loop runs until the **integrator validates** (= SHIPPED). The planner authors the milestone rubrics + each
per-cell `verify.mjs` **dynamically** ("make as many rubrics as we need") — the generator/critic split is
mechanical: the planner writes the gate, the worker writes the code, and the gate is worker-deny.

## The arc (four `bin/` steps)

| Step | Script | What it does | Model? |
| --- | --- | --- | --- |
| **scaffold** | `bin/scaffold.py <name> --brief solitaire` | Fresh `runs/<name>/` project (git init) + a dev-factory instance bound to the **app kit** + `.claude/settings.json` (LOCAL source) + `dev-factory.env` + the brief as a **PROMPT** ticket | no |
| **cold-start** | `bin/coldstart.py <name>` | The **privileged planner**: brief → spec + the **milestone lattice** (3 rubrics, the capability cells each with a `verify.mjs`, the integrator) + build tickets. Runs BEFORE the server (single writer) | live: yes · `--mock`: no |
| **build** | (inside `ralph.py`) | The bounded loop drains the milestones in order — mock: `MockAdapter` authors source + `node verify.mjs` grades; live: the heartbeat dispatches real `claude` workers. **On a stall, a build learning revises the spec (bi-directional) and the dependents re-validate.** | live: yes |
| **verdict** | `bin/verdict.py <name>` | Did it **ship**? `shipped` (the integrator validated — its `verify.mjs` gate passed) + the produced `capability/app/` artifact | no |

`bin/ralph.py <name>` runs the whole arc.

## Run it

```bash
# the CI-safe plumbing proof — deterministic, no model, no server, ~zero tokens:
python3 debug/bin/ralph.py demo --brief solitaire --mock --fresh

# the real thing — boots the dashboard, dispatches REAL `claude` workers (spends tokens), watched live:
DEBUG_RALPH_LIVE=1 python3 debug/bin/ralph.py solitaire --brief solitaire --fresh
#   then open the dashboard:  cd debug/runs/solitaire && ../../dev-factory/dev-server/run.sh   →  http://127.0.0.1:8731
```

### The idea-bank

`briefs/` is a bank of project thought-starters to **randomly pick between** when confirming an improvement held
(so we don't overfit to one app): `solitaire` · `car-game-2d` · `shader-designer` · `physics-sim` · `breakout` ·
`drum-sequencer` · `game-of-life` · `markdown-editor` (+ `todo-cli`). Each is written so the **core logic lives
in pure ES modules a `verify.mjs` can check headlessly**, with rendering in a thin shell. Run `--brief random` to
pick one, or drop in your own `briefs/<x>.md` and run `--brief <x>`.

## Watching + steering live (the dashboard)

The dashboard streams the board, the lattice grid, the ledger, and the live workers. Two operator surfaces this
harness exercises:

- **Steer dock** (bottom-right): type guidance; the server reads operator input **every 5 seconds** and folds it
  into the **next** dispatched worker's prompt. *(A running one-shot `claude -p` worker can't be steered
  mid-flight — guidance reaches the next dispatch and the orchestrator, by design.)*
- **New-intake modal** → **Prompt / Instruction** tabs: a **Prompt** is a free-form brief the cold-start planner
  triages into structured tickets; an **Instruction** is literal steps, folded into the loop's guidance.

## Shippable software, not a markdown lattice (DF-9 closed)

The factory now authors **real multi-file source**, not one `.md` per cell. A kit declares multi-file code
authoring per layer (dev-kit-app: `capability` → a source directory); the worker authors `index.mjs` + friends
into the cell's directory to industrial standards, and the cell is graded by `node {cell}/verify.mjs` — the
**critic's** harness, which the worker is **gate-denied from writing** (it can write source, not its own gate).
`validate.py` mints the signal from the verifier's real exit status, so "validated" means the code actually
passes. The **SHIP** milestone (`capability.system.app`) composes every capability and, live, runs the build +
the spec's acceptance + a **real-browser smoke** (`DEV_FACTORY_BROWSER_SMOKE=1`, local only — the lightweight CI
proves the structure headlessly). `verdict` reports **`shipped`** = the integrator validated.

## How it stays honest

- **The factory guarantees STRUCTURE + real gates, not that any single run ships.** Whether the live workers
  author code that passes the verifiers is the model's job — the milestone rubrics + the loop exist to *keep
  iterating until the real gates pass*, and to fail honestly (and revise the spec) when they don't.

- **Bounded**: the factory's armed budget + the ralph outer caps both gate every dispatch — never unbounded.
- **Privilege split**: the cold-start planner seeds `lattice.json` + tickets through the single-writer server
  (it runs before the server boots); gate-wired build workers stay sandboxed (denied `lattice.json` / `signals/`
  / the ledger). Correct, not a hole.
- **Local source**: `runs/<name>/.claude/settings.json` points `extraKnownMarketplaces` at the working-tree
  `dev-factory/` (a bare path). The loop does not depend on the plugin *loader* — the dev-server resolves the
  kernel bins + kit by path and workers get them via `--add-dir`, so the factory runs even if the install UX
  doesn't.
- **Tokens are real**: a live run dispatches real workers. The mock path proves the whole plumbing first.

`runs/` is gitignored — the harness is tracked, what it produces is not.
