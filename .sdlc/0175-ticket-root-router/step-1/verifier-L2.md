<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Criterion 1, new under `tickets/`: pass. Evidence: ran the command. It printed `.../.sdlc/tickets/alpha/handoff.md` and `ok: 1 tickets, roadmap current`, rc=0.
- Criterion 2, numbered close with `--rewrite-refs` in a git fixture: pass. Evidence: ran the command. Output was `T-0001 done; ... moved to .0001-alpha; rewrote refs in spec.md`, then `ok: 1 tickets, roadmap current`, rc=0.
- Criterion 3, cite refusal names `spec.md` and never `roadmap.md`: pass. Evidence: ran the command, rc=0. Close refused, `spec.md` is in stderr, `roadmap.md` is not, and `tickets/0001-alpha` still exists. Selftest also covers this, and the builder's extra negative control (dropping `roadmap=` from `cmd_close` makes the case fail) fits the `outside_refs` change at tickets.py:455-477.
- Criterion 4, `close --reason`, then `number`, then `archive` under `tickets/`: pass. Evidence: ran the command. rc=0 and `check` printed `ok: 1 tickets, roadmap current`.
- Criterion 5, unsupported `ticket_root: work`: pass. Evidence: ran the command, rc=0. `new` refused with a message holding `ticket_root: tickets`, and no `alpha`, `work` or `roadmap.md` was written. `check` failed. I also ran `roadmap`, `archive`, `number` and `close --reason` on the same root. Each exited 1 and `.sdlc` still held only `config`.
- Criterion 6, stray ticket folder at `<root>`: pass. Evidence: ran the command, rc=0. `check` failed with `alpha: ticket folder outside the ticket root`, `new beta` refused, and no `tickets/` dir was created. `roadmap`, `number` and `archive` also refused on the stray root. `close a --reason x` refused with "not a ticket" because it looks under `tickets/`, and wrote nothing.
- Criterion 7, docstring phrases: pass. Evidence: ran the command, rc=0. `tickets.__doc__` contains both `ticket_root: tickets` and `outside the ticket root`.
- Criterion 8, `ticket_dir` mutation: pass. Evidence: ran the command (the `def ticket_dir(root):` body replaced with `return root`), rc=0. The unmutated copy's selftest passes and the mutated copy's fails, so the new selftest cases catch it.
- Criterion 9, `strays` mutation: pass. Evidence: ran the command (the `def strays(root):` body replaced with `return []`), rc=0. The mutated copy's selftest fails, so the cases catch it.
- (guard) `tickets.py selftest`: pass. Evidence: `tickets selftest: PASS`, rc=0. The diff shows no removed lines inside existing selftest cases. The only removed lines are in code that was rewritten to use `td`.
- (guard) default layout: pass. Evidence: ran the command, rc=0. The ticket sits at `<root>/alpha`, there is no `tickets/` dir, and the roadmap holds `| [alpha](alpha/handoff.md) |`.
- (guard) `render` byte-identical to base: pass. Evidence: ran the command with `SDLC_BASE_SHA=c6d39d0f`, rc=0.
- (guard) scope, only `tickets.py` outside `.sdlc`: pass. Evidence: ran the command, rc=0.

Dependents checked:
- `board.py selftest`, `fanout.py selftest` and `traces.py selftest` all print PASS.
- `tickets.load` keeps its signature. `fanout.py:283` and `traces/sources/tickets.py:18` still call it.
- `git diff --check` is clean.

Steelman: I drafted the fail "`close` on a stray reports 'not a ticket' instead of a stray message". The builder would answer that the spec only requires the refusal to write nothing, and that `strays` fires for `new`, `check`, `roadmap`, `archive` and `number`. I dropped the finding.

## Out of scope changes
None. The only tracked source change is `plugins/sdlc-lite/scripts/tickets.py`. The other changes are under `.sdlc` (the step's artifacts and other tickets' `runs.jsonl` and plan-reviewer files), which are not part of the step.

## For the next attempt
None
