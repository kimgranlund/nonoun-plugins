<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -qxF '## \`scripts/evals.py\`' docs/references/sdlc-internals.md`: pass. Evidence: exit 0. The heading is at line 17, right after the `scripts/results.py` entry (line 13) and before `scripts/messages.py`. The old heading list shows it was not there before, so the check can go red.
- `grep -qF 'table-lock.json' docs/references/sdlc-internals.md`: pass. Evidence: exit 0. The diff shows the entry describing `.sdlc/evals/table-lock.json` and its three keys (`eval`, `previous_eval`, `table_sha256`).
- `grep -qF '.sdlc/evals/' plugins/sdlc-lite/skills/handoff-format/SKILL.md`: pass. Evidence: exit 0. The diff adds the layout line after the `.sdlc/messages/` line, as the Do specified.
- `grep -qF 'scripts/evals.py' plugins/sdlc-lite/AGENTS.md`: pass. Evidence: exit 0. The Contracts bullet is extended and the Verification list gains the evals line.
- `grep -qF 'evals.py lock' docs/references/codex-role-execution.md`: pass. Evidence: exit 0. The new sentence sits directly after "Regenerate the agent files after changes."
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: prints "Codex agent definitions verified", exit 0.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: pass. Evidence: prints "ok: 19 role levels, 9 agents checked", exit 0. I did not run it at the base commit, because it is green.
- (guard) `git diff --quiet "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/adapters/codex/models.json`: pass. Evidence: exit 0. Neither file changed.
- (guard) scope guard on changed and untracked files outside `.sdlc`: pass. Evidence: exit 0. The only changed or untracked non-`.sdlc` files are in the allowed list.
- Doc claims checked against the artifact (builder claims not taken from its summary):
  - `evals.py --help` shows exactly the commands and the `--root` and `--plugin` options the entry lists.
  - check.py item 14 and `skip: evals lock guard` (check.py:448) match the entry.
  - `evals.py selftest` prints PASS with the three negative controls named in the entry.
  - The diff adds no em dashes.

## Out of scope changes
None outside the allowed list. `.sdlc/AGENTS.md` is also modified and matches the "Evals" line in its Other records section. It sits under `.sdlc`, which the scope guard excludes, and is generated or step-2 work. I read the diff of the docs, AGENTS and handoff-format files and found nothing unexpected.

## For the next attempt
None
