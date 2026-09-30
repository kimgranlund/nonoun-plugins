<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: `depends` entries are now one of three kinds, `T-NNNN`, `file:<path>` or `cap:<name>`, checked by `dep_kind` and the new `CAP_RE`. Tickets can list what they supply in an optional `provides` key (`provides_of`, `providers`); it is not in `REQUIRED`. `problems()` gained errors for malformed entries, a `cap:` nobody provides, a non-list `provides` and a bad `provides` item. `order()` uses a new `edges_of`, so a `cap:` entry waits on every ticket that provides it and `file:` entries add no ordering; the Kahn tie-break by id is unchanged. `render(ts, root)` marks entries `(unmet)` and escapes `|`, and file paths resolve through a new `file_base(root)`. The module docstring now describes all three forms and says to rerun `roadmap` when a named file appears or a provider closes. Selftest cases added.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS (rc 0).
- Acceptance criteria 1 to 11 (the cap, file, malformed, unprovided, cycle, non-list `provides`, docstring and selftest-label checks): all rc 0. AC1 was also run verbatim: rc 0.
- Guard, T-only roadmap byte-identical to the `$SDLC_BASE_SHA` output (`cmp`): rc 0, run both through a wrapper script and verbatim.
- Guard `tickets.py selftest`: rc 0.
- Negative controls: I ran the selftest against 7 mutated copies of tickets.py, each inside a copied plugin tree. The mutations were: no cap edges, file entries never unmet, file path not validated, unprovided cap accepted, no git-toplevel lookup, no `|` escape, and `provides` type not checked. The selftest FAILED on every mutant, each time naming the matching new case. The unmutated copy passed.
- `python3 plugins/sdlc-lite/scripts/board.py selftest`: PASS. `fanout.py selftest`: PASS. Both import tickets.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: ok, 170 tickets, roadmap current.
- `git diff --check`: clean.

## Notes
- `render` now takes a required `root` argument, needed to resolve `file:` paths. Its only callers are `write_roadmap` and `stale` in tickets.py; board.py and fanout.py use only `tickets.load`.
- Two behavior changes to know about:
  - A malformed entry that used to report "which no ticket has" (for example `T-12`) now gets the malformed-entry error.
  - A ticket that both depends on `cap:x` and provides `x` is reported as a self-cycle. That is what the spec says literally: an edge to every provider.
- The selftest's file-path cases assume the temp dir is outside git, the same assumption the existing tests make. One extra case runs `git init` in a temp dir to show paths resolve against the git toplevel rather than the root's parent; it is skipped when git is missing.
- Docs and skills outside tickets.py were left alone, as this step required.
