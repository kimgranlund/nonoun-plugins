---
id: T-0571
title: "Closed tickets keep only handoff.md and their Outcome"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0567]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-17
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Each closed `.NNNN-*` ticket folder in this repo tracks only its `handoff.md`, plus, when that handoff has no `## Outcome`, its newest verifier result. Old run records leave the tree, and git history keeps them.

## Intent
- Do:
  1. List the citations first: `grep -rln '\.sdlc/\.[0-9]\{4\}-' docs plugins .sdlc/*.md AGENTS.md`. Cited files that are removed get their links pointed at the last commit that held them: `https://github.com/<repo>/blob/<sha>/<path>`, or a `<sha>:<path>` form when the repo has no remote URL. Dated reports under `docs/reports/` are history: rewrite their links the same way, and leave their text alone.
  2. `git rm` everything else under closed folders: `runs.jsonl`, `*.attempt.json`, `*.dispatch.json`, `base-sha`, `builder-L*.md`, `planner-L*.md`, `filer-L*.md`, `skips.md`, logs, nested step folders. Keep the newest `verifier-L*.md` only where the handoff lacks `## Outcome`.
  3. One commit for the removal, with the sha recorded in the Outcome.
- Non-goals: open tickets; a reusable trim command for consumer repos (a new ticket if wanted).
- Done when: the criteria pass.

## Context
Maintainer chose this cleanup on 2026-10-15 (gap G2). 549 closed folders hold 5321 tracked files (15.6 MB): 891 `runs.jsonl`, about 700 attempt and dispatch JSON files, 383 `base-sha`, and 1026 `handoff.md` including nested step handoffs. Since 0.23.0 the lean-records rule is that a closed ticket keeps `handoff.md` plus one `## Outcome`, and run records live in `.sdlc/runtime/tasks/`.

## Constraints
Never remove a closed ticket's top `handoff.md`. `tickets.py check` and `tickets.py roadmap` must still pass, and ticket ids stay unique.

## Acceptance criteria
1. `git ls-files '.sdlc/.[0-9]*' | grep -v -E '^\.sdlc/\.[0-9]{4}-[^/]+/(handoff\.md|verifier-L[0-9]+(-[0-9]+)?\.md)$'` prints nothing.
2. Every `.sdlc/.NNNN-*/verifier-L*.md` still tracked sits beside a handoff with no `## Outcome`.
3. `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0.
4. A link checker over `docs plugins AGENTS.md .sdlc/*.md` finds no relative link to a removed path; name the command used.
5. `git diff --check` exits 0.

## Outcome

2026-10-17 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: plain-text (non-link) citations of removed paths remain unrewritten in dated reports, for example `docs/reports/proposals-live-run.md` (45 mentions), `docs/reports/2026-10-12-ceremony-audit.md` and `docs/reports/2026-10-12-ceremony-audit/counts.txt`, `docs/reports/2026-10-12-compaction-prompt-replay.md`. Criterion 4 covers links only, and the handoff says to leave report text alone, so this is not a fail. | note: many closed-ticket `handoff.md` files still name removed siblings such as `.0440-per-tier-agent-prompts/architect-L1.md` in plain text. They sit outside the `docs plugins .sdlc/*.md AGENTS.md` scope the handoff names. | note: `plugins/sdlc-lite/scripts/traces/fixtures/corpus-sdlc/` now ships about 35 run-record files inside the plugin tree; they are test fixtures only.) · verifier: verifier-L2 (sonnet) · base: 51cbf1bacc20
- Changed: see commits
- Commits: a4ecbde T-0571: Closed tickets keep only handoff.md and their Outcome
- Check: 1 Only handoff.md and verifier-L*.md remain tracked under closed folders: pass
- Check: 2 Every tracked verifier-L*.md sits beside a handoff with no `## Outcome`: pass
- Check: 3 tickets.py check exits 0: pass
- Check: 5 git diff --check exits 0: pass
