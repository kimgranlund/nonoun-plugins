<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc/scripts/tickets.py`: new `outside_refs(root, slug)` helper. It finds the git toplevel the same way `worktree_pairs` does, dropping `GIT_ENV_DROP`, then runs `git grep --untracked -I -l -z --full-name -F -e <rel>/<slug>` from the toplevel and leaves out the ticket's own folder and `<root>/roadmap.md`. It returns no hits outside git, when git fails, or when root is outside the toplevel.
- Same file, `cmd_close`: new `rewrite_refs=False` kwarg. The scan runs only when `archive` is true. It sits after the already-closed, target-exists, problems, and status-done refusals and before any write, and it covers every close path.
  - Hits with neither `--rewrite-refs` nor `--force` refuse with `Fail`, naming each file, and write nothing.
  - `--rewrite-refs` rewrites the files right after the rename, on both the `--reason` and filer paths, and appends `; rewrote refs in <files>` to the output.
  - The dry run prints `rewrite <file>` lines just before `expect`.
- Same file, CLI: `--rewrite-refs` flag on the `close` subparser, passed through `main`.
- Same file, selftest: new `(u) refs:` cases in a git repo, skipped when git is missing.
  - Refusals: a committed file, an untracked file, `--reason`, and `--dry-run` each refuse, and nothing changes in the whole case dir outside `.git`.
  - Closes: `--rewrite-refs`, `--reason --rewrite-refs`, `--dry-run --rewrite-refs` (lists the file and writes nothing), and `--force` (leaves the file).
  - Negative controls: a reference only in the ticket's own folder or in the roadmap still closes, and plain mode never refuses.
- Same file, module docstring: the `Usage:` line gains `[--rewrite-refs]`, and the `close` paragraph describes the scan, the refusal, `--rewrite-refs`, the dry-run lines, `--force`, and that there is no scan outside git.

## Checks
- Acceptance criteria 1 to 5 (committed refusal, untracked refusal, `--reason` refusal, `--rewrite-refs` rewrite, `--dry-run --rewrite-refs`): each exit 0.
- Guard `--force` closes and leaves the file: exit 0.
- Guard reference only inside the own folder closes: exit 0.
- Guard plain mode never refuses: exit 0.
- Guard outside git closes: exit 0.
- `python3 plugins/sdlc/scripts/tickets.py selftest`: `tickets selftest: PASS`.
- `grep -qF -- '--rewrite-refs' plugins/sdlc/scripts/tickets.py`: exit 0.
- Observable criterion: in a throwaway copy (plugin `scripts/` and `skills/` in a mktemp dir), I replaced the `outside_refs(...)` call in `cmd_close` with an empty result. Selftest reported FAIL on 7 `(u) refs:` cases: 4 refusals, 2 `--rewrite-refs` rewrites, and the dry-run listing. The copy is removed.
- Extra mutations in throwaway copies, each FAILing the own-folder control:
  - Dropping the roadmap exclusion: FAIL, `.sdlc/roadmap.md` listed.
  - Dropping the own-folder exclusion: FAIL, `.sdlc/0003-x/notes.md` listed.
- `plugins/sdlc/scripts/check.sh`: rc=0 (all selftests, shellcheck, and plugin validate ok).

## Notes
- The refusal message offers `--force` only when `--ack-warnings` is not given. `--ack-warnings` already refuses together with `--force`, so suggesting it there would send the user to a second refusal. On that path the message offers only `--rewrite-refs`.
- With both `--rewrite-refs` and `--force`, the rewrite happens.
- `-I` (skip binary files) was added to the `git grep` so a rewrite never touches binary content. Files are rewritten as bytes, so their encoding is kept.
- When the ticket root is the git toplevel itself (rel `.`), the pattern is the bare `<slug>`.
- Nothing is committed. Only `tickets.py` changed.
