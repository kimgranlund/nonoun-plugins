<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -qF 'scripts/footprint.py" selftest || fail=1' plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: exit 0 on the built tree (c1=0). It exits 1 in a throwaway worktree at `$SDLC_BASE_SHA` (22cf2d8), so the check can fail. The diff adds the line directly after the `messages.py` selftest line (check.sh:25), and the header comment now lists `footprint.py`.
- `grep -qF 'scripts/footprint.py' docs/references/sdlc-internals.md`: pass. Evidence: exit 0 on the built tree, exit 1 at base. The new `## \`scripts/footprint.py\`` entry sits directly after the `order.py` entry. It has 3 sentences and covers everything the handoff asks for: what it measures (superseded dirs excluded, runs.jsonl role/level counts), `check --max-files N --max-bytes N` exiting 1 and naming the limit, read-only on ticket folders, and `check.sh` running its selftest. It does not copy the Baseline table.
- `grep -qF -- '--max-files' docs/references/sdlc-internals.md`: pass. Evidence: exit 0 on the built tree, exit 1 at base.
- Scope criterion (`test -z "$( { git diff --name-only "$SDLC_BASE_SHA" ... } | grep -vxF ...)"`): pass. Evidence: exit 0. The changed list is only `docs/references/sdlc-internals.md` and `plugins/sdlc-lite/scripts/check.sh`. I checked that it can fail: in the base worktree, after adding an untracked `stray.txt`, the same predicate exited 1.
- Builder result holds footprint output for T-0188, T-0164, T-0181 and T-0175, matching the Baseline table: pass. Evidence: builder-L1.md has all four outputs. I reran `python3 plugins/sdlc-lite/scripts/footprint.py .sdlc/<dir>` for each ticket and got the same numbers. Format is steps / role runs / files / bytes / .md bytes:
  - 0188: 1/2/8/8010/4521
  - 0164: 1/2/8/10050/6586
  - 0181: 5/15/51/214502/185323
  - 0175: 8/21/69/224330/187209

  These match every row of `docs/lean-sdlc/design.md` "Baseline (measured 2026-10-03)". The per-role breakdowns also agree with the table's notes in parentheses. For example, T-0181 has 3 planner runs (L2 1, L3 2) and 5 builder runs (L2 1, L3 4).
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: rc=0, and the output includes `footprint selftest: PASS`. It printed `skip: shellcheck not installed`, the same as the builder's run.
- (guard) `python3 scripts/check-packaging.py`: pass. Evidence: exit 0.
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: exit 0.
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: pass. Evidence: exit 0.
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`: pass. Evidence: exit 0, no output.

## Out of scope changes
None. `git diff` shows changes only to check.sh (header comment plus one selftest line) and sdlc-internals.md (one new entry). The untracked files are all step artifacts under `.sdlc/0193-footprint/step-2/`. I removed the throwaway worktree afterwards and confirmed it no longer appears in `git worktree list`.

## For the next attempt
None
