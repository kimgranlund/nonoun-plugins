---
id: T-0577
title: "--rewrite-refs rewrites citations inside frozen records"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`tickets.py ... --rewrite-refs` (close, archive, number, migrate-layout) never rewrites a file under a frozen path. It lists such a file as `kept frozen: <file>` instead, so frozen records (ADRs, dated reports) keep their original citations.

## Repro
1. A repo whose `docs/layout.md` lists frozen paths, for example `.claude/docs/adr/**` (agent-ui, 2026-10-15).
2. Run `tickets.py migrate-layout --rewrite-refs` (or archive or close with `--rewrite-refs`) where a frozen file cites a moved ticket path.

## Expected
Frozen files are left alone and listed; every other citing file is rewritten.

## Actual
`--rewrite-refs` rewrote citations inside frozen ADRs and `.claude/docs/adr/`.

## Context
Frozen paths are already declared in `docs/layout.md` (`Frozen paths`, one glob per line; `onboard.py setup` refuses another format). Read that list, the same way `onboard.py` does, plus an optional `rewrite_skip:` glob line in `.sdlc/config`. Also seen: `onboard.py setup` refused with exit 1 until the Frozen paths list was one glob per line. If that refusal's message does not say so, make it say so. Reported by the agent-ui conductor.

## Constraints
Non-frozen rewrite behavior is unchanged.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0. Its new case shows a fixture with a frozen `docs/adr/0001.md` and a non-frozen doc, both citing a ticket path that `archive --rewrite-refs` moves: the frozen file is unchanged and listed as `kept frozen:`, and the other file is rewritten. The case failed before the change.
2. The onboard refusal for a malformed Frozen paths list names the expected one-glob-per-line format. Show it with a selftest line or a command and its output.
3. `git diff --check` exits 0.

## Outcome
- Changed: `tickets.py` adds `frozen_globs` (docs/layout.md `## Frozen paths` via `onboard.parse_layout`, plus `rewrite_skip:` config globs) and `is_frozen`; `outside_refs(frozen=[])` leaves frozen citing files out and collects them; close, archive, number and migrate-layout print `kept frozen: <file>` and never rewrite them. `onboard.py` Frozen paths refusal now says `write one backticked glob per line, such as - \`docs/adr/**\``. Usage text, `skills/ticket/SKILL.md` and `docs/references/sdlc-internals.md` updated.
- Check: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exit 0 (new case `archive refs: --rewrite-refs keeps a frozen file and rewrites the other`; with `is_frozen` forced False it fails, exit 1). `python3 plugins/sdlc-lite/scripts/onboard.py selftest` exit 0 (asserts the refusal names `one backticked glob per line`); refusal output: `bad-layout.md:5: list line under '## Frozen paths' is not one \`<glob>\`: write one backticked glob per line, such as - \`docs/adr/**\``. `git diff --check` exit 0. `python3 scripts/check-packaging.py` exit 0.
- Open: migrate-work-root keeps its own docs/reports and closed-ticket rule and does not read the frozen list.

## Outcome

2026-10-19 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: tickets.py:3971 and the callers at 5585, 7829 and 8068 call `outside_refs` without `frozen=`, so their behavior is unchanged as the Constraints require. | note: the selftest covers archive only. close, number and migrate-layout got the same `kept frozen:` wiring in the diff but have no dedicated selftest case, and I did not run them.) · verifier: verifier-L2 (sonnet) · base: ab9c6afd1857
- Changed: see commits
- Commits: 080e711 T-0577: --rewrite-refs keeps files under frozen paths
- Check: 1 tickets.py selftest exits 0 with the new frozen-path case: pass
- Check: 2 onboard refusal names the one-glob-per-line format: pass
- Check: 3 git diff --check exits 0: pass
