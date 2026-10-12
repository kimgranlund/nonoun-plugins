<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 land and prep --help list --light-gate: pass. Evidence: ran the span as written; exit 0. The recorded pre-edit control in red-checkpoint.jsonl shows exit 1 at base 01a8cca7.
- #2 cover --help lists --gate: pass. Evidence: span exit 0; pre-edit control exit 1.
- #3 settle --help lists --require-covered: pass. Evidence: span exit 0; pre-edit control exit 1.
- #4 tickets.py defines light_scope_globs(root) and merge_gate_declared(root): pass. Evidence: both greps exit 0; pre-edit control exit 1.
- #5 land_command emits --light-gate true: pass. Evidence: the python -c span exited 0 (assert on '--light-gate true' held); pre-edit control exit 1.
- #6 fanout SKILL.md names --require-covered and 'fanout.py cover': pass. Evidence: span exit 0; the diff shows the new section-5 paragraph and `--light-gate` in the argument-hint and the run and land text. check.py (items 24, 42) exit 0.
- #7 sdlc-internals.md names light_scope and gate-ledger.jsonl: pass. Evidence: span exit 0. The diff adds a gate-class paragraph and a cover and settle paragraph.
- #8 fanout.py contains T-0481: pass. Evidence: grep exit 0. The T-0481 selftest case 34 is at fanout.py:4656-4732 with 10 labelled expects.
- #9 Negative control (gate_class forced to full makes selftest fail on T-0481 labels): pass. Evidence: HEAD lacks the build, and `git worktree add --detach` is denied by block-stray-worktree.sh because SDLC_TMP_WORKTREES is unset, so I used a `cp -R` copy of the built plugins/sdlc-lite under the tmp prefix, as the builder did. I edited `gate_class` to return `('full','mutant')` and ran `fanout.py selftest`. It exited 1 and printed `these did not hold:` with 5 T-0481 labels: the light lane merges, land.jsonl `"gate": "light"`, the `## Closed` note `gate: light`, the README.md control (gate), and the cover ledger entry naming the merged ticket. The unmodified built tree passes (see #11).
- #10 (guard) scope diff: pass. Evidence: with SDLC_BASE_SHA=01a8cca7 the guard command exited 0. `git diff --stat` shows only fanout.py, tickets.py, SKILL.md, sdlc-internals.md and light-merge-lane.md. `git diff --check` is clean.
- #11 (guard) fanout.py selftest: pass. Evidence: `fanout.py selftest` exit 0, last line `fanout selftest: PASS`. The T-0481 labels hold, and the existing settle and roll cases stay green.
- #12 (guard) check.py, tickets.py selftest, report.py selftest: pass. Evidence: check.py exit 0 (`ok: 19 role levels, 9 agents, 22 generated definitions checked`); `tickets selftest: PASS`; `report.py selftest: all cases passed`.

Builder claims checked against the tree. The `cover` and `require_covered` code matches the handoff: ledger keys at, run_id, integration, from, to, gates, rc, log and merges; the ledger commit uses `git add -f`; red prints the `git bisect start <to> <from> --first-parent` line and exits 1; settle accepts a ledger-only diff after `to`. `gate_class` applies every light condition in the handoff and uses `steps.declared_hits`. The red checkpoint in red-checkpoint.jsonl shows 8 pre-edit red controls and an audit status of ok. process-deviations.md is absent. The builder noted that roll now prints `gate: full (roll)`; this is within the handoff and the roll cases stay green.

## Out of scope changes
None. Only the five allowed paths changed, and light-merge-lane.md has the front-matter status change the handoff asked for. Ticket-dir files under .sdlc are excluded from the scope guard.

## For the next attempt
None
