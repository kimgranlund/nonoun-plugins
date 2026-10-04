## Task goal
Every role result file is validated against one declared schema before the pipeline advances, and a malformed result is refused so the pipeline does not move.

## Step 5: Document the invalid-result stop and results.py ownership
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 2, 3, 4. Make these edits, with no em dashes:
- `plugins/sdlc-lite/skills/chain/SKILL.md`, the action list at line 45: `invalid result: <path>: <reason>` from `steps.py next` (also from `steps.py review`, and the `steps.py split` refusal) is a stop. Interactive: report it and ask the user. Unattended: stop the task and report the line. It is never a rebuild, reverify, bump, or replan. Update the sentence "`run.sh` exits 3 when the result lacks its required section" to say that `run.sh` exits 3 when the result fails `results.py validate`, and that a missing or disallowed Status or Verdict still routes through items 5 and 6.
- `plugins/sdlc-lite/skills/fix/SKILL.md` step 3: add `invalid result` from `steps.py next` to the stop list.
- `docs/maintenance/sdlc-internals.md`:
  - Add an entry headed exactly ``## `scripts/results.py` `` (table, CLI, reasons, `structure_error` versus `validate`, selftest and negative control).
  - Update the `scripts/run.sh` entry (line 11): the post-run check is `results.py validate`, the heading comes from `results.py key`, and the order case.
  - Update the `scripts/steps.py` entry (line 35): the `invalid result` action for `next`, `review`, and `resume`, and the `split` refusal.
- `plugins/sdlc-lite/AGENTS.md`: under Contracts and routing, add one bullet. `scripts/results.py` owns each role's result schema (key section, allowed first values, header, declared order). `run.sh` and `steps.py` call it, `check.py` checks agent bodies against it, and no other file copies it.

Left untouched on purpose:
- `agents/conductor.md`: it says "Escalation follows /chain", and an edit there would regenerate Codex agent TOML.
- `skills/handoff-format/SKILL.md`: the `.sdlc` layout does not change, since this ticket adds no file or folder under `.sdlc/`.
- `.sdlc/AGENTS.md`: no new folder, so no router line.

Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`. It must stay green, because chain and fix are not preloaded skills.
### Acceptance criteria
- `grep -qF 'invalid result' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -qF 'invalid result' plugins/sdlc-lite/skills/fix/SKILL.md`
- ``grep -qxF '## `scripts/results.py`' docs/maintenance/sdlc-internals.md``
- `grep -qF 'invalid result' docs/maintenance/sdlc-internals.md`
- `grep -qF 'scripts/results.py' plugins/sdlc-lite/AGENTS.md`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/results.py -e plugins/sdlc-lite/scripts/check.sh -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e plugins/sdlc-lite/scripts/check.py -e plugins/sdlc-lite/scripts/steps.py -e plugins/sdlc-lite/scripts/fanout.py -e plugins/sdlc-lite/scripts/traces/selftest.py -e plugins/sdlc-lite/skills/chain/SKILL.md -e plugins/sdlc-lite/skills/fix/SKILL.md -e docs/maintenance/sdlc-internals.md -e plugins/sdlc-lite/AGENTS.md | { ! grep -q .; }`
