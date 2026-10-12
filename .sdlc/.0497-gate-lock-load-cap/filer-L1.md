<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0497: gate_lock.py: cap admission by load average (opt-in max_load)

## PR body
## Summary
`gate_lock.py` can now refuse new grants while the host's 1-minute load average is above an opt-in `max_load` policy cap. This addresses the fleet retro (12h) rows 1 and 2, where other repos' CPU-bound gates stretched a critical gate past its 1800 s guard. The cap is off by default, so the default policy is unchanged. A repo opts in with `gate_lock.py policy set max_load=<n>`.

## Changes
- `plugins/sdlc-lite/scripts/gate_lock.py`:
  - `load_policy` accepts an optional top-level `max_load`, a whole number of 0 or more. A value of 0 means off and the key is dropped.
  - `policy set max_load=<n>` keeps the value out of `capacity`. The confirmation line adds the cap only when it is set.
  - New `host_load()` returns `os.getloadavg()[0]`. The env var `SDLC_GATE_LOAD_FILE` is a test seam that replaces it with a number read from a shared file. If the host reports no load average, the cap is not applied.
  - `schedule` stops granting when the load is above the cap. A load equal to the cap admits.
  - The check sits on a new `# LOAD-CAP` line. The `# SLOT-CAP` line and `fits` are untouched.
  - A held grant is never revoked. A head refused for load keeps its round-robin turn, because `rr` moves only on a grant.
  - `status` prints `waiting: load 36.5 over cap 24` when the queue is non-empty and the load is over the cap. `status --json` gains a `load` object (`value`, `max_load`, `over`) whenever `max_load` is set.
  - Selftest gets `case_load`, a `load cap` negative control (mutant on the `LOAD-CAP` line), and `max_load` checks in `case_rr`. The `case_rr` checks cover order at a low load, no grant at a high load, and equal-to-cap admits.
- `docs/references/sdlc-internals.md`: the `scripts/gate_lock.py` section names `max_load`, `policy set max_load=<n>`, the status row, and `SDLC_GATE_LOAD_FILE` (tests only).
- `docs/specs/sdlc-lite/gate-lock-admission.md`: new section 14 dated 2026-10-12. Section 5 is untouched.

## Verification
The verifier passed all 10 criteria. Each `(red)` criterion has a red control recorded before the edit (`red-checkpoint.jsonl`), and the verifier re-ran the over-cap and `policy set` probes against the base script to see them fail there.
- `gate_lock.py selftest` exits 0 and prints `negative control observed (load cap)`.
- At load 36.5 with cap 24, `run --timeout 2` exits 3. After the load drops to 10, the same run is admitted.
- A held grant survives a load rise to 36.5, `status` shows the `waiting:` row, and the waiter runs after the drop.
- `max_load` appears in `policy show` as a top-level key, never inside `capacity`, and `max_load=0` removes it.
- Both docs name `max_load`, and `sdlc-internals.md` names `SDLC_GATE_LOAD_FILE`.
- The default `policy show` on a fresh root equals the built-in policy exactly.
- The scope guard shows only the three target files changed. `git diff --check` is clean.
- `check.py` exits 0 (`ok: 19 role levels, 9 agents, 22 generated definitions checked`).
- `check.sh` exits 0, and the builder timed it at 1202 s.

Limit: the admission rule is proved with a fake load. Nothing here shows that a real cap shortens a real gate on a loaded host.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `gate_lock.py`: new opt-in policy key `max_load` (set with `policy set max_load=<n>`, 0 turns it off). While the 1-minute load average is above the cap, no new grant is admitted, and `status` prints `waiting: load <x> over cap <n>`. Held grants are never revoked, and the default policy is unchanged.

## Follow-ups
- decide: `case_cap` and `case_livegroup` in the `gate_lock.py` selftest guard their status checks with `label == 'real'`, but the controls loop passes `real0`, `real1` and so on, so those checks never run. This predates T-0497. Decide whether to fix them in a ticket.
- note: T-0497 proves the rule only with a fake load. Whether a real `max_load` shortens a real gate on a loaded host is untested until a repo opts in.
- note: The 1-minute load average lags, so several queued heads can be admitted in the seconds after the load drops under the cap. Per-job priority was a handoff non-goal, to be revisited if the cap is not enough.
- note: The `check.sh` guard took 1202 s in this tree against the 897 s recorded earlier, so it needs a Bash timeout well above 20 minutes. The `(guard)` scope check passes vacuously if `SDLC_BASE_SHA` is unset.
