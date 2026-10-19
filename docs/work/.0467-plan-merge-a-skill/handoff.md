---
id: T-0467
title: "Merge plan skills A: new /plan skill with kinds steps, doc, goal, campaign, fanout"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0461]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`/sdlc-lite:plan <kind> [args]` is one skill with kinds `steps` (default, today's `plan`), `doc`, `goal`, `campaign` and `fanout`, with the shared rules in one reference and a dry-run printed before every block.

## Intent
- Do: build ticket A of the design's build split: new `plugins/sdlc-lite/skills/plan/SKILL.md` (rewrites the 20-line file; router plus shared procedure, at most 90 lines and 7 KB), `references/plan-rules.md`, `references/steps.md`, `references/goal.md` (copy of `plan-goal/references/goal-rules.md`), `references/campaign.md`, `references/doc.md` (copy of `plan-doc-format.md`), `references/fanout.md`, `evals/README.md` with five ask pairs; add the `plan` kinds row to `skills/sdlc-lite/SKILL.md` and keep the old rows; one new `check.py` item pinning the new skill; leave the four old skills untouched. Kind resolution: the first argument token when it is one of the five, else `steps` when the rest names a `handoff.md`, else one `AskUserQuestion` with the five kinds (`steps` recommended; unattended, `steps`). Read a `/clarify` handoff first and fill slots from it. Dry run printed before every fenced block: lint, cost (computed by instruction from `budget.py` TIERS and `tickets.py check`, since `prompt_lint.py` P-2 rejects a flag a script lacks; C swaps to `--summary`), lanes from `fanout.py run --dry-run` (fanout and campaign), the control `plan_done.py exits 1, n steps open` (doc). Reserve the first word of each kind: a goal that starts with a kind name is written `goal <kind> ...` or quoted; state it in the skill. Description carries the trigger phrases of all five kinds.
- Non-goals: stubs and check retargets (B); `--summary` and the controlled-language lint (C); `compaction` (T-0465, after this ticket); removing old skills (D, a release later).
- Done when: `check.py`, `check-packaging.py`, `prompt_lint.py` on the new files, `plan_check.py selftest`, item 42 self-containment and `check.sh` exit 0; the five-ask replay (from the design: an overnight goal, a parallel fanout, a plan doc, a steps plan, a campaign) in a throwaway worktree for goal and fanout at least, recorded in the ticket notes with old-skill versus new-skill lint results.
- outcome metric: questions asked and `plan_check.py` refusals per plan artifact in the replay, new `/plan` versus the old skills, before: recorded by the replay

## Context
Approved design: `.sdlc/.0462-plan-skills-merge-design/architect-L1.md` (read all of it: Approach, Interfaces with the overlap table and the dry-run shape, Constraints, Rejected alternatives, Risks, Carry forward). Maintainer decision 2026-10-12: file A to C, and put the `compaction` kind (T-0465) after A so `skills/plan/SKILL.md` has one writer at a time. Hot files one writer at a time: `plan_check.py`, `check.py`, `core.md`. If the merged `SKILL.md` passes 130 lines, stop and report: the design lists "keep seven skills" as the first alternative to reconsider.

## Constraints
No model or effort change. Old skills stay working until B. The skill stays self-contained (`check.py` item 42). Controlled language per T-0461 for plan artifacts. State only what a file or command shows; the replay is unverified if it was not an independent run.

## Closed

2026-10-12: warnings acknowledged: all three steps verifier pass, no process deviations; the replay covers goal and fanout only and is not an independent run (the report says so); the external mutant of check.py item 57 was blocked by the stray-worktree hook, inline controls ran; the untracked-files note is superseded by the lane commit b33310a

> - All three steps passed their verifiers: step 1 at verifier L2, steps 2 and 3 at verifier L1. No `process-deviations.md` exists in the artifacts dir or the step folders, so there is no process deviation.
> - The handoff's done-when asks for a five-ask replay, with goal and fanout at a minimum. Only goal and fanout were replayed (steps 2 and 3). Steps, doc and campaign were not run, so their dry-run output and first-return lint results are unobserved.
> - The replay is unverified as an independent comparison of the two skills. In step 2 one builder wrote both the old and the new blocks. In step 3 one reader did both runs, and the builder says the new blocks match the old by construction. The step 3 builder also says the equal fanout refusal is not a second discovery. The report says "unverified: not an independent run".
> - The step 3 verifier checked the report's structure and did not re-run the four replays.
> - The step 1 verifier could not run an external mutant of the `check.py` item 57 gate. The stray-worktree hook blocked `git worktree add` because `SDLC_TMP_WORKTREES` was unset. Only the inline controls that run on every `check.py` run observed the gate rejecting a defect.
> - Nothing is committed. The new skill's `references/`, `evals/` and the replay report are untracked. `SKILL.md` names its six reference files as code-span paths instead of Markdown links, because `check.py` item 32 counts a link from a tracked file to an untracked one as broken.
