<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: added `migrate_text`, `ensure_topics_config` and `cmd_migrate_layout`, the `migrate-layout` branch in `run`, the subparser and its kwargs in `main`, the `import posixpath` line, the docstring Usage text and a `migrate-layout` command entry, and the `(mig)` selftest cases.

## Checks
- Criteria 1 to 9 (fixture criteria, each run with `bash -c` from the repo root): all PASS.
- Criterion 10 (the docstring Usage line and the selftest's `run(<name>, 'migrate-layout'` grep): PASS.
- Guard `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: `tickets selftest: PASS` in 37.7 s.
- Guard scope check against `$SDLC_BASE_SHA` (44168d55): PASS. The only changed file outside `.sdlc` is `tickets.py`.
- `git diff --check`: clean.
- Negative control: I imported `tickets` and patched `onboard.find_block` to always report no block, then ran `selftest()`. It fails as expected. The cite-refusal case then lists `  AGENTS.md`, which proves the managed-block freeze is under test. The migration cases also fail, because the router checks see no block.

## Notes
- `ensure_topics_config` leaves the config alone when every `layout:` line there already says `topics`. It drops the layout lines and appends `layout: topics` only when no layout line exists or one says something else. Handoff item 7 read literally drops every layout line. I kept existing topics lines so a topics config stays byte-identical, which is why the skipped-migration case prints no `config` lines. Every other line is untouched, and `ticket_root: tickets` is appended only when no `ticket_root` line exists.
- Dry-run output order is: `move` lines (sorted by src), then `rewrite` and `keep` lines (sorted together by file), then `config` lines. A real run appends `cmd_check`'s output after those.
- In the token form test, a token whose prefix lands on a src from the file's dir stops there: it is file-relative. Only when it does not land from there is the toplevel tried. The re-expression for a moved file uses the existence test only for tokens that name no src. So `router: .sdlc/tickets/AGENTS.md`-style lines in moved handoffs stay unchanged.
- I did not run the command against this repo's `.sdlc`. It would refuse by design: the tree is dirty, and `.sdlc/pause-2026-10-06.md` is a loose root file. Before the real migration in step 2, that file must be moved or removed and the tree committed.
- The selftest now takes about 37 s; the handoff measured 31 s at HEAD.
- `results.py validate` rejects a draft without the `<!-- role=... -->` header line. This message has no header, as the brief asked, because the harness saves it verbatim.
