<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -qF 'invalid result' plugins/sdlc-lite/skills/chain/SKILL.md`: pass. Evidence: rc 0. The chain text reads "report the line and ask the user; unattended, stop the task and report the line. It is never a rebuild, a reverify, a bump, or a replan." It also covers `steps.py next`, `review`, `resume`, and the `split` refusal.
- `grep -qF 'invalid result' plugins/sdlc-lite/skills/fix/SKILL.md`: pass. Evidence: rc 0. The step 3 stop list now reads "`inherited` or `invalid result` from `steps.py next`".
- ``grep -qxF '## `scripts/results.py`' docs/references/sdlc-internals.md``: pass. Evidence: rc 0. The entry covers the table, CLI, reasons, `structure_error` versus `validate`, and the selftest.
- `grep -qF 'invalid result' docs/references/sdlc-internals.md`: pass. Evidence: rc 0. The `steps.py` entry lists `invalid result` for `next`, `review` and `resume`, and the `split` refusal.
- `grep -qF 'scripts/results.py' plugins/sdlc-lite/AGENTS.md`: pass. Evidence: rc 0. The diff adds one bullet under Contracts and routing.
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: "Codex agent definitions verified", rc 0.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: pass. Evidence: "ok: 19 role levels, 9 agents checked", rc 0.
- (guard) scope-limit pipeline: pass. Evidence: rc 0. Every changed or untracked file outside `.sdlc` is on the allowed list.

Other handoff Do items I checked directly:
- The `run.sh` sentence in chain now says "`run.sh` exits 3 when the result fails `results.py validate`", and that a missing or disallowed Status or Verdict "still routes through items 5 and 6".
- The `run.sh` entry in `sdlc-internals.md` names `results.py validate` as the post-run check.
- A grep for em dashes in the added lines of the docs, skills and `AGENTS.md` diff returned 0.

The guards are inherited-style gates, so I did not re-run them at the base commit. Each exited 0 on the built tree. For the content greps, the 'invalid result' and 'results.py' strings are new in the diff, so they would be red at the base.

## Out of scope changes
None for this step. The other modified files, such as `run.sh`, `steps.py` and `check.py`, come from steps 1 to 4 and are on the guard allowlist. The builder also added `steps.py resume` to the chain sources of the stop. I checked that against the `steps.py` entry in `sdlc-internals.md`, which documents `resume` printing the line, so it is consistent.

## For the next attempt
None
