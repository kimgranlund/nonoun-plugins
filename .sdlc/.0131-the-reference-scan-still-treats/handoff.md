---
id: T-0131
title: "The reference scan still treats another tree's .sdlc/0003-x as a..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0118
---

## Goal
`tickets.py close` and `archive` (numbered mode) stop reporting and rewriting a path that only contains `<rel>/<slug>` but names a folder in another tree (`other/.sdlc/0003-x`, `/elsewhere/repo/.sdlc/0003-x`, `../other/.sdlc/0003-x`), so the scan follows the documented rule that a path resolving elsewhere is not a reference.

## Intent
Literal ask: the reference scan still treats another tree's `.sdlc/0003-x` as a reference, and `.sdlc/0003-xy` as a match for `0003-x`; the literal-substring rule contradicts the rule that a path resolving elsewhere is not a reference.
Deltas:
- `.sdlc/0003-xy` half: defaulted: already fixed by T-0128 (`literal_re` lookahead); keep it, add nothing beyond a regression guard if the planner wants one.
- Where the literal must start: defaulted: the literal `<rel>/<slug>` counts only when it begins a path token (start of text or right after a `TOKEN_RE` delimiter: whitespace, quotes, backticks, parens, angle or square brackets). A literal preceded by any other character (`other/`, `/abs/elsewhere/`, `../x/`, `https://host/.../`, `file:`) is no longer a literal hit; such a token still counts only if `ref_tokens` resolves it to the folder (for example the absolute path of this toplevel, or `./.sdlc/0003-x`).
- Rewrite: defaulted: `rewrite_files` applies the same start boundary, so a non-resolving other-tree path in a file that also cites the real folder stays byte-identical while the real cite is rewritten.
- URLs and prefixed forms (`https://.../blob/main/.sdlc/0003-x`, `key=.sdlc/0003-x`): defaulted: not references any more (they do not resolve to the folder); noted in the docs as a limitation.
- T-0118 Constraint "existing toplevel-relative detection unchanged": defaulted: superseded for the other-tree case only; a bare `.sdlc/0003-x` token, one after `(`, a quote, or backtick, and every existing selftest case keep working.
Do: in `plugins/sdlc-lite/scripts/tickets.py`, add the token-start boundary to `literal_re` (used by `outside_refs` and `rewrite_files`); add selftest cases for close and archive proving `other/.sdlc/0003-x`, an absolute path into another directory ending in `.sdlc/0003-x`, and `../other/.sdlc/0003-x` neither block nor get rewritten, and a file citing both an other-tree path and the real `.sdlc/0003-x` gets only the real cite rewritten; update the `outside_refs`/`literal_re`/`rewrite_files` docstrings, the close/archive help text if it describes the rule, the CLAUDE.md Layout `tickets.py` entry, `.claude/agents/sdlc-lite-author.md`, and `plugins/sdlc-lite/skills/ticket/SKILL.md` where they describe the literal rule.
Non-goals: case folding, symlinks beyond today's absolute realpath, `~`, self-references inside the moving folder, other git worktrees' files, fanout.py changes.
Done when: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` passes with the new cases, the new negative cases fail against the pre-change `literal_re` (red before, green after), and `plugins/sdlc-lite/scripts/check.sh` is green.

## Context
Follow-up from T-0118 (the-reference-scan-matches-only/filer-L1.md):

The reference scan still treats another tree's `.sdlc/0003-x` as a reference, and `.sdlc/0003-xy` as a match for `0003-x`. The literal-substring rule was kept per the T-0118 Constraints, which contradicts the Deltas rule that a path resolving elsewhere is not a reference.

## Constraints
All existing tickets.py selftest cases, CLI flags, and output formats stay unchanged. Stdlib only. Every refusal still writes nothing.
