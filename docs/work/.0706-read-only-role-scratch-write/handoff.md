---
id: T-0706
title: "Read-only roles may write in their brief's scratch dir"
type: bug             # feature | bug | chore | spike | idea
status: done        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
claimed_by: sdlc-lite-author 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A read-only role can Write files under the scratch dir its brief names, and every other Write it attempts stays blocked.

## Intent
- Do: in `plugins/sdlc-lite/hooks/block-role-write.sh`, also allow a read-only role's Write when `file_path` resolves inside this repo's scratch root (the parent of the brief's `Scratch files ... only under <dir>` path, from `wtroot.py` `scratch_root`, `plugins/sdlc-lite/scripts/wtroot.py`). Edit and NotebookEdit stay denied. Add hook selftest cases to `plugins/sdlc-lite/scripts/hook-selftest.sh`. Update the hook's header comment and `docs/references/claude-hooks.md` where it states what a read-only role may write.
- Non-goals: granting Edit, changing writer roles, changing brief text.
- Done when: the criteria pass.

## Repro
1. Prepare any read-only role brief (`dispatch.py prepare planner L2 <handoff>`): it says `Scratch files that are not worktrees (probe files, mutated copies) only under <scratch dir>` (`dispatch.py:1312`).
2. As that role, Write `<scratch dir>/probe.md`.

## Expected
The write succeeds: the brief offered that dir.

## Actual
agent-ui T-0393 planner, 2026-10-21 20:28, plugin 0.30.0 (`~/.claude/projects/-Users-kimgranlund-Projects-nonoun-agent-ui/a8ce3b21-c0a4-4e5f-b099-1796666e5f7f/subagents/agent-a0393-planner-L3-cfc2678acfd8194b.jsonl`):
"Blocked for sdlc role 'planner': '/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/agent-ui-7439b17c/0393-planner-L3/planner-L3.md' is not the result path of a dispatch for this role."

## Context
`block-role-write.sh` allows only the dispatch result path. The brief line comes from `dispatch.py:1312`, the dir from `wtroot.scratch_dir`. Path matching must resolve `..` and symlinks (`/var` vs `/private/var` on macOS) so a path like `<scratch>/../../x` stays blocked.

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exits 0 and has cases: a planner Write inside the scratch root passes; Writes outside it, a `..` escape out of it, and an Edit inside it stay blocked.
2. Negative control: with the hook change reverted, the new "Write inside the scratch root passes" case fails.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- `block-role-write.sh` now lets a read-only role Write any file whose canonical real path (`os.path.realpath`, so `/var` equals `/private/var`, `..` and symlinks resolved) is strictly inside `wtroot.scratch_root(<hook cwd>)`; the root comes from `wtroot.py` via python3. Edit, NotebookEdit and every other Write stay denied; the result-path rule is unchanged. Header comment, block message and `docs/references/claude-hooks.md` updated.
- `hook-selftest.sh` gained scratch-root cases: allowed (planner `.md`, `.txt`, verifier nested `.py`, `/private/var` spelling); denied (outside, `<root>/<dir>/../../probe.md`, `..` into a sibling dir, symlink out, the root itself, a `-sibling` prefix dir, a relative path, Edit, NotebookEdit); builder unrestricted.
- Negative control: with the hook reverted to HEAD, `hook-selftest.sh` fails: "block-role-write allows sdlc-lite:planner-L2 Write inside the scratch root '.../scratch-tmp/sdlc-lite/sdlc-lite-0a5e021b/0001-planner-L2/probe.md': exit 2, want 0". Hook restored; selftest PASS.
- Checks: `hook-selftest.sh` PASS (via gate_lock), `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check dd9b93e0` exit 0.

## Outcome

2026-10-21 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: dd9b93e094da
- Changed: see commits
- Commits: 3614ffd T-0706: read-only roles may Write under the scratch root
- Check: 1 `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exits 0 and has cases: a planner Write inside t...: pass
- Check: 2 Negative control: with the hook change reverted, the new "Write inside the scratch root passes" c...: pass
- Check: 3 `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes...: pass
- Follow-up: note: plugins/sdlc-lite/hooks/block-role-write.sh:34-43: I ran... -> notes.md
- Follow-up: note: plugins/sdlc-lite/hooks/block-role-write.sh:36: the hook fails closed -> notes.md
- Follow-up: note: plugins/sdlc-lite/hooks/block-role-write.sh:33: the root is keyed... -> notes.md
- Follow-up: note: plugins/sdlc-lite/hooks/block-role-write.sh:41: a self-looping... -> notes.md
- Follow-up: note: cleanup of my probe files was refused by the permission system -> notes.md
- Follow-up: note: redck.py deviations printed no process deviation: lines for this... -> notes.md
