<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `docs/validation/solo-live-run.md`: the opening paragraph now says the first two arms were direct launches, and a new paragraph points to the conductor start section. Appended the "Claude Code through a conductor" section with Method, What the conductor did (lane output, the solo start command, a table of models, effort, verifier, hidden check, cost and wall time), Defects, and Limits.
- `docs/validation/solo-live-run/conductor/` (new): `session-trace.txt`, `prompt.txt`, `skips.md`, `runs.jsonl`, `verifier-L3.md`, `verifier-L3.attempt.json`, `footprint.txt`, `solo.diff`, `hidden-check.txt`.

## Checks
- Fixture rebuilt: `cp -R` of step 1's pristine project into a fresh `mktemp -d` dir (`/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/solo-cond.1ItLD1KNXX`), with `hidden_check.py` outside `project/`. On the fresh project the hidden check printed `hidden_check: 2/20 passed`. A lane probe on a separate copy printed `solo`.
- Conductor run: `env-wrapper.sh env SDLC_HEADLESS=1 BASH_DEFAULT_TIMEOUT_MS=3600000 BASH_MAX_TIMEOUT_MS=3600000 claude -p --plugin-dir <plugin> --agent sdlc-lite:conductor --model sonnet --effort high --dangerously-skip-permissions --output-format stream-json --verbose "Deliver the size-M ticket at .sdlc/slug-max-length/handoff.md." < /dev/null`: exit 0, 21:42:30Z to 21:51:43Z, result `success`, verifier verdict pass.
- `python3 hidden_check.py project` on the final tree: `hidden_check: 20/20 passed`, exit 0.
- `footprint.py <task dir> --session <transcript>` on the conductor and solo transcripts: ran, output saved in `footprint.txt`.
- `grep -q "Claude Code through a conductor" docs/validation/solo-live-run.md`: pass
- `test -d docs/validation/solo-live-run/conductor`: pass
- `grep -q "sdlc-lite:conductor" docs/validation/solo-live-run.md`: pass
- `grep -q -- "--agent sdlc-lite:solo" docs/validation/solo-live-run.md`: pass
- `grep -qi "hidden" docs/validation/solo-live-run.md`: pass
- `git diff --check main -- plugins docs`: pass, rerun after the last edit. The new untracked evidence files were also grepped for trailing whitespace and blank last lines: none found.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: `ok: 217 tickets, roadmap current`, exit 0
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. All selftests PASS, `ok: plugin validate`, `skip: shellcheck not installed`.
- The record and the evidence files contain no em dashes (grep count 0).

## Notes
Results:
- The conductor ran `steps.py lane`, which printed `solo`.
- It printed `Lane: solo because size M` and recorded a longer Lane line in `skips.md`.
- It started solo with one foreground Bash call (`timeout` 900000): `SDLC_ROLE=solo CLAUDE_PLUGIN_ROOT=$P claude -p --plugin-dir "$P" --agent sdlc-lite:solo --model sonnet --effort xhigh --dangerously-skip-permissions -- "<brief>"`.
- It made no Agent-tool spawn, so no hook denial occurred.
- Models from the transcripts:
  - Conductor: `claude-sonnet-5-5`, effort `high`.
  - Solo: `claude-sonnet-5-5`, effort `xhigh`.
  - Verifier: `claude-fable-5-1` (`fable` `xhigh` in the runner records).
- Cost:

| Session | USD |
|---|---|
| Conductor | 0.233 |
| Solo | 1.126 (0.792 of it is Fable `advisor` from the user's setup) |
| Verifier | 3.852 |
| Total | 5.21 (budget about 10) |

Defects for the planner, recorded as notes only, nothing fixed:
1. The conductor's brief told solo "Do not run the verifier; the conductor will.", and the conductor then ran `run.sh verifier L3` itself. So solo.md's own verification step was not exercised on this path. Neither agent file says who runs the verifier when a conductor starts solo.
2. No Agent-tool spawn was attempted, so this run does not prove `block-role-spawn.sh` live.
3. The conductor set `CLAUDE_PLUGIN_ROOT=$P` itself and used the literal plugin path; it did not copy solo.md's `"${CLAUDE_PLUGIN_ROOT}"` form. The stream does not show whether that variable was in its Bash environment.
4. The printed Lane line and the recorded one differ in wording; conductor.md asks for the same line in both places.
5. conductor.md's "`steps.py next <step dir>` after every verifier run" has no step dir to use on the solo lane, and the conductor did not run it.
6. Solo's mutation loop wrote `/tmp/words.bak`, outside the project.

Limits:
- The Codex conductor path was not run in this step.
- The raw stream and the three transcripts stay on this machine: under `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/solo-cond.1ItLD1KNXX` and `~/.claude/projects/-private-var-folders-n0-b1pq09652mbd8kncmz8tgkvc0000gn-T-solo-cond-1ItLD1KNXX-project/`.
- Nothing was committed.
