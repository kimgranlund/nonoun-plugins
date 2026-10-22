---
id: T-0722
title: "fanout.py land reads merge_gate from the integration tree"
type: bug             # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`fanout.py land --light-gate` accepts a `merge_gate: light` line that is on the integration branch but not yet on main; if it keeps reading main, the refusal names that difference.

## Intent
- Do: Read `merge_gate` / `light_scope` from the integration tree `land` merges into, falling back to the primary checkout.
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #58 (quoted):

> ## What happened
> A ticket added `merge_gate: light` and `light_scope:` to `.sdlc/config` and was landed on the integration branch. The next `fanout.py land ... --light-gate <cmd>` refused:
>
> ```
> fanout: --light-gate needs a `merge_gate: light` line in <repo>/.sdlc/config: the repo owner declares the light gate class there, ...
> ```
>
> `land` reads the config from the primary checkout (main), not from the integration tree it merges into. So the light gates can't be used until the change reaches main through a cover and fast-forward. Meanwhile my land helper, which grepped for result lines, swallowed the refusal, and both lands silently did nothing.
>
> ## Expected
> Either read the gate config from the integration tree, or keep reading it from main but say so in the refusal ("the integration branch has merge_gate: light; main does not yet"). Exit 2 should also be loud enough that a wrapper notices.
>
> ## Repro
> 1. Land a commit that adds `merge_gate: light` to `.sdlc/config` on the integration branch.
> 2. Run `fanout.py land <lane> --ticket T-x --gate ... --light-gate ...` before main has it.
>
> Seen on 0.30.0.

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `fanout.py` selftest case reproduces the issue's repro and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
`fanout.py land` now reads `merge_gate` / `light_scope` from the integration worktree it merges into when that worktree exists (new `config_root`, `ctx['cfg_root']`, used by `light_refusal` and `gate_class`), else from the primary checkout.
- New selftest case in the case 34 block: main has only `light_scope:`, the integration worktree commits `merge_gate: light`, and `land --light-gate true` merges with `gate: light`.
- Negative control (config_root forced back to main): `fanout selftest: FAIL`, `T-0722 light-gate config is read from the integration tree ... got first rc=0 rc=2 ... err='fanout: --light-gate needs a `merge_gate: light` line in .../light-integ/.sdlc/config ...'`. Restored: PASS.
- `fanout.py selftest` via gate_lock exit 0; `check.py` exit 0; `check-packaging.py` exit 0; `git diff --check d747bc8d` exit 0.
- Not done: an integration branch that exists without a worktree still reads main (the first land of a fanout branches from main anyway).

## Outcome

2026-10-22 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: d747bc8da3ab
- Changed: see commits
- Commits: effdf4b T-0722: fanout land reads merge_gate from the integration tree
- Check: 1 A `fanout.py` selftest case reproduces the issue's repro and passes; with the change reverted it ...: pass
- Check: 2 `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plug...: pass
- Check: 3 `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes...: pass
- Follow-up: note: plugins/sdlc-lite/scripts/fanout.py:1753 Security angle asked by... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/fanout.py:1076 A lane that edits... -> notes.md
- Follow-up: decide: plugins/sdlc-lite/scripts/fanout.py:1745 The dirty check uses... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/fanout.py:2487 As the Outcome says, an... -> notes.md
