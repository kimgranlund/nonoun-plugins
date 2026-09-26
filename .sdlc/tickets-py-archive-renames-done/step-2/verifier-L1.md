<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -qE '^argument-hint:.*archive \[--dry-run\] \[--rewrite-refs\] \[--force\]' plugins/sdlc-lite/skills/ticket/SKILL.md`: pass. Evidence: in the tree it exits 0. In a throwaway worktree at HEAD^ (under `$SDLC_TMP_WORKTREES/base`, removed afterward) it exits 1, so the check can go red. `git show HEAD -- plugins/sdlc-lite/skills/ticket/SKILL.md` shows the argument-hint now reads `archive [--dry-run] [--rewrite-refs] [--force] [--numbered]`, so `[--numbered]` is kept.
- `grep -qF 'archive [--dry-run] [--rewrite-refs] [--force]' CLAUDE.md`: pass. Evidence: exits 0 in the tree and 1 at HEAD^. The Layout entry now reads "renames existing done/dropped numbered folders after the same reference scan as `close` (refuses, writing nothing, naming each citing file; `--rewrite-refs` rewrites the cites, `--dry-run --rewrite-refs` lists `rewrite <file>` lines, `--force` leaves them, no scan outside git)". That covers the facts the step asked for.
- `grep -qF 'archive [--dry-run] [--rewrite-refs] [--force]' .claude/agents/sdlc-lite-author.md`: pass. Evidence: exits 0 in the tree and 1 at HEAD^. The diff changes only the archive phrase, which now adds "after the same reference scan as `close`". The sync list "tickets.py, the /ticket, handoff-format, and /file skills, and CLAUDE.md" is unchanged.
- `test "$(grep -cF ... SKILL.md)" -ge 2`: pass. Evidence: exits 0 in the tree and 1 at HEAD^. The second match is the numbered-folders bullet. It names the same scan as `close` for every folder it would rename, including "a file inside another folder archived in the same run counts". It also says archive refuses and writes nothing while naming each citing file, and it covers `--rewrite-refs`, the `--dry-run --rewrite-refs` `rewrite <file>` lines, `--force`, and "outside git there is no scan".
- (guard) `plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: exit 0. The tail shows `tickets selftest: PASS`, `order`/`fanout`/`run`/`hook`/`hook live probe selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`.
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: pass. Evidence: exit 0 (`selftest=0`).

The builder said it edited nothing because the docs were already done. I checked that claim: `git status --short` lists only the untracked `step-2/builder-L1.md` and `runs.jsonl`. `git show --stat HEAD` (10e31c3, "wip(tickets-py-archive-renames-done): conductor run") shows that commit already holds the doc edits to the three files. So the step's work is in HEAD, not in the working tree, and all four criteria bite against HEAD^.

## Out of scope changes
None. The step touches only `plugins/sdlc-lite/skills/ticket/SKILL.md`, `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md`, as shown by `git show HEAD` on those three paths. The other files in HEAD (the `tickets.py` code and the step-1 artifacts) belong to step 1 of this task. The working tree changes are only the builder's own result files. Side note, not a project file: while cleaning up I removed the scratch files matching `/tmp/chk-*.txt`, and that included `/tmp/chk-planner.txt`, which I did not create.

## For the next attempt
None
