---
id: T-0121
title: "Pattern-kill hook does not catch a kill word assigned through a..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0111
---

## Goal
Inside a role run, `plugins/sdlc-lite/hooks/block-pattern-kill.sh` blocks a kill word assigned to a variable through a command substitution and then expanded as a command (`p=$(command -v pkill); $p x`, `k=$(which killall); ${k} node`, backtick forms too), while `cmd=$(command -v ls); $cmd -la` and quoted mentions still pass.

## Context
Follow-up from T-0111 (pattern-kill-hook-misses-forms/filer-L1.md):

Pattern-kill hook does not catch a kill word assigned through a substitution (`p=$(command -v pkill); $p x`), so it still passes inside role runs.

## Constraints
Every existing fixture in `plugins/sdlc-lite/scripts/hook-selftest.sh` keeps its result; new pass and block fixtures cover the substitution forms. The hook header comment and the `block-pattern-kill.sh` Layout entry in the repo-root CLAUDE.md and `.claude/agents/sdlc-lite-author.md` (if it describes the hook forms) stay accurate. `scripts/check.sh` stays green.

## Acceptance (done when)
`bash plugins/sdlc-lite/scripts/hook-selftest.sh` passes with the new fixtures, and `plugins/sdlc-lite/scripts/check.sh` exits 0.

## Plan review

steps.py split refused planner-L1.md:
```
  bash: -c: line 0: unexpected EOF while looking for matching `"'
  bash: -c: line 1: syntax error: unexpected end of file
plan defect: replan this step (/chain 3)
steps: .sdlc/0121-pattern-kill-hook-does-not/planner-L1.md step 1: acceptance criterion command does not parse: pk=$(printf 'p%s' kill); json="$(python3 -c 'import json,sys;print(json.dumps({"tool_input":{"command":sys.argv[1]}}))' "p=\
```
Cause: criteria 2 and 6 put a literal backtick inside a markdown code span, so the span ends early. Build backtick forms without a literal backtick in the criterion (for example bt=$(printf '\140')), or check them through fixtures in hook-selftest.sh.
