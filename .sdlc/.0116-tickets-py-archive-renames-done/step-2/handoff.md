## Task goal
`tickets.py archive` never silently breaks a committed or untracked reference to a folder it renames: it runs the same reference scan `close` runs (`outside_refs`) for every done/dropped `NNNN-<slug>` folder it would rename, refuses with nothing written while any file cites one, and offers the same escape hatches as `close` (`--rewrite-refs` rewrites each cite to the dot form with the rename; `--force` archives and leaves them). `archive --dry-run` lists the renames plus one `rewrite <file>` line per citing file when `--rewrite-refs` is given, and names the citing files otherwise.

Done when: the new behavior is covered by `tickets.py selftest` cases (refuse naming the file and writing nothing, `--rewrite-refs` rewrites and renames, `--force` renames and leaves the cite, dry run with and without `--rewrite-refs`, outside git no scan), `scripts/check.sh` is green, and every doc that describes `archive` (tickets.py usage/docstring, the ticket skill, repo CLAUDE.md Layout entry, `.claude/agents/sdlc-lite-author.md` if it describes archive) states the new flags.

## Step 2: Document the archive flags
level: L1
### Do
Change `archive [--dry-run]` to `archive [--dry-run] [--rewrite-refs] [--force]` (keep `[--numbered]` where it appears today) and state the new behavior in each of these places:

1. `plugins/sdlc-lite/skills/ticket/SKILL.md`, in two spots:
   - the `argument-hint` line;
   - the numbered-folders bullet (line 15), where `archive` "renames existing done/dropped numbered folders the same way". Say that it first runs the same reference scan as `close` for every folder it would rename (a file inside another folder archived in the same run counts), and refuses, writing nothing, naming each citing file. Say that `--rewrite-refs` rewrites them to the dot form before renaming (`--dry-run --rewrite-refs` lists one `rewrite <file>` line each), that `--force` archives and leaves them, and that outside git there is no scan.
2. `CLAUDE.md` (repo root), in the `scripts/tickets.py` Layout entry, in the phrase `` `archive [--dry-run]` renames existing done/dropped numbered folders ``: give the same facts, briefly.
3. `.claude/agents/sdlc-lite-author.md` line 17, in the dot-prefix sync sentence: change `` `archive [--dry-run]` renames existing done/dropped folders `` to name `archive [--dry-run] [--rewrite-refs] [--force]` and the archive reference scan. The sync list (tickets.py, the /ticket, handoff-format and /file skills, CLAUDE.md) stays.

Edit no code.
### Acceptance criteria
- `grep -qE '^argument-hint:.*archive \[--dry-run\] \[--rewrite-refs\] \[--force\]' plugins/sdlc-lite/skills/ticket/SKILL.md`
- `grep -qF 'archive [--dry-run] [--rewrite-refs] [--force]' CLAUDE.md`
- `grep -qF 'archive [--dry-run] [--rewrite-refs] [--force]' .claude/agents/sdlc-lite-author.md`
- `test "$(grep -cF 'archive [--dry-run] [--rewrite-refs] [--force]' plugins/sdlc-lite/skills/ticket/SKILL.md)" -ge 2`
- (guard) `plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
