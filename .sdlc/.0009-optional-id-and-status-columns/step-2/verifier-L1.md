<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- The handoff-format doc no longer makes an unqualified claim that board.py never parses front matter: pass. Evidence: `grep -n "does not parse" plugins/sdlc-lite/skills/handoff-format/SKILL.md` gives rc=1. That literal grep proves nothing, because it also had no match at HEAD, where the line reads "neither `run.sh` nor `board.py` requires or parses it". So I checked with a broader pattern that fails at HEAD. In a throwaway HEAD worktree, `grep -n "does not parse\|parses it"` matched line 45 with the unqualified board.py claim (rc=0). In the working tree, line 45 now reads "`run.sh` never requires or parses it. `board.py` reads `id`/`status` from front matter for display only (via `tickets.py`'s parser ...); it still never requires, validates, or writes front matter ... `scripts/tickets.py` remains the sole parser and writer of front matter semantics." The code says the same thing: board.py:28 has `import tickets  # ... the only front matter parser`, board.py:169-173 has `ticket_of` calling `tickets.parse`, and it treats any error as no front matter.
- The board SKILL.md text around "Task, Step, Status" documents the ID/Ticket columns: pass. Evidence: `grep -n "Task, Step, Status" plugins/sdlc-lite/skills/board/SKILL.md` matches line 3, and that same description line now adds "gains optional ID and Ticket columns when a rendered task's handoff.md has ticket front matter". A new rule line (line 18 in the diff) describes the gating and the empty cells. At HEAD, `grep -c "ID\|Ticket"` on the file returned 0; in the working tree it matches. The doc agrees with board.py:17-20 (columns appear only when at least one rendered task has front matter).
- `plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: it printed "ok: 18 role levels, 8 agents checked / selftest: PASS / tickets selftest: PASS / board selftest: PASS / ok: shellcheck / ok: plugin validate", check_rc=0.

## Out of scope changes
None made by this step. The working tree also has changes from earlier steps of the same task:
- `plugins/sdlc-lite/scripts/board.py` and `plugins/sdlc-lite/scripts/check.sh` come from step 1 (its builder-L3.md lists them).
- The edits to `.sdlc/0009-optional-id-and-status-columns/handoff.md` (Intent/Constraints, status: ready) come from the task's clarify stage.

This step changed only the two SKILL.md files.

## For the next attempt
None
