<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `grep -q -- "--agent sdlc-lite:solo" plugins/sdlc-lite/agents/solo.md`: pass. Evidence: exit 0. The start command is at the new `## Start` section in solo.md.
- The four-file `grep -q "solo"` chain (conductor.md, fix/SKILL.md, plugins/sdlc-lite/AGENTS.md, .claude/agents/sdlc-lite-author.md): pass. Evidence: exit 0. The diff shows the routing sentence in each file.
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: pass. Evidence: exit 0, "hook selftest: PASS". No hook file is in the diff.
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: pass. Evidence: exit 0, "ok: 19 role levels, 9 agents checked". The new item 19 is in both the docstring and the code.
- Item 19 negative control: pass. Evidence: I ran this on a throwaway copy under `$SDLC_TMP_WORKTREES`, not on the real tree. I removed each of the 5 phrases one at a time, and each removal gave exit 1 with `FAIL <file>: solo start path missing "<phrase>"`. Item 19 also has its own in-script negative control (`solo_route_missing` on the phrase-stripped text). The restored copy still failed, but only because my partial copy had no `docs/maintenance/claude-hooks.md`. The full tree passes (see the check.py criterion).
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: exit 0, "Codex agent definitions verified". The regenerated tomls are in the diff.
- `python3 scripts/check-packaging.py`: pass. Evidence: exit 0, "PASS: catalog parity, identity, skill routes, hook isolation and context links".
- `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: exit 0. The supervisor, run, hook, and hook live probe selftests all print PASS, and the last line is "ok: plugin validate". shellcheck is not installed, so that step was skipped, as the builder noted.
- `git diff --check main -- plugins docs .claude`: pass. Evidence: exit 0, no output.
- Do item 1, `SDLC_ROLE=solo` guarding the session: pass. Evidence: `grep SDLC_ROLE hooks/*.sh` shows block-publish, block-pattern-kill, block-disk-scan, block-stray-worktree, and block-background all key off `SDLC_ROLE` being non-empty, so `SDLC_ROLE=solo` arms them. block-role-spawn only gates conductor, so no hook change was needed.
- Builder's `--dangerously-skip-permissions` addition: accepted. Evidence: run.sh line 10 says the Claude backend runs with that flag, so the command matches run.sh's own launch.

## Out of scope changes
None. The four regenerated `adapters/codex/agents/sdlc-{conductor-l1,solo-l1,solo-l2,solo-l3}.toml` files are generated output that criterion 5 (`generate --check`) requires. I confirmed that check is green with them and that they are the only adapters files in the diff. The builder's `.sdlc/.../step-1/` artifacts are expected run output.

## For the next attempt
None. Two notes for the T-0216 live run. `steps.py lane` never prints `fix`, though the routing text mentions that case. A solo session started this way gets Claude Code's default Bash timeout cap, not run.sh's raised cap. Neither affects this step's criteria.
