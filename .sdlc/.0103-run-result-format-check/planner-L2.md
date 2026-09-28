<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Make a role run that ends without its required result section fail loudly. `run.sh` should exit 3 and name the missing section. `steps.py next` should route a builder result with no Status to a rerun, never to done. The docs should say both.

## Step 1: run.sh checks the saved result for the role's required section
level: L2
### Do
In `plugins/sdlc-lite/scripts/run.sh`, after the result file and its `runs.jsonl` line are written, check the saved result for the role's required section. Keep both files: the evidence stays on disk and rerun numbering still advances.

Required section per role (a line that is exactly `## <Name>`, trailing whitespace allowed):

| Role | Section | Extra rule |
|---|---|---|
| builder | `## Status` | first non-blank line under it is `done` or `blocked`, any case |
| verifier | `## Verdict` | first non-blank line under it is `pass` or `fail`, any case |
| planner | `## Goal` | none |
| researcher | `## Answer` | none |
| scout | `## Map` | none |
| archaeologist | `## Summary` | none |
| architect | `## Approach` | none |
| filer | `## Warnings` | none |

These are the first sections each `agents/<role>.md` defines.

When the section is missing, or its value is not allowed, print one stderr line and exit 3. The line names the role, the missing section with its `## `, and the result path, for example `run.sh: builder result lacks ## Status (done|blocked); see <path>`. Exit codes 0, 1, and 2 keep their current meaning. Update the header comment of run.sh to document exit 3.

In `plugins/sdlc-lite/scripts/run-selftest.sh`:
- Change the stub `claude` so it can return a role-appropriate result. For example, the stub cats a JSON file named by an env var when that is set, and otherwise keeps today's `## Goal` output. The existing `.nvmrc` real run uses `builder L1`, so it must get a result with `## Status` and `done`, or it will now fail.
- Add failing-first cases in the same change:
  - builder with no `## Status` → exit 3, stderr names `## Status`, result file and `runs.jsonl` line kept
  - builder `## Status` then `maybe` → exit 3
  - verifier `## Verdict` then `maybe` → exit 3
  - planner with no `## Goal` → exit 3
  - builder `## Status` then `done` → exit 0
  - verifier `## Verdict` then `pass` → exit 0
### Acceptance criteria
Run every command below from the repo toplevel.
- `t=$(mktemp -d) && mkdir -p "$t/bin" "$t/r" && printf '#!/bin/sh\ncat "$STUB"\n' >"$t/bin/claude" && chmod +x "$t/bin/claude" && jq -n --arg r 'Waiting for the background job to notify.' '{is_error:false,result:$r,num_turns:9}' >"$t/s.json" && echo x >"$t/r/h.md" && git -C "$t/r" init -q && git -C "$t/r" add -A && git -C "$t/r" -c user.name=x -c user.email=x@x -c commit.gpgsign=false commit -qm i && top=$PWD && ( cd "$t/r" && STUB="$t/s.json" PATH="$t/bin:$PATH" bash "$top/plugins/sdlc-lite/scripts/run.sh" builder L2 h.md >/dev/null 2>"$t/err"; test $? -eq 3 ) && grep -q '## Status' "$t/err" && test -f "$t/r/builder-L2.md" && grep -q 'builder-L2.md' "$t/r/runs.jsonl"`
- `t=$(mktemp -d) && mkdir -p "$t/bin" "$t/r" && printf '#!/bin/sh\ncat "$STUB"\n' >"$t/bin/claude" && chmod +x "$t/bin/claude" && jq -n --arg r $'## Verdict\nmaybe' '{is_error:false,result:$r,num_turns:3}' >"$t/s.json" && echo x >"$t/r/h.md" && git -C "$t/r" init -q && git -C "$t/r" add -A && git -C "$t/r" -c user.name=x -c user.email=x@x -c commit.gpgsign=false commit -qm i && top=$PWD && ( cd "$t/r" && STUB="$t/s.json" PATH="$t/bin:$PATH" bash "$top/plugins/sdlc-lite/scripts/run.sh" verifier L1 h.md >/dev/null 2>"$t/err"; test $? -eq 3 ) && grep -q '## Verdict' "$t/err"`
- `t=$(mktemp -d) && mkdir -p "$t/bin" "$t/r" && printf '#!/bin/sh\ncat "$STUB"\n' >"$t/bin/claude" && chmod +x "$t/bin/claude" && jq -n --arg r $'## Findings\nx' '{is_error:false,result:$r,num_turns:3}' >"$t/s.json" && echo x >"$t/r/h.md" && git -C "$t/r" init -q && git -C "$t/r" add -A && git -C "$t/r" -c user.name=x -c user.email=x@x -c commit.gpgsign=false commit -qm i && top=$PWD && ( cd "$t/r" && STUB="$t/s.json" PATH="$t/bin:$PATH" bash "$top/plugins/sdlc-lite/scripts/run.sh" researcher L1 h.md >/dev/null 2>"$t/err"; test $? -eq 3 ) && grep -q '## Answer' "$t/err"`
- (guard) `t=$(mktemp -d) && mkdir -p "$t/bin" "$t/r" && printf '#!/bin/sh\ncat "$STUB"\n' >"$t/bin/claude" && chmod +x "$t/bin/claude" && jq -n --arg r $'## Status\ndone\n\n## Changes\nNone' '{is_error:false,result:$r,num_turns:3}' >"$t/s.json" && echo x >"$t/r/h.md" && git -C "$t/r" init -q && git -C "$t/r" add -A && git -C "$t/r" -c user.name=x -c user.email=x@x -c commit.gpgsign=false commit -qm i && top=$PWD && ( cd "$t/r" && STUB="$t/s.json" PATH="$t/bin:$PATH" bash "$top/plugins/sdlc-lite/scripts/run.sh" builder L2 h.md >/dev/null 2>"$t/err" )`
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh`
- `git diff HEAD -- plugins/sdlc-lite/scripts/run-selftest.sh` shows new cases that assert exit 3 for a builder with no `## Status` and for a verifier verdict of `maybe`.

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

## Risks
- A result that keeps its required heading but is otherwise truncated still passes. The check covers only the first required section, which is the ticket's proposal.
- Exit 3 is new to callers. `bench.sh`, `fanout.py` lane conductors, and interactive `/chain` treat any non-zero exit as a failure. Step 3 tells `/chain` and the conductor to go on through `steps.py next`. Until then, a caller that stops on non-zero only stops too early, which is safe.
- The planner requires only `## Goal`. A plan with a Goal but no steps still passes run.sh, and `steps.py split` catches it later.
- The ticket's second open item is not in this plan: why the T-0072 background hook did not stop the run. It waits on T-0076.
