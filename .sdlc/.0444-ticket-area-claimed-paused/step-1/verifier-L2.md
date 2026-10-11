<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 (red) unknown area rejected: pass. Evidence: ran the criterion span verbatim via bash -c with SDLC_BASE_SHA=222f817e and SDLC_TMP_WORKTREES set; exit 0. Pre-edit red recorded in step-1/red-checkpoint.jsonl (exit 1, phase pre-edit, base_sha 222f817e), so the check can go red.
- #2 (red) listed area shows in an Area column: pass. Evidence: span exit 0; pre-edit control red in red-checkpoint.jsonl. Code: tickets.py render adds `| Area |` only when some ticket has a non-empty area.
- #3 (red) paused without a reason rejected naming paused_reason: pass. Evidence: span exit 0 (check exit 1, stderr names paused_reason); pre-edit control red. problems() adds the `status paused needs a non-empty paused_reason` line.
- #4 (red) paused with a reason passes and shows in the roadmap: pass. Evidence: span exit 0; pre-edit red. tickets selftest also pins `| ⏸️ paused (waiting on vendor \| api) |` (pipe escaped) and GLYPH['paused'] is U+23F8 U+FE0F, checked by python.
- #5 (red) claimed without claimed_by rejected naming claimed_by: pass. Evidence: span exit 0; pre-edit red.
- #6 (red) claimed with claimed_by passes and the router counts it: pass. Evidence: span exit 0 (`^- claimed: 1$` in the fixture AGENTS.md); pre-edit red.
- #7 (red) board Ticket cell shows status and area: pass. Evidence: span exit 0 (`claimed · ui-kit` on the T-0001 row); pre-edit red. board.py adds area_of beside ticket_of and leaves the ticket_of tuple unchanged.
- #8 (red) this repo's router lists the vocabulary: pass. Evidence: `grep -qF "status: proposed | ready | claimed | paused | blocked | done | dropped" .sdlc/AGENTS.md` exit 0. The .sdlc/AGENTS.md diff also shows `- claimed: 0` and `- paused: 0` stage lines and the new claim, release and pause steps.
- #9 (guard) no-area root keeps today's roadmap header: pass. Evidence: span exit 0. The tickets selftest also pins the old header with no Area column.
- #10 (guard) tickets.py selftest and board.py selftest: pass. Evidence: exit 0. The output ends `board selftest: PASS`, and `tickets.py selftest` printed `tickets selftest: PASS`. Dependent selftests I also ran: budget, dispatch, fleet_status, solo_run and steps all passed.
- #11 (guard) `tickets.py --root .sdlc check`: pass. Evidence: exit 0, with only the existing flat-layout and placeholder warnings.
- #12 (guard) only the two scripts changed outside .sdlc: pass. Evidence: span exit 0. `git status --short` outside 0444 shows only .sdlc/AGENTS.md, board.py and tickets.py.

Builder claims checked against the tree. I ran all 12 criteria myself instead of taking the builder's list. I read the tickets.py diff for ENUMS order, GLYPH, ACTIVE used at both cmd_close dedupe sites, one-way validation, config_areas, areas passed at all 8 callers, the render conditional Area column, `, paused:` in stage_lines, and the new ROUTER_PROCEDURES text. All match the Do. The note about traces/sources/tickets.py:31 holds: it calls problems() without areas, so it takes areas=None and skips the area check. That is out of this step's scope and does not break anything.

Steelman and unchecked item. I considered failing for "the no-areas error uses a literal `<root>/config`". The Do says `<root>/config`, so I dropped it. I could not rerun the criteria in a detached HEAD worktree: the block-stray-worktree hook refused the `git worktree add` because SDLC_TMP_WORKTREES was unset in that call. Red-first for the 8 (red) criteria therefore rests on the red-checkpoint.jsonl pre-edit controls (8 entries, result red, exit 1, base_sha 222f817e) and the builder's audit entry (status ok). There is no process-deviations.md.

## Out of scope changes
None. The only tracked changes are .sdlc/AGENTS.md, board.py and tickets.py, plus the task-dir artifacts and the task handoff.md edit, which belong to the ticket records.

## For the next attempt
None
