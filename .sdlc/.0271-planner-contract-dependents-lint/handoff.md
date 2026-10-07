---
id: T-0271
title: "steps.py lint should enforce plan-defect contract dependents"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
steps.py lint refuses a plan that omits a path a verifier `plan defect:` line named.

## Context
Source: maison `.0130` report, draft 3. T-0105 step 3 failed on `scripts/gen-ui-harness/dependencies.json`, which step 1's verifier had already flagged. planner.md "Contract dependents" is advisory only.
Fix: in `lint_steps`, read `step-*/verifier-*.md` and `step-*/builder-*.md` beside the plan, take path tokens from lines starting `plan defect:`, add one finding per token named in no `## Step` block. split inherits it through `lint_or_fail`. Existing selftest fixtures with `plan defect:` lines must name the path or hold no token.

## Constraints
No push, tag, version bump, or publish. No em dashes.

## Acceptance criteria
- `steps.py lint` and `split` refuse a plan that names in no `## Step` block a path an earlier `step-*/verifier-*.md` or `step-*/builder-*.md` flagged on a line starting `plan defect:`, one finding per path, ending with the plan defect last line: `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -q '^ok: (s) lint refuses a plan that omits a bare path'`
- A plan whose step names the flagged path lints clean and splits; a `plan defect:` line holding no path token (`c2 contradicts c1`, `and/or`, a url, a path outside the repo) adds no finding: `python3 plugins/sdlc-lite/scripts/steps.py selftest | grep -q '^ok: (s) lint accepts a plan whose step names the flagged path'`
- The whole steps selftest passes, existing swap and widen cases included: `python3 plugins/sdlc-lite/scripts/steps.py selftest | tail -1`
- The new gate has an observed negative control: with `defect_dependents` stubbed to return no findings, the `(s)` refusal cases fail while the positive cases still pass (run `steps.selftest()` from a module load that stubs it).
- The Codex agent definitions match `planner.md`: `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- Role and skill contracts hold: `python3 plugins/sdlc-lite/scripts/check.py`
- Full regression suite is green: `bash plugins/sdlc-lite/scripts/check.sh`
- Whitespace is clean and the diff adds no em dash: `git diff --check`
- Scope: `git diff --name-only` lists only `docs/maintenance/sdlc-internals.md`, `plugins/sdlc-lite/agents/planner.md`, the three `plugins/sdlc-lite/adapters/codex/agents/sdlc-planner-l*.toml` files, and `plugins/sdlc-lite/scripts/steps.py`, besides this ticket folder.

## Closed

2026-10-06: delivered by the solo agent (tier M); one independent batched verifier passed before the merge
