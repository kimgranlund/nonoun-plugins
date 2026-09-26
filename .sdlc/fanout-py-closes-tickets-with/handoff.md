---
id: T-0117
title: "fanout.py closes tickets with a plain close <slug>, so in a..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0113
---

## Goal
In a numbered-mode repo, a user who opted in at /fanout's confirm step gets each merged ticket closed on the integration branch even when other files cite its folder: `fanout.py run --rewrite-refs` passes `--rewrite-refs` to `tickets.py close` and the `close <id>` commit carries the rewritten files. Without the flag, behavior is unchanged (`merged, close refused: ...`), and the refusal outcome tells the user the flag exists.

Done when:
- `fanout.py run --rewrite-refs` passes the flag through to `tickets.py close`; `--dry-run` shows it in the plan.
- The `close <id>` commit stages every file the close rewrote, not only files under the ticket root (today it runs `git add -A -- <rel>`, which would leave rewritten files outside `.sdlc/` uncommitted and dirty in the integration worktree).
- `fanout.py selftest` proves, on a numbered-mode throwaway repo with a file outside the ticket root citing `<rel>/NNNN-<slug>`: without the flag the outcome is `merged, close refused` and the ticket stays open; with it the outcome is `merged`, the folder is `.NNNN-<slug>`, the citing file holds the dot path in the `close <id>` commit, and the integration worktree is clean.
- `skills/fanout/SKILL.md` step 2 (Confirm) offers the flag as a choice when the repo is in numbered mode (never added silently); `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md` describe the flag; `scripts/check.sh` passes.

## Context
Follow-up from T-0113 (close-rename-breaks-refs/filer-L1.md):

`fanout.py` closes tickets with a plain `close <slug>`, so in a numbered-mode repo a reference hit ends the ticket as `merged, close refused` and leaves it open until someone reruns with `--rewrite-refs`.

## Constraints
- T-0113 user decision: never rewrite references silently. The flag is opt-in only; the default stays refuse.
- Main is never touched, nothing is pushed; commits only inside the lanes dir.
- `tickets.py` behavior does not change.
