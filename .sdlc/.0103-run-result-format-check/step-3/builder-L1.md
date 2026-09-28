<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `CLAUDE.md`: the `run.sh` bullet now says it checks the saved result for the required section and exits 3 (naming the section) when it is missing, keeping the result file and `runs.jsonl` line. The `steps.py next` description now maps a builder result with no done/blocked Status to `rebuild`, with two in a row mapping to `stop`. I removed the "Stop hook" item from the Later line.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: step 4 now says `run.sh` exits 3 when the result lacks its required section, and to then run `steps.py next` as usual. I added rule 6 for a builder result with no done/blocked `## Status`.
- `plugins/sdlc-lite/agents/conductor.md`: I added one sentence to "How you run roles" saying exit 3 goes through `steps.py next`, never to done.

## Checks
- All six grep criteria passed, run together from the repo toplevel (`exits 3` in CLAUDE.md and chain SKILL.md, `exit 3` in conductor.md, the Stop hook phrase gone, the Bash write guard phrase kept, `no done/blocked` in chain SKILL.md).
- `bash plugins/sdlc-lite/scripts/check.sh` passed. I read only the last 8 lines of its output, which end with the hook selftests, shellcheck and plugin validate all ok.

## Notes
- I did not touch `.claude/agents/sdlc-lite-author.md`. It has a no-verdict route line about `steps.py next`, but it does not describe `run.sh` exit codes or the builder `rebuild` rule. The handoff says to add a line only if it already describes those, so I left it alone.
