<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0116: tickets.py archive scans for references before renaming done/dropped folders

## PR body
## Summary
`tickets.py archive` renamed done/dropped numbered folders to the dot-prefixed form with no reference scan. It could break committed or untracked references the same way `close` did (T-0113). It now runs close's scan (`outside_refs`) before any write. It uses the same refusal, `--rewrite-refs` and `--force` handling as `close`.

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - Moved the rewrite loop out of `cmd_close`'s `rewrite_now` into a module-level `rewrite_files(top, files, old, new)`. `close` calls it with the same output and ordering. No second scanner was added.
  - `cmd_archive(root, numbered, dry_run, rewrite_refs, force)` calls `outside_refs` for each folder it would rename.
  - If any file cites one of those folders and neither flag is given, archive refuses and writes nothing. The message names each cited folder, each citing file, both flags, and ends with `nothing written`. A `--dry-run` without a flag refuses the same way.
  - `--dry-run --rewrite-refs` prints the rename lines plus one sorted `rewrite <file>` line per citing file. `--dry-run --force` prints only the renames.
  - A real `--rewrite-refs` run rewrites every citing file before any rename, then renames and regenerates the roadmap. This covers a file inside one archived folder that cites another archived folder in the same run. The output ends with `; rewrote refs in ...`.
  - `--force` renames and leaves the cites. Outside git there is no scan.
  - New `--rewrite-refs` and `--force` argparse flags, passed through in `main`. The usage line and the `archive` docstring paragraph are updated.
  - Nine new selftest expects next to the archive block.
- Docs, so the new flags are stated where `archive` is described:
  - `plugins/sdlc-lite/skills/ticket/SKILL.md` (`argument-hint` and the numbered-folders bullet)
  - the repo `CLAUDE.md` Layout entry
  - `.claude/agents/sdlc-lite-author.md`

`close` behavior and its selftests are unchanged. Existing archive behavior is kept: numbered mode only, collision refusal, roadmap regeneration, dry run writes nothing, and "nothing to archive". `fanout.py` is untouched.

## Verification
- Step 1 verifier (L2): pass.
  - Every acceptance command exits 0 in the tree. The non-guard ones exit non-zero at pre-build HEAD, so the checks bite. The two guards, the selftest and the outside-git rename, are green before and after.
  - `git diff` showed no `close` selftest `expect` line removed.
  - `plugins/sdlc-lite/scripts/check.sh` exit 0.
- Builder negative control: changing the scan's `if files` to `if files and False` made 6 `archive refs` expects fail. The file was restored and the selftest passed again.
- Step 2 verifier (L1): pass.
  - The four doc greps exit 0 in the tree and 1 at HEAD^.
  - `check.sh` and the tickets selftest are green.
  - The doc edits were already committed in the `wip(tickets-py-archive-renames-done)` HEAD commit. The step 2 builder made no changes.

## Changelog entry
- `tickets.py archive` now runs the same reference scan as `close` before renaming done/dropped numbered folders. It refuses, naming each citing file and writing nothing, unless given `--rewrite-refs` (rewrite the cites to the dot form, then rename) or `--force` (rename and leave them). `--dry-run --rewrite-refs` lists one `rewrite <file>` line per citing file. There is no scan outside git.

## Follow-ups
- `tickets.py outside_refs` matches folder paths by fixed-string prefix, so `.sdlc/0001-a` also matches `.sdlc/0001-ab`. `close` and `archive` can report or rewrite a citation of a different folder that shares the prefix.
