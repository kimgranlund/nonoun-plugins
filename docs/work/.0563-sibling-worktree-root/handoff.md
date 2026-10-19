---
id: T-0563
title: "Worktree root moves to a sibling folder outside the repo"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every worktree SDLC Lite makes in a normal (non-bare) repo lives in a sibling folder outside the repo, `<main checkout parent>/<repo name>.worktrees/`, so no watcher, test runner, indexer or `.sdlc` scanner walks into lanes, on Claude Code and Codex alike.

## Intent
- Do:
  1. `plugins/sdlc-lite/scripts/wtroot.py`: the non-bare default root becomes `<main checkout parent>/<main checkout name>.worktrees` (lanes `<root>/<lane>`, fanout `<root>/fanout/<lane>`, role tmp `<root>/tmp/<agent>`). `.claude/worktrees` joins `.worktrees` as a legacy root that is still read for one release. The bare-clone default (`<bare parent>/lanes`) and the `worktree_root:` override keep their meaning.
  2. Every consumer of the root follows it: `lanes.py`, `fanout.py`, `dispatch.py prepare`, `run.sh`, `reap-tmp-worktrees.sh`, and the Claude hooks that allow or deny worktree adds and removals (`hooks/block-stray-worktree.sh` and the role hooks T-0561 touched). A worktree Claude Code makes for itself under `.claude/worktrees/` (Agent `isolation: worktree`, `claude --worktree`, EnterWorktree) is host-owned and stays allowed.
  3. A new `plugins/sdlc-lite/scripts/migrate-worktrees.sh` (dry run by default, `--apply`, `--selftest`), modeled on `migrate-0.23.sh`, moves each registered SDLC worktree under `.worktrees/` or `.claude/worktrees/` (except Claude-owned `agent-*` trees) to the same relative path under the sibling root with `git worktree move`, and keeps the same skip rules (locked, dirty, live owner, unlanded branch, destination exists). `migrate-0.23.sh` becomes a one-line wrapper that execs it.
- Non-goals: docs, AGENTS.md and onboarding text (T-0564); Codex's own `~/.codex/worktrees`; changing bare-clone behavior.
- Done when: the criteria below pass.

## Context
Maintainer decision 2026-10-15: lanes move out of the repo to a sibling folder so Claude Code and Codex are treated alike. Codex creates its own worktrees under `~/.codex/worktrees/<id>/<repo>`, which is not configurable, so neither host's convention fits both. A nested root makes every `.sdlc` walker and watcher see each lane. Example: `dispatch.py attempt_dirs()` skips only `.worktrees`, `.git` and `node_modules`. T-0550 (0.23.0) set the root to `.claude/worktrees`; T-0561 added bare clones and `worktree_root:`. Read the `wtroot.py` docstring first; it owns the root rule.

## Constraints
The `worktree_root:` override, the bare-clone default and the owner-marker sweep keep working. Lanes that are already open under `.claude/worktrees/` still land and close during the legacy release. No worktree is ever moved with `mv`.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/wtroot.py selftest` exits 0. Its new cases print `ok:` and printed `FAIL:` before the change: a normal repo's root is `<parent>/<name>.worktrees`, outside the main checkout; the same root comes back from inside a lane; and a lane under `.claude/worktrees` is read as legacy.
2. `python3 plugins/sdlc-lite/scripts/lanes.py selftest` and `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exit 0, and each default lanes dir is under the sibling root.
3. `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exits 0. A verifier sub-agent may add a detached worktree under `<wtroot.py root>/tmp` and is denied under `<repo>/.claude/worktrees/tmp`. A plain session may still add `.claude/worktrees/agent-x`.
4. `bash plugins/sdlc-lite/scripts/migrate-worktrees.sh --selftest` exits 0. It covers: moving from both legacy roots; skipping locked, dirty, unlanded and Claude-owned `agent-*` trees; and a second run that reports nothing to move.
5. `bash plugins/sdlc-lite/scripts/run-selftest.sh` exits 0.
6. `git diff --check` exits 0.

## Outcome

2026-10-15 · lane: full L3 · verdict: pass · verifier: verifier-L2 (sonnet) · base: cae6a6b05bf3
- Changed: worktree root is now the sibling <parent>/<repo>.worktrees; migrate-worktrees.sh moves legacy lanes
- Commits: efb7dac T-0563: worktree root moves to the sibling <parent>/<repo>.worktrees; migrate-worktrees.sh
- Check: 1 wtroot.py selftest: pass
- Check: 2 lanes.py and fanout.py selftests: pass
- Check: 3 hook-selftest.sh: pass
- Check: 4 migrate-worktrees.sh --selftest: pass
- Check: 5 run-selftest.sh: pass
- Check: 6 git diff --check: pass
- Follow-up: note: plugins/sdlc-lite/scripts/lanes.py:124 and fanout.py:33/:40/:492... -> notes.md
- Follow-up: note: I could not remove my scratch copies mut/, base/ under... -> notes.md
