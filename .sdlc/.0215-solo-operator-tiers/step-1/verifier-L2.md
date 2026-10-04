<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `test -f plugins/sdlc-lite/agents/solo.md`: pass. Evidence: rc=0. The file is 33 lines and I read it in full.
- `grep -q "Sonnet" … && grep -q "Opus" …`: pass. Evidence: rc=0. The tier table reads `Sonnet low`, `Sonnet xhigh`, `Opus xhigh`.
- models.json `solo` assert: pass. Evidence: python assert rc=0. The diff adds exactly one `solo` line and changes no existing row.
- Three `sdlc-solo-l1..l3.toml` files exist: pass. Evidence: rc=0.
- Lane size M gives `solo`: pass. Evidence: `steps.py lane` printed `solo` then `reason: size M decides before planning (no planner result yet)`. The diff shows the old code mapped M to `lean`, so this check goes red before the change.
- Lane size S gives `solo`: pass. Evidence: first line was `solo`. The old mapping gave `fix`.
- Lane size L gives `full`: pass. Evidence: first line was `full`.
- `grep -q "solo" plugins/sdlc-lite/agents/conductor.md`: pass. Evidence: rc=0. The diff adds one line at conductor.md:14.
- `steps.py selftest`: pass. Evidence: `steps selftest: PASS`. The diff shows the S/M table, the check name and `rec_m` were updated.
- `check.py plugins/sdlc-lite`: pass. Evidence: `ok: 19 role levels, 9 agents checked`, rc=0.
  - Negative control on a temp copy: changing `Opus xhigh` in solo.md printed `FAIL solo: agents/solo.md missing "Opus xhigh"`. Deleting `sdlc-solo-l2.toml` printed `FAIL solo: adapters/codex/agents/sdlc-solo-l2.toml missing`.
  - The check goes red on a defect and green on the real tree.
- `evals.py check`: pass. Evidence: `ok (2 evals, lock cites .sdlc/evals/0001-solo-tiers.md)`.
  - `.sdlc/evals/0001-solo-tiers.md` cites the T-0215 handoff and the orchestration doc as evidence.
  - The lock was updated. Only the `solo` entry was added to models.json, so no other default changed.
- `codex_roles.py generate --check`: pass. Evidence: `Codex agent definitions verified`.
- `check-packaging.py`: pass. Evidence: `PASS: catalog parity, identity, skill routes, hook isolation and context links`.
- `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: rc=0. Output includes `skip: shellcheck not installed` and `skip: evals lock guard`, both environment skips. The check.py and evals guards were run directly above.
- `git diff --check main -- plugins docs`: pass. Evidence: rc=0.
- Builder claim that the runner's family rule does not cover solo: accepted. Evidence: `run.sh` lines 116-118 give verifier L2 = sonnet and L3 = fable. solo.md therefore pairs Sonnet (tier M) with `verifier L3` (Fable) and Opus (tier L) with `verifier L2` (Sonnet), which are different families.

## Out of scope changes
- `.sdlc/evals/0001-solo-tiers.md` and `.sdlc/evals/table-lock.json` are required by Do item 5.
- `adapters/codex/agents/sdlc-conductor-l1.toml` is a regeneration forced by the conductor.md edit. `generate --check` passes.
- `.sdlc/0215-solo-operator-tiers/step-1/*` are run artifacts. The `.sdlc/.0186-*` and `.sdlc/.0196-*` files appear in `git diff main` but not in `git status`, so they are already committed on this branch and not part of this step.
- solo.md tells tiers M and L to write `## Acceptance criteria` when the handoff has none. The step did not ask for this. I checked it against the Do: it supports the verifier and breaks no criterion, so I judge it acceptable.
- `skills/chain/SKILL.md:27` still says the lane prints `fix`, `lean`, or `full`. The step did not call for editing it and the builder disclosed it. It is prose only, and nothing in the repo parses the lane word. It belongs to T-0199 or a follow-up.

## For the next attempt
None
