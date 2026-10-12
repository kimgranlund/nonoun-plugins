<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- #1 `test -f docs/reports/2026-10-08-lean-template-hunks-0301.md` and it holds a disposition (accept, adapt or decline, with a reason) for each of the four hunks plus the standing-orders note, and states the receipt checker and T-0299 preflight are not built: pass. Evidence:
  - `test -f` gave report=0 on the built tree and report=1 in a throwaway worktree at d85d9eef, the parent of commit 5c2a6797 that added the report.
  - Its "Disposition per hunk" table and sections 1 to 5 give a disposition and a reason for each item: handoff-format template (adapt), planner rule 1 (adapt, in part declined), planner rule 14 with whole-suite timing (adapt), fanout.py rerun-all briefs (adapt, plus solo.md), and the standing-orders note (decline).
  - Paragraph 2 says the install-receipt integrity check and the T-0299 preflight "are proposals in the maison review, not built, and nothing here claims them".
  - Hunk set checked against the source: `grep '^## '` on the maison proposed-diff.md lists handoff-format/SKILL.md, planner.md (@@ -24 and @@ -41, which are rules 1 and 14), fanout.py and standing-orders.md. That matches the report.
- #2 `grep -q 'selected-test count'` and `grep -q 'integration gate'` in plugins/sdlc-lite/agents/planner.md, and `grep -q 'validation scope'` in plugins/sdlc-lite/skills/handoff-format/SKILL.md: pass. Evidence: a=0, b=0, c=0 on the built tree. In the base worktree at d85d9eef all three gave 1.
- #3 `! grep -q 'rerun them all' plugins/sdlc-lite/scripts/fanout.py` and `! grep -q 'rerun all checks' plugins/sdlc-lite/agents/solo.md`: pass. Evidence:
  - Built tree, with `test -f` guarding each path so a missing file cannot pass: d=0, e=0.
  - Base worktree: d=1, e=1.
- #4 `python3 plugins/sdlc-lite/scripts/check.py` exits 0: pass. Evidence:
  - Built tree: rc=0, "ok: 19 role levels, 9 agents, 22 generated definitions checked".
  - Bite check, first try: copying the current check.py onto the base worktree failed with `ModuleNotFoundError: prompt_lint`, because later commits added that module.
  - Bite check, second try: I put check.py from commit 5c2a6797 onto the d85d9eef tree instead. It gave rc=1 with 10 item-46 FAIL lines: the five planner phrases, solo.md "still says rerun all checks", fanout.py "(2 expected)" and "still says rerun them all", and handoff-format "validation scope".
  - Item 46 is still present in the current check.py at lines 182-183 and 640-659, including its own mutants.
- #5 `tickets.py --root .sdlc check`, `steps.py selftest`, `fanout.py selftest`, `claude_roles.py generate --check` and `codex_roles.py generate --check` exit 0: pass. Evidence: all five gave rc=0 on the built tree.
  - tickets.py printed warnings only: closed-ticket placeholders and the flat layout.
  - The others printed "steps selftest: PASS", "fanout selftest: PASS", "Claude agent definitions verified (22 files)" and "Codex agent definitions verified".
- #6 No em or en dash in the changed files, and `git diff --check` is clean: pass. Evidence:
  - `grep -c` for U+2014 and U+2013 gave 0 in all 23 files changed by 5c2a6797, including the report.
  - Positive control: the same grep on `printf 'x\u2014y'` gave 1, so the pattern does match.
  - `git diff --check` gave rc=0 with no output.

## Out of scope changes
None.
- The ticket work is committed at 5c2a6797, an ancestor of HEAD 4694d0cd. Its files are the four source files, the 12 regenerated planner and solo copies, check.py item 46, the report and the task artifacts. The two `generate --check` runs confirm the regenerated copies match.
- The current working tree changes only run artifacts under `.sdlc/0385-template-hunks-0301/` (base-sha, runs.jsonl, skips.md, an attempt json), per `git status --short`.
- No criterion covers the Done-when item "sent to the maison conductor", and I did not verify it.

## For the next attempt
None
