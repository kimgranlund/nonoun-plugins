---
id: T-0465
title: "Compaction prompt as a report view: /sdlc-lite:report compaction (from the ultimate-tokens handoff)"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0460, T-0461]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`/sdlc-lite:report compaction [<focus>]` returns one high signal prompt, in a fixed shape and controlled language, that the person pastes into a manual `/compact <prompt>`; most of it is derived by script from the report record, and it never runs the compaction.

## Intent
- Do: build the reviewed spec `docs/planning/compaction-prompt.md` (status proposed; read all of it, sections 1 to 10 are the contract): add a `compaction` view to `plugins/sdlc-lite/scripts/report.py` and its row in the `report` skill (`views.md`, argument hint `compaction [<focus phrase>] [--write-handoff] | compaction --clear`); derive STATE, OPEN, NEXT and POINT from the report record, `git`, `gh` and `dispatch.py status`; take GOAL, RULES and DECISIONS from the conversation with a transcript pointer or `[U]` each; render in the fixed order GOAL, RULES, DECISIONS, STATE, OPEN, NEXT, DROP with the grammar of section 5 (closed lead verbs KEEP, POINT, DROP, NEXT; one fact per line of at most 20 words; DECISION lines `<who> <date> <decision> | <reason> | <pointer>`); a `compaction_lint` in `report.py` selftest, each rule with an observed-red control (a line over 20 words, a verb off the list, a wrong section order, over 60 lines, an em dash, a line copied from `CLAUDE.md` or `AGENTS.md`, a DECISION without who, date and pointer, an inferred approval not marked `[U]`); the optional `--write-handoff` writes only `CLAUDE.local.md` under the guards of section 7 (gitignored, one replaceable `## Compaction handoff` H2, at most 8 lines) and is off by default; `--clear` removes only that H2; add the advisory `consider compaction` line to `report signals` from the context-fill signal; record a replay on fixture transcripts as in section 9 and mark it unverified if it was not an independent run.
- Review changes already made to the original handoff (do not undo them): not a `/plan` mode but a report view; script-derived sections; the `AGENTS.md` write dropped; the handoff file off by default; evidence marks added; the fact grammar aligned with `core.md`. The original is `.sdlc/0465-compaction-prompt/source-handoff.md`.
- Non-goals: running the compaction; any write to `AGENTS.md`; hosting the view in `/plan` (T-0462 may alias it later); Codex file writes; a model or effort change.
- Done when: `python3 plugins/sdlc-lite/scripts/report.py selftest` exits 0 with each compaction rule observed red before the rule; `/sdlc-lite:report compaction "<focus>"` on this repo prints one fenced prompt of at most 60 lines, a `lines: N of 60` note, and a final `NEXT` line, and its lint exits 0; `--clear` removes only the handoff H2 in a fixture; the one live check of whether Claude Code loads `CLAUDE.local.md` after `/compact` is recorded in the ticket notes (verified or unverified); `check.py`, `check-packaging.py` and `check.sh` exit 0.
- outcome metric: re-asked questions and violated standing rules in the 5 turns after a compaction, replay arm with the prompt versus a free `/compact`, before: unmeasured (the replay records the first baseline)

## Context
Origin: handoff from the ultimate-tokens conductor session of 2026-10-12, spec for `/plan compaction`; the maintainer asked for a review aligned with this session's work. Alignment sources: T-0460 (report record, views, health signals), T-0461 (grammar, closed verbs, glossary), T-0447 (`docs/specs/doc-standards/core.md`, `prompts.md`), `docs/specs/sdlc-lite/lane-lifecycle.md` section 8.1, T-0463 (hint standard), T-0464 (resolve and ship), `docs/specs/sdlc-lite/plan-doc-executor.md` (plan docs and `plan-state.json` already survive compaction). Verified in the authoring session: `CLAUDECODE=1` and `CLAUDE_CODE_ENTRYPOINT=cli` are set in a Claude Code CLI session; `CLAUDE.local.md` is not gitignored in this repository today, so the build adds the entry or the guard stops.

## Constraints
No write to `AGENTS.md` or `CLAUDE.md`. Read-only except the report snapshot and, with `--write-handoff`, the one H2 in `CLAUDE.local.md`. Never record an approval the person did not give in their own words. No model or effort change. One writer on `report.py` and `core.md` at a time (runs after T-0460 and T-0461).
