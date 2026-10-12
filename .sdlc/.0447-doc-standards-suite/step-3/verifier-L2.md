<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 (red) ten files exist: pass. Evidence: the loop printed no MISSING, and `ls docs/specs/doc-standards` lists AGENTS, CLAUDE, README, core, delivery, design, intent, knowledge-ops, prompts and work-items. `process-deviations.md` records a red-checkpoint deviation (no pre-edit failing control for the nine (red) criteria). The files are new, so this check is red before the step. I did not rebuild the pre-edit control.
- #2 (red) registry covers every source-list type, the seven cards plus core, and S-1 to S-7 and P-1 to P-6: pass. Evidence: the command printed `ok 30` with exit 0. I read the registry: 35 rows (30 source-list types plus Agent file, Skill, Overlay, Handoff, Tool description), the exact header, and rule lines S-1 to S-7 and P-1 to P-6.
- #3 (red) `docs_check.py --root . --only standards` exits 0: pass. Evidence: "0 errors, 0 warnings". Bite checked in a throwaway copy outside git state. A broken kpi.json link gave `error S-7 ... line 8 link does not resolve`. An Enforcement set to `enforced` on a `-` Check row gave an S-7 error. A changed header gave an S-7 header error. A kpi.json `required` list with an extra key gave four S-1 errors. After restoring the real registry it was 0 errors again.
- #4 (guard) `docs_check.py --root .`: pass. Evidence: "0 errors, 24 warnings (B-2a 10, B-3a 7, D-10 3, D-11 4)", exit 0. All 24 are warnings, as the builder reported.
- #5 (red) glossary rows and "unapproved": pass. Evidence: the command printed `ok`. The file has the eight seeded terms plus `fanout lane`, the header `| Term | Part of speech | Definition | Unapproved aliases |`, and a definition for each.
- #6 (red) schemas against `KPI_REQUIRED` and the ticket and test-case enums: pass. Evidence: the command printed `ok`. I also read ticket.json: the `required` list, the status and type enums, and the size enum L1 to L4.
- #7 (red) seven `.tmpl` files: pass. Evidence: the loop printed no MISSING. I read `adr.tmpl` (one `## Decision`, with context and consequences) and `bug.tmpl` (environment, numbered steps, expected, actual, evidence, severity).
- #8 (red) `onboard.py check` reports both new entry files current: pass. Evidence: `current docs/specs/doc-standards/AGENTS.md` and `current docs/specs/doc-standards/CLAUDE.md` both matched. The other stale rows (`docs/AGENTS.md`, `docs/specs/AGENTS.md`, `docs/references/AGENTS.md`) are step 4's job. Its criterion at `step-4/handoff.md:24` and its Do at line 13 cover those three paths.
- #9 (red) required phrases in prompts.md, delivery.md, core.md and work-items.md: pass. Evidence: the command printed `ok`. I read prompts.md: seven numbered points, each naming its P rule or "No check". The `.0440-per-tier-agent-prompts/architect-L1.md` path is a code span, and T-0428, the live-run report and `results.py` are cited. The `plan defect:`, `stale lane:` and `unverified` claim matches the handoff.
- #10 (red) no em or en dash and no trailing whitespace: pass. Evidence: the command printed `ok 21`, meaning 21 files checked across `docs/specs/doc-standards`, the glossary and `docs/assets`.
- #11 (guard) diff scope: pass. Evidence: with `SDLC_BASE_SHA=ad35eaaa...` the guard printed `ok`. The changed files are the whitelisted step 1 and 2 files plus the step 3 files.

## Out of scope changes
None. The builder ran `git add -N` on the ten `docs/specs/doc-standards` files, which only marks intent-to-add and commits nothing. It disclosed this because onboard.py reads `git ls-files`. I confirmed they show as ` A` in `git status`, and the diff guard (#11) passes.

## For the next attempt
None. Steelman: I drafted a fail for the Enforcement of mixed rows, because Overlay and Agent file are `enforced` while their P-4 to P-6 rules are advisory. The registry states the "any rule in the Check cell fails a gate" convention under the table and lists each rule's own tier, which matches the built prompt_lint.py docstring and check.py item 53. S-7 accepts it. I dropped the finding.
