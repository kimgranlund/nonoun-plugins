<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
`tickets.py` close and archive (numbered mode) must report and rewrite only citations of the ticket's own folder. A literal `<rel>/<slug>` that continues into a longer folder name (`.sdlc/0001-a` inside `.sdlc/0001-ab`) must be neither reported by `outside_refs` nor rewritten by `rewrite_files`.

## Step 1: Boundary-match the literal folder path in outside_refs and rewrite_files (gates green)
level: L2
### Do
Edit `plugins/sdlc-lite/scripts/tickets.py`:
- In `outside_refs` (around line 277), replace the fixed-string test `old in text` with a regex match. The regex is `re.escape(old)` followed by a negative lookahead for a folder-name character, for example `(?![A-Za-z0-9_-])`. That way `.sdlc/0001-a` matches when it is followed by `/`, end of text or token, whitespace, or punctuation (`.,;:!?)]"'` and so on), but never when it runs on into `.sdlc/0001-ab`. Compile it once per call and share it with `rewrite_files`, for example through a small helper such as `literal_re(old)`.
- In `rewrite_files` (around line 327), replace `.replace(old, new)` with the same regex's `sub`, so a file citing both `.sdlc/0001-a/x.md` and `.sdlc/0001-ab/y.md` rewrites only the first. `ref_tokens` already compares whole path components, so leave it alone.
- Keep every documented reference form working: a literal followed by `/`, end of token, or punctuation, plus toplevel-relative, file-relative, and absolute tokens.
- Add selftest cases next to the existing `(u) refs:` close cases (around lines 1640 to 1760), and one archive case near the `arch_ref` cases (around lines 1869 to 1990), in a fixture that holds both a `0001-a` and a `0001-ab` numbered folder (or `0003-x` / `0003-xy` in the close fixture's naming; the id-prefixed pair must share a prefix):
  - A file citing only `.sdlc/<longer>/...` does not block a plain close of the shorter ticket (rc 0, no `rewrote`) and is byte-identical afterwards.
  - With `--rewrite-refs`, a file citing both folders gets only the shorter folder's cite rewritten.
  - The literal string `0001-ab` must appear in the selftest source.
- Update the wording of the literal rule so it says the literal must end at `/`, the end of a token, or punctuation, and never runs on into a longer folder name. Change the module docstring (around line 25), the `outside_refs` docstring (line 244), the `rewrite_files` docstring, the close docstring near line 658, and the matching sentence in the repo-root `CLAUDE.md` `scripts/tickets.py` bullet ("keeps files with a literal `<rel>/<slug>` ..."). Update `.claude/agents/sdlc-lite-author.md` only if it describes the scan (it currently does not mention the literal rule).
- This is the only step, so it is also the gates green step. Run `plugins/sdlc-lite/scripts/check.sh` and fix any red this change introduced.
### Acceptance criteria
- `python3 -B -c 'import sys,tempfile,pathlib,subprocess as s; sys.path.insert(0,"plugins/sdlc-lite/scripts"); import tickets as t; d=pathlib.Path(tempfile.mkdtemp()); r=d/".sdlc"; (r/"0001-a").mkdir(parents=True); (r/"0001-ab").mkdir(); (d/"only.md").write_text("see .sdlc/0001-ab/handoff.md\n"); (d/"both.md").write_text("see .sdlc/0001-a/x.md and .sdlc/0001-ab/y.md\n"); s.run(["git","-C",str(d),"init","-q"]); top,old,new,fs=t.outside_refs(r,"0001-a"); t.rewrite_files(top,fs,old,new); print(fs); sys.exit(0 if fs==["both.md"] and (d/"only.md").read_text()=="see .sdlc/0001-ab/handoff.md\n" and (d/"both.md").read_text()=="see .sdlc/.0001-a/x.md and .sdlc/0001-ab/y.md\n" else 1)'` exits 0. It is red at HEAD: it prints `['both.md', 'only.md']`.
- (guard) `python3 -B -c 'import sys,tempfile,pathlib,subprocess as s; sys.path.insert(0,"plugins/sdlc-lite/scripts"); import tickets as t; d=pathlib.Path(tempfile.mkdtemp()); r=d/".sdlc"; (r/"0001-a").mkdir(parents=True); (d/"e.md").write_text("see .sdlc/0001-a\n"); (d/"p.md").write_text("see .sdlc/0001-a, ok\n"); (d/"q.md").write_text("(.sdlc/0001-a)\n"); (d/"s.md").write_text("see .sdlc/0001-a/h.md\n"); s.run(["git","-C",str(d),"init","-q"]); top,old,new,fs=t.outside_refs(r,"0001-a"); t.rewrite_files(top,fs,old,new); print(fs); sys.exit(0 if fs==["e.md","p.md","q.md","s.md"] and (d/"p.md").read_text()=="see .sdlc/.0001-a, ok\n" and (d/"q.md").read_text()=="(.sdlc/.0001-a)\n" else 1)'` exits 0. This covers a literal at end of line, before punctuation, and before `/`, which must still be found and rewritten.
- `grep -qF "0001-ab" plugins/sdlc-lite/scripts/tickets.py` passes, showing the selftest carries the prefix-sibling case.
- (guard) `python3 -B plugins/sdlc-lite/scripts/tickets.py selftest` exits 0.
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0.
- The diff shows the updated literal-rule wording in the `tickets.py` docstrings and in the `CLAUDE.md` `scripts/tickets.py` bullet (observable with `git diff HEAD -- CLAUDE.md plugins/sdlc-lite/scripts/tickets.py`).

## Risks
- The folder-name character class for the lookahead is a judgment call. Slugs are `[a-z0-9-]`. Adding `_` and uppercase is conservative, but it means a cite like `.sdlc/0001-a_old` is no longer matched. That is acceptable, because it names a different folder.
- A literal followed by `.` then more text (`.sdlc/0001-a.md`) still matches, since `.` counts as punctuation. This keeps the documented punctuation form and is not covered by this ticket.
- `check.sh` takes about 90 seconds.
