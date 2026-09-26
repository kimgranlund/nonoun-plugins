<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0113: close refuses to rename a numbered ticket folder while other files cite its path

## PR body
### Summary
In numbered mode, `tickets.py close` renames `NNNN-<slug>` to `.NNNN-<slug>`. That rename left committed references to the old path broken. A doc that cited the ticket folder failed its doc-path lint on main, and every merge went red until someone fixed it by hand (reported by a peer repo).

Now `close` scans for files outside the ticket folder that cite the old path. If it finds any, it refuses and writes nothing. `--rewrite-refs` rewrites those references to the dot-prefixed path as part of the close. `--force` closes and leaves them. This is option 1 from the ticket, the recommended one: list and refuse, with an opt-in rewrite and no silent rewrite.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`:
  - New `outside_refs(root, slug)` helper. It runs `git grep --untracked -I -l -z --full-name -F` from the git toplevel. It leaves out the ticket's own folder and `<root>/roadmap.md`, skips binary files, and does no scan outside git or when git fails.
  - `cmd_close` gets a `rewrite_refs` kwarg and the CLI gets a `--rewrite-refs` flag. The scan runs only in numbered mode, after the existing refusals and before any write. It covers the filer, `--reason`, `--ack-warnings` and `--dry-run` paths.
  - With hits and neither flag, `close` refuses and names each file.
  - With `--rewrite-refs`, it rewrites `<rel>/<slug>` to `<rel>/.<slug>` in each hit and appends `; rewrote refs in <files>` to the output.
  - `--dry-run` applies the same refusal. With `--rewrite-refs` it prints one `rewrite <file>` line per hit before the `expect` line.
  - The refusal message leaves out the `--force` suggestion when `--ack-warnings` is given, because those two flags already refuse together.
  - The docstring and `Usage:` line are updated.
- New `(u) refs:` selftest cases, skipped when git is missing. They cover a committed file, an untracked file, `--reason`, `--dry-run`, `--rewrite-refs`, `--reason --rewrite-refs`, `--dry-run --rewrite-refs` and `--force`. Negative controls: a reference only in the ticket's own folder or the roadmap still closes, and plain mode never refuses. The failing tests land in the same change as the fix.
- Docs synced to the new behavior: `CLAUDE.md`, `skills/ticket/SKILL.md`, `skills/handoff-format/SKILL.md`, `.claude/agents/sdlc-lite-author.md`, and `skills/file/SKILL.md`. Step 3.1 of `/file` now handles the refusal with an AskUserQuestion: "Rewrite references" (recommended), "Leave open", "Close anyway". An unattended run stops and never rewrites or forces.

### How each was verified
- Step 1, verifier L2, pass. Each of the five acceptance commands exited 0 in the tree. Where they were run at HEAD in a throwaway worktree, they went red: exit 1, or exit 2 for the unknown flag. The `--force`, own-folder, plain-mode and outside-git guards passed. `tickets.py selftest` prints PASS, and `scripts/check.sh` passed.
- Mutation check: replacing the scan call with an empty result turned the selftest to `FAIL, these did not bite`. The builder ran the same mutation and got 7 failing `(u) refs:` cases. Dropping the roadmap exclusion or the own-folder exclusion also failed the own-folder control.
- Step 2 (docs), verifier L1, pass. Each of the five files carries `--rewrite-refs` and each check is red at HEAD. `file/SKILL.md` has "Rewrite references" in the required option order. `check.sh` exited 0, only `tickets.py` differs under `scripts/` and `hooks/`, and `close --help` lists the flag.
- An earlier step 2 attempt was superseded after it blocked on a plan defect: a criterion compared `tickets.py` against HEAD, which cannot pass while step 1 is uncommitted. The replan fixed the criterion.

## Changelog entry
- `tickets.py close` in numbered mode now refuses to rename a ticket folder while other files cite its path, and lists them. `--rewrite-refs` rewrites those references to the dot-prefixed path. `--force` closes and leaves them. `/file` asks which to do.

## Follow-ups
- `tickets.py archive` renames done/dropped numbered folders to the dot-prefixed form with no reference scan, so it can break committed references the same way `close` did.
- `fanout.py` closes tickets with a plain `close <slug>`, so in a numbered-mode repo a reference hit ends the ticket as `merged, close refused` and leaves it open until someone reruns with `--rewrite-refs`.
- The reference scan matches only the literal toplevel-relative path `<rel>/<slug>`, so relative (`../NNNN-x/`) or absolute-path references to the ticket folder are missed and still break on rename.
