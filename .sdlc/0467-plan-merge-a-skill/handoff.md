---
id: T-0467
title: "Merge plan skills A: new /plan skill with kinds steps, doc, goal, campaign, fanout"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
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
