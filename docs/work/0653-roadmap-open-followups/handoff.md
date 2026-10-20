---
id: T-0653
title: "Roadmap renders an Open follow-ups section from NOTES.md"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
claimed_by: sdlc-lite-author 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Open follow-ups have a visible register: the roadmap lists every NOTES.md `decide:` item that has not become a ticket, and `tickets.py check` reports how many are unrouted.

## Intent
- Do: (1) `render` (the roadmap writer behind `write_roadmap`, `plugins/sdlc-lite/scripts/tickets.py`) appends an `## Open follow-ups` section listing each NOTES.md line tagged `decide:` (and `source-fix:` when present) that carries no `-> T-NNNN` marker, with its `## <id>: <title>` block as the source; no section when there are none. (2) `cmd_check` prints `open follow-ups: <n> unrouted in <notes path>` when n > 0 (an info or warning line, exit 0). (3) Usage text and the router's close steps say: mark an item routed by adding `-> T-NNNN` to its NOTES.md line.
- Non-goals: `close` writing the marker back into NOTES.md automatically (a follow-up once T-0651 files reason-close items); a status field in NOTES.md; reading closed handoffs.
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #13, ui-kit-neue audit 2026-10-20. This ticket is part (c) of #13 (open follow-ups register); parts (a) and (b) are T-0651 and T-0652.
- ui-kit-neue: `docs/work/NOTES.md` stops at T-0005 and has no status; one follow-up (admin-shell docs page) lived only in conductor chat and a git-ignored verifier record.
- NOTES.md format: `append_notes` at `plugins/sdlc-lite/scripts/tickets.py:3156` writes `## <id>: <title> (<date>)` blocks of `- <tag>: <text>` lines; tags come from `TAG_RE` at `plugins/sdlc-lite/scripts/tickets.py:3146` (`fix-now`, `decide`, `note`). `source-fix:` is not a tag in this repo; match it only as a literal prefix.
- The `-> T-NNNN` form already exists on Outcome Follow-up lines (`- Follow-up: decide: Add retry to fetch -> T-0002`, selftest near `plugins/sdlc-lite/scripts/tickets.py:7851`); reuse it for NOTES.md lines. This ticket reads the marker; nothing writes it yet, so it does not depend on T-0651.
- Roadmap: `write_roadmap` at `plugins/sdlc-lite/scripts/tickets.py:2505` writes `render(ts, root)`; `stale` (line 2515) compares the rendered text, so `check` treats a roadmap missing the new section as stale, which is the intended refresh path. `cmd_check` at `plugins/sdlc-lite/scripts/tickets.py:3840`; the notes path is `layout_paths(root).notes`.
- This repo's own `docs/work/NOTES.md` holds such items; after the change `roadmap` will add the section to `docs/work/ROADMAP.md`. Regenerate it in the same commit.

## Constraints
A repo with no NOTES.md, or with no open `decide:` item in it, renders the roadmap byte-identical to today. `check` keeps its exit code; the count is not a failure.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with a new case: a NOTES.md with `- decide: a`, `- decide: b -> T-0009` and `- note: c` renders `## Open follow-ups` listing only `a`, and `check` prints `open follow-ups: 1 unrouted`. The case fails with the change reverted.
2. The same selftest asserts a fixture with no NOTES.md renders no `## Open follow-ups` heading.
3. `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc roadmap` then `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0 in this repo.
4. `git diff --check` exits 0.
