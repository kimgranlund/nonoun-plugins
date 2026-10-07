---
id: T-0161
title: "Spike: read-only reorganization plan on this repository"
type: spike        # feature | bug | chore | spike | idea
status: done        # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0160]          # ticket ids, e.g. [T-0002]
created: 2026-09-29
---

## Question
Which rules let a script classify this repository's documents and produce a move plan that a person would accept, and which of the open findings in the draft design are real in practice?

## Goal
A recommendation with cited evidence, written back into this file: the rules to keep, the rules to change, and whether apply is worth building.

## Context
Draft design: `docs/planning/repo-onboarding/reorganization.md` (v0.6). Three review rounds each found new edge cases, so the user chose on 2026-09-29 to test the rules against real files before specifying more. The design's "Open findings" section lists N1, N2, N3, N5, N8, N9, and N15 from `docs/reports/repo-onboarding-design-review-3.md`.

Build a throwaway prototype that does only the read-only part:

1. Parse `docs/layout.md` with the parser from T-0160.
2. Inventory every tracked Markdown file and build the link graph.
3. Classify the documents under `docs/` as placed, misplaced, or unplaced.
4. Print a plan: moves, link rewrites, unplaced files, frozen candidates, and links that are already broken.

Run it on this repository with a `docs/layout.md` written for the trial. The design's "First trial" section lists the known mismatches, the paths to freeze, and the two links that are already broken.

Answer at least these:

- How many documents are placed, misplaced, and unplaced, and does each proposed move look right to a person?
- How many cites of a moved document are Markdown links, and how many are backticked paths or other forms (N5)?
- Do any of the ambiguous inputs in N2 occur?
- Is a glob on a topic needed (N3)?
- What should hold the plan: a ticket, or a file outside `.sdlc/` (N1, N9, N15)?
- Is apply worth building, or is a reviewed plan that a person carries out by hand enough?

The answer unblocks a later ticket for apply, or a decision to drop it.

## Constraints
Timebox: one working session. No production code lands from a spike. The prototype stays outside the plugin's shipped folders. Nothing in this repository is moved or rewritten. No ticket is created by the prototype.

## Recommendation
Evidence is the spike output in `spike/`: `plan.json` and `plan.txt` from `reorg_plan.py` run on base `9d6ca64` with the trial `spike/layout.md`, and the person's review in `review.md`. Rule names below refer to `docs/planning/repo-onboarding/reorganization.md` v0.6.

Counts: placed 12, misplaced 4, unplaced 0
Of the 4 moves, `review.md` judged 2 `ok` (50%): `docs/references/codex-role-execution.md` and `docs/references/plugin-compatibility.md` (`review.md` lines 11-12). It marked `docs/other/claude-handoff.md` and `docs/other/claude-response.md` `wrong`, because both are dated correspondence that a person would freeze in place (`review.md` lines 9-10, 20). The counts come from `len(placed)`, `len(moves)` and `len(unplaced)` in `plan.json` (lines 52-65, 30-51, 179), and match `summary` (`plan.json` lines 166-178, `plan.txt` lines 5-19). The 12 placed files are right (`review.md` line 21).

N1: Occurred in practice. The first review of the first plan found 2 of 4 moves wrong (`review.md` lines 9-10), and the fix a person gives is to freeze both files in the layout and plan again. So planning again is the normal path, not an edge case. The spike also regenerated the plan with probe layouts (`review.md` line 24). A plan held in a ticket made through `tickets.py new` would then need a second ticket or a refusal on every plan after the first. The plan should be held in a file outside `.sdlc/`: each run of plan overwrites it, so no ticket has to be found, reset, or left approved for a plan nobody reviewed. The work that asks for the reorganization keeps its own ticket and cites the plan file.

N2: Did not occur. `ambiguities` is `[]` in `plan.json` (line 2), `summary.ambiguous` is 0 (`plan.json` line 167), and `plan.txt` lists none (lines 53-55). The detection works: a probe layout gave `multi_home` and `into_frozen`, and a simulated path gave a case-folded `name_collision` (`review.md` line 24). The two-sources-one-destination case was not exercised, because no two documents under `docs/` share a file name (`review.md` line 24). The probe also showed a broad glob such as `claude-*.md` pulling the placed file `docs/references/claude-hooks.md` (`review.md` line 24).

N3: No topic needed a glob. `unplaced` is empty (`plan.json` line 179), every loose document matched a home line (`review.md` line 16), and the 7 files in `docs/specs/generative-constructs/` and the 3 in `docs/specs/repo-onboarding/` are placed with no glob pulling them out (`plan.json` lines 53-64, `review.md` line 21). The topic-glob form is not needed for this repository and should stay unspecified until a repository needs it.

N5: Occurred. `cite_forms` in `plan.json` (lines 15-26) counts 12 `markdown_link` and 6 `backtick_path` cites of moved documents in files that are not frozen, 0 for `reference_link`, `autolink`, `html_link`, `anchor`, `code_fence`, `non_markdown` and `other`, and 25 mentions in frozen files. A third of the cites a person reads as cites (6 of 18) are invisible to a link rewriter; they are listed in `unrewritten_cites` (`plan.json` lines 180-217, `plan.txt` lines 89-98). None of the 6 should be rewritten: 4 are on `docs/planning/repo-onboarding/reorganization.md` line 142, which describes where the files sit today, and 2 are in the correspondence that should be frozen (`review.md` line 22). Every inline Markdown link was handled by the 14 entries in `rewrites` (`plan.json` lines 66-165).

N9: Would occur if the plan were a ticket. The spike held its plan in two files, `spike/plan.json` and `spike/plan.txt`, not in a ticket, and the person reviewed it from `plan.json` (`review.md` line 3); that was enough for the full review. A plan file outside `.sdlc/` needs no `tickets.py new`, so it cannot rewrite `.sdlc/roadmap.md`, write `.sdlc/config`, or fail on an unrelated ticket's problem, and approval needs no status field that no command sets.

N15: Real as designed. `plan.json` has no `version` or `digest` field (keys at `plan.json` lines 2-217), so nothing in the spike binds the reviewed tables to the file that would be applied. `plan.txt` is generated from the same run as `plan.json` (`plan.txt` line 3), and the person reviewed `plan.json` itself (`review.md` line 3). Since the plan is always generated from `docs/layout.md` and the tree, the file should hold the plan and anything that consumes it should generate the plan again and refuse on any difference. A hand edit to the plan file then cannot be applied.

### Rules to keep
- Decisions, "Classification: globs in `docs/layout.md`": the home lines moved every loose file and left all 12 placed files alone (`review.md` lines 16, 21). Each move names the home line that matched (`plan.json` `moves[].rule`, lines 33-49).
- Decisions, "User decisions: recorded by editing `docs/layout.md`, then planning again": both wrong moves are fixed by listing the files as frozen and planning again (`review.md` lines 9-10).
- Inventory, the placed, misplaced and unplaced definitions: they produced 12, 4 and 0 with no wrong placement of a placed file (`plan.json` `summary`, `review.md` line 21).
- Frozen material, "A frozen record may cite a path that has since moved. That is accepted.": 25 mentions sit in frozen files, almost all under `.sdlc/`, and stay as they are (`plan.json` `cite_forms.in_frozen_files`, `review.md` line 22).
- Decisions, "Broken links: compared with a baseline": `baseline_broken` holds exactly the 2 expected sibling-project links (`plan.json` lines 3-14, `review.md` line 23).
- Decisions, "Link rewriting: a new rewriter in the script", including links inside each moved file (Apply step 3): the 14 `rewrites` keep every inline link cite of the two accepted moves valid (`plan.json` lines 66-165, `review.md` lines 11-12).
- Plan, `baseline_broken` and `rule` on each move as plan fields: the review used both to judge the moves and the broken links (`plan.json` lines 3-14 and 33-49, `review.md` lines 9-12, 23).

### Rules to change
- Frozen material, frozen candidates (a `YYYY-MM-DD` name or a `Recorded:` line in the first ten lines): it found none (`plan.json` `frozen_candidates`, line 27) and missed both records, one with `Date:` instead of `Recorded:` and one with no date line (`review.md` line 20). Widen the date-line test to `Date:`, and state that the person's review of each move is the classifier of last resort for records, because no glob or date test sees correspondence (`review.md` line 20).
- Open finding N5, "Link" undefined: define a link as an inline Markdown link, the only form found (`plan.json` `cite_forms`). Report every other cite form in the plan, as `unrewritten_cites` does, and never rewrite it (`review.md` line 22).
- Plan, `plan.json` fields: add `placed`, `ambiguities`, `unrewritten_cites`, and `form` on each rewrite. The review relied on them (`review.md` lines 16, 21, 22, 24), and the field table in the design has none of them.
- Plan, "`onboard plan` ... creates one ticket through `tickets.py new` and writes `plan.json` into that ticket's folder": write the plan to a file outside `.sdlc/` that each run overwrites (N1, N9 above).
- Plan, "The ticket's Context section holds the same content as tables ... When the two disagree, `plan.json` decides": generate the tables from the plan file, and have any consumer generate the plan again and refuse on a difference (N15 above).
- Approve, "The user approves by setting the ticket's status to `ready`": drop the ticket status as the approval record, since there is no plan ticket (N1, N9 above).
- Apply, Refusals: add the three ambiguity cases as plan output that blocks a move, which is how the spike holds them (`review.md` line 24).

Apply verdict: defer
A reviewed plan carried out by hand is enough here. After the person's fix (freeze the two records), the plan is 2 moves and 13 line edits, each with an exact old and new value in `plan.json` (lines 66-165, less the `docs/other/claude-handoff.md` line 5 rewrite); that is a few minutes of `git mv` and edits, and running plan again afterwards checks the result against `baseline_broken`. The hard part of this trial was judgement that apply could not automate: 2 of 4 moves were wrong for a reason no glob sees (`review.md` line 20). Apply would still need refusals, locking and restore (N8) specified and tested for a job this small. Revisit apply when a repository's reviewed plan is too large to carry out by hand.
