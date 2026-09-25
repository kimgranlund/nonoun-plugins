<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -c -- "--expect"` gives at least 1 for each of the three files: pass. Evidence: the command prints `file/SKILL.md:2`, `ticket/SKILL.md:2`, `CLAUDE.md:1`. The check goes red at HEAD: in a throwaway worktree the same command printed 0 for all three files.
- The /file step 3.4 command has both `--skip` and `--expect <digest>`, and step 3.5 mentions `--expect`: pass. Evidence: in `git diff`, step 3.4 of `plugins/sdlc-lite/skills/file/SKILL.md` reads `close <slug> --skip <unselected indices> --expect <digest>`, and step 3.5 reads `(`--skip` the dropped indices, with `--expect <digest>`)`. I ran the real script against a temp root and it matches the docs:
  - The dry run's last line is `expect 520f99c438b0`.
  - `--skip 1` without `--expect` refuses with rc=1 and "--skip needs --expect <digest>".
  - `--expect deadbeef` refuses with rc=1 and "... does not match the current Follow-ups ...; nothing written". Step 3.4 keys its rerun rule on the phrase `does not match`, and the refusal contains it.
- `argument-hint` shows `[--expect DIGEST]`: pass. Evidence: `ticket/SKILL.md:4` contains `[--skip N[,N...]] [--expect DIGEST] [--numbered]`. At HEAD, `grep -c "expect DIGEST"` gave 0. The claim in item 4 that `--reason` does not combine with `--expect` also matches the running script: `close demo --reason x --expect abc` gave rc=1 with "does not combine with --dry-run, --skip or --expect".
- No new em dashes: pass. Evidence: `grep -c "—"` gives 0 for `file/SKILL.md`, `ticket/SKILL.md`, `CLAUDE.md`, and `.claude/agents/sdlc-lite-author.md`. `git show HEAD:<f> | grep -c '—'` also gives 0 for each file.
- `plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: I observed `check exit=0`. The output includes `tickets selftest: PASS`, `order selftest: PASS`, `run selftest: PASS`, `ok: shellcheck`, and `ok: plugin validate`. The check can go red: in the throwaway HEAD worktree I appended a syntax error to `tickets.py` and `check.sh` exited 1.

## Out of scope changes
None from this step. The four step-2 edits are all in scope, including the `--expect` addition to the sync rule in `.claude/agents/sdlc-lite-author.md`. The working tree also has changes this step did not produce:
- `plugins/sdlc-lite/scripts/tickets.py` is step 1's work.
- `.sdlc/guard-close-skip-against-index/handoff.md` has the task Goal and Constraints filled in.

## For the next attempt
None
