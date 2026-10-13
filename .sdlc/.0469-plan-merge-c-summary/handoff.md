---
id: T-0469
title: "Merge plan skills C: plan_check --summary cost line and controlled-language rules"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0468]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`plan_check.py` can print a `--summary` cost line, and plan artifacts follow the controlled-language rules of T-0461, so `/plan` stops computing cost by instruction.

## Intent
- Do: ticket C of the design: `plan_check.py` `--summary` (the cost line from `budget.py` TIERS) with the controlled-language rules for plan artifacts (closed lead verbs in `Do`, declarative Outcome and Goal lines, RFC 2119 words in Authorization) each with an observed-red control; update `skills/plan/references/goal.md` example, `plan-rules.md` and the `cost:` sentence in `skills/plan/SKILL.md` to use the flag; the campaign template and worked example reworded if they fail the verb rule; the five-ask replay recorded.
- Non-goals: any change to `check.py` (C stays out of it so T-0463 can run in parallel).
- Done when: `plan_check.py selftest` with one observed-red control per rule, the item 49 phrase set, `prompt_lint.py`, `check.sh` exit 0; the replay is recorded in the ticket notes.

## Context
Approved design: `.sdlc/.0462-plan-skills-merge-design/architect-L1.md` (read all of it: Approach, Interfaces with the overlap table and the dry-run shape, Constraints, Rejected alternatives, Risks, Carry forward). Maintainer decision 2026-10-12: file A to C, and put the `compaction` kind (T-0465) after A so `skills/plan/SKILL.md` has one writer at a time. Hot files one writer at a time: `plan_check.py`, `check.py`, `core.md`. If the merged `SKILL.md` passes 130 lines, stop and report: the design lists "keep seven skills" as the first alternative to reconsider.

## Constraints
No model or effort change. Old skills stay working until B. The skill stays self-contained (`check.py` item 42). Controlled language per T-0461 for plan artifacts. State only what a file or command shows; the replay is unverified if it was not an independent run.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/plan_check.py selftest` exits 0: it carries a `language:` control per rule (`hedge`, `verb`, `rfc2119`) on goal, campaign and plan, and a `cost:` control for a sized ticket, an unsized one, a level with no TIERS row, a missing cap, a sum over the cap and a block with no ticket.
2. `python3 plugins/sdlc-lite/scripts/plan_check.py goal --summary --root /nonexistent --text x | grep -q '^cost: unknown of unknown (0 tickets)'` exits 0: the flag exists and prints the line (before the change the flag was an argparse error).
3. `python3 -c "import sys; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import plan_check as p; g=p.GOOD_GOAL; w=lambda t:[r for r,_ in p.check_goal(t)[1]]; sys.exit(0 if 'hedge' in w(g.replace('/goal Overnight: ship','/goal Overnight: probably ship')) and 'verb' in w(g.replace('How to work: run','How to work: lane first, run')) and 'rfc2119' in w(g.replace('The run MUST NOT publish, push or tag.','Publish is not implied.')) and not w(g) else 1)"` exits 0: each rule warns on its own mutant and the good goal warns on none.
4. `python3 -c "import re,subprocess,sys; t=open('plugins/sdlc-lite/skills/plan/references/goal.md').read().split('## Example block')[1]; b=re.search(chr(96)*3+r'\n(.*?)'+chr(96)*3, t, re.S).group(1).replace('\${CLAUDE_PLUGIN_ROOT}','plugins/sdlc-lite'); r=subprocess.run([sys.executable,'plugins/sdlc-lite/scripts/plan_check.py','goal'],input=b,capture_output=True,text=True); sys.exit(0 if r.stdout.strip()=='ok: goal plan passes' else 1)"` exits 0: the `goal.md` example passes with no warning.
5. `grep -q -- '--summary' plugins/sdlc-lite/skills/plan/SKILL.md && grep -q -- '--summary' plugins/sdlc-lite/skills/plan/references/plan-rules.md` exits 0, and `test -z "$(git diff --name-only -- plugins/sdlc-lite/scripts/check.py)"` exits 0: the skill and the rules use the flag and `check.py` is untouched.
6. `python3 plugins/sdlc-lite/scripts/prompt_lint.py` exits 0.
7. `python3 plugins/sdlc-lite/scripts/check.py` exits 0 (the item 49 phrase set among it).
8. `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
verifier: L3

## Notes

Five-ask replay (2026-10-12, T-0469). Not an independent model run: one session ran the lint half only, so every count that needs a model is `[U]`. Design asks and what was run:
1. goal for T-0455 and T-0456: the `GOOD_GOAL` block with those ids through `plan_check.py goal --summary`: `ok: goal plan passes`, `cost: unknown of $60 (2 tickets: T-0455 unknown, T-0456 unknown)`. Both tickets are closed folders (`.NNNN-`), which `load_tickets` does not read, so the cost is unknown, not 0.
2. fanout for T-0459 and T-0381: `plan_check.py fanout --summary` exits 1 with `unknown-ticket` for both (closed folders), `cost: unknown of unknown (2 tickets: ...)`. The lint and the summary agree that the tickets are not open work.
3. doc: `GOOD_PLAN` through `plan_check.py plan --summary`: passes with the existing `kpi-drift` warning only, no `hedge`, `verb` or `rfc2119`; `cost: unknown of $60 (2 tickets: T-0413 unknown, T-0414 unknown)` (closed folders).
4. campaign for every page: `GOOD_CAMPAIGN` through `plan_check.py campaign --summary`: passes, `machine-load` warning only; `cost: unknown of $900 (0 tickets)` (a campaign names lanes, not tickets).
5. a `/clarify` handoff with `## Outcome` as the argument to doc: not run `[U]`.
First-return lint count: 4 of 4 blocks run pass their lint with the reworded examples; the model half (does a fresh `/plan` session write a passing block, and the number of questions asked) is `[U]` and needs an independent run. Promotion of `hedge`, `verb` and `rfc2119` from warning to FAIL waits for that run.


## Closed

2026-10-12: delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: The `block-stray-worktree.sh` hook denied `git worktree add --detach` under the brief's tmp prefix (the hook sees SDLC_ROLE=solo with SDLC_TMP_WORKTREES unset), so every base-sha control ran on a `git archive` or `git show` extraction of the base files under /tmp/0469-base, never on a worktree; `git worktree list` shows no 0469-verifier entry and the working tree is unchanged. The extraction (/tmp/0469-base and /tmp/0469-base-goal.md) is still in place because the permission system denied `rm -rf`; it is outside the repository. | plugins/sdlc-lite/skills/plan/references/goal.md:46 describes `rfc2119` as firing only when Authorization has no `MUST` line; `lang_warn` in plan_check.py also fires on a lower-case must, shall or should inside Authorization. | docs/reports/plan-skills-live-run.d/goal.txt:15 and docs/reports/2026-10-12-plan-merge-replay.md:57 keep the old `not implied` Authorization form; dated reports are history per AGENTS.md, not shipped guidance, so no change is owed. | Steelman record: draft finding "the campaign template was not reworded as the Do says"; rebuttal: the Do conditions rewording on failing the verb rule and the template has no verb-led line (campaign.md:31-54); dropped. No fail reason remained to file.
