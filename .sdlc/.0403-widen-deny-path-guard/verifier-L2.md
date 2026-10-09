<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: pass. Evidence: I ran it on the built tree and got rc=0 with the last line `steps selftest: PASS`. All four new `widen: (d)` cases print `ok:`.
- `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: rc=0. The last line is `ok: 19 role levels, 9 agents, 22 generated definitions checked`.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: pass. Evidence: rc=0 with `ok: 397 tickets, roadmap current`. The only other output was warnings about closed tickets and the flat layout, and none of them involve this change.
- Selftest cases `widen: (d)` cover four things: a deny-path rewrite (red before, green after, lookalike still red), the rerun `widen: already applied`, a span with no allow-list and no exclude still refused with the "no criterion line" message, and a span with two exclude runs refused: pass.
  - Where they are: steps.py:4471-4505. D_SPAN is the ultimate-tokens form `git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude)sdlc' ':(exclude)a.txt' | { ! grep -q .; }`. The case asserts `red_before`, then `green_after`, then that the lookalike `bxtxt` is still red (`outside`).
  - Failing-first: I made a throwaway worktree at base `a923df70` and applied only the selftest hunk (`@@ -4418`) to the old steps.py. Selftest gave rc=1 and listed three failures: the rewrite case, the rerun case and the two-exclude-runs case. The base code refuses that last span with the "no criterion line" message, so the `pathspec runs` message match is what makes it bite. The "neither allow-list nor exclude" case passed on base, which is expected: it guards behaviour the change must keep.
  - Mutation M1: I made `is_deny_span` drop the `DENY_EXCL_RE` requirement. Only `widen: (d) a git diff --name-only span with neither allow-list nor exclude is still refused` failed (rc=1), so the refusal guard bites.
  - Mutation M3: I made widen append `':(exclude)<first char>*'` instead of the exact path. The rewrite case (through its lookalike conjunct) and the rerun case failed (rc=1), so the lookalike check bites.
- The allow-list forms F, E and A are unchanged: pass.
  - Selftest on the built tree prints `ok:` for all six cases: `widen: (a)` and `widen: (b)` for each of F, E and A.
  - I read the diff at steps.py:2981-2995. The allow-list branch keeps `widen_forms`, `widen_listed`, the `ere_escape` comparison and `widen_span` unchanged. The only change is a duplicated `if not add` early return, which is harmless.
  - Callers: `is_scope_span` itself is unchanged, and its other callers (steps.py:1656 and 2343, used by lane and planned scope) still call only `is_scope_span` and `widen_forms`, so lane and fanout behaviour does not move.
- Constraints (no em or en dashes, no push): pass. `git diff | grep '^+' | grep -P '[\x{2013}\x{2014}]'` found nothing (rc=1), and `git diff --check` gave rc=0. `git log` shows no new commits on top of base a923df70.

## Out of scope changes
None.
- `.sdlc/0403-widen-deny-path-guard/handoff.md` gained an `## Acceptance criteria` section, written by the solo agent. I read it: it restates the ticket's "Done when" as runnable lines and widens nothing, so I'm treating it as harmless.
- One follow-up, not required by any criterion: `docs/references/sdlc-internals.md:93` still describes widen as accepting only `grep -v` allow-list forms. The usage text in steps.py (lines 344-346) was updated, but this reference was not, so a follow-up ticket should bring it in line.

## For the next attempt
None
