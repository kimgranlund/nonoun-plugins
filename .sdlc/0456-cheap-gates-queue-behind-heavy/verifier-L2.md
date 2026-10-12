<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- #1 `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0; case 21b shows a cheap gate (`check.py`) granted 1 compute unit, a default gate granted 3, `--gate-need` overriding both, and a bad spec refused with exit 2: pass. Evidence: on the built tree the selftest printed `fanout selftest: PASS` with rc=0 in 3:03. Case 21b is at fanout.py:3651-3742. I confirmed each part can go red. I copied the built fanout.py into a throwaway worktree at `$SDLC_BASE_SHA` and made one mutant per rule, each stopping right after case 21b.
  - The unmutated copy m0 printed `STOP21b []`.
  - m1 (cheap need returns ''): `case 21b cheap: the gate saw SDLC_GATE_WORKERS=[1], log=... W=[3]`, and cheapfit did not merge.
  - m4 (prefix check replaced by `if True`): `case 21b noprefix: ... [3] ... W=[4]`.
  - m6 (spec validation skipped): `case 21b bad spec: refused with rc 2 naming --gate-need, got rc=1`.
- #2 With a peer holding 5 of 6 compute units and `SDLC_GATE_TIMEOUT=1`, a cheap gate merges while a default gate ends as `gate waited 1 s for a slot, not run`, with no `red:`, the merge reset, and logs a1 and a2; a command that exits 3 itself stays `red: ... rc=3`: pass. Evidence: case 21b's cheapfit, stuck, retry and exit3 legs (fanout.py:3687-3742) are green in the PASS run above. Mutant results:
  - m2 (lock timeout never detected): `timed-out gate: exits 1 as ...`, `not red`, `retried once ... got ['gate-alpha-T-0001-1-a1.log']` and `retry` all went red.
  - m3 (no retry): `retried once (logs a1 and a2), got ['...-a1.log']` and `retry` went red.
  - m5 (every rc 3 treated as a lock wait): `control: a gate command that exits 3 is red: ... rc=3` went red.
- #3 `python3 plugins/sdlc-lite/scripts/gate_lock.py selftest` exits 0; `bash plugins/sdlc-lite/scripts/check.sh` exits 0; `python3 scripts/check-packaging.py` exits 0: pass. Evidence:
  - gate_lock selftest printed `gate_lock selftest: PASS`, rc=0.
  - check.sh exited 0; its tail shows `run selftest: PASS`, `hook selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`, and grep found no FAIL line.
  - check-packaging printed `PASS: catalog parity, identity, skill routes, hook isolation and context links`, rc=0.
- #4 gate-lock-admission.md (section 13), sdlc-internals.md and the fanout.py docstring describe `--gate-need`, `SDLC_GATE_TIMEOUT`, the cheap-gate default and the not-run report, with the lock's capacity and default need unchanged: pass. Evidence:
  - Section 13 is at gate-lock-admission.md:198. Its three bullets cover the weight (cheap gates get `compute_units=1`, plus `--gate-need [PREFIX::]RES=N`), the wait limit (`SDLC_GATE_TIMEOUT`) and the report (`gate waited N s for a slot, not run`, and a command's own rc 3 stays red).
  - The sdlc-internals.md diff adds the same four facts to the fanout sentence of the gate_lock section.
  - The fanout.py docstring diff covers them too (the run section near line 221 and the case 21b description near line 355).
  - `git diff --quiet HEAD -- plugins/sdlc-lite/scripts/gate_lock.py` reports it unchanged, so capacity 6/3 and default need 3 are untouched. Section 13 says so too.
  - `git diff --check` is clean.

## Out of scope changes
`.sdlc/0456-cheap-gates-queue-behind-heavy/handoff.md` gained the `## Acceptance criteria` section. This is allowed: the solo contract (plugins/sdlc-lite/agents/solo.md:48) says to write the task handoff's `## Acceptance criteria` when it has none and the ticket needs a verifier. No other changes beyond fanout.py and the two docs. The untracked files are run records: base-sha, runs.jsonl, skips.md, verifier-L2.attempt.json.

## For the next attempt
None
