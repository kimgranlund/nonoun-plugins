<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- Report exists with a disposition per hunk and the not-built statement: pass. Evidence: `test -f docs/reports/2026-10-08-lean-template-hunks-0301.md` gave exit 0 on the built tree and exit 1 in the throwaway worktree at base d85d9eef. In the report:
  - Its "Disposition per hunk" table and sections 1 to 5 cover: the handoff-format template (adapt), planner rule 1 (adapt, in part declined), planner rule 14 with whole-suite timing (adapt), the fanout.py rerun-all briefs (adapt, plus solo.md), and the standing-orders note (decline). Each one gives a reason.
  - Its second paragraph says "The install-receipt integrity check and the T-0299 preflight are proposals in the maison review, not built, and nothing here claims them."
  - I checked the hunk set against the maison source. `grep '^## ' .../0301-lean-template-bootstrap-design/proposed-diff.md` lists handoff-format/SKILL.md, planner.md (@@ -24 and @@ -41, which are rules 1 and 14), fanout.py, and standing-orders.md. That matches the report.
- planner.md and handoff-format text greps: pass. Evidence: on the built tree, `grep -q 'selected-test count'` (planner.md), `grep -q 'integration gate'` (planner.md) and `grep -q 'validation scope'` (handoff-format/SKILL.md) each exited 0. All three exited 1 at base d85d9eef, so the checks bite. Diff locations: planner.md rule 1, rule 14 and its timeout bullet, and the `### Do` template line; SKILL.md has a new paragraph after the step template.
- Old wording removed from fanout.py and solo.md: pass. Evidence: on the built tree, `! grep -q 'rerun them all' plugins/sdlc-lite/scripts/fanout.py` and `! grep -q 'rerun all checks' plugins/sdlc-lite/agents/solo.md` both exited 0. Both exited 1 at base. Both paths exist (`test -f` gave 0), so the negation is not hiding a missing file. `git grep` finds no other copy of the old wording outside check.py's own pins.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0: pass. Evidence:
  - Built tree: exit 0, ending "ok: 19 role levels, 9 agents, 22 generated definitions checked".
  - Bite check: in the base worktree with the new check.py copied over the old one, it exited 1 with 10 item-46 failures. These were 5 missing planner phrases, the solo.md affected-rerun wording plus "still says rerun all checks", fanout.py "(2 expected)" plus "still says rerun them all", and handoff-format "validation scope".
  - Item 46 at check.py:608-628 also mutation-tests itself: it removes each phrase and plants the old wording, and must flag both.
- tickets.py check, steps.py selftest, fanout.py selftest, claude_roles and codex_roles `generate --check`: pass. Evidence: all exited 0. The outputs were warnings only (closed-ticket placeholders, flat layout), "steps selftest: PASS", "fanout selftest: PASS", "Claude agent definitions verified (22 files)" and "Codex agent definitions verified".
- No em or en dashes in the changed files, and `git diff --check` clean: pass. Evidence:
  - Counting U+2014 and U+2013 with `grep -c` gave 0 in each of the 18 modified files and in the untracked report. The diff's added lines also contained 0.
  - `git diff --check` exited 0 with no output. It does not cover untracked files, so I ran a separate trailing-whitespace grep on the report: 0 hits.

## Out of scope changes
None. I checked each change outside the four named source files:
- The 12 generated role copies (planner-L1..L3, solo-L1..L3, and the six matching Codex TOMLs) are expected regenerations. Both `generate --check` runs report parity.
- The check.py item 46 change is the coverage the ticket's Done-when requires.
- The `.sdlc/0385-template-hunks-0301/handoff.md` diff only adds `## Acceptance criteria`, which the solo brief tells an L2 ticket with none to do.

Not covered by these criteria and left open: the Done-when items "committed in docs/reports/" and "sent to the maison conductor". The report is still untracked, and no listed criterion checks the reply to the maison conductor.

## For the next attempt
None
