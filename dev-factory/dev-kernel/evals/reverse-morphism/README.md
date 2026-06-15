# Reverse-morphism — the answer key

The central thesis is a **biconditional**: "the board cannot disagree with the lattice." `tracer-bullet`
proves the **forward** direction (ticket `done` ⟹ the cell advanced through a critic-minted signal). This
eval proves the **reverse** (council finding M1, which noted the biconditional was half-proven): a cell
reaching `validated` ⟹ the board recorded it, and there is **no out-of-band path** to `validated`.

| Check | Claim |
|---|---|
| **R1** | a worker **cannot** advance a cell by writing `lattice.json` — `gate-verifier` denies it. Maturity is server-only. |
| **R2** | a worker **cannot** forge the signal `validated` requires — `gate-signal` denies it. The currency is critic-only. |
| **R3** | so the only path to `validated` is the validation path, which **ledgers** the advance — every validated cell has a recorded transition the board reflects (no silent advance). |
| **R4** | the lattice's own invariant: a `validated`-without-signal cell is **structurally rejected** by `lattice.py check`, so a maturity the board doesn't know about is unrepresentable. |

Together with `tracer-bullet`, the biconditional holds in **both** directions: `board ⟺ lattice`.

```bash
python3 dev-factory/dev-kernel/evals/reverse-morphism/replay.py   # exit 0 = the reverse holds
```
