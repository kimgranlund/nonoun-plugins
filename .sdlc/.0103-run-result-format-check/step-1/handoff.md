## Task goal
A role run that ends without its required output is reported as a failed run, never as done.

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
