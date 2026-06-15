# dev-kit-corpus — the corpus family kit

Binds the `dev-kernel` contracts to one family of work: **building and validating a knowledge corpus** (spec, rubric, pattern, methodology cells). A kit is a stateless plugin — it *binds* the kernel, it never forks it. `dev-kernel/bin/check-kit-conform.py` enforces that mechanically (zero kernel edits, species-correct adapters).

## What it ships

| Piece | File | Role |
|---|---|---|
| Kit manifest | `kit.json` | the `Kit` contract: family, kernel_compat, rubric manifest, adapters, dispatch policy, seed patterns |
| Dispatch policy | `dispatch-policy.json` | the deterministic unit→execution-plan map — graded corpus cells get `evaluator-optimizer` + `auto-research` hill-climb; high-risk definitional cells escalate to a team |
| Validation harness | `bin/doc-check.py` · `bin/rubric-check.py` | the verifiers the validation adapters bind — a spec must be substantive; a rubric must carry a `[gate]` + a pristine reference (it earns "verifier" only by passing its own meta-verifier) |
| Rubric manifest | (in `kit.json`) | which validated rubric gates which layer (`spec-quality`, `rubric-quality`, `pattern-quality`) |
| Seed pattern | `patterns/spec-decomposition.md` | warms the pattern layer + the compass cold-start priors |

## How it's consumed

`dev-server`'s dispatcher reads the dispatch policy to assemble each unit's execution plan, provisions a worktree, and runs the worker through a `DispatchAdapter` (the kit's `headless` adapter binds the live runtime; CI uses the kernel's `mock`). The critic validates the cell's asset by running the kit's validation harness via `validate.py`, which mints the signal from its exit status.

## Conform

```bash
python3 ../dev-kernel/bin/check-kit-conform.py kit .   # exit 0 = binds the kernel cleanly
python3 bin/doc-check.py selftest && python3 bin/rubric-check.py selftest
```

The boundary's falsification test (TDD §5): adding this kit required **zero** edits to `dev-kernel`. The second kit, `dev-kit-app`, proves the boundary holds for a different family.
