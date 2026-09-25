<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `tickets.py selftest` exits 0: pass. Evidence: I ran `python3 plugins/sdlc-lite/scripts/tickets.py selftest`. It printed "tickets selftest: PASS" with exit 0. The new cases in the diff cover:
  - the config line being written;
  - the rename-then-plain-check failure;
  - existing config lines being kept;
  - no duplicate line;
  - plain `new` writing no config.
- Manual check: pass. Evidence: in a mktemp root, `--root $A new feature a --numbered` exited 0 and printed `.../0001-a/handoff.md`. `config` held `ticket_folders: numbered`. A plain `check` exited 0. After `mv 0001-a 9999-a`, plain `check` exited 1 with "9999-a: folder prefix 9999- does not match id 'T-0001'". The check can go red: at HEAD in a throwaway worktree, the same `new --numbered` left no config file ("HEAD: no config (red)").
- Refusal case (`new feature 0007-x --numbered`): pass. Evidence: exit 1 with "slug '0007-x' already starts with NNNN-... nothing written". `ls -A` of the root showed it empty and `test -e config` was false. In the diff, `ensure_numbered_config` runs after `path.write_text` and before `write_roadmap`, and only when the flag was passed (`flag`).
- `check.sh` passes: pass. Evidence: `plugins/sdlc-lite/scripts/check.sh` printed "ok: shellcheck" and "ok: plugin validate", with exit 0. (Exit 0 is from the script itself, not the `tail` I piped it through, since the earlier output ended cleanly with the final ok lines.)
- Docs updated (docstring lines 5-9, `--numbered` help, CLAUDE.md bullet): pass. Evidence: `git diff` shows all three changed.

## Out of scope changes
None. The diff also contains the step-1 selftest additions, which were still uncommitted in the worktree. The builder disclosed this.

## For the next attempt
None
