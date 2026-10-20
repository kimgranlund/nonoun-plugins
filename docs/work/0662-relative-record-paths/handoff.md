---
id: T-0662
title: "Tracked work records hold no absolute machine paths"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Tracked work records (NOTES.md, a ticket's Outcome, the gate ledger) never hold an absolute machine path, and `tickets.py check` warns when one does.

## Intent
- Do: (1) Add one helper in `plugins/sdlc-lite/scripts/tickets.py` that relativizes a text: a path under the repo toplevel becomes repo-relative, and a path under the lanes root (`wtroot.py root`, `../<repo>.worktrees/<lane>/`) becomes `<lane>:<rest>`; `append_notes` and `outcome_section` pass every written line through it. (2) `cover_at` in `plugins/sdlc-lite/scripts/fanout.py` writes the ledger entry's `log` (and any other path field) through the same helper. (3) `cmd_check` warns `warning: <file>:<line>: absolute path in a tracked work record` for `/Users/`, `/home/`, `/var/folders/` or `/private/tmp/` in tracked NOTES.md, open-ticket `handoff.md` files and the gate ledger.
- Non-goals: deciding whether the gate ledger should be tracked at all (issue #22 raises it; a separate decision ticket); rewriting existing closed handoffs or history.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #22, ui-kit-neue audit 2026-10-20.
- ui-kit-neue `git grep -c` for a home path: `docs/work/NOTES.md` 6 hits, `.sdlc/gate-ledger.jsonl` 11 lines, closed handoffs `.0003` 6 and six others 1 each; `.0051-bottom-panel/handoff.md:44` points into another lane's `.sdlc/runtime/`.
- Writers: `append_notes` at `plugins/sdlc-lite/scripts/tickets.py:3156` (verifier notes verbatim to NOTES.md); `outcome_section` at `plugins/sdlc-lite/scripts/tickets.py:3249`; the reason close text built by `close_reason` at `plugins/sdlc-lite/scripts/fanout.py:951` carries verifier notes into the Outcome verdict line; the ledger entry at `plugins/sdlc-lite/scripts/fanout.py:2855-2859` (`cover_at`, fields `log`, `gates`), ledger name `LEDGER` at `plugins/sdlc-lite/scripts/fanout.py:2738`, committed with `git add -f`.
- Check: `cmd_check` at `plugins/sdlc-lite/scripts/tickets.py:3840` already collects `warning:` lines (`link_warnings` line 621, `top_level_warnings` line 933); add one more collector there.
- This repo: `git grep -l -E '/Users/|/home/|/var/folders/|/private/tmp/' -- docs/work .sdlc | wc -l` finds 109 tracked files, almost all closed `.NNNN-*` handoffs and verifier records, some of them prose that only names the pattern. Scope the warning to NOTES.md, open (undotted) ticket handoffs and the ledger so this repo's history does not flood it, and say in the Outcome how many warnings this repo prints.

## Constraints
Text with no absolute path is written byte-identical to today. `check` keeps exit 0 for these warnings. No closed `.NNNN-*` handoff is edited.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with a new case: a close whose verifier `## Notes` holds `- note: see <tmp repo>/src/a.py:3` and `- note: see <lanes root>/wave6/b.py` writes `src/a.py:3` and `wave6:b.py` into NOTES.md and the Outcome, never the absolute prefix. The case fails with the change reverted.
2. The same selftest asserts `check` prints `absolute path in a tracked work record` for a NOTES.md line holding `/Users/x/repo/a.py` and prints no such line for a clean NOTES.md (the negative control).
3. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 and its cover case asserts the ledger line's `log` is not absolute.
4. `git diff --check` exits 0.

## Outcome

- Changed: `tickets.py` gains `relative_paths` and `path_bases` (repo toplevel and main checkout become repo-relative, the lanes root becomes `<lane>:<rest>`, each in its realpath and macOS `/private`-less spelling); close relativizes every follow-up item before the digest, `append_notes` and `outcome_section` pass their text through it; `check` adds `abs_path_warnings` over tracked NOTES.md, open undotted handoffs and `gate-ledger.jsonl`. `fanout.py` `cover_at` writes `gates` and `log` through it, the log as `logs:cover-<run_id>-<k>.log` under the lanes dir.
- Checks: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exit 0 (new T-0662 cases; the close case failed before the fix, when only the realpath spelling was matched); `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exit 0 (cover asserts `log` starts `logs:cover-` and is not absolute); `git diff --check` exit 0; `python3 plugins/sdlc-lite/scripts/check.py` exit 0.
- This repo: `tickets.py --root .sdlc check` prints 5 absolute-path warnings, 3 in this handoff (its own prose naming the patterns) and 2 in `docs/work/NOTES.md` (lines 34 and 58, verifier notes naming lanes-root tmp paths).
