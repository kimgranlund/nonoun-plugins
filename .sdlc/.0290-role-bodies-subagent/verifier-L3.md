<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
fail

## Criteria
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0: pass. Evidence: exit 0, `ok: 19 role levels, 9 agents checked`. Gate held before the change: exit 0 in a throwaway worktree at `main` (89768c7). Bites: deleting the `## Carry forward` heading from `agents/scout.md` in the throwaway gave exit 1 with `FAIL agents/scout.md: carry-forward text missing "## Carry forward"` and `FAIL agents/scout.md: result schema: missing ## Carry forward`.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0: pass. Evidence: exit 0, `Codex agent definitions verified`; exit 0 at `main`. Bites: the same scout mutation without regenerating gave exit 2, `generated agent drift: .../adapters/codex/agents/sdlc-scout-l1.toml`.
- `python3 scripts/check-packaging.py` exits 0: pass. Evidence: exit 0, `PASS: catalog parity, identity, skill routes, hook isolation and context links`; exit 0 at `main`. Bites: appending `-x` to `name` in `plugins/sdlc-lite/.claude-plugin/plugin.json` in the throwaway gave exit 1, `FAIL: sdlc-lite: name differs by host`. This gate does not read role body text (the scout mutation left it at exit 0).
- `for r in scout researcher architect archaeologist planner plan-reviewer builder verifier filer solo; do grep -q "results.py" plugins/sdlc-lite/agents/$r.md || exit 1; done`: fail. Evidence: run verbatim under `bash -c`, exit 1. `grep -c "results.py"` per file: scout 1, researcher 1, architect 1, archaeologist 1, planner 1, plan-reviewer 1, builder 1, verifier 1, filer 1, solo 0. At `main` the same command exits 1 with all ten at 0, so the check is not vacuous and `solo.md` is the only miss. The `## Output` section at `plugins/sdlc-lite/agents/solo.md:47-48` describes a compact report and never names `results.py`. Steelman: the builder's likely rebuttal is that `results.py` has no solo role, so the criterion is a plan defect. Checked: `results.py validate <file> --role solo` prints `invalid choice: 'solo'` and `results.py schema` lists nine roles. The rebuttal does not hold: the criterion needs the string, not a solo schema; it parses, contradicts no other criterion, and can go green with a truthful line in `solo.md`. Ordinary fail, no swap. The report's "Checks run" list never ran this loop.
- `! grep -l "run\.sh" plugins/sdlc-lite/agents/scout.md plugins/sdlc-lite/agents/researcher.md plugins/sdlc-lite/agents/architect.md plugins/sdlc-lite/agents/archaeologist.md plugins/sdlc-lite/agents/builder.md plugins/sdlc-lite/agents/verifier.md plugins/sdlc-lite/agents/filer.md plugins/sdlc-lite/agents/plan-reviewer.md`: pass. Evidence: `test -f` holds for all 8 paths, and the un-negated grep exits 1 (no match), not 2 (bad path), so the `!` is not inverting an error. Verbatim exit 0. At `main` the same command exits 1 and lists all 8 files.
- `git diff --quiet main -- plugins/sdlc-lite/agents/conductor.md plugins/sdlc-lite/agents/messenger.md plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json`: pass. Evidence: all four paths exist in the tree and in `main`; exit 0. Bites: the same command with one line appended to `conductor.md` in the throwaway exits 1, and the same form on the changed `agents/builder.md` exits 1. `main` equals the merge-base (89768c7) today, so the comparison is not stale.
- `test -s docs/reports/role-bodies-subagent.md`: pass. Evidence: exit 0, 2661 bytes; at `main` exit 1 (file absent).

Pre-change reference: `$SDLC_BASE_SHA` is dee3de4, which is HEAD with a clean tree, because the solo lane committed before this run. A worktree there is the built tree, so every red-side run used `main` instead. The throwaway was removed (`git worktree remove --force` exit 0, 0 entries left in `git worktree list`).

Claim under review: there is no `builder-*.md` (solo lane, per `skips.md`), so `docs/reports/role-bodies-subagent.md` is the claim.
- Its line-count table matches `wc -l` at `main` and HEAD for all ten files.
- "`results.py` has no `check` subcommand" matches `results.py --help` (validate, schema, key, selftest).
- Its live-run claims are not criteria and are unverified here; only `/tmp/rbs-demo` existing was observed.

Neighbors (rule 2):
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0, including the results, run, hook, and hook live probe selftests and `ok: plugin validate`. Shellcheck was skipped because it is not installed.
- `git grep -F` for ten removed phrases found no quoting dependent outside `agents/` and the generated TOML. The hits for `stop and ask`, `run.sh exports`, and `set by run.sh` are generic text in docs, skills, `steps.py`, and a hook about `run.sh`, which is unchanged.
- Generated TOML holds no literal `CLAUDE_PLUGIN_ROOT`: `codex_roles.py:62` swaps it for a token, and `sdlc-scout-l1.toml` shows `@SDLC_PLUGIN_ROOT@/scripts/results.py`.
- `git diff --check main HEAD` exits 0, and `tickets.py --root .sdlc check` exits 0 (`ok: 269 tickets, roadmap current`).

## Out of scope changes
- `.sdlc/messages/AGENTS.md`, `.sdlc/messages/new/AGENTS.md`, `.sdlc/messages/read/AGENTS.md`, `.sdlc/messages/done/AGENTS.md` (commit b2452be): every `messages.py` and `codex_roles.py` path now names this worktree (`.../.claude/worktrees/agent-a71eae2e5d02b449d/plugins/...`) instead of the main checkout. The step did not call for it. Check: `git grep -l "The script path in the commands below" -- plugins scripts` names `plugins/sdlc-lite/scripts/messages.py` as the writer, and `git log -- .sdlc/messages/AGENTS.md` shows the same rewrite from other lane worktrees in 230a9ef and 5b3c32c, put back to the main path in 8d45cb6. It is generated churn, not a hand edit, and fails no criterion. Still open: merging it as is leaves main's mailbox instructions pointing at a path that goes away with this worktree.
- `.sdlc/AGENTS.md` and `.sdlc/roadmap.md`: `tickets.py new` output. Diff read: one T-0290 row, ready count 0 to 1, managed-block sha. `tickets.py check` exits 0. Expected.
- `.sdlc/0290-role-bodies-subagent/handoff.md` and `skips.md`: the ticket's own records. Untracked `base-sha` and `verifier-L3.attempt.json` belong to this verifier run.
- 25 `plugins/sdlc-lite/adapters/codex/agents/*.toml` and `docs/reports/role-bodies-subagent.md`: called for by the step.

## For the next attempt
`plugins/sdlc-lite/agents/solo.md` holds no `results.py` reference (`grep -c` gives 0), so the ten-role loop criterion exits 1. Add a truthful one in `solo.md`, in `## Verification` or `## Output`. For example: the verifier result solo starts is checked with `results.py validate <file> --role verifier`, and solo writes no result file of its own because the schema has no solo role.

Constraints on the fix:
- Do not instruct `--role solo`: argparse rejects it (`invalid choice: 'solo'`).
- Do not add a solo role to `results.SCHEMA`: check.py rule 13 iterates it, and check.py contracts are a non-goal.
- After editing `solo.md`, run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. The three `sdlc-solo-l*.toml` files embed the body, and an un-regenerated body exits 2 with `generated agent drift`.
- Then rerun `check.py`, `codex_roles.py generate --check`, and the ten-role loop.

Not criterion failures, fixable in the same pass:
- Restore the four `.sdlc/messages/**/AGENTS.md` files to `main`'s content before any merge.
- `plugins/sdlc-lite/agents/planner.md:34` has a sentence starting in lowercase: "plan time. the dispatcher sets".
- `plugins/sdlc-lite/agents/filer.md:11` has a budget with no number, where the handoff's Do asks for numeric stop rules.
