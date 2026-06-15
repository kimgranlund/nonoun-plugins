# Run milestone — the answer key

`replay.py` is the **Run-phase milestone** (TDD §19): proof that the outer loop *closes* — the factory
improves its own **definitions** from the ledger, not just its outputs (Failure 1, designed out). Where
Walk ran the factory unattended, Run shows it sharpening the substrate it runs against.

| Check | Claim |
|---|---|
| **R1** | distillation surfaces a recurring failure signature from the ledger window, **with provenance** (`ledger_refs`) — a pattern without provenance is a guess the next iteration can't reconstruct. |
| **R2** | a regeneration ticket drives the spec cell `validated → regenerating` as a **deliberate, ledgered** transition (the revision begins) — authoring, not a re-validation, so no critic signal. |
| **R3** | `regenerating → validated` re-validates the **revised** spec through the critic's signal — the trust line holds *across* a revision: a worker can revise, but cannot self-declare the revision validated. |
| **R4** | the spec asset actually changed, and the whole `validated → regenerating → validated` cycle plus the distillation-driven proposal are in the append-only ledger — deliberate, attributable, reversible; never a silent overwrite. |

## The loop it closes

`operate → ledger → distill → patterns → upstream → spec → (re-validate) → operate`. The **scan** half
(finding recurring signatures) is `bin/distill.py` — computation, per the routing law. The **judgment**
half (is this a real pattern? what revision does it imply?) is the `pattern-distiller` / `spec-regenerator`
agents. A merge is policy-gated; the revision lands only through the deliberate maturity transition.

```bash
python3 dev-factory/dev-server/evals/run-milestone/replay.py   # exit 0 = the loop closes
```
