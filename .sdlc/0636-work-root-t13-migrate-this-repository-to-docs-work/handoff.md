---
id: T-0636
title: "work_root t13: migrate this repository to docs/work"
type: chore           # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0626, T-0627, T-0628, T-0629, T-0630, T-0631, T-0632, T-0633, T-0634, T-0635, T-0637]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
migrate this repository to docs/work.

## Context
Part 16 of 16 from the T-0618 design (user decision 2026-10-19: tracked work records move to `docs/work/`, `.sdlc/` keeps config, runtime, messages and the router). Design: `.sdlc/runtime/tasks/0618-work-records-in-docs/architect-L1.md` (Interfaces section) and node `t13` in `.sdlc/runtime/tasks/0618-work-records-in-docs/decompose/manifest-v2.json`. Read those two, not the whole tree. Docs naming follows T-0620 (no master files; `work/ROADMAP.md` and `work/NOTES.md` are the declared UPPERCASE singletons).

Files: `.sdlc/** -> docs/work/** (git renames)`, `.sdlc/config`, `AGENTS.md`, `.sdlc/AGENTS.md (regenerated)`, `docs/reports/broken-links-allowlist.md (rows only)`

Actions this ticket hosts:
-  keep the spelling allowlist and broken-link baseline valid for closed tickets in the new root
-  migrate this repository and leave every check green
-  record the layout and config key in the design homes (ticket-stages, repo-onboarding, docs/layout.md)

## Constraints
- Old layouts stay the default: with no `work_root:` line every path is unchanged, and existing selftest fixtures keep passing; add `work_root` cases rather than rewriting fixtures.
- The failing check lands before or with the change.
- Touch only the files listed; a needed change elsewhere is a new ticket.

## Acceptance criteria
- after `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc migrate-work-root --to docs/work --rewrite-refs` and `git add -A`: `git ls-files .sdlc | grep -vE '^\.sdlc/(config|AGENTS\.md|CLAUDE\.md|messages/)' | wc -l` prints 0 (red before: 778 on 2026-10-19), every `git status --porcelain` row starts with R or M, and `tickets.py --root .sdlc check`, `docs_check.py --root .`, `bash plugins/sdlc-lite/scripts/check.sh` and `python3 scripts/check-packaging.py` each exit 0
- From T-0635 (do in this ticket): `migrate-work-root --rewrite-refs` also rewrites path mentions in prose (in a trial it changed an error string in `check.py` and a historical sentence in `docs/specs/sdlc-lite/design.md`); review `git diff` of every non-record file and revert prose that describes history before committing. Also record the layout in `docs/specs/repo-onboarding/design.md` and `docs/layout.md` (named by T-0635, not in its files).
