## Task goal
A role run that ends without its required output is reported as a failed run, never as done.

## Step 3: Document exit 3 and the builder rerun rule
level: L1
### Do
Update these files:
- `CLAUDE.md`, Layout bullet for `scripts/run.sh`: after a run, run.sh checks the saved result for the role's required section. It exits 3 and names the section when that section is missing. The result file and `runs.jsonl` line are kept.
- `CLAUDE.md`, the `scripts/steps.py` `next` description: a builder result with no done/blocked Status maps to `rebuild` at its level, and two in a row map to `stop`. It is no longer an error.
- `CLAUDE.md`, Later line: remove "a Stop hook that checks result format". The Later list keeps its other items.
- `plugins/sdlc-lite/skills/chain/SKILL.md`, step 4: say that `run.sh` exits 3 when the result lacks its required section. Say to then run `steps.py next` as usual, since the result file exists. Add a rule next to rule 5 in the words "no done/blocked" `## Status`. The rule: `next` prints `rebuild` at the same level, it is never a fail and never a bump, and a second in a row → stop.
- `plugins/sdlc-lite/agents/conductor.md`, "How you run roles": one sentence saying that run.sh exit 3 means the role ended without its required section, and that it goes through `steps.py next`, never to done.
- `.claude/agents/sdlc-lite-author.md`: add the matching line only if it already describes run.sh exit codes or the `next` rules. Keep it in sync with CLAUDE.md.
### Acceptance criteria
Run every command below from the repo toplevel.
- `grep -q 'exits 3' CLAUDE.md`
- `grep -q 'exits 3' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -q 'exit 3' plugins/sdlc-lite/agents/conductor.md`
- `! grep -q 'a Stop hook that checks result format' CLAUDE.md`
- `grep -q 'Bash write guard for read-only roles' CLAUDE.md`
- `grep -q 'no done/blocked' plugins/sdlc-lite/skills/chain/SKILL.md`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
