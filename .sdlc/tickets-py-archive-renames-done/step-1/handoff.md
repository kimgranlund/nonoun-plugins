## Task goal
`tickets.py archive` never silently breaks a committed or untracked reference to a folder it renames: it runs the same reference scan `close` runs (`outside_refs`) for every done/dropped `NNNN-<slug>` folder it would rename, refuses with nothing written while any file cites one, and offers the same escape hatches as `close` (`--rewrite-refs` rewrites each cite to the dot form with the rename; `--force` archives and leaves them). `archive --dry-run` lists the renames plus one `rewrite <file>` line per citing file when `--rewrite-refs` is given, and names the citing files otherwise.

Done when: the new behavior is covered by `tickets.py selftest` cases (refuse naming the file and writing nothing, `--rewrite-refs` rewrites and renames, `--force` renames and leaves the cite, dry run with and without `--rewrite-refs`, outside git no scan), `scripts/check.sh` is green, and every doc that describes `archive` (tickets.py usage/docstring, the ticket skill, repo CLAUDE.md Layout entry, `.claude/agents/sdlc-lite-author.md` if it describes archive) states the new flags.

## Step 1: Reference scan and flags for archive in tickets.py
level: L3
### Do
Edit `plugins/sdlc-lite/scripts/tickets.py` only.

1. Pull the rewrite loop out of `cmd_close`'s `rewrite_now` into one module-level helper, for example `rewrite_files(top, files, old, new)`. It replaces `old` with `new` as bytes in each toplevel-relative file.
   - `cmd_close` calls this helper. Its behavior, output text and ordering stay exactly as now.
   - Do not write a second scanner. Archive calls `outside_refs(root, name)` for each folder it would rename.
2. Give `cmd_archive` the signature `cmd_archive(root, numbered=False, dry_run=False, rewrite_refs=False, force=False)`. After the existing numbered-mode, problems and collision checks, and before any write:
   - Collect `(name, top, old, new, files)` for each target name that has hits.
   - Outside git, `outside_refs` returns no files, so there is no scan and archive behaves as today.
   - A file inside one archived folder that cites another archived folder counts. `outside_refs` excludes only the folder's own files, so it already finds that file.
3. With hits and neither `rewrite_refs` nor `force`, raise `Fail` and write nothing. The message names:
   - each cited folder path (`old`),
   - each citing file, one per line, indented like close's refusal,
   - `--rewrite-refs` (rewrite them to the dot form) and `--force` (archive anyway, leaving them),
   - and ends with `nothing written`.
   A `--dry-run` without either flag refuses the same way, as `close --dry-run` does.
4. `--dry-run` with `--rewrite-refs` prints the existing `<name> -> .<name>` lines, then one `rewrite <file>` line per distinct citing file, sorted. With `--force` it prints only the rename lines. It writes nothing in either case.
5. On a real run with `--rewrite-refs`, rewrite every citing file BEFORE any rename. The paths are toplevel-relative to the pre-rename tree, and a file inside a folder being archived moves when that folder is renamed.
   - A file cited for several folders gets each folder's replacement.
   - Then do the renames, the roadmap regeneration and the config persistence as now.
   - Append `; rewrote refs in <files>` to the output.
   `--force` renames and leaves the files untouched.
6. Keep all existing archive behavior unchanged: numbered mode only, collision refusal, roadmap regeneration, `--dry-run` writes nothing, `nothing to archive`.
7. Wiring:
   - Add `--rewrite-refs` and `--force` to the `archive` argparse subparser and pass both through in `main`.
   - Update the module usage line to `archive [--dry-run] [--rewrite-refs] [--force] [--numbered]`.
   - Update the `archive` paragraph of the docstring (around line 50) to describe the scan, the refusal, both flags, the dry-run `rewrite <file>` lines, and that outside git there is no scan.
8. Add selftest cases next to the existing archive block, reusing the `(u) refs` git-fixture pattern (`rgit`, `whole`). Put the git-dependent ones under the existing `shutil.which('git')` guard. Cover:
   - a committed reference refuses, names the file, and writes nothing (`whole` unchanged);
   - `run(root, 'archive', rewrite_refs=True)` rewrites the file and renames;
   - `run(root, 'archive', force=True)` renames and leaves the cite;
   - a dry run with `rewrite_refs=True` lists `rewrite <file>` and writes nothing;
   - a dry run without flags refuses, names the file, and writes nothing;
   - a file in one archived folder citing another archived folder in the same run is rewritten under `--rewrite-refs`, and both folders are renamed;
   - outside git (no `git init`) a citing file does not block the archive.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- A committed cite makes archive refuse and leaves the folder in place: `d=$(mktemp -d) && git -C "$d" init -q && mkdir -p "$d/.sdlc/0001-a" && printf -- "---\nid: T-0001\ntitle: a\ntype: idea\nstatus: done\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-09-25\n---\n" > "$d/.sdlc/0001-a/handoff.md" && printf "ticket_folders: numbered\n" > "$d/.sdlc/config" && printf "see .sdlc/0001-a/handoff.md\n" > "$d/spec.md" && ! python3 plugins/sdlc-lite/scripts/tickets.py --root "$d/.sdlc" archive 2>/dev/null && test -d "$d/.sdlc/0001-a"`
- The refusal names the citing file: `d=$(mktemp -d) && git -C "$d" init -q && mkdir -p "$d/.sdlc/0001-a" && printf -- "---\nid: T-0001\ntitle: a\ntype: idea\nstatus: done\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-09-25\n---\n" > "$d/.sdlc/0001-a/handoff.md" && printf "ticket_folders: numbered\n" > "$d/.sdlc/config" && printf "see .sdlc/0001-a/handoff.md\n" > "$d/spec.md" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$d/.sdlc" archive 2>&1 | grep -qF spec.md`
- `--rewrite-refs` rewrites and renames: `d=$(mktemp -d) && git -C "$d" init -q && mkdir -p "$d/.sdlc/0001-a" && printf -- "---\nid: T-0001\ntitle: a\ntype: idea\nstatus: done\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-09-25\n---\n" > "$d/.sdlc/0001-a/handoff.md" && printf "ticket_folders: numbered\n" > "$d/.sdlc/config" && printf "see .sdlc/0001-a/handoff.md\n" > "$d/spec.md" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$d/.sdlc" archive --rewrite-refs && grep -qxF "see .sdlc/.0001-a/handoff.md" "$d/spec.md" && test -d "$d/.sdlc/.0001-a"`
- `--force` renames and leaves the cite: `d=$(mktemp -d) && git -C "$d" init -q && mkdir -p "$d/.sdlc/0001-a" && printf -- "---\nid: T-0001\ntitle: a\ntype: idea\nstatus: done\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-09-25\n---\n" > "$d/.sdlc/0001-a/handoff.md" && printf "ticket_folders: numbered\n" > "$d/.sdlc/config" && printf "see .sdlc/0001-a/handoff.md\n" > "$d/spec.md" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$d/.sdlc" archive --force && grep -qxF "see .sdlc/0001-a/handoff.md" "$d/spec.md" && test -d "$d/.sdlc/.0001-a"`
- The dry run with `--rewrite-refs` lists the file and writes nothing: `d=$(mktemp -d) && git -C "$d" init -q && mkdir -p "$d/.sdlc/0001-a" && printf -- "---\nid: T-0001\ntitle: a\ntype: idea\nstatus: done\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-09-25\n---\n" > "$d/.sdlc/0001-a/handoff.md" && printf "ticket_folders: numbered\n" > "$d/.sdlc/config" && printf "see .sdlc/0001-a/handoff.md\n" > "$d/spec.md" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$d/.sdlc" archive --dry-run --rewrite-refs | grep -qxF "rewrite spec.md" && test -d "$d/.sdlc/0001-a" && grep -qxF "see .sdlc/0001-a/handoff.md" "$d/spec.md"`
- The dry run without flags names the citing file and writes nothing: `d=$(mktemp -d) && git -C "$d" init -q && mkdir -p "$d/.sdlc/0001-a" && printf -- "---\nid: T-0001\ntitle: a\ntype: idea\nstatus: done\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-09-25\n---\n" > "$d/.sdlc/0001-a/handoff.md" && printf "ticket_folders: numbered\n" > "$d/.sdlc/config" && printf "see .sdlc/0001-a/handoff.md\n" > "$d/spec.md" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$d/.sdlc" archive --dry-run 2>&1 | grep -qF spec.md && test -d "$d/.sdlc/0001-a"`
- A cite between two folders archived in the same run is rewritten, and both folders are renamed: `d=$(mktemp -d) && git -C "$d" init -q && for s in 1-a 2-b; do mkdir -p "$d/.sdlc/000$s" && printf -- "---\nid: T-000${s%%-*}\ntitle: ${s#*-}\ntype: idea\nstatus: done\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-09-25\n---\n" > "$d/.sdlc/000$s/handoff.md"; done && printf "ticket_folders: numbered\n" > "$d/.sdlc/config" && printf "see .sdlc/0002-b/handoff.md\n" > "$d/.sdlc/0001-a/notes.md" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$d/.sdlc" archive --rewrite-refs && grep -qxF "see .sdlc/.0002-b/handoff.md" "$d/.sdlc/.0001-a/notes.md" && test -d "$d/.sdlc/.0002-b"`
- (guard) Outside git there is no scan and archive still renames: `d=$(mktemp -d) && mkdir -p "$d/.sdlc/0001-a" && printf -- "---\nid: T-0001\ntitle: a\ntype: idea\nstatus: done\nsize: S\npriority: P2\ndepends: []\ncreated: 2026-09-25\n---\n" > "$d/.sdlc/0001-a/handoff.md" && printf "ticket_folders: numbered\n" > "$d/.sdlc/config" && printf "see .sdlc/0001-a/handoff.md\n" > "$d/spec.md" && python3 plugins/sdlc-lite/scripts/tickets.py --root "$d/.sdlc" archive >/dev/null && test -d "$d/.sdlc/.0001-a"`
- `grep -qF 'archive [--dry-run] [--rewrite-refs] [--force]' plugins/sdlc-lite/scripts/tickets.py`
- `grep -qE "run\(root, 'archive'.*rewrite_refs=True" plugins/sdlc-lite/scripts/tickets.py`
- `grep -qE "run\(root, 'archive'.*force=True" plugins/sdlc-lite/scripts/tickets.py`
- Every existing `close` selftest expect line is still present unchanged. The verifier checks this by reading `git diff HEAD -- plugins/sdlc-lite/scripts/tickets.py`: the only removed lines are the moved `rewrite_now` body and the lines of `cmd_archive` and `main` that were replaced.
