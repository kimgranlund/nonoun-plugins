# `/debug/` — the dev-factory ralph-loop harness

A reproducible harness that **runs the whole Software Dark Factory end to end from a one-paragraph brief** —
*brief → plan → spec → hydrated lattice → built app* — and a verdict that says whether it worked. The point is
to *ralph-loop* across briefs until we can confidently say dev-factory reliably turns "almost any idea" into a
reasonably solid spec and then builds it, watched live on the web dashboard.

> **Ralph** = brute-force the same loop until it converges. Here the loop is **bounded by construction**: the
> factory's own armed run-budget (deadline / max-dispatches / token-ceiling) *and* the harness's outer caps
> (`--max-iters`, `--deadline-s`) both apply. It can stall and stop; it cannot run away.

## The arc (four `bin/` steps)

| Step | Script | What it does | Model? |
| --- | --- | --- | --- |
| **scaffold** | `bin/scaffold.py <name> --brief solitaire` | Fresh `runs/<name>/` project (git init) + a dev-factory instance + `.claude/settings.json` (plugins from LOCAL source) + `dev-factory.env` + the brief seeded as a **PROMPT** ticket | no |
| **cold-start** | `bin/coldstart.py <name>` | The **privileged planner**: brief → spec asset + hydrated lattice cells + active build tickets (realises *prompt = triaged*). Runs BEFORE the server so it is the single writer | live: yes · `--mock`: no |
| **build** | (inside `ralph.py`) | The bounded loop drains the build tickets — mock: `MockAdapter`; live: the dev-server heartbeat dispatches real `claude` workers | live: yes |
| **verdict** | `bin/verdict.py <name>` | Did it build? `lattice_built` (every spec/capability cell settled) + an app artifact + an optional `npm run build` smoke | no |

`bin/ralph.py <name>` runs the whole arc.

## Run it

```bash
# the CI-safe plumbing proof — deterministic, no model, no server, ~zero tokens:
python3 debug/bin/ralph.py demo --brief solitaire --mock --fresh

# the real thing — boots the dashboard, dispatches REAL `claude` workers (spends tokens), watched live:
DEBUG_RALPH_LIVE=1 python3 debug/bin/ralph.py solitaire --brief solitaire --fresh
#   then open the dashboard:  cd debug/runs/solitaire && ../../dev-factory/dev-server/run.sh   →  http://127.0.0.1:8731
```

Briefs live in `briefs/` (`solitaire.md` is the worked example; `todo-cli.md` shows a second, unrelated idea).
Drop in your own `briefs/<x>.md` and run `--brief <x>`.

## Watching + steering live (the dashboard)

The dashboard streams the board, the lattice grid, the ledger, and the live workers. Two operator surfaces this
harness exercises:

- **Steer dock** (bottom-right): type guidance; the server reads operator input **every 5 seconds** and folds it
  into the **next** dispatched worker's prompt. *(A running one-shot `claude -p` worker can't be steered
  mid-flight — guidance reaches the next dispatch and the orchestrator, by design.)*
- **New-intake modal** → **Prompt / Instruction** tabs: a **Prompt** is a free-form brief the cold-start planner
  triages into structured tickets; an **Instruction** is literal steps, folded into the loop's guidance.

## Known limit — lattice built ≠ app built (DF-9)

The shipped dispatch adapters author **one `{layer}/{slug}.md` per cell**, so a live run today builds a
*markdown lattice* (specs, rubrics, capability docs) and validates it — it does **not** yet emit runnable
multi-file source. So `verdict` separates **`lattice_built`** (the loop converged — its stop condition) from
**`app_built`** (a real runnable artifact + a clean smoke). Until the **DF-9 code-authoring adapter** lands (a
worker that authors N source files to a cell-defined layout and is graded by the cell's real verifier, e.g. a
`verify.mjs`/`npm run build`), a live ralph run proves the **loop mechanics end to end** but reports
`app_built: NO`. The harness says so plainly rather than calling a markdown lattice a finished app. See
`docs/tickets/dev-server-ui-fixes.md` → DF-9.

## How it stays honest

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
