---
id: T-0093
title: "Check the steps.py || lint allowance against the merge guards peers..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0082
---

## Goal
The `steps.py` `||` lint refuses only real fallbacks (a criterion that passes when either side passes) and stops refusing the fail-fast `||` forms that peer repos' plans actually use, so a valid plan is never sent to a replan as a plan defect.

## Intent
Literal ask: check the `steps.py` `||` lint allowance against the merge guards peers actually use; it only exempts `test $# -eq 0 ||`, so a peer using a different empty-argument short circuit gets its valid plan refused.
Evidence (conductor grep, 2026-09-26, `planner-*.md` and `step-*/handoff.md` under the `.sdlc/` of gen-ui-system, gen-ui-system-svelte, gen-ui-system-svelte-lite, sdlc-single-agent-drill, ultimate-tokens, sdlc-orchestration, codex-explorations-sdlc): no peer criterion uses `test $# -eq 0 ||` or any other empty-argument short circuit, and no peer merge guard uses `||`. Peers do use fail-fast forms that the current lint refuses, for example `for f in a b; do test -f "$f" || exit 1; done` and `for id in P1 P2; do grep -qE "..." "$f" || { echo "missing $id"; exit 1; }; done`. They also use `|| echo MISSING $p` inside loops, which always exits 0 and is a vacuous criterion.
Deltas:
- The premise names merge guards; the real false positives are fail-fast loop checks: defaulted: widen the allowance to fail-fast forms, not to other empty-argument short circuits nobody uses.
- Which right-hand sides count as fail-fast: defaulted: `exit N` with N a nonzero integer literal, and a brace group `{ ...; exit N; }` whose last command is such an exit. `|| false` and `|| return N` are out unless the planner finds a reason.
- `|| echo ...` (no exit): defaulted: stays refused; it cannot fail the criterion.
- The existing `test $# -eq 0 ||` exemption: defaulted: keep it (backward compatible).
Do: change the `||` rule in `plugins/sdlc-lite/scripts/steps.py` (`or_fallback` and its docstrings) so an unquoted `||` whose right operand is a nonzero `exit` (bare or as the last command of a `{ ...; }` group) passes, keep refusing every other unquoted `||` except the `test $# -eq 0` short circuit, extend the `(k2)` selftest with positive and negative controls (the two peer forms above pass; `|| echo MISSING x`, `|| exit 0`, `|| true`, and `grep a x || grep b x` stay refused), and update every record that states the rule (at least `agents/planner.md`, repo `CLAUDE.md`, `.claude/agents/sdlc-lite-author.md`, and any skill or check.py text that quotes it).
Non-goals: editing peer repos; changing the sha pin or count lints; changing the merge-step template.
Done when: `python3 plugins/sdlc-lite/scripts/steps.py selftest` and `plugins/sdlc-lite/scripts/check.sh` pass, `steps.py lint` accepts a plan whose criterion is `for f in a b; do test -f "$f" || exit 1; done` and still refuses one whose criterion is `grep -q a x || grep -q b x`, and no record still says `test $# -eq 0` is the only allowed `||` form.

## Context
Follow-up from T-0082 (criteria-or-fallback/filer-L1.md):

Check the `steps.py` `||` lint allowance against the merge guards peers actually use. It only exempts the exact form `test $# -eq 0 ||`, which was inferred from the ticket because this repo has no such form, so a peer using a different empty-argument short circuit would get its valid plan refused as a plan defect.

## Constraints
`scripts/check.sh` stays green. The lint still executes nothing and stays read-only. Every doc copy of the rule changes in the same change (stale context is a defect).
