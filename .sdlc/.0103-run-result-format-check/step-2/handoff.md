## Task goal
A role run that ends without its required output is reported as a failed run, never as done.

## Step 2: steps.py next reruns a builder result with no Status
level: L2
### Do
In `plugins/sdlc-lite/scripts/steps.py` `next_action`, stop raising `Fail` when the newest builder result has no `done`/`blocked` under `## Status`. Route it instead:
- The newest builder has no Status, and the builder just before it in `order.ordered` has a Status (or there is none) → `rebuild L<level of that result>`. The reason says the result had no Status and was not counted as a fail.
- Two or more consecutive builder results with no Status, newest first → `stop`. The reason says to ask the user.

A builder result with no Status is never a done and never a fail. It never adds a bump, and it never changes the fail counts of verifiers paired with other builders. This mirrors the existing verifier no-verdict rule.

Update the module docstring's `next` rules and its Errors line: a builder with no done/blocked Status is no longer an error. Update the selftest:
- Replace the case `next error: a builder with no done/blocked Status` with `rebuild L2` for one such result.
- Add a case for `stop` after two in a row.
- Add a case for `verify L1` when a statusless builder is followed by a `done` builder.
### Acceptance criteria
Run every command below from the repo toplevel.
- `d=$(mktemp -d) && printf '## Step 1: x\nlevel: L2\n' >"$d/handoff.md" && printf 'Waiting for the background job to notify.\n' >"$d/builder-L2.md" && printf '{"file": "builder-L2.md"}\n' >"$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -qx 'rebuild L2'`
- `d=$(mktemp -d) && printf '## Step 1: x\nlevel: L2\n' >"$d/handoff.md" && printf 'Waiting.\n' >"$d/builder-L2.md" && printf 'Waiting.\n' >"$d/builder-L2-2.md" && printf '{"file": "builder-L2.md"}\n{"file": "builder-L2-2.md"}\n' >"$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -qx 'stop'`
- (guard) `d=$(mktemp -d) && printf '## Step 1: x\nlevel: L2\n' >"$d/handoff.md" && printf 'Waiting.\n' >"$d/builder-L2.md" && printf '## Status\ndone\n' >"$d/builder-L2-2.md" && printf '{"file": "builder-L2.md"}\n{"file": "builder-L2-2.md"}\n' >"$d/runs.jsonl" && python3 plugins/sdlc-lite/scripts/steps.py next "$d" | head -1 | grep -qx 'verify L1'`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- `! grep -q "next error: a builder with no done/blocked Status" plugins/sdlc-lite/scripts/steps.py`
