---
id: T-0561
title: "Bare-clone repos: worktree root falls back to the current lane's toplevel and nests again"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
claimed_by: claude 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
verifier: L3
---

## Goal
In a bare-clone repo (a bare git dir with lanes beside it and no main checkout the agents may use), every SDLC Lite worktree goes to one fixed root outside any lane, and `migrate-0.23.sh` reports the layout instead of finding nothing.

## Repro
1. A bare clone with lanes at `ui-kit/lanes/<lane>` (gen-ui-kit's layout) and the owner's checkout at `main/`, where conductors never run git.
2. From inside a lane, run `python3 <plugin>/scripts/wtroot.py` or open a role's tmp prefix through `dispatch.py prepare`.

## Expected
A root outside every lane: a `worktree_root:` line in `.sdlc/config` when set, else the bare repo's lanes dir (`<bare parent>/lanes` or the dir holding existing lanes).

## Actual
`wtroot.py` falls back to `--show-toplevel` for a bare or non-`.git` common dir (wtroot.py:16-17), which inside a lane is the lane itself, so role tmp trees nest under `<lane>/.claude/worktrees/` again. gen-ui-kit (0.23.0 installed, 2026-10-15): "this repo is a bare clone with lanes at ui-kit/lanes/ (no .worktrees/ under a main checkout) ... the script has nothing in scope here."

## Context
T-0550 made the main checkout the root; a bare clone has none the agents may write to. Fix with a `worktree_root:` config line plus a bare-clone default, and teach `migrate-0.23.sh` to print the chosen root and exit 0 with "nothing to move" for this layout.

## Constraints
The failing selftest (a bare-clone fixture with a lane, prefix outside the lane) lands with the fix. Target 0.23.1.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/wtroot.py selftest` exits 0, and its bare-clone cases (a bare clone with lanes at `<dir>/lanes/<lane>`: root and tmp prefix from a lane are `<dir>/lanes` and `<dir>/lanes/tmp`, outside the lane; a relative `worktree_root:` resolves against the bare parent; an absolute one wins in a normal repo, from a lane too) print `ok:`; they printed `FAIL:` before the fix.
2. `bash plugins/sdlc-lite/scripts/migrate-0.23.sh --selftest` exits 0, including its bare-clone cases: from a lane and from the bare dir it prints `bare clone: worktree root <dir>/lanes` and `nothing to move`, exits 0, and changes nothing (the 0.23.0 script exited 2 there).
3. `bash plugins/sdlc-lite/scripts/run-selftest.sh` exits 0, and `! (python3 plugins/sdlc-lite/scripts/dispatch.py selftest | grep '^FAIL' | grep -v 'accept-all validator')` exits 0 (dispatch prepare and run.sh take their prefix from `wtroot.py`; the three accept-all control FAILs fail on unchanged main too and are T-0558).
4. `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0 with its `bare root` case (a bare-clone lane's default lanes root is `<bare parent>/lanes` and `tmp_dirs` holds `<bare parent>/lanes/tmp`), which failed before the change; an explicit `lanes_root:` keeps its meaning.
5. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 with its `bare clone: --dry-run from a lane` case (the default lanes dir is `<bare parent>/lanes/fanout`), which failed before the change; `--lanes-dir` keeps its meaning.
6. reap-tmp-worktrees.sh run on a lane of a bare clone reaps a dead `<bare parent>/lanes/tmp/<role>-<pid>` prefix and its worktree (the 0.23.0 script left it).
7. `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exits 0, with its T-0561 fixtures (a bare-clone lane and a `worktree_root:` repo): a verifier sub-agent may add a detached worktree and rm under `<wtroot.py root>/tmp`, and is denied both under the old nested `<cwd>/.claude/worktrees/tmp`; they failed before the hook change.
8. `git diff --check` exits 0.
