---
id: T-0118
title: "The reference scan matches only the literal toplevel-relative path..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0113
---

## Goal
When `tickets.py close` (numbered mode) or `tickets.py archive` renames `NNNN-<slug>` to `.NNNN-<slug>`, its reference scan also finds (and with `--rewrite-refs` rewrites) references to the folder written as a path relative to the citing file (`../0003-x/`, `../../.sdlc/0003-x/handoff.md`) or as an absolute path (`/abs/toplevel/.sdlc/0003-x`), not only the literal toplevel-relative `<rel>/<slug>`, so those references no longer break silently on rename.

## Intent
Literal ask: the reference scan matches only the literal toplevel-relative path `<rel>/<slug>`, so relative (`../NNNN-x/`) or absolute-path references to the ticket folder are missed and still break on rename.
Deltas:
- Which references count: defaulted: a path-like token (no whitespace, quotes, backticks, parens, angle or square brackets) that contains the folder name as a whole path component and that resolves to `<toplevel>/<rel>/<slug>` (or a path under it) when read (a) as toplevel-relative (today's rule), (b) relative to the citing file's own directory, or (c) as an absolute path. A bare `0003-x` word or a path that resolves elsewhere (another tree's `.sdlc/0003-x`, `other/0003-x`) is not a reference.
- Candidate discovery: defaulted: keep one `git grep --untracked -I -lF` from the toplevel, but on the folder name `<slug>` (NNNN-<slug>), then filter each hit file's tokens by the resolution rule above in Python; files with no resolving token drop out.
- Rewrite: defaulted: `--rewrite-refs` rewrites only the matched tokens, turning that path component `<slug>` into `.<slug>`, keeping the token's form (relative stays relative, absolute stays absolute); all other bytes in the file stay unchanged.
- Exclusions: defaulted: unchanged. Files under the ticket's own folder and `<root>/roadmap.md` stay skipped (a self-reference like `../0003-x/` from inside the moving folder is out of scope; gap: noted, not handled).
- Output: defaulted: refusal text, `rewrite <file>` dry-run lines, and the `; rewrote refs in ...` suffix keep their current formats; no new flags.
- Case, symlinks, `~` home paths, URL-encoded paths: defaulted: not handled (exact-case match, no symlink resolution beyond `os.path.normpath`, no `~` expansion).
Do: extend `outside_refs` / `rewrite_files` in `plugins/sdlc-lite/scripts/tickets.py` (shared by `close` and `archive`) per the rules above; add selftest cases proving a relative reference from another folder, a relative reference from a file inside another ticket folder (`../0003-x/filer-L1.md`), and an absolute reference are each refused without `--rewrite-refs`, listed by `--dry-run --rewrite-refs`, and rewritten correctly with it, plus negative controls (a bare `0003-x` word and a same-named path elsewhere are not refs and are left untouched); update the docstrings and every doc that describes the scan (CLAUDE.md Layout `tickets.py` entry, `.claude/agents/sdlc-lite-author.md` if it describes it, `skills/ticket` and `skills/file` if they do, tickets.py module help).
Non-goals: self-references inside the moving folder; references in other git worktrees; non-numbered mode (plain folders never move); changing fanout.py beyond what it inherits.
Done when: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` passes with the new cases, the new cases fail against the pre-change `outside_refs` (red before, green after), and `plugins/sdlc-lite/scripts/check.sh` is green.

## Context
Follow-up from T-0113 (close-rename-breaks-refs/filer-L1.md):

The reference scan matches only the literal toplevel-relative path `<rel>/<slug>`, so relative (`../NNNN-x/`) or absolute-path references to the ticket folder are missed and still break on rename.

## Constraints
Existing toplevel-relative detection and rewrite behavior, all existing selftests, CLI flags, and output formats stay unchanged. Stdlib only. Every refusal still writes nothing.
