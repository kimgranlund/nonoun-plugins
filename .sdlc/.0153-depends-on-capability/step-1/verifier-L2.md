<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Criterion 1, cap: edge orders after its provider (provider done): pass. Ran verbatim. rc=0 and the roadmap has `| T-0002 | ... | 🟢 done` above `| T-0001 | ... | cap:widget | 🔵 ready`. It fails at `$SDLC_BASE_SHA` in a throwaway worktree: "depends on cap:widget, which no ticket has", rc=1.
- Criterion 2, cap: with an open provider renders `cap:widget (unmet)`: pass. rc=0, and the grep for `| cap:widget (unmet) |` passes.
- Criterion 3, existing file: does not block: pass. Roadmap and check both rc=0 ("ok: 1 tickets, roadmap current"), and the row shows `| file:src/present.txt |`.
- Criterion 4, missing file: is unmet but not an error: pass. Roadmap and check both rc=0, and the row shows `| file:missing.txt (unmet) |`. At base, check gave rc=1 ("depends on file:missing.txt, which no ticket has"), so this check can go red.
- Criterion 5, malformed entry `bogus`: pass. check exits 1 with `alpha: depends entry 'bogus' is not T-NNNN, file:<path> or cap:<name>`.
- Criterion 6, absolute `file:/etc/hosts`: pass. check exits 1 with the malformed-entry message.
- Criterion 7, unprovided `cap:nobody`: pass. check exits 1 with `alpha: depends on cap:nobody, which no ticket provides`.
- Criterion 8, cycle through a capability: pass. check exits 1 with `alpha: dependency cycle T-0001 -> T-0002 -> T-0001`.
- Criterion 9, non-list `provides`: pass. check exits 1 and the output contains `beta: provides 'widget' is not a list`.
- Criterion 10, docstring: pass. The python import check exits 0, and the diff shows the docstring paragraph covering the three forms, `provides` and the stale-roadmap note.
- Criterion 11, selftest labels: pass. The grep loop exits 0 for all four exact labels. The diff shows them as `expect(...)` labels.
- (guard) T-only roadmap byte-identical to the base output: pass. Ran verbatim: `cmp` rc=0. The fixture includes a `done` ticket and a multi-dependency ticket, so `render` output is exercised.
- (guard) `tickets.py selftest`: pass. "tickets selftest: PASS", rc=0.

Extra checks I ran:
- `board.py selftest` and `fanout.py selftest` both pass.
- `tickets.py --root .sdlc check` gives "ok: 170 tickets, roadmap current".
- `git diff --check` is clean.

Not independently re-run: the builder's claim of 7 mutation negative controls. Criteria 1 and 4 do go red at base, so the acceptance checks bite.

Steelman: my only doubt was that `render` now needs a `root` argument. The diff shows it is called only from `write_roadmap` and `stale` in `tickets.py`. I did not find another caller with my grep. The builder's own check is that `board.py` and `fanout.py` selftest, which import `tickets`, both pass. Dropped.

## Out of scope changes
- `plugins/sdlc-lite/scripts/tickets.py` is the only file the step allowed, and it is the only source file changed.
- `.sdlc/0153-depends-on-capability/handoff.md` is modified. The diff shows it filling in the Intent section, which is planner work on the task record and not part of the build.
- The other untracked files are `.sdlc` task artifacts.

## For the next attempt
None
