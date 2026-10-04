<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `test "$(cat .sdlc/proposals/CLAUDE.md)" = '@AGENTS.md'`: pass. Evidence: I ran it and it gave exit 0.
- The grep loop over 28 strings in `.sdlc/proposals/AGENTS.md`: pass. Evidence: I ran the loop and no string was reported missing.
- The awk check for a `proposals/AGENTS.md` line after the managed end marker in `.sdlc/AGENTS.md`: pass. Evidence: exit 0. The Proposals line sits after the Evals line, below the generated block.
- `## \`scripts/proposals.py\`` header, `.sdlc/proposals/` in handoff-format, `scripts/proposals.py` in plugin AGENTS.md: pass. Evidence: exit 0. I read the diffs and the three added lines match the handoff text.
- The grep loop over 15 strings in `docs/validation/proposals-live-run.md`: pass. Evidence: nothing was reported missing.
- Date regex `2026-NN-NN` in the live-run doc: pass. Evidence: exit 0.
- `.sdlc/proposals/` holds only `AGENTS.md` and `CLAUDE.md`: pass. Evidence: exit 0.
- (guard) `tickets.py check`: pass. Evidence: `ok: 208 tickets, roadmap current`.
- (guard) `codex_roles.py generate --check`: pass. Evidence: `Codex agent definitions verified`.
- (guard) The out-of-scope file filter against `$SDLC_BASE_SHA`: pass. Evidence: exit 0. The base is `66586153`, read from the step's `base-sha` file.

Runtime behavior, checked beyond the criteria:
- I ran `proposals.py --root .sdlc --proposals $T/p scan` myself. It printed `19 new, 0 updated, 0 unchanged`. `list` showed P-0001 to P-0018 as `replan` and P-0019 as `plan-defect` with 12 occurrences. The live-run doc records the same figures (lines 94 and 96 to 105), including arm 7's `cmp` exit 1 and its note about the lost exit code.
- The doc's negative controls record exit 1 with `no eval given` and `is not in`. They also record the source and `plugins/` manifests as unchanged.
- A grep for em dashes found none in the new docs or the diff.

## Out of scope changes
- `plugins/sdlc-lite/scripts/check.sh` is modified (3 lines). The handoff's guard allowlists it, and it belongs to the step-1 selftest wiring. Not a problem: the guard run above passed with it listed.
- Untracked `.sdlc/0186-.../` run artifacts (plan-reviewer, planner, `runs.jsonl`, step folders) are run.sh output and fall under `.sdlc`, which the guard excludes.

## For the next attempt
None
