<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/chain/SKILL.md`: added the `invalid result: <path>: <reason>` stop to the section 4 action list. It covers `steps.py next`, `review` and `resume`, plus the `split` refusal text. Interactive runs report the line and ask the user. Unattended runs stop the task and report the line. It is never a rebuild, reverify, bump or replan. Also reworded the exit 3 sentence: `run.sh` exits 3 when the result fails `results.py validate`, and a missing or disallowed Status or Verdict still routes through items 5 and 6.
- `plugins/sdlc-lite/skills/fix/SKILL.md`: step 3 stop list now includes `invalid result` from `steps.py next`.
- `docs/maintenance/sdlc-internals.md`:
  - New entry headed ``## `scripts/results.py` ``. It covers the table, CLI, reasons, `structure_error` versus `validate`, `key_value`, and the selftest with its negative control.
  - `scripts/run.sh` entry: the post-run check is `results.py validate`, the heading comes from `results.py key`, and the section-order case exits 3 naming `comes before`.
  - `scripts/steps.py` entry: `invalid result` action for `next`, `review` and `resume`, and the `split` refusal.
- `plugins/sdlc-lite/AGENTS.md`: new Contracts and routing bullet on `scripts/results.py` owning the schema.

## Checks
- `grep -qF 'invalid result' plugins/sdlc-lite/skills/chain/SKILL.md`: rc 0
- `grep -qF 'invalid result' plugins/sdlc-lite/skills/fix/SKILL.md`: rc 0
- ``grep -qxF '## `scripts/results.py`' docs/maintenance/sdlc-internals.md``: rc 0
- `grep -qF 'invalid result' docs/maintenance/sdlc-internals.md`: rc 0
- `grep -qF 'scripts/results.py' plugins/sdlc-lite/AGENTS.md`: rc 0
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: rc 0 ("Codex agent definitions verified")
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: rc 0 ("ok: 19 role levels, 9 agents checked")
- Scope guard against `SDLC_BASE_SHA=f45649ed`: rc 0
- `git diff --check`: rc 0. No em dashes in the added lines (grep count 0).

## Notes
In the chain skill, the action list adds `steps.py resume` to the sources of the invalid-result stop. The handoff named only `next` and `review` plus the `split` refusal, but `steps.py` documents that `resume` prints `invalid result` the same way.
