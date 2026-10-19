## Verdict
pass

## Criteria
- #1 Given identical blocked and deferred records, flat, ticket-root, and topics fixtures produce the same open-question inventory: pass. Evidence: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` printed `tickets selftest: PASS` rc=0. The new cases are at tickets.py:5327-5395: the same five-ticket fixture runs in each of the three layouts, and the selftest asserts `inv['flat'] == inv['ticket-root'] == inv['topics']`. Bite check: I copied the plugin to /tmp and replaced `td = layout_paths(root).tickets` with a hard-coded `root / 'tickets'`. The selftest then failed with `flat: [] ... ticket-root: [alpha, beta]` and `.sdlc/tickets: ticket dir does not exist`, rc=1.
- #2 Given a supplied task directory, the sweep uses the repository configuration and limits results to the requested scope: pass. Evidence: cmd_blockers resolves the ticket dir only from `layout_paths(root)` and applies `--scope` after `load(td)` (tickets.py:2261-2289). ask SKILL.md:22 says to run every command from the repository root, with the task dir only narrowing results. Live run on a throwaway flat project: `blockers --scope .sdlc/stuck` returned only `T-0001 blocked`, and `--scope .sdlc/fin` printed `none`. In the selftest, scope runs for each layout keep just `beta`. Bite check: with the scope filter replaced by `if False:`, six selftest cases failed (`a task-dir scope keeps only that ticket`, `a scope with nothing open prints none`) in all three layouts.
- #3 Resolved and closed tickets do not contribute unresolved questions: pass. Evidence: in the selftest, `gamma` (done, Deferred) and `eps` (dropped) are excluded, and a `.0099-old` folder with blocked status is excluded. In the live flat project, `fin` (done, `## Deferred`) and `.0007-old` (blocked) did not appear. On this repo, `tickets.py --root .sdlc blockers` printed `none`. A grep cross-check found six `## Deferred` handoffs, and all six have `status: dropped`. Bite checks: removing `status not in ACTIVE` made 6 cases fail (`closed ones excluded`). Removing `DOT_RE.fullmatch(name)` made the `.NNNN-slug` case fail. Both ran rc=1.
- #4 The flat blocked fixture fails against the baseline sweep and passes after the fix; missing directories are surfaced accurately: pass. Evidence: in the live flat project, the baseline `grep -rl '^status: blocked' .sdlc/tickets` gave `No such file or directory` rc=2. After the fix, `blockers` listed `.sdlc/stuck/handoff.md: T-0001 blocked: blocked` rc=0. A missing scope gives `.sdlc/nope: scope does not exist; nothing searched` rc=1. Running from the wrong cwd gives `.sdlc: ticket dir does not exist (...)` rc=1, not `none`. The selftest also asserts that the baseline grep returns rc 2 on the flat fixture and that a missing `tickets/` dir is named in the error.
- #5 Run affected ticket/layout regression tests, check.py, packaging checks, and git diff --check: pass. Evidence:
  - `tickets.py selftest` printed PASS.
  - `python3 plugins/sdlc-lite/scripts/check.py` printed `ok: 19 role levels, 9 agents, 22 generated definitions checked` rc=0.
  - `python3 scripts/check-packaging.py` printed `PASS: catalog parity, identity, skill routes, hook isolation and context links` rc=0.
  - `git diff --check` returned rc=0.
  - Negative control for the changed check.py item 29: built check.py against the base-sha ask SKILL.md printed `FAIL check.py: ask skill: ask SKILL.md missing "tickets.py --root .sdlc blockers"` and `missing "--scope"`.
- #6 Exercise the revised /ask instructions against a throwaway flat-layout project with a blocker and retain the observed inventory: pass. Evidence: docs/reports/2026-10-12-ask-layout-sweep.md keeps the observed inventory table. It says plainly that a live model `/ask` session was not run, which the handoff Constraints allow ("Report required live checks as unverified if unavailable"). I ran the skill's three sweep commands myself in a fresh flat project (blocked, deferred, done, and closed tickets, plus a fail verdict and a gap line):
  - blockers listed `later` (deferred) and `stuck` (blocked).
  - The verdict grep with `--exclude-dir='.[0-9]*'` found `.sdlc/stuck/verifier-L2.md` and skipped `.0007-old`.
  - The gap grep found only `.sdlc/later/handoff.md:29:gap: need decision`.
  
  Steelman: a strict reader could ask for a model session. The criterion asks for the instructions to be exercised and the inventory retained. The sweep commands are the inventory-producing part, and the remaining step, AskUserQuestion, is interactive, so I did not file a fail.

## Out of scope changes
None. Diff: plugins/sdlc-lite/scripts/tickets.py (new `blockers` command and its selftest), plugins/sdlc-lite/skills/ask/SKILL.md (the sweep), plugins/sdlc-lite/scripts/check.py (item 29 phrases follow the skill text), and the new report docs/reports/2026-10-12-ask-layout-sweep.md, which the Constraints require. The untracked .sdlc/0508-*/base-sha, skips.md, and verifier-L2.*.json files are run records. The dated Astra report is untouched: `git status` shows no change under docs/reports/2026-10-12-sdlc-lite-astra-review*.

## For the next attempt
None.
