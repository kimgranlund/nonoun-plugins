<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- The skill shows the fenced `.gitignore` block next to the existing "Add `.sdlc/` to the project's `.gitignore`" sentence, with a one-line explanation per pattern: pass. Evidence: `git diff` of `plugins/sdlc-lite/skills/handoff-format/SKILL.md` adds lines 27-39, directly after the sentence on line 25. The block holds `.sdlc/.board-state.json`, `.sdlc/**/*.running` and `.sdlc/**/*.log`. Each has an explanation line: "board cache, rewritten on every `/board` render", "marker for a role run in progress", "raw role transcript". It closes with "Keep the results `.md` files and `runs.jsonl` committed."
- In a scratch repo that uses the block, `git check-ignore` ignores the three runtime files and not the three kept files: pass. Evidence: I took the block from the skill file with awk and made it the `.gitignore` of a fresh `git init` repo. Results: IGNORED for `.sdlc/.board-state.json`, `.sdlc/t/builder-L1.running` and `.sdlc/t/builder-L1.log`. Tracked for `.sdlc/t/builder-L1.md`, `.sdlc/t/runs.jsonl` and `.sdlc/t/handoff.md`.
  - Proof the check goes red, three negative controls:
    - An empty `.gitignore` leaves all 6 files tracked, so the "ignored" half goes red.
    - Dropping the `running` line leaves only `builder-L1.running` tracked. Each pattern is load-bearing on its own.
    - An over-broad `.sdlc/` ignores all 6, including the `.md`, `runs.jsonl` and `handoff.md`. The "not ignored" half goes red too.
- `plugins/sdlc-lite/scripts/check.sh` passes: pass. Evidence: its output was `ok: 18 role levels, 8 agents checked`, `selftest: PASS`, `tickets selftest: PASS`, `board selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`, `EXIT=0`. The change is docs only. The only way it could break this gate is plugin validation, which passed.
- `git diff --stat` lists only the skill file and this ticket folder: pass. Evidence: it lists `.sdlc/gitignore-board-state/handoff.md` (8 lines changed) and `plugins/sdlc-lite/skills/handoff-format/SKILL.md` (14 lines added). `git status --porcelain` shows only two untracked files, `builder-L1.md` and `runs.jsonl`, both inside the ticket folder.
- Constraints (no script, agent or level-table change; no em dashes): pass. Evidence: no file under `scripts/` or `agents/` appears in the diff. `grep -c '—'` counts 0 em dashes in the whole skill file and 0 in the added diff lines.
- Non-goals respected (this repo's `.gitignore` not edited, `.board-state.json` not moved): pass. Evidence: `.gitignore` is not in `git status`. The block also agrees with the repo's own `.gitignore`, which ignores `*.log`, `.board-state.json` and `*.running` and keeps the `.md` results and `runs.jsonl`.

## Out of scope changes
None. The `handoff.md` diff only fills in the Intent and Constraints sections of this ticket, which is inside the allowed ticket folder.

## For the next attempt
None
