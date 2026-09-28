<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0103: run.sh fails a role run whose result lacks its required section

## PR body
## Summary
A role run that ends without its required output was reported as done. In the reported case, a builder L2 on a merge step ended with "Waiting for the background job to notify." and never wrote a Status. Its result file was 95 bytes, and run.sh still exited 0.

Now run.sh checks the saved result for the role's required section and exits 3, naming the missing section, when it is absent. `steps.py next` routes a builder result with no Status to a rerun instead of erroring or treating it as done.

## Changes
- `run.sh`: after the result file and `runs.jsonl` line are written, it checks the result for the role's first required section.
  - A builder needs `## Status` followed by done or blocked.
  - A verifier needs `## Verdict` followed by pass or fail.
  - The other roles need their heading: `## Goal` (planner), `## Answer` (researcher), `## Map` (scout), `## Summary` (archaeologist), `## Approach` (architect), `## Warnings` (filer).
  - On a miss it prints one stderr line naming the role, the section and the path, then exits 3. Both files stay on disk. The header comment documents the exit codes.
- `run-selftest.sh`: the stub `claude` prints the JSON file named by `STUB_RESULT` when it is set. New cases expect exit 3 for a builder with no Status, builder `maybe`, verifier `maybe` and a planner with no Goal. They expect exit 0 for a builder `Done` (with a leading blank line and trailing space) and a verifier `pass`. The existing `.nvmrc` real run now gets a `## Status done` result.
- `steps.py`: in `next`, a builder result with no done/blocked Status gives `rebuild` at its level, and two in a row give `stop`. It is never counted as a fail or a bump. Statusless builders are left out when a verifier is paired with its builder. The docstring and selftest are updated.
- Docs:
  - `CLAUDE.md` covers the run.sh exit 3 and the `next` rule, and drops "a Stop hook that checks result format" from the Later list.
  - `skills/chain/SKILL.md` step 4 covers exit 3, and a new rule 6 covers the builder no-Status route.
  - `agents/conductor.md` has one sentence saying exit 3 goes through `steps.py next`, never to done.

## Verification
- Step 1 (verifier L1, pass):
  - The three exit 3 acceptance cases (builder with no Status, verifier `maybe`, researcher with no Answer) returned rc=3 and named the section. The builder case also kept the result file and the `runs.jsonl` line.
  - The same setups on `HEAD` returned rc=0, so the checks go red on the old code.
  - The builder `done` guard returned rc=0.
  - `run-selftest.sh` passed. Run against the old `run.sh`, it failed with `builder result '## Changes\nNone': exit 0, want 3`.
  - `shellcheck --severity=warning` was clean.
- Step 2 (verifier L1, pass):
  - One statusless builder printed `rebuild L2`.
  - Two in a row printed `stop`.
  - A statusless builder followed by a `done` builder printed `verify L1`.
  - `steps.py selftest` passed.
  - The old error case is gone.
  - At `HEAD` the first fixture exits 1.
- Step 3 (verifier L1 on Opus, pass):
  - The six doc greps are green in the tree. Five are red at `HEAD` and the preservation grep for the Bash write guard is green in both, as expected.
  - `scripts/check.sh` exited 0, including the run, steps, order, fanout, hook and live-probe selftests, shellcheck and plugin validate.

Not verified: the ticket's second open item, why the T-0072 background hook did not stop the original run. It waits on T-0076.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `run.sh` now exits 3 and names the missing section when a role run's saved result lacks its required section, such as a builder with no `## Status` done|blocked or a verifier with no `## Verdict` pass|fail. The result file and `runs.jsonl` line are kept.
- `steps.py next` maps a builder result with no done/blocked Status to `rebuild` at its level, and two in a row to `stop`. It is no longer an error.

## Follow-ups
- Find out why the T-0072 background hook did not stop the run in T-0103 (likely an Agent or Monitor background route); confirm after T-0076 ships.
- Extend `.claude/agents/sdlc-lite-author.md` line 19 to cover the builder no-Status `rebuild`/`stop` route and run.sh exit 3, so it matches CLAUDE.md.
