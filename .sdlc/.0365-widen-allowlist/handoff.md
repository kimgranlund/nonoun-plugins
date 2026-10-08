---
id: T-0365
title: "steps.py widen accepts real scope growth without a hand-written diff-name-only criterion"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
steps.py widen can approve real scope growth without a plan that happened to include a diff-name-only allow-list criterion.

## Intent
- Do: In scripts/steps.py widen: accept an explicit file list given at widen time (with the reason recorded) as the allow-list, or have the planner template always emit the diff-name-only allow-list criterion; pick the smaller change and say why.
- Non-goals: model or effort changes; anything outside this finding.
- Done when:
  - A selftest: widen with an explicit file list succeeds and records the reason; widen with neither the list nor the criterion still refuses (observed failing first).
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

## Context
maison T-0227 step 2 (widen refused, forced a conductor scope decision plus a user round) and ultimate-tokens T-0017 step 13 (two replans for citation-only doc edits). Two repos. Source: docs/reports/2026-10-08-fleet-retro-06.md (fleet retro 2026-10-08, filed by the user's choice). outcome metric: widen refusals per run in the next retro, before: 2

## Constraints
No em or en dashes. No push or publish.

## Choice
Smaller change picked: `steps.py widen --reason "<why>"`. When a step has no scope criterion, the explicit path list plus the reason are recorded under `## Scope widened` as the allow-list instead of refusing. Changing the planner template would touch the generated agents and every future plan; this edits one command and keeps the refusal when neither list-with-reason nor a criterion is present.

## Acceptance criteria
- [ ] `python3 plugins/sdlc-lite/scripts/steps.py selftest | tail -1 | grep -q 'PASS'`
- [ ] `d=$(mktemp -d) && mkdir $d/s && printf '## Task goal\ng\n\n## Step 1: x\nlevel: L2\n### Do\nd\n### Acceptance criteria\n- `test -d .`\n' > $d/s/handoff.md && cd $d && git init -q . && ! python3 "$OLDPWD/plugins/sdlc-lite/scripts/steps.py" widen s b.txt 2>/dev/null && python3 "$OLDPWD/plugins/sdlc-lite/scripts/steps.py" widen s b.txt --reason why | grep -q 'no scope criterion' && grep -q 'steps.py widen): why' s/handoff.md`
- [ ] `python3 plugins/sdlc-lite/scripts/check.py && python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check && python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check && python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check`

## Closed

2026-10-08: delivered by the solo agent (level L2); one independent batched verifier passed before the merge
