# The Engine — define → create → validate on one cell

`Cell: methodology.workflow.engine · Status: defined · Register: established lineage (PDCA, red–green–refactor, build–measure–learn, tracer bullets, eval-driven development); the authoring-vs-signal-bearing distinction is house (dev-factory's lifecycle.py)`

The engine is the factory's **inner loop**: one closed `define → create → validate` pass on **exactly one cell** at the smallest scope that yields decisive signal. This methodology is what a dispatched `cell-engine` unit runs. The *bookkeeping between* cells (scan, rank, the lattice advance) is the kernel's; the *judgment inside* the cell is the engine's.

## One pass is one closed loop

- **Scope** = the one cell. Not two; a worker that opens a second cell at `defined` while the first lacks signal has broken the trajectory rule.
- **Verifier** = the cell's bound `validated` rubric + its harness. A loop without a verifier is a machine for generating confident mistakes at scale.
- **Stop condition** = the **signal** (pass), or the budget cap / no-progress signature (stop-and-report). Never the worker's opinion that it is done.

## define → create → validate

1. **Define.** Read the cell's spec — *what done means* — and restate its acceptance criteria as checkable predicates. If the spec is ambiguous, that is a finding against the spec cell, not a guess to paper over.
2. **Create.** The `cell-advancer` authors the asset into the target layer dir (`spec/`, `methodology/`, `policy/`, …) and **only** there. Front-load the right context (the cell's spec, its bound rubric, the nearest patterns) rather than padding the window — first-pass context quality beats iteration count.
3. **Validate — by a critic, never the author.** The `cell-validator` runs the bound verifier *through the validation path* (`validate.py`), which mints the signal from the command's exit status. The advancer does not write the signal; `signals/` is protected. On pass, the cell advances; on fail, the unit returns with localized evidence (attempts++), never advanced.

Each pass terminates in a **ledger entry** carrying the result, the *why* (the rationale the next fresh-context iteration won't have), and the measured cost. No silent work.

## The authoring/signal-bearing line (where the trust boundary falls)

`lifecycle.py` is precise about which advances require a critic signal (`SIGNAL_BEARING = {validated, operating, regenerating}`):

| Advance | Who applies it | Mints a critic signal? | Why |
| --- | --- | --- | --- |
| `absent → defined` | server (single-writer) | **no** | the worker wrote the asset; it makes no validation claim |
| `defined → instantiated` | server (single-writer) | **no** | still authoring; the asset exists but is not yet trusted |
| → `validated` / `operating` / `regenerating` | the **validation path** (critic) | **yes** | the cell will be reused/trusted; a signal the worker cannot forge is required |

The line is exact: **a worker can author, but cannot declare its own work validated.** An authoring advance is the server recording that an asset now exists; a signal-bearing advance is a critic certifying it holds. A worker still cannot write `lattice.json` for *either* (`gate-verifier`) — the server applies the maturity bump.

## The dispatch contract (what the unit receives)

A `cell-engine` dispatch runs in a hermetic git worktree and carries a typed `ExecutionPlan` (`dispatch-policy.schema.json`):

| Field | What it sets |
| --- | --- |
| `orchestration_shape` | the topology of model calls inside the unit (`single-pass` … `evaluator-optimizer`) |
| `loop_strategy` | the iteration discipline (`ralph-fresh-context`, `auto-research`, `tracer-bullet`, …) |
| `context_plan` | the working-set / retrieval / compaction policy — disk remembers, context forgets |
| `effort` | model tier × reasoning effort × iteration budget × parallelism, set by (risk × scope × tier) |
| `delegation` | sub-agent vs team, and the **bounded** depth (handoff fidelity is multiplicative) |

The plan is assembled **deterministically by the compass** from the family's dispatch policy — never chosen by inference at dispatch time (selection is policy, not vibes). The runtime guarantees the worktree is hermetic, the PreToolUse/PostToolUse gates are active (protected paths enforced), tool/loop events tee into the ledger, and the unit terminates on its stop condition.

## Budgets are policy, not afterthoughts

Every pass carries an iteration cap, a wall-clock limit, a no-progress detector, and a *separate* done-judge. Loop length, not model choice, dominates cost — so the bounds are **code**, not the worker's counting: `ledger.py no-progress` is the detector and `lattice.py block` is the flag — **both ship in this kernel**. Converting that flag into a *denied write* is `gate-budget`, which lives with the runtime (**dev-server**) and is **consent-wired into the worker loop** — it is not bundled in dev-kernel (the same honest scope as `gate-signal`: a kernel installed alone enforces nothing; the bounds become mechanical once dev-server wires them). The graceful stop (notice the budget is spent, report, hand back) is the agent's courtesy; once wired, the floor is the gate.

## Failure modes the engine guards against

A worker writing its own signal (the canonical reward-hack — designed out by `gate-signal`). A cell advanced against an unvalidated rubric (scoring vibes). A second cell opened at `defined` while the slice lacks signal (trajectory violation). A done declared by opinion instead of a passing exit status (validated-by-assertion). Looping harder on a no-progress cell instead of stopping (token burn). Context hoarding — preloading the whole corpus instead of just-in-time retrieval of the cell's substrate.
