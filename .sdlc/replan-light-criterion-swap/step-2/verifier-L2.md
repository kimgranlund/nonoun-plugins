<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `grep -q "steps.py swap"` in chain/SKILL.md: pass. Evidence: exit 0 in the tree; exit 1 in a HEAD worktree, so it can go red.
- `grep -q "swap applied:"` in chain/SKILL.md: pass. Evidence: exit 0 in the tree; exit 1 at HEAD.
- `grep -q "steps.py swap"` in agents/conductor.md: pass. Evidence: exit 0. The conductor.md diff shows the added swap route on the escalation bullet.
- `grep -q "steps.py swap"` in handoff-format/SKILL.md: pass. Evidence: exit 0.
- `grep -q "steps.py swap"` in level-rubric/SKILL.md: pass. Evidence: exit 0.
- `grep -q "steps.py swap"` in CLAUDE.md: pass. Evidence: exit 0; exit 1 at HEAD.
- `grep -q "inherited., .swap"` in CLAUDE.md: pass. Evidence: exit 0. The diff shows the `next` action list now ending `inherited`, `swap`. At HEAD it exits 1.
- `grep -q "steps.py swap"` in `.claude/agents/sdlc-lite-author.md`: pass. Evidence: exit 0; exit 1 at HEAD.
- `grep -q "steps.py swap"` in check.py: pass. Evidence: exit 0. The diff shows the new `PLAN_DEFECT_DOCS` entry `'steps.py swap'` covering the conductor, chain, handoff-format, level-rubric and steps.py.
- Guard-bites probe: pass. Evidence: I ran the exact command (copy the plugin, strip `steps.py swap` from the chain skill, run check.py). check.py printed `FAIL skills/chain/SKILL.md: plan-defect route missing "steps.py swap"`, and the grep exited 0. A control copy with no stripping printed 0 `route missing` lines, so the guard fires only on the stripped copy.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: pass. Evidence: exit 0, `ok: 18 role levels, 8 agents checked`. I also ran `plugins/sdlc-lite/scripts/check.sh`. Its tail shows the order, fanout, run, hook and hook-live-probe selftests, shellcheck and plugin validate all passing. The tail I saw does not show the tickets, board, steps or check.py lines. The check.sh exit code was also never captured. The `scripts/check.sh` I tried at the repo root does not exist (exit 127).
- Observable, chain/SKILL.md section 4: pass. Evidence, read from the diff:
  - The first paragraph lists `swap` → run `steps.py swap`, with exit 0 appending `swap applied: step <n>: ...` to `## Plan review` and exit 1 taking the 4.2 replan.
  - Item 4's exception reads "unless `steps.py next` prints `swap`".
  - Item 8 states the swap comes only from the verifier ("whoever writes the work never sets its check") and that a second swap on the step replans.
  - The doc's `swap L<build level>` claim matches steps.py:671-676, where `next` returns `('swap', level, ...)` and the message says "rebuild at L{level}".
- Builder's claim that the check.py docstring edit goes beyond the Do: accepted. Evidence: the diff shows one docstring edit in check.py.

## Out of scope changes
- The check.py docstring item 5 edit is beyond the Do. It only stops that docstring going stale, and the builder disclosed it. Dismissed as harmless: it is comment text inside check.py, a file the step already edits.
- The `swap old:` and `swap new:` `PLAN_DEFECT_DOCS` entries, the steps.py and verifier.md changes, and the earlier check.py edits are step 1's uncommitted work, already in the tree. They are not part of this step's diff.
- Untracked `.sdlc/` step artifacts are task bookkeeping, not project changes.
- Nothing else changed outside the files this step names.

## For the next attempt
None
