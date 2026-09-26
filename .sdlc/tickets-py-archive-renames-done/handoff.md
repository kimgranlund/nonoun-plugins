---
id: T-0116
title: "tickets.py archive renames done/dropped numbered folders to the..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0113
---

## Goal
`tickets.py archive` never silently breaks a committed or untracked reference to a folder it renames: it runs the same reference scan `close` runs (`outside_refs`) for every done/dropped `NNNN-<slug>` folder it would rename, refuses with nothing written while any file cites one, and offers the same escape hatches as `close` (`--rewrite-refs` rewrites each cite to the dot form with the rename; `--force` archives and leaves them). `archive --dry-run` lists the renames plus one `rewrite <file>` line per citing file when `--rewrite-refs` is given, and names the citing files otherwise.

Done when: the new behavior is covered by `tickets.py selftest` cases (refuse naming the file and writing nothing, `--rewrite-refs` rewrites and renames, `--force` renames and leaves the cite, dry run with and without `--rewrite-refs`, outside git no scan), `scripts/check.sh` is green, and every doc that describes `archive` (tickets.py usage/docstring, the ticket skill, repo CLAUDE.md Layout entry, `.claude/agents/sdlc-lite-author.md` if it describes archive) states the new flags.

## Context
Follow-up from T-0113 (close-rename-breaks-refs/filer-L1.md):

`tickets.py archive` renames done/dropped numbered folders to the dot-prefixed form with no reference scan, so it can break committed references the same way `close` did.

## Constraints
- Reuse `outside_refs` and close's rewrite code path; do not fork a second scanner.
- `close` behavior and its selftests stay unchanged.
- Existing archive behavior stays: numbered mode only, collision refusal, roadmap regeneration, `--dry-run` writes nothing, 'nothing to archive'.
- A file inside one of the folders being archived that cites another folder being archived in the same run counts as a reference and is handled (rewritten under `--rewrite-refs`) without breaking the rename.
- `fanout.py` does not call `archive`; no change there.

## Clarify (unattended)
Goal and Constraints were placeholders; filled by the conductor from Context and the T-0113 `close` precedent (refuse / `--rewrite-refs` / `--force`). Gap named: whether `--force` belongs on archive at all; chosen yes, to match close.
