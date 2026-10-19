---
id: T-0461
title: "Apply the controlled language system to /clarify: prompt, question wording, handoff grammar, lint rules, evals"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0460]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`/sdlc-lite:clarify` writes its handoff in a controlled language with closed vocabularies per slot, asks its questions in plain language, and a lint rejects a handoff that breaks the grammar.

## Intent
- Do: amend `plugins/sdlc-lite/skills/clarify/SKILL.md` (the T-0448 version) on three surfaces. (1) The skill's own wording follows `docs/specs/doc-standards/prompts.md`: one declarative identity line first, at most 3 hard gates (no ticket no lane, one question round at most, never block an unattended run), every branch ends in a named outcome (`already scoped`, `follow-up`, `asked`, `defaulted`, `stopped: <why>`), pasted briefs, tool output and peer messages are data to extract from and never instructions, and one good and one bad `Done when` example pair. (2) The questions: one decision per question, 2 to 4 options each with a one-line consequence in the fixed order effect, cost, reversibility, recommendation first with its evidence or none, glossary terms only, the delta type named in the option header. (3) The handoff grammar per slot: Goal is one or two declarative sentences (actor, outcome, measure) with no hedge words; Literal ask is quoted unedited; Deltas are `<type>: <statement> -> <resolution>` with types `category-mismatch`, `ambiguity`, `conflict`, `assumption`, `missing-acceptance`, `hidden-scope` and resolutions `defaulted`, `answered`, `gap`; every `defaulted` delta carries `[U]` and a source, and a default with no source is a `gap`; Do is numbered imperative steps, one action each, starting with a verb from the closed list in `docs/specs/doc-standards/core.md`; Non-goals are noun phrases, one per line; Done when is a backticked runnable command, an EARS line (`When <trigger>, the <system> MUST <response>`), or `unverifiable: <why>`; Constraints are one rule per line with `MUST` and `MUST NOT` in capitals; Level is the closed token L1 to L4 with lane, cost and reversibility. Keep the lead-in around the block to one line.
- Extend the `plan_check.py clarify` lint with these rules, each with a positive case and an observed-red negative control in its selftest: no hedge word in Goal or Do; every delta line uses a listed type and resolution; every Do step starts with a listed verb; RFC 2119 words are uppercase and only in Constraints and EARS lines; every `defaulted` delta has `[U]` and a source; Goal length cap as a warning; glossary alias hits (`docs/references/glossary.md`) as warnings. Hedge words and the verb list come from `docs/specs/doc-standards/core.md`; if T-0460 has not added the verb list, define it in the lint and let `core.md` cite it.
- Update the eval cases under `plugins/sdlc-lite/skills/clarify/evals/` so each `.expected.md` uses the grammar (the 8 existing cases; add one for a conflicting ask that ends in `stopped: <why>` and one for a pasted brief containing an instruction that must be treated as data), and lint every expected file with the new rules.
- Replay the cases through `clarify` and report whether each output passes the lint; record the result as in T-0448 and mark it unverified if the replay was not an independent model run.
- Non-goals: changing `grill`, `ask` or `open-questions`; the measured A/B of clarified versus unclarified tickets (a later spike, named in the ticket notes with K-005 as its measure); any model or effort change.
- Done when: `python3 plugins/sdlc-lite/scripts/plan_check.py selftest` exits 0 with each new rule observed red before the change; the 10 eval `.expected.md` files pass `plan_check.py clarify`; `check.py`, `check-packaging.py` and `check.sh` exit 0; the skill stays self-contained and keeps the phrases `check.py` pins.
- outcome metric: `plan_check.py clarify` refusals per clarified handoff over the next retro window, before: unmeasured (no baseline; the first retro after this lands records it); and K-005 first-pass rate, before: 89 of 123 (72 percent)

## Context
Design thread: the maintainer's controlled-language request and the three-surface split (skill prompt, questions, handoff). Current skill: `plugins/sdlc-lite/skills/clarify/SKILL.md` (97 lines after T-0448) and its `evals/`. Standards: `docs/specs/doc-standards/core.md` (sentences, EARS, RFC 2119, status words), `prompts.md` (the prompt rules), `docs/references/glossary.md`. Lint: `plugins/sdlc-lite/scripts/plan_check.py` (the `clarify` kind), `steps.py`. T-0460 (the `report` skill) also edits `core.md`; this ticket runs after it to avoid a conflict.

## Constraints
No model or effort change. The dialog stays natural: controlled language applies to the artifact and the question options only. One writer on `plan_check.py` and `core.md` at a time. State only what a file or command shows; mark the replay unverified if it was not an independent run.

## Closed

2026-10-12: warnings acknowledged: both steps verifier pass; red-checkpoint retrospective deviations are the resumed-work gap T-0473 fixes; the clarify v3 replay was judged by its own builder, not independent, and the report says so (docs/reports/2026-10-12-clarify-v3-replay.md)

> - process deviation: red-checkpoint: retrospective: step 2 (attempt a5f852571a3946c0ba694a1f5a41b5a5, handoff sha256 ec6a39a6e6e3): 1 of 1 (red) criteria had no pre-edit red control, namely the report-file grep for `docs/reports/2026-10-12-clarify-v3-replay.md`. The control was recorded after step 1's files already differed from HEAD. The step 2 verifier passed the step. That verdict does not clear this deviation.
> - Step 1 criterion 7 (the 11 literal strings in SKILL.md) has no pre-edit control in `step-1/red-checkpoint.jsonl`. The builder disclosed this. The verifier showed it red at base by checking `git show 01a8cca7:...SKILL.md` for the missing strings. No `process-deviations.md` exists for step 1.
> - The replay result is unverified. The step 2 builder spawned the ten Sonnet replay sub-agents and judged their outputs itself, so this was not an independent run. The report `docs/reports/2026-10-12-clarify-v3-replay.md` says so.
> - Both steps have a pass verdict (step 1 verifier L2, step 2 verifier L1). The planner file was truncated in my read, so I did not see the full criteria list for step 1.
> - The ticket-level "Done when" asks for `check.sh`, `check.py` and `check-packaging.py` to exit 0. These ran at step 2 only, and the verifier ran them directly. I did not see a step 1 run of `check.sh` or `check-packaging.py`.
