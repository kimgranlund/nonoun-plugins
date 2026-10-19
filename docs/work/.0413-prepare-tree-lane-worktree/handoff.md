---
id: T-0413
title: "prepare --tree names the lane worktree as Tree and base"
type: bug             # feature | bug | chore | spike | idea
status: done
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0412]
created: 2026-10-09
claimed_by: claude 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
prepare --tree names the lane worktree as Tree and base. Serves goal G-002 (docs/goals/002-restart-and-blocked-run-cost.md); spec: docs/specs/sdlc-lite/restart-and-blocked-run-plan.md; plan step 3 in .sdlc/plan-reliability-docs/plan.md.

## Intent
Ticket: bug, size L3, candidate 3 of the spec (section 3). Depends on: step 2 (same file, same lane). L3 because it touches the base order T-0381 and T-0376 settled.

In `plugins/sdlc-lite/scripts/dispatch.py`: add `prepare --tree PATH` to the parser (`dispatch.py:1105-1116`) and a `tree=''` parameter to `prepare` (`dispatch.py:542`). PATH must resolve (by `os.path.realpath`) to a path in `worktrees(<handoff's toplevel>)` (`dispatch.py:517-529`), else raise `Refuse(2, 'dispatch.py: --tree %s is not a worktree of this repository' % PATH)` before the lock, so no record is written. Settle the execution tree once: PATH when given, else `exec_tree(directory)` (`dispatch.py:306-320`). Use that tree's toplevel for `toplevel` (today the handoff's own toplevel, `dispatch.py:652`), so the Tree line, the `tree` key, the tmp prefix (`dispatch.py:653`) and the `worktrees_before` and `branches_before` snapshot follow it; and give `build_base` (`dispatch.py:340-389`) an optional `tree` argument used as its `cwd` in place of its own `exec_tree(directory)` call, so the Base sha comes from the same tree. With no `--tree`, the only behavior change is that a main-checkout handoff dispatched from inside a linked lane worktree gets the lane as Tree, matching the Base sha it already gets. The flag name matches `steps.py split --tree`.

In `plugins/sdlc-lite/agents/conductor.md`, at the dispatch step, add one sentence: when a build runs in a lane worktree while its handoff lives in the primary checkout, run `prepare --tree <lane worktree>`. Then run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` to refresh `plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml`. `docs/references/sdlc-internals.md`: add `--tree` where it lists the prepare flags, if it does.

Contract dependents: the selftest case "a verifier prompt for a lane worktree handoff carries the worktree as Tree, not the cwd tree" (`dispatch.py:1611-1613`) must still pass unchanged; `record` reads `d['tree']` for `remove_tmp` and `strays` (`dispatch.py:880`) and `deliver` reads it (`dispatch.py:1045`), both consistent as long as `tree` and `tmp_prefix` come from the same execution tree; `redck.py` is left alone (it follows the base `prepare` hands it). Add selftest cases with exactly these labels: `prepare --tree: Tree, Base sha and the tmp prefix name the given lane worktree`, `prepare --tree: a path that is not a worktree of this repository is refused, exit 2`, `prepare from a lane worktree for a main-checkout handoff: Tree names the lane, as Base sha does`. Write each label as one string literal on one line, so the (red) source grep finds it. Validation scope: `dispatch.py selftest`, `codex_roles.py generate --check`.

## Read first
- `plugins/sdlc-lite/AGENTS.md`
- `docs/references/AGENTS.md`

## Done when
- (red) `grep -qF 'prepare --tree: Tree, Base sha and the tmp prefix name the given lane worktree' plugins/sdlc-lite/scripts/dispatch.py`
- `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && for l in 'prepare --tree: Tree, Base sha and the tmp prefix name the given lane worktree' 'prepare --tree: a path that is not a worktree of this repository is refused, exit 2' 'prepare from a lane worktree for a main-checkout handoff: Tree names the lane, as Base sha does'; do printf '%s\n' "$out" | grep -qxF "ok: $l" || exit 1; done`
- (red) `python3 plugins/sdlc-lite/scripts/dispatch.py prepare --help | grep -qF -- '--tree'`
- (red) `grep -qF 'prepare --tree' plugins/sdlc-lite/agents/conductor.md`
- (guard) `out=$(python3 plugins/sdlc-lite/scripts/dispatch.py selftest 2>&1) && printf '%s\n' "$out" | grep -qxF 'ok: a verifier prompt for a lane worktree handoff carries the worktree as Tree, not the cwd tree'`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vxF -e plugins/sdlc-lite/scripts/dispatch.py -e plugins/sdlc-lite/agents/conductor.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml -e docs/references/sdlc-internals.md)"`

## Acceptance criteria
verifier: L3

- [ ] `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0 and prints, each as its own line, the exact labels `ok: prepare --tree: Tree, Base sha and the tmp prefix name the given lane worktree`, `ok: prepare --tree: a path that is not a worktree of this repository is refused, exit 2`, and `ok: prepare from a lane worktree for a main-checkout handoff: Tree names the lane, as Base sha does`; each label is one string literal on one line of `plugins/sdlc-lite/scripts/dispatch.py`.
- [ ] The existing case `ok: a verifier prompt for a lane worktree handoff carries the worktree as Tree, not the cwd tree` still prints, unchanged.
- [ ] `python3 plugins/sdlc-lite/scripts/dispatch.py prepare --help` lists `--tree`; `prepare(..., tree='')` refuses a PATH whose `os.path.realpath` is not a path in `worktrees(<handoff's toplevel>)` with exit 2 and the message `dispatch.py: --tree PATH is not a worktree of this repository`, before the lock, so no file is written in the handoff dir.
- [ ] The execution tree is settled once (PATH when given, else `exec_tree(directory)`): the `Tree:` line, the `tree` key, `tmp_prefix`, `worktrees_before` and `branches_before` use its toplevel, and `build_base(directory, tree)` uses it as its git `cwd`, so the Base sha comes from the same tree. With no `--tree`, only a main-checkout handoff dispatched from inside a linked lane worktree changes (Tree becomes the lane).
- [ ] `plugins/sdlc-lite/agents/conductor.md` step 1 (Prepare) carries one sentence with `prepare --tree <lane worktree>` for a build run in a lane worktree whose handoff lives in the primary checkout, and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exits 0.
- [ ] `docs/references/sdlc-internals.md` lists `[--tree PATH]` in the prepare usage.
- [ ] Outside `.sdlc/`, the diff against the base sha touches only `plugins/sdlc-lite/scripts/dispatch.py`, `plugins/sdlc-lite/agents/conductor.md`, `plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml`, and `docs/references/sdlc-internals.md`; no em or en dashes are added.

## Context
Planner L3 output for the 2026-10-09 retros. KPIs: K-002 restart recovery minutes, K-003 blocked builders per wave, K-004 unsatisfiable criteria caught. The spec marks which candidates may already be fixed or need diagnosis first; follow it.

## Constraints
No em or en dashes. No push or publish. The plan step is the contract: if it is wrong or silent, stop and report a plan defect instead of improvising.

## Closed

2026-10-10: delivered by the solo agent (level L3); verified by the lane verifier
