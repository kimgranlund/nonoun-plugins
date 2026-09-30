<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -qF 'cap:<name>' plugins/sdlc-lite/skills/handoff-format/SKILL.md`: pass. Evidence: rc=0 on the built tree and rc=1 in a throwaway worktree at `$SDLC_BASE_SHA` (a6ce325), so the check bites. The new text is at SKILL.md:65: `depends: [T-NNNN, file:<path>, cap:<name>, ...]`.
- `grep -qE '^provides: .*optional' plugins/sdlc-lite/skills/handoff-format/SKILL.md`: pass. Evidence: rc=0 built, rc=1 at base. The line `provides: [name, ...]   # optional, capability names this ticket delivers` sits after `from:`, as the Do asks. The satisfaction paragraph that follows the block covers file:, cap:, and check, and it matches tickets.py:109-111 and :553.
- `grep -qF 'cap:<name>' plugins/sdlc-lite/skills/ticket/SKILL.md`: pass. Evidence: rc=0 built, rc=1 at base. The new Rules bullet names the three forms, `provides:`, `(unmet)` and the stale-roadmap rerun. `(unmet)` is confirmed in tickets.py:585-587.
- `grep -qF 'provides:' plugins/sdlc-lite/skills/ticket/SKILL.md`: pass. Evidence: rc=0 built, rc=1 at base.
- Template loop (`for f in .../templates/*.md; ... grep -qF 'cap:<name>' || exit 1`): pass. Evidence: rc=0 built, rc=1 at base. `grep -c '^depends:'` gives 1 for each of bug, chore, feature, idea and spike, so the loop checks all 5 files and is not vacuous. The diff shows only the trailing comment changed, and `depends: []` is kept.
- `grep -qF 'cap:<name>' docs/maintenance/sdlc-internals.md`: pass. Evidence: rc=0 built, rc=1 at base. It is one sentence added at the start of the `scripts/tickets.py` entry.
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: pass. Evidence: "tickets selftest: PASS", exit 0. It also exits 0 at base.
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: "ok: 18 role levels, 8 agents checked", exit 0.
- Extra neighbor checks, not criteria: `codex_roles.py generate --check` printed "Codex agent definitions verified" and exited 0, since skill bodies changed. `git diff --check` was clean.

## Out of scope changes
None from this step. `plugins/sdlc-lite/scripts/tickets.py` is modified, but step-1/handoff.md says "Change only `plugins/sdlc-lite/scripts/tickets.py`", so that work belongs to step 1. `.sdlc/0153-depends-on-capability/handoff.md` is also modified. I read its diff: it fills in the task's Intent section from the clarify pass and is not a build change from this step.

## For the next attempt
None
