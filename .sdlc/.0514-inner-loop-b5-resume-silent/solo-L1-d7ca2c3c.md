<!-- role=solo level=L1 model=sonnet effort=low -->
## Output
T-0514 is done: under `profile: inner-loop`, `dispatch.py resume` now prints the three-rung ladder for a running attempt whose transcript has been silent for 30 minutes or more. The ladder is the same one it prints for an orphan: ask by name, ask by id, then a new attempt at the same level with the resume addendum. I did not run the verifier.

**Changed:** `plugins/sdlc-lite/scripts/dispatch.py` only.
- **New helper:** `inner_loop()` returns true when the nearest `.sdlc/config` above the attempt file has a `profile: inner-loop` line.
- **`resume()` change:** a `running` attempt with a stored agent id now counts as resumable when `inner_loop()` is true and its transcript's last write is at least `SILENT_SECONDS` old.
- **Unchanged cases:** a repo without the profile, a live attempt written to recently, and a running attempt with no agent id or no transcript all still refuse as before.

**Checks:** `python3 dispatch.py selftest` ends `PASS`. I did not run the repo-wide checks, so the full suite is unrun.

New selftest cases:
- The ladder prints for a running attempt silent for 2 hours under the profile.
- A negative control refuses when the transcript was just written, with the profile on.
- A negative control refuses a silent running attempt when the profile is absent.

**Open:**
- **Red control:** I never ran `specgate.py red` or `redck.py record` before the edit. The ticket has no `(red)` criterion and no `## Acceptance criteria` section.
- **Verifier:** the ticket is size L1, so it needs no batched verifier. Say if you want one anyway.
- **No commit:** per the brief, `fanout.py` commits this lane.
- **Stray file:** `.sdlc/0514-inner-loop-b5-resume-silent/skips.md` appeared untracked and isn't mine. I left it alone.
