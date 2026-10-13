<!-- role=solo level=L2 model=sonnet effort=high -->
## Output
T-0510 is built and its checks pass. The one batched verifier has not run: `agents/solo.md` says the parent starts it, not solo, so I left it for the parent despite the brief's line. `verify_scope.py` exited 1 (`tests-gate: red-control: no (red) criterion`), so the report ends `verify: needed`.

**Changes**
- `tickets.py`: reads `profile:`, `local_gate:` and `full_gate:` from `.sdlc/config` beside `hash_bound:`. New helpers `profile`, `local_gate_commands`, `full_gate_commands` and `inner_loop`. A handoff line `profile: default` opts a ticket out.
- `solo_run.py`: the new `inner_loop_brief`, called from `dispatch_json` and `run`, runs before the budget gate and the record write.
  - A criterion span equal to a `full_gate:` command exits 2, names the local gate, and writes no record.
  - Otherwise `Checks: <local gates>` is appended when the brief has none.
  - The selftest has four cases: the refusal, plus the three negative controls from the ticket.
- `steps.py`: `lint` refuses a `(guard)` equal to a `full_gate:` command as `plan defect: full gate ... owned by the merge gate`. Four `(profile)` selftest cases: the refusal, and clean lint with no profile line, with `profile: default`, and with a different guard.
- `docs/references/sdlc-internals.md` and the `tickets.py` docstring document the profile.
- I added `## Acceptance criteria` to the ticket's `handoff.md`.

**Red first:** on the unchanged tree (`git archive HEAD`) the CLI run with the full-gate criterion exited 0 and wrote `runs.jsonl` and a dispatch file. With the change it exits 2 and writes neither.

**Run-verbatim** (the three runnable spans exit 0; the four Done-when fixture spans are listed with the defect below):
- `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` exit 0
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` exit 0
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exit 0
- `python3 plugins/sdlc-lite/scripts/check.py` exit 0
- `solo_run.py selftest` exit 127 (bare name, not runnable as written)
- `steps.py selftest` exit 127 (same)
- `python3 suite.py` exit 2 (fixture command, no such file)
- `python3 check.py` exit 0 (only because it ran from `scripts/`)

**Other checks:** `results.py selftest` and `docs_check.py` exit 0, `scripts/check-packaging.py` exits 0, and `git diff --check` is clean with no em dashes in the diff. A first `solo_run.py selftest` failed two process-kill negative controls because the control copy of `solo_run.py` couldn't import its sibling scripts; I fixed that and it now passes.

**Plan defect (blocked: plan defect: Done when spans):** the ticket's Done-when line has spans that don't run as written: `solo_run.py selftest` and `steps.py selftest` are bare names, and `python3 suite.py` is a fixture. `results.py solo-report` will list them as missing exit lines. The runnable replacements are the four exit-0 lines above.

**Other**
- `git status` shows an untracked `.sdlc/0510-inner-loop-b1-config/skips.md` that I did not create.
- Nothing was committed, per the brief.
- Held for later tickets: the planner or lane policy does not yet tell authors to put `local_gate:` commands in `(guard)` lines. B3 is the next ticket that depends on this one.

verify: needed
