# Integration milestone — the answer key

`replay.py` closes the gap an audit found after the first build: the **execution-strategy** and **rubric**
layers were fully specced + schema'd but the dispatcher ignored them (the dispatch policy was inert; the
kit's rubric pointers were dangling; the real verifier was a thin "a file exists"). This proves the layers
are now *wired*, not just declared.

| Check | Claim |
|---|---|
| **I1** | the execution plan is **assembled from the kit's dispatch policy** — a spec unit runs as the policy's `evaluator-optimizer` shape, not the default `single-pass`. `dispatch-policy` is consumed, not ignored. |
| **I2** | the **roster** picks the right worker — a spec cell is advanced by `spec-architect`, not a generic worker. |
| **I3** | the kit's **real** verifier runs — a structured spec clears `spec-quality-check`'s five `[gate]` dimensions (schema-valid · criteria-checkable · rubric-binds · non-goals · decomposition-entailment) and validates. |
| **I4** | that verifier has **teeth** a file-exists check lacks — a *prose* spec FAILS `spec-quality-check`, so the ticket does **not** reach done. "validated" now means the family's rubric, not "a file is present." |
| **I5** | the **activity/agent lens** is populated (agent · kind · orchestration_shape) from the run. |

## Why this matters

The first build's milestones proved the *spine* with a generic worker and an asset-exists check. That's
necessary but it let the "intelligence" layer (how each unit runs, what "validated" means per family) sit
declared-but-inert. This milestone binds the corpus kit (`DEV_FACTORY_KIT`) and shows the loop actually
*driven by the kit*: the policy shapes the dispatch, the roster staffs it, and the family's rubric gates it.

```bash
python3 dev-factory/dev-server/evals/integration-milestone/replay.py   # exit 0 = the kit drives the loop
```
