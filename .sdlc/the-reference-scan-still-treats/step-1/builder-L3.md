<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: `literal_re` now takes the lookbehind `(?<![^\s'"`()<>\[\]])`, so the literal counts only where it starts a path token. The trailing `(?![A-Za-z0-9_-])` lookahead is kept.
  - The docstrings of `literal_re`, `outside_refs` and `rewrite_files` now state the rule with the phrase "starts a path token".
  - New close `(u) refs` selftest cases: three other-tree paths, each run with plain `close` and with `close --rewrite-refs`, plus one file mixing an `other/` cite with a real cite.
  - New `archive refs` selftest cases: the other-tree paths, run with `archive` and with `archive --rewrite-refs`, plus a mixed file using `other/.sdlc/0001-alpha/...`.
- `CLAUDE.md`: the tickets.py bullet's literal rule now includes "starts a path token" and the limitation that URL and prefixed forms are no longer references.
- `.claude/agents/sdlc-lite-author.md`: the reference-scan passage now states the same rule.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: the scan sentence now states the same rule.

## Checks
- C1, other-tree paths are not references (`outside_refs` with the python3 -c one-liner): printed `[]`, rc=0
- C2, the mixed file gets only its real cite rewritten: printed `['a.md'] 'see other/.sdlc/0003-x/h.md and .sdlc/.0003-x/h.md\n'`, rc=0
- C3 (guard), real cites are still found: printed `['a.md', 'b.md', 'c.md', 'e.md', 'f.md']`, rc=0
- C4, red before and green after with `literal_re` patched back to the old body: printed `rc 1`, exit 0. The "did not bite" list holds exactly the 10 new cases (7 close, 3 archive) and nothing else.
- All six `grep -qF` criteria (`other/.sdlc/0003-x`, `other/.sdlc/0001-alpha`, and `starts a path token` in tickets.py, CLAUDE.md, sdlc-lite-author.md and ticket/SKILL.md): rc=0 each
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS, rc=0
- (guard) `plugins/sdlc-lite/scripts/check.sh`: rc=0. It ends with shellcheck and plugin validate ok, and a grep of its output for fail, warn or error found nothing.

## Notes
- `.sdlc/the-reference-scan-still-treats/handoff.md` was already modified before this step started. I did not touch it.
- `ref_tokens` is unchanged, as the step asked. A `./.sdlc/...` token or this toplevel's absolute path still counts through `ref_tokens` (C3 covers the absolute path).
- The `--rewrite-refs` help text does not describe the literal rule, so I left it as it was.
