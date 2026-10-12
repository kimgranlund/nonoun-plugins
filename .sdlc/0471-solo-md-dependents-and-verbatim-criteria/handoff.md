---
id: T-0471
title: "solo.md: search dependents before changing a shared name; run each criterion verbatim before verify: needed"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A solo builder finds the dependents of a changed shared name before it reports, and runs every acceptance criterion exactly as written before it asks for a verifier, so fewer tickets fail their first verifier round for reasons the builder could have caught.

## Intent
- Do: edit `plugins/sdlc-lite/agents/solo.md` (the shared role body; the `solo-L1`, `solo-L2` and `solo-L3` files and the Codex mapping are generated: run `python3 plugins/sdlc-lite/scripts/claude_roles.py generate` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`). Rule 1, in `## Loop` step 2 after "Touch no file outside the ticket's scope.": when the change adds, renames or removes a shared name (a contract id or dependency, a schema key, an element id, a selftest label, a command line other files repeat), run `git grep` for it first, fix each dependent the change can break, and report a dependent outside the ticket's scope as `blocked: plan defect: scope misses <path>`. Rule 2, in `## Loop` step 3: before `verify: needed`, run each acceptance criterion and Done-when command span exactly as written (the same text, not a paraphrase), list each with its exit code in the report, and report a span that cannot exit 0 on a correct tree (a padded count, output that never prints) as `blocked: plan defect: <criterion> <why>`. Write both rules in the affirmative form (state the action to take, one rule per line, a handle each: Search-dependents, Run-verbatim) and add no new prohibition; `solo.md` is already over the prompt-lint budget (17 prohibitions, `prompt_lint.py`), so the edit must not raise that count. Add a detect rule or a selftest case: a solo report with `verify: needed` that lacks one exit-code line per acceptance criterion span fails a `results.py` or `check.py` check, with an observed-red control.
- Non-goals: the `[owner: <stage>]` rule 3 of the report (it waits for the maison P0, T-0470, which covers the deferred-owner verdict mechanics); rules 4 and 5; solo overlays (T-0443); the controlled-language pass (T-0461); any model or effort change.
- Done when: `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` and `codex_roles.py generate --check` exit 0; `check.py`, `prompt_lint.py` on `agents/solo.md` (prohibition count not above 17) and `check.sh` exit 0; the new check observed red before the edit; both rules appear in the generated `solo-L1`, `-L2` and `-L3` files.
- outcome metric: K-005 first-pass rate (`docs/kpi/005-solo-first-pass-rate.md`, `solo_stats.py`), before: 89 of 123 (72 percent); the report's upper bound is 96 of 123 [U]; and the number of first-round fails whose cause is "missed a contract dependent" or "criterion span not run", before: 13 of 34 (`docs/reports/2026-10-11-solo-fails-and-blocks.md`)

## Context
Origin: T-0450 report `docs/reports/2026-10-11-solo-fails-and-blocks.md`, Ranked changes 1 and 2 (the maintainer chose "rules 1 and 2 together", 2026-10-12). Rule 1 mirrors the planner's `## Contract dependents` (T-0149) and the verifier's `git grep` rule 2; rule 2 extends `agents/solo.md` Loop step 3 and `## Verification`. Evidence per change, with the verifier result path of each ticket, is in that report. Prompt-lint baseline: `docs/reports/2026-10-11-agent-prompt-lint-baseline.md`.

## Constraints
No model or effort change. One writer on `agents/solo.md` at a time (T-0443 and T-0461 also edit it; this ticket runs first). Never hand-edit a generated file. State only what a command shows.

## Acceptance criteria
- [ ] `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` exits 0
- [ ] `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0
- [ ] `python3 plugins/sdlc-lite/scripts/check.py` exits 0
- [ ] `python3 plugins/sdlc-lite/scripts/prompt_lint.py plugins/sdlc-lite/agents/solo.md` exits 0 and prints a prohibition count not above 19, the count before this ticket (the ticket text says 17; the file read 19 before the edit)
- [ ] `python3 plugins/sdlc-lite/scripts/results.py selftest` exits 0, and its cases show a `verify: needed` solo report missing one criterion exit-code line, a paraphrased span, and a line with no exit code each flagged
- [ ] `grep -c "Search-dependents" plugins/sdlc-lite/agents/solo-L1.md plugins/sdlc-lite/agents/solo-L2.md plugins/sdlc-lite/agents/solo-L3.md` and the same for `Run-verbatim` print 1 for each file
- [ ] `bash plugins/sdlc-lite/scripts/check.sh` exits 0
