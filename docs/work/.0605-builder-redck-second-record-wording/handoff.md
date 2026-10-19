---
id: T-0605
title: "builder.md says a second redck record is only a base control, stale since T-0473"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-17
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`agents/builder.md` rule 11 describes `redck.py record` as T-0473 changed it, and the generated builder files match.

## Context
`plugins/sdlc-lite/agents/builder.md:28` still says a second `record` "is only a base control and is stored as retrospective". T-0473 changed `redck.py` to bind records to the working tree and an ancestor base, so that sentence is partly stale. T-0473 forbade prompt wording changes, so it was left. Source note: `.sdlc/notes.md` T-0473.

## Constraints
Read `plugins/sdlc-lite/scripts/redck.py` first and word the sentence from its current behavior. Edit `builder.md` only, then run `python3 plugins/sdlc-lite/scripts/claude_roles.py generate` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`. Model and effort defaults stay unchanged.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` and `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check` exit 0.
2. `grep -c 'only a base control' plugins/sdlc-lite/agents/builder.md` prints 0.

## Outcome

2026-10-17 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: plugins/sdlc-lite/agents/builder.md:28 the new sentence matches plugins/sdlc-lite/scripts/redck.py: dirty_paths (redck.py:122-135) diffs against HEAD plus untracked files with .sdlc/ and the handoff dir left out, cmd_record sets `phase = 'pre-edit' if dirty == [] else 'retrospective'` (redck.py:201), the docstring (redck.py:11-15) names the resumed-branch case, and the retrospective stderr reads "this is a base control, not a red-before-edit checkpoint" (redck.py:214). The sentence omits the declared `tests:` prelude exception (redck.py:138-149), which is a precision gap, not a contradiction. | note: `python3 plugins/sdlc-lite/scripts/check.py` rc 0 (`ok: 20 role levels, 10 agents, 23 generated definitions checked`); `git diff --check 4973e6a6` rc 0; `redck.py deviations` printed no lines (no `(red)` criteria). | note: /Users/kimgranlund/Projects/nonoun/sdlc-lite.worktrees/tmp/0605-verifier-L2 is left as an empty directory: the worktree was removed with `git worktree remove`, but `rm -rf` on the prefix was denied.) · verifier: verifier-L2 (opus) · base: 4973e6a6bed7
- Changed: see commits
- Commits: cb11577 T-0605: builder.md says a second redck record is only a base control, stale since T-0473
- Check: 1 `python3 plugins/sdlc-lite/scripts/claude_roles.py generate --check` and `python3 plugins/sdlc-li...: pass
- Check: 2 `grep -c 'only a base control' plugins/sdlc-lite/agents/builder.md` prints 0: pass
