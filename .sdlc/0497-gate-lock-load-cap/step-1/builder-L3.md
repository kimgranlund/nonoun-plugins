<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout49/c/plugins/sdlc-lite/scripts/gate_lock.py`: `load_policy` accepts an optional top-level `max_load`; new `host_load()` with the `SDLC_GATE_LOAD_FILE` seam; `schedule(..., load=None)` with the `# LOAD-CAP` line; `status_data` and `cmd_status` carry the load fact and the `waiting: load ... over cap ...` row; `cmd_policy set max_load=<n>`; docstring and usage strings; selftest `case_load`, `M_LOAD`, the `load cap` control row, and the `max_load` checks in `case_rr`.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout49/c/docs/references/sdlc-internals.md`: section `scripts/gate_lock.py` names `max_load`, `policy set max_load=<n>`, the status row, `SDLC_GATE_LOAD_FILE` (tests only) and the `LOAD-CAP` mutant.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout49/c/docs/specs/sdlc-lite/gate-lock-admission.md`: new section 14 dated 2026-10-12 for T-0497; section 5 untouched.

## Checks
- `python3 .../scripts/redck.py record .sdlc/0497-gate-lock-load-cap/step-1/handoff.md`, before the first edit: exit 0, 6 pre-edit controls recorded red.
- Criterion 1 (red), `gate_lock.py selftest` plus the grep for `negative control observed (load cap)`: rc 0, `gate_lock selftest: PASS`, line present with the tell `the waiter ran over the load cap`.
- Criterion 2 (red), over the cap exits 3 and under it is admitted: exit 0.
- Criterion 3 (red), held grant survives, status reason, waiter runs after the drop: exit 0.
- Criterion 4 (red), `max_load` is top-level, never a capacity, 0 turns it off: exit 0.
- Criterion 5 (red), `max_load` in both docs: exit 0.
- Criterion 6 (red), `SDLC_GATE_LOAD_FILE` in `sdlc-internals.md`: exit 0.
- Guard, default policy unchanged: exit 0.
- Guard, only the three target files change (with `SDLC_BASE_SHA=1f6e5ea2a1b79a6a2ac6a6a5ae7876bf54d29222` exported in the same call): exit 0.
- Guard, `python3 plugins/sdlc-lite/scripts/check.py`: exit 0, `ok: 19 role levels, 9 agents, 22 generated definitions checked`.
- `git diff --check`: exit 0.
- Guard, `bash plugins/sdlc-lite/scripts/check.sh`, run once: rc 0 in 1202 s.

## Notes
- `SDLC_BASE_SHA` and `SDLC_TMP_WORKTREES` were empty in my shell. Export the base sha from the brief in the same call as the scope guard, or the guard passes vacuously.
- `check.sh` took 1202 s here against the recorded 897 s. Run it with a Bash timeout well above 20 minutes.
- Criterion 3 relies on `sleep 2` windows with real processes, so it is timing-sensitive. It passed once on a host running a fanout wave.
- Three places go slightly beyond the handoff's literal wording:
  - `schedule` reads `host_load()` only when `max_load` is set, so a policy with the cap off makes no load call.
  - `case_rr` has one assertion the handoff did not ask for: `load=24` against cap 24 admits, which pins "equal to the cap admits".
  - `host_load` also catches `AttributeError`, for a platform with no `os.getloadavg`.
- `load_policy` drops a `max_load` of 0 from the loaded policy, so off always means the key is absent from `policy show` and `capabilities --json`.
- `status --json` carries `load` whenever `max_load` is set. If the host reports no load average, `value` is null and `over` is false.
- `--default max_load=N` is not special-cased: it lands in `default_need` as an uncapped resource name, as any unknown name did before.
- A seam file that is unreadable or not a number falls through to the real load average, as the handoff specifies. `case_load` replaces the file atomically so no poll sees a half write; the shell criteria use a plain `echo >`.
- Existing behavior I did not touch: `case_cap` and `case_livegroup` guard their status checks with `label == 'real'`, but the controls loop passes `real0`, `real1` and so on, so those checks never run.
- Nothing is committed and no throwaway worktree was created.
- Limit from the handoff: the admission rule is proved with a fake load. Nothing here shows that a real cap shortens a real gate on a loaded host.
