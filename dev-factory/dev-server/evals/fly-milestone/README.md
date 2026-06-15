# Fly milestone — the answer key

`replay.py` is the **Fly-phase milestone** (TDD §19): the dark factory — lights-out at fleet scope, with
the kernel/kit boundary proven by a *second* kit. It asserts the two structural preconditions.

| Check | Claim |
|---|---|
| **F1** | the boundary's **falsification test**: two different families — `dev-kit-corpus` and `dev-kit-app` — both conform against **one unchanged** `dev-kernel`. Adding the second required zero kernel edits, and neither kit ships a kernel bin/schema. A kit that needed the kernel changed would fail `check-kit-conform`. |
| **F2** | Tier 3 (scheduled / lights-out) is **reachable but earned**: a sustained clean independent-refuter record **plus** a hermetic sandbox **plus** a tamper-evident audit trail. Absent any one, the family is capped at Tier 2 — and a single incident mechanically revokes even Tier 3. Autonomy at the top of the ladder is still measured, never assumed. |

## Why two kits is the whole argument

The architecture's central claim is that the **kernel is invariant capability** and a **kit is a family
binding**. The only way to prove the boundary didn't leak is to add a *second* family and show the kernel
didn't move. `dev-kit-app` (validate-by-test-suite, bisect-for-bugs) is a genuinely different family from
`dev-kit-corpus` (validate-by-doc-check, hill-climb-for-graded-cells), and both bind the same contracts.

```bash
python3 dev-factory/dev-server/evals/fly-milestone/replay.py   # exit 0 = the dark factory is earned, not assumed
```
