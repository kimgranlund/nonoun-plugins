<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- Step 2 (focused live run) is blocked, and no verifier ran on it. There is no `step-2/verifier-*.md`. The builder reported criteria 2 and 9 as FAIL (`read_scout_result=no` and the README line). The ticket's own "Known limits" section states there was no third cycle.
- Step 2 was built twice and blocked twice on the probe's own metric, not on behavior. First the metric cut each tool input at 200 characters. Then it looked only for the literal `scout-L1.md`, but the planner read the file through a glob.
- The step 1 verifier (L2) passed. Its output lists AC1 to AC12 as pass.
- A separate branch verification under `.sdlc/verify-t0202/step-1` (verifier-L3) has only a log, a `.running` marker and an attempt file. No verdict file exists, so it is unfinished.
- The "Done when" items "an independent verifier passed each step" and the live-run proof are therefore not met.

## PR title
T-0202: Carry forward section in scout, researcher, architect, archaeologist

## PR body
**Warning:** step 2 (live run) is blocked and unverified. See the Verification section.

### Summary
Scout, researcher, architect and archaeologist results now close with a `## Carry forward` section of at most 15 lines. It holds facts and paths later roles must not re-derive. The planner and builder contracts now say to read that section before searching and to search only what it does not answer. The planner cites the result path and does not copy the section. This is build row L10 of the lean SDLC design, `docs/lean-sdlc/design.md`.

### Changes
- `plugins/sdlc-lite/agents/{scout,researcher,architect,archaeologist}.md`: a closing `## Carry forward` template section, with the same text in all four.
- `plugins/sdlc-lite/agents/planner.md`: a reader paragraph. Read Carry forward first, search only what it does not answer, and cite the result path instead of copying the section.
- `plugins/sdlc-lite/agents/builder.md`: a reader sentence added to the first paragraph.
- `plugins/sdlc-lite/scripts/results.py`: `Carry forward` is added as the last section in `SCHEMA` for the four producer roles, with selftest cases. An out-of-order result fails with "## Carry forward comes before ## Map". Existing results without the section still validate.
- `plugins/sdlc-lite/scripts/check.py`: docstring item 15 and a `CARRY_FORWARD` guard with negative controls. It flags a producer contract missing the heading or the "at most 15 lines" text, and a builder contract missing the reader text. The step 1 builder reports that a comment label in `check.py` numbered an item 13 where the docstring says 14. Commit `3617cda` ("check.py: carry-forward comment numbering") followed.
- `plugins/sdlc-lite/adapters/codex/agents/*.toml`: 14 files regenerated with `codex_roles.py generate`.
- `docs/validation/carry-forward-live-run.md`, `docs/validation/carry-forward-live-run/` (`probe.sh`, `scout.txt`, `with.txt`, `without.txt`) and one `docs/README.md` line: the live-run report. It states the actual outcome and its limits.

### Verification
Step 1 (contracts, schema, guard, Codex agents) passed the independent verifier at L2.
- All twelve acceptance criteria passed.
- The verifier checked red-before and green-after for the out-of-order fixture (the base `results.py` accepted it, the built one rejects it).
- The verifier removed the heading from a copy of `scout.md` and the reader phrase from `builder.md` in plugin copies. The `check.py` guard flagged both.
- It also removed "at most 15 lines" from `researcher.md` and the guard flagged that too.
- `codex_roles.py generate --check` and `codex-selftest.py` (22 tests) passed, and `git diff --check` was clean.

Step 2 (focused live run) was built and not verified.
- The builder's run 2 gates were green: `check.sh` (shellcheck not installed, so skipped), `check-packaging.py`, `codex_roles.py generate --check`, and `tickets.py --root .sdlc check` ("ok: 208 tickets, roadmap current").
- Live behavior, as the builder reports it:
  - In run 2 the planner given the scout result read it and cited `.sdlc/cf/scout-L1.md`. It ran no symbol search (`symbol_searches=0`, one tree search) and did not copy the section.
  - The planner without the scout result ran `git grep -n pad_cell` (`symbol_searches=1`).
  - The scout result carried 5 Carry forward lines.
- Run 1 recounted over untruncated inputs gave the same direction. `symbol_searches` was 1 in the scout arm and the with arm (0 for the with arm, 1 for the without arm: with 0, without 1).
- The probe's `read_scout_result=no` for the with arm is a metric miss. It looks for the literal file name and the planner read the file through a glob.
- The README line and report state this outcome, not a pass.
- Limit: this is one run per arm and not a pass. Per the ticket, live proof is T-0208's.

### Limits
- The live-run report writes any em dash a role produced as `--`.
- The first Carry forward line in run 2's scout section held an em dash, which the report cannot reproduce verbatim.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- sdlc-lite: scout, researcher, architect and archaeologist results end with an optional `## Carry forward` section (at most 15 lines). Planner and builder read it before searching. `results.py` and `check.py` validate and guard it, and the Codex agents are regenerated. The focused live run is recorded as a limit, not a pass.

## Follow-ups
- decide: Step 2's live run never passed its own metric (criteria 2 and 9). Choose whether T-0208's live evidence re-proves the planner-reads-scout behavior with a probe that detects reads through a glob.
- fix-now: The scout result in run 1 listed both call sites without naming the search or scope that produced the list, which the scout contract asks for on a complete list. Check the contract wording for that clause.
- note: The branch verification at `.sdlc/verify-t0202/step-1` (verifier-L3) has no verdict, so no independent branch-level verdict exists beyond the step 1 L2 pass.
- note: A role's own em dash cannot be reproduced in a report that forbids the character. The report writes it as `--`.
