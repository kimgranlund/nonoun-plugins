# First-slice walkthrough — the kernel's behavioral baseline (recorded 2026-06-12, v0.2)

Selftests prove the units; **this run proves the loop.** `replay.py` drives a real first slice on the README's toy project (invoice-parser) using only the public machinery — no hand-set maturities, no forged signals — and CI replays it hermetically on every push. There is deliberately **no committed baseline tree**: the wired copies it produces (`.agents/harness/hooks/_lattice.py`) would drift against the kernel as it evolves; `replay.py --keep DIR` regenerates the positive control in seconds whenever the judge needs one to score.

## The run

```
seed     lattice.py init invoice-parser        → 4 cells (ontology · spec · rubric · ledger) + the scaffold
wire     wire.py apply --confirm && wire.py check  → WIRED (gate-signal PreToolUse deny + emit-ledger + propagate-staleness)
loop ×4  lattice.py rank picks the next cell   → the COMPASS chose: ontology → spec → rubric → ledger (the partial order, computed not narrated)
         the "worker" writes the cell's asset
         validate.py <cell> -- python3 -c <predicate>   → the signal minted from the predicate's EXIT STATUS
         ledger.py append                      → the why + the cost, every pass
distill  ledger.py distill / cost / false-pass
```

## The end state (asserted by replay.py, every run)

- **Frontier empty** — `lattice.py scan` returns 0 open cells; all 4 validated.
- **Every signal is real** — one `signals/{cell}/{ts}--predicate-check.json` per cell, on disk, minted by `validate.py` from a content predicate (`## Entities`/`## Operations`/`## States` present; ≥3 numbered acceptance predicates; `[gate]`+`[review]` labels; every ledger line parses with `operation`+`actor`).
- **Provenance chains by content hash** — e.g. the spec's signal carries `validated_against: {ontology.task.domain: sha256:18e93f175ad5d25d}`; `lattice.py check --dir` re-verifies every recorded hash against the assets on disk (the stale-but-trusted gate, passing positively).
- **Still wired** — `wire.py check` exits 0 after the run; the worker loop's deny-on-write held throughout.
- **`false-pass` reads UNMEASURED** — no independent refuter has run yet, and the kernel says so instead of minting a flattering 0.0%. A fresh slice has earned *validated cells*, not *autonomy*.

## Recorded ledger (one run, verbatim shape)

```
validate  ontology.task.domain     — predicate-check exit 0 (the verifier's exit status, not the worker's opinion)
validate  spec.task.first-slice    — predicate-check exit 0 …
validate  rubric.task.first-slice  — predicate-check exit 0 …
record    ledger.task.events       — ledger schema laid in the first slice (cannot be retrofitted)
validate  ledger.task.events       — predicate-check exit 0 …
```

## What this run caught at authoring time

Driving the loop for real surfaced a **kernel deadlock** the selftests had missed: the original seed wired `spec.verifier → rubric.task.first-slice` while the rubric's `depends_on` included the spec — a circular wait that left the frontier permanently empty after two validations. Fixed in 0.2.1 (`seed_lattice` drops the circular verifier link: the spec validates first against a spec-quality predicate; the rubric is authored against the validated spec; downstream work cells bind their `verifier` to the rubric), with a bootstrap-to-full-validation regression in `lattice.py selftest`. That is the walkthrough doing its job — behavioral evidence catching what unit proofs cannot.

## Replay

```bash
python3 harness-forge/evals/first-slice-walkthrough/replay.py            # hermetic; CI runs this
python3 harness-forge/evals/first-slice-walkthrough/replay.py --keep d/  # materialize a run (the judge's positive control)
```
