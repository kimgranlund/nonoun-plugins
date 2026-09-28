<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0065: Set SDLC_ROLE=conductor for fanout lane drivers so block-publish guards lanes

## PR body
### Summary
`scripts/fanout.py` started lane drivers without `SDLC_ROLE`, so `hooks/block-publish.sh` never fired inside a lane. Only the prompt stopped a lane conductor from running `git push`, `gh` writes, or a package publish. This PR sets `SDLC_ROLE=conductor` in the shared lane env. The selftest now proves a driver receives it, and the docs that said only `scripts/run.sh` sets it are fixed.

### Changes
- **`plugins/sdlc-lite/scripts/fanout.py`**
  - `run_ticket` adds `SDLC_ROLE='conductor'` to the lane env, next to `SDLC_HEADLESS='1'`. `run.sh` still sets `SDLC_ROLE` to the role name on each role run, so roles started under a lane keep their own name.
  - The module docstring's driver env list now includes `SDLC_ROLE=conductor`.
  - The selftest `STUB` exits 1 when `SDLC_ROLE` is not `conductor`.
- **`plugins/sdlc-lite/agents/conductor.md`**: now says `run.sh` sets `SDLC_ROLE` per role run and `fanout.py` sets it to `conductor` for every lane driver, and that an interactive session has no `SDLC_ROLE`. The AskUserQuestion approval sentence is unchanged.
- **`CLAUDE.md`**: the block-publish, block-background, and fanout.py bullets now say fanout sets `SDLC_ROLE=conductor`.
- **Unchanged on purpose:**
  - The hooks and `skills/file/SKILL.md`, as the ticket required.
  - `.claude/agents/sdlc-lite-author.md` and `skills/fanout/SKILL.md`, which did not repeat the claim.

### Limitation
`block-publish.sh` is a Claude Code PreToolUse hook. It guards only the Claude sessions a driver launches: the default conductor and every `run.sh` role under it. A custom `--driver CMD` that runs `git push` directly from bash is still not blocked.

### Verification
There was one step (builder L2), and verifier L1 passed it.
- **fanout.py:** a grep finds `SDLC_ROLE='conductor'`. Before this change the grep failed.
- **Stub refuses a missing role:** run with `SDLC_ROLE` unset, it exits non-zero and prints `SDLC_ROLE not conductor`. With `SDLC_ROLE=conductor` it exits 0.
- **Selftest:** `fanout.py selftest` prints `fanout selftest: PASS`. The stub now refuses when the role is missing, so this pass also proves the lane env carries the role.
- **Docs:** greps find the new wording in the docstring, `conductor.md`, and `CLAUDE.md`. `git grep` finds no file outside `.sdlc` that still says "only `scripts/run.sh` sets it".
- **Guards:**
  - The hooks and `skills/file/SKILL.md` are unchanged.
  - No added line has an em dash.
- **`scripts/check.sh`:** the builder ran it here and in a `git worktree add` copy of HEAD. Both exited 0 with identical fail/error/warn lines. The verifier's run showed every selftest, shellcheck, and plugin validate passing. The verifier did not see the exit code and skipped the base comparison because nothing failed.
- The first plan (planner L1) was refused by the `steps.py split` lint because a criterion command did not parse. It was replanned at L3.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- fanout: lane drivers now run with `SDLC_ROLE=conductor`, so `hooks/block-publish.sh` blocks `git push`, `gh` writes, and package publishing in the Claude sessions a lane launches. The fanout selftest checks this.

## Follow-ups
- block-publish.sh matches publish commands inside heredoc and file text, not only real commands: a builder's Bash edit whose text contained "git push" was blocked in T-0065, and the builder had to work around it with a temp script.
- skills/file/SKILL.md line 18 still says block-publish "only fires when `SDLC_ROLE` is set by `scripts/run.sh`", which is stale now that fanout.py sets `SDLC_ROLE=conductor` for lane drivers (T-0065).
