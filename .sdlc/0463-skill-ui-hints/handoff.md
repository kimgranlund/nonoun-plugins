---
id: T-0463
title: "Standardize skill argument hints and question UI across all skills, with a parity lint"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0461, T-0468]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every user-invocable skill shows a consistent, complete argument hint, documents its arguments in one table, and asks its questions in one UI style, and a lint keeps hints and the real flags in agreement.

## Intent
- Do: (1) Write the standard into `docs/specs/doc-standards/prompts.md` (or a new `skills.md` card in the registry) and the skill-authoring note in `plugins/sdlc-lite/AGENTS.md`: POSIX-style hint syntax (`<required>`, `[optional]`, `a|b` choice, `...` repeat, `--flag VALUE`), order (subcommand or view first, then positionals, then flags), enums inline, defaults shown as `[--since T=last]`, at most 100 characters (longer flag sets go in the skill's `## Arguments` table with a pointer), the hint shows shape only (intent stays in `description`), one level notation `[L1|L2|L3]` with the allowed set per skill, no hint on reference skills (`checking-rules`, `checks-that-bite`, `handoff-format`, `level-rubric`). (2) Rewrite the `argument-hint` of every skill under `plugins/sdlc-lite/skills/` that reads `$ARGUMENTS` (about 31), confirming each flag against the skill body and the script it calls (for example `ticket` shows `new`, `close`, `roadmap`, `check`, `migrate` as the script supports; `fleet-retro` shows `--since`; `fanout` is not truncated); add a `sdlc-lite` router hint if the router reads arguments. (3) Add one `## Arguments` table to each skill with arguments (argument, meaning, default, example). (4) Question UI in skills that call `AskUserQuestion`: header chip at most 12 characters, labels 1 to 5 words, one decision per question, 2 to 4 options each with a one-line consequence, recommendation first and marked `(Recommended)` only when evidence supports it, a `preview` when options are code, config or layout, and an explicit `Write it in chat` option when prose is needed; apply by editing the skills' wording, no script change. (5) Lint in `check.py`: every skill that reads `$ARGUMENTS` has an `argument-hint`; the hint parses under the grammar; every `--flag` in the hint appears in the skill body and, where the skill names a script, in that script's usage text; every flag in a script's usage text is in the hint or on an explicit allowlist in the check; hint length cap. Each rule has a positive case and an observed-red control. (6) Include the new skills when they land: `report` (T-0460, draft hint `[view...] [--since T=last-report] [--last N=5] [--next N=3] [--format text|md|json]`) and the merged `/plan` (T-0467 builds it; T-0463 runs after T-0468 so it standardizes one `plan` hint and never touches the stubs); if either is not merged, list them in the ticket notes as follow-ups.
- Non-goals: renaming any skill; changing what a skill does; Codex-only hint behavior (state it unverified); a model or effort change.
- Done when: `check.py`, `check-packaging.py` and `check.sh` exit 0 with the new rules each observed red before the change; every skill that reads `$ARGUMENTS` has a parseable hint and an `## Arguments` table; a table in the ticket notes lists each skill's old and new hint; no hint lists a flag its script lacks.

## Context
Audit of 2026-10-11: mixed `{}`, `<>` and `[]` syntax (`agent`), free-text hints (`plan-goal`, `plan-loop`, `plan-campaign`, `plan-doc`, `plan-fanout`, `plan-verification`), incomplete flag coverage (`ticket`, `fleet-retro`, `fanout` truncated), mixed level notation (`[L1..L5]` on `build`, `[L1..L3]` on `plan`, `research`, `verify`), no hint on the `sdlc-lite` router. Related: T-0448 and T-0461 (clarify), T-0460 (report), T-0462 (plan merge design), `docs/specs/doc-standards/prompts.md`. Run after T-0461 because both edit skill frontmatter and `check.py`.

## Constraints
One writer on `check.py` at a time. Skills stay self-contained (`check.py` item 42). No behavior change in any skill: wording, hints and tables only.

## Plan review
- replan: step 1: step-1/builder-L3.md blocked with `plan defect:` on criterion 3 (the `^FAIL` guard also matches the `FAIL: N role levels` summary line; the builder proposes `^FAIL ` with a trailing space). Every other step 1 criterion passes and the step 1 work is in the tree, uncommitted, so its `(red)` criteria are no longer red on this tree.

## Notes
- Old and new hint per skill: [hints.md](hints.md) (33 rows; `report` and the merged `plan` are standardized here, so no follow-up for them).
