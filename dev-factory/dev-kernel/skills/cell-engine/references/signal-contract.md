# The Signal Contract — the validation path is the only writer of signals/

`Cell: protocol.workflow.signal-contract · Status: defined · Register: established lineage (generator/critic split, eval-driven development, reward-hacking defenses); the protected-boundary mechanization is house (dev-factory's validate.py + gate-signal)`

"Signal is the only currency." No cell advances and no scope widens without a **signal artifact written by the validation path** (TDD §3). This reference is the contract: what a signal is, who may write it, and why the worker structurally cannot.

## What a signal is

A signal is the evidence that a cell's verifier passed against its asset — a JSON artifact under `signals/{cell-id}/{iso-ts}--{harness}.json`. It is **computed from an external check**, not authored: `validate.py` runs the verifier command and mints the signal from the command's **exit status** (0 = pass, nonzero = fail), capturing the command's output as localized evidence and stamping the validated cell's `validated_against` with the asset's content hash. A signal is therefore a *fact about a command that ran*, not an opinion typed into a file.

## The validation path (`validate.py`) — the only minting authority

```
validate.py <cell-id> --dir DIR --harness NAME -- <verifier-command>
```

- Loads the cell, runs `<verifier-command>` (pytest, a linter, a link-check, a rubric scorer, a build), and reads its return code.
- **Pass (exit 0):** writes the signal under `signals/{cell-id}/`, stamps `validated_against` (the asset's content hash + each upstream dependency's hash — the input to staleness propagation), and advances the cell to `validated`.
- **Fail (nonzero):** writes nothing that advances the cell; the cell stays put; the output is captured as evidence for the next pass.
- Exit codes: `0` = verifier passed (cell advanced), `1` = failed (cell not advanced), `2` = bad invocation.

The signal's result is *the command's exit status*. A worker hand-asserting "pass" into the ledger is not a signal — there is no command, no exit status, no external check. That distinction is the whole anti-reward-hacking story.

## Why the worker structurally cannot write a signal

`signals/` is on the **immutable side** of the boundary (TDD §14.1). In a wired instance:

- **`gate-signal`** (PreToolUse deny) denies any worker `Write`/`Edit` to a `signals/` path. It is the load-bearing, focused subset of the broader immutable-boundary gate.
- **`gate-verifier`** (the superset) additionally denies worker writes to `rubric/`, the hooks, the run budget, `lattice.json`, the kernel schemas, and the wiring (`.claude/settings.json`) — so a wired worker cannot unwire its own gate.
- **`gate-ledger`** denies mutation of the append-only ledger — a worker cannot launder a false transition by editing history.

A clean scoreboard a worker produced by editing its own verifier is the canonical reward-hack (TDD §14, REQ-SAFE-001). It is **designed out, not detected after the fact**: the worker is *mechanically unable* to reach the scorer. Even unwired, the `cell-advancer` and `spec-architect` carry no path to `signals/` in their tool posture — the discipline is a floor before the gate makes it a wall.

## The morphism: ticket `done` ⟺ a critic-validated cell

The signal contract is what makes the coordination board unable to disagree with the lattice. A ticket reaches `done` for a signal-bearing transition only when `lifecycle.py`'s `gate-signal` confirms the target cell carries a signal_ref **and** has reached the ticket's `to`-maturity — and a signal can only have been written by the validation path. So `done` *proves* a critic, not the worker, validated the work (TDD §4, §7.1). The same gate governs the ticket close and the cell advance; there is one gate, and both transitions pass through it.

## Authoring advances carry no signal — and that is correct

Reaching `defined` or `instantiated` is an **authoring** advance: the worker wrote the asset, the server records the bump, no validation claim is made, so no critic signal is minted (`lifecycle.py`'s `SIGNAL_BEARING` excludes them). This is not a gap in the contract — it is the contract being precise about where trust is *claimed*. The signal requirement bites exactly at the line a cell becomes reusable/trusted (`validated` and above), which is the only line where a forged pass would do harm.
