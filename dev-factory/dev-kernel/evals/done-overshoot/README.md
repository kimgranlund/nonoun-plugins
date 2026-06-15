# done-overshoot — the answer key (DF-7)

A falsifiable replay for **DF-7**: an author ticket whose target cell a verifier already **overshot** must close
`done` as a satisfied no-op — not be wedged by an "illegal maturity advance" error.

## The bug

The factory builds a cell in two tickets: an **author** ticket (`defined → instantiated`, the worker writes the
asset) then a **validate** ticket (`instantiated → validated`, the verifier mints the signal). But `validate.py`
auto-steps `defined → instantiated → validated` in **one** pass. Run validate-first and the cell jumps straight to
`validated`, **past** the author ticket's `instantiated` target. Closing that author ticket then hit
`_author_advance`'s bare `transition_ok(validated, instantiated)` — `False` (`validated` never steps back to
`instantiated`) — and was denied *"illegal maturity advance validated → instantiated."* The authoring work was
demonstrably done, yet the ticket couldn't close. (Operator workaround at the time: cancel the subsumed ticket,
or always validate-last.)

## The fix

`_author_advance` recognizes a target the cell has **already reached** on the linear maturation axis
(`lattice.reached`: `absent → defined → instantiated → validated → operating`) as a **satisfied no-op**, distinct
from an illegal advance — *before* it tests `transition_ok`. `reached(cur, target)` is at-or-beyond on that axis
and **False for off-axis states** (`regenerating · stale · deprecated`), so the recognizer can't be abused to wave
through a genuinely illegal advance. `reached` lives in `lattice.py` (the single source of maturity semantics,
vendored from harness-forge), not duplicated in the lifecycle layer.

## What `replay.py` proves (exit 0 = all hold)

| Check | Assertion |
|---|---|
| **O1** | An author ticket (`defined→instantiated`) on a cell a verifier overshot to `validated` **closes `done`**, and the no-op **does not mutate** the cell's maturity (stays `validated`). |
| **O2** | The fix is **tight**, not permissive: an author ticket on an **off-axis** cell (`deprecated`) is **still denied** as an illegal advance — `reached()` never treats off-axis as "beyond", so the hole stays closed. |
| **O3** | The recognizer itself: `reached()` accepts at-or-beyond on the PROGRESS axis, rejects short-of-target, and is False for off-axis states. |

O1 is the wedge removed; **O2 is the load-bearing guard** — it falsifies the lazy fix (a blanket "always allow the
author advance"), which would pass O1 but fail O2.

## Run

```bash
python3 dev-factory/dev-kernel/evals/done-overshoot/replay.py   # exit 0 = DF-7 closed, no permissive hole
```

CI runs it via the `evals/*/replay.py` glob in `.github/workflows/dev-factory.yml`. The regression is also pinned
in `lifecycle.py selftest` (case 6).
