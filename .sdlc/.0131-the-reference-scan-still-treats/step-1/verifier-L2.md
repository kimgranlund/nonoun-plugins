<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Other-tree paths are not references (`outside_refs` returns `[]`): pass. Evidence: ran the exact criterion command, printed `[]`, exit 0. Negative control: same command against pre-build HEAD (`$SDLC_BASE_SHA`, throwaway worktree `$SDLC_TMP_WORKTREES/base`) printed `['a.md']`, exit 1 — the check bites.
- A mixed file gets only its real cite rewritten: pass. Evidence: ran the exact criterion command, printed `['a.md'] 'see other/.sdlc/0003-x/h.md and .sdlc/.0003-x/h.md\n'`, exit 0, matching the expected string exactly.
- (guard) Real cites are still found: pass. Evidence: ran the exact criterion command, printed `['a.md', 'b.md', 'c.md', 'e.md', 'f.md']`, exit 0, matching `sorted(w)`.
- Red before, green after (`literal_re` patched back): pass. Evidence: ran the exact criterion command, printed `rc 1`, exit 0 (i.e. `selftest()` really returned 1 with the old regex, proving the new cases require the new boundary).
- The close selftest cases exist: pass. Evidence: `grep -qF "other/.sdlc/0003-x" plugins/sdlc-lite/scripts/tickets.py` exit 0.
- The archive selftest cases exist: pass. Evidence: `grep -qF "other/.sdlc/0001-alpha" plugins/sdlc-lite/scripts/tickets.py` exit 0.
- The docstrings state the rule (tickets.py): pass. Evidence: `grep -qF "starts a path token" plugins/sdlc-lite/scripts/tickets.py` exit 0; read the diff, the phrase appears in `literal_re`, `outside_refs`, and `rewrite_files` docstrings (git diff hunks at lines 240-262, 334-341).
- `starts a path token` in CLAUDE.md: pass. Evidence: `grep -qF` exit 0; read the diff, phrase is in the `scripts/tickets.py` Layout bullet with the full new sentence describing the token-start rule and the URL/prefixed-form limitation.
- `starts a path token` in `.claude/agents/sdlc-lite-author.md`: pass. Evidence: `grep -qF` exit 0; read the diff, the reference-scan passage is updated in sync.
- `starts a path token` in `plugins/sdlc-lite/skills/ticket/SKILL.md`: pass. Evidence: `grep -qF` exit 0; read the diff, the Rules section sentence is updated in sync, including the URL/prefixed-form note.
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: pass. Evidence: ran it directly, output `tickets selftest: PASS`, exit 0.
- (guard) `plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: ran it directly (full run, ~foreground), ended with `ok: shellcheck` and `ok: plugin validate`; grepped the full output for `fail|error` outside `ok:` lines and found none.

## Out of scope changes
`.sdlc/0131-the-reference-scan-still-treats/handoff.md` (task-level handoff, modified) and untracked `.sdlc/0131-the-reference-scan-still-treats/planner-L2.md` / `runs.jsonl`. Checked: `git log` shows the handoff's prior committed state was a raw template (`## Goal\nOne or two sentences...`), and the working-tree diff fills in Goal/Intent/Constraints with exactly the ask this step builds (clarify-stage content, e.g. "Literal ask: the reference scan still treats another tree's `.sdlc/0003-x`..."). This is the task-level clarify/plan output that precedes step-1, not something the builder touched as part of the `Do` list (which only names `tickets.py`, `CLAUDE.md`, `.claude/agents/sdlc-lite-author.md`, and `plugins/sdlc-lite/skills/ticket/SKILL.md`); the builder's diff for `tickets.py` etc. contains exactly 4 hunks, all accounted for by the Do steps, so this pre-existing task-level artifact is not part of the step's own change. Not out of scope for this step's criteria.

## For the next attempt
None.
